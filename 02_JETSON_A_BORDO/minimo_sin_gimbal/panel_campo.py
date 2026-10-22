# -*- coding: utf-8 -*-
"""
Panel de campo del mínimo (v3): lo que se ve en el navegador del portátil y del celular durante las pruebas.
  /          panel del operador: video con cajas de YOLO, LiDAR, Pixhawk, percepción, enlaces, eventos y CONTROL DE TOMAS (paso 4).
  /persona   pantalla grande para quien camina: qué hacer, cuenta regresiva, pitidos, voz y vibración; también inicia y cancela la toma.
  /calibrar  medir el campo de visión y la inclinación de la cámara y del LiDAR (marcas en la pared + el dedo); guarda ~/calibracion_angulos.json.
  /alinear   marcar con clics en qué punto de la imagen pega el LiDAR; se guarda en ~/alineacion_lidar.json y registro_minimo.py lo anota en cada cuadro.
Solo lectura de sensores. Lo usa registro_minimo.py con --panel y --tomas (comparte sus sensores: un puerto serie no se abre dos veces).

    registro_minimo.py --video --panel 8080 --tomas ~/toma_actual.json --pitch-fijo -5
Prueba sin hardware (datos inventados):   python panel_campo.py --demo 8099
"""
import argparse
import glob
import json
import math
import os
import socket
import tempfile
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import cv2
import numpy as np

import geometria_lidar as GL

try:
    import config as _C
except Exception:          # panel de demostración fuera de la carpeta del código
    _C = None
GEO = dict(hfov=getattr(_C, "CAMARA_HFOV_DEG", 68.3), vfov=getattr(_C, "CAMARA_VFOV_DEG", 54.0),     # medidos con /calibrar (20-oct)
           cam_pitch=getattr(_C, "CAMARA_PITCH_DEG", -2.4), lidar_pitch=getattr(_C, "LIDAR_PITCH_DEG", -6.7))
ALTURA_PERSONA_M = 1.72     # para estimar la distancia por el alto de la caja (aproximado: la persona real puede medir otra cosa)
# perfiles del video hacia el navegador: (ancho, alto, calidad JPEG). 'normal' es el de siempre; los grandes cuestan más WiFi (ver /datos -> video.kbps)
PERFILES = {"normal": (640, 480, 55), "alta": (960, 720, 65), "maxima": (1280, 960, 72)}

UMBRAL_FRENA_CM, UMBRAL_ARBITRO_CM = 300, 800      # reglas duras: < 3 m frena, < 8 m el árbitro vigila
VOLT_AVISO, VOLT_CORTE = 14.4, 14.0                # desconectar a 14.0 V (plan del mínimo)
EDAD_MAX_MS = 2000
CELDAS = 4              # batería LiPo 4S: 16.8 V llena (4.2 V/celda); aviso a 14.4 V y desconectar a 14.0 V (3.5 V/celda), regla del plan del mínimo
# Voltaje en reposo por celda -> % de carga (curva típica de una LiPo; con carga el voltaje cae, así que el % es aproximado y optimista en vuelo)
CURVA_LIPO = ((3.27, 0), (3.61, 5), (3.69, 10), (3.71, 15), (3.73, 20), (3.75, 25), (3.77, 30), (3.79, 35), (3.80, 40), (3.82, 45), (3.84, 50),
              (3.85, 55), (3.87, 60), (3.91, 65), (3.95, 70), (3.98, 75), (4.02, 80), (4.08, 85), (4.11, 90), (4.15, 95), (4.20, 100))


def pct_lipo(v_total):
    c = v_total / CELDAS
    if c <= CURVA_LIPO[0][0]:
        return 0
    for (v0, p0), (v1, p1) in zip(CURVA_LIPO, CURVA_LIPO[1:]):
        if c <= v1:
            return round(p0 + (p1 - p0) * (c - v0) / (v1 - v0))
    return 100


CALIDAD_JPEG = 55       # con 92 cada cuadro pesaba ~70 KB (≈14 Mbps a 25 FPS): el WiFi del celular no lo lleva y el atraso crecía en el buffer
FPS_VIDEO = 30          # tope del video hacia el navegador (la cámara da ~30); lo que hace fluido el video es el buffer chico, no el tope
REALCE = False          # shortcut: el realce (CLAHE + nitidez) amplifica el ruido de esta cámara; activarlo solo para probar
PREPARACION_S = 5       # cuenta regresiva antes de empezar una toma, para que la persona se acomode

# Escenarios del paso 4 (plan, sección 6). Copia de herramientas/campo.py (ESCENARIOS): si cambia uno, cambiar el otro.
# fases: (segundos desde el inicio, pitidos, qué hace la persona)
ESCENARIOS = {
    "E0": dict(nombre="Sin nadie al frente (falsas detecciones)", dist="-", dur=20, campos=["rep", "altura"],
               guia=["Despeja el campo de la cámara: no debe haber nadie delante del dron.",
                     "Quédate fuera de la imagen (a un lado o detrás del dron) hasta que termine.",
                     "Dura 20 s. Sirve para contar las falsas detecciones."],
               fases=[(0, 1, "Nadie en el campo de la cámara")]),
    "E1": dict(nombre="Persona quieta en cada marca (5 s por marca)", dist="conos", dur=63, campos=["rep", "altura"],
               guia=["Párate de frente al dron, mirándolo, en el cono de 15 m y quédate quieto.",
                     "Cada 9 s suena la señal: camina al siguiente cono (12, 10, 8, 6, 4 y 2 m) y quédate quieto 5 s en él.",
                     "Sin hélices puedes llegar a 2 m. Con hélices, nunca a menos de 3 m."],
               fases=[(0, 1, "En la marca de 15 metros"), (9, 1, "A la marca de 12 metros"), (18, 1, "A 10 metros"),
                      (27, 1, "A 8 metros"), (36, 1, "A 6 metros"), (45, 1, "A 4 metros"), (54, 1, "A 2 metros")],
               conos=[15, 12, 10, 8, 6, 4, 2]),
    "E2": dict(nombre="Persona camina hacia el dron 15 → 3 m", dist="15->3", dur=16, campos=["rep", "altura"],
               guia=["Párate a 15 m del dron, de frente a él, y espera la señal.",
                     "Cuando suene, camina a paso normal hacia el dron y detente en la marca de 3 m (nunca más cerca)."],
               fases=[(0, 2, "En 15 metros, lista"), (3, 1, "¡Camina! y detente a 3 metros")]),
    "E3": dict(nombre="Persona trota hacia el dron 15 → 4 m", dist="15->4", dur=11, campos=["rep", "altura"],
               guia=["Párate a 15 m del dron, de frente a él, y espera la señal.",
                     "Cuando suene, trota hacia el dron y detente en la marca de 4 m (nunca más cerca)."],
               fases=[(0, 2, "En 15 metros, lista"), (3, 1, "¡Trota! y detente a 4 metros")]),
    "E4": dict(nombre="Persona cruza de lado (línea a 5, 8 o 12 m)", dist="5|8|12", dur=15, campos=["rep", "altura", "dist", "nota"],
               guia=["Elige la línea (5, 8 o 12 m) y anota en la nota si cruzas caminando o trotando.",
                     "Párate en el extremo de TU DERECHA de la línea (queda a la IZQUIERDA del dron), de frente al dron.",
                     "Cuando suene, cruza hacia TU IZQUIERDA (la DERECHA del dron). En la pantalla de la cámara ves que te mueves de izquierda a derecha."],
               fases=[(0, 2, "En el extremo de TU DERECHA de la línea"), (3, 1, "¡Cruza hacia TU IZQUIERDA!")]),
    "E5": dict(nombre="4B: silla con el dron empujada hacia la persona quieta", dist="15->3", dur=18, campos=["rep", "altura", "montaje"],
               guia=["La persona espera quieta, de frente al dron. Quien empuja la silla parte a 15 m de ella.",
                     "Cuando suene, empuja despacio (~1 m/s) hacia la persona y detente a 3 m."],
               fases=[(0, 2, "Silla en 15 metros, persona quieta"), (3, 1, "¡Empuja despacio! Parar a 3 metros")]),
    "E6": dict(nombre="Cartón (panel) acercándose al dron, empujado en la silla", dist="15->3", dur=18, campos=["rep", "altura", "montaje"],
               guia=["Pon el cartón a 15 m del dron, de frente a él. Quien empuja queda escondido detrás.",
                     "Cuando suene, empuja el cartón hacia el dron y detente a 3 m."],
               fases=[(0, 2, "Cartón en 15 metros, quien empuja escondido"), (3, 1, "¡Empuja! Parar a 3 metros")]),
}
MONTAJES = ("4A", "4B-silla", "4B-mano")

_cv = threading.Condition()
_img, _t_img, _n = None, 0.0, 0              # último cuadro anotado (lo deja publicar) y su hora de captura
_jpegs = {k: (None, 0.0) for k in PERFILES}   # perfil -> (último JPEG ya codificado, hora de captura); lo deja el hilo codificador
_njs = {k: 0 for k in PERFILES}
_esp = {k: 0 for k in PERFILES}              # navegadores viendo cada perfil de /video: sin nadie no se anota ni se codifica
_bytes_tx = deque(maxlen=600)                # (hora, bytes) de lo enviado por /video, para medir los kbps
_exp = dict(media=None, sat=None, osc=None)  # exposición de la imagen (cada 6 cuadros)
_sist = dict(t=0.0, cpu=None, gpu=None)      # temperaturas de la Jetson
_ncuadro, _tam_origen = 0, (0, 0)
_datos = {}
_hist = deque(maxlen=150)                           # distancia del LiDAR, ~10 s
_eventos = deque(maxlen=12)
_prev = {}
_clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

# --- alineación LiDAR <-> cámara (/alinear): en qué punto del cuadro pega el rayo ---
RUTA_ALINEACION = os.path.expanduser("~/alineacion_lidar.json")   # shortcut: misma ruta en registro_minimo.py, si cambia una cambia la otra
LIDAR_MAX_CLIC_M = 20.0     # un clic con el LiDAR leyendo más que esto no vale: el rayo no está pegando en el objeto de prueba (da ~58 m: la pared del fondo)
_alin = dict(punto=None, clics=[])      # punto = dict(x, y, n, t, dist_m) normalizado 0..1 sobre el cuadro; clics = dict(x, y, m, ok)
_lock_a = threading.Lock()

# --- tomas (paso 4) ---
_ruta_tomas = None
_sel = dict(esc="E2", rep=1, altura=0.0, montaje="4A", dist="", nota="")
_tm = dict(activa=False, id="", esc="", n=0, texto="", pitidos=0, t0=0.0, dur=0.0, prep=0.0, fase=-1)
_tomas_hist = deque(maxlen=40)
_cancelar = threading.Event()
_lock_t = threading.Lock()


def _v(x):
    """'' / None / NaN -> None (JSON válido)."""
    return None if x in ("", None) or (isinstance(x, float) and math.isnan(x)) else x


def _dist_cam(alto_norm):
    """Distancia a la persona por el alto de su caja (cámara de agujero): d = altura real / (2 tan(VFOV/2) · alto normalizado). Solo orientativa."""
    return ALTURA_PERSONA_M / (2.0 * math.tan(math.radians(GEO["vfov"] / 2.0)) * max(alto_norm, 1e-3))


def _texto(img, t, org, esc, color, grosor):
    cv2.putText(img, t, org, cv2.FONT_HERSHEY_SIMPLEX, esc, (0, 0, 0), grosor * 3, cv2.LINE_AA)       # contorno negro para que se lea sobre cualquier fondo
    cv2.putText(img, t, org, cv2.FONT_HERSHEY_SIMPLEX, esc, color, grosor, cv2.LINE_AA)


def anotar(frame, cajas, fila=None):
    """Copia para mostrar + cajas + medida del LiDAR sobre el video. YOLO NO ve esta imagen (usa la original). Todo escala con el ancho (k = 1 a 640 px)."""
    img = frame.copy()
    if REALCE:
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        lab[:, :, 0] = _clahe.apply(lab[:, :, 0])
        img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        img = cv2.addWeighted(img, 1.35, cv2.GaussianBlur(img, (0, 0), 2.0), -0.35, 0)
    alto, ancho = img.shape[:2]
    k = ancho / 640.0
    g = lambda v: max(1, int(round(v * k)))
    fuente = cv2.FONT_HERSHEY_SIMPLEX
    with _lock_a:
        punto, clics = _alin["punto"], list(_alin["clics"])
    fila = fila or {}
    cm = _v(fila.get("lidar_cm"))
    lid_m = cm / 100.0 if cm is not None and fila.get("lidar_valido") and (_v(fila.get("edad_lidar_ms")) or 9999) < EDAD_MAX_MS else None
    col_l = (80, 80, 255) if lid_m is not None and lid_m < UMBRAL_FRENA_CM / 100.0 else (255, 255, 0)      # BGR: rojo bajo 3 m, cian si no
    pc = GL.punto_para(lid_m) if punto else None          # el rayo cae más abajo cuanto más cerca (paralaje entre LiDAR y cámara)
    pxy = (int(pc[0] * ancho), int(pc[1] * alto)) if pc else None
    for x1, y1, x2, y2, tid, conf in cajas:
        p1, p2 = (int(x1), int(y1)), (int(x2), int(y2))
        en_caja = bool(pxy and p1[0] <= pxy[0] <= p2[0] and p1[1] <= pxy[1] <= p2[1])
        cv2.rectangle(img, p1, p2, (0, 165, 255) if en_caja else (80, 220, 120), g(3) if en_caja else g(2), cv2.LINE_AA)
        txt = "ID %d  %d%%" % (tid, round(conf * 100))
        (w, h), _ = cv2.getTextSize(txt, fuente, 0.55 * k, g(1))
        cv2.rectangle(img, (p1[0], max(0, p1[1] - h - g(8))), (p1[0] + w + g(8), p1[1]), (80, 220, 120), -1)
        cv2.putText(img, txt, (p1[0] + g(4), max(h + g(2), p1[1] - g(5))), fuente, 0.55 * k, (20, 30, 20), g(1), cv2.LINE_AA)
        trunc = y1 < g(3) or y2 > alto - g(3)
        _texto(img, "cam %s%.1f m" % (">" if trunc else "~", _dist_cam((y2 - y1) / alto)), (p1[0] + g(4), min(alto - g(6), p2[1] + g(18))), 0.55 * k, (80, 220, 120), g(1))
        if en_caja:
            _texto(img, "LiDAR EN LA PERSONA", (p1[0] + g(4), min(alto - g(26), p2[1] + g(40))), 0.55 * k, (0, 165, 255), g(1))
    for c in clics:                                     # clics de prueba: amarillo = valido, rojo = el LiDAR no pegaba en nada cercano
        cv2.drawMarker(img, (int(c["x"] * ancho), int(c["y"] * alto)), (0, 220, 255) if c["ok"] else (80, 80, 255), cv2.MARKER_TILTED_CROSS, g(14), g(2))
    if pxy:                                             # punto guardado: donde pega el LiDAR, con su distancia al lado
        px, py = pxy
        cv2.circle(img, (px, py), g(10), col_l, g(2), cv2.LINE_AA)
        for a, b in (((-22, 0), (-12, 0)), ((12, 0), (22, 0)), ((0, -22), (0, -12)), ((0, 12), (0, 22))):
            cv2.line(img, (px + int(a[0] * k), py + int(a[1] * k)), (px + int(b[0] * k), py + int(b[1] * k)), col_l, g(2), cv2.LINE_AA)
        et = "%.2f m" % lid_m if lid_m is not None else "sin retorno"
        (w, h), _ = cv2.getTextSize(et, fuente, 0.9 * k, g(2))
        bx = min(px + g(16), ancho - w - g(10))
        cv2.rectangle(img, (bx - g(4), py - h - g(8)), (bx + w + g(4), py + g(6)), (0, 0, 0), -1)
        cv2.putText(img, et, (bx, py), fuente, 0.9 * k, col_l, g(2), cv2.LINE_AA)
    # lectura fija en la esquina (aunque no haya punto de alineación guardado)
    et = "LiDAR  %s" % ("%.2f m" % lid_m if lid_m is not None else "sin retorno")
    (w, h), _ = cv2.getTextSize(et, fuente, 0.8 * k, g(2))
    cv2.rectangle(img, (g(8), g(8)), (g(8) + w + g(14), g(8) + h + g(14)), (0, 0, 0), -1)
    cv2.putText(img, et, (g(15), g(15) + h), fuente, 0.8 * k, col_l, g(2), cv2.LINE_AA)
    return img


def _cargar_alineacion():
    try:
        with open(RUTA_ALINEACION, encoding="utf-8") as f:
            j = json.load(f)
        _alin["punto"] = dict(x=float(j["x"]), y=float(j["y"]), n=j.get("n", 0), t=j.get("t", 0), dist_m=j.get("dist_m"))
    except (OSError, ValueError, KeyError):
        _alin["punto"] = None


def _api_alinear(ruta, q):
    """/alinear/<clic|quitar|limpiar|guardar|borrar|estado>  ->  (codigo, dict). Los clics son de prueba; 'guardar' deja la mediana de los válidos."""
    acc = ruta.rsplit("/", 1)[-1]
    with _lock_a:
        if acc == "clic":
            try:
                x, y = float(q["x"][0]), float(q["y"][0])
            except (KeyError, ValueError, IndexError):
                return 400, dict(mensaje="faltan x e y")
            if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
                return 400, dict(mensaje="x e y deben estar entre 0 y 1")
            m = (_datos.get("lidar") or {}).get("m")
            _alin["clics"] = (_alin["clics"] + [dict(x=x, y=y, m=m, ok=m is not None and m < LIDAR_MAX_CLIC_M)])[-12:]
        elif acc == "quitar":
            _alin["clics"] = _alin["clics"][:-1]
        elif acc == "limpiar":
            _alin["clics"] = []
        elif acc == "guardar":
            buenos = [c for c in _alin["clics"] if c["ok"]]
            if not buenos:
                return 400, dict(mensaje="no hay clics válidos: el LiDAR tiene que estar leyendo el objeto de prueba (menos de %d m)" % LIDAR_MAX_CLIC_M)
            med = lambda v: sorted(v)[len(v) // 2] if len(v) % 2 else (sorted(v)[len(v) // 2 - 1] + sorted(v)[len(v) // 2]) / 2.0
            _alin["punto"] = dict(x=round(med([c["x"] for c in buenos]), 4), y=round(med([c["y"] for c in buenos]), 4), n=len(buenos),
                                  t=round(time.time(), 1), dist_m=round(med([c["m"] for c in buenos]), 2))
            tmp = RUTA_ALINEACION + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(_alin["punto"], f)
            os.replace(tmp, RUTA_ALINEACION)
            _alin["clics"] = []
        elif acc == "borrar":
            _alin["punto"], _alin["clics"] = None, []
            try:
                os.remove(RUTA_ALINEACION)
            except OSError:
                pass
        elif acc != "estado":
            return 404, dict(mensaje="acción desconocida")
        return 200, dict(punto=_alin["punto"], clics=list(_alin["clics"]), lidar_m=(_datos.get("lidar") or {}).get("m"), max_m=LIDAR_MAX_CLIC_M)


def _evento(nivel, texto):
    _eventos.appendleft([time.strftime("%H:%M:%S"), nivel, texto])


def _cambio(clave, valor):
    """True si el valor cambió respecto al anterior (y no es la primera lectura)."""
    ant = _prev.get(clave, "__nuevo__")
    _prev[clave] = valor
    return ant != "__nuevo__" and ant != valor


# ---------------------------------------------------------------------------------------------- tomas
def _escribir_ctrl(d):
    """Archivo de control que lee registro_minimo (--tomas): existe = hay toma. Escritura atómica."""
    tmp = _ruta_tomas + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)
    os.replace(tmp, _ruta_tomas)


def _esperar(hasta):
    while time.time() < hasta:
        if _cancelar.is_set():
            return False
        time.sleep(0.05)
    return True


def _correr_toma(s):
    e = ESCENARIOS[s["esc"]]
    dist = s["dist"] if s["esc"] == "E4" and s["dist"] else e["dist"]
    tid = "%s-%s%s-R%d" % (s["esc"], s["montaje"], ("-" + str(s["dist"])) if s["esc"] == "E4" and s["dist"] else "", s["rep"])
    base = dict(toma_id=tid, escenario=s["esc"], repeticion=s["rep"], distancia_m=dist, altura_camara_m=s["altura"], montaje=s["montaje"], nota=s["nota"])
    ok = False
    try:
        with _lock_t:
            _tm.update(activa=True, id=tid, esc=s["esc"], texto="Prepárate: la toma empieza en %d s" % PREPARACION_S, pitidos=0, t0=0.0, dur=e["dur"], prep=time.time() + PREPARACION_S, fase=-1)
            _tm["n"] += 1
        if not _esperar(_tm["prep"]):
            return
        t0 = time.time()
        _escribir_ctrl(base)
        with _lock_t:
            _tm["t0"] = t0
        for k, (t, npit, txt) in enumerate(e["fases"]):
            if not _esperar(t0 + t):
                return
            with _lock_t:
                _tm.update(texto=txt, pitidos=npit, fase=k)
                _tm["n"] += 1
            if "conos" in e:
                _escribir_ctrl(dict(base, distancia_m=e["conos"][k]))
        if not _esperar(t0 + e["dur"]):
            return
        ok = True
        with _lock_t:
            _tm.update(texto="Fin de la toma. Gracias", pitidos=-1)
            _tm["n"] += 1
    finally:
        try:
            os.remove(_ruta_tomas)
        except OSError:
            pass
        with _lock_t:
            _tm["activa"] = False
            if not ok:
                _tm.update(texto="Toma cancelada", pitidos=0)
                _tm["n"] += 1
            _tomas_hist.appendleft([time.strftime("%H:%M:%S"), tid, "ok" if ok else "cancelada"])
            if ok:
                _sel["rep"] += 1
                _evento("ok", "Toma %s terminada" % tid)
            else:
                _evento("warn", "Toma %s cancelada" % tid)


def _api_toma(ruta, q):
    """Devuelve (código, mensaje)."""
    if _ruta_tomas is None:
        return 400, "las tomas no están activas (falta --tomas)"
    if ruta == "/toma/sel":
        try:
            esc = q.get("esc", [_sel["esc"]])[0]
            mon = q.get("montaje", [_sel["montaje"]])[0]
            assert esc in ESCENARIOS and mon in MONTAJES
            if esc in ("E5", "E6"):
                mon = mon if mon != "4A" else "4B-silla"       # E5 y E6 son siempre 4B
            else:
                mon = "4A"                                     # E0-E4: dron quieto, sin elegir
            _sel.update(esc=esc, montaje=mon, rep=max(1, int(q.get("rep", [_sel["rep"]])[0])),
                        altura=round(float(q.get("altura", [_sel["altura"]])[0]), 2),
                        dist=q.get("dist", [_sel["dist"]])[0][:6], nota=q.get("nota", [_sel["nota"]])[0][:40])
        except (ValueError, AssertionError):
            return 400, "parámetros no válidos"
        return 200, "ok"
    if ruta == "/toma/iniciar":
        if _tm["activa"]:
            return 409, "ya hay una toma en curso"
        if _sel["esc"] == "E4" and not _sel["dist"]:
            return 400, "En E4 elige primero la línea (5, 8 o 12 m)"
        threading.Thread(target=_correr_toma, args=(dict(_sel),), name="toma", daemon=True).start()
        return 200, "iniciada"
    if ruta == "/toma/cancelar":
        _cancelar.set()
        time.sleep(0.2)
        _cancelar.clear()
        return 200, "cancelada"
    return 404, "no existe"


def _estado_tomas():
    with _lock_t:
        tm = dict(_tm)
    ahora = time.time()
    resta = resta_fase = siguiente = None
    n_fases = 0
    if tm["activa"]:
        resta = max(0.0, tm["prep"] - ahora) if tm["t0"] == 0.0 else max(0.0, tm["t0"] + tm["dur"] - ahora)
        e = ESCENARIOS.get(tm["esc"])
        if e:
            n_fases = len(e["fases"])
            if tm["t0"]:
                k = tm["fase"]
                prox = e["fases"][k + 1] if 0 <= k + 1 < n_fases else None
                resta_fase = max(0.0, (tm["t0"] + (prox[0] if prox else e["dur"])) - ahora)
                siguiente = prox[2] if prox else "Fin de la toma"
    r = lambda x: None if x is None else round(x, 1)
    return dict(disponible=_ruta_tomas is not None, sel=dict(_sel), activa=tm["activa"], id=tm["id"], n=tm["n"], texto=tm["texto"],
                pitidos=tm["pitidos"], preparando=tm["activa"] and tm["t0"] == 0.0, resta=r(resta), resta_fase=r(resta_fase),
                fase=tm["fase"], n_fases=n_fases, siguiente=siguiente, historial=list(_tomas_hist)[:40],
                escenarios={k: dict(nombre=v["nombre"], dist=v["dist"], dur=v["dur"], campos=v["campos"], guia=v["guia"]) for k, v in ESCENARIOS.items()},
                montajes=list(MONTAJES))


# ---------------------------------------------------------------------------------------------- estado de sensores
def _temps():
    ahora = time.time()
    if ahora - _sist["t"] > 5.0:
        _sist["t"] = ahora
        for z in glob.glob("/sys/class/thermal/thermal_zone*"):
            try:
                nombre = open(z + "/type", "rb").read().decode().strip()
                t = int(open(z + "/temp", "rb").read()) / 1000.0
            except Exception:          # algunas zonas dan error al leerse (un TypeError raro de Python 3.10): se saltan
                continue
            if nombre.startswith("cpu"):
                _sist["cpu"] = round(t, 1)
            elif nombre.startswith("gpu"):
                _sist["gpu"] = round(t, 1)
    return dict(cpu=_sist["cpu"], gpu=_sist["gpu"])


def _estado(fila, cajas, dim=(640, 480)):
    cm, valido, edad_l = _v(fila.get("lidar_cm")), bool(fila.get("lidar_valido", 0)), _v(fila.get("edad_lidar_ms"))
    lidar_ok = cm is not None and edad_l is not None and edad_l < EDAD_MAX_MS
    edad_p = _v(fila.get("edad_pixhawk_ms"))
    pix_ok = edad_p is not None and edad_p < EDAD_MAX_MS
    W, H = dim
    _pc = GL.punto_para(cm / 100.0 if lidar_ok and valido else None)
    pl = dict(x=_pc[0], y=_pc[1]) if _pc else None
    cam_c, lid_c, des_c, hf_c, vf_c = GL.angulos_chasis()
    pers = []
    for x1, y1, x2, y2, tid, conf in sorted(cajas, key=lambda c: -(c[2] - c[0]) * (c[3] - c[1]))[:4]:
        cxn, an = (x1 + x2) / 2.0 / W, (y2 - y1) / H
        pers.append(dict(id=int(tid), conf=round(conf, 2), alto=round(an, 3), y1=round(y1 / H, 3), y2=round(y2 / H, 3), d_cam=round(_dist_cam(an), 2), trunc=bool(y1 < 3 or y2 > H - 3),
                         az=round(math.degrees(math.atan((cxn - 0.5) * 2 * math.tan(math.radians(GEO["hfov"] / 2)))), 1),
                         en_caja=bool(pl and x1 / W <= pl["x"] <= x2 / W and y1 / H <= pl["y"] <= y2 / H)))
    volt = _v(fila.get("volt"))
    con_bat = volt is not None and volt >= 5.0                  # con la Pixhawk solo por USB el voltaje marca ~0
    grande = max(cajas, key=lambda c: (c[2] - c[0]) * (c[3] - c[1])) if cajas else None

    obst = bool(lidar_ok and valido and cm < UMBRAL_FRENA_CM)
    if _cambio("obst", obst):
        _evento("bad" if obst else "ok", ("Obstáculo a %.2f m" % (cm / 100.0)) if obst else "Camino libre")
    if _cambio("persona", bool(cajas)):
        _evento("info", ("Persona detectada (ID %d, %d %%)" % (grande[4], round(grande[5] * 100))) if cajas else "Persona fuera de cuadro")
    if _cambio("lidar_ok", lidar_ok):
        _evento("ok" if lidar_ok else "bad", "LiDAR conectado" if lidar_ok else "LiDAR sin datos")
    if _cambio("pix_ok", pix_ok):
        _evento("ok" if pix_ok else "bad", "Pixhawk conectada" if pix_ok else "Pixhawk sin señal")
    if _cambio("modo", fila.get("modo")) and fila.get("modo"):
        _evento("info", "Modo de vuelo: %s" % fila["modo"])
    if _cambio("armado", bool(fila.get("armado"))):
        _evento("warn" if fila.get("armado") else "info", "ARMADO" if fila.get("armado") else "Desarmado")
    nivel_bat = 0 if not con_bat else 2 if volt < VOLT_CORTE else 1 if volt < VOLT_AVISO else 0
    if _cambio("bat", nivel_bat) and nivel_bat:
        _evento("bad" if nivel_bat == 2 else "warn", "Batería %.2f V: %s" % (volt, "DESCONECTAR" if nivel_bat == 2 else "baja, ir terminando"))

    if lidar_ok and valido:
        _hist.append(round(cm / 100.0, 2))
    return dict(
        t=time.time(),
        lidar=dict(m=round(cm / 100.0, 2) if lidar_ok and valido else None, ok=lidar_ok, valido=valido, fuerza=_v(fila.get("lidar_fuerza"))),
        hist=list(_hist),
        pix=dict(ok=pix_ok, modo=fila.get("modo"), armado=bool(fila.get("armado")), alt=_v(fila.get("alt_rel_m")), vel=_v(fila.get("vx")),
                 volt=volt if con_bat else None, pitch=_v(fila.get("cabeceo_deg")) if pix_ok else None, roll=_v(fila.get("alabeo_deg")) if pix_ok else None,
                 vel_suelo=_v(fila.get("vel_suelo")) if pix_ok else None, ascenso=_v(fila.get("ascenso")) if pix_ok else None, rumbo=_v(fila.get("hdg_deg")) if pix_ok else None,
                 gps=dict(fix=_v(fila.get("gps_fix")), sats=_v(fila.get("gps_sats")), hdop=_v(fila.get("gps_hdop")),
                          lat=_v(fila.get("lat")) if _v(fila.get("gps_fix")) and fila.get("gps_fix") >= 2 else None,
                          lon=_v(fila.get("lon")) if _v(fila.get("gps_fix")) and fila.get("gps_fix") >= 2 else None) if pix_ok else None),
        bat=dict(volt=round(volt, 2) if con_bat else None, celda=round(volt / CELDAS, 2) if con_bat else None,
                 pct=pct_lipo(volt) if con_bat else None, celdas=CELDAS, aviso=VOLT_AVISO, corte=VOLT_CORTE, llena=16.8),
        vision=dict(fps=_v(fila.get("fps")), yolo=_v(fila.get("lat_yolo_ms")), personas=len(cajas),
                    id=grande[4] if grande else None, conf=round(grande[5], 2) if grande else None,
                    pers=pers, lidar_en_caja=pers[0]["en_caja"] if pers else None),
        geo=dict(hfov=hf_c, vfov=vf_c, cam_pitch=cam_c, lidar_pitch=lid_c, lidar_desvio=des_c, lidar_px=[round(pl["x"], 4), round(pl["y"], 4)] if pl else None),
        expo=dict(_exp), sist=_temps(),
        toma=fila.get("toma_id") or None,
        eventos=list(_eventos),
    )


def publicar(frame, cajas, fila, hd=None):
    """Lo llama el bucle de YOLO: solo deja el cuadro anotado y los datos; el JPEG lo codifica otro hilo para no frenar a YOLO.
    frame = cuadro de análisis (cajas en sus píxeles); hd = el mismo instante en grande (opcional): sobre él se dibuja y de él salen los perfiles de /video."""
    global _img, _t_img, _n, _datos, _ncuadro, _tam_origen
    base = hd if hd is not None else frame
    k = base.shape[1] / float(frame.shape[1])
    cajas_b = [(x1 * k, y1 * k, x2 * k, y2 * k, i, c) for x1, y1, x2, y2, i, c in cajas]
    img = anotar(base, cajas_b, fila) if sum(_esp.values()) else None
    _ncuadro += 1
    if _ncuadro % 6 == 0:                                   # exposición: media de gris y % de píxeles quemados (>=250) y negros (<=10)
        gris = cv2.cvtColor(frame[::4, ::4], cv2.COLOR_BGR2GRAY)
        _exp.update(media=round(float(gris.mean()), 1), sat=round(float((gris >= 250).mean() * 100), 1), osc=round(float((gris <= 10).mean() * 100), 1))
    d = _estado(fila, cajas, (frame.shape[1], frame.shape[0]))
    with _cv:
        _img, _t_img, _datos, _n, _tam_origen = img, time.time(), d, _n + 1, (base.shape[1], base.shape[0])
        _cv.notify_all()


def _codificador():
    """Codifica solo el cuadro más nuevo y a lo sumo FPS_VIDEO veces por segundo (lo demás se salta, no se encola), una vez por cada perfil que alguien esté viendo."""
    visto, t_ult = 0, 0.0
    while True:
        with _cv:
            _cv.wait_for(lambda: _n != visto, timeout=1.0)
            img, t, visto = _img, _t_img, _n
        if img is None or time.time() - t_ult < 0.8 / FPS_VIDEO:
            continue
        t_ult = time.time()          # la hora se toma ANTES de codificar: medida al terminar, un cuadro grande (~10 ms) hacía saltar uno de cada dos (15 fps)
        for nombre, (w, h, q) in PERFILES.items():
            if not _esp[nombre]:
                continue
            im = img if img.shape[1] <= w else cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
            ok, buf = cv2.imencode(".jpg", im, [cv2.IMWRITE_JPEG_QUALITY, q])
            if ok:
                with _cv:
                    _jpegs[nombre], _njs[nombre] = (buf.tobytes(), t), _njs[nombre] + 1
                    _cv.notify_all()


# ---------------------------------------------------------------------------------------------- páginas
COMUN_JS = r"""
const $=i=>document.getElementById(i),f=(v,d=1,u='')=>v==null?'--':v.toFixed(d)+u;
let audioOn=false,ctx=null,ultN=null;
function activarAudio(){audioOn=true;try{ctx=ctx||new (window.AudioContext||window.webkitAudioContext)();ctx.resume();pitar(1)}catch(e){}hablar('Sonido activado')}
function pitar(n,largo){if(!audioOn||!ctx)return;let t=ctx.currentTime;for(let i=0;i<Math.max(n,1);i++){const o=ctx.createOscillator(),g=ctx.createGain();o.frequency.value=largo?600:1000;o.connect(g);g.connect(ctx.destination);g.gain.setValueAtTime(.3,t);const d=largo?.8:.18;o.start(t);o.stop(t+d);t+=d+.14}}
function hablar(x){if(!audioOn||!window.speechSynthesis)return;try{speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(x);u.lang='es-CO';u.rate=1.0;speechSynthesis.speak(u)}catch(e){}}
function anunciar(T){if(ultN===null){ultN=T.n;return}if(T.n===ultN)return;ultN=T.n;
 if(T.pitidos===-1){pitar(1,true)}else if(T.pitidos>0){pitar(T.pitidos)}hablar(T.texto);if(navigator.vibrate)navigator.vibrate(T.pitidos===-1?[600]:Array(Math.max(T.pitidos,1)).fill(200).flatMap(x=>[x,120]))}
async function api(u){try{await fetch(u,{cache:'no-store'})}catch(e){}}
function selUrl(){const g=i=>encodeURIComponent($(i).value);return '/toma/sel?esc='+g('t_esc')+'&rep='+g('t_rep')+'&altura='+g('t_alt')+'&montaje='+g('t_mon')+'&dist='+g('t_dist')+'&nota='+g('t_nota')}
"""

PAGINA = (r"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Panel de campo · Mínimo indispensable</title>
<style>
:root{--bg:#0b0f14;--card:#121922;--line:#1f2b38;--txt:#e6edf3;--mut:#8b9bb0;--ok:#2ecc71;--warn:#f5a524;--bad:#ff4d4f;--acc:#4da3ff}
*{box-sizing:border-box}html,body{margin:0;height:100%;background:var(--bg);color:var(--txt);font-family:system-ui,"Segoe UI",Roboto,sans-serif}
.app{display:grid;grid-template-columns:minmax(0,1fr) 400px;gap:12px;padding:12px;height:100vh}
.video{position:relative;background:#000;border:1px solid var(--line);border-radius:14px;overflow:hidden;min-height:0}
.video img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;background:#000}
.badge{position:absolute;top:12px;padding:6px 12px;border-radius:999px;background:rgba(10,14,20,.72);backdrop-filter:blur(6px);font-size:13px;font-weight:600;letter-spacing:.3px}
.b1{left:12px}.b2{right:12px;color:var(--mut)}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--bad);margin-right:7px;animation:p 1.4s infinite}.dot.ok{background:var(--ok)}
@keyframes p{50%{opacity:.35}}
.alerta{position:absolute;left:12px;right:12px;bottom:12px;padding:14px 18px;border-radius:12px;font-weight:800;font-size:clamp(18px,3.2vw,30px);text-align:center;background:rgba(255,77,79,.9);color:#fff;display:none;animation:p .9s infinite}
.alerta.on{display:block}.alerta.w{background:rgba(245,165,36,.92);color:#201400;animation:none}
.tomab{position:absolute;left:12px;right:12px;top:52px;padding:10px 16px;border-radius:12px;background:rgba(18,90,160,.9);font-weight:700;font-size:clamp(16px,2.4vw,24px);text-align:center;display:none}.tomab.on{display:block}
.col{display:flex;flex-direction:column;gap:10px;overflow-y:auto;min-height:0;padding-right:2px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:10px 14px}
.t{font-size:11px;letter-spacing:1.2px;color:var(--mut);text-transform:uppercase;margin-bottom:6px;display:flex;justify-content:space-between}
.big{font-size:clamp(34px,7vh,60px);font-weight:800;line-height:1.05;font-variant-numeric:tabular-nums}.big small{font-size:.38em;color:var(--mut);font-weight:600;margin-left:6px}
.big.txt{font-size:clamp(22px,4vh,32px)}
.ok{color:var(--ok)}.warn{color:var(--warn)}.bad{color:var(--bad)}.mut{color:var(--mut)}
.gauge{position:relative;height:14px;border-radius:8px;margin-top:12px;background:linear-gradient(90deg,#7a1f21 0 20%,#7a5a14 20% 53.3%,#14562f 53.3% 100%);overflow:visible}
.gauge i{position:absolute;top:-5px;width:4px;height:24px;border-radius:2px;background:#fff;transform:translateX(-2px);box-shadow:0 0 8px #000;transition:left .12s linear}
.ticks{display:flex;justify-content:space-between;font-size:11px;color:var(--mut);margin-top:5px}
svg{width:100%;height:clamp(28px,5vh,44px);margin-top:6px;display:block}
.row{display:grid;grid-template-columns:1fr 1fr;gap:6px 14px}.r4{grid-template-columns:repeat(4,1fr);gap:6px 8px}.k{font-size:10px;color:var(--mut);letter-spacing:.8px;text-transform:uppercase}.v{font-size:clamp(15px,2.6vh,21px);font-weight:700;font-variant-numeric:tabular-nums;white-space:nowrap}
.chip{display:inline-block;padding:3px 10px;border-radius:999px;font-size:13px;font-weight:700;background:#1c2733}.chip.rojo{background:#5a1a1c;color:#ffb3b4}.chip.az{background:#14335a;color:#a9d2ff}
.bat{height:12px;border-radius:7px;background:#1c2733;margin-top:8px;overflow:hidden}.bat b{display:block;height:100%;transition:width .3s,background .3s}
.enl{display:flex;gap:14px;flex-wrap:wrap;font-size:13px}.enl span{display:flex;align-items:center}
.ev{list-style:none;margin:0;padding:0;font-size:12px;max-height:clamp(60px,15vh,130px);overflow:auto}.ev li{padding:3px 0;border-bottom:1px solid var(--line);display:flex;gap:10px}.ev time{color:var(--mut);font-variant-numeric:tabular-nums}
label{font-size:10px;color:var(--mut);letter-spacing:.8px;text-transform:uppercase;display:block}
select,input{width:100%;background:#0e151d;color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:6px 8px;font-size:14px}
.bt{border:0;border-radius:10px;padding:10px;font-weight:800;font-size:15px;cursor:pointer;width:100%}.go{background:#1f9d57;color:#fff}.no{background:#7a1f21;color:#fff}.sd{background:#243447;color:var(--txt)}
@media(max-width:900px){.app{grid-template-columns:1fr;height:auto}.video{aspect-ratio:4/3}.col{overflow:visible}}
</style></head><body><div class="app">
<div class="video"><img id="img" src="/video" alt="cámara" onerror="setTimeout(()=>{this.src='/video?'+Date.now()},800)"><div class="badge b1"><span class="dot" id="live"></span><span id="liveT">CONECTANDO</span></div><div class="badge b2" id="reloj"></div><div class="tomab" id="tomab"></div><div class="alerta" id="alerta"></div></div>
<div class="col">
<div class="card"><div class="t"><span>LiDAR TF03 · frente</span><span id="lfz"></span></div><div class="big" id="lm">--<small>m</small></div>
<div class="gauge"><i id="lmk" style="left:0"></i></div><div class="ticks"><span>0</span><span>3 m · frena</span><span>8 m · árbitro</span><span>15 m</span></div><svg id="spark" viewBox="0 0 300 54" preserveAspectRatio="none"></svg></div>
<div class="card"><div class="t"><span>Batería LiPo 4S</span><span id="bcel"></span></div><div style="display:flex;align-items:baseline;gap:16px"><div class="big" id="bv">--<small>V</small></div><div class="big" id="bp" style="font-size:clamp(26px,5vh,42px)">--</div></div>
<div class="bat" style="position:relative"><b id="batb" style="width:0"></b></div><div class="ticks"><span>14.0 V corte</span><span id="bes"></span><span>16.8 V llena</span></div></div>
<div class="card"><div class="t"><span>Pixhawk</span><span id="pmodo"></span></div><div class="row r4" style="grid-template-columns:repeat(3,1fr)"><div><div class="k">Estado</div><div class="v" id="parm">--</div></div>
<div><div class="k">Altura</div><div class="v" id="palt">--</div></div><div><div class="k">Velocidad</div><div class="v" id="pvel">--</div></div></div></div>
<div class="card"><div class="t"><span>Percepción · YOLO26n</span><span id="toma"></span></div><div class="row r4"><div><div class="k">Personas</div><div class="v" id="vper">0</div></div><div><div class="k">Objetivo</div><div class="v" id="vid">--</div></div>
<div><div class="k">FPS</div><div class="v" id="vfps">--</div></div><div><div class="k">YOLO</div><div class="v" id="vyolo">--</div></div></div></div>
<div class="card" id="ctomas" style="display:none"><div class="t"><span>Tomas de campo (paso 4)</span><span id="tinfo"></span></div>
<label>Escenario</label><select id="t_esc" onchange="api(selUrl())"></select>
<ol class="k" id="t_guia" style="margin:8px 0 6px 18px;padding:0;line-height:1.45;text-transform:none;letter-spacing:0;font-size:13.5px;color:#cfd8dc"></ol><div id="t_fase" style="font-weight:700;min-height:20px"></div>
<div class="row" style="margin-top:6px"><div id="f_rep"><label>Repetición</label><input id="t_rep" type="number" min="1" onchange="api(selUrl())"></div><div id="f_alt"><label>Altura cámara (m)</label><input id="t_alt" type="number" step="0.05" onchange="api(selUrl())"></div>
<div id="f_mon"><label>Montaje</label><select id="t_mon" onchange="api(selUrl())"></select></div><div id="f_dist"><label>Línea E4 (m)</label><select id="t_dist" onchange="api(selUrl())"><option value="">--</option><option>5</option><option>8</option><option>12</option></select></div></div>
<div id="f_nota"><label style="margin-top:6px">Nota (p. ej. camina / trota)</label><input id="t_nota" onchange="api(selUrl())"></div>
<div class="row" style="margin-top:8px"><button class="bt go" id="t_go" onclick="iniciarToma()">▶ INICIAR TOMA</button><button class="bt no" onclick="api('/toma/cancelar')">■ CANCELAR</button></div>
<div id="t_msg" class="k" style="color:var(--bad);min-height:18px;margin-top:4px"></div>
<button class="bt sd" style="margin-top:6px" id="bsnd" onclick="activarAudio();this.textContent='🔊 sonido y voz activados'">🔊 Activar sonido y voz en este equipo</button>
<div class="k" style="margin-top:8px">Para quien camina: abrir <b id="urlp"></b> en el celular · <a href="/alinear" style="color:var(--acc)">alinear LiDAR con la cámara</a> · <a href="/calibrar" style="color:var(--acc)">medir ángulos</a></div><ul class="ev" id="thist"></ul></div>
<div class="card"><div class="t"><span>Enlaces e inclinación</span><span id="gp"></span></div><div class="enl" id="enl"></div></div>
<div class="card"><div class="t"><span>Eventos</span></div><ul class="ev" id="ev"></ul></div>
</div></div>
<script>""" + COMUN_JS + r"""
let tomasListas=false;
async function iniciarToma(){try{await api(selUrl());const r=await fetch('/toma/iniciar',{cache:'no-store'});const d=await r.json();$('t_msg').textContent=r.ok?'':(d.mensaje||'no se pudo iniciar')}catch(e){$('t_msg').textContent='sin conexión con el dron'}}
function enlace(n,ok){return '<span><span class="dot '+(ok?'ok':'')+'"></span>'+n+'</span>'}
function pintarTomas(T){
 if(!T||!T.disponible)return;$('ctomas').style.display='';
 if(!tomasListas){tomasListas=true;$('t_esc').innerHTML=Object.entries(T.escenarios).map(([k,v])=>'<option value="'+k+'">'+k+' · '+v.nombre+'</option>').join('');$('t_mon').innerHTML=T.montajes.map(m=>'<option>'+m+'</option>').join('');$('urlp').textContent=location.origin+'/persona'}
 const e=T.escenarios[T.sel.esc]||{campos:[],guia:[]},mostrar=k=>e.campos.indexOf(k)>=0;
 [['f_rep','rep'],['f_alt','altura'],['f_mon','montaje'],['f_dist','dist'],['f_nota','nota']].forEach(p=>{$(p[0]).style.display=mostrar(p[1])?'':'none'});
 ['t_esc','t_rep','t_alt','t_mon','t_dist','t_nota','t_go'].forEach(id=>{$(id).disabled=!!T.activa});
 $('t_guia').innerHTML=(e.guia||[]).map(x=>'<li>'+x+'</li>').join('');
 $('t_fase').textContent=(T.activa&&!T.preparando)?('Paso '+(T.fase+1)+' de '+T.n_fases+(T.siguiente?'  ·  después: '+T.siguiente:'')):'';
 const a=document.activeElement.id||'';if(!a.startsWith('t_')){$('t_esc').value=T.sel.esc;$('t_rep').value=T.sel.rep;$('t_alt').value=T.sel.altura;$('t_mon').value=T.sel.montaje;$('t_dist').value=T.sel.dist;$('t_nota').value=T.sel.nota}
 const b=$('tomab');if(T.activa){b.className='tomab on';b.textContent=(T.preparando?'PREPÁRATE · ':T.id+' · ')+T.texto+(T.resta!=null?' · '+T.resta.toFixed(0)+' s':'')}else if(T.texto&&T.n){b.className='tomab on';b.textContent=T.texto;setTimeout(()=>{if(!T.activa)b.className='tomab'},3000)}else b.className='tomab';
 $('tinfo').textContent=T.activa?'EN CURSO':'lista';$('thist').innerHTML=T.historial.map(h=>'<li><time>'+h[0]+'</time><span class="'+(h[2]=='ok'?'ok':'warn')+'">'+h[1]+' · '+h[2]+'</span></li>').join('');
 anunciar(T);
}
function pintar(d){
 const l=d.lidar,p=d.pix,v=d.vision,m=l.m;
 const cls=m==null?'warn':m<3?'bad':m<8?'warn':'ok';
 $('lm').className='big '+cls+(m==null?' txt':'');$('lm').innerHTML=(m==null?(l.ok?'sin retorno':'SIN DATOS'):m.toFixed(2))+(m==null?'':'<small>m</small>');
 $('lmk').style.left=(m==null?0:Math.min(m,15)/15*100)+'%';$('lfz').textContent=l.fuerza!=null?'fuerza '+l.fuerza:'';
 const h=d.hist;$('spark').innerHTML=h.length>1?'<polyline fill="none" stroke="#4da3ff" stroke-width="2" vector-effect="non-scaling-stroke" points="'+h.map((y,i)=>(i/(h.length-1)*300).toFixed(1)+','+(52-Math.min(y,15)/15*50).toFixed(1)).join(' ')+'"/><line x1="0" x2="300" y1="'+(52-3/15*50)+'" y2="'+(52-3/15*50)+'" stroke="#ff4d4f" stroke-dasharray="4 4" stroke-width="1" vector-effect="non-scaling-stroke"/>':'';
 $('pmodo').innerHTML='<span class="chip az">'+(p.modo||'--')+'</span>';
 $('parm').innerHTML=p.ok?'<span class="chip '+(p.armado?'rojo':'')+'">'+(p.armado?'ARMADO':'desarmado')+'</span>':'<span class="chip rojo">SIN SEÑAL</span>';
 const vb=p.volt,bc=vb==null?'':vb<14?'bad':vb<14.4?'warn':'ok';
 const B=d.bat||{},pp=B.pct;
 $('bv').className='big '+bc;$('bv').innerHTML=vb==null?'<span style="font-size:.5em;color:var(--warn)">sin lectura</span>':vb.toFixed(2)+'<small>V</small>';
 $('bp').className='big '+bc;$('bp').textContent=pp==null?'':pp+' %';
 $('bcel').textContent=B.celda!=null?B.celda.toFixed(2)+' V por celda':'';
 const pc=vb==null?0:Math.max(0,Math.min(100,(vb-14)/(16.8-14)*100));$('batb').style.width=pc+'%';$('batb').style.background=vb==null?'#333':vb<14?'#ff4d4f':vb<14.4?'#f5a524':'#2ecc71';
 $('bes').textContent=vb==null?'':vb<14?'DESCONECTAR YA':vb<14.4?'baja: ir terminando':'carga útil · % aprox.';
 batTxt=vb==null?'':'   🔋 '+vb.toFixed(1)+' V · '+pp+' %';
 $('palt').textContent=f(p.alt,1,' m');$('pvel').textContent=f(p.vel,1,' m/s');
 $('vper').textContent=v.personas;$('vper').className='v '+(v.personas?'ok':'');$('vid').textContent=v.id!=null?'ID '+v.id+' · '+Math.round(v.conf*100)+'%':'--';$('vid').style.fontSize=v.id!=null?'clamp(13px,2.2vh,18px)':'';
 $('vfps').textContent=f(v.fps,0);$('vyolo').textContent=f(v.yolo,0,' ms');$('toma').textContent=d.toma?'TOMA '+d.toma:'';
 $('gp').textContent=p.pitch!=null?'cabeceo '+f(p.pitch,1,'°')+' · alabeo '+f(p.roll,1,'°'):'';
 $('enl').innerHTML=enlace('Cámara',v.fps!=null&&v.fps>1)+enlace('LiDAR',l.ok)+enlace('Pixhawk',p.ok);
 $('ev').innerHTML=d.eventos.map(e=>'<li><time>'+e[0]+'</time><span class="'+({bad:'bad',warn:'warn',ok:'ok',info:''}[e[1]])+'">'+e[2]+'</span></li>').join('')||'<li class="mut">sin eventos</li>';
 const A=$('alerta');let msg='',w=false;
 if(!l.ok)msg='SIN DATOS DEL LiDAR';else if(m!=null&&m<3)msg='OBSTÁCULO A '+m.toFixed(2)+' m · FRENAR';
 else if(vb!=null&&vb<14){msg='BATERÍA '+vb.toFixed(2)+' V · DESCONECTAR'}else if(vb!=null&&vb<14.4){msg='BATERÍA BAJA · '+vb.toFixed(2)+' V';w=true}
 A.textContent=msg;A.className='alerta'+(msg?' on':'')+(w?' w':'');
 pintarTomas(d.tomas);
}
async function tick(){try{const r=await fetch('/datos',{cache:'no-store'});const d=await r.json();pintar(d);$('live').className='dot ok';$('liveT').textContent='EN VIVO'+(d.vision.fps!=null?' · '+d.vision.fps.toFixed(0)+' FPS':'')}catch(e){$('live').className='dot';$('liveT').textContent='SIN CONEXIÓN'}setTimeout(tick,120)}
let batTxt='';setInterval(()=>$('reloj').textContent=new Date().toLocaleTimeString('es-CO')+batTxt,1000);tick();
</script></body></html>""").encode("utf-8")

PERSONA = (r"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>Pantalla de la persona</title><style>
*{box-sizing:border-box}html,body{margin:0;height:100%;background:#0b0f14;color:#fff;font-family:system-ui,Roboto,sans-serif}
.w{display:flex;flex-direction:column;height:100%;padding:12px;gap:10px}
#cab{font-size:15px;color:#8b9bb0;text-align:center}
#caja{flex:1;border-radius:22px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:16px;background:#1c2733;transition:background .25s;overflow:auto}
#paso{font-size:15px;color:#cfe3ff;margin-bottom:6px}
#txt{font-size:clamp(26px,8vw,56px);font-weight:900;line-height:1.1}
#cnt{font-size:clamp(70px,28vw,180px);font-weight:900;font-variant-numeric:tabular-nums;line-height:1}
#sub{font-size:15px;color:#cfd8dc;margin-top:4px}
#sig{font-size:clamp(16px,4.5vw,24px);color:#ffe9a8;margin-top:10px}
#guia{font-size:clamp(16px,4.4vw,22px);text-align:left;line-height:1.35;max-width:640px;margin:10px 0 0;padding-left:22px}#guia li{margin:8px 0}
#bar{height:8px;border-radius:4px;background:#243447;margin-top:12px;width:100%;max-width:640px;overflow:hidden}#bar b{display:block;height:100%;width:0;background:#4da3ff}
.bt{border:0;border-radius:18px;padding:20px;font-weight:900;font-size:22px;width:100%;color:#fff}.go{background:#1f9d57}.no{background:#a12327}.sd{background:#243447;font-size:17px}.bt:disabled{opacity:.45}
.f{display:grid;grid-template-columns:1fr 1fr;gap:10px}#estado{font-size:12px;color:#ffb74d;text-align:center;min-height:16px}
</style></head><body><div class="w"><div id="cab">conectando…</div>
<div id="caja"><div id="paso"></div><div id="txt">Toca “Activar sonido” y espera</div><div id="cnt"></div><div id="sub"></div><div id="sig"></div><ol id="guia"></ol><div id="bar"><b id="barb"></b></div></div>
<button class="bt sd" id="bs" onclick="activarAudio();this.textContent='🔊 sonido y voz activados'">🔊 Activar sonido y voz</button>
<div class="f"><button class="bt go" id="bgo" onclick="iniciar()">▶ INICIAR</button><button class="bt no" onclick="api('/toma/cancelar')">■ CANCELAR</button></div><div id="estado"></div></div>
<script>""" + COMUN_JS + r"""
let T=null,ref=null,fallos=0,lock=null;
async function pantallaEncendida(){try{if('wakeLock' in navigator&&document.visibilityState==='visible')lock=await navigator.wakeLock.request('screen')}catch(e){}}
document.addEventListener('visibilitychange',pantallaEncendida);pantallaEncendida();
function iniciar(){$('bgo').disabled=true;$('txt').textContent='Enviando…';fetch('/toma/iniciar',{cache:'no-store'}).then(r=>r.json()).then(d=>{if(d.mensaje&&d.mensaje!=='iniciada')$('estado').textContent=d.mensaje}).catch(()=>{});setTimeout(()=>{$('bgo').disabled=false},1500)}
function recibir(t){T=t;ref={resta:t.resta,rf:t.resta_fase,t:performance.now()};anunciar(t);dibujar()}
function dibujar(){
 if(!T||!T.disponible){if(T)$('cab').textContent='las tomas no están activas';return}
 const e=T.escenarios[T.sel.esc],dt=ref?(performance.now()-ref.t)/1000:0,c=$('caja');
 $('cab').textContent=T.sel.esc+' · '+e.nombre+' · repetición '+T.sel.rep;$('bgo').disabled=!!T.activa;
 if(T.activa){
  const resta=ref&&ref.resta!=null?Math.max(0,ref.resta-dt):null,rf=ref&&ref.rf!=null?Math.max(0,ref.rf-dt):null;
  c.style.background=T.preparando?'#8a6d00':'#125aa0';
  $('paso').textContent=T.preparando?'PREPÁRATE':'Paso '+(T.fase+1)+' de '+T.n_fases;
  $('txt').textContent=T.texto;$('cnt').textContent=T.preparando?(resta!=null?Math.ceil(resta):''):(rf!=null?Math.ceil(rf):'');
  $('sub').textContent=T.preparando?'la toma empieza en segundos':(resta!=null?'quedan '+Math.ceil(resta)+' s en total':'');
  $('sig').textContent=(!T.preparando&&T.siguiente)?'Después: '+T.siguiente:'';$('guia').innerHTML='';
  $('barb').style.width=(resta!=null&&!T.preparando?Math.min(100,Math.max(0,100*(1-resta/e.dur))):0)+'%'}
 else{c.style.background=T.pitidos===-1?'#14562f':'#1c2733';$('paso').textContent='';$('cnt').textContent='';$('sub').textContent='';$('sig').textContent='';$('barb').style.width='0';
  $('txt').textContent=T.pitidos===-1?T.texto:'Lista para empezar';$('guia').innerHTML=(e.guia||[]).map(x=>'<li>'+x+'</li>').join('')}
}
setInterval(dibujar,100);
async function tick(){try{const ac=new AbortController(),to=setTimeout(()=>ac.abort(),2500);const r=await fetch('/toma/estado',{cache:'no-store',signal:ac.signal});clearTimeout(to);recibir(await r.json());fallos=0;if($('estado').textContent.indexOf('sin conexión')===0)$('estado').textContent=''}catch(e){fallos++;if(fallos>=3)$('estado').textContent='sin conexión con el dron… reintentando'}setTimeout(tick,fallos>=3?1000:250)}tick();
</script></body></html>""").encode("utf-8")


ALINEAR = (r"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Alinear LiDAR con la cámara</title><style>
:root{--bg:#0b0f14;--card:#121922;--line:#1f2b38;--txt:#e6edf3;--mut:#8b9bb0;--ok:#2ecc71;--bad:#ff4d4f;--acc:#4da3ff;--cian:#00e5ff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--txt);font-family:system-ui,"Segoe UI",Roboto,sans-serif;padding:12px}
a{color:var(--acc)}h1{font-size:20px;margin:0 0 8px}.fila{display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:12px}
@media(max-width:900px){.fila{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px;margin-bottom:12px}
#marco{position:relative;display:inline-block;max-width:100%;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#000;line-height:0}
#img{max-width:100%;height:auto;cursor:crosshair;display:block;-webkit-user-select:none;user-select:none}
.m{font-size:56px;font-weight:800;line-height:1.05}.lej{color:var(--mut)}.cer{color:var(--ok)}
button{background:#1c2733;color:var(--txt);border:1px solid var(--line);border-radius:10px;padding:10px 14px;font-size:15px;font-weight:600;cursor:pointer;margin:3px 4px 3px 0}
button.pri{background:var(--acc);color:#04121f;border:0}button.mal{background:#3a1c1e}
ol{padding-left:20px;margin:6px 0}li{margin:5px 0;font-size:14px}.k{color:var(--mut);font-size:13px}#msg{min-height:20px;margin-top:6px;font-size:14px}
</style></head><body>
<h1>Alinear el LiDAR con la cámara <span class="k">· <a href="/" onclick="if(window.parent!==window){window.parent.postMessage('cerrar-jetson','*');return false}">volver</a></span></h1>
<div class="fila"><div><div id="marco"><img id="img" src="/video" alt="cámara" onerror="setTimeout(()=>{this.src='/video?'+Date.now()},800)"></div>
<div class="k" style="margin-top:6px">Haz clic en la imagen donde ves el centro del objeto que el LiDAR está midiendo. Cruz amarilla = clic válido, roja = el LiDAR no leía nada cercano, círculo celeste = punto guardado.</div></div>
<div><div class="card"><div class="k">LiDAR TF03 · frente</div><div class="m lej" id="lid">--</div><div class="k" id="lidk"></div></div>
<div class="card"><b>Cómo hacerlo</b><ol>
<li>Pon un cartón grande (o una persona) de frente al dron, a <b>3 a 5 m</b>.</li>
<li>Muévelo de lado hasta que el número de arriba pase de lejos (~58 m, la pared del fondo) a la distancia del cartón: <b>se pone verde</b>.</li>
<li>Haz <b>clic en el centro del cartón</b> en la imagen. Repite 3 o 4 veces moviéndolo un poco.</li>
<li>Pulsa <b>Guardar punto</b>: queda la mediana de los clics válidos. Desde ahí cada cuadro del registro dice si el rayo cae dentro de la caja de la persona.</li></ol>
<div class="k">Por la separación entre LiDAR y cámara, el punto cambia un poco con la distancia: hazlo a la distancia donde más importa (3 a 5 m).</div></div>
<div class="card"><div id="pto" class="k">Sin punto guardado</div><div id="clics" class="k" style="margin-top:6px"></div><div id="msg"></div>
<button class="pri" onclick="ir('guardar')">Guardar punto</button><button onclick="ir('quitar')">Quitar último clic</button><button onclick="ir('limpiar')">Limpiar clics</button><button class="mal" onclick="if(confirm('¿Borrar el punto guardado?'))ir('borrar')">Borrar punto guardado</button></div></div></div>
<script>
const $=i=>document.getElementById(i);
async function ir(a,q){try{const r=await fetch('/alinear/'+a+(q||''),{cache:'no-store'});const d=await r.json();$('msg').textContent=r.ok?'':(d.mensaje||'error');$('msg').style.color='var(--bad)';pintar(d)}catch(e){$('msg').textContent='sin conexión con el dron'}}
$('img').addEventListener('click',e=>{const r=$('img').getBoundingClientRect();ir('clic','?x='+((e.clientX-r.left)/r.width).toFixed(4)+'&y='+((e.clientY-r.top)/r.height).toFixed(4))});
function pintar(d){if(!d||d.punto===undefined)return;const m=d.lidar_m;
 $('lid').textContent=m==null?'--':m.toFixed(2)+' m';$('lid').className='m '+(m!=null&&m<d.max_m?'cer':'lej');
 $('lidk').textContent=m==null?'sin lectura válida':(m<d.max_m?'el rayo está pegando en algo cercano: puedes hacer clic':'lejos: el rayo no pega en el objeto, muévelo');
 const p=d.punto;$('pto').textContent=p?('Punto guardado: x '+(p.x*100).toFixed(1)+' % · y '+(p.y*100).toFixed(1)+' %  (en 640×480: '+Math.round(p.x*640)+', '+Math.round(p.y*480)+')  · '+p.n+' clics · objeto a '+(p.dist_m==null?'?':p.dist_m)+' m'):'Sin punto guardado';
 $('clics').textContent=d.clics.length?('Clics de prueba: '+d.clics.map(c=>(c.ok?'✓':'✗')+(c.m==null?'':' '+c.m.toFixed(1)+' m')).join(' · ')):'Sin clics de prueba'}
async function tick(){try{pintar(await (await fetch('/alinear/estado',{cache:'no-store'})).json())}catch(e){}setTimeout(tick,300)}tick();
</script></body></html>""").encode("utf-8")


RUTA_CALIBRACION = os.path.expanduser("~/calibracion_angulos.json")


def _pagina_calibrar():
    """calibrar.html vive junto a este archivo; se lee en cada petición para poder editarla sin reiniciar."""
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "calibrar.html"), "rb") as f:
        return f.read()


def _api_calibrar(ruta, q):
    """/calibrar/guardar?j=<json>  guarda la calibración de ángulos;  /calibrar/estado  devuelve lo guardado."""
    acc = ruta.rsplit("/", 1)[-1]
    if acc == "guardar":
        try:
            d = json.loads(q["j"][0])
            if not isinstance(d, dict) or len(q["j"][0]) > 20000:
                raise ValueError
        except (KeyError, IndexError, ValueError):
            return 400, dict(mensaje="datos inválidos")
        tmp = RUTA_CALIBRACION + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        os.replace(tmp, RUTA_CALIBRACION)
        return 200, dict(mensaje="guardado")
    if acc == "estado":
        try:
            with open(RUTA_CALIBRACION, encoding="utf-8") as f:
                return 200, json.load(f)
        except (OSError, ValueError):
            return 200, {}
    return 404, dict(mensaje="acción desconocida")


class _Manejador(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _enviar(self, tipo, cuerpo, codigo=200):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/":
            self._enviar("text/html; charset=utf-8", PAGINA)
        elif u.path == "/persona":
            self._enviar("text/html; charset=utf-8", PERSONA)
        elif u.path == "/calibrar":
            self._enviar("text/html; charset=utf-8", _pagina_calibrar())
        elif u.path.startswith("/calibrar/"):
            codigo, d = _api_calibrar(u.path, parse_qs(u.query))
            self._enviar("application/json", json.dumps(d).encode(), codigo)
        elif u.path == "/alinear":
            self._enviar("text/html; charset=utf-8", ALINEAR)
        elif u.path.startswith("/alinear/"):
            codigo, d = _api_alinear(u.path, parse_qs(u.query))
            self._enviar("application/json", json.dumps(d).encode(), codigo)
        elif u.path == "/datos":
            with _cv:
                d = dict(_datos) or {"lidar": {}, "pix": {}, "vision": {}, "hist": [], "eventos": []}
                origen = _tam_origen
            ahora = time.time()
            d["video"] = dict(kbps=round(sum(b for t, b in list(_bytes_tx) if ahora - t < 3.0) * 8 / 3.0 / 1000.0), origen=list(origen),
                              perfiles={k: v for k, v in _esp.items() if v}, opciones={k: list(v[:2]) for k, v in PERFILES.items()})
            d["tomas"] = _estado_tomas()
            self._enviar("application/json", json.dumps(d).encode())
        elif u.path == "/toma/estado":
            self._enviar("application/json", json.dumps(_estado_tomas()).encode())
        elif u.path.startswith("/toma/"):
            codigo, msg = _api_toma(u.path, parse_qs(u.query))
            self._enviar("application/json", json.dumps({"mensaje": msg}).encode(), codigo)
        elif u.path == "/video":
            perfil = parse_qs(u.query).get("res", ["normal"])[0]
            perfil = perfil if perfil in PERFILES else "normal"
            self.send_response(200)
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            # buffer de envío chico: si el WiFi no da abasto, write() se bloquea y el siguiente cuadro es el más nuevo (antes se acumulaban segundos de video)
            self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, {"normal": 65536, "alta": 262144, "maxima": 393216}[perfil])   # con un buffer chico el rendimiento queda en buffer/RTT: los cuadros grandes lo necesitan mayor
            self.connection.settimeout(3.0)
            with _cv:
                _esp[perfil] += 1
            visto = 0
            try:
                while True:
                    with _cv:
                        _cv.wait_for(lambda: _njs[perfil] != visto, timeout=2.0)
                        j, t = _jpegs[perfil]
                        visto = _njs[perfil]
                    if j:
                        paquete = b"--frame\r\nContent-Type: image/jpeg\r\nX-T: %.3f\r\nContent-Length: %d\r\n\r\n" % (t, len(j)) + j + b"\r\n"
                        self.wfile.write(paquete)
                        _bytes_tx.append((time.time(), len(paquete)))
            except OSError:           # navegador cerrado, o sin avance por 3 s: se suelta y la página vuelve a pedir el video
                pass
            finally:
                with _cv:
                    _esp[perfil] -= 1
        else:
            self.send_error(404)


class _Servidor(ThreadingHTTPServer):
    """Escucha en IPv4 e IPv6: talos-jetson.local a veces resuelve a IPv6 y solo-IPv4 no responde."""
    address_family = socket.AF_INET6

    def server_bind(self):
        self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        super().server_bind()


def iniciar_servidor(puerto, ruta_tomas=None):
    """ruta_tomas = el mismo archivo que registro_minimo.py recibe en --tomas (si es None, el panel no ofrece tomas)."""
    global _ruta_tomas
    _ruta_tomas = os.path.expanduser(ruta_tomas) if ruta_tomas else None
    srv = _Servidor(("::", puerto), _Manejador)
    srv.daemon_threads = True
    threading.Thread(target=_codificador, name="jpeg", daemon=True).start()
    _cargar_alineacion()
    threading.Thread(target=srv.serve_forever, name="panel", daemon=True).start()
    print("[PANEL] operador: http://<nombre-de-la-Jetson>:%d   persona (celular): /persona   tomas: %s"
          % (puerto, "ACTIVAS" if _ruta_tomas else "no (falta --tomas)"), flush=True)


def _demo(puerto):
    """Datos inventados para ver la interfaz sin hardware."""
    iniciar_servidor(puerto, os.path.join(tempfile.gettempdir(), "toma_demo.json"))
    t0 = time.time()
    while True:
        t = time.time() - t0
        img = np.full((480, 640, 3), 90, np.uint8)
        cv2.rectangle(img, (0, 300), (640, 480), (70, 90, 70), -1)
        x = int(320 + 200 * math.sin(t / 3))
        cv2.rectangle(img, (x - 40, 140), (x + 40, 400), (120, 130, 160), -1)
        cv2.putText(img, "DEMO SIN HARDWARE", (170, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        persona = (t % 14) < 10
        cajas = [(x - 40, 140, x + 40, 400, 3, 0.91)] if persona else []
        cm = 700 + 650 * math.sin(t / 2.5) if (t % 30) < 24 else ""
        fila = dict(fps=15, lat_yolo_ms=19.5, lidar_cm=cm, lidar_valido=1, edad_lidar_ms=5 if cm != "" else 5000, lidar_fuerza=420,
                    modo="LOITER" if t > 8 else "STABILIZE", armado=1 if t > 12 else 0, alt_rel_m=2.3 if t > 12 else 0.1, vx=1.2 if t > 12 else 0.0,
                    volt=16.8 - (t % 120) * 0.03, edad_pixhawk_ms=100, cabeceo_deg=round(2.5 * math.sin(t / 3), 2), alabeo_deg=round(1.5 * math.cos(t / 4), 2),
                    toma_id=_tm["id"] if _tm["activa"] and _tm["t0"] else "")
        if _alin["punto"] is None:
            _alin["punto"] = dict(x=0.495, y=0.595, n=1, t=0, dist_m=2.0)
        publicar(img, cajas, fila, cv2.resize(img, (1280, 960)))
        time.sleep(1 / 15)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", type=int, metavar="PUERTO", help="servidor con datos inventados")
    a = ap.parse_args()
    if a.demo:
        _demo(a.demo)
