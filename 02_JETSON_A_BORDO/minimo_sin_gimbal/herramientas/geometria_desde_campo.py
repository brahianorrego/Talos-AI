# -*- coding: utf-8 -*-
"""
Saca la inclinación REAL de la cámara a partir de las tomas: cuando el rayo del LiDAR pega en una persona (lidar_en_caja = 1) conocemos su distancia d,
y sus pies están en el borde inferior de la caja (y2). Con la altura del lente h sobre el suelo, los pies quedan a una depresión φ = atan(h / d) bajo el horizonte;
en la imagen están en y2_norm. De ahí sale cuánto mira hacia abajo la cámara (α, respecto al horizonte), sin usar la calibración del escritorio:

    y2_norm = 0.5 + tan(φ − α) / (2·tan(VFOV/2))      →      α = φ − atan((y2_norm − 0.5)·2·tan(VFOV/2))

Luego, restando el cabeceo del dron (Pixhawk, + = nariz arriba), queda la inclinación respecto al chasis:   cámara_chasis = −α − cabeceo.
Uso:   python geometria_desde_campo.py CARPETA [CARPETA ...] --altura-lente 1.88 [--vfov 54]
Supuestos (se dicen porque limitan la cifra): pinhole sin distorsión, cámara sin giro (roll), pies visibles (y2 < 0.98), suelo plano, altura del lente medida con metro.
"""
import argparse
import csv
import math
import os
import sys

import numpy as np

NAN = float("nan")


def num(x):
    try:
        return float(x) if x not in ("", None) else NAN
    except ValueError:
        return NAN


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("carpetas", nargs="+")
    ap.add_argument("--altura-lente", type=float, required=True)
    ap.add_argument("--vfov", type=float, default=54.0)
    ap.add_argument("--altura-lidar", type=float, default=0.0, help="altura del eje del LiDAR (por defecto, la del lente − 0.05 m)")
    a = ap.parse_args()
    h = a.altura_lente
    hl = a.altura_lidar or (h - 0.05)
    tv = math.tan(math.radians(a.vfov / 2.0))
    filas = []
    for c in a.carpetas:
        with open(os.path.join(c, "datos.csv"), encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r.get("toma_id") and num(r.get("lidar_en_caja")) == 1 and num(r.get("lidar_valido")) == 1:
                    y2 = num(r["y2"]) / 480.0
                    d = num(r["lidar_cm"]) / 100.0
                    if 0.0 < y2 < 0.98 and 2.5 < d < 16.0:
                        filas.append((d, y2, num(r["cabeceo_deg"]), num(r["alabeo_deg"])))
    M = np.array(filas)
    print("# Inclinación real de la cámara a partir de las tomas\n")
    print("Cuadros usados (rayo dentro de la persona, pies visibles, 2.5 a 16 m): %d. Altura del lente %.2f m, VFOV %.1f°.\n" % (len(M), h, a.vfov))
    print("| Distancia (m) | Cuadros | y2 mediana | Depresión de los pies φ (°) | Cámara respecto al horizonte (°) | Cabeceo del dron (°) | Cámara respecto al chasis (°) |")
    print("|---:|---:|---:|---:|---:|---:|---:|")
    alfas = []
    for d0, d1 in ((2.5, 3.5), (3.5, 5), (5, 7), (7, 9), (9, 11), (11, 13), (13, 16)):
        m = (M[:, 0] >= d0) & (M[:, 0] < d1)
        if m.sum() < 30:
            continue
        d = float(np.median(M[m, 0]))
        y2 = float(np.median(M[m, 1]))
        pit = float(np.nanmedian(M[m, 2]))
        phi = math.degrees(math.atan2(h, d))
        alfa = phi - math.degrees(math.atan((y2 - 0.5) * 2.0 * tv))        # + = mira hacia abajo
        elev = -alfa
        alfas.append((m.sum(), elev, elev - pit))
        print("| %.1f | %d | %.3f | %.1f | %.2f | %.1f | %.2f |" % (d, m.sum(), y2, phi, elev, pit, elev - pit))
    if alfas:
        w = np.array([x[0] for x in alfas], float)
        print("\nPromedio ponderado: cámara a %.2f° del horizonte; respecto al chasis %.2f° (+ = hacia arriba)." % (
            np.average([x[1] for x in alfas], weights=w), np.average([x[2] for x in alfas], weights=w)))
    print("\nEl rayo del LiDAR (eje a %.2f m) si cae al suelo a distancia D: ángulo = −atan(%.2f / D). Compárese con lo que da la calibración del escritorio (−6.7°)." % (hl, hl))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
