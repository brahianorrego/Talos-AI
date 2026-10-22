# -*- coding: utf-8 -*-
# Uso (en el PC):  python medir_video.py [host=talos-jetson.local] [segundos=15]    (variable PUERTO=8080 por defecto)
# Mide el video del panel desde el PC: FPS recibidos, Mbps y atraso (hora de captura en la Jetson vs llegada), con el reloj corregido por /datos.
import os
PUERTO = int(os.environ.get("PUERTO", 8080))
import socket, time, json, re, sys, urllib.request
H = sys.argv[1] if len(sys.argv) > 1 else "talos-jetson.local"; DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 15
def offset():
    mejores = []
    for _ in range(8):
        t0 = time.time(); d = json.load(urllib.request.urlopen("http://%s:%d/datos" % (H, PUERTO), timeout=5)); t1 = time.time()
        mejores.append((t1 - t0, d["t"] - (t0 + t1) / 2))
    rtt, off = min(mejores); return rtt, off   # off = reloj Jetson - reloj PC
rtt, off = offset(); print("RTT mínimo %.0f ms | reloj Jetson - PC = %.3f s" % (rtt * 1000, off))
s = socket.create_connection((H, PUERTO), 8); s.sendall(b"GET /video HTTP/1.0\r\n\r\n")
buf = b""; n = 0; bytes_ = 0; lags = []; t_ini = time.time(); sizes = []
while time.time() - t_ini < DUR:
    d = s.recv(65536)
    if not d: break
    buf += d; bytes_ += len(d)
    while True:
        m = re.search(rb"--frame\r\nContent-Type: image/jpeg\r\n(?:X-T: ([0-9.]+)\r\n)?Content-Length: (\d+)\r\n\r\n", buf)
        if not m: break
        L = int(m.group(2)); fin = m.end() + L
        if len(buf) < fin: break
        if m.group(1): lags.append((time.time() + off) - float(m.group(1)))
        sizes.append(L); buf = buf[fin:]; n += 1
dt = time.time() - t_ini
print("cuadros/s=%.1f  Mbps=%.1f  tamaño medio=%.0f KB" % (n / dt, bytes_ * 8 / dt / 1e6, sum(sizes) / max(1, len(sizes)) / 1024))
if lags:
    lags.sort(); print("atraso (s): mediana=%.2f  p90=%.2f  máx=%.2f  | primero=%.2f último=%.2f" % (lags[len(lags)//2], lags[int(len(lags)*0.9)], lags[-1], lags[0], lags[-1] if False else 0))
