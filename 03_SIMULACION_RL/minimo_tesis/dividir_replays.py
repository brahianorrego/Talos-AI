# -*- coding: utf-8 -*-
r"""Parte cada replay_protocolo*.json (13+ escenarios seguidos) en un archivo por escenario para el visor.

Salida: minimo_tesis/replay/escenarios/<decisor>/<escenario>.json y minimo_tesis/replay/escenarios/lista.json
(el visor lo lee para llenar el grupo "Mínimo indispensable · por escenario"). No corre simulaciones: solo corta los archivos ya hechos.
Uso: .venv/Scripts\python.exe -m minimo_tesis.dividir_replays
"""
import json
import os

from . import protocolo_comite as P

AQUI = os.path.dirname(os.path.abspath(__file__))
REPLAY = os.path.join(AQUI, "replay")
DECISORES = {"": "reglas (protocolo del comité)", "_reglas": "reglas", "_ia": "IA sola", "_ia_env": "IA + envolvente",
             "_ia_env_estricta": "IA + envolvente estricta"}


def main():
    lista = []
    for suf, etiqueta in DECISORES.items():
        ruta = os.path.join(REPLAY, "replay_protocolo%s.json" % suf)
        if not os.path.exists(ruta):
            continue
        d = json.load(open(ruta, encoding="utf-8"))
        ini = d["inicio"] + [len(d["cuadros"])]
        carpeta = os.path.join(REPLAY, "escenarios", suf.strip("_") or "comite")
        os.makedirs(carpeta, exist_ok=True)
        for i, nom in enumerate(d["escenarios"]):
            parte = dict(d, cuadros=d["cuadros"][ini[i]:ini[i + 1]], escenarios=[nom], inicio=[0], resultado="escenario")
            archivo = "%s/%s.json" % (suf.strip("_") or "comite", nom)
            with open(os.path.join(REPLAY, "escenarios", archivo), "w", encoding="utf-8") as fh:
                json.dump(parte, fh, ensure_ascii=False, separators=(",", ":"))
            lista.append({"decisor": etiqueta, "grupo": suf.strip("_") or "comite", "escenario": nom,
                          "texto": P.TODOS[nom][1] if nom in P.TODOS else nom, "archivo": archivo,
                          "segundos": round(len(parte["cuadros"]) * d["dt"], 1)})
    with open(os.path.join(REPLAY, "escenarios", "lista.json"), "w", encoding="utf-8") as fh:
        json.dump(lista, fh, ensure_ascii=False, indent=1)
    print(len(lista), "archivos de escenario")


if __name__ == "__main__":
    main()
