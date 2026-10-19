# -*- coding: utf-8 -*-
"""
De la repetición de la simulación (foto() cada 0.1 s) a lo que necesita cada maniquí a 24 cps: posición, giro hacia donde mira o camina,
velocidad, postura (pos0, pos, avance pt), carrera y fase del salto. NumPy puro (se prueba sin el editor).
"""
import math

import numpy as np

FPS = 24
GIRO_MAX = 420.0           # °/s: tope del giro del cuerpo (una persona gira rápido pero no al instante)


def _interp(xs, ys, x):
    return np.interp(x, xs, ys)


def trayectoria(C, dt, clave, n, fps=FPS):
    """C: cuadros de la repetición (ya recortados); clave: id de la persona; n: cuadros de salida a fps. Devuelve un dict de arreglos (n,)."""
    ks, d = [], []
    for k, c in enumerate(C):
        for p in c.get("pers", []):
            if p.get("id", p.get("rol")) == clave:
                ks.append(k)
                v = p.get("v", [0.0, 0.0])
                s = c.get("salto") if p.get("rol") == "ladron" else None
                d.append((p["p"][0], p["p"][1], v[0], v[1], p.get("mira", math.nan), int(p.get("pos0", 0) or 0), int(p.get("pos", 0) or 0),
                          float(p.get("pt", 1.0) or 1.0), bool(p.get("run", False)), int((s or {}).get("f", 0) or 0), float((s or {}).get("h", 0.0) or 0.0)))
    ks = np.array(ks, float)
    D = np.array(d, float)
    t = np.arange(n) / fps / dt                                     # índice (decimal) del cuadro de la repetición
    out = {"visible": np.array([(np.abs(ks - ti).min() <= 1.5) for ti in t])}
    out["x"], out["y"] = _interp(ks, D[:, 0], t), _interp(ks, D[:, 1], t)
    vx, vy = _interp(ks, D[:, 2], t), _interp(ks, D[:, 3], t)
    v = np.hypot(vx, vy)
    ancho = max(1, int(0.5 * fps))                                  # media móvil de 0.5 s: la velocidad de foto() salta entre 1.2 y 1.5
    out["v"] = np.convolve(np.pad(v, ancho, mode="edge"), np.ones(ancho) / ancho, mode="same")[ancho:-ancho]
    near = np.abs(ks[None, :] - t[:, None]).argmin(1)                # lo discreto, del cuadro más cercano
    out["pos0"], out["pos"] = D[near, 5].astype(int), D[near, 6].astype(int)
    out["pt"] = D[near, 7]                                           # el avance pt es de a 0.1 s: se toma del cuadro más cercano
    out["run"] = D[near, 8] > 0.5
    out["saltof"], out["h"] = D[near, 9].astype(int), _interp(ks, D[:, 10], t)
    # segundos dentro de la fase del salto
    tf = np.zeros(n)
    for i in range(1, n):
        tf[i] = tf[i - 1] + 1.0 / fps if out["saltof"][i] == out["saltof"][i - 1] and out["saltof"][i] > 0 else 0.0
    out["saltot"] = tf
    # rumbo: hacia donde se mueve; quieto, hacia donde mira (mira es el ángulo de la simulación, rad)
    mira = D[:, 4]
    mira_t = np.where(np.isnan(mira[near]), np.nan, mira[near])
    rumbo = np.zeros(n)
    previo = None
    for i in range(n):
        if out["v"][i] > 0.25:
            alvo = math.atan2(vy[i], vx[i])
        elif not math.isnan(mira_t[i]):
            alvo = mira_t[i]
        else:
            alvo = previo if previo is not None else 0.0
        if previo is None:
            previo = alvo
        da = (alvo - previo + math.pi) % (2 * math.pi) - math.pi
        paso = math.radians(GIRO_MAX) / fps
        previo += max(-paso, min(paso, da))
        rumbo[i] = previo
    out["rumbo"] = rumbo
    # guiñada de Unreal: la figura mira hacia +Y de su malla; el eje y del mundo está invertido -> yaw = -rumbo - 90°
    yaw = -np.degrees(np.unwrap(rumbo)) - 90.0
    out["yaw"] = yaw
    return out


def personas_de(C):
    claves = {}
    for c in C:
        for p in c.get("pers", []):
            claves.setdefault(p.get("id", p.get("rol")), (p.get("rol", "peaton"), p.get("est", 1.72)))
    return claves
