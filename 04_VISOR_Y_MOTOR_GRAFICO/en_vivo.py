# -*- coding: utf-8 -*-
"""
Simulación EN VIVO para el visor (fase V5 del plan del visor): corre UNA partida del entorno de 03_SIMULACION_RL a tiempo
real y manda cada foto() al navegador apenas ocurre (Server-Sent Events, solo biblioteca estándar). Al terminar una partida
empieza otra. No modifica nada de 03_SIMULACION_RL: solo importa entorno.py (y, en el modo enseñar, escribe demos_brahian/).

Quién decide el dron:
  - por defecto, la acción 0 en cada paso (el dron queda en manos de las reglas deterministas: búsqueda, árbitro, etc.);
  - con --politica modelos/dron_politica.json, la red exportada (respetando los botones permitidos de la V17).

MODO ENSEÑAR (la estación manda por POST a 127.0.0.1:8767): Brahian dirige al dron y se graba la demostración.
  /modo     {"modo": "auto" | "ensenar", "sub": "mapa" | "manual"}        quién lleva al dron
  /waypoint {x, y, yaw, pan, tilt}   agrega un punto de paso (yaw y pan en °, + = izquierda; tilt en °, -45..+15)
            {"borrar": "ultimo" | "todos"}    {"ir": true | false}    (ir = seguir los puntos; false = parar)
  /manual   {vx, vy, wz, pan, tilt, vz}  de -1 a 1: adelante, a la izquierda, giro, velocidad del pan y del tilt, y subir/bajar (la regla de seguridad manda)
  /camara   {"modo": "asistida" | "manual"}   asistida = el pan-tilt sigue al ladrón mientras se vuela a mano
  /reset    empieza otra partida (si se estaba grabando, guarda la demostración)
  /grabar   {"on": true | false}     al apagar guarda 03_SIMULACION_RL/demos_brahian/demo_<fecha>.json (fuera de Git)
El dron lo lleva el autopiloto del entorno con el control del operador de la Simulación (set_manual, set_objetivo, objetivo_llego, liberar):
geocerca, árbitro y reflejo de punto ciego mandan sobre Brahian.

Uso (desde la raíz del proyecto, con el .venv de la simulación):
  03_SIMULACION_RL\\.venv\\Scripts\\python.exe 04_VISOR_Y_MOTOR_GRAFICO\\en_vivo.py [--nivel 6] [--semilla 1] [--velocidad 1]
Luego, en el visor, elegir "Simulación en vivo" (o el botón Enseñar).
"""
import argparse
import datetime
import json
import math
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import numpy as np

SIM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "03_SIMULACION_RL")
sys.path.insert(0, SIM)
sys.path.insert(0, os.path.join(SIM, "herramientas"))
import entorno as E  # noqa: E402
from demostraciones import Grabador  # noqa: E402  (herramientas/ de la Simulación: guarda obs y mandos para imitar)
E.aplicar_hw("H")                                          # el dron del visor es el plus (pan-tilt): sin esto el pan no responde

ap = argparse.ArgumentParser()
ap.add_argument("--puerto", type=int, default=8767)
ap.add_argument("--nivel", type=int, default=getattr(E, "NIVEL_V17", E.NIVEL_V16))
ap.add_argument("--semilla", type=int, default=1)
ap.add_argument("--velocidad", type=float, default=1.0, help="1 = tiempo real; 2 = el doble de rápido")
ap.add_argument("--politica", default="", help="JSON exportado de la política (si no, acción 0: reglas)")
A = ap.parse_args()

politica = None
if A.politica:
    from politica_json import PoliticaJSON
    politica = PoliticaJSON(os.path.join(SIM, A.politica) if not os.path.isabs(A.politica) else A.politica, n_obs=E.OBS_DRON)

# estado compartido: la partida actual (cabecera + cuadros) y una condición para despertar a los navegadores conectados
estado = {"partida": 0, "cabecera": None, "cuadros": []}
cambio = threading.Condition()

# ---------------------------------------------------------------------------------------------------------------- modo enseñar
ens = {"modo": "auto", "sub": "mapa", "cola": [], "i": 0, "ir": False, "man": {}, "t_man": 0.0, "graba": False, "reg": [], "reset": False, "fin": False, "demo": "", "cam": "manual", "cam_enviada": ""}
lock = threading.Lock()
DEMOS = os.path.join(SIM, "demos_brahian")


enviado = {"i": -1}                                      # último punto de la cola que ya se le dio al entorno


def mandar(env):
    """El dron lo lleva el autopiloto del entorno (control del operador de la Simulación: geocerca, árbitro y reflejos mandan sobre Brahian)."""
    with lock:
        manual = ens["sub"] == "manual"
        man = ens["man"] if time.time() - ens["t_man"] < E.T_MAN else {}
        c = dict(ens["cola"][ens["i"]]) if (not manual and ens["ir"] and ens["i"] < len(ens["cola"])) else None
        i = ens["i"]
    if manual:
        enviado["i"] = -1
        asistida = ens["cam"] == "asistida"                 # cámara asistida: el pan-tilt sigue solo al ladrón mientras Brahian vuela
        v = [float(man.get(k, 0.0)) for k in ("vx", "vy", "wz", "pan", "tilt", "vz")]
        if asistida:
            v[3] = v[4] = 0.0
        env.set_manual(0, *v)
        if asistida and ens["cam_enviada"] != "asistida":
            env.set_camara(0, "asistida")
        ens["cam_enviada"] = ens["cam"]
    elif c is not None:
        if enviado["i"] != i:
            env.set_objetivo(0, c["x"], c["y"], c["yaw"], c["pan"], c["tilt"])
            enviado["i"] = i
        elif env.objetivo_llego(0):
            with lock:
                ens["i"] += 1
                if ens["i"] >= len(ens["cola"]):
                    ens["ir"] = False
    elif enviado["i"] != -2:                              # sin orden: el dron se queda donde está
        env.set_manual(0)
        enviado["i"] = -2


def guardar_demo(cab, grab=None):
    if grab is not None:
        grab.guardar()
    with lock:
        reg, ens["reg"], ens["graba"], ens["fin"] = ens["reg"], [], False, False
    if len(reg) < 5:
        return
    os.makedirs(DEMOS, exist_ok=True)
    ruta = os.path.join(DEMOS, "demo_%s.json" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump({"tipo": "demo_brahian", "dt": E.DT, "paneles": cab["paneles"], "version": cab["version"], "cuadros": reg}, f)
    with lock:
        ens["demo"] = os.path.basename(ruta)
    print("Demostración guardada:", ruta, flush=True)


def simular():
    semilla = A.semilla
    while True:
        env = E.EntornoDronPersona(1, semilla=semilla, nivel=A.nivel)
        cab = {"tipo": "partida", "paneles": env.paneles(0), "dt": E.DT, "version": "en vivo · nivel %d · semilla %d" % (A.nivel, semilla),
               "titulo": "Simulación en vivo · nivel %d · semilla %d · %s" % (A.nivel, semilla, "política" if politica else "reglas"),
               "autor": "Brahian Andrés Orrego Osorio", "adversaria": True}
        enviado["i"] = -1
        with lock:
            ens["cola"], ens["i"], ens["ir"] = [], 0, False
        with cambio:
            estado["partida"] += 1
            estado["cabecera"], estado["cuadros"] = cab, [env.foto(0)]
            cambio.notify_all()
        reiniciar, prev_ens, grab = False, False, Grabador(env, 0)
        for paso in range(E.PASOS_EPISODIO + 5):
            t0 = time.perf_counter()
            enseñando = ens["modo"] == "ensenar"
            previo, prev_ens = prev_ens and not enseñando, enseñando
            if enseñando:
                mandar(env)
                ad = np.zeros(1, int)
            elif previo:
                env.liberar(0)
                ad = np.zeros(1, int)
            elif politica is not None:
                lg = politica.logits(env.obs_dron())
                if hasattr(env, "action_masks"):
                    lg = np.where(env.action_masks(), lg, -1e9)
                ad = lg.argmax(1)
            else:
                ad = np.zeros(1, int)
            _, _, done, _ = env.step(ad, np.full(1, E.N_ACC_PERSONA - 1), auto_reset=False)
            f = env.foto(0)
            with lock:
                if ens["graba"] and enseñando:
                    grab.paso()
                    ens["reg"].append({"d": f["d"], "pan": f["pan"], "gmb": f["gmb"], "i": ens["i"], "cola": [dict(q) for q in ens["cola"]] if paso % 10 == 0 else None,
                                       "man": dict(ens["man"]) if ens["sub"] == "manual" else None, "pers": f["pers"], "vis": f["vis"], "lid": f["lid"], "dm": f["dm"]})
                f["ens"] = {"modo": ens["modo"], "sub": ens["sub"], "cola": ens["cola"], "i": ens["i"], "ir": ens["ir"], "graba": ens["graba"], "n": len(ens["reg"]), "demo": ens["demo"]}
                reiniciar, ens["reset"] = ens["reset"], False
                guardar = ens["fin"]
            if guardar:
                guardar_demo(cab, grab)
                grab = Grabador(env, 0)
            with cambio:
                estado["cuadros"].append(f)
                cambio.notify_all()
            if done[0] or reiniciar:
                if os.environ.get("EN_VIVO_DEPURAR"):
                    print("fin de partida: paso", paso, "done", bool(done[0]), "reset", reiniciar, "estado", int(env.estado[0]), "res", getattr(env, "resultado", None), flush=True)
                break
            time.sleep(max(0.0, E.DT / A.velocidad - (time.perf_counter() - t0)))
        if ens["reg"]:
            guardar_demo(cab, grab)
        time.sleep(1 if reiniciar else 3)                    # pausa entre partidas
        semilla += 1


class Manejador(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_OPTIONS(self):
        self.send_response(204)
        for k, v in (("Access-Control-Allow-Origin", "*"), ("Access-Control-Allow-Methods", "POST, GET, OPTIONS"), ("Access-Control-Allow-Headers", "Content-Type")):
            self.send_header(k, v)
        self.end_headers()

    def do_POST(self):
        try:
            m = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except ValueError:
            self.send_error(400)
            return
        ruta = self.path.split("?")[0]
        with lock:
            if ruta == "/modo":
                ens["modo"] = "ensenar" if m.get("modo") == "ensenar" else "auto"
                if m.get("sub") in ("mapa", "manual"):
                    ens["sub"] = m["sub"]
                if ens["modo"] != "ensenar":
                    ens["ir"] = False
            elif ruta == "/waypoint":
                if m.get("borrar") == "todos":
                    ens["cola"], ens["i"], ens["ir"] = [], 0, False
                elif m.get("borrar") == "ultimo" and ens["cola"]:
                    ens["cola"].pop()
                    ens["i"] = min(ens["i"], len(ens["cola"]))
                elif "ir" in m:
                    ens["ir"] = bool(m["ir"]) and ens["i"] < len(ens["cola"])
                elif "x" in m and "y" in m:
                    ens["cola"].append({"x": float(m["x"]), "y": float(m["y"]), "yaw": float(m.get("yaw", 0.0)),
                                        "pan": float(np.clip(m.get("pan", 0.0), -90.0, 90.0)), "tilt": float(np.clip(m.get("tilt", -5.0), -45.0, 15.0))})
            elif ruta == "/manual":
                ens["man"], ens["t_man"] = {k: float(np.clip(m.get(k, 0), -1, 1)) for k in ("vx", "vy", "wz", "pan", "tilt", "vz")}, time.time()
            elif ruta == "/camara":
                ens["cam"] = "asistida" if m.get("modo") == "asistida" else "manual"
            elif ruta == "/reset":
                ens["reset"] = True
            elif ruta == "/grabar":
                if m.get("on"):
                    ens["graba"], ens["reg"], ens["demo"] = True, [], ""
                else:
                    ens["fin"] = True                        # el bucle guarda en el próximo paso
            else:
                self.send_error(404)
                return
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b"{}")

    def do_GET(self):
        if not self.path.startswith("/vivo"):
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")     # el visor está en otro puerto
        self.end_headers()
        partida, enviados = None, 0
        try:
            while True:
                with cambio:
                    cambio.wait_for(lambda: estado["partida"] != partida or len(estado["cuadros"]) > enviados, timeout=15)
                    if estado["partida"] != partida:              # partida nueva: cabecera y lo que ya pasó
                        partida, enviados = estado["partida"], 0
                        msgs = [json.dumps(estado["cabecera"])]
                    else:
                        msgs = []
                    nuevos = estado["cuadros"][enviados:]
                    enviados += len(nuevos)
                msgs += [json.dumps({"tipo": "cuadro", "c": c}) for c in nuevos]
                self.wfile.write("".join("data: %s\n\n" % m for m in msgs).encode("utf-8") if msgs else b": sigo\n\n")
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass


if __name__ == "__main__":
    threading.Thread(target=simular, daemon=True).start()
    print("Simulación en vivo en http://127.0.0.1:%d/vivo  (Ctrl+C para cerrar)" % A.puerto, flush=True)
    ThreadingHTTPServer(("127.0.0.1", A.puerto), Manejador).serve_forever()
