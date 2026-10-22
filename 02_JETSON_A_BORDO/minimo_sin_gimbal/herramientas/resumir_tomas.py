# -*- coding: utf-8 -*-
"""
Resumen rápido de las tomas del paso 4, para mostrar resultados en la demostración. Corre en el PC (solo Python estándar).
Uso:  python resumir_tomas.py <carpeta con registros\\AAAAMMDD_HHMMSS ...>      (la que baja `scp -r ...registros .`)
Por cada toma: filas, FPS, % de cuadros con persona, primera detección (tiempo y distancia del LiDAR), distancia mínima del LiDAR y ancho de la caja.
No juzga ni estima exactitud: son medidas crudas por toma. Escribe resumen_tomas.csv junto a la carpeta dada.
"""
import csv
import glob
import os
import sys


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def resumir(ruta):
    filas = []
    for d in sorted(glob.glob(os.path.join(ruta, "**", "datos.csv"), recursive=True)):
        with open(d, encoding="utf-8") as fh:
            filas += list(csv.DictReader(fh))
    tomas = {}
    for r in filas:
        if r.get("toma_id"):
            tomas.setdefault(r["toma_id"], []).append(r)
    out = []
    for tid, rs in tomas.items():
        t0, t1 = f(rs[0]["t"]), f(rs[-1]["t"])
        dur = t1 - t0
        con = [r for r in rs if (f(r.get("personas")) or 0) > 0]
        lid = [(f(r.get("lidar_cm")), r) for r in rs if f(r.get("lidar_cm")) and r.get("lidar_valido") == "1"]
        primera = con[0] if con else None
        anchos = [f(r.get("ancho_norm")) for r in con if f(r.get("ancho_norm"))]
        out.append(dict(
            toma=tid, escenario=rs[0]["escenario"], rep=rs[0]["repeticion"], altura_m=rs[0]["altura_camara_m"], montaje=rs[0]["montaje"], nota=rs[0]["nota"],
            filas=len(rs), duracion_s=round(dur, 1), fps=round(len(rs) / dur, 1) if dur > 0 else "",
            con_persona_pct=round(100.0 * len(con) / len(rs), 1),
            primera_deteccion_s=round(f(primera["t"]) - t0, 1) if primera else "",
            lidar_en_primera_cm=primera.get("lidar_cm") if primera else "",
            lidar_min_cm=int(min(v for v, _ in lid)) if lid else "",
            ancho_caja_max=round(max(anchos), 3) if anchos else "",
            yolo_ms_medio=round(sum(f(r["lat_yolo_ms"]) for r in rs if f(r.get("lat_yolo_ms"))) / max(1, sum(1 for r in rs if f(r.get("lat_yolo_ms")))), 1),
        ))
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    res = resumir(sys.argv[1])
    if not res:
        raise SystemExit("no encontré tomas con toma_id en %s" % sys.argv[1])
    cols = list(res[0].keys())
    print(" | ".join(cols))
    for r in res:
        print(" | ".join(str(r[c]) for c in cols))
    destino = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), "resumen_tomas.csv")
    with open(destino, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(res)
    print("\n%d tomas. Escrito %s" % (len(res), destino))
