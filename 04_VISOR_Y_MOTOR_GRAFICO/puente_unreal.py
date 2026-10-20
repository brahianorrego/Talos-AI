# -*- coding: utf-8 -*-
"""
Puente en vivo Python -> Unreal: lee la simulación en vivo (en_vivo.py, Server-Sent Events, puerto 8767) y manda por UDP (127.0.0.1:8770)
lo que Unreal necesita para dibujar la partida: la cabecera (paneles) y, en cada paso (10 Hz), una versión compacta de foto().
Unreal (unreal/vivo_unreal.py) interpola entre paso y paso para dibujar a 30-60 cuadros por segundo.
  03_SIMULACION_RL\\.venv\\Scripts\\python.exe 04_VISOR_Y_MOTOR_GRAFICO\\puente_unreal.py [--puerto-udp 8770]
Los comandos de la estación (enseñar, manual) van directo a en_vivo.py; este puente solo envía cuadros.
"""
import argparse
import json
import socket
import time
import urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("--en-vivo", default="http://127.0.0.1:8767/vivo")
ap.add_argument("--puerto-udp", type=int, default=8770)
A = ap.parse_args()
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
destino = ("127.0.0.1", A.puerto_udp)


def compacto(c):
    """Lo que dibuja Unreal: pose del dron, pan y tilt, personas con postura y hacia dónde miran, y datos de la partida."""
    return {"t": "c", "d": c["d"], "pan": c.get("pan", 0.0), "tilt": c.get("tilt", c.get("gmb", -5.0)), "cam": c.get("cam_modo", ""), "vis": c.get("vis", False),
            "pers": [{"r": p["rol"], "p": p["p"], "v": p["v"], "pos": p.get("pos", 0), "alto": p.get("alto", p.get("est", 1.75)), "mira": p.get("mira", 0.0), "run": p.get("run", False),
                      "est": p.get("est", 1.75), "sz": p.get("sz", 0.0)} for p in c["pers"]],
            "ens": c.get("ens"), "ruta": c.get("ruta_op"), "viento": c.get("viento"), "lid": c.get("lid"), "dm": c.get("dm")}


def main():
    while True:
        try:
            with urllib.request.urlopen(A.en_vivo, timeout=30) as s:
                print("Conectado a", A.en_vivo, "-> UDP", destino, flush=True)
                n = 0
                for linea in s:
                    if not linea.startswith(b"data: "):
                        continue
                    m = json.loads(linea[6:])
                    if m.get("tipo") == "partida":
                        udp.sendto(json.dumps({"t": "cab", "paneles": m["paneles"], "dt": m.get("dt", 0.1), "version": m.get("version", "")}).encode(), destino)
                    elif m.get("tipo") == "cuadro":
                        c = m["c"]
                        if "grosor" in c:
                            pass
                        udp.sendto(json.dumps(compacto(c), separators=(",", ":")).encode(), destino)
                        n += 1
        except OSError as e:
            print("Sin en_vivo.py (%s); reintento en 2 s" % e, flush=True)
            time.sleep(2)


if __name__ == "__main__":
    main()
