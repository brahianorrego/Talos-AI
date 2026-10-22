# -*- coding: utf-8 -*-
"""
Analiza las tomas del paso 4 que dejó registro_minimo.py (datos.csv con las columnas de toma) y arma:
  - una tabla por toma (cuadros, fps, % con persona, primera detección, LiDAR, % del rayo dentro de la caja, inclinación del dron),
  - la geometría del montaje: inclinación del dron (Pixhawk) y distancia a la que el rayo toca el suelo,
  - el ángulo real del rayo del LiDAR respecto al chasis, si se da la altura del eje del LiDAR.

Uso (en el PC, con cualquier Python 3 con numpy):
    python analizar_campo.py CARPETA_DE_LA_SESION [CARPETA2 ...] --altura-lidar 1.83 [--salida resumen.md]
Cada carpeta lleva datos.csv. Solo lectura.
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


def leer(ruta):
    with open(ruta, encoding="utf-8", newline="") as f:
        filas = list(csv.DictReader(f))
    return filas


def tomas_de(filas):
    """Agrupa los cuadros por (toma, línea/fase): las del E1 cambian de marca dentro de la misma toma."""
    grupos = {}
    for r in filas:
        tid = r.get("toma_id") or ""
        if not tid:
            continue
        grupos.setdefault((tid, r.get("distancia_m", "")), []).append(r)
    return grupos


def resumen_toma(rows):
    t = np.array([num(r["t"]) for r in rows])
    dur = max(t[-1] - t[0], 1e-6) if len(t) > 1 else NAN
    pers = np.array([num(r["personas"]) for r in rows]) > 0
    lid = np.array([num(r["lidar_cm"]) for r in rows]) / 100.0
    val = np.array([num(r["lidar_valido"]) for r in rows]) == 1
    caja = np.array([num(r["lidar_en_caja"]) for r in rows])
    pit = np.array([num(r["cabeceo_deg"]) for r in rows])
    rol = np.array([num(r["alabeo_deg"]) for r in rows])
    alto = np.array([num(r["alto_norm"]) for r in rows])
    first = float(t[np.argmax(pers)] - t[0]) if pers.any() else NAN
    lv = lid[val & ~np.isnan(lid)]
    return dict(n=len(rows), dur=dur, fps=len(rows) / dur if dur == dur else NAN, pers=100 * pers.mean(), primera=first,
                lid_pers=100 * (val & pers).sum() / max(pers.sum(), 1) if pers.any() else NAN,
                en_caja=100 * np.nansum(caja[pers]) / max(pers.sum(), 1) if pers.any() else NAN,
                lid_min=float(lv.min()) if len(lv) else NAN, lid_med=float(np.median(lv)) if len(lv) else NAN, lid_max=float(lv.max()) if len(lv) else NAN,
                pit=float(np.nanmean(pit)) if np.isfinite(pit).any() else NAN, rol=float(np.nanmean(rol)) if np.isfinite(rol).any() else NAN,
                alto_max=float(np.nanmax(alto)) if np.isfinite(alto).any() else NAN)


def fmt(x, d=1):
    return "–" if x != x else ("%.*f" % (d, x))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("carpetas", nargs="+")
    ap.add_argument("--altura-lidar", type=float, default=0.0, help="altura del eje del LiDAR sobre el suelo, en metros (0 = no calcular el ángulo)")
    ap.add_argument("--salida", default="")
    a = ap.parse_args()
    out = []
    P = out.append
    todas = []
    for c in a.carpetas:
        filas = leer(os.path.join(c, "datos.csv"))
        todas.append((os.path.basename(os.path.normpath(c)), filas))

    P("# Análisis de las tomas de campo\n")
    for nombre, filas in todas:
        P("## Sesión `%s` · %d cuadros\n" % (nombre, len(filas)))
        gr = tomas_de(filas)
        P("| Toma | Marca | Altura lente | Cuadros | fps | % con persona | 1.ª detección (s) | LiDAR en persona (%) | Rayo dentro de la caja (%) | LiDAR mín / mediana / máx (m) | Cabeceo medio (°) | Alabeo medio (°) |")
        P("|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|")
        for (tid, marca), rows in sorted(gr.items(), key=lambda kv: num(kv[1][0]["t"])):
            s = resumen_toma(rows)
            if s["n"] < 5:
                continue
            P("| %s | %s | %s | %d | %s | %s | %s | %s | %s | %s / %s / %s | %s | %s |" % (
                tid, marca, rows[0].get("altura_camara_m", ""), s["n"], fmt(s["fps"]), fmt(s["pers"], 0), fmt(s["primera"]), fmt(s["lid_pers"], 0), fmt(s["en_caja"], 0),
                fmt(s["lid_min"]), fmt(s["lid_med"]), fmt(s["lid_max"]), fmt(s["pit"]), fmt(s["rol"])))
        P("")

    # --- geometría: inclinación y distancia del suelo
    P("## Geometría del montaje\n")
    for nombre, filas in todas:
        pit = np.array([num(r["cabeceo_deg"]) for r in filas]); lid = np.array([num(r["lidar_cm"]) for r in filas]) / 100.0
        val = np.array([num(r["lidar_valido"]) for r in filas]) == 1; pers = np.array([num(r["personas"]) for r in filas]) > 0
        en_toma = np.array([bool(r.get("toma_id")) for r in filas])
        P("### `%s`" % nombre)
        if np.isfinite(pit).any():
            P("- Cabeceo del dron durante la sesión: mediana %.1f°, rango %.1f° a %.1f° (+ = nariz arriba)." % (np.nanmedian(pit), np.nanmin(pit), np.nanmax(pit)))
            if en_toma.any():
                p2 = pit[en_toma]
                P("- Cabeceo durante las tomas: mediana %.1f°, p5 %.1f°, p95 %.1f°." % (np.nanmedian(p2), np.nanpercentile(p2, 5), np.nanpercentile(p2, 95)))
        # el suelo: lecturas válidas sin persona, entre 5 y 30 m, agrupadas por cabeceo
        m = val & ~pers & (lid > 5) & (lid < 30) & np.isfinite(pit)
        if m.sum() > 50:
            cuartos = np.nanpercentile(pit[m], [0, 25, 50, 75, 100])
            P("- Lecturas del LiDAR sin persona (5-30 m): %d; mediana %.2f m, p10 %.2f m, p90 %.2f m." % (m.sum(), np.median(lid[m]), np.percentile(lid[m], 10), np.percentile(lid[m], 90)))
            if a.altura_lidar > 0:
                # a cada nivel de cabeceo, la moda de la distancia es el suelo si el rayo baja
                bins = np.arange(np.floor(np.nanmin(pit[m])), np.ceil(np.nanmax(pit[m])) + 1.0, 1.0)
                P("")
                P("| Cabeceo (°) | Lecturas | Distancia mediana (m) | Ángulo del rayo sobre el horizonte (°) | Ángulo respecto al chasis (°) |")
                P("|---:|---:|---:|---:|---:|")
                for b0 in bins[:-1]:
                    mm = m & (pit >= b0) & (pit < b0 + 1)
                    if mm.sum() < 40:
                        continue
                    d = float(np.median(lid[mm]))
                    elev = -math.degrees(math.atan2(a.altura_lidar, d))
                    P("| %.0f a %.0f | %d | %.2f | %.2f | %.2f |" % (b0, b0 + 1, mm.sum(), d, elev, elev - (b0 + 0.5)))
                P("")
                P("(Si el rayo cae al suelo, ángulo = −atan(altura / distancia). Respecto al chasis = ese ángulo menos el cabeceo del dron. Lo medido en el escritorio fue −6.7°.)")
        P("")
    texto = "\n".join(out)
    if a.salida:
        with open(a.salida, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    sys.stdout.buffer.write((texto + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
