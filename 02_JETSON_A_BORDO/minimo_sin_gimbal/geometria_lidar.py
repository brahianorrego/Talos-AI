# -*- coding: utf-8 -*-
"""
Dónde cae el rayo del LiDAR dentro de la imagen según su distancia.

El LiDAR y la cámara no están en el mismo sitio (la cámara va unos centímetros arriba y atrás), así que el punto donde el rayo "pega" en la imagen cambia con la distancia:
a 2 m queda más abajo que a 15 m. /alinear (o el paso 3 de /calibrar) guarda el punto a UNA distancia (d0) en ~/alineacion_lidar.json; aquí se le suma lo que cambia
al pasar de d0 a la distancia actual d, con la geometría del montaje:

    tan(eps) = (d·tan(inc) − (hc − hl)) / (d + off)        eps = ángulo, visto desde la cámara, del punto donde pega el rayo (respecto al chasis)
    fy = 0.5 − tan(eps − pitch_cam) / (2·tan(VFOV/2))      fx = 0.5 + tan(desvío)·d/(d + off) / (2·tan(HFOV/2))

inc / pitch_cam / desvío son los ángulos del montaje RESPECTO AL CHASIS (config.py o ~/calibracion_angulos.json si trae 'lidarIncChasis' y 'pitchCamChasis').
Si no hay punto guardado o falta algo, devuelve None. Lo usan registro_minimo.py (lidar_en_caja) y panel_campo.py (cruz sobre el video).
"""
import json
import math
import os
import time

RUTA_ALINEACION = os.path.expanduser("~/alineacion_lidar.json")
RUTA_CALIBRACION = os.path.expanduser("~/calibracion_angulos.json")
DH_CM_POR_OMISION = 4.5      # cámara sobre el eje del LiDAR (medido el 20-oct: 32.0 y 27.5 cm sobre el escritorio)
OFF_CM_POR_OMISION = 6.0     # cámara detrás del frente del LiDAR (medido el 20-oct)

_cache = {"t": 0.0, "alin": None, "cal": {}}
try:
    import config as _C
except Exception:
    _C = None


def _leer():
    if time.time() - _cache["t"] < 2.0:
        return
    _cache["t"] = time.time()
    try:
        with open(RUTA_ALINEACION, encoding="utf-8") as f:
            j = json.load(f)
        _cache["alin"] = (float(j["x"]), float(j["y"]), float(j.get("dist_m") or 0.0))
    except (OSError, ValueError, KeyError, TypeError):
        _cache["alin"] = None
    try:
        with open(RUTA_CALIBRACION, encoding="utf-8") as f:
            _cache["cal"] = json.load(f)
    except (OSError, ValueError):
        _cache["cal"] = {}


def angulos_chasis():
    """(cam_pitch, lidar_pitch, lidar_desvio, hfov, vfov) en grados, respecto al chasis. El archivo de calibración manda si trae los valores 'Chasis'."""
    _leer()
    c = _cache["cal"]
    g = lambda k, d: getattr(_C, k, d)
    cam = c.get("pitchCamChasis", g("CAMARA_PITCH_DEG", -2.4))
    lid = c.get("lidarIncChasis", g("LIDAR_PITCH_DEG", -6.7))
    des = c.get("lidarDesv", g("LIDAR_DESVIO_YAW_DEG", -0.6)) if c else g("LIDAR_DESVIO_YAW_DEG", -0.6)
    return cam, lid, des, g("CAMARA_HFOV_DEG", 68.3), g("CAMARA_VFOV_DEG", 54.0)


def _xy(d, cam, inc, des, hfov, vfov):
    _leer()
    c = _cache["cal"]
    dh = (c.get("hc", 0) - c.get("hl", 0)) / 100.0 if c.get("hc") and c.get("hl") else DH_CM_POR_OMISION / 100.0
    off = (c.get("off_camara_cm") or OFF_CM_POR_OMISION) / 100.0
    eps = math.atan((d * math.tan(math.radians(inc)) - dh) / (d + off))
    fy = 0.5 - math.tan(eps - math.radians(cam)) / (2.0 * math.tan(math.radians(vfov / 2.0)))
    fx = 0.5 + (math.tan(math.radians(des)) * d / (d + off)) / (2.0 * math.tan(math.radians(hfov / 2.0)))
    return fx, fy


def punto_para(d_m):
    """(fx, fy) normalizados donde cae el rayo cuando mide d_m metros; None si no hay punto guardado o d_m no sirve."""
    _leer()
    a = _cache["alin"]
    if a is None:
        return None
    x0, y0, d0 = a
    if not d_m or d_m <= 0.3 or d_m > 60.0 or d0 <= 0.3:
        return (x0, y0)                  # sin distancia útil: el punto guardado tal cual
    try:
        cam, inc, des, hfov, vfov = angulos_chasis()
        fx0, fy0 = _xy(d0, cam, inc, des, hfov, vfov)
        fx1, fy1 = _xy(d_m, cam, inc, des, hfov, vfov)
    except (ValueError, ZeroDivisionError):
        return (x0, y0)
    return (min(max(x0 + (fx1 - fx0), 0.0), 1.0), min(max(y0 + (fy1 - fy0), 0.0), 1.0))


if __name__ == "__main__":
    # autocomprobación: con la calibración del escritorio, a 2 m debe dar el punto guardado y a 15 m un punto más arriba
    _cache.update(t=time.time() + 1e9, alin=(0.4956, 0.5954, 2.02), cal={})
    p2, p15 = punto_para(2.02), punto_para(15.0)
    print("a 2 m:", p2, "| a 15 m:", p15)
    assert abs(p2[1] - 0.5954) < 1e-9 and p15[1] < p2[1] - 0.005, "a mayor distancia el rayo debe verse más arriba"
    print("ok")
