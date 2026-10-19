# -*- coding: utf-8 -*-
r"""Pruebas de la ruta de búsqueda de Brahian dibujada en la estación y en Unreal (entorno/ruta_busqueda.py)."""
import glob
import math
import os
import sys
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "entorno"))
import ruta_busqueda as R  # noqa: E402

# las dos V de la cancha de la V17: vértice compartido, alas de 1.5 m a 90° entre sí (boca de 2.12 m), 10 m entre vértices
PANELES = [[0.0, -5.0, -1.06, -6.06, 2.25], [0.0, -5.0, 1.06, -6.06, 2.25], [0.0, 5.0, 1.06, 6.06, 2.25], [0.0, 5.0, -1.06, 6.06, 2.25]]


class TestRuta(unittest.TestCase):
    def setUp(self):
        self.r = R.ruta(PANELES, (-2.0, -12.0, 1.85))

    def test_encuentra_las_dos_v_con_su_boca(self):
        self.assertEqual(len(self.r["v"]), 2)
        abren = sorted(round(v["eje"][1]) for v in self.r["v"])
        self.assertEqual(abren, [-1, 1])                                # una abre al sur y la otra al norte

    def test_detras_a_4_5_m_del_centro_y_mirando_a_la_v(self):
        for v in self.r["v"]:
            m = v["puntos"][-1]
            self.assertAlmostEqual(math.hypot(m[0] - v["centro"][0], m[1] - v["centro"][1]), R.D_DETRAS, places=2)
            a = math.atan2(v["centro"][1] - m[1], v["centro"][0] - m[0])
            self.assertAlmostEqual((math.radians(m[3]) - a + math.pi) % (2 * math.pi) - math.pi, 0.0, places=2)

    def test_cuadrado_de_la_boca_mas_el_margen(self):
        for v in self.r["v"]:
            c = v["cuadrado"]
            lado = math.hypot(c[1][0] - c[0][0], c[1][1] - c[0][1])
            self.assertAlmostEqual(lado, R.BOCA + 2 * R.MARGEN, places=2)
            self.assertAlmostEqual(c[0][0], c[4][0], places=6)           # se cierra

    def test_altura_fija_3_30_y_dentro_de_la_zona_de_30_m(self):
        for p in self.r["polilinea"][1:]:
            self.assertAlmostEqual(p[2], 3.30, places=2)
            self.assertLessEqual(abs(p[0]), 15.0)
            self.assertLessEqual(abs(p[1]), 15.0)

    def test_empieza_por_la_v_mas_cercana(self):
        self.assertLess(self.r["v"][0]["centro"][1], 0.0)

    def test_con_una_repeticion_real(self):
        import json
        for ruta in sorted(glob.glob(os.path.join(AQUI, "..", "..", "03_SIMULACION_RL", "salida_v17_*", "replay_v17.json")))[:1]:
            with open(ruta, encoding="utf-8") as f:
                d = json.load(f)
            r = R.ruta(d["paneles"], d["cuadros"][0]["d"][:3])
            self.assertEqual(len(r["v"]), 2)


if __name__ == "__main__":
    unittest.main()
