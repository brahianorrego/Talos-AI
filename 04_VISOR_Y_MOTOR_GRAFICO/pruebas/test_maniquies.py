# -*- coding: utf-8 -*-
r"""Pruebas de los maniquíes de Unreal (unreal/maniquies_*.py): alturas por postura, pies en el suelo y rumbo hacia donde camina.
Necesitan unreal/_cache/maniquies.json (lo vuelca maniquies_volcar.py desde el editor); sin él se saltan. Desde la raíz del proyecto:
   03_SIMULACION_RL\.venv\Scripts\python.exe -m unittest discover -s 04_VISOR_Y_MOTOR_GRAFICO/pruebas"""
import math
import os
import sys
import unittest

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
UE = os.path.normpath(os.path.join(AQUI, "..", "unreal"))
sys.path.insert(0, UE)
HAY_DATOS = os.path.exists(os.path.join(UE, "_cache", "maniquies.json"))
if HAY_DATOS:
    import maniquies_animar as MA  # noqa: E402
    import maniquies_replay as MR  # noqa: E402
    from maniquies_fk import Pose  # noqa: E402


@unittest.skipUnless(HAY_DATOS, "falta unreal/_cache/maniquies.json (maniquies_volcar.py)")
class TestManiquies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.A = MA.Animador()

    def anim(self, n, v, pos, pt=1.0):
        return self.A.animar([v] * n, [pos] * n, [pos] * n, [pt] * n, [False] * n)

    def pose(self, S, k):
        return Pose(self.A.E, S[k][:, :3], S[k][:, 3:])

    def test_altura_de_cada_postura_como_en_foto(self):
        """de pie 1.0, agachado 0.67, recostado 1.0 y gateando 0.35 de la estatura (F_ALTO_POSTURA de entorno.py)."""
        for pos, esperado, tol in ((0, 1.0, 0.03), (1, 0.67, 0.03), (2, 1.0, 0.04), (3, 0.35, 0.04)):
            S = self.anim(24, 0.0, pos)
            razon = self.pose(S, 12).alto() / self.A.alto_pie
            self.assertAlmostEqual(razon, esperado, delta=tol, msg=f"postura {pos}")

    def test_los_pies_no_se_hunden_ni_flotan(self):
        for pos, v in ((0, 1.2), (0, 3.5), (1, 0.8), (2, 0.0)):
            S = self.anim(48, v, pos)
            suelos = [self.pose(S, k).suelo() for k in range(0, 48, 4)]
            self.assertGreater(min(suelos), -8.0, f"pos {pos} v {v}")
            self.assertLess(min(suelos), 4.0, f"pos {pos} v {v}: ningún pie toca el suelo")

    def test_transicion_lineal_entre_posturas(self):
        S = self.A.animar([0.0] * 3, [0] * 3, [1] * 3, [0.0, 0.5, 1.0], [False] * 3)
        h = [self.pose(S, k).alto() / self.A.alto_pie for k in range(3)]
        self.assertAlmostEqual(h[0], 1.0, delta=0.03)
        self.assertAlmostEqual(h[1], 0.835, delta=0.04)
        self.assertAlmostEqual(h[2], 0.67, delta=0.03)

    def test_rumbo_hacia_donde_camina(self):
        """Hacia el este (+x de la simulación) la guiñada de Unreal es -90°; hacia el norte, 180° (el mundo de Unreal tiene y invertida)."""
        def cuadros(vx, vy):
            return [{"pers": [{"id": 1, "rol": "ladron", "p": [vx * 0.1 * k, vy * 0.1 * k], "v": [vx, vy], "pos0": 0, "pos": 0, "pt": 1.0}]}
                    for k in range(30)]
        este = MR.trayectoria(cuadros(1.2, 0.0), 0.1, 1, 60)
        norte = MR.trayectoria(cuadros(0.0, 1.2), 0.1, 1, 60)
        self.assertAlmostEqual(este["yaw"][-1] % 360, 270.0, delta=2)
        self.assertAlmostEqual(norte["yaw"][-1] % 360, 180.0, delta=2)

    def test_quieto_mira_hacia_donde_dice_mira(self):
        C = [{"pers": [{"id": 1, "rol": "peaton", "p": [0, 0], "v": [0, 0], "mira": math.pi / 2, "pos0": 0, "pos": 0, "pt": 1.0}]} for _ in range(30)]
        t = MR.trayectoria(C, 0.1, 1, 60)
        self.assertAlmostEqual(t["yaw"][-1] % 360, 180.0, delta=2)

    def test_la_velocidad_se_suaviza(self):
        """foto() alterna 1.2 y 1.5 m/s cada pocos cuadros: la animación no debe cambiar de ritmo a saltos."""
        C = [{"pers": [{"id": 1, "rol": "ladron", "p": [0, 0], "v": [1.5 if (k // 2) % 2 else 1.2, 0.0], "pos0": 0, "pos": 0, "pt": 1.0}]}
             for k in range(60)]
        v = MR.trayectoria(C, 0.1, 1, 140)["v"]
        self.assertLess(np.abs(np.diff(v[20:120])).max(), 0.05)


if __name__ == "__main__":
    unittest.main()
