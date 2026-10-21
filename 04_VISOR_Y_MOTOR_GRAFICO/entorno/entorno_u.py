# -*- coding: utf-8 -*-
"""
El entorno de la universidad como ESPECIFICACIÓN (un JSON con medidas), para que la estación web (estacion/universidad.js) y
Unreal (unreal/entorno_u_ue.py) construyan lo mismo.

Marco (como la simulación): x al ESTE, y al NORTE, z arriba; metros; origen = centro de la zona de IA de 30 x 30 m, que está en
el centro de la mitad NORTE de la cancha de fútbol (D-051).

Redistribución del 21-oct (pedido de Brahian: "que se parezca a la universidad real"): posiciones y tamaños de edificios, canchas, parqueadero,
estanque y vías se midieron sobre una vista satelital (Esri World Imagery, zoom 19, 0.2976 m por píxel a esta latitud) del campus, cotejada con el mapa
oficial de la USB (08_EVIDENCIA_Y_DIAGRAMAS/fotos/universidad_referencia_dia/mapa-USB.pdf) y las vistas aéreas de esa misma carpeta. Los rectángulos van en
PÍXELES de ese mosaico (listas PX_*): así la medición se puede repetir con entorno/mosaico_satelital.py. La imagen satelital NO se guarda en el repositorio
(licencia): solo estas medidas. Se quitó lo que no existe en el campus (torres de 46-66 m, "vestuarios del coliseo", caseta, vía sur, cerros en forma de domo).

  Medidas de Google Earth (Brahian):  cancha de fútbol 6 821.78 m2, perímetro 337.03 m  ->  67 x 102 m (largo N-S)
                                      cancha de tenis    694.81 m2, perímetro 110.4  m  ->  19.5 x 35.7 m (largo N-S)   [se conservan]

Georreferencia: el centro de la cancha de fútbol cae en ORIGEN_LATLON (aprox. ±5 m, por medir con GPS); la estación satelital (estacion/mapa) usa este valor.
Ejecutar este archivo escribe entorno_u.json (aquí y en estacion/). Las pruebas están en pruebas/test_entorno_u.py.
"""
import json
import math
import os
import random

AQUI = os.path.dirname(os.path.abspath(__file__))

# ---- registro de la vista satelital: píxeles del mosaico z19 de 6 x 6 teselas (tesela 0 = 154327, 255212) -> metros del mundo
M_PX = 0.29755                      # metros por píxel (zoom 19 a 4.75° N)
PX_ORIGEN = (913.0, 771.3)          # píxel del origen del mundo (25.5 m al norte del centro de la cancha de fútbol, que está en el píxel (913, 857))
ORIGEN_LATLON = (4.752094, -74.029553)          # lat, lon del CENTRO DE LA CANCHA DE FÚTBOL (el origen del mundo está 25.5 m al norte)
ROTACION_MAPA = 0.0                 # grados que el eje y del mundo gira respecto al norte (cancha alineada con el norte en la vista satelital)


def pm(x, y):
    """Píxel del mosaico -> (x este, y norte) en metros del mundo."""
    return ((x - PX_ORIGEN[0]) * M_PX, (PX_ORIGEN[1] - y) * M_PX)


def caja_px(x0, y0, x1, y1):
    """Rectángulo en píxeles -> (centro, tamaño) en metros."""
    (xa, ya), (xb, yb) = pm(x0, y0), pm(x1, y1)
    return ((round((xa + xb) / 2, 1), round((ya + yb) / 2, 1)), (round(abs(xb - xa), 1), round(abs(ya - yb), 1)))


CAMPO_C = (0.0, -25.5)            # centro de la cancha de fútbol (la zona de IA queda en el centro de su mitad norte)
CAMPO_T = (67.0, 102.0)           # ancho (x) y largo (y)
JUEGO = {"x": 30.0, "y0": CAMPO_C[1] - 48.0, "y1": CAMPO_C[1] + 48.0}      # líneas de la cancha (96 x 60 m dentro de los 67 x 102)


def rect(c, t, margen=0.0):
    return (c[0] - t[0] / 2 - margen, c[1] - t[1] / 2 - margen, c[0] + t[0] / 2 + margen, c[1] + t[1] / 2 + margen)


# ---- edificios: (nombre, rectángulo en píxeles, alto en m, tipo, techo)   techo: None = gris, "terracota", "blanco"
PX_EDIFICIOS = [
    # campus (mapa 3D de la USB: 7 = aeronáutica, 6 = polideportivo, 1-5 = edificios académicos y biblioteca, capilla, cafetería, casa de San Buenaventura)
    ("edificio_aeronautica", (571, 601, 661, 696), 9.0, "laboratorio", None),            # edificio 7, Fray Rogelio Bacon (talleres y laboratorios de aeronáutica)
    ("polideportivo", (614, 773, 744, 894), 11.0, "coliseo", None),                       # edificio 6, Fray Fernando Garzón Ramírez
    ("edificio_1", (580, 1013, 645, 1158), 12.0, "ladrillo", None),
    ("edificio_2", (585, 1163, 640, 1298), 12.0, "ladrillo", None),
    ("edificio_principal", (570, 1308, 655, 1398), 13.0, "ladrillo", "terracota"),
    ("capilla_san_damian", (680, 1070, 745, 1140), 8.0, "ladrillo", "terracota"),
    ("cafeteria", (790, 1056, 840, 1098), 4.5, "ladrillo", "blanco"),
    ("edificio_3", (855, 1123, 935, 1228), 14.0, "ladrillo", "blanco"),
    ("edificio_4", (855, 1235, 935, 1343), 14.0, "ladrillo", "blanco"),
    ("biblioteca", (780, 1203, 845, 1393), 14.0, "ladrillo", None),
    ("edificio_5", (700, 1283, 765, 1468), 14.0, "ladrillo", None),
    ("casa_san_buenaventura", (910, 1338, 1020, 1458), 10.0, "ladrillo", None),
    ("talleres_a", (325, 1028, 395, 1073), 8.0, "ladrillo", None),
    ("talleres_b", (410, 1003, 465, 1158), 8.0, "ladrillo", None),
    ("talleres_c", (285, 1020, 335, 1118), 8.0, "ladrillo", None),
    ("talleres_d", (310, 1078, 408, 1178), 8.0, "ladrillo", None),
    ("talleres_e", (340, 1180, 415, 1235), 7.0, "ladrillo", None),
    ("edificio_noroeste", (360, 150, 548, 322), 10.0, "ladrillo", None),
    # vecinos: conjuntos de casas en hilera de tres pisos (techo gris) al norte, y bloques de cinco pisos al este
    ("hilera_a1", (637, 90, 812, 140), 10.0, "apartamentos", None), ("hilera_a2", (627, 143, 802, 195), 10.0, "apartamentos", None),
    ("hilera_a3", (620, 195, 790, 245), 10.0, "apartamentos", None), ("hilera_a4", (607, 248, 782, 300), 10.0, "apartamentos", None),
    ("hilera_a5", (817, 108, 997, 160), 10.0, "apartamentos", None), ("hilera_a6", (815, 160, 990, 210), 10.0, "apartamentos", None),
    ("hilera_a7", (827, 212, 984, 265), 10.0, "apartamentos", None), ("hilera_a8", (820, 268, 982, 320), 10.0, "apartamentos", None),
    ("hilera_b1", (590, 358, 787, 410), 10.0, "apartamentos", None), ("hilera_b2", (797, 378, 972, 430), 10.0, "apartamentos", None),
    ("hilera_b3", (637, 415, 744, 467), 10.0, "apartamentos", None), ("hilera_b4", (757, 433, 952, 498), 10.0, "apartamentos", None),
    ("hilera_b5", (562, 455, 744, 520), 10.0, "apartamentos", None), ("hilera_b6", (747, 487, 957, 550), 10.0, "apartamentos", None),
    ("hilera_b7", (552, 505, 747, 567), 10.0, "apartamentos", None), ("hilera_b8", (757, 538, 952, 600), 10.0, "apartamentos", None),
    ("bloque_e1", (1222, 127, 1307, 275), 17.0, "apartamentos", None), ("bloque_e2", (1277, 268, 1502, 360), 17.0, "apartamentos", None),
    ("bloque_e3", (1397, 145, 1487, 225), 17.0, "apartamentos", None), ("bloque_e4", (1217, 420, 1437, 470), 14.0, "apartamentos", None),
    ("bloque_e5", (1217, 472, 1412, 525), 14.0, "apartamentos", None),
    ("hilera_e1", (1212, 525, 1257, 650), 11.0, "apartamentos", None), ("hilera_e2", (1277, 535, 1327, 660), 11.0, "apartamentos", None),
    ("hilera_e3", (1330, 535, 1377, 665), 11.0, "apartamentos", None), ("hilera_e4", (1382, 560, 1427, 670), 11.0, "apartamentos", None),
    ("hilera_e5", (1432, 565, 1477, 680), 11.0, "apartamentos", None), ("hilera_e6", (1482, 560, 1532, 690), 11.0, "apartamentos", None),
    ("hilera_se1", (1230, 1017, 1432, 1080), 10.0, "apartamentos", None), ("hilera_se2", (1462, 1035, 1536, 1088), 10.0, "apartamentos", None),
    ("hilera_se3", (1222, 1102, 1417, 1162), 10.0, "apartamentos", None), ("hilera_se4", (1440, 1117, 1536, 1170), 10.0, "apartamentos", None),
    ("hilera_se5", (1200, 1185, 1402, 1252), 10.0, "apartamentos", None), ("hilera_se6", (1425, 1207, 1536, 1275), 10.0, "apartamentos", None),
]
EDIFICIOS = []
for _n, _r, _h, _k, _t in PX_EDIFICIOS:
    _c, _t2 = caja_px(*_r)
    EDIFICIOS.append((_n, _c, _t2, _h, _k, _t))

# ---- suelos: (nombre, rectángulo en píxeles, tipo)
PX_SUELOS = [
    ("parqueadero", (561, 924, 766, 1016), "asfalto"),
    ("patio_adoquin", (650, 1163, 780, 1268), "adoquin"),
    ("cancha_baloncesto", (386, 868, 481, 978), "asfalto"),
    ("via_interna_oeste", (517, 250, 544, 1500), "via"),
    ("via_este", (1135, 560, 1162, 1500), "via"),
    ("via_norte", (560, 325, 1536, 355), "via"),
    ("avenida_oeste", (105, 0, 165, 1536), "via"),
]
SUELOS = [(n,) + caja_px(*r) + (k,) for n, r, k in PX_SUELOS]
SUELOS.append(("plaza_avion", (-96.0, 11.0), (22.0, 22.0), "adoquin"))          # adoquín bajo el avión Searca y la turbina (fotos de exhibición)
SUELOS.append(("acera_cancha_cerrada", (-57.0, 7.5), (42.0, 3.0), "adoquin"))

# ---- canchas cerradas junto al edificio de aeronáutica (el tamaño del tenis es el medido en Google Earth)
CANCHAS = [
    ("tenis", (-65.5, 28.4), (19.5, 36.0), "tenis"),
    ("multiple", (-48.2, 28.4), (14.0, 34.0), "multiple"),
]
ESTANQUE = ("estanque", caja_px(974, 1021, 1056, 1136))          # lago pequeño al sureste de la cancha de fútbol (mapa 3D y aérea del lago)
CERROS = [      # los cerros orientales: lejos (2.5 km al este) y bajos, para que se vean como una cresta y no como un domo pegado al campus
    ((2800.0, -400.0), (1400.0, 1000.0), 300.0), ((2700.0, 1100.0), (1300.0, 800.0), 340.0), ((2600.0, -1700.0), (1300.0, 800.0), 260.0),
]
MOTOR = {"nombre": "motor_de_avion", "p": [-86.0, 12.0], "rot": 20.0}      # escultura de turbina: junto al edificio de aeronáutica (7), en la plaza al sur; no en el centro del campus
AVION = {"nombre": "avion_searca", "p": [-98.0, 9.0], "rot": 0.0}          # avión Searca en exhibición (foto avion_searca_exhibicion.webp): sobre el adoquín de la plaza, nariz al este


def vallas():
    """Mallas y muros: el cerco de las canchas cerradas y el muro del costado este del campo."""
    t, m = CANCHAS[0], CANCHAS[1]
    x0, x1, y0, y1 = t[1][0] - t[2][0] / 2 - 1.5, m[1][0] + m[2][0] / 2 + 1.5, t[1][1] - 20.0, t[1][1] + 20.0
    return [
        {"nombre": "cerco_canchas", "tipo": "malla", "alto": 10.0, "cerrado": True, "p": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]},      # malla de unos 10 m alrededor de las canchas
        {"nombre": "malla_divisoria", "tipo": "malla", "alto": 10.0, "cerrado": False, "p": [[(t[1][0] + m[1][0]) / 2 + 0.2, y0], [(t[1][0] + m[1][0]) / 2 + 0.2, y1]]},
        {"nombre": "muro_este_campo", "tipo": "muro", "alto": 1.9, "cerrado": False, "p": [[50.0, -80.0], [50.0, 28.0]]},
    ]


def libre(x, y, prohibidos, margen):
    return all(not (a - margen <= x <= c + margen and b - margen <= y <= d + margen) for a, b, c, d in prohibidos)


# ---- zonas de árboles leídas de la vista satelital: (rectángulo en píxeles, cantidad, "cipres" para las hileras de ciprés)
PX_ARBOLES = [
    ((1, 1, 1, 1), 0, None),
    ((450, 577, 518, 1035), 36, "cipres"),         # hilera de cipreses al oeste de la vía interna (la cortina oscura del mapa)
    ((600, 1008, 780, 1050), 14, None), ((225, 1260, 495, 1500), 40, None), ((720, 1035, 840, 1140), 10, None), ((960, 1005, 1080, 1140), 10, None),
    ((982, 450, 1110, 660), 18, None), ((975, 345, 1170, 495), 16, None), ((560, 328, 1536, 352), 22, None), ((0, 780, 90, 1500), 14, None),
    ((255, 0, 540, 75), 12, None), ((796, 636, 1096, 686), 4, None), ((640, 1140, 700, 1300), 6, None), ((1090, 560, 1130, 1000), 14, "cipres"),
]
ZONAS_M = [(-47.0, -76.0, -36.0, -10.0, 14, "cipres")]       # cipreses que bordean el costado oeste de la cancha de fútbol (fotos del campo)


def arboles(semilla=2026):
    r = random.Random(semilla)
    prohibidos = [rect(CAMPO_C, CAMPO_T, 4.0)]
    prohibidos += [rect(c, t, 2.0) for _, c, t, _, _, _ in EDIFICIOS] + [rect(c, t, 1.0) for n, c, t, _ in SUELOS if n in ("parqueadero", "patio_adoquin", "cancha_baloncesto")]
    prohibidos += [rect(c, t, 3.0) for _, c, t, _ in CANCHAS] + [rect(ESTANQUE[1][0], ESTANQUE[1][1], 1.0)]
    prohibidos += [rect(c, t, 0.5) for n, c, t, _ in SUELOS if n.startswith("via") or n.startswith("avenida") or n.startswith("acera")]
    prohibidos += [(-77.5, 8.0, -39.0, 49.5)]
    zonas = []
    for rpx, n, k in PX_ARBOLES:
        if n:
            (cx, cy), (w, h) = caja_px(*rpx)
            zonas.append((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, n, k))
    zonas += ZONAS_M
    lista = []
    for x0, y0, x1, y1, n, k in zonas:
        puestos, intentos = 0, 0                                      # el tope de intentos es por zona (una zona llena no gasta las demás)
        while puestos < n and intentos < 4000:
            intentos += 1
            x, y = r.uniform(x0, x1), r.uniform(y0, y1)
            if not libre(x, y, prohibidos, 0.0) or any(math.hypot(x - a["p"][0], y - a["p"][1]) < 4.5 for a in lista):
                continue
            tipo = "cipres" if (k == "cipres" or (k is None and r.random() < 0.15)) else "frondoso"
            lista.append({"p": [round(x, 2), round(y, 2)], "alto": round(r.uniform(9.0, 15.0) if tipo == "cipres" else r.uniform(8.0, 14.0), 2),
                          "copa": round(r.uniform(2.2, 3.2) if tipo == "cipres" else r.uniform(3.5, 5.5), 2), "semilla": round(r.random(), 3), "tipo": tipo})
            puestos += 1
    return lista


def carros(semilla=7):
    """Unos 12 autos en el parqueadero (en la vista satelital está casi vacío; las filas siguen las rayas)."""
    r = random.Random(semilla)
    colores = [(0.80, 0.80, 0.80), (0.02, 0.02, 0.025), (0.45, 0.46, 0.48), (0.55, 0.03, 0.03), (0.04, 0.12, 0.45), (0.90, 0.90, 0.90), (0.15, 0.15, 0.17)]
    lista = []
    p = next(s for s in SUELOS if s[0] == "parqueadero")
    cx, cy = p[1]
    for fila in range(4):
        y = cy - 8.5 + fila * 5.6
        for k in range(15):
            if r.random() < 0.62 or (fila in (1, 2) and abs(k - 7) < 1.2):
                continue
            lista.append({"p": [round(cx - 24.5 + k * 3.6 + r.uniform(-0.2, 0.2), 2), round(y + r.uniform(-0.2, 0.2), 2)], "rot": 90.0 if fila % 2 == 0 else 270.0,
                          "color": list(r.choice(colores))})
    return lista


def poses():
    """Las dos vistas de la tecla de vuelo: una sobre la zona de IA y otra sobre las canchas cerradas."""
    return {"campo": {"nombre": "Cancha de fútbol (zona de IA)", "pos": [26.0, -40.0, 15.0], "mira": [0.0, 0.0, 1.5]},
            "cancha_cerrada": {"nombre": "Cancha cerrada (tenis y múltiple)", "pos": [-38.0, -2.0, 13.0], "mira": [-60.0, 28.0, 1.5]},
            "altura_de_vuelo": 55.0, "segundos": 7.0}


def construir():
    return {
        "nombre": "Universidad de San Buenaventura, Bogotá · cancha de fútbol y canchas cerradas", "unidades": "m",
        "marco": "x este, y norte, z arriba; origen = centro de la zona de IA (30 x 30 m) en la mitad norte de la cancha de fútbol",
        "fuente": "vista satelital z19 (Esri World Imagery), mapa-USB.pdf y 08_EVIDENCIA_Y_DIAGRAMAS/fotos/universidad_referencia_dia; aproximado (±3 m), por medir con GPS",
        "georef": {"centro_campo_latlon": list(ORIGEN_LATLON), "origen_desde_centro_campo_m": [0.0, 25.5], "rotacion_grados": ROTACION_MAPA, "metros_por_pixel_z19": M_PX},
        "campo": {"centro": list(CAMPO_C), "tam": list(CAMPO_T), "juego": JUEGO, "zona_ia": 30.0},
        "canchas": [{"nombre": n, "centro": list(c), "tam": list(t), "tipo": k} for n, c, t, k in CANCHAS],
        "edificios": [dict({"nombre": n, "centro": list(c), "tam": list(t), "alto": h, "tipo": k}, **({"techo": tc} if tc else {})) for n, c, t, h, k, tc in EDIFICIOS],
        "suelos": [{"nombre": n, "centro": list(c), "tam": list(t), "tipo": k} for n, c, t, k in SUELOS],
        "agua": [{"nombre": ESTANQUE[0], "centro": list(ESTANQUE[1][0]), "tam": list(ESTANQUE[1][1])}],
        "vallas": vallas(), "arboles": arboles(), "carros": carros(),
        "cerros": [{"centro": list(c), "radio": list(r), "alto": h} for c, r, h in CERROS],
        "extras": [MOTOR], "avion": AVION,
        "poses": poses(),
    }


if __name__ == "__main__":
    datos = construir()
    for destino in (os.path.join(AQUI, "entorno_u.json"), os.path.join(AQUI, "..", "estacion", "entorno_u.json")):
        with open(destino, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=1)
    print(f"{len(datos['edificios'])} edificios · {len(datos['arboles'])} árboles · {len(datos['carros'])} autos · {len(datos['cerros'])} cerros")
