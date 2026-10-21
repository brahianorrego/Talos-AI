# -*- coding: utf-8 -*-
"""Modo enseñar de en_vivo.py de punta a punta: clic (POST /waypoint) -> el dron va, gira y apunta el pan-tilt -> se graba la demostración."""
import glob
import json
import math
import os
import subprocess
import sys
import time
import unittest
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, "..", ".."))
PY = os.path.join(RAIZ, "03_SIMULACION_RL", ".venv", "Scripts", "python.exe")
PUERTO = 8791


def post(ruta, d):
    r = urllib.request.Request("http://127.0.0.1:%d%s" % (PUERTO, ruta), json.dumps(d).encode(), {"Content-Type": "application/json"})
    urllib.request.urlopen(r, timeout=5).read()


def cuadro_nuevo(s, hasta=0):
    """Lee cuadros del flujo en vivo hasta cumplir hasta(c) o pasar 40 s."""
    t0 = time.time()
    for linea in s:
        if time.time() - t0 > 40:
            break
        if linea.startswith(b"data: "):
            m = json.loads(linea[6:])
            if m.get("tipo") == "cuadro" and hasta(m["c"]):
                return m["c"]
    return None


@unittest.skipUnless(os.path.exists(PY), "sin el .venv de la simulación")
class TestEnsenar(unittest.TestCase):
    def test_punta_a_punta(self):
        antes = set(glob.glob(os.path.join(RAIZ, "03_SIMULACION_RL", "demos_brahian", "demo_*.json")))
        p = subprocess.Popen([PY, os.path.join(AQUI, "..", "en_vivo.py"), "--puerto", str(PUERTO), "--velocidad", "6"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(60):
                try:
                    s = urllib.request.urlopen("http://127.0.0.1:%d/vivo" % PUERTO, timeout=20)
                    break
                except OSError:
                    time.sleep(1)
            c0 = cuadro_nuevo(s, lambda c: True)
            x0, y0 = c0["d"][0] + 2.0, c0["d"][1] + 1.0          # un punto cercano y libre: un vuelo largo puede chocar con un panel y terminar la partida
            post("/modo", {"modo": "ensenar", "sub": "mapa"})
            post("/grabar", {"on": True})
            post("/waypoint", {"x": x0, "y": y0, "yaw": 90.0, "pan": 40.0, "tilt": -20.0})
            post("/waypoint", {"x": -3.0, "y": 6.0, "yaw": 0.0, "pan": 0.0, "tilt": -5.0})
            post("/waypoint", {"borrar": "ultimo"})
            post("/waypoint", {"ir": True})
            c = cuadro_nuevo(s, lambda c: "ens" in c and c["ens"]["ir"] is False and c["ens"]["i"] == 1)
            self.assertIsNotNone(c, "no llegó al punto")
            self.assertLess(math.hypot(c["d"][0] - x0, c["d"][1] - y0), 0.6)
            self.assertAlmostEqual(math.degrees(c["d"][3]), 90.0, delta=4.0)
            self.assertAlmostEqual(c["pan"], 40.0, delta=3.0)
            self.assertTrue(-45.0 <= c["gmb"] <= 15.0)
            post("/grabar", {"on": False})
            time.sleep(2)
            nuevos = set(glob.glob(os.path.join(RAIZ, "03_SIMULACION_RL", "demos_brahian", "demo_*.json"))) - antes
            self.assertTrue(nuevos, "no se guardó la demostración")
            d = json.load(open(sorted(nuevos)[0], encoding="utf-8"))
            for f in nuevos:
                os.remove(f)
            self.assertGreater(len(d["cuadros"]), 10)
        finally:
            p.kill()

    def test_teclado_y_mouse(self):
        """§G.1: mouse = pan/tilt absolutos, Espacio/C = altura (vz), F mantenida = giro 360°, clic = fijar sospechoso."""
        p = subprocess.Popen([PY, os.path.join(AQUI, "..", "en_vivo.py"), "--puerto", str(PUERTO), "--velocidad", "6"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(60):
                try:
                    s = urllib.request.urlopen("http://127.0.0.1:%d/vivo" % PUERTO, timeout=20)
                    break
                except OSError:
                    time.sleep(1)
            c0 = cuadro_nuevo(s, lambda c: True)
            z0, psi0 = c0["d"][2], c0["d"][3]
            post("/modo", {"modo": "ensenar", "sub": "manual"})
            post("/camara", {"modo": "manual", "pan": 35.0, "tilt": -20.0})
            t0 = time.time()
            c = None
            while time.time() - t0 < 30:
                post("/manual", {"vz": 1.0, "f360": 1.0})        # se repite cada 0.1 s como la estación (el mando vence a los 0.4 s)
                c = cuadro_nuevo(s, lambda c: "ens" in c)
                if c and c["ens"]["f360"] and abs(math.degrees(c["d"][3] - psi0)) > 25 and c["d"][2] > z0 + 0.3:
                    break
            self.assertTrue(c["ens"]["f360"], "F mantenida no activó el 360")
            self.assertGreater(c["d"][2], z0 + 0.3, "no subió con vz")
            self.assertAlmostEqual(c["pan"], 35.0, delta=4.0)
            self.assertTrue(-45.0 <= c["gmb"] <= 15.0)
            post("/fijar", {"j": 0})                           # no debe romper aunque no esté a la vista (el clic se pierde)
            self.assertIsNotNone(cuadro_nuevo(s, lambda c: "ens" in c))
        finally:
            p.kill()


if __name__ == "__main__":
    unittest.main()
