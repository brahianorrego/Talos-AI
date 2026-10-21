# -*- coding: utf-8 -*-
"""Baja a disco (mapa/teselas/) las teselas satelitales de Esri del campus para que la estación muestre el mapa SIN internet.
Atribución obligatoria en el mapa: Esri, Maxar, Earthstar Geographics. Uso académico, caché local (no se sube al repositorio).
    03_SIMULACION_RL\\.venv\Scripts\python.exe 04_VISOR_Y_MOTOR_GRAFICO\estacion\mapa\precargar_teselas.py [radio_en_metros=450]
"""
import json
import math
import os
import sys
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
E = json.load(open(os.path.join(AQUI, "..", "entorno_u.json"), encoding="utf-8"))
LAT, LON = E["georef"]["centro_campo_latlon"]
R = float(sys.argv[1]) if len(sys.argv) > 1 else 450.0


def tesela(lat, lon, z):
    n = 2 ** z
    return int((lon + 180) / 360 * n), int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)


total = nuevas = 0
for z in range(15, 20):
    dlat, dlon = R / 111320.0, R / (111320.0 * math.cos(math.radians(LAT)))
    x0, y1 = tesela(LAT - dlat, LON - dlon, z)
    x1, y0 = tesela(LAT + dlat, LON + dlon, z)
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            ruta = os.path.join(AQUI, "teselas", str(z), str(x), f"{y}.jpg")
            total += 1
            if os.path.isfile(ruta):
                continue
            try:
                req = urllib.request.Request(f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                                             headers={"User-Agent": "TALOS-AI-estacion/1.0 (proyecto de grado, uso academico)"})
                datos = urllib.request.urlopen(req, timeout=15).read()
                os.makedirs(os.path.dirname(ruta), exist_ok=True)
                open(ruta, "wb").write(datos)
                nuevas += 1
            except OSError as e:
                print("falló", z, x, y, e)
print(f"{total} teselas en el área ({nuevas} nuevas) · radio {R:.0f} m · centro {LAT:.5f}, {LON:.5f}")
