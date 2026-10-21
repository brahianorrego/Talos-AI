# -*- coding: utf-8 -*-
"""
Texturas de los suelos del campus (de las fotos nocturnas de la zona de vuelo, 20-oct): adoquín gris entrelazado, losas grandes de concreto con
pasto entre ellas y rejilla negra de canaleta. Sin ruido aleatorio no repetido: cada una se repite en mosaico sin costuras.
    03_SIMULACION_RL\\.venv\\Scripts\\python.exe 04_VISOR_Y_MOTOR_GRAFICO\\entorno\\suelos_tex.py
Escribe entorno/texturas/suelo_<nombre>.png (no van a Git).
"""
import os
import random

from PIL import Image, ImageDraw, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "texturas")
N = 512


def ruido(im, fuerza, semilla):
    r = random.Random(semilla)
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            d = r.randint(-fuerza, fuerza)
            c = px[x, y]
            px[x, y] = tuple(max(0, min(255, v + d)) for v in c[:3])
    return im


def adoquin():
    """Adoquín gris en forma de hueso/trébol, en filas desplazadas, con juntas oscuras."""
    im = Image.new("RGB", (N, N), (46, 47, 46))
    d = ImageDraw.Draw(im)
    r = random.Random(3)
    a = 64                                                        # lado de cada pieza (8 por lado)
    for j in range(N // a):
        for i in range(N // a):
            x0, y0 = i * a + (a // 2 if j % 2 else 0), j * a
            g = r.randint(98, 128)
            col = (g, g + 1, g - 2)
            for dx in (0, -N) if x0 + a > N else (0,):
                d.rounded_rectangle([x0 + dx + 3, y0 + 3, x0 + dx + a - 3, y0 + a - 3], radius=14, fill=col)
                d.ellipse([x0 + dx + a // 2 - 8, y0 + 1, x0 + dx + a // 2 + 8, y0 + 9], fill=(46, 47, 46))      # el entrante del trébol
                d.ellipse([x0 + dx + a // 2 - 8, y0 + a - 9, x0 + dx + a // 2 + 8, y0 + a - 1], fill=(46, 47, 46))
    im = ruido(im, 7, 5).filter(ImageFilter.GaussianBlur(0.8))
    return im


def losas():
    """Losas de concreto de ~1 x 0.55 m (la textura cubre 2 x 2 m) con pasto en las juntas."""
    pasto = (52, 92, 38)
    im = Image.new("RGB", (N, N), pasto)
    d = ImageDraw.Draw(im)
    r = random.Random(8)
    h = N // 4
    for j in range(4):
        w = N // 2
        off = (j % 2) * w // 3
        for i in range(-1, 3):
            x0 = i * w + off
            g = r.randint(98, 124)
            d.rectangle([x0 + 14, j * h + 12, x0 + w - 14, (j + 1) * h - 12], fill=(g, g, g - 3))
    im = ruido(im, 10, 9)
    for _ in range(900):                                         # hierba que invade el borde de las losas
        x, y = r.randrange(N), r.randrange(N)
        d.line([x, y, x + r.randint(-4, 4), y + r.randint(-6, 6)], fill=(58 + r.randint(0, 30), 100 + r.randint(0, 40), 40), width=1)
    return im.filter(ImageFilter.GaussianBlur(0.6))


def rejilla():
    """Rejilla negra de canaleta: barras finas y paralelas sobre fondo oscuro."""
    im = Image.new("RGB", (N, N), (12, 13, 14))
    d = ImageDraw.Draw(im)
    for k in range(0, N, 16):
        d.rectangle([k + 3, 0, k + 11, N], fill=(34, 36, 38))
    d.rectangle([0, 0, N, 10], fill=(48, 50, 52))
    d.rectangle([0, N - 10, N, N], fill=(48, 50, 52))
    return im


def pasto():
    """Césped de cerca (de noche bajo luminaria): verde con manchas más secas y hojas sueltas."""
    r = random.Random(11)
    im = Image.new("RGB", (N, N), (42, 84, 30))
    d = ImageDraw.Draw(im)
    for _ in range(26000):
        x, y = r.randrange(N), r.randrange(N)
        v = r.random()
        c = (46 + int(40 * v), 92 + int(46 * v), 30 + int(14 * v)) if r.random() < 0.85 else (92, 96, 44)
        d.line([x, y, x + r.randint(-2, 2), y - r.randint(2, 6)], fill=c, width=1)
    return im.filter(ImageFilter.GaussianBlur(0.4))


def principal():
    os.makedirs(SALIDA, exist_ok=True)
    for nombre, f in (("adoquin", adoquin), ("losas", losas), ("rejilla", rejilla), ("pasto", pasto)):
        f().save(os.path.join(SALIDA, f"suelo_{nombre}.png"))
        print("suelo_" + nombre)


if __name__ == "__main__":
    principal()
