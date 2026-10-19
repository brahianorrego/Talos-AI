# -*- coding: utf-8 -*-
"""
Hace una repetición SINTÉTICA (mismo formato que foto()) en la que el ladrón pasa por todas las posturas y movimientos delante de la
cámara, y un civil camina y se queda quieto: de pie, caminar, trotar, agacharse, caminar agachado, recostarse contra un panel, gatear y
saltar. Sirve para revisar los maniquíes sin esperar a que una partida los muestre. Escribe unreal/_cache/galeria/replay_v17.json:
    03_SIMULACION_RL/.venv/Scripts/python.exe 04_VISOR_Y_MOTOR_GRAFICO/unreal/galeria_posturas.py
y después se importa y renderiza igual que una partida (importar_repeticion.py <ese json>, renderizar.py <secuencia>).
"""
import json
import math
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
DT = 0.1
# (segundos, postura, velocidad m/s, fase del salto)
GUION = [(2.0, 0, 0.0, 0), (3.0, 0, 1.2, 0), (3.0, 0, 3.2, 0), (1.0, 0, 0.0, 0), (1.2, 1, 0.0, 0), (3.0, 1, 0.8, 0), (1.2, 0, 0.0, 0),
         (2.5, 2, 0.0, 0), (1.2, 0, 0.0, 0), (1.5, 3, 0.0, 0), (3.5, 3, 0.45, 0), (1.5, 0, 0.0, 0), (0.25, 0, 0.0, 1), (0.6, 0, 0.0, 2),
         (0.6, 0, 0.0, 3), (2.0, 0, 0.0, 0)]
ALTO = (1.0, 0.67, 1.0, 0.35)


def principal():
    cuadros, x, x_recosta = [], -14.0, None
    t = 0.0
    pos, pos0, pt = 0, 0, 1.0
    for dur, p, v, fs in GUION:
        pasos = int(round(dur / DT))
        if p != pos:
            pos0, pos, pt = pos, p, 0.0
        for k in range(pasos):
            pt = min(1.0, pt + DT / 0.5)
            x += v * DT
            tf = k * DT
            if p == 2 and x_recosta is None:
                x_recosta = x
            h = 0.0
            if fs == 2:
                h = max(0.0, 0.45 * 4 * (tf / 0.6) * (1 - tf / 0.6))
            est = 1.72
            alto = est * (ALTO[pos0] * (1 - pt) + ALTO[pos] * pt)
            civil_x = -4.0 + 0.9 * math.sin(t / 5.0) * 1.0
            cuadros.append({
                "d": [x, -6.0, 5.0, math.pi / 2], "cr": 0.0, "cp": 0.0, "dv": [0, 0, 0],
                "pers": [
                    {"rol": "ladron", "id": 1, "p": [x, 0.0], "v": [v, 0.0], "mira": 0.0, "est": est, "pos0": pos0, "pos": pos, "pt": pt,
                     "run": v > 2.4, "alto": alto},
                    {"rol": "peaton", "id": 2, "p": [civil_x, 3.0], "v": [0.0, 0.0], "mira": -math.pi / 2, "est": 1.63, "pos0": 0, "pos": 0,
                     "pt": 1.0, "run": False, "alto": 1.63}],
                "salto": {"f": fs, "h": round(h, 3), "mano": [0, 0, 0]}})
            t += DT
    datos = {"dt": DT, "paneles": [[x_recosta - 0.5, -1.5, x_recosta - 0.5, 1.5, 2.25]], "cuadros": cuadros}
    salida = os.path.join(AQUI, "_cache", "galeria")
    os.makedirs(salida, exist_ok=True)
    with open(os.path.join(salida, "replay_v17.json"), "w", encoding="utf-8") as f:
        json.dump(datos, f)
    print(f"galería: {len(cuadros)} cuadros, {len(cuadros) * DT:.1f} s -> {salida}")


if __name__ == "__main__":
    principal()
