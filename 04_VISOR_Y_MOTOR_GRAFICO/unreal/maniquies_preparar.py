# -*- coding: utf-8 -*-
"""
Prepara, FUERA del editor (con el Python del proyecto, que sí tiene NumPy), todo lo que importar_repeticion.py necesita para poner los
maniquíes: por cada persona de la repetición, su trayectoria a 24 cps y su animación (huesos x 7 números por cuadro, float32). Escribe en
unreal/_cache/preparado/ (fuera de Git). importar_repeticion.py lo llama solo; también se puede correr a mano:
    03_SIMULACION_RL/.venv/Scripts/python.exe 04_VISOR_Y_MOTOR_GRAFICO/unreal/maniquies_preparar.py <replay.json> [desde_s] [hasta_s]
"""
import json
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import maniquies_animar as MA  # noqa: E402
import maniquies_replay as MR  # noqa: E402

SALIDA = os.path.join(AQUI, "_cache", "preparado")
FPS = MA.FPS
FPS_ANIM = 30


def preparar(ruta, desde=0.0, hasta=None):
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)
    C, dt = datos["cuadros"], datos.get("dt", 0.1)
    k0 = int(desde / dt)
    k1 = min(len(C), int(hasta / dt) + 1) if hasta else len(C)
    C = C[k0:k1]
    n = int(round((len(C) - 1) * dt * FPS)) + 1
    os.makedirs(SALIDA, exist_ok=True)
    for viejo in os.listdir(SALIDA):
        os.remove(os.path.join(SALIDA, viejo))
    A = MA.Animador()
    n_a = int(round((len(C) - 1) * dt * FPS_ANIM)) + 1             # el AnimSequence de Unreal pide 30 cps (o múltiplo/factor de 30)
    meta = {"n": n, "n_anim": n_a, "fps_anim": FPS_ANIM, "huesos": A.E.huesos, "personas": {}}
    for clave, (rol, est) in MR.personas_de(C).items():
        t = MR.trayectoria(C, dt, clave, n)
        ta = MR.trayectoria(C, dt, clave, n_a, FPS_ANIM)
        S = A.animar(ta["v"], ta["pos0"], ta["pos"], ta["pt"], ta["run"], ta["saltof"], ta["saltot"], FPS_ANIM).astype("<f4")
        S.tofile(os.path.join(SALIDA, f"anim_{clave}.f32"))
        with open(os.path.join(SALIDA, f"tray_{clave}.json"), "w") as f:
            json.dump({k: v.tolist() for k, v in t.items() if k in ("x", "y", "h", "yaw", "visible")}, f)
        meta["personas"][str(clave)] = [rol, est]
    with open(os.path.join(SALIDA, "meta.json"), "w") as f:
        json.dump(meta, f)
    return meta


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("-")]
    m = preparar(a[0], float(a[1]) if len(a) > 1 else 0.0, float(a[2]) if len(a) > 2 and a[2] else None)
    print(f"preparado: {len(m['personas'])} personas, {m['n']} cuadros")
