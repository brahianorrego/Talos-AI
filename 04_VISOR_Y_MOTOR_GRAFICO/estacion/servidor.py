# -*- coding: utf-8 -*-
"""
Servidor de la estación de tierra (D-065), http://127.0.0.1:8768/

Entrega los archivos de esta carpeta (index.html, ventanas.js, lib/) y, si un archivo no está aquí, lo busca en
03_SIMULACION_RL (salida/, minimo_tesis/replay/, ...): así la estación lee las repeticiones y el entrenamiento sin copiar
ni tocar nada de la simulación. Solo lectura y solo en este computador (127.0.0.1).

Uso:  03_SIMULACION_RL\\.venv\\Scripts\\python.exe 04_VISOR_Y_MOTOR_GRAFICO\\estacion\\servidor.py [--puerto 8768]
"""
import argparse
import http.server
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.normpath(os.path.join(AQUI, "..", "..", "03_SIMULACION_RL"))
TIPOS = {".js": "text/javascript", ".json": "application/json", ".css": "text/css", ".html": "text/html; charset=utf-8"}


class Manejador(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        propio = super().translate_path(path)                  # dentro de esta carpeta (el servidor corre en AQUI)
        if os.path.exists(propio):
            return propio
        rel = os.path.relpath(propio, AQUI)
        otro = os.path.normpath(os.path.join(SIM, rel))
        return otro if otro.startswith(SIM) else propio        # nunca fuera de 03_SIMULACION_RL

    def guess_type(self, path):
        return TIPOS.get(os.path.splitext(path)[1].lower()) or super().guess_type(path)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--puerto", type=int, default=8768)
    a = ap.parse_args()
    os.chdir(AQUI)
    print("Estación de tierra en http://127.0.0.1:%d/  (Ctrl+C para cerrar)" % a.puerto, flush=True)
    http.server.ThreadingHTTPServer(("127.0.0.1", a.puerto), Manejador).serve_forever()
