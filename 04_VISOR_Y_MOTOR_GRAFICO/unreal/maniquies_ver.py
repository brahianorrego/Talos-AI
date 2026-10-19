# -*- coding: utf-8 -*-
"""Dibuja las poses del maniquí como figuras de palitos (de lado y de frente) para revisarlas sin abrir el editor."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CADENAS = [["pelvis", "spine_01", "spine_02", "spine_03", "spine_04", "spine_05", "neck_01", "neck_02", "head"],
           ["spine_05", "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l"], ["spine_05", "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r"],
           ["pelvis", "thigh_l", "calf_l", "foot_l", "ball_l"], ["pelvis", "thigh_r", "calf_r", "foot_r", "ball_r"]]


def dibujar(poses, titulos, archivo):
    n = len(poses)
    fig, ejes = plt.subplots(2, n, figsize=(3.4 * n, 8.2))
    ejes = np.array(ejes).reshape(2, n)
    for j, (p, t) in enumerate(zip(poses, titulos)):
        P, _ = p.fk()
        for fila, (a, b, nom) in enumerate(((1, 2, "de lado (y adelante)"), (0, 2, "de frente (x)"))):
            ax = ejes[fila, j]
            for cad in CADENAS:
                pts = np.array([P[p.E.idx[h]] for h in cad])
                ax.plot(pts[:, a], pts[:, b], "-o", ms=2.5, lw=2, color="#d33" if "_l" in cad[-1] else ("#36c" if "_r" in cad[-1] else "#222"))
            ax.axhline(0, color="#777", lw=0.8)
            ax.set_xlim(-110, 110); ax.set_ylim(-5, 190); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([0, 50, 100, 150])
            if fila == 0:
                ax.set_title(t, fontsize=9)
    plt.tight_layout(); plt.savefig(archivo, dpi=75); plt.close()
