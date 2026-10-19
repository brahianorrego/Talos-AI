# -*- coding: utf-8 -*-
"""
Posturas del maniquí que Unreal NO trae (agachado, recostado contra el panel, gateando), armadas a mano con cinemática directa sobre la
pose de reposo del propio maniquí. Todo en NumPy: no necesita el editor. Alturas pedidas a foto(): de pie 1.0, agachado 0.67, recostado
1.0 y gateando 0.35 de la estatura (ALTO_POSTURA de importar_repeticion.py y F_ALTO_POSTURA de entorno.py).
"""
import numpy as np

from maniquies_fk import IDENT, Esqueleto, Pose, qeje, qmul

X = (1, 0, 0)
Y = (0, 1, 0)
Z = (0, 0, 1)
ALTO_POSTURA = (1.0, 0.67, 1.0, 0.35)


def pose_reposo(E, k=0):
    c = E.clip("reposo")[k]
    p = Pose(E, c[:, :3], c[:, 3:])
    p.T[0] = 0
    p.R[0] = IDENT
    return p


def bajar_al_suelo(p, suelo_ref):
    """Mueve la pelvis en vertical hasta que los pies apoyen a la misma altura que de pie."""
    p.T[p.E.idx["pelvis"]][2] += suelo_ref - p.suelo()
    return p


def agachado(base, zeta=0.67, inclinacion=25.0, brazos=0.7):
    """Cuclillas: muslos adelante, pantorrillas atrás (tobillo bajo la cadera), tronco inclinado, cabeza al frente, brazos colgando."""
    alto0, suelo0 = base.alto(), base.suelo()
    objetivo = zeta * alto0

    def armar(th):
        p = base.copia()
        for lado in "lr":
            p.girar("thigh_" + lado, X, th)
            p.girar("calf_" + lado, X, -2 * th)
            p.girar("foot_" + lado, X, th)
        bajar_al_suelo(p, suelo0)
        p.girar("spine_01", X, -inclinacion * 0.5)
        p.girar("spine_03", X, -inclinacion * 0.5)
        p.girar("neck_01", X, inclinacion * 0.8)
        for lado in "lr":
            p.girar("upperarm_" + lado, X, inclinacion * brazos)
        return p

    lo, hi = 0.0, 100.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if armar(mid).alto() > objetivo:
            lo = mid
        else:
            hi = mid
    return armar((lo + hi) / 2)


def recostado(base, atras=9.0):
    """De pie con la espalda contra el panel: tronco echado hacia atrás, cabeza erguida, un pie adelante, manos atrás (simple, a mano)."""
    p = base.copia()
    p.girar("spine_01", X, atras * 0.5)
    p.girar("spine_03", X, atras * 0.5)
    p.girar("neck_01", X, -atras * 0.8)
    p.girar("thigh_r", X, 14)
    p.girar("calf_r", X, -14)
    p.girar("foot_r", X, 0)
    for lado in "lr":
        p.girar("upperarm_" + lado, X, -12)
    return p


def gateando(base, fase=0.0, amplitud=1.0, tronco=96.0, muslo=32.0):
    """A cuatro apoyos (base = pose_ref: brazos en A): rodillas y antebrazos en el suelo (gateo bajo), tronco casi horizontal, cabeza levantada al frente.
    fase en ciclos: brazo izquierdo con pierna derecha. Parte de una pose con los brazos ya colgando derechos (hacia abajo)."""
    s = np.sin(2 * np.pi * fase) * amplitud
    c = np.cos(2 * np.pi * fase) * amplitud
    p = base.copia()
    for lado, sg in (("l", 1), ("r", -1)):                                  # brazos colgando derechos (la pose de referencia los tiene en A)
        p.girar("upperarm_" + lado, Y, 45 * sg)
    p.girar("pelvis", X, -tronco)
    for lado, sg in (("l", 1), ("r", -1)):
        p.girar("thigh_" + lado, X, tronco + muslo + 20 * s * sg)           # el muslo queda inclinado: la rodilla adelante de la cadera
        p.girar("calf_" + lado, X, -(80 + muslo) - 18 * max(0.0, c * sg))   # pantorrilla horizontal hacia atrás
        p.girar("upperarm_" + lado, X, tronco - 12 * s * sg)                # el brazo vuelve a colgar y oscila al revés
        p.girar("lowerarm_" + lado, X, 90)                                  # antebrazo hacia delante, apoyado
    p.girar("neck_01", X, 38)
    p.girar("neck_02", X, 20)
    p.girar("head", X, 25)
    return p


def asentar_gateo(p):
    """Baja la pose hasta que las rodillas y los antebrazos toquen el suelo."""
    P, _ = p.fk()
    z = [P[p.E.idx[h]][2] for h in ("lowerarm_l", "lowerarm_r", "hand_l", "hand_r", "calf_l", "calf_r")]
    p.T[p.E.idx["pelvis"]][2] -= min(z) - 5.0
    return p


def pose_ref(E):
    """La pose de referencia del esqueleto (simétrica, brazos en A): base de las posturas que deben quedar parejas."""
    p = Pose(E, E.ref_p.copy(), E.ref_q.copy())
    p.T[0] = 0
    p.R[0] = IDENT
    return p
