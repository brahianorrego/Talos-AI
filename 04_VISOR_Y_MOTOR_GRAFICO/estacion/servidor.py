# -*- coding: utf-8 -*-
"""
Servidor de la estación de tierra (D-065), http://127.0.0.1:8768/

Entrega los archivos de esta carpeta (index.html, ventanas.js, lib/) y, si un archivo no está aquí, lo busca en
03_SIMULACION_RL (salida/, minimo_tesis/replay/, ...): así la estación lee las repeticiones y el entrenamiento sin copiar
ni tocar nada de la simulación. Solo lectura y solo en este computador (127.0.0.1).

Uso:  03_SIMULACION_RL\\.venv\\Scripts\\python.exe 04_VISOR_Y_MOTOR_GRAFICO\\estacion\\servidor.py [--puerto 8768]
"""
import argparse
import json
import http.server
import os
import sys
import time
import urllib.parse
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.normpath(os.path.join(AQUI, "..", "..", "03_SIMULACION_RL"))
TIPOS = {".js": "text/javascript", ".json": "application/json", ".css": "text/css", ".html": "text/html; charset=utf-8"}


def corridas_v17():
    """Las carpetas salida_v17_* de la simulación, la más reciente primero (la estación solo muestra la V17)."""
    lista = []
    for nombre in os.listdir(SIM):
        ruta = os.path.join(SIM, nombre, "estado.json")
        if nombre.startswith("salida_v17") and os.path.isfile(ruta):
            try:
                e = json.load(open(ruta, encoding="utf-8"))
            except (OSError, ValueError):
                continue
            lista.append({"carpeta": nombre, "it": e.get("it"), "pasos": e.get("pasos", 0), "t": e.get("t", 0),
                          "vivo": time.time() - e.get("t", 0) < 120})
    return sorted(lista, key=lambda c: -c["t"])


sys.path.insert(0, os.path.join(AQUI, "..", "entorno"))
import ruta_busqueda  # noqa: E402


class Manejador(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        """/captura/<nombre>.png: guarda en mediciones/capturas la imagen (dataURL) que manda la página; solo ahí y solo .png."""
        nombre = os.path.basename(self.path.split("?")[0])
        if self.path.startswith("/mundo/"):                       # /mundo/<seguir|cenital|campus|off>: enciende o apaga la cámara de la vista "Mundo 3D" de Unreal
            modo = nombre
            archivo = os.path.join(AQUI, "..", "unreal", "_cache", "mundo.txt")
            if modo in ("seguir", "cenital", "campus"):
                open(archivo, "w", encoding="utf-8").write(modo)
            elif modo == "off" and os.path.exists(archivo):
                os.remove(archivo)
            elif modo != "off":
                self.send_error(404)
                return
            self.send_response(200)
            self.end_headers()
            return
        if not (self.path.startswith("/captura/") and nombre.endswith(".png") and nombre.replace("_", "").replace(".png", "").isalnum()):
            self.send_error(404)
            return
        import base64
        cuerpo = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode("ascii", "ignore")
        carpeta = os.path.normpath(os.path.join(AQUI, "..", "mediciones", "capturas"))
        os.makedirs(carpeta, exist_ok=True)
        with open(os.path.join(carpeta, nombre), "wb") as f:
            f.write(base64.b64decode(cuerpo.split(",", 1)[-1]))
        self.send_response(200)
        self.end_headers()

    def tesela(self):
        """/tiles/<z>/<x>/<y>.jpg: teselas satelitales de Esri World Imagery con caché en disco (mapa/teselas/). Sin internet entrega las ya guardadas
        (mapa/precargar_teselas.py baja el campus antes de salir); si falta una, 404 y el mapa deja ese cuadro vacío."""
        try:
            z, x, y = (int(v) for v in os.path.splitext(self.path.split("?")[0])[0].split("/")[2:5])
            if not (10 <= z <= 20 and 0 <= x < 2 ** z and 0 <= y < 2 ** z):
                raise ValueError
        except ValueError:
            self.send_error(404)
            return
        ruta = os.path.join(AQUI, "mapa", "teselas", str(z), str(x), f"{y}.jpg")
        datos = None
        if os.path.isfile(ruta):
            datos = open(ruta, "rb").read()
        else:
            try:
                req = urllib.request.Request(f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                                             headers={"User-Agent": "TALOS-AI-estacion/1.0 (proyecto de grado, uso academico)"})
                datos = urllib.request.urlopen(req, timeout=6).read()
                os.makedirs(os.path.dirname(ruta), exist_ok=True)
                with open(ruta, "wb") as f:
                    f.write(datos)
            except OSError:
                datos = None
        if not datos:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Cache-Control", "max-age=86400")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def do_GET(self):
        if self.path.startswith("/tiles/"):
            return self.tesela()
        if self.path.startswith("/unreal_cam/"):                  # lo que ven las cámaras del dron en Unreal (unreal/vivo_unreal.py las guarda como JPG ~10 Hz)
            nombre = os.path.basename(self.path.split("?")[0])
            ruta = os.path.join(AQUI, "..", "unreal", "_cache", "cam", nombre)
            try:
                if not (nombre in ("cam0.jpg", "cam1.jpg", "cam2.jpg") and os.path.isfile(ruta)):
                    raise OSError
                if time.time() - os.path.getmtime(ruta) < 0.06:   # recién escrita: se espera un instante para no mandar un JPG a medias
                    time.sleep(0.08)
                datos = open(ruta, "rb").read()
                edad = time.time() - os.path.getmtime(ruta)
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("X-Edad", "%.2f" % edad)
                self.send_header("Content-Length", str(len(datos)))
                self.end_headers()
                self.wfile.write(datos)
            except OSError:
                self.send_error(404)
            return
        if self.path.split("?")[0] == "/ruta.json":              # ruta de búsqueda de Brahian sobre los paneles y la posición inicial que manda la página
            try:
                q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                paneles = [[float(v) for v in p[:5]] for p in json.loads(q["paneles"][0])][:16]
                inicio = [float(v) for v in json.loads(q["inicio"][0])][:3]
                datos = json.dumps(ruta_busqueda.ruta(paneles, inicio)).encode("utf-8")
                self.send_response(200)
            except (KeyError, ValueError, TypeError, IndexError):
                datos = b"{}"
                self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(datos)))
            self.end_headers()
            self.wfile.write(datos)
            return
        if self.path.split("?")[0] == "/corridas.json":
            datos = json.dumps(corridas_v17()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(datos)))
            self.end_headers()
            self.wfile.write(datos)
            return
        super().do_GET()

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
