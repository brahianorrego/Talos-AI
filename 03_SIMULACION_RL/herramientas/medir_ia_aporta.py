# -*- coding: utf-8 -*-
"""Medición del arquitecto (plan V17): ¿la política PPO V15 aporta algo frente a acciones fijas o al azar?
Compara la política con "solo reglas" (una acción fija: mantener, avanzar...) y con el azar. Resultados de la V15 en
informes/diagnostico_v17_ia_aporta.md. Uso (desde 03_SIMULACION_RL):
  .venv\\Scripts\\python.exe herramientas\\medir_ia_aporta.py mision --pol v15,mantener,avanzar,azar --n 256 --nivel 4 --salida x.json
  .venv\\Scripts\\python.exe herramientas\\medir_ia_aporta.py fijos  --pol v15,mantener,avanzar,azar --n 50
  .venv\\Scripts\\python.exe herramientas\\medir_ia_aporta.py probs  (probabilidades de la red en estados reales)
--pol acepta: v15, v15-est (estocástica), v15base, el nombre de una acción en minúsculas, azar o la ruta de un .zip.

V17 (docs/PLAN_V17_REFUERZO.md, sección 2): misión de la cancha (NIVEL_V17), 512 partidas de 5 min, mismas semillas para
todas las políticas. b0 = solo reglas (siempre QUEDARSE), b1 = azar entre los botones permitidos, b2 = regla de
posicionamiento por cobertura (entorno.regla_b2), o la ruta de un .zip (MaskablePPO o PPO de 7 botones; con "-est" al
final, estocástica). --set cambia constantes de entorno.py (reglas del ladrón: --set RULETA_V17=0, etc.).
  .venv\\Scripts\\python.exe herramientas\\medir_ia_aporta.py v17 --pol b0,b1,b2 --n 512 --salida informes\\v17_linea_base.json
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import torch

SIM = os.getcwd()
sys.path.insert(0, SIM)
sys.path.insert(0, os.path.join(SIM, "herramientas"))
import entorno as E  # noqa: E402

torch.set_num_threads(4)


class Fija(object):
    def __init__(self, a):
        self.a = a

    def predict(self, obs, env=None, deterministic=True):
        return np.full(len(obs), self.a), None


class Azar(object):
    def __init__(self, semilla=7):
        self.r = np.random.default_rng(semilla)

    def predict(self, obs, deterministic=True):
        return self.r.integers(0, len(E.CLASES), len(obs)), None


class Estocastica(object):
    def __init__(self, m):
        self.m = m

    def predict(self, obs, deterministic=True):
        return self.m.predict(obs, deterministic=False)


def cargar(nombre):
    from stable_baselines3 import PPO
    if nombre == "azar":
        return Azar()
    if nombre in [c.lower() for c in E.CLASES]:
        return Fija([c.lower() for c in E.CLASES].index(nombre))
    ruta = {"v15": "modelos_v15/ultimo.zip", "v15base": "modelos_v15/base_v15.zip"}.get(nombre.replace("-est", ""), nombre)
    m = PPO.load(ruta, device="cpu")
    return Estocastica(m) if nombre.endswith("-est") else m


def mision(pol, n, nivel, semilla, max_pasos):
    """Partidas aleatorias del nivel (currículo fijo, sin repaso) con el ladrón congelado del entrenamiento."""
    from entrenar import ActorCritico, actuar
    red_p = ActorCritico(E.OBS_PERSONA, E.N_ACC_PERSONA)
    red_p.load_state_dict(torch.load("modelos_v15/ladron_congelado.pt", weights_only=False))
    E.EntornoDronPersona.p_repaso_inicial = 0.0
    env = E.EntornoDronPersona(n, semilla=semilla, nivel=nivel)
    env.nivel = 0.21                                       # dificultad continua del final de la V15 (estado_entrenamiento.json)
    env.reset(np.ones(n, bool))
    vivo = np.ones(n, bool)
    res = np.array(["tiempo"] * n, dtype=object)
    vista, racha, pasos, mando, pierde, recupera = (np.zeros(n) for _ in range(6))
    acc_cnt = np.zeros(len(E.CLASES))
    fin = {}
    with torch.no_grad():
        for paso in range(max_pasos):
            obs = env.obs_dron().astype(np.float32)
            a, _ = pol.predict(obs, deterministic=True)
            a = np.asarray(a).astype(int)
            ap, _, _, _ = actuar(red_p, env.obs_persona())
            md = env.mascara_decision() & vivo
            acc_cnt += np.bincount(a[md], minlength=len(E.CLASES))
            r, _, done, info = env.step(a, ap, auto_reset=False)
            pasos += vivo
            mando += vivo & info["al_mando"]
            pierde += vivo & info["pierde"]
            recupera += vivo & info["recupera"]
            for i in np.where(done & vivo)[0]:
                res[i] = E.resultado_de(info, i)
                vista[i] = info["t_vista_ac"][i]
                racha[i] = info["racha"][i]
                fin[i] = dict(nr=int(info["n_readq"][i]), tr=float(info["t_readq_sum"][i]))
            vivo &= ~done
            if not vivo.any():
                break
    for i in np.where(vivo)[0]:                            # cortadas por max_pasos: lo acumulado hasta ahí
        vista[i], racha[i] = env.t_vista_ac[i], env.racha_max[i]
        fin[i] = dict(nr=int(env.n_readq[i]), tr=float(env.t_readq_sum[i]))
    tr = [fin[i]["tr"] / fin[i]["nr"] for i in fin if fin[i]["nr"] > 0]
    out = {k: float(np.mean(res == k)) for k in ["cumplida", "alcanzado", "perdido", "no_encontrado", "panel",
                                                    "choque_peaton", "geocerca", "tiempo"]}
    out.update(dur=float(np.mean(pasos) * E.DT), vista_s=float(np.mean(vista)), racha_s=float(np.mean(racha)),
               custodia60=float(np.mean(racha >= 60.0)), custodia90=float(np.mean(racha >= 90.0)),
               mando=float(mando.sum() / pasos.sum()), pierde=float(pierde.mean()), recupera=float(recupera.mean()),
               t_readq=float(np.mean(tr)) if tr else float("nan"),
               acciones=[round(float(x), 3) for x in acc_cnt / max(acc_cnt.sum(), 1)])
    return out


class B0(object):
    def predict(self, obs, env=None, deterministic=True):
        return np.full(len(obs), E.QUEDARSE), None


class B1(object):
    def __init__(self, semilla=7):
        self.r = np.random.default_rng(semilla)

    def predict(self, obs, env=None, deterministic=True):
        mk = env.action_masks()
        return np.argmax(self.r.random(mk.shape) * mk + mk * 1e-9, 1), None     # uno al azar entre los permitidos


class B2(object):
    def predict(self, obs, env=None, deterministic=True):
        return env.regla_b2(), None


class Red17(object):
    """Política de 7 botones (MaskablePPO o PPO): decide con la máscara de la V17; guarda sus probabilidades donde decide."""

    def __init__(self, ruta, estocastica=False):
        try:
            from sb3_contrib import MaskablePPO
            self.m = MaskablePPO.load(ruta, device="cpu")
        except Exception:
            from stable_baselines3 import PPO
            self.m = PPO.load(ruta, device="cpu")
        self.est = estocastica
        self.r = np.random.default_rng(11)
        self.P = []

    def predict(self, obs, env=None, deterministic=True):
        mk = env.action_masks()
        logits = self.m.policy.get_distribution(torch.as_tensor(obs)).distribution.logits.numpy()
        logits = np.where(mk, logits, -1e9)
        p = np.exp(logits - logits.max(1, keepdims=True))
        p /= p.sum(1, keepdims=True)
        dec = env.mascara_decision()
        if dec.any():
            self.P.append(p[dec])
        if self.est:
            return np.minimum((np.cumsum(p, 1) < self.r.random(len(p))[:, None]).sum(1), p.shape[1] - 1), None
        return p.argmax(1), None


def cargar17(nombre):
    if nombre in ("b0", "b1", "b2"):
        return {"b0": B0, "b1": B1, "b2": B2}[nombre]()
    if nombre == "b3":                                      # V17.1 · D-059: B3 = siempre SUBIR
        return Fija(E.SUBIR)
    if nombre.upper() in E.CLASES_V17:                      # un botón fijo (si no está permitido, el entorno usa QUEDARSE)
        return Fija(E.CLASES_V17.index(nombre.upper()))
    return Red17(nombre.replace("-est", ""), nombre.endswith("-est"))


def v17(pol, n, semilla, max_pasos):
    """Misión V17 (cancha): M1 custodia (60 s seguidos con el ladrón a la vista y el ID correcto), M2 re-adquisición
    (pérdidas de más de 1 s recuperadas en 10 s o menos), M3 rendición y seguridad. Plan V17, sección 2."""
    env = E.EntornoDronPersona(n, semilla=semilla, nivel=E.NIVEL_V17)
    vivo = np.ones(n, bool)
    res = np.array(["tiempo"] * n, dtype=object)
    fin = {}
    pasos = np.zeros(n)
    t_real8 = t_real8_bajo = t_dec = t_tot = 0
    acc_cnt = np.zeros(len(E.CLASES_V17))
    ap = np.full(n, E.N_ACC_PERSONA - 1)
    reconf = cambio_nodet = 0
    ent_hecho = np.zeros(n, bool)
    mapeo = []                                             # E7: fracción de las 2 V que el LiDAR mapeó en el 360° de entrada
    t_bajo8_ent = t_bajo8_est = 0
    t_fij, run_vis, tramos = 0, np.zeros(n, int), []
    ret, comp = np.zeros(n), np.zeros((n, len(E.R_COMP)))     # retorno de cada partida y por componente
    datos = lambda i, src: dict(racha=float(src["racha"][i]), vista=float(src["t_vista_ac"][i]), gmin=float(src["gmb_min"][i]),
                                nr=int(src["n_readq"][i]), tr=float(src["t_readq_sum"][i]), np_=int(src["n_perd"][i]),
                                n10=int(src["n_readq10"][i]), rul=int(src["ruleta"][i]), esc=int(src["escudo"][i]))
    with torch.no_grad():
        for paso in range(max_pasos):
            obs = env.obs_dron().astype(np.float32)
            a, _ = pol.predict(obs, env=env, deterministic=True)
            ent0 = env.entrada.copy()
            r_, _, done, info = env.step(np.asarray(a).astype(int), ap, auto_reset=False)
            ret += np.where(vivo, r_, 0.0)
            comp += np.where(vivo[:, None], info["r_comp"], 0.0)
            for i in np.where(ent0 & ~env.entrada & vivo & ~ent_hecho)[0]:
                ent_hecho[i] = True
                env._mapear_lidar(i)
                ok_v = 0
                for k in range(2):
                    c = (env.pa[i, 2 * k] + env.pb[i, 2 * k] + env.pb[i, 2 * k + 1]) / 3
                    ok_v += any(np.hypot(*((env.det_a[i, j] + env.det_b[i, j]) / 2 - c)) < 1.5 for j in range(env.det_n[i]))
                mapeo.append(ok_v / 2)
            pasos += vivo
            dec = info["decide17"] & vivo
            t_dec += int(dec.sum())
            t_tot += int(vivo.sum())
            acc_cnt += np.bincount(info["boton"][dec], minlength=len(E.CLASES_V17))
            dh = np.hypot(env.px - env.dx[:, None], env.py - env.dy[:, None])
            r8 = (env.activa & (dh < E.R_GENTE)).any(1) & vivo
            t_real8 += int(r8.sum())
            t_real8_bajo += int((r8 & (env.dz < E.Z_SEGURA - 0.05)).sum())
            t_bajo8_ent += int((r8 & (env.dz < E.Z_SEGURA - 0.05) & ent0).sum())
            t_bajo8_est += int((r8 & (env.dz_est < E.Z_SEGURA - 0.05)).sum())
            reconf += int((info["reconf"] & vivo).sum())
            cambio_nodet += int((info["cambio_nodet"] & vivo).sum())
            # cuánto del tiempo FIJADO decide la red, y cuánto dura cada vez que lo ve (seguido) antes de perderlo
            t_fij += int(((env.modo == E.FIJADO) & vivo).sum())
            ve_ = info["visto"] & vivo
            corta = (run_vis > 0) & ~ve_
            tramos.extend((run_vis[corta] * E.DT).tolist())
            run_vis = np.where(ve_, run_vis + 1, 0)
            for i in np.where(done & vivo)[0]:
                res[i] = E.resultado_de(info, i)
                fin[i] = datos(i, info)
            vivo &= ~done
            if not vivo.any():
                break
    if vivo.any():                                         # cortadas por max_pasos: lo acumulado hasta ahí
        src = dict(racha=env.racha_max, t_vista_ac=env.t_vista_ac, gmb_min=env.gmb_min_ep, n_readq=env.n_readq,
                   t_readq_sum=env.t_readq_sum, n_perd=env.n_perd, n_readq10=env.n_readq10, ruleta=env.n_ruleta,
                   escudo=env.n_escudo)
        for i in np.where(vivo)[0]:
            fin[i] = datos(i, src)
    F = [fin[i] for i in range(n)]
    racha = np.array([f["racha"] for f in F])
    perd, r10 = sum(f["np_"] for f in F), sum(f["n10"] for f in F)
    nr, tr = sum(f["nr"] for f in F), sum(f["tr"] for f in F)
    out = {k: float(np.mean(res == k)) for k in ["cumplida", "alcanzado", "perdido", "no_encontrado", "panel",
                                                    "choque_peaton", "geocerca", "tiempo"]}
    out.update(n=n, dur=float(np.mean(pasos) * E.DT),
               custodia60=float(np.mean(racha >= 60.0)), custodia90=float(np.mean(racha >= 90.0)),
               racha_s=float(racha.mean()), vista_s=float(np.mean([f["vista"] for f in F])),
               # complementarias (la de 60 s seguidos se satura en 0 en la cancha): racha >= 30 s y la de la V16 (rendición o
               # 60 s de vista acumulada)
               custodia30=float(np.mean(racha >= 30.0)),
               m1=float(np.mean(racha >= E.RACHA_M1_V17)),            # V17.1 · D-059: M1 = racha >= 30 s
               retorno=float(ret.mean()), retorno_comp={k: round(float(v), 2) for k, v in zip(E.R_COMP, comp.mean(0))},
               custodia_v16=float(np.mean((res == "cumplida") | (np.array([f["vista"] for f in F]) >= 60.0))),
               readq10=float(r10 / max(perd, 1)), t_readq=float(tr / max(nr, 1)), perdidas=float(perd / n),
               gimbal_fuera=int(sum(f["gmin"] < E.GIMBAL_MIN - 1e-6 for f in F)),
               bajo_330_con_persona_8m=float(t_real8_bajo / max(t_real8, 1)),
               bajo_330_8m_en_entrada=float(t_bajo8_ent / max(t_real8_bajo, 1)),
               bajo_330_pedida_con_persona_8m=float(t_bajo8_est / max(t_real8, 1)),     # sin el error del barómetro
               mapeo_entrada=float(np.mean(mapeo)) if mapeo else float("nan"),
               frac_decide=float(t_dec / max(t_tot, 1)), frac_decide_en_fijado=float(t_dec / max(t_fij, 1)),
               tramo_visto_medio_s=float(np.mean(tramos)) if tramos else float("nan"),
               tramo_visto_mediana_s=float(np.median(tramos)) if tramos else float("nan"), reconf_partida=float(reconf / n), cambio_nodet=cambio_nodet,
               ruleta_partidas=float(np.mean([f["rul"] > 0 for f in F])), escudo_partidas=float(np.mean([f["esc"] > 0 for f in F])),
               acciones={c: round(float(x), 3) for c, x in zip(E.CLASES_V17, acc_cnt / max(acc_cnt.sum(), 1))})
    if isinstance(pol, Red17) and pol.P:
        P = np.concatenate(pol.P)
        H = -(P * np.log(P + 1e-12)).sum(1)
        out.update(p_max_media=float(P.max(1).mean()), entropia_media=float(H.mean()), entropia_max=float(np.log(P.shape[1])))
    return out


def fijos(pol, n, semilla, escenarios):
    import evaluar_politica as EP
    out = {}
    for k, nombre in enumerate(escenarios):
        out[nombre] = EP.resumir(EP.correr_escenario(pol, nombre, n, semilla + 1000 * k, 120.0, 0.1))
        out[nombre]["acciones"] = [round(float(x), 3) for x in out[nombre]["acciones"]]
    return out


def probs(n, semilla):
    """Probabilidades de la red V15 en los estados donde decide (nivel 4, ladrón congelado)."""
    from stable_baselines3 import PPO
    from entrenar import ActorCritico, actuar
    m = PPO.load("modelos_v15/ultimo.zip", device="cpu")
    red_p = ActorCritico(E.OBS_PERSONA, E.N_ACC_PERSONA)
    red_p.load_state_dict(torch.load("modelos_v15/ladron_congelado.pt", weights_only=False))
    env = E.EntornoDronPersona(n, semilla=semilla, nivel=4)
    env.nivel = 0.21
    env.reset(np.ones(n, bool))
    P, V = [], []
    dec = tot = 0
    with torch.no_grad():
        for paso in range(1500):
            obs = env.obs_dron().astype(np.float32)
            t = torch.as_tensor(obs)
            d = m.policy.get_distribution(t)
            p = d.distribution.probs.numpy()
            v = m.policy.predict_values(t).numpy()[:, 0]
            md = env.mascara_decision()
            dec += md.sum()
            tot += len(md)
            if md.any():
                P.append(p[md])
                V.append(v[md])
            a = d.distribution.sample().numpy()
            ap, _, _, _ = actuar(red_p, env.obs_persona())
            env.step(a, ap, auto_reset=True)
    P = np.concatenate(P)
    H = -(P * np.log(P + 1e-12)).sum(1)
    return dict(frac_pasos_decide=float(dec / tot), n_estados=len(P), p_max_media=float(P.max(1).mean()),
                p_max_p90=float(np.percentile(P.max(1), 90)), entropia_media=float(H.mean()),
                entropia_p10=float(np.percentile(H, 10)), p_media=[round(float(x), 3) for x in P.mean(0)],
                argmax_frec=[round(float(x), 3) for x in np.bincount(P.argmax(1), minlength=10) / len(P)])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("modo")
    ap.add_argument("--pol", default="v15")
    ap.add_argument("--n", type=int, default=256)
    ap.add_argument("--nivel", type=int, default=4)
    ap.add_argument("--semilla", type=int, default=123)
    ap.add_argument("--max-seg", type=float, default=300.0)
    ap.add_argument("--esc", default="abierto,cambio_brusco,tras_muro,detras_punta,cambia_lado,debajo")
    ap.add_argument("--salida", default=None)
    ap.add_argument("--set", action="append", default=[], help="NOMBRE=VALOR de entorno.py (se puede repetir)")
    a = ap.parse_args()
    for kv in a.set:
        k, v = kv.split("=", 1)
        viejo = getattr(E, k)
        setattr(E, k, v if isinstance(viejo, str) else (bool(float(v)) if isinstance(viejo, bool) else type(viejo)(float(v))))
    todo = {}
    if a.modo == "probs":
        todo = probs(a.n, a.semilla)
        print(json.dumps(todo, indent=1))
    else:
        for nombre in a.pol.split(","):
            t0 = time.time()
            pol = cargar17(nombre) if a.modo == "v17" else cargar(nombre)
            if a.modo == "v17":
                todo[nombre] = v17(pol, a.n, a.semilla, int(a.max_seg / E.DT))
                todo[nombre]["set"] = a.set
            elif a.modo == "mision":
                todo[nombre] = mision(pol, a.n, a.nivel, a.semilla, int(a.max_seg / E.DT))
            else:
                todo[nombre] = fijos(pol, a.n, a.semilla, a.esc.split(","))
            print(nombre, "%.0f s" % (time.time() - t0), json.dumps(todo[nombre]), flush=True)
    if a.salida:
        json.dump(todo, open(a.salida, "w", encoding="utf-8"), indent=1)
