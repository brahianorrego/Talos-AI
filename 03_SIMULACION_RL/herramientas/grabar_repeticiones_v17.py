# -*- coding: utf-8 -*-
"""Repeticiones escogidas de la cancha V17 (D-065, para Unreal y el visor): corre partidas de una en una con una política
y guarda en repeticiones_v17/ (fuera de Git) la primera de cada tipo, con el mismo formato que salida_*/replay_v17.json,
más un LEEME.md con el modelo y la semilla de cada una. Tipos: el ladrón se rinde; se esconde tras una V y el dron lo
re-encuentra estando alto (> 4 m); salta para agarrar el dron; un civil curioso mira o graba; el ladrón cambia de V (L3).
Uso (desde 03_SIMULACION_RL):
  .venv\\Scripts\\python.exe herramientas\\grabar_repeticiones_v17.py --modelo modelos_v17_2\\ultimo.zip
"""
import argparse
import json
import os
import sys
import time

import torch

SIM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SIM)
import entorno as E  # noqa: E402
import entrenar_master as EM  # noqa: E402

TIPOS = {
    "rendicion": "El ladrón se rinde (contador de seguimiento completo)",
    "reencuentro_alto": "Se esconde tras una V y el dron lo vuelve a ver estando a más de 4 m de altura",
    "salto": "El ladrón salta para agarrar el dron",
    "civil_curioso": "El civil nota el dron y lo mira o lo graba con el celular",
    "cambio_de_v": "El dron ve la boca de la V y el ladrón corre a la otra V (regla L3)",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default=os.path.join("modelos_v17_2", "ultimo.zip"))
    ap.add_argument("--max-partidas", type=int, default=60)
    ap.add_argument("--semilla", type=int, default=500, help="semilla de la primera partida (luego +1, +2, ...)")
    ap.add_argument("--salida", default="repeticiones_v17")
    ap.add_argument("--tipos", default=",".join(TIPOS), help="solo estos tipos (los demás quedan como estén)")
    a = ap.parse_args()
    torch.set_num_threads(1)                                   # de a una partida y un hilo: no le quita CPU al entrenamiento
    from sb3_contrib import MaskablePPO
    pol = EM.PoliticaSB3(MaskablePPO.load(a.modelo, device="cpu"))
    red_p = EM.red_ladron(None)
    os.makedirs(a.salida, exist_ok=True)
    hechas = {t: None for t in TIPOS if t not in a.tipos.split(",")}     # None: no se buscan en esta corrida
    for k in range(a.max_partidas):
        if all(t in hechas for t in TIPOS):
            break
        semilla = a.semilla + k
        vio = set()

        def al_paso(env, info):
            if info["exito"][0]:
                vio.add("rendicion")
            if info["descubre"][0] and env.dz[0] > 4.0:
                vio.add("reencuentro_alto")
            if env.salto_f[0] > 0:
                vio.add("salto")
            if env.activa[0, 1] and env.c_est[0, 1] in (E.C_MIRA, E.C_GRABA):
                vio.add("civil_curioso")
            if env.n_ruleta[0] > 0:
                vio.add("cambio_de_v")

        t0 = time.time()
        rep = EM.grabar_nivel(pol, red_p, E.NIVEL_V17, semilla, 0, 0, al_paso=al_paso)
        nuevos = sorted(vio - set(hechas))
        for t in nuevos:
            hechas[t] = semilla
            rep_t = dict(rep, tipo=t, descripcion=TIPOS[t], semilla=semilla, modelo=a.modelo.replace("\\", "/"),
                         paneles_v17=[E.ANCHO_PANEL_V17, list(E.ALTO_PANEL_V17)])
            with open(os.path.join(a.salida, "%s.json" % t), "w", encoding="utf-8") as f:
                json.dump(rep_t, f, ensure_ascii=False)
        print("semilla %d: %s · %s · %.0f s" % (semilla, rep["resultado"], ", ".join(sorted(vio)) or "-", time.time() - t0),
              flush=True)
    # el LEEME sale de los archivos que hay en la carpeta (también los de corridas anteriores)
    def fila(t):
        ruta = os.path.join(a.salida, "%s.json" % t)
        if not os.path.exists(ruta):
            return "| %s | %s | no salió |" % (t, TIPOS[t])
        r = json.load(open(ruta, encoding="utf-8"))
        return "| %s | %s | %s (`%s`) |" % (t, TIPOS[t], r["semilla"], r["modelo"])
    filas = [fila(t) for t in TIPOS]
    with open(os.path.join(a.salida, "LEEME.md"), "w", encoding="utf-8") as f:
        f.write("# Repeticiones escogidas de la cancha V17\n\nGrabadas con `herramientas/grabar_repeticiones_v17.py`, "
                "modelo `%s`, paneles de %.1f m × %.1f-%.1f m (D-066), %s. Formato: el de `salida_*/replay_v17.json` "
                "(una lista de cuadros de `entorno.foto()`), más `tipo`, `descripcion`, `semilla` y `modelo`.\n\n"
                "| Archivo (`<tipo>.json`) | Qué muestra | Semilla (modelo) |\n|---|---|---|\n%s\n"
                % (a.modelo.replace("\\", "/"), E.ANCHO_PANEL_V17, E.ALTO_PANEL_V17[0], E.ALTO_PANEL_V17[1],
                   time.strftime("%Y-%m-%d"), "\n".join(filas)))
    print("listo:", hechas)


if __name__ == "__main__":
    main()
