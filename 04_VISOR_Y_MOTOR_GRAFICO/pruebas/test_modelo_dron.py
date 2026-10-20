# -*- coding: utf-8 -*-
r"""Pruebas del modelo 3D del dron (04_VISOR_Y_MOTOR_GRAFICO/modelo_dron). Correr desde la raíz del proyecto:
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
        esperado = json.loads(json.dumps({"piezas": dron_real.piezas(), "piezas_gimbal": dron_real.piezas("gimbal"), "colores": dron_real.COLORES}))
        for ruta in COPIAS:
            with open(ruta, encoding="utf-8") as f:
                d = json.load(f)
            for k in ("piezas", "piezas_gimbal"):
                self.assertEqual(d[k], esperado[k], ruta + " está desactualizado: correr modelo_dron/dron_real.py")
            self.assertEqual(d["variante"], "sin_gimbal")

    def test_cada_pieza_es_valida(self):
        for variante in ("sin_gimbal", "gimbal"):
            for p in dron_real.piezas(variante):
                self.assertIn(p["forma"], ("caja", "cilindro"))
                self.assertIn(p["color"], dron_real.COLORES)
                self.assertEqual(len(p["centro"]), 3)
                self.assertEqual(len(p["tam"]), 3 if p["forma"] == "caja" else 2)
                self.assertTrue(all(v > 0 for v in p["tam"]), p["nombre"])

    def nombres(self, variante):
        return {p["nombre"] for p in dron_real.piezas(variante)}

    def test_el_dron_de_hoy_no_tiene_gimbal_ni_camara_usb(self):
        n = self.nombres("sin_gimbal")
        self.assertFalse([x for x in n if x.startswith("gimbal") or "usb" in x])
        for esperado in ("tf03", "csi_placa", "csi_lente", "csi_flex_lazo", "base_impresa", "estructura_volteada", "jetson", "caja_acrilico", "bateria",
                         "gps", *[f"motor{k}" for k in range(4)], *[f"helice{k}" for k in range(4)], *[f"cono{k}" for k in range(4)]):
            self.assertIn(esperado, n)

    def test_el_interruptor_conserva_el_dron_de_antes(self):
        n = self.nombres("gimbal")
        for esperado in ("tf03", "camara_usb_lente", "gimbal_motor_pitch", "gimbal_placa"):
            self.assertIn(esperado, n)
        self.assertFalse([x for x in n if x.startswith("csi") or x == "base_impresa"])

    def test_tamano_cercano_al_real(self):
        x0, x1, y0, y1, z0, z1 = dron_real.tamano_total()
        self.assertTrue(0.5 < x1 - x0 < 0.7 and 0.5 < y1 - y0 < 0.7, "de punta a punta de las hélices, ~0.6 m")
        self.assertTrue(0.3 < z1 - z0 < 0.5, "alto del apoyo a la antena, ~0.4 m")

    def test_tf03_fijo_adelante_a_la_altura_del_chasis_y_csi_arriba(self):
        P = {p["nombre"]: p for p in dron_real.piezas()}
        self.assertGreater(P["tf03"]["centro"][0], 0.1)
        self.assertTrue(-0.04 < P["tf03"]["centro"][2] < 0.03, "a la altura de las placas, no colgando de un gimbal")
        self.assertGreater(P["csi_placa"]["centro"][2], P["caja_acrilico"]["centro"][2])
        self.assertLess(P["bateria"]["centro"][2], 0)
        self.assertLess(P["estructura_volteada"]["centro"][2], P["placa_inferior"]["centro"][2])

    def test_con_gimbal_el_tf03_cuelga_de_la_nariz(self):
        P = {p["nombre"]: p for p in dron_real.piezas("gimbal")}
        self.assertGreater(P["tf03"]["centro"][0], 0.1)
        self.assertLess(P["tf03"]["centro"][2], P["bateria"]["centro"][2])


if __name__ == "__main__":
    unittest.main()
