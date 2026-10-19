# -*- coding: utf-8 -*-
"""
Arma, con NumPy, la animación del maniquí de Unreal para una persona de la simulación: un arreglo (cuadros, huesos, 7) con posición y
cuaternio LOCALES de cada hueso, a 24 cps, que maniquies_unreal.py convierte en un AnimSequence.
  - De pie: reposo -> caminar -> trotar de la plantilla Third Person, con la amplitud del paso y el ritmo según la velocidad real.
  - Agachado, recostado contra el panel y gateando: poses armadas a mano (maniquies_posturas.py); agachado camina con el paso de
    la plantilla en pequeño. Las transiciones salen de pos0 -> pos con el avance pt que ya trae foto().
  - Salto (fases 1 impulso, 2 vuelo, 3 aterrizaje): clips de salto, caída y aterrizaje de la plantilla.
La figura NO se desliza ni se mueve en el mundo: eso lo hace Sequencer con la posición de la repetición.
"""
import numpy as np

from maniquies_fk import IDENT, Esqueleto, qconj, qmul, qnorm, slerp
from maniquies_posturas import agachado, asentar_gateo, gateando, pose_ref, pose_reposo, recostado

V_CAMINAR, V_TROTAR = 3.0, 6.0            # m/s de la plantilla (movimiento de raíz de MF_Unarmed_Walk_Fwd y Jog_Fwd)
FPS = 24


def suave(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


class Animador:
    def __init__(self):
        E = self.E = Esqueleto()
        self.H = len(E.huesos)
        self.idle = self._clip("reposo")
        self.walk = self._clip("caminar", lazo=True)
        self.jog = self._clip("trotar", lazo=True)
        self.salto, self.caida, self.aterriza = self._clip("salto"), self._clip("caida"), self._clip("aterrizar")
        self.dt_clip = {n: E.d["clips"][n]["largo"] / (E.d["clips"][n]["n"] - 1) for n in E.d["clips"]}
        self.idle0 = self.idle[0]
        base = pose_reposo(E)
        ref = pose_ref(E)
        self.est_agachado = self._arr(agachado(base, inclinacion=40.0))
        self.est_recostado = self._arr(recostado(base))
        self.cr_estatica = self._arr(asentar_gateo(gateando(ref, 0.0, 0.0)))
        self.cr_ciclo = np.stack([self._arr(asentar_gateo(gateando(ref, k / 16.0, 1.0))) for k in range(16)])
        self.alto_pie = base.alto()

    @staticmethod
    def _arr(p):
        a = np.concatenate([p.T, p.R], -1)
        a[0, :3] = 0
        a[0, 3:] = IDENT
        return a

    def _clip(self, nombre, lazo=False):
        c = self.E.clip(nombre)
        c[:, 0, :3] = 0
        c[:, 0, 3:] = IDENT
        return c[:-1] if lazo else c

    # --------------------------------------------------------------------------------------- mezclas
    @staticmethod
    def mezcla(A, B, w):
        """A, B: (N, H, 7); w: (N,) -> mezcla de posición (lineal) y giro (esférica)."""
        w = np.asarray(w, float).reshape(-1, 1)
        T = A[..., :3] * (1 - w[..., None]) + B[..., :3] * w[..., None]
        return np.concatenate([T, slerp(A[..., 3:], B[..., 3:], w)], -1)

    @staticmethod
    def de_ciclo(clip, t, dt):
        """Pose del clip en lazo en el instante t (s de clip), por interpolación entre cuadros. t: (N,) -> (N, H, 7)."""
        n = len(clip)
        x = (t / dt) % n
        k0 = np.floor(x).astype(int) % n
        k1 = (k0 + 1) % n
        return Animador.mezcla(clip[k0], clip[k1], x - np.floor(x))

    def de_reposo(self, t):
        n = len(self.idle)
        x = np.clip(t / self.dt_clip["reposo"], 0, None) % (n - 1)
        k0 = np.floor(x).astype(int)
        return self.mezcla(self.idle[k0], self.idle[k0 + 1], x - k0)

    def delta_ciclo(self, clip, t, dt, w):
        """Diferencia del ciclo contra la pose de reposo (en el marco del padre), con amplitud w. -> (N, H, 7)"""
        P = self.de_ciclo(clip, t, dt)
        dR = qmul(P[..., 3:], qconj(self.idle0[None, :, 3:]))
        w = np.asarray(w, float).reshape(-1, 1)
        return np.concatenate([(P[..., :3] - self.idle0[None, :, :3]) * w[..., None],
                               slerp(np.broadcast_to(IDENT, dR.shape), dR, w)], -1)

    # --------------------------------------------------------------------------------------- posturas
    def postura_de_pie(self, t, v, run, dt):
        trote = v > 2.4                                   # el indicador run de foto() parpadea: manda la velocidad
        w = np.where(trote, np.clip(v / 4.5, 0.55, 1.0), np.clip(0.30 + 0.35 * v, 0.30, 1.0))       # amplitud del paso
        vclip = np.where(trote, V_TROTAR, V_CAMINAR)
        ct = np.cumsum(np.where(v > 0.03, v / (vclip * w), 0.0) * dt)                                # segundos de clip recorridos
        cam = self.de_ciclo(self.walk, ct, self.dt_clip["caminar"])
        tro = self.de_ciclo(self.jog, ct, self.dt_clip["trotar"])
        mov = self.mezcla(cam, tro, trote.astype(float))
        return self.mezcla(self.de_reposo(t), mov, np.where(v > 0.03, w * np.minimum(1.0, v / 0.15), 0.0))

    def postura_agachado(self, v, dt):
        wc = np.clip(v / 0.9, 0, 1) * 0.55
        ct = np.cumsum(np.where(v > 0.03, v / (V_CAMINAR * np.maximum(wc, 0.1)), 0.0) * dt)
        d = self.delta_ciclo(self.walk, ct, self.dt_clip["caminar"], wc)
        est = np.broadcast_to(self.est_agachado, d.shape).copy()
        est[:, 1, :2] += d[:, 1, :2]                                      # la pelvis solo se balancea de lado y de frente
        est[..., 3:] = qnorm(qmul(d[..., 3:], est[..., 3:]))
        return est

    def postura_recostado(self, n):
        return np.broadcast_to(self.est_recostado, (n,) + self.est_recostado.shape).copy()

    def postura_gateo(self, v, dt):
        a = suave(np.clip(v / 0.3, 0, 1))
        fase = np.cumsum(np.where(v > 0.03, v / 0.55, 0.0) * dt)
        x = (fase % 1.0) * 16
        k0 = np.floor(x).astype(int) % 16
        ciclo = self.mezcla(self.cr_ciclo[k0], self.cr_ciclo[(k0 + 1) % 16], x - np.floor(x))
        return self.mezcla(np.broadcast_to(self.cr_estatica, ciclo.shape), ciclo, a)

    # --------------------------------------------------------------------------------------- todo junto
    def animar(self, v, pos0, pos, pt, run, saltof=None, saltot=None, fps=FPS):
        """v (m/s), pos0/pos (0 de pie, 1 agachado, 2 recostado, 3 gateando), pt 0..1, run bool, por cuadro a 24 cps -> (N, H, 7)."""
        N = len(v)
        dt = 1.0 / fps
        t = np.arange(N) * dt
        v, run = np.asarray(v, float), np.asarray(run, bool)
        pos0, pos = np.asarray(pos0), np.asarray(pos)
        A = np.zeros((N, self.H, 7))
        B = np.zeros((N, self.H, 7))
        for j, hacer in enumerate((lambda: self.postura_de_pie(t, v, run, dt), lambda: self.postura_agachado(v, dt),
                                   lambda: self.postura_recostado(N), lambda: self.postura_gateo(v, dt))):
            usa0, usa1 = pos0 == j, pos == j
            if usa0.any() or usa1.any():
                P = hacer()
                A[usa0] = P[usa0]
                B[usa1] = P[usa1]
        salida = self.mezcla(A, B, np.clip(np.asarray(pt, float), 0, 1))   # lineal, como el alto de foto()
        if saltof is not None and np.any(np.asarray(saltof) > 0):
            salida = self.salto_encima(salida, np.asarray(saltof), np.asarray(saltot))
        return salida

    def sin_altura(self, P):
        """Quita de una pose de salto la subida de los pies (la altura la pone h de foto() en la posición del actor)."""
        P = P.copy()
        pos, rot = P[..., :3], P[..., 3:]
        Pw, _ = self.E.fk(pos, rot)
        piso = np.minimum(Pw[:, self.E.idx["foot_l"], 2], Pw[:, self.E.idx["foot_r"], 2])
        P[:, self.E.idx["pelvis"], 2] -= np.maximum(piso - 8.0, 0.0)
        return P

    def salto_encima(self, base, f, tf):
        """Fases del salto de foto(): 1 impulso (0.25 s: se agacha para saltar), 2 vuelo (piernas recogidas y luego caída), 3 aterrizaje
        (0.6 s). tf = segundos dentro de la fase. Con cuadros de entrada y salida suaves (0.1 s)."""
        N = len(f)
        pose = base.copy()
        w = np.zeros(N)
        m = f == 1
        if m.any():
            k = np.clip(tf[m] / 0.25 * 3.0, 0, 3.0)
            pose[m] = self.mezcla(self.salto[np.floor(k).astype(int)], self.salto[np.minimum(np.floor(k).astype(int) + 1, 25)], k - np.floor(k))
            w[m] = np.minimum(1.0, tf[m] / 0.1 + 0.2)
        m = f == 2
        if m.any():
            subida = self.sin_altura(self.salto[7:13])
            k = np.clip(tf[m] / 0.25 * 5.0, 0, 5.0)
            a = self.mezcla(subida[np.floor(k).astype(int)], subida[np.minimum(np.floor(k).astype(int) + 1, 5)], k - np.floor(k))
            c = self.sin_altura(self.de_ciclo(self.caida[:-1], tf[m], self.dt_clip["caida"]))
            pose[m] = self.mezcla(a, c, np.clip((tf[m] - 0.25) / 0.2, 0, 1))
            w[m] = 1.0
        m = f == 3
        if m.any():
            k = np.clip(tf[m] / 0.6 * 18.0, 0, 18.0)
            pose[m] = self.mezcla(self.aterriza[np.floor(k).astype(int)], self.aterriza[np.minimum(np.floor(k).astype(int) + 1, 25)], k - np.floor(k))
            w[m] = np.clip((0.6 - tf[m]) / 0.2, 0.0, 1.0)
        return self.mezcla(base, pose, w)
