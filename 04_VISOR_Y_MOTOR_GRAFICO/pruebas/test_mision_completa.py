# -*- coding: utf-8 -*-
r"""Pruebas de la misión completa (entorno/mision_completa.py): el tránsito sigue las reglas del mínimo, no choca con nada, y empalma
con la partida V17. Desde la raíz del proyecto:
   03_SIMULACION_RL\.venv\Scripts\python.exe -m unittest discover -s 04_VISOR_Y_MOTOR_GRAFICO/pruebas"""
import glob
import math
import os
import sys
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, ".."))
sys.path.insert(0, os.path.join(RAIZ, "entorno"))
import mision_completa as M  # noqa: E402

REPLAYS = sorted(glob.glob(os.path.join(M.SIM, "salida_v17_*", "replay_v17.json")))


@unittest.skipUnless(REPLAYS and os.path.exists(M.MINIMO), "faltan una repetición V17 y la del mínimo")
class TestMisionCompleta(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.D = M.generar(REPLAYS[0], 20.0)
        cls.C = cls.D["cuadros"]
        cls.kz = cls.D["k_zona"]

    def test_tres_intervenciones_del_minimo_cada_una_con_su_reanudar(self):
        ev = self.D["eventos_extra"]
        riesgos = [e for e in ev if e["txt"].startswith("MÍNIMO · RIESGO")]
        self.assertEqual([("obstáculo" in e["txt"]) for e in riesgos], [True, True, False])          # panel, árbol, persona
        self.assertEqual(len([e for e in ev if "REANUDAR" in e["txt"]]), 3)

    def test_al_intervenir_frena_y_sube_a_3_30_antes_de_tocar_nada(self):
        tr = self.C[: self.kz]
        retenidos = [c for c in tr if c["min"] == "RETENIDO"]
        self.assertTrue(retenidos)
        for c in retenidos:
            self.assertGreaterEqual(c["d"][2], M.Z_SEGURA - 0.03)
            self.assertLess(math.hypot(*c["dv"]), 0.05)
        for c in tr:                                                                # nunca más cerca de 1.5 m de un obstáculo o persona
            x, y = c["d"][0], c["d"][1]
            if abs(x - M.OBSTACULOS["arbol"]["p"][0]) < 1.0:                       # por su carril, nunca a menos de 3 m del árbol
                self.assertGreater(M.OBSTACULOS["arbol"]["p"][1] - y, 3.0)
            for p in c["pers"]:
                if p["id"] == 90:
                    self.assertGreater(math.hypot(x - p["p"][0], y - p["p"][1]), 2.0)

    def test_el_panel_se_pasa_por_arriba_a_la_altura_segura(self):
        py = M.OBSTACULOS["panel"][1]
        sobre = [c for c in self.C[: self.kz] if abs(c["d"][1] - py) < 0.5]
        self.assertTrue(sobre)
        self.assertTrue(all(c["d"][2] > M.OBSTACULOS["panel"][4] + 0.8 for c in sobre))

    def test_empalma_con_la_partida_v17_y_activa_ch7_antes_de_que_mande_la_ia(self):
        zona = self.C[self.kz]
        self.assertEqual(zona["fase"], 2)
        antes = self.C[self.kz - 1]
        self.assertLess(math.hypot(zona["d"][0] - antes["d"][0], zona["d"][1] - antes["d"][1]), 0.3)     # sin salto de posición
        self.assertAlmostEqual(zona["d"][2], antes["d"][2], delta=0.15)
        self.assertTrue(any(c["ch7"] == 1 and c["fase"] == 1 for c in self.C[: self.kz]))
        self.assertTrue(all(c["fase"] == 1 for c in self.C[: self.kz]))

    def test_todo_dentro_de_la_cancha_de_futbol(self):
        for c in self.C:
            self.assertLess(abs(c["d"][0]), 33.5)
            self.assertGreater(c["d"][1], -76.5)
            self.assertLess(c["d"][1], 25.5)


if __name__ == "__main__":
    unittest.main()
