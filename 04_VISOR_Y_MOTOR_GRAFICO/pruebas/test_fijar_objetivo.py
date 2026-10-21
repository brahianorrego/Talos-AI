# -*- coding: utf-8 -*-
"""Clic sobre una persona real a la vista (regla dura 4: lo hace el humano): se fija; clic derecho: se suelta. Usa el entorno de 03_SIMULACION_RL."""
import os
import sys
import unittest

import numpy as np

SIM = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "03_SIMULACION_RL"))
sys.path.insert(0, SIM)
try:
    import entorno as E
except Exception:                                              # noqa: BLE001
    E = None


@unittest.skipUnless(E is not None and hasattr(E, "EntornoDronPersona"), "sin el entorno de la simulación")
class TestFijarObjetivo(unittest.TestCase):
    def paso(self, env):
        return env.step(np.zeros(1, int), np.full(1, E.N_ACC_PERSONA - 1), auto_reset=False)

    def test_fijar_y_soltar(self):
        E.aplicar_hw("H")
        env = E.EntornoDronPersona(1, semilla=3, nivel=getattr(E, "NIVEL_V17", E.NIVEL_V16))
        env.set_manual(0)
        for _ in range(5):
            self.paso(env)
        x, y, psi = float(env.dx[0]), float(env.dy[0]), float(env.psi[0])
        ahi = lambda: (x + 6 * np.cos(psi), y + 6 * np.sin(psi))                       # el ladrón, quieto, 6 m delante del dron
        visto = False
        for _ in range(60):
            env.px[0, 0], env.py[0, 0] = ahi()
            env.pvx[0, 0] = env.pvy[0, 0] = 0.0
            env.set_manual(0)
            self.paso(env)
            if env.foto(0)["pers"][0]["vis"]:
                visto = True
                break
        self.assertTrue(visto, "el ladrón puesto delante no quedó a la vista")
        env.fijar_sospechoso(0, 0)
        for _ in range(5):
            env.px[0, 0], env.py[0, 0] = ahi()
            self.paso(env)
        self.assertEqual(env.foto(0)["eb"], "PERSECUCION", "no quedó fijado")
        env.soltar_sospechoso(0)
        for _ in range(3):
            self.paso(env)
        self.assertNotEqual(env.foto(0)["eb"], "PERSECUCION", "no se soltó")


if __name__ == "__main__":
    unittest.main()
