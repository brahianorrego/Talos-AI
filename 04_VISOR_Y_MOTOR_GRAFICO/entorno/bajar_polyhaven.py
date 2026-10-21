# -*- coding: utf-8 -*-
"""
Baja de Poly Haven (polyhaven.com, licencia CC0: libre, sin cuenta ni permisos de administrador) las texturas PBR reales para el campus de Unreal:
ladrillo, pasto, asfalto, adoquín, losas con pasto entre ellas y concreto. Guarda color, normal, rugosidad y AO a 2K en 04_VISOR_Y_MOTOR_GRAFICO/assets_polyhaven/<id>/
(carpeta fuera de Git). Uso:  03_SIMULACION_RL\\.venv\\Scripts\\python.exe 04_VISOR_Y_MOTOR_GRAFICO\\entorno\\bajar_polyhaven.py
"""
import json
import os
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.normpath(os.path.join(AQUI, "..", "assets_polyhaven"))
ASSETS = {                                     # id de Poly Haven: para qué se usa en el campus
    "red_brick_03": "fachadas de ladrillo",
    "leafy_grass": "pasto de las zonas verdes",
    "asphalt_04": "parqueadero y vías",
    "patterned_paving": "adoquín de las plazas",
    "grass_concrete_pavement": "losas de concreto con pasto entre ellas",
    "concrete_pavement": "concreto liso (bordes, bases)",
}
MAPAS = {"Diffuse": "color", "nor_gl": "normal", "Rough": "rugosidad", "AO": "ao"}
UA = {"User-Agent": "DronIA-proyecto-de-grado/1.0"}


def pedir(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()


def main():
    for aid, uso in ASSETS.items():
        carpeta = os.path.join(SALIDA, aid)
        os.makedirs(carpeta, exist_ok=True)
        archivos = json.loads(pedir(f"https://api.polyhaven.com/files/{aid}"))
        for clave, nombre in MAPAS.items():
            try:
                u = archivos[clave]["2k"]["jpg"]["url"]
            except KeyError:
                print(aid, clave, "no existe a 2K en jpg")
                continue
            destino = os.path.join(carpeta, nombre + ".jpg")
            if not os.path.exists(destino):
                open(destino, "wb").write(pedir(u))
            print(aid, nombre, os.path.getsize(destino) // 1024, "KB")
        open(os.path.join(carpeta, "LICENCIA.txt"), "w", encoding="utf-8").write(f"{aid}: Poly Haven (https://polyhaven.com/a/{aid}), licencia CC0. Uso en el proyecto: {uso}.\n")


if __name__ == "__main__":
    main()
