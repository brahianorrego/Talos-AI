# -*- coding: utf-8 -*-
"""Lógica de las posturas de los maniquíes en vivo (unreal/vivo_unreal.py) sin abrir Unreal: se le da la repetición de la galería de posturas y se mira
en qué tramo de la animación pone a la persona en cada instante (agacharse, agachado caminando, recostarse, gateo, salto)."""
import json
import os
import sys
import types
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
UE = os.path.normpath(os.path.join(AQUI, "..", "unreal"))
GAL = os.path.join(UE, "_cache", "galeria", "replay_v17.json")


@unittest.skipUnless(os.path.exists(GAL), "falta la repetición de la galería (unreal/galeria_posturas.py)")
class TestPosturasVivo(unittest.TestCase):
    def test_tramos(self):
        falsos = [n for n in ("unreal", "dronia_ue", "maniquies_unreal") if n not in sys.modules]
        for nombre in falsos:                                                          # el editor no está: un módulo vacío basta para importar la lógica
            sys.modules[nombre] = types.ModuleType(nombre)
        sys.path.insert(0, UE)
        self.addCleanup(lambda: [sys.modules.pop(n, None) for n in falsos + ["vivo_unreal"]])
        self.addCleanup(lambda: sys.path.remove(UE))
        import importlib
        V = importlib.import_module("vivo_unreal")
        d = json.load(open(GAL, encoding="utf-8"))
        marcas = []

        def scrub(p, t):
            p["anim"] = "gal"
            marcas.append(t)
        V.scrub = scrub
        p = {"anim": None}
        vistos = {}
        dt = 1.0 / 60.0
        for k, c in enumerate(d["cuadros"]):
            q0 = c["pers"][0]
            q = {"pos": q0.get("pos", 0), "v": q0["v"], "sz": (c.get("salto") or {}).get("h", 0.0)}
            for _ in range(6):                                                         # 10 Hz de la simulación = 6 cuadros de dibujo a 60 fps
                marcas.clear()
                especial = V.postura(p, q, dt)
                vistos[round(k * 0.1, 1)] = (especial, marcas[-1] if marcas else None)
        en = lambda t: vistos[round(t, 1)]
        self.assertFalse(en(5.0)[0], "trotando debe usar las animaciones normales")
        esp, t = en(11.5)
        self.assertTrue(esp and 10.2 <= t <= 13.2, "agachado caminando fuera de su tramo: %s" % t)
        esp, t = en(16.0)
        self.assertTrue(esp and 14.4 <= t <= 16.9, "recostado fuera de su tramo: %s" % t)
        esp, t = en(21.0)
        self.assertTrue(esp and 19.6 <= t <= 23.1, "gateando fuera de su tramo: %s" % t)
        esp, t = en(25.2)
        self.assertTrue(esp and 24.85 <= t <= 26.05, "salto fuera de su tramo: %s" % t)
        self.assertFalse(en(27.5)[0], "después del salto debe volver a las animaciones normales")


if __name__ == "__main__":
    unittest.main()
