# -*- coding: utf-8 -*-
"""V17 (docs/PLAN_V17_REFUERZO.md): la cancha (2 V de paneles de 2 m), los 7 botones con efecto, la evasión por regla del
árbitro, la máscara de acciones (MaskablePPO), la partida desde la activación, la regla B2 y las reglas del ladrón. Las
reglas duras de CLAUDE.md también se prueban en la cancha: si una falla, no se relaja la prueba."""
import unittest

import numpy as np

import entorno as E

EPS = 1e-6
AP = lambda n: np.full(n, E.N_ACC_PERSONA - 1)


def fijado_quieto(n, d=4.5, z17=E.Z_SEGURA, semilla=0):
    """n partidas de la cancha con el ladrón ya designado, quieto a d m delante del dron y sin civil: la red decide."""
    env = E.EntornoDronPersona(n, semilla=semilla, nivel=E.NIVEL_V17)
    env.activa[:, 1:] = False
    env.pa += 60.0                                           # las V fuera de la zona: aquí se prueban botones, no paneles
    env.pb += 60.0
    env.px[:, 1:] = env.py[:, 1:] = 999.0
    env.dx[:], env.dy[:], env.psi[:] = 9.0, -3.0, np.pi / 2        # lejos de las V y de la geocerca
    env.px[:, 0], env.py[:, 0] = 9.0, -3.0 + d
    env.v_forzada[:, 0] = 0.0                                # el ladrón no se mueve, de pie
    env.tactico[:] = False
    g = -np.degrees(np.arctan2(E.Z_SEGURA - 1.0, d))         # la cámara ya apuntándole
    env.gimbal[:] = env.gimbal_cmd[:] = env.cam_pitch[:] = env.gb.ang[:] = env.gb.sp[:] = g
    env.modo[:], env.lock[:], env.trk[:], env.visto_alguna[:] = E.FIJADO, True, 0, True
    env.entrada[:] = False
    env.dz[:] = env.alt_obj[:] = E.Z_SEGURA
    env.e_baro[:] = 0.0
    env.e_gps[:] = 0.0
    env.z_v17[:] = z17
    env.ap.sincronizar(env, np.ones(n, bool))
    for _ in range(20):                                     # que los sensores (con retardo) lo vean
        env.step(np.zeros(n, int), AP(n), auto_reset=False)
    return env


class TestCancha(unittest.TestCase):

    def test_escenario(self):
        env = E.EntornoDronPersona(64, semilla=3, nivel=E.NIVEL_V17)
        self.assertEqual(env.A, E.ARENA_V17)
        self.assertEqual(E.ARENA, 25.0)                         # la arena de la V15/V16 no cambia
        self.assertTrue((env.lvl_ep == E.NIVEL_V17).all())
        L = np.hypot(*(env.pb - env.pa).transpose(2, 0, 1))
        np.testing.assert_allclose(L, E.ANCHO_PANEL_V17, atol=1e-9)
        self.assertTrue(((env.ph >= E.ALTO_PANEL_V17[0]) & (env.ph <= E.ALTO_PANEL_V17[1])).all())
        for v in range(2):
            u1 = env.pb[:, 2 * v] - env.pa[:, 2 * v]
            u2 = env.pb[:, 2 * v + 1] - env.pa[:, 2 * v + 1]
            np.testing.assert_allclose(env.pa[:, 2 * v], env.pa[:, 2 * v + 1])        # las dos alas comparten el vértice
            np.testing.assert_allclose((u1 * u2).sum(1), 0.0, atol=1e-9)              # V de 90°
        sep = np.hypot(*(env.pa[:, 2] - env.pa[:, 0]).T)
        self.assertTrue(((sep > E.SEP_V17 - 2 * np.sqrt(2) * E.AZAR_POS_V17) & (sep < E.SEP_V17 + 2 * np.sqrt(2) * E.AZAR_POS_V17)).all())
        boca = lambda v: (env.pb[:, 2 * v] + env.pb[:, 2 * v + 1]) / 2 - env.pa[:, 2 * v]
        self.assertTrue(((boca(0) * boca(1)).sum(1) < 0).all())                         # bocas hacia lados contrarios
        self.assertTrue((boca(0)[:, 1] < 0).all())                                       # la V del sur abre hacia el dron
        self.assertTrue((env.activa[:, 1:].sum(1) == 1).all())                           # 1 ladrón y 1 civil
        # E5: la partida empieza en la activación, en el borde sur de la zona, buscando
        self.assertTrue((np.abs(env.dy - E.Y_ACTIVA_V17) <= 1.0).all())
        self.assertTrue((env.modo == E.BUSCAR).all() and env.entrada.all())
        dl = np.hypot(env.px[:, 0] - env.dx, env.py[:, 0] - env.dy)
        self.assertTrue((dl >= 8.0 - EPS).all())
        self.assertTrue((np.abs(env.px[:, 0]) < env.A).all() and (np.abs(env.py[:, 0]) < env.A).all())

    def test_paneles_reales_d066(self):
        # D-066: medidas de Brahian (alas de 1.5 m, alto 2.2-2.3 m); la V de 90° y los 10 m entre V no cambian
        self.assertEqual(E.ANCHO_PANEL_V17, 1.5)
        self.assertEqual(E.ALTO_PANEL_V17, (2.2, 2.3))
        env = E.EntornoDronPersona(32, semilla=8, nivel=E.NIVEL_V17)
        np.testing.assert_allclose(np.hypot(*(env.pb - env.pa).transpose(2, 0, 1)), 1.5, atol=1e-9)
        self.assertTrue(((env.ph >= 2.2) & (env.ph <= 2.3)).all())

    def test_geocerca_de_la_cancha(self):
        env = E.EntornoDronPersona(4, semilla=1, nivel=E.NIVEL_V17)
        env.dx[:] = E.ARENA_V17 + 0.5
        _, _, done, info = env.step(np.zeros(4, int), AP(4), auto_reset=False)
        self.assertTrue(info["fuera"].all() and done.all())

    def test_entrada_completa_antes_de_verificar(self):
        env = E.EntornoDronPersona(32, semilla=2, nivel=E.NIVEL_V17)
        for _ in range(30):
            env.step(np.zeros(32, int), AP(32), auto_reset=False)
            self.assertFalse(((env.modo == E.VERIFICAR) & env.entrada).any())


class TestFotoVisor(unittest.TestCase):

    def test_cmd_y_arb_en_cada_cuadro(self):
        env = E.EntornoDronPersona(2, semilla=1, nivel=E.NIVEL_V17)
        quienes = set()
        for _ in range(150):
            env.step(np.zeros(2, int), AP(2), auto_reset=True)
            f = env.foto(0)
            self.assertTrue(f["v17"])
            self.assertEqual(len(f["cmd"]), 7)
            self.assertTrue(all(np.isfinite(f["cmd"][:5])))
            self.assertIn(f["cmd"][5], E.NOMBRE_ESTADO)
            self.assertIn(f["cmd"][6], ("red", "regla", "arbitro"))
            self.assertIsInstance(f["arb"], str)
            quienes.add(f["cmd"][6])
        self.assertIn("regla", quienes)


class TestBotones(unittest.TestCase):

    def correr_botones(self, d, z17, reps=8):
        # varias partidas por botón (cerca, el árbitro esquiva alguna por el ruido de la velocidad medida): se comparan
        # medias. Devuelve distancia, corrimiento lateral, altura pedida y altura por botón
        k = len(E.CLASES_V17)
        b = np.arange(reps * k) % k
        env = fijado_quieto(reps * k, d=d, z17=z17)
        self.assertGreater(env.mascara_decision().mean(), 0.3, "la red casi no decide")
        x0 = env.dx.copy()
        for _ in range(20):
            env.step(b, AP(len(b)), auto_reset=False)
        med = lambda v: np.array([v[b == j].mean() for j in range(k)])
        return (med(np.hypot(env.px[:, 0] - env.dx, env.py[:, 0] - env.dy)), med(env.dx - x0), med(env.z_v17),
                med(env.dz))

    def test_cada_boton_cambia_algo(self):
        q = E.QUEDARSE
        # a 7.5 m (sin amenaza): rodear, acercarse, subir, bajar
        d, lat, z17, dz = self.correr_botones(7.5, E.Z_SEGURA + 1.0)
        self.assertLess(lat[E.RODEAR_IZQ], lat[q] - 0.5)          # mirando al norte: la izquierda es -x
        self.assertGreater(lat[E.RODEAR_DER], lat[q] + 0.5)
        self.assertLess(d[E.ACERCARSE], d[q] - 0.5)
        self.assertGreater(z17[E.SUBIR], z17[q] + 0.4)
        self.assertLess(z17[E.BAJAR], z17[q] - 0.4)
        self.assertGreater(dz[E.SUBIR], dz[q] + 0.3)
        self.assertLess(dz[E.BAJAR], dz[q] - 0.3)
        # cerca (el dron mide ~1 m de más: ALEJARSE lleva a 6 m MEDIDOS)
        d, _, _, _ = self.correr_botones(4.4, E.Z_SEGURA, reps=30)
        self.assertGreater(d[E.ALEJARSE], d[q] + 0.3)

    def test_evasion_por_regla_sea_cual_sea_el_boton(self):
        # E3 (D-049, regla dura 5): con una amenaza real (persona a < 8 m que se acerca) el árbitro evade con SU maniobra,
        # elija la red lo que elija
        n = 6 * len(E.CLASES_V17)
        env = fijado_quieto(n, d=6.5)
        env.v_forzada[:, 0] = (0.0, -1.0)                      # camina hacia el dron (sin llegar al reflejo de ataque)
        evade, racha = np.zeros(n, bool), np.zeros(n, int)
        for _ in range(25):
            puede = env.estado == E.VIGILANDO
            _, _, _, info = env.step(np.arange(n) % len(E.CLASES_V17), AP(n), auto_reset=False)
            self.assertFalse(info["reflejo"].any())
            self.assertFalse((info["decide17"] & env.amenaza).any())       # ante la amenaza la red no manda
            racha = np.where(env.amenaza & puede, racha + 1, 0)
            # N_CONFIRMACION cuadros seguidos de amenaza real -> la maniobra arranca, sea cual sea el botón
            self.assertTrue((info["inicia"] | (racha < E.N_CONFIRMACION) | evade).all())
            evade |= info["inicia"]
        self.assertGreater(evade.mean(), 0.5, evade)                    # (que la prueba no quede vacía)

    def test_mascara(self):
        env = E.EntornoDronPersona(16, semilla=0, nivel=E.NIVEL_V17)
        mk = env.action_masks()
        self.assertEqual(mk.shape, (16, len(E.CLASES_V17)))
        self.assertTrue(mk[:, E.QUEDARSE].all())
        self.assertFalse(mk[~env.mascara_decision(), 1:].any())   # sin decisión: un solo botón
        env = fijado_quieto(8, z17=E.Z_SEGURA)
        mk = env.action_masks()
        d = env.mascara_decision()
        self.assertTrue(d.any())
        self.assertTrue(mk[d, E.RODEAR_IZQ].all() and mk[d, E.SUBIR].all())
        self.assertFalse(mk[:, E.BAJAR].any())                    # ya a la altura segura: nunca más abajo
        env.z_v17[:] = E.Z_MAX_V17
        self.assertFalse(env.action_masks()[:, E.SUBIR].any())
        # un botón prohibido se toma como QUEDARSE
        z = env.z_v17.copy()
        env.z_v17[:] = E.Z_SEGURA
        env.step(np.full(8, E.BAJAR), AP(8), auto_reset=False)
        self.assertTrue((env.z_v17 >= E.Z_SEGURA - EPS).all())

    def test_regla_b4_nunca_prohibido(self):
        # D-067: B4 y B4* nunca aprietan un botón prohibido, en partidas reales de la cancha
        env = E.EntornoDronPersona(16, semilla=3, nivel=E.NIVEL_V17)
        for k in range(300):
            mk = env.action_masks()
            b = env.regla_b4(oraculo=bool(k % 2))
            self.assertTrue(mk[np.arange(16), b].all())
            self.assertTrue(np.isin(b, (E.QUEDARSE, E.SUBIR, E.BAJAR)).all())
            env.step(b, AP(16), auto_reset=True)

    def test_regla_b2(self):
        env = fijado_quieto(8)
        b = env.regla_b2()
        mk = env.action_masks()
        self.assertTrue(mk[np.arange(8), b].all())


class TestReglasDurasCancha(unittest.TestCase):
    """Las reglas duras en la cancha, con botones al azar entre los permitidos (64 partidas x 60 s)."""

    @classmethod
    def setUpClass(cls):
        rng = np.random.default_rng(0)
        env = E.EntornoDronPersona(64, semilla=5, nivel=E.NIVEL_V17)
        cls.g_min, cls.g_max, cls.z17_min, cls.alt_fij_min = 99.0, -99.0, 99.0, 99.0
        cls.trans, cls.reconf_a_fijado, cls.inicia_sin_amenaza = [], [], 0
        cls.modos = set()
        cls.decide_sin_ver = 0
        for _ in range(600):
            modo0, cand0, tm0, tr0 = env.modo.copy(), env.cand.copy(), env.t_modo.copy(), env.t_resp.copy()
            mk = env.action_masks()
            a = np.argmax(rng.random(mk.shape) * mk + mk * 1e-9, 1)
            _, _, done, info = env.step(a, AP(64), auto_reset=False)
            cls.inicia_sin_amenaza += int((info["inicia"] & ~(env.amenaza | info["reflejo"])).sum())
            cls.decide_sin_ver += int((info["decide17"] & (modo0 != E.FIJADO)).sum())
            cls.modos |= set(np.unique(env.modo).tolist())
            for arr in (env.cam_pitch, env.gimbal, env.gimbal_cmd):
                cls.g_min, cls.g_max = min(cls.g_min, arr.min()), max(cls.g_max, arr.max())
            cls.z17_min = min(cls.z17_min, env.z_v17.min())
            fj = (env.modo == E.FIJADO) & (env.z_v17 > E.Z_SEGURA)
            if fj.any():
                cls.alt_fij_min = min(cls.alt_fij_min, env.alt_obj[fj].min())
            for i in np.where(~done & (env.modo != modo0))[0]:
                cls.trans.append((modo0[i], env.modo[i], cand0[i]))
                if modo0[i] == E.RECONFIRMAR and env.modo[i] == E.FIJADO:
                    cls.reconf_a_fijado.append((tm0[i] + E.DT, tr0[i], env.trk[i]))
            env.reset(done)

    def test_gimbal(self):
        self.assertGreaterEqual(self.g_min, E.GIMBAL_MIN - EPS)
        self.assertLessEqual(self.g_max, E.GIMBAL_MAX + EPS)

    def test_nunca_bajo_la_altura_segura_por_la_red(self):
        self.assertGreaterEqual(self.z17_min, E.Z_SEGURA - EPS)

    def test_busqueda_determinista(self):
        self.assertNotIn(E.BUSQUEDA_IA, self.modos)
        self.assertEqual(self.decide_sin_ver, 0)

    def test_arbitro_solo_ante_amenaza(self):
        self.assertEqual(self.inicia_sin_amenaza, 0)

    def test_humano_en_el_lazo(self):
        fij = [(a, c) for a, b, c in self.trans if b == E.FIJADO]
        self.assertTrue(any(a == E.VERIFICAR for a, _ in fij), "no hubo ningún lock-on")
        for antes, cand in fij:
            if antes == E.VERIFICAR:
                self.assertEqual(cand, 0)
        for t_en, t_resp, trk in self.reconf_a_fijado:
            self.assertGreaterEqual(t_en + 1e-9, t_resp)
            self.assertEqual(trk, 0)


class TestReglasLadron(unittest.TestCase):

    def correr(self, **apagar):
        viejos = {k: getattr(E, k) for k in apagar}
        for k, v in apagar.items():
            setattr(E, k, v)
        try:
            env = E.EntornoDronPersona(32, semilla=4, nivel=E.NIVEL_V17)
            pos, salto = set(), 0
            for _ in range(900):
                _, _, done, _ = env.step(np.zeros(32, int), AP(32), auto_reset=False)
                pos |= set(env.pos[:, 0].tolist())
                salto += int((env.salto_f > 0).sum())
            return env, pos, salto
        finally:
            for k, v in viejos.items():
                setattr(E, k, v)

    def test_con_todas(self):
        env, pos, _ = self.correr()
        self.assertGreater((env.n_ruleta > 0).mean(), 0.3)          # L3 aparece en >= 30 % de las partidas
        self.assertGreater(env.n_escudo.sum(), 0)
        self.assertGreater(len(pos), 1)

    def test_apagadas(self):
        env, pos, salto = self.correr(RULETA_V17=False, ESCUDO_V17=False, POSTURAS_V17=False, SALTO_V17=False,
                                      CURIOSO_V17=False)
        self.assertEqual(env.n_ruleta.sum(), 0)
        self.assertEqual(env.n_escudo.sum(), 0)
        self.assertEqual(pos, {E.DE_PIE})
        self.assertEqual(salto, 0)
        self.assertFalse((env.c_est[:, 1:] != 0).any())


class TestEntrenamientoV17(unittest.TestCase):

    def test_maskable_ppo_aprende_unos_pasos(self):
        import torch
        import entrenar_master as EM
        venv = EM.VecDron(16, 0, EM.red_ladron(None))
        mk = np.stack(venv.env_method("action_masks"))
        self.assertEqual(mk.shape, (16, len(E.CLASES_V17)))
        self.assertTrue(venv.has_attr("action_masks"))
        torch.manual_seed(0)
        m = EM.nuevo_ppo(venv, 1e-4, 0.003, 0)
        m.n_steps, m.batch_size = 8, 64
        m.rollout_buffer = m.rollout_buffer.__class__(8, m.observation_space, m.action_space, gamma=0.99, gae_lambda=0.95,
                                                      n_envs=16)
        m.learn(total_timesteps=256)
        self.assertGreaterEqual(m.num_timesteps, 256)


if __name__ == "__main__":
    unittest.main()
