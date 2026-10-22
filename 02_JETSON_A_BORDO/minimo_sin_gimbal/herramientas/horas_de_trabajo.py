# -*- coding: utf-8 -*-
"""
Calcula cuánto se trabajó con Claude a partir de las conversaciones guardadas en este computador (~/.claude/projects/*/*.jsonl).

Tiempo activo = suma de los intervalos entre mensajes consecutivos de una sesión cuando el intervalo es menor que el umbral (por defecto 20 min: más que eso se
considera que hubo una pausa). Es una estimación: no mide cuánto tiempo estuvo Brahian frente a la pantalla, solo cuánto hubo actividad registrada.
Cuenta también mensajes del usuario, respuestas, llamadas a herramientas e imágenes. Solo lectura. Uso: python horas_de_trabajo.py [--umbral-min 20] [--salida archivo.md]
"""
import argparse
import collections
import datetime
import glob
import json
import os
import sys

ZONA = datetime.timezone(datetime.timedelta(hours=-5))      # hora de Colombia


def leer(ruta):
    ev = []
    with open(ruta, encoding="utf-8", errors="replace") as f:
        for ln in f:
            try:
                j = json.loads(ln)
            except ValueError:
                continue
            ts = j.get("timestamp")
            if not ts:
                continue
            try:
                t = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                continue
            m = j.get("message") if isinstance(j.get("message"), dict) else {}
            c = m.get("content")
            n_img = n_uso = 0
            es_usuario_real = False
            if isinstance(c, list):
                for b in c:
                    if isinstance(b, dict):
                        if b.get("type") == "image":
                            n_img += 1
                        elif b.get("type") == "tool_use":
                            n_uso += 1
                        elif b.get("type") == "tool_result" and isinstance(b.get("content"), list):
                            n_img += sum(1 for x in b["content"] if isinstance(x, dict) and x.get("type") == "image")
                        elif b.get("type") == "text" and j.get("type") == "user" and not str(b.get("text", "")).lstrip().startswith("<"):
                            es_usuario_real = True
            elif isinstance(c, str) and j.get("type") == "user" and not c.lstrip().startswith("<"):
                es_usuario_real = True
            ev.append((t, j.get("type"), es_usuario_real, n_img, n_uso))
    return sorted(ev, key=lambda e: e[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--umbral-min", type=float, default=20.0)
    ap.add_argument("--salida", default="")
    a = ap.parse_args()
    umbral = datetime.timedelta(minutes=a.umbral_min)
    base = os.path.expanduser("~/.claude/projects")
    por_dia = collections.defaultdict(lambda: datetime.timedelta())
    tramos = []
    por_carpeta = collections.defaultdict(lambda: dict(sesiones=0, activo=datetime.timedelta(), usuario=0, resp=0, herr=0, img=0, ini=None, fin=None))
    for ruta in glob.glob(os.path.join(base, "*", "*.jsonl")):
        ev = leer(ruta)
        if len(ev) < 2:
            continue
        carpeta = os.path.basename(os.path.dirname(ruta))
        etiqueta = ("Dron-IA-Proyecto" if "Dron-IA-Proyecto" in carpeta else "Desktop-Claude" if carpeta.endswith("Desktop-Claude") else "otras (espacios de trabajo temporales)")
        d = por_carpeta[etiqueta]
        d["sesiones"] += 1
        d["ini"] = min(d["ini"], ev[0][0]) if d["ini"] else ev[0][0]
        d["fin"] = max(d["fin"], ev[-1][0]) if d["fin"] else ev[-1][0]
        for (t0, *_), (t1, tipo, usr, ni, nu) in zip(ev, ev[1:]):
            if t1 - t0 < umbral:
                d["activo"] += t1 - t0
                tramos.append((t0, t1))
                dia = t1.astimezone(ZONA).date()
                por_dia[dia] += t1 - t0
        for t, tipo, usr, ni, nu in ev:
            d["usuario"] += 1 if usr else 0
            d["resp"] += 1 if tipo == "assistant" else 0
            d["herr"] += nu
            d["img"] += ni
    h = lambda td: td.total_seconds() / 3600.0
    L = ["# Horas de trabajo con Claude (estimadas a partir de las conversaciones guardadas)\n",
         "Generado el %s con `02_JETSON_MINIMO/herramientas/horas_de_trabajo.py` (umbral de pausa: %.0f min). Es una **estimación del tiempo con actividad registrada**, no de cuánto tiempo estuvo la persona frente al computador ni de lo que se trabajó sin Claude (armar el dron, medir, salir al campo).\n" % (datetime.datetime.now(ZONA).strftime("%Y-%m-%d %H:%M"), a.umbral_min),
         "## Por carpeta de trabajo\n", "| Carpeta | Sesiones | Desde | Hasta | Horas activas | Mensajes de Brahian | Respuestas | Llamadas a herramientas | Imágenes |", "|---|---:|---|---|---:|---:|---:|---:|---:|"]
    tot = datetime.timedelta()
    for k, d in sorted(por_carpeta.items(), key=lambda kv: -kv[1]["activo"]):
        tot += d["activo"]
        L.append("| %s | %d | %s | %s | %.1f | %d | %d | %d | %d |" % (k, d["sesiones"], d["ini"].astimezone(ZONA).strftime("%d-%b %H:%M"), d["fin"].astimezone(ZONA).strftime("%d-%b %H:%M"), h(d["activo"]), d["usuario"], d["resp"], d["herr"], d["img"]))
    L.append("| **Total** | %d | | | **%.1f** | %d | %d | %d | %d |" % (sum(d["sesiones"] for d in por_carpeta.values()), h(tot), sum(d["usuario"] for d in por_carpeta.values()), sum(d["resp"] for d in por_carpeta.values()), sum(d["herr"] for d in por_carpeta.values()), sum(d["img"] for d in por_carpeta.values())))
    tramos.sort()
    union, cur = datetime.timedelta(), None
    for t0, t1 in tramos:
        if cur is None or t0 > cur[1]:
            if cur:
                union += cur[1] - cur[0]
            cur = [t0, t1]
        else:
            cur[1] = max(cur[1], t1)
    if cur:
        union += cur[1] - cur[0]
    L += ["", "Si dos sesiones corrieron a la vez, la suma de arriba cuenta ese rato dos veces. **Horas de reloj con alguna sesión activa (sin repetir): %.1f.**" % h(union)]
    L += ["", "## Por día (hora de Colombia)\n", "| Día | Horas activas |", "|---|---:|"]
    for dia in sorted(por_dia):
        L.append("| %s | %.1f |" % (dia.strftime("%Y-%m-%d"), h(por_dia[dia])))
    texto = "\n".join(L) + "\n"
    if a.salida:
        with open(a.salida, "w", encoding="utf-8") as f:
            f.write(texto)
    sys.stdout.buffer.write(texto.encode("utf-8"))


if __name__ == "__main__":
    main()
