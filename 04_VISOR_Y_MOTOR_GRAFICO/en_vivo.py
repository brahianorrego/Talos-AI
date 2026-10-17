# -*- coding: utf-8 -*-
"""
Simulación EN VIVO para el visor (fase V5 del plan del visor): corre UNA partida del entorno de 03_SIMULACION_RL a tiempo
real y manda cada foto() al navegador apenas ocurre (Server-Sent Events, solo biblioteca estándar). Al terminar una partida
empieza otra. No modifica nada de 03_SIMULACION_RL: solo importa entorno.py.

Quién decide el dron:
  - por defecto, la acción 0 en cada paso (el dron queda en manos de las reglas deterministas: búsqueda, árbitro, etc.);
  - con --politica modelos/dron_politica.json, la red exportada (respetando los botones permitidos de la V17).

Uso (desde la raíz del proyecto, con el .venv de la simulación):
  03_SIMULACION_RL\\.venv\\Scripts\\python.exe 04_VISOR_Y_MOTOR_GRAFICO\\en_vivo.py [--nivel 6] [--semilla 1] [--velocidad 1]
Luego, en el visor (puerto 8766), elegir la repetición "Simulación en vivo".
"""
import argparse
import json
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


def simular():
    semilla = A.semilla
    while True:
        env = E.EntornoDronPersona(1, semilla=semilla, nivel=A.nivel)
        cab = {"tipo": "partida", "paneles": env.paneles(0), "dt": E.DT, "version": "en vivo · nivel %d · semilla %d" % (A.nivel, semilla),
               "titulo": "Simulación en vivo · nivel %d · semilla %d · %s" % (A.nivel, semilla, "política" if politica else "reglas"),
               "autor": "Brahian Andrés Orrego Osorio", "adversaria": True}
        with cambio:
            estado["partida"] += 1
            estado["cabecera"], estado["cuadros"] = cab, [env.foto(0)]
            cambio.notify_all()
        for _ in range(E.PASOS_EPISODIO + 5):
            t0 = time.perf_counter()
            if politica is not None:
                lg = politica.logits(env.obs_dron())
                if hasattr(env, "action_masks"):
                    lg = np.where(env.action_masks(), lg, -1e9)
                ad = lg.argmax(1)
            else:
                ad = np.zeros(1, int)
            _, _, done, _ = env.step(ad, np.full(1, E.N_ACC_PERSONA - 1), auto_reset=False)
            with cambio:
                estado["cuadros"].append(env.foto(0))
                cambio.notify_all()
            if done[0]:
                break
            time.sleep(max(0.0, E.DT / A.velocidad - (time.perf_counter() - t0)))
        time.sleep(3)                                       # pausa entre partidas
        semilla += 1


class Manejador(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if not self.path.startswith("/vivo"):
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")     # el visor está en otro puerto (8766)
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
