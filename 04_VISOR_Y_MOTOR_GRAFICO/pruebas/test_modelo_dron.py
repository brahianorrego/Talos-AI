# -*- coding: utf-8 -*-
"""Pruebas del modelo 3D del dron (04_VISOR_Y_MOTOR_GRAFICO/modelo_dron). Correr desde la raíz del proyecto:
   03_SIMULACION_RL\.venv\Scripts\python.exe -m unittest discover -s 04_VISOR_Y_MOTOR_GRAFICO/pruebas"""
import json
import os
import sys
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, ".."))
sys.path.insert(0, os.path.join(RAIZ, "modelo_dron"))
import dron_real  # noqa: E402

COPIAS = [os.path.join(RAIZ, "modelo_dron", "dron_real.json"), os.path.join(RAIZ, "v16", "simulacion", "recursos", "dron_real.json"),
          os.path.join(RAIZ, "estacion", "dron_real.json")]


class TestModeloDron(unittest.TestCase):
    def test_las_copias_del_json_son_iguales_al_modelo(self):
        esperado = json.loads(json.dumps({"piezas": dron_real.piezas(), "colores": dron_real.COLORES}))
        for ruta in COPIAS:
            with open(ruta, encoding="utf-8") as f:
                d = json.load(f)
            self.assertEqual(d["piezas"], esperado["piezas"], ruta + " está desactualizado: correr modelo_dron/dron_real.py")

    def test_cada_pieza_es_valida(self):
        nombres = set()
        for p in dron_real.piezas():
            self.assertIn(p["forma"], ("caja", "cilindro"))
            self.assertIn(p["color"], dron_real.COLORES)
            self.assertEqual(len(p["centro"]), 3)
            self.assertEqual(len(p["tam"]), 3 if p["forma"] == "caja" else 2)
            self.assertTrue(all(v > 0 for v in p["tam"]), p["nombre"])
            nombres.add(p["nombre"])
        for esperado in ("tf03", "camara_usb_lente", "jetson", "caja_acrilico", "bateria", "gps", "gimbal_motor_pitch",
                         *[f"motor{k}" for k in range(4)], *[f"helice{k}" for k in range(4)], *[f"cono{k}" for k in range(4)]):
            self.assertIn(esperado, nombres)

    def test_tamano_cercano_al_real(self):
        x0, x1, y0, y1, z0, z1 = dron_real.tamano_total()
        self.assertTrue(0.5 < x1 - x0 < 0.7 and 0.5 < y1 - y0 < 0.7, "de punta a punta de las hélices, ~0.6 m")
        self.assertTrue(0.3 < z1 - z0 < 0.5, "alto del apoyo a la antena, ~0.4 m")

    def test_el_gimbal_cuelga_de_la_nariz_y_la_bateria_bajo_el_chasis(self):
        P = {p["nombre"]: p for p in dron_real.piezas()}
        self.assertGreater(P["tf03"]["centro"][0], 0.1)
        self.assertLess(P["tf03"]["centro"][2], P["bateria"]["centro"][2])
        self.assertLess(P["bateria"]["centro"][2], 0)


if __name__ == "__main__":
    unittest.main()
