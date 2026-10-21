# -*- coding: utf-8 -*-
"""
Prueba de los maniquíes en vivo SIN la simulación: manda por UDP (como puente_unreal.py) la repetición sintética de la galería de posturas
(galeria_posturas.py: de pie, caminar, trotar, agacharse, agachado caminando, recostarse, gatear, saltar) a unreal/vivo_unreal.py.
    03_SIMULACION_RL\\.venv\\Scripts\\python.exe 04_VISOR_Y_MOTOR_GRAFICO\\unreal\\enviar_galeria_udp.py [--capturas 11.5,15.5,21,25.1]
Con --capturas pide una foto del viewport (archivo _cache/captura.txt) en esos segundos de la repetición.
"""
import argparse
import json
import os
import socket
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--puerto", type=int, default=8770)
ap.add_argument("--capturas", default="")
ap.add_argument("--vueltas", type=int, default=1)
A = ap.parse_args()
d = json.load(open(os.path.join(AQUI, "_cache", "galeria", "replay_v17.json"), encoding="utf-8"))
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
destino = ("127.0.0.1", A.puerto)
horas = sorted(float(v) for v in A.capturas.split(",") if v)
for _ in range(A.vueltas):
    s.sendto(json.dumps({"t": "cab", "paneles": d["paneles"], "dt": d["dt"], "version": "galeria"}).encode(), destino)
    t0, i, k = time.time(), 0, 0
    while i < len(d["cuadros"]):
        c = d["cuadros"][i]
        pers = [{"r": p["rol"], "p": p["p"], "v": p["v"], "pos": p.get("pos", 0), "alto": p.get("alto", 1.7), "mira": p.get("mira", 0.0), "run": p.get("run", False), "est": p.get("est", 1.7),
                 "sz": (c.get("salto") or {}).get("h", 0.0) if p["rol"] == "ladron" else 0.0} for p in c["pers"]]
        s.sendto(json.dumps({"t": "c", "d": c["d"], "pan": 0.0, "tilt": -5.0, "pers": pers}).encode(), destino)
        i += 1
        if k < len(horas) and i * d["dt"] >= horas[k]:
            open(os.path.join(AQUI, "_cache", "captura.txt"), "w").write("1")
            k += 1
        time.sleep(max(0.0, t0 + i * d["dt"] - time.time()))
