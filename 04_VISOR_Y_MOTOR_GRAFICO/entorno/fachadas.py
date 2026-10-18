# -*- coding: utf-8 -*-
"""
Texturas de las fachadas del campus (ladrillo con ventanas) para Unreal: una imagen por pared, del tamaño exacto de la pared en
metros (así las ventanas no salen estiradas). Lee entorno_u.json y escribe entorno/texturas/<edificio>_<lado>.png (no van a Git: se
regeneran con este archivo). Mismo dibujo que estacion/universidad.js.
    03_SIMULACION_RL\\.venv\\Scripts\\python.exe 04_VISOR_Y_MOTOR_GRAFICO\\entorno\\fachadas.py
"""
import json
import os
import random

from PIL import Image, ImageDraw

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "texturas")
PPM = 12                                                      # píxeles por metro


def fachada(tipo, ancho, alto, semilla):
    r = random.Random(semilla)
    W, H = max(8, int(ancho * PPM)), max(8, int(alto * PPM))
    base = {"torre": (176, 97, 63), "caseta": (169, 86, 58), "laboratorio": (201, 201, 196), "coliseo": (181, 86, 58)}.get(tipo, (181, 86, 58))
    im = Image.new("RGB", (W, H), base)
    d = ImageDraw.Draw(im, "RGBA")
    if tipo != "laboratorio":                                  # ladrillos: manchas más claras y más oscuras
        for _ in range(int(W * H / 38)):
            x, y = r.randrange(W), r.randrange(H)
            d.rectangle([x, y, x + r.randint(3, 6), y + 1], fill=(70, 25, 15, r.randint(0, 40)) if r.random() < 0.5 else (230, 150, 110, r.randint(0, 40)))
    def ventanas(paso, aw, ah, y0, vidrio, marco):
        y = y0
        while y + ah < H - 0.4 * PPM:
            x = 1.4 * PPM
            while x + aw * PPM < W - 0.5 * PPM:
                d.rectangle([x - 2, y - 2, x + aw * PPM + 2, y + ah * PPM + 2], fill=marco)
                d.rectangle([x, y, x + aw * PPM, y + ah * PPM], fill=vidrio)
                d.rectangle([x, y, x + aw * PPM * 0.4, y + ah * PPM], fill=(255, 255, 255, 40))
                x += (aw + 1.3) * PPM
            y += paso * PPM
    if tipo == "apartamentos":
        ventanas(3.0, 1.5, 1.4 * PPM, 1.0 * PPM, (42, 58, 74), (217, 211, 199))
        for y in range(int(3 * PPM), H, int(3 * PPM)):
            d.rectangle([0, y - 4, W, y], fill=(210, 205, 195, 230))
    elif tipo == "torre":
        ventanas(2.9, 1.3, 1.3 * PPM, 1.2 * PPM, (39, 55, 74), (207, 200, 187))
        for y in range(int(2.9 * PPM), H, int(2.9 * PPM)):
            d.rectangle([0, y - 3, W, y], fill=(205, 200, 190, 220))
        for x in range(0, W, int(5 * PPM)):
            d.rectangle([x, 0, x + int(0.9 * PPM), H], fill=(190, 100, 70, 230))
    elif tipo == "laboratorio":
        ventanas(3.2, 2.2, 1.8 * PPM, 1.4 * PPM, (58, 95, 134), (138, 143, 148))
    elif tipo == "ladrillo":
        ventanas(3.0, 2.0, 1.2 * PPM, 1.4 * PPM, (39, 55, 74), (122, 74, 53))
    elif tipo == "caseta":
        d.rectangle([W * 0.55, H * 0.22, W * 0.75, H], fill=(61, 42, 29)); d.rectangle([W * 0.1, H * 0.35, W * 0.45, H * 0.65], fill=(49, 64, 74))
    elif tipo == "coliseo":
        d.rectangle([0, H * 0.18, W, H * 0.48], fill=(38, 50, 61))
        for x in range(0, W, int(3.2 * PPM)):
            d.line([x, H * 0.18, x, H * 0.48], fill=(192, 82, 58), width=4)
    return im


def principal():
    with open(os.path.join(AQUI, "entorno_u.json"), encoding="utf-8") as f:
        E = json.load(f)
    os.makedirs(SALIDA, exist_ok=True)
    n = 0
    for k, b in enumerate(E["edificios"]):
        alto = b["alto"] - 3.0 if b["tipo"] == "coliseo" else b["alto"]
        sx, sy = b["tam"]
        for lado, ancho in (("ns", sx), ("eo", sy)):          # las paredes norte y sur miden sx; las este y oeste, sy
            tipo = "coliseo" if (b["tipo"] == "coliseo" and lado == "ns") else ("ladrillo" if b["tipo"] == "coliseo" else b["tipo"])
            fachada(tipo, ancho, alto, 100 * k + (7 if lado == "ns" else 11)).save(os.path.join(SALIDA, f"{b['nombre']}_{lado}.png"))
            n += 1
    print(f"{n} texturas en {SALIDA}")


if __name__ == "__main__":
    principal()
