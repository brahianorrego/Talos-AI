# -*- coding: utf-8 -*-
"""
Matemática de cuaternios y cinemática directa del esqueleto del maniquí de Unreal (datos de unreal/_cache/maniquies.json, que
vuelca maniquies_volcar.py). Sirve para armar y revisar poses sin abrir el editor. Cuaternio = (x, y, z, w); cm; marco de Unreal.
"""
import json
import os

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))


def cargar():
    with open(os.path.join(AQUI, "_cache", "maniquies.json"), encoding="utf-8") as f:
        return json.load(f)


def qmul(a, b):
    """a * b (primero b, luego a), vectorizado en la última dimensión."""
    ax, ay, az, aw = np.moveaxis(a, -1, 0)
    bx, by, bz, bw = np.moveaxis(b, -1, 0)
    return np.stack([aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
                     aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz], -1)


def qrot(q, v):
    qv = np.concatenate([v, np.zeros(v.shape[:-1] + (1,))], -1)
    conj = q * np.array([-1, -1, -1, 1.0])
    return qmul(qmul(q, qv), conj)[..., :3]


def qeje(eje, grados):
    e = np.asarray(eje, float)
    e = e / np.linalg.norm(e)
    a = np.radians(grados) / 2
    return np.concatenate([e * np.sin(a), [np.cos(a)]])


def qnorm(q):
    return q / np.linalg.norm(q, axis=-1, keepdims=True)


def slerp(a, b, t):
    """a, b: (..., 4); t: escalar o (...,) -> interpolación esférica por el camino corto."""
    a, b = qnorm(a), qnorm(b)
    d = np.sum(a * b, -1, keepdims=True)
    b = np.where(d < 0, -b, b)
    d = np.abs(d)
    t = np.asarray(t, float)[..., None] if np.ndim(t) else float(t)
    th = np.arccos(np.clip(d, -1, 1))
    s = np.sin(th)
    cerca = s < 1e-5
    w1 = np.where(cerca, 1 - t, np.sin((1 - t) * th) / np.where(cerca, 1, s))
    w2 = np.where(cerca, t, np.sin(t * th) / np.where(cerca, 1, s))
    return qnorm(w1 * a + w2 * b)


class Esqueleto:
    def __init__(self, datos=None):
        d = datos or cargar()
        self.d = d
        self.huesos = d["huesos"]
        self.idx = {h: i for i, h in enumerate(self.huesos)}
        self.padre = np.array([self.idx.get(d["padres"][h], -1) if d["padres"][h] not in (None, "None") else -1 for h in self.huesos])
        ref = np.array([d["ref"][h] for h in self.huesos], float)
        self.ref_p, self.ref_q = ref[:, :3], ref[:, 3:]

    def pose_clip(self, nombre, k):
        """(n_huesos, 7) del cuadro k del clip: x y z + cuaternio."""
        return np.array(self.d["clips"][nombre]["cuadros"][k], float)

    def clip(self, nombre):
        return np.array(self.d["clips"][nombre]["cuadros"], float)             # (n, huesos, 7)

    def fk(self, pos, rot):
        """pos (..., H, 3), rot (..., H, 4) locales -> posición y giro en el marco del componente."""
        P = np.zeros_like(pos)
        R = np.zeros_like(rot)
        for i in range(len(self.huesos)):
            p = self.padre[i]
            if p < 0:
                P[..., i, :], R[..., i, :] = pos[..., i, :], rot[..., i, :]
            else:
                P[..., i, :] = P[..., p, :] + qrot(R[..., p, :], pos[..., i, :])
                R[..., i, :] = qmul(R[..., p, :], rot[..., i, :])
        return P, R

    def p(self, nombre):
        return self.idx[nombre]


# ---------------------------------------------------------------------------------------------------- poses
def qconj(q):
    return q * np.array([-1, -1, -1, 1.0])


IDENT = np.array([0, 0, 0, 1.0])
HUESOS_VISIBLES = ["pelvis", "spine_01", "spine_02", "spine_03", "spine_04", "spine_05", "neck_01", "neck_02", "head", "clavicle_l", "upperarm_l",
                   "lowerarm_l", "hand_l", "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r", "thigh_l", "calf_l", "foot_l", "ball_l", "thigh_r",
                   "calf_r", "foot_r", "ball_r"]


class Pose:
    """Una pose = posición local y giro local de cada hueso. Los giros se piden en el marco del COMPONENTE (x derecha, y adelante, z arriba)."""

    def __init__(self, E, T, R):
        self.E, self.T, self.R = E, np.array(T, float), np.array(R, float)

    def copia(self):
        return Pose(self.E, self.T.copy(), self.R.copy())

    def fk(self):
        return self.E.fk(self.T, self.R)

    def girar(self, hueso, eje, grados):
        """Gira el hueso (y todo lo que cuelga de él) alrededor de su articulación; eje en el marco del componente."""
        E = self.E
        i = E.idx[hueso]
        _, Rw = self.fk()
        p = E.padre[i]
        Rp = Rw[p] if p >= 0 else IDENT
        q = qeje(eje, grados)
        d = qmul(qconj(Rp), qmul(q, Rp))
        self.R[i] = qnorm(qmul(d, self.R[i]))
        return self

    def mundo(self, hueso):
        P, _ = self.fk()
        return P[self.E.idx[hueso]]

    def alto(self):
        """Altura de la coronilla (cm): el hueso de la cabeza más 15 cm."""
        return self.mundo("head")[2] + 15.0

    def suelo(self):
        """Menor altura entre pies y puntas de los pies."""
        P, _ = self.fk()
        return min(P[self.E.idx[h]][2] for h in ("ball_l", "ball_r", "foot_l", "foot_r"))
