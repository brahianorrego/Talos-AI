# -*- coding: utf-8 -*-
"""Medición del arquitecto (plan V17): ¿la política PPO V15 aporta algo frente a acciones fijas o al azar?
Compara la política con "solo reglas" (una acción fija: mantener, avanzar...) y con el azar. Resultados de la V15 en
informes/diagnostico_v17_ia_aporta.md. Uso (desde 03_SIMULACION_RL):
  .venv\\Scripts\\python.exe herramientas\\medir_ia_aporta.py mision --pol v15,mantener,avanzar,azar --n 256 --nivel 4 --salida x.json
  .venv\\Scripts\\python.exe herramientas\\medir_ia_aporta.py fijos  --pol v15,mantener,avanzar,azar --n 50
  .venv\\Scripts\\python.exe herramientas\\medir_ia_aporta.py probs  (probabilidades de la red en estados reales)
--pol acepta: v15, v15-est (estocástica), v15base, el nombre de una acción en minúsculas, azar o la ruta de un .zip.
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

    def predict(self, obs, deterministic=True):
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
    a = ap.parse_args()
    todo = {}
    if a.modo == "probs":
        todo = probs(a.n, a.semilla)
        print(json.dumps(todo, indent=1))
    else:
        for nombre in a.pol.split(","):
            t0 = time.time()
            pol = cargar(nombre)
            if a.modo == "mision":
                todo[nombre] = mision(pol, a.n, a.nivel, a.semilla, int(a.max_seg / E.DT))
            else:
                todo[nombre] = fijos(pol, a.n, a.semilla, a.esc.split(","))
            print(nombre, "%.0f s" % (time.time() - t0), json.dumps(todo[nombre]), flush=True)
    if a.salida:
        json.dump(todo, open(a.salida, "w", encoding="utf-8"), indent=1)
