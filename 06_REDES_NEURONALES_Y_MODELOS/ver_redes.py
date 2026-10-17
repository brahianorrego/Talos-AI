# -*- coding: utf-8 -*-
"""
Muestra las dos redes neuronales del proyecto de grado, para enseñarlas en vivo:

  1. El DECISOR del mínimo indispensable (MLP de scikit-learn, minimo_tesis/decision.pkl y decision.json).
  2. La POLÍTICA PPO de la IA de refuerzo (Stable-Baselines3, modelos_v15/ultimo.zip).

Para cada una: (i) capas, neuronas y parámetros; (ii) diagrama e histograma de pesos en PNG
(08_EVIDENCIA_Y_DIAGRAMAS/redes/); (iii) qué probabilidades da sobre escenas de ejemplo.

Uso, desde la raíz del proyecto:
    03_SIMULACION_RL\\.venv\\Scripts\\python.exe 06_REDES_NEURONALES_Y_MODELOS\\ver_redes.py
    ... ver_redes.py --ppo 03_SIMULACION_RL\\modelos_v12\\ultimo.zip     (otra política)
    ... ver_redes.py --solo-decisor                                         (rápido, sin cargar torch)
"""
import argparse
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIM = os.path.join(RAIZ, "03_SIMULACION_RL")
SALIDA = os.path.join(RAIZ, "08_EVIDENCIA_Y_DIAGRAMAS", "redes")
sys.path.insert(0, SIM)


def titulo(t):
    print("\n" + "=" * 78 + "\n" + t + "\n" + "=" * 78)


def dibujar_red(capas, nombres, archivo, titulo_fig, max_nodos=14):
    """Diagrama de capas: un círculo por neurona (hasta max_nodos; el resto como '…') y el número real abajo."""
    fig, ax = plt.subplots(figsize=(2.2 * len(capas) + 2, 6))
    xs = np.arange(len(capas)) * 2.0
    pos = []
    for x, n in zip(xs, capas):
        k = min(n, max_nodos)
        ys = np.linspace(-1, 1, k) * (k / max_nodos) * 2.5
        pos.append([(x, y) for y in ys])
    for a, b in zip(pos[:-1], pos[1:]):
        for p in a:
            for q in b:
                ax.plot([p[0], q[0]], [p[1], q[1]], color="0.75", lw=0.3, zorder=1)
    for (x, n), pts, nom in zip(zip(xs, capas), pos, nombres):
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=120, color="#2b6cb0", edgecolor="white", zorder=2)
        if n > max_nodos:
            ax.text(x, 0, "…", ha="center", va="center", fontsize=18, color="white", zorder=3,
                    bbox=dict(boxstyle="round", fc="#2b6cb0", ec="none"))
        ax.text(x, -3.1, "%s\n%d neuronas" % (nom, n), ha="center", va="top", fontsize=9)
    ax.set_title(titulo_fig)
    ax.set_xlim(xs[0] - 1, xs[-1] + 1)
    ax.set_ylim(-4, 3)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(archivo, dpi=130)
    plt.close(fig)


def histogramas(matrices, nombres, archivo, titulo_fig):
    fig, axs = plt.subplots(1, len(matrices), figsize=(3.2 * len(matrices), 3))
    for ax, W, nom in zip(np.atleast_1d(axs), matrices, nombres):
        ax.hist(np.ravel(W), bins=60, color="#2b6cb0")
        ax.set_title("%s\n%s" % (nom, "×".join(map(str, np.shape(W)))), fontsize=9)
        ax.tick_params(labelsize=7)
    fig.suptitle(titulo_fig, fontsize=10)
    fig.tight_layout()
    fig.savefig(archivo, dpi=130)
    plt.close(fig)


# ------------------------------------------------------------------------------------------ decisor del mínimo
def ver_decisor():
    from minimo_tesis import decisor_ia as D
    titulo("1. DECISOR DEL MÍNIMO INDISPENSABLE (MLP de scikit-learn)")
    pesos = json.load(open(os.path.join(SIM, "minimo_tesis", "decision.json"), encoding="utf-8"))
    Ws = [np.array(c["W"]) for c in pesos["capas"]]
    bs = [np.array(c["b"]) for c in pesos["capas"]]
    capas = [Ws[0].shape[0]] + [W.shape[1] for W in Ws]
    print("Archivo: 03_SIMULACION_RL/minimo_tesis/decision.json (lo que va a la Jetson) y decision.pkl")
    print("Entradas (%d): %s" % (len(pesos["entradas"]), ", ".join(pesos["entradas"])))
    print("Capas: %s   activación oculta: %s   salida: %s" % (" -> ".join(map(str, capas)), pesos["activacion"],
                                                             pesos["salida"]))
    for i, (W, b) in enumerate(zip(Ws, bs)):
        print("  capa %d: %3d x %-3d pesos + %3d sesgos = %5d parámetros" % (i + 1, W.shape[0], W.shape[1], b.size,
                                                                         W.size + b.size))
    print("Total: %d parámetros" % sum(W.size + b.size for W, b in zip(Ws, bs)))
    print("Regla de decisión: DETENER_Y_ASCENDER si la probabilidad > %.2f durante %d cuadros seguidos "
          "(horizonte %.1f s)" % (pesos["umbral"], pesos["k_seguidos"], pesos["horizonte_s"]))

    dibujar_red(capas, ["entrada", "oculta 1", "oculta 2", "salida"],
                os.path.join(SALIDA, "decisor_minimo_red.png"), "Decisor del mínimo: MLP %s" % "-".join(map(str, capas)))
    histogramas(Ws, ["capa %d" % (i + 1) for i in range(len(Ws))], os.path.join(SALIDA, "decisor_minimo_pesos.png"),
                "Decisor del mínimo · distribución de los pesos")

    # escenas de ejemplo: cuadros reales del conjunto de PRUEBA (vuelos que el decisor nunca vio al entrenar)
    d = np.load(os.path.join(SIM, "minimo_tesis", "datos", "prueba.npz"))
    X, y = d["X"], d["y"]
    p = D.predecir_json(pesos, X)
    try:                                    # comprobación: el pickle de scikit-learn da lo mismo que el JSON
        m = D.Modelo.cargar(os.path.join(SIM, "minimo_tesis"))
        dif = float(np.max(np.abs(m.proba(X[:2000]) - p[:2000])))
        print("JSON (NumPy, Jetson) vs pickle (scikit-learn): diferencia máxima %.2e" % dif)
    except Exception as e:                  # p. ej. otra versión de scikit-learn
        print("No se pudo cargar decision.pkl (%s): en la Jetson usar decision.json" % type(e).__name__)
    rng = np.random.default_rng(0)
    print("\nEscenas de ejemplo (cuadros del conjunto de prueba; etiqueta = verdad del simulador):")
    cab = "  %-9s %-8s %-8s %-7s %-7s  %-6s %-22s %s" % ("persona", "alto_caja", "lidar*", "v_prop", "v_acerc",
                                                          "prob", "decide", "etiqueta")
    print(cab)
    print("  (* valores normalizados como los recibe la red; ver decisor_ia.py)")
    i_ent = {n: j for j, n in enumerate(pesos["entradas"])}
    for clase in (0, 1):
        for i in rng.choice(np.flatnonzero(y == clase), 3, replace=False):
            x = X[i]
            print("  %-9s %-9.3f %-8.1f %-7.1f %-7.1f  %-6.2f %-22s %s" % (
                "sí" if x[i_ent["detectada"]] > 0.5 else "no", x[i_ent["alto_caja"]], x[i_ent["lidar"]],
                x[i_ent["v_propia"]], x[i_ent["v_acercamiento"]], p[i],
                pesos["clases"][int(p[i] > pesos["umbral"])], "RIESGO" if clase else "sin riesgo"))
    acierto = np.mean((p > pesos["umbral"]) == (y > 0.5))
    print("En los %d cuadros de prueba, un solo cuadro sobre el umbral coincide con la etiqueta el %.1f %% de las veces"
          % (len(y), 100 * acierto))
    print("(cifra por cuadro; las métricas oficiales por vuelo están en informes/minimo_tesis_decisor_ia.md)")


# ------------------------------------------------------------------------------------------ política PPO
def ver_ppo(ruta, segundos):
    import torch
    from stable_baselines3 import PPO
    import entorno as E
    titulo("2. POLÍTICA PPO DE LA IA DE REFUERZO (Stable-Baselines3)")
    modelo = PPO.load(ruta, device="cpu")
    pol = modelo.policy
    print("Archivo: %s" % os.path.relpath(ruta, RAIZ))
    print(pol)
    actor = list(pol.mlp_extractor.policy_net.parameters()) + list(pol.action_net.parameters())
    critico = list(pol.mlp_extractor.value_net.parameters()) + list(pol.value_net.parameters())
    n = lambda ps: sum(q.numel() for q in ps)
    print("Parámetros: actor (decide la acción) %d · crítico (estima el valor, solo se usa al entrenar) %d · total %d"
          % (n(actor), n(critico), n(pol.parameters())))
    lin = [m for m in list(pol.mlp_extractor.policy_net) + [pol.action_net] if isinstance(m, torch.nn.Linear)]
    capas = [lin[0].in_features] + [m.out_features for m in lin]
    print("Actor: %s (tanh entre capas; salida = probabilidad de cada una de las %d acciones)"
          % (" -> ".join(map(str, capas)), capas[-1]))
    print("Acciones: %s" % ", ".join(E.CLASES))

    dibujar_red(capas, ["sensores", "oculta 1", "oculta 2", "acciones"], os.path.join(SALIDA, "ppo_actor_red.png"),
                "Política PPO (actor): %s" % "-".join(map(str, capas)))
    histogramas([m.weight.detach().numpy() for m in lin], ["capa %d" % (i + 1) for i in range(len(lin))],
                os.path.join(SALIDA, "ppo_actor_pesos.png"), "Política PPO · distribución de los pesos del actor")

    # escena de ejemplo: una misión completa (último nivel), con la política al mando
    env = E.EntornoDronPersona(1, semilla=7, nivel=E.N_NIVELES - 1)
    acc_p = np.full(1, E.N_ACC_PERSONA - 1)
    probs, impresos = [], 0
    print("\nMisión de ejemplo (nivel %d, semilla 7). Solo se muestra cuando la red decide (objetivo fijado):"
          % (E.N_NIVELES - 1))
    for paso in range(int(segundos / E.DT)):
        obs = env.obs_dron().astype(np.float32)
        with torch.no_grad():
            dist = pol.get_distribution(torch.as_tensor(obs))
            pr = dist.distribution.probs.numpy()[0]
        acc, _ = modelo.predict(obs, deterministic=True)
        if env.mascara_decision()[0]:
            probs.append(pr)
            if impresos < 6 and paso % int(5 / E.DT) == 0:
                top = np.argsort(pr)[::-1][:3]
                print("  t=%5.1f s  decide %-17s  %s" % (paso * E.DT, E.CLASES[int(acc[0])],
                                                        "  ".join("%s=%.2f" % (E.CLASES[j], pr[j]) for j in top)))
                impresos += 1
        _, _, done, _ = env.step(np.asarray(acc).astype(int), acc_p, auto_reset=True)
    if probs:
        P = np.array(probs)
        ent = float(np.mean(-np.sum(P * np.log(P + 1e-12), axis=1)))
        print("\nEn %d cuadros con el objetivo fijado:" % len(P))
        print("  probabilidad media de cada acción: %s" % "  ".join("%s=%.2f" % (c, v) for c, v in
                                                                   zip(E.CLASES, P.mean(0))))
        print("  probabilidad de la acción preferida, en promedio: %.2f (al azar sería %.2f)"
              % (P.max(1).mean(), 1 / len(E.CLASES)))
        print("  entropía media: %.2f (máximo posible %.2f = elegir al azar)" % (ent, np.log(len(E.CLASES))))
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.bar(E.CLASES, P.mean(0), color="#2b6cb0")
        ax.axhline(1 / len(E.CLASES), color="k", ls="--", lw=1, label="al azar")
        ax.set_ylabel("probabilidad media")
        ax.set_title("PPO · probabilidad media por acción con el objetivo fijado (entropía %.2f de %.2f)"
                     % (ent, np.log(len(E.CLASES))), fontsize=9)
        ax.tick_params(axis="x", rotation=45, labelsize=7)
        ax.legend()
        fig.tight_layout()
        fig.savefig(os.path.join(SALIDA, "ppo_probabilidades.png"), dpi=130)
        plt.close(fig)
    else:
        print("En %.0f s la red nunca tuvo el objetivo fijado; pruebe con más --segundos" % segundos)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ppo", default=os.path.join(SIM, "modelos_v15", "ultimo.zip"), help="modelo SB3 (.zip)")
    ap.add_argument("--segundos", type=float, default=90, help="duración de la misión de ejemplo del PPO")
    ap.add_argument("--solo-decisor", action="store_true", help="solo el decisor del mínimo (no carga torch)")
    a = ap.parse_args()
    os.makedirs(SALIDA, exist_ok=True)
    os.chdir(SIM)                           # los módulos de la simulación esperan correr desde su carpeta
    ver_decisor()
    if not a.solo_decisor:
        ver_ppo(os.path.abspath(os.path.join(RAIZ, a.ppo)) if not os.path.isabs(a.ppo) else a.ppo, a.segundos)
    print("\nImágenes en %s" % os.path.relpath(SALIDA, RAIZ))


if __name__ == "__main__":
    main()
