# -*- coding: utf-8 -*-
"""
El entorno de la universidad como ESPECIFICACIÓN (un JSON con medidas), para que la estación web (estacion/universidad.js) y
Unreal (unreal/entorno_u_ue.py) construyan lo mismo. Hecho con las fotos y las mediciones de Google Earth que subió Brahian
(08_EVIDENCIA_Y_DIAGRAMAS/privado/sitio_universidad/, carpeta PRIVADA: el JSON solo trae medidas, nada de fotos).

Marco (como la simulación): x al ESTE, y al NORTE, z arriba; metros; origen = centro de la zona de IA de 30 x 30 m, que está en
el centro de la mitad NORTE de la cancha de fútbol (D-051). Las posiciones salen de las imágenes de satélite (norte arriba) con la
escala de las dos mediciones; son aproximaciones, no planos (por medir con cinta o GPS).

  Medidas de Google Earth:  cancha de fútbol 6 821.78 m2, perímetro 337.03 m  ->  67 x 102 m (largo N-S)
                            cancha de tenis    694.81 m2, perímetro 110.4  m  ->  19.5 x 35.7 m (largo N-S)

Ejecutar este archivo escribe entorno_u.json (aquí y en estacion/). Las pruebas están en pruebas/test_entorno_u.py.
"""
import json
import math
import os
import random

AQUI = os.path.dirname(os.path.abspath(__file__))

CAMPO_C = (0.0, -25.5)            # centro de la cancha de fútbol (la zona de IA queda en el centro de su mitad norte)
CAMPO_T = (67.0, 102.0)           # ancho (x) y largo (y)
JUEGO = {"x": 30.0, "y0": CAMPO_C[1] - 48.0, "y1": CAMPO_C[1] + 48.0}      # líneas de la cancha (96 x 60 m dentro de los 67 x 102)


def rect(c, t, margen=0.0):
    return (c[0] - t[0] / 2 - margen, c[1] - t[1] / 2 - margen, c[0] + t[0] / 2 + margen, c[1] + t[1] / 2 + margen)


EDIFICIOS = [
    # nombre, centro, tamaño (x, y), alto, tipo
    ("coliseo", (-70.0, -26.9), (39.5, 34.5), 11.0, "coliseo"),
    ("vestuarios_del_coliseo", (-70.0, -2.0), (31.0, 8.0), 6.5, "ladrillo"),
    ("laboratorio", (-88.0, 29.0), (23.0, 26.0), 8.5, "laboratorio"),
    ("caseta_parqueadero", (-99.0, -71.0), (3.6, 3.0), 2.8, "caseta"),
    ("bloque_norte_1", (-62.0, 53.0), (24.0, 15.0), 15.0, "apartamentos"),
    ("bloque_norte_2", (-34.0, 53.0), (24.0, 15.0), 15.0, "apartamentos"),
    ("bloque_norte_3", (-6.0, 53.0), (24.0, 15.0), 15.0, "apartamentos"),
    ("bloque_norte_4", (22.0, 53.0), (24.0, 15.0), 15.0, "apartamentos"),
    ("bloque_este_1", (88.0, -48.0), (16.0, 24.0), 15.0, "apartamentos"),
    ("bloque_este_2", (88.0, -78.0), (16.0, 24.0), 15.0, "apartamentos"),
    ("torre_1", (135.0, 70.0), (20.0, 20.0), 58.0, "torre"),
    ("torre_2", (165.0, -15.0), (20.0, 20.0), 66.0, "torre"),
    ("torre_3", (125.0, -125.0), (20.0, 20.0), 52.0, "torre"),
    ("torre_4", (45.0, -135.0), (18.0, 18.0), 46.0, "torre"),
    ("torre_5", (-30.0, 125.0), (20.0, 20.0), 50.0, "torre"),
]
SUELOS = [
    ("parqueadero", (-70.6, -59.1), (55.0, 25.0), "asfalto"),
    ("camino_peatonal", (-52.0, -46.0), (3.0, 40.0), "adoquin"),
    ("via_este", (56.0, -30.0), (8.0, 260.0), "via"),
    ("via_oeste", (-108.0, -20.0), (8.0, 260.0), "via"),
    ("via_sur", (-20.0, -112.0), (330.0, 8.0), "via"),
    ("acera_cancha_cerrada", (-56.0, 0.8), (40.0, 3.0), "adoquin"),
]
CANCHAS = [
    # nombre, centro, tamaño (x, y), tipo
    ("tenis", (-62.5, 23.5), (19.5, 36.0), "tenis"),
    ("multiple", (-45.3, 22.1), (14.0, 30.0), "multiple"),
]
CERROS = [      # (centro x, y), radios (x, y), alto: los cerros orientales, grandes al este y bajos al oeste
    ((1300.0, -700.0), (900.0, 600.0), 520.0), ((1250.0, 100.0), (900.0, 700.0), 620.0), ((1200.0, 850.0), (850.0, 600.0), 480.0),
    ((600.0, 1500.0), (800.0, 500.0), 260.0), ((-900.0, 1400.0), (700.0, 500.0), 220.0), ((-1500.0, -200.0), (700.0, 800.0), 200.0),
    ((-700.0, -1500.0), (800.0, 500.0), 240.0), ((400.0, -1600.0), (900.0, 500.0), 300.0),
]


def vallas():
    """Mallas y muros: el cerco de las canchas cerradas, el muro oscuro del costado este del campo y la malla del parqueadero."""
    return [
        {"nombre": "cerco_canchas", "tipo": "malla", "alto": 4.5, "cerrado": True,
         "p": [[-74.0, 3.8], [-37.6, 3.8], [-37.6, 39.0], [-74.0, 39.0]]},
        {"nombre": "muro_este_campo", "tipo": "muro", "alto": 1.9, "cerrado": False, "p": [[38.0, -80.0], [38.0, 28.0]]},
        {"nombre": "malla_parqueadero", "tipo": "malla", "alto": 2.4, "cerrado": False, "p": [[-98.0, -72.0], [-98.0, -47.0], [-43.0, -47.0]]},
    ]


def libre(x, y, prohibidos, margen):
    return all(not (a - margen <= x <= c + margen and b - margen <= y <= d + margen) for a, b, c, d in prohibidos)


def arboles(semilla=2026):
    r = random.Random(semilla)
    prohibidos = [rect(CAMPO_C, CAMPO_T, 4.0)]
    prohibidos += [rect(c, t, 2.5) for _, c, t, _, _ in EDIFICIOS] + [rect(c, t, 1.5) for _, c, t, _ in SUELOS if _ in ("parqueadero", "camino_peatonal")]
    prohibidos += [rect(c, t, 3.0) for _, c, t, _ in CANCHAS] + [(-74.5, 3.3, -37.1, 39.5)]
    prohibidos += [rect(c, t, 0.5) for n, c, t, _ in SUELOS if n.startswith("via") or n.startswith("acera")]
    zonas = [(39, -102, 52, 42, 80), (-40, -102, 56, -86, 40), (-42, 28, 42, 42, 32), (-82, 4, -74, 46, 14),          # alrededor del campo y de las canchas
             (-36, 0, -33, 30, 8), (-112, -100, -100, 70, 18), (-98, -82, -44, -46, 14), (-44, -100, -34, -50, 12),
             (60, -110, 80, 60, 20), (-30, 62, 50, 90, 25), (-190, -100, -112, 100, 70), (60, 70, 120, 140, 30)]
    lista = []
    for x0, y0, x1, y1, n in zonas:
        puestos, intentos = 0, 0                                      # el tope de intentos es por zona (una zona llena no gasta las demás)
        while puestos < n and intentos < 4000:
            intentos += 1
            x, y = r.uniform(x0, x1), r.uniform(y0, y1)
            if not libre(x, y, prohibidos, 0.0) or any(math.hypot(x - a["p"][0], y - a["p"][1]) < 4.5 for a in lista):
                continue
            tipo = "cipres" if r.random() < 0.22 else "frondoso"
            lista.append({"p": [round(x, 2), round(y, 2)], "alto": round(r.uniform(9.0, 15.0) if tipo == "cipres" else r.uniform(8.0, 14.0), 2),
                          "copa": round(r.uniform(2.2, 3.2) if tipo == "cipres" else r.uniform(3.5, 5.5), 2), "semilla": round(r.random(), 3), "tipo": tipo})
            puestos += 1
    return lista


def carros(semilla=7):
    """Unos 40 autos en filas dentro del parqueadero (las filas, a ojo de la foto 2)."""
    r = random.Random(semilla)
    colores = [(0.80, 0.80, 0.80), (0.02, 0.02, 0.025), (0.45, 0.46, 0.48), (0.55, 0.03, 0.03), (0.04, 0.12, 0.45), (0.90, 0.90, 0.90), (0.15, 0.15, 0.17)]
    lista = []
    cx, cy = -70.6, -59.1
    for fila in range(4):
        y = cy - 8.5 + fila * 5.6
        for k in range(14):
            if r.random() < 0.28 or (fila in (1, 2) and abs(k - 6.5) < 1.2):      # el pasillo y algunos puestos vacíos
                continue
            lista.append({"p": [round(cx - 24 + k * 3.6 + r.uniform(-0.2, 0.2), 2), round(y + r.uniform(-0.2, 0.2), 2)], "rot": 90.0 if fila % 2 == 0 else 270.0,
                          "color": list(r.choice(colores))})
    return lista


def poses():
    """Las dos vistas de la tecla de vuelo: una sobre la zona de IA y otra sobre las canchas cerradas."""
    return {"campo": {"nombre": "Cancha de fútbol (zona de IA)", "pos": [26.0, -40.0, 15.0], "mira": [0.0, 0.0, 1.5]},
            "cancha_cerrada": {"nombre": "Cancha cerrada (tenis y múltiple)", "pos": [-28.0, -6.0, 13.0], "mira": [-54.0, 22.0, 1.5]},
            "altura_de_vuelo": 55.0, "segundos": 7.0}


def construir():
    return {
        "nombre": "Universidad de San Buenaventura, Bogotá · cancha de fútbol y canchas cerradas", "unidades": "m",
        "marco": "x este, y norte, z arriba; origen = centro de la zona de IA (30 x 30 m) en la mitad norte de la cancha de fútbol",
        "fuente": "08_EVIDENCIA_Y_DIAGRAMAS/privado/sitio_universidad (Google Earth y fotos de Brahian); aproximado, por medir",
        "campo": {"centro": list(CAMPO_C), "tam": list(CAMPO_T), "juego": JUEGO, "zona_ia": 30.0},
        "canchas": [{"nombre": n, "centro": list(c), "tam": list(t), "tipo": k} for n, c, t, k in CANCHAS],
        "edificios": [{"nombre": n, "centro": list(c), "tam": list(t), "alto": h, "tipo": k} for n, c, t, h, k in EDIFICIOS],
        "suelos": [{"nombre": n, "centro": list(c), "tam": list(t), "tipo": k} for n, c, t, k in SUELOS],
        "vallas": vallas(), "arboles": arboles(), "carros": carros(),
        "cerros": [{"centro": list(c), "radio": list(r), "alto": h} for c, r, h in CERROS],
        "extras": [{"nombre": "motor_de_avion", "p": [-51.0, 0.0], "rot": 20.0}],
        "poses": poses(),
    }


if __name__ == "__main__":
    datos = construir()
    for destino in (os.path.join(AQUI, "entorno_u.json"), os.path.join(AQUI, "..", "estacion", "entorno_u.json")):
        with open(destino, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=1)
    print(f"{len(datos['edificios'])} edificios · {len(datos['arboles'])} árboles · {len(datos['carros'])} autos · {len(datos['cerros'])} cerros")
