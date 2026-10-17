"""Comprueba los config_sim/variante_*.json contra las reglas duras del proyecto.

Uso (desde cualquier carpeta):  python validar_variantes.py
Sale con código 1 si algo falla. No importa nada del proyecto: solo lee los JSON.
"""
import glob
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
TIPOS_GIMBAL = {"basecam", "servo", "mixto", "servo_sobre_basecam"}


def pwm(theta):  # regla dura 1 (CLAUDE.md): pwm = 1500 + θ·500/45
    return 1500 + theta * 500 / 45


def revisar(v):
    e = []
    if not (-45.0 <= v["GIMBAL_MIN"] < v["GIMBAL_MAX"] <= 15.0):
        e.append("GIMBAL_MIN/MAX fuera de −45°..+15° (regla dura 1)")
    if not (v["GIMBAL_MIN"] <= v["GIMBAL_TOPE_FISICO_MIN"] <= v["GIMBAL_MAX"]):
        e.append("GIMBAL_TOPE_FISICO_MIN fuera de GIMBAL_MIN..GIMBAL_MAX")
    if not (1000 <= pwm(v["GIMBAL_MIN"]) and pwm(v["GIMBAL_MAX"]) <= 1667):
        e.append("el PWM de AUX1 se sale de 1000..1667 µs")
    if v["GIMBAL_TIPO"] not in TIPOS_GIMBAL:
        e.append("GIMBAL_TIPO desconocido")
    if v["GIMBAL_TIPO"] != "basecam" and not v["GIMBAL_TOPES_MECANICOS"]:
        e.append("un gimbal por servo debe llevar topes mecánicos")
    if v["PAN_ACTIVO_EN_ENTRENAMIENTO"] and not v["PAN_DISPONIBLE"]:
        e.append("PAN activo sin estar disponible")
    if v["PAN_DISPONIBLE"] and not (-90.0 <= v["PAN_MIN"] < v["PAN_MAX"] <= 90.0):
        e.append("PAN fuera de ±90°")
    if v["CAM_PISO_ACTIVA"] and v["CAM_PISO_PITCH"] != -90.0:
        e.append("la cámara al piso va recta a −90°")
    if v["CAM_PISO_ACTIVA"] and v["CAM_PISO_PUERTO"] == v["CAM_FRONTAL_ANCHA_PUERTO"]:
        e.append("dos cámaras CSI en el mismo puerto")
    if v["LIDAR_TF03_MONTAJE"] == "chasis" and not -5.0 <= v["LIDAR_TF03_PITCH_DEG"] <= 5.0:
        e.append("TF03 fijo al chasis: cabeceo de montaje debe quedar entre −5° y +5°")
    if v["LIDAR_TF03_MONTAJE"] == "chasis" and not v["LIDAR_DESCARTE_SUELO_CON_ACTITUD"]:
        e.append("TF03 al chasis exige descartar impactos al suelo con la actitud")
    if v["LIDAR_TF03_MONTAJE"] == "chasis" and v["LIDAR_TF03_SIGUE_GIMBAL"]:
        e.append("TF03 al chasis no puede seguir al gimbal")
    return e


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # la consola de Windows usa cp1252 y no tiene el signo −
    archivos = sorted(glob.glob(os.path.join(AQUI, "config_sim", "variante_*.json")))
    if not archivos:
        print("No hay variantes")
        return 1
    datos = {}
    for a in archivos:
        with open(a, encoding="utf-8") as f:
            datos[os.path.basename(a)] = json.load(f)
    claves = set(next(iter(datos.values())))
    malo = False
    for nombre, v in datos.items():
        errores = revisar(v) if set(v) == claves else ["no tiene las mismas claves que las demás"]
        malo |= bool(errores)
        print(f"{nombre}: {'OK' if not errores else 'FALLA'}")
        for e in errores:
            print("   -", e)
    return 1 if malo else 0


if __name__ == "__main__":
    sys.exit(main())
