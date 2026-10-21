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
PPM = 32                                                      # píxeles por metro


def ladrillos(d, r, W, H, base):
    """Hiladas de ladrillo de verdad: 7.5 cm de alto por 24 cm de largo, juntas de mortero y cada ladrillo con su tono."""
    ah, aw = max(2, int(0.075 * PPM)), max(4, int(0.24 * PPM))
    d.rectangle([0, 0, W, H], fill=(196, 188, 174))                       # mortero
    for k, y in enumerate(range(0, H, ah)):
        x = -(aw // 2 if k % 2 else 0)
        while x < W:
            f = r.uniform(0.82, 1.12)
            c = tuple(max(0, min(255, int(v * f + r.randint(-6, 6)))) for v in base)
            d.rectangle([x + 1, y + 1, x + aw - 1, y + ah - 1], fill=c)
            x += aw


def fachada(tipo, ancho, alto, semilla):
    r = random.Random(semilla)
    W, H = max(8, int(ancho * PPM)), max(8, int(alto * PPM))
    base = {"torre": (176, 97, 63), "caseta": (169, 86, 58), "laboratorio": (201, 201, 196), "coliseo": (181, 86, 58)}.get(tipo, (181, 86, 58))
    im = Image.new("RGB", (W, H), base)
    d = ImageDraw.Draw(im, "RGBA")
    if tipo != "laboratorio":
        ladrillos(d, r, W, H, base)
    def ventanas(paso, aw, ah, y0, vidrio, marco):
        y = y0
        while y + ah < H - 0.4 * PPM:
            x = 1.4 * PPM
            while x + aw * PPM < W - 0.5 * PPM:
                m = int(0.07 * PPM)
                d.rectangle([x - 0.12 * PPM, y - 0.18 * PPM, x + aw * PPM + 0.12 * PPM, y - 0.02 * PPM], fill=(170, 166, 158))       # dintel de concreto
                d.rectangle([x - m, y - m, x + aw * PPM + m, y + ah + m], fill=marco)                                              # marco
                d.rectangle([x, y, x + aw * PPM, y + ah], fill=vidrio)
                for k in range(1, 3):                                                                                              # divisiones del vidrio
                    d.line([x + aw * PPM * k / 3, y, x + aw * PPM * k / 3, y + ah], fill=marco, width=max(1, m))
                d.line([x, y + ah * 0.55, x + aw * PPM, y + ah * 0.55], fill=marco, width=max(1, m))
                d.polygon([(x, y + ah * 0.9), (x + aw * PPM * 0.55, y), (x + aw * PPM * 0.8, y), (x + aw * PPM * 0.25, y + ah * 0.9)], fill=(255, 255, 255, 38))   # reflejo
                d.rectangle([x - 0.1 * PPM, y + ah + m, x + aw * PPM + 0.1 * PPM, y + ah + m + 0.08 * PPM], fill=(168, 164, 156))    # alféizar
                x += (aw + 1.3) * PPM
            y += paso * PPM
    if tipo == "apartamentos":
        ventanas(3.0, 1.5, 1.4 * PPM, 1.0 * PPM, (42, 58, 74), (217, 211, 199))
        for y in range(int(3 * PPM), H, int(3 * PPM)):
            d.rectangle([0, y - 0.12 * PPM, W, y], fill=(210, 205, 195, 230))
    elif tipo == "torre":
        ventanas(2.9, 1.3, 1.3 * PPM, 1.2 * PPM, (39, 55, 74), (207, 200, 187))
        for y in range(int(2.9 * PPM), H, int(2.9 * PPM)):
            d.rectangle([0, y - 0.1 * PPM, W, y], fill=(205, 200, 190, 220))
        for x in range(0, W, int(5 * PPM)):
            d.rectangle([x, 0, x + int(0.9 * PPM), H], fill=(190, 100, 70, 230))
    elif tipo == "laboratorio":                                  # fachada de vidrio continua en bandas y franja naranja (fotos nocturnas, zona de vuelo)
        d.rectangle([0, 0, W, H], fill=(84, 88, 92))             # estructura gris oscuro
        for k in range(max(1, int(H / (3.4 * PPM)))):
            y = int(0.8 * PPM + k * 3.4 * PPM)
            d.rectangle([0.8 * PPM, y, W - 0.8 * PPM, y + 2.4 * PPM], fill=(70, 108, 142))              # vidrio azul
            d.rectangle([0.8 * PPM, y, W - 0.8 * PPM, y + 2.4 * PPM], outline=(200, 204, 208), width=max(2, int(0.08 * PPM)))
            for x in range(int(0.8 * PPM), int(W - 0.8 * PPM), int(2.2 * PPM)):                        # montantes
                d.rectangle([x, y, x + max(2, int(0.08 * PPM)), y + 2.4 * PPM], fill=(200, 204, 208))
            d.polygon([(0.8 * PPM, y + 2.4 * PPM), (W * 0.3, y), (W * 0.45, y), (0.8 * PPM + W * 0.15, y + 2.4 * PPM)], fill=(255, 255, 255, 36))      # reflejo
        d.rectangle([0, int(H * 0.5), W, int(H * 0.5 + 0.7 * PPM)], fill=(232, 118, 36))                  # franja naranja
        d.rectangle([0, 0, W, 0.5 * PPM], fill=(60, 64, 68))
    elif tipo == "ladrillo":
        ventanas(3.0, 2.0, 1.2 * PPM, 1.4 * PPM, (39, 55, 74), (122, 74, 53))
    elif tipo == "caseta":
        d.rectangle([W * 0.55, H * 0.22, W * 0.75, H], fill=(61, 42, 29)); d.rectangle([W * 0.1, H * 0.35, W * 0.45, H * 0.65], fill=(49, 64, 74))
    elif tipo == "coliseo":
        d.rectangle([0, H * 0.18, W, H * 0.48], fill=(38, 50, 61))
        for x in range(0, W, int(3.2 * PPM)):
            d.line([x, H * 0.18, x, H * 0.48], fill=(192, 82, 58), width=4)
    d.rectangle([0, H - 0.5 * PPM, W, H], fill=(140, 134, 126))                            # zócalo de concreto
    d.rectangle([0, 0, W, 0.35 * PPM], fill=(196, 190, 180))                              # cornisa
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
