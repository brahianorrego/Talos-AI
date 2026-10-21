# -*- coding: utf-8 -*-
"""El servidor de la estación entrega las imágenes de las cámaras del dron que guarda Unreal (unreal/_cache/cam/cam0.jpg, cam1.jpg) con su edad en X-Edad."""
import os
import subprocess
import sys
import time
import unittest
import urllib.error
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
CAM = os.path.join(AQUI, "..", "unreal", "_cache", "cam")
PUERTO = 8794
JPG = bytes.fromhex("ffd8ffe000104a46494600010100000100010000ffdb004300080606070605080707070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c2837292c30313434341f27393d38323c2e333432ffc0000b080001000101011100ffc4001f0000010501010101010100000000000000000102030405060708090a0bffc400b5100002010303020403050504040000017d01020300041105122131410613516107227114328191a1082342b1c11552d1f02433627282090a161718191a25262728292a3435363738393a434445464748494a535455565758595a636465666768696a737475767778797a838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9faffda0008010100003f00fbfcffd9")


class TestCamaraUnreal(unittest.TestCase):
    def test_sirve_la_imagen_con_su_edad(self):
        os.makedirs(CAM, exist_ok=True)
        ruta = os.path.join(CAM, "cam0.jpg")
        existia = os.path.exists(ruta)
        if not existia:
            open(ruta, "wb").write(JPG)
        p = subprocess.Popen([sys.executable, os.path.join(AQUI, "..", "estacion", "servidor.py"), "--puerto", str(PUERTO)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(40):
                try:
                    r = urllib.request.urlopen("http://127.0.0.1:%d/unreal_cam/cam0.jpg" % PUERTO, timeout=3)
                    break
                except (urllib.error.URLError, ConnectionError):
                    time.sleep(0.25)
            self.assertEqual(r.headers["Content-Type"], "image/jpeg")
            self.assertGreaterEqual(float(r.headers["X-Edad"]), 0.0)
            self.assertTrue(r.read().startswith(b"\xff\xd8"))
            with self.assertRaises(urllib.error.HTTPError):                     # solo cam0.jpg y cam1.jpg: nada más sale de esa carpeta
                urllib.request.urlopen("http://127.0.0.1:%d/unreal_cam/../servidor.py" % PUERTO, timeout=3)
        finally:
            p.kill()
            if not existia:
                os.remove(ruta)


if __name__ == "__main__":
    unittest.main()
