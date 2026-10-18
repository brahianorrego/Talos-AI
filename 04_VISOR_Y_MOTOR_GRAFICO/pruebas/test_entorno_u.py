# -*- coding: utf-8 -*-
r"""Pruebas del entorno de la universidad (entorno/entorno_u.py). Desde la raíz del proyecto:
   03_SIMULACION_RL\.venv\Scripts\python.exe -m unittest discover -s 04_VISOR_Y_MOTOR_GRAFICO/pruebas"""
import json
import math
import os
import sys
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, ".."))
sys.path.insert(0, os.path.join(RAIZ, "entorno"))
import entorno_u as U  # noqa: E402


def dentro(p, r, m=0.0):
    return r[0] - m <= p[0] <= r[2] + m and r[1] - m <= p[1] <= r[3] + m


class TestEntornoU(unittest.TestCase):
    def setUp(self):
        self.E = U.construir()

    def test_las_copias_del_json_estan_al_dia(self):
        for ruta in (os.path.join(RAIZ, "entorno", "entorno_u.json"), os.path.join(RAIZ, "estacion", "entorno_u.json")):
            with open(ruta, encoding="utf-8") as f:
                self.assertEqual(json.load(f), json.loads(json.dumps(self.E)), ruta + " desactualizado: correr entorno/entorno_u.py")

    def test_las_areas_coinciden_con_google_earth(self):
        campo = self.E["campo"]["tam"][0] * self.E["campo"]["tam"][1]
        self.assertAlmostEqual(campo, 6821.78, delta=250, msg="cancha de fútbol medida: 6 821.78 m2")
        tenis = next(c for c in self.E["canchas"] if c["tipo"] == "tenis")
        self.assertAlmostEqual(tenis["tam"][0] * tenis["tam"][1], 694.81, delta=40, msg="cancha de tenis medida: 694.81 m2")

    def test_la_zona_de_ia_esta_dentro_de_las_lineas_y_a_mas_de_10_m_de_los_arboles(self):
        z = self.E["campo"]["zona_ia"] / 2
        J = self.E["campo"]["juego"]
        self.assertTrue(-J["x"] < -z and z < J["x"] and J["y0"] < -z and z < J["y1"], "la zona de 30 x 30 m cabe dentro de las líneas de la cancha")
        for a in self.E["arboles"]:
            d = max(abs(a["p"][0]) - z, abs(a["p"][1]) - z)          # distancia al borde de la zona (norma infinito)
            self.assertGreater(d, 10.0, f"árbol en {a['p']} a menos de 10 m de la zona de IA (D-051)")

    def test_ningun_arbol_ni_auto_sobre_canchas_edificios_o_campo(self):
        c = self.E["campo"]; rc = (c["centro"][0] - c["tam"][0] / 2, c["centro"][1] - c["tam"][1] / 2, c["centro"][0] + c["tam"][0] / 2, c["centro"][1] + c["tam"][1] / 2)
        otros = [U.rect(b["centro"], b["tam"]) for b in self.E["edificios"]] + [U.rect(k["centro"], k["tam"]) for k in self.E["canchas"]]
        for a in self.E["arboles"]:
            self.assertFalse(dentro(a["p"], rc), f"árbol en la cancha {a['p']}")
            for r in otros:
                self.assertFalse(dentro(a["p"], r), f"árbol dentro de un edificio o cancha {a['p']}")
        pq = next(s for s in self.E["suelos"] if s["nombre"] == "parqueadero")
        for k in self.E["carros"]:
            self.assertTrue(dentro(k["p"], U.rect(pq["centro"], pq["tam"])), f"auto fuera del parqueadero {k['p']}")

    def test_hay_suficiente_vegetacion_y_las_dos_poses_del_vuelo(self):
        self.assertGreater(len(self.E["arboles"]), 200)
        self.assertEqual(len({a["tipo"] for a in self.E["arboles"]}), 2)
        P = self.E["poses"]
        self.assertGreater(math.dist(P["campo"]["mira"], P["cancha_cerrada"]["mira"]), 40.0, "las dos vistas apuntan a sitios distintos")
        for n in ("campo", "cancha_cerrada"):
            self.assertGreater(P[n]["pos"][2], 5.0)

    def test_las_canchas_cerradas_estan_cerca_de_la_de_futbol(self):
        c = self.E["campo"]["centro"]
        for k in self.E["canchas"]:
            self.assertLess(math.dist(k["centro"], c), 80.0, k["nombre"])


if __name__ == "__main__":
    unittest.main()
