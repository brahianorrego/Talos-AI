# -*- coding: utf-8 -*-
"""
Paso 4 del plan mínimo: tomas de datos en campo, manejadas DESDE EL PORTÁTIL (Windows).

La Jetson graba sin parar (registro_minimo.py --tomas ~/toma_actual.json); este programa escribe ese archivo para
INICIAR una toma, guía con pitidos y lo borra para TERMINARLA. Nadie etiqueta a mano: las etiquetas se calculan
después con el LiDAR y la cinta (plan, sección 6).

Uso (desde Tesis-IA-Drone):
    py jetson\\herramientas\\campo.py buscar                     # encuentra la Jetson en la red del celular
    py jetson\\herramientas\\campo.py arrancar --ip X            # arranca la grabación continua (video + datos)
    py jetson\\herramientas\\campo.py toma E2 --rep 1 --altura 1.55 --montaje 4A --ip X
    py jetson\\herramientas\\campo.py estado --ip X
    py jetson\\herramientas\\campo.py parar --ip X               # detiene y muestra el resumen
    py jetson\\herramientas\\campo.py descargar --ip X           # copia registros/ a datos_campo/ (fuera de Git)
"""
import argparse
import json
import os
import socket
import subprocess
import time
import winsound

USUARIO = "brahian"
CTRL = "~/toma_actual.json"
# mata las grabaciones anteriores sin matarse a sí mismo (el texto del comando contiene el nombre del programa)
MATAR = "for p in $(pgrep -f registro_minimo.py); do [ $p != $$ ] && [ $p != $PPID ] && kill -%s $p; done"
DIR = "~/Escritorio/dron_ia"

# Escenarios (plan, sección 6, y decisiones del arquitecto del 2026-10-11).
# fases: (segundos desde el inicio, pitidos, qué hace la persona)
ESCENARIOS = {
    "E0": dict(nombre="sin nadie al frente (falsas detecciones)", dist="-", dur=20,
               fases=[(0, 1, "nadie en el campo de la cámara")]),
    "E1": dict(nombre="persona quieta en cada marca (5 s por marca)", dist="conos", dur=63,
               fases=[(0, 1, "en la marca de 15 m"), (9, 1, "a la marca de 12 m"), (18, 1, "a 10 m"),
                      (27, 1, "a 8 m"), (36, 1, "a 6 m"), (45, 1, "a 4 m"), (54, 1, "a 2 m")],
               conos=[15, 12, 10, 8, 6, 4, 2]),
    "E2": dict(nombre="persona camina hacia el dron 15 -> 3 m (~9 s, 1.4 m/s)", dist="15->3", dur=16,
               fases=[(0, 2, "en 15 m, lista"), (3, 1, "¡camina! y se detiene en 3 m")]),
    "E3": dict(nombre="persona trota hacia el dron 15 -> 4 m (~3.5 s, 3.3 m/s)", dist="15->4", dur=11,
               fases=[(0, 2, "en 15 m, lista"), (3, 1, "¡trota! y se detiene en 4 m")]),
    "E4": dict(nombre="persona cruza de lado (ver --dist 5/8/12 y --nota camina/trota)", dist="5|8|12", dur=15,
               fases=[(0, 2, "en el extremo izquierdo de la línea"), (3, 1, "¡cruza! hasta el otro extremo")]),
    "E5": dict(nombre="4B: silla con el dron empujada hacia la persona quieta 15 -> 3 m (~1 m/s)", dist="15->3",
               dur=18, fases=[(0, 2, "silla en 15 m, persona quieta en 0"), (3, 1, "¡empuja despacio! parar en 3 m")]),
    "E6": dict(nombre="cartón (panel) acercándose al dron 15 -> 3 m, empujado en la silla", dist="15->3", dur=18,
               fases=[(0, 2, "cartón en 15 m, quien empuja escondido detrás"), (3, 1, "¡empuja! parar en 3 m")]),
}


def ssh(ip, cmd, timeout=20):
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=6", "%s@%s" % (USUARIO, ip), cmd],
                       capture_output=True, text=True, timeout=timeout)
    return r.stdout + r.stderr


def pitar(n, larga=False):
    for _ in range(n):
        winsound.Beep(700 if larga else 1000, 900 if larga else 300)
        time.sleep(0.12)


def buscar():
    ip_local = socket.gethostbyname(socket.gethostname())
    redes = {ip_local.rsplit(".", 1)[0]}
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        redes.add(s.getsockname()[0].rsplit(".", 1)[0])
        s.close()
    except OSError:
        pass
    for red in sorted(redes):
        print("buscando en %s.0/24 ..." % red)
        abiertos = []
        socks = []
        for i in range(1, 255):
            ip = "%s.%d" % (red, i)
            k = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            k.setblocking(False)
            k.connect_ex((ip, 22))
            socks.append((ip, k))
        time.sleep(2.0)
        for ip, k in socks:
            try:
                k.getpeername()
                abiertos.append(ip)
            except OSError:
                pass
            k.close()
        for ip in abiertos:
            if "sant" in ssh(ip, "hostname", timeout=8):
                print("JETSON en %s" % ip)
                return ip
    print("no la encontré: ¿la Jetson está encendida y el portátil en el mismo WiFi del celular?")


def arrancar(ip):
    print(ssh(ip, "rm -f %s; " % CTRL + MATAR % "TERM" + "; sleep 1; cd %s && "
                  "(setsid nohup ~/dron_env/bin/python -u registro_minimo.py --video --tomas %s --pitch-fijo -5 "
                  "> ~/campo.log 2>&1 < /dev/null &) ; sleep 25; grep -vE 'Warning|warn|TRT|Loading|PreArm' ~/campo.log | tail -5"
                  % (DIR, CTRL), timeout=60))


def toma(ip, esc, rep, altura, montaje, dist, nota):
    e = ESCENARIOS[esc]
    base = dict(toma_id="%s-%s%s-R%d" % (esc, montaje, ("-" + dist) if dist else "", rep), escenario=esc,
                repeticion=rep, distancia_m=dist or e["dist"], altura_camara_m=altura, montaje=montaje,
                nota=nota)
    print("\n== %s: %s (repetición %d)" % (base["toma_id"], e["nombre"], rep))

    def escribir(extra=None):
        d = dict(base, **(extra or {}))
        ssh(ip, "cat > %s.tmp <<'X'\n%s\nX\nmv %s.tmp %s" % (CTRL, json.dumps(d, ensure_ascii=False), CTRL, CTRL))

    t0 = time.time()
    escribir()
    for k, (t, n, txt) in enumerate(e["fases"]):
        while time.time() - t0 < t:
            time.sleep(0.05)
        print("  %4.1f s  %s pitido(s): %s" % (time.time() - t0, n, txt))
        pitar(n)
        if "conos" in e:
            escribir({"distancia_m": e["conos"][k]})
    while time.time() - t0 < e["dur"]:
        time.sleep(0.05)
    ssh(ip, "rm -f %s" % CTRL)
    pitar(1, larga=True)
    print("  fin de la toma (%.0f s)" % (time.time() - t0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("accion", choices=["buscar", "arrancar", "toma", "estado", "parar", "descargar"])
    ap.add_argument("escenario", nargs="?", choices=sorted(ESCENARIOS))
    ap.add_argument("--ip")
    ap.add_argument("--rep", type=int, default=1)
    ap.add_argument("--altura", type=float, default=0.0, help="m del suelo al centro del lente de la cámara")
    ap.add_argument("--montaje", default="4A", choices=["4A", "4B-silla", "4B-mano"])
    ap.add_argument("--dist", default="", help="E4: línea de cruce 5, 8 o 12")
    ap.add_argument("--nota", default="", help="E4: camina o trota; cualquier observación")
    a = ap.parse_args()
    if a.accion == "buscar":
        buscar()
    elif a.accion == "arrancar":
        arrancar(a.ip)
    elif a.accion == "toma":
        toma(a.ip, a.escenario, a.rep, a.altura, a.montaje, a.dist, a.nota)
    elif a.accion == "estado":
        print(ssh(a.ip, "grep -E ' s \\||TOMA|BATERIA|reabriendo' ~/campo.log | tail -8"))
    elif a.accion == "parar":
        print(ssh(a.ip, "rm -f %s; " % CTRL + MATAR % "INT" + "; sleep 6; tail -6 ~/campo.log"))
    elif a.accion == "descargar":
        destino = os.path.join("datos_campo")
        os.makedirs(destino, exist_ok=True)
        subprocess.run(["scp", "-r", "%s@%s:%s/registros" % (USUARIO, a.ip, DIR), destino])
        print("copiado en %s" % os.path.abspath(destino))


if __name__ == "__main__":
    main()
