# -*- coding: utf-8 -*-
"""Baja un mosaico satelital (Esri World Imagery) para MEDIR el campus en píxeles; la imagen no se guarda en el repositorio (licencia).
Uso: python mosaico_satelital.py LAT LON ZOOM N salida.png   (ej.: 4.75165 -74.02955 19 6 mosaico.png). Atribución obligatoria: Esri, Maxar, Earthstar Geographics."""
import math, urllib.request, io, sys
from PIL import Image
lat, lon, z, n = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
def tile(lat, lon, z):
    x = (lon + 180) / 360 * 2**z
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * 2**z
    return x, y
x0, y0 = tile(lat, lon, z); cx, cy = int(x0), int(y0)
im = Image.new('RGB', (256*n, 256*n))
for i in range(n):
    for j in range(n):
        tx, ty = cx - n//2 + i, cy - n//2 + j
        u = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{ty}/{tx}"
        d = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'DronIA-proyecto-de-grado/1.0'}), timeout=30).read()
        im.paste(Image.open(io.BytesIO(d)), (i*256, j*256))
im.save(sys.argv[5])
print('centro px', (x0-(cx-n//2))*256, (y0-(cy-n//2))*256, 'tile0', cx-n//2, cy-n//2)
