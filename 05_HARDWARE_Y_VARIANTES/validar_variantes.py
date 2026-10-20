"""Comprueba los config_sim/variante_*.json contra las reglas duras del proyecto y, para C y D, contra las
constantes de 03_SIMULACION_RL/entorno.py y control.py (solo las LEE con ast; no importa ni escribe nada de 03_).

Uso (desde cualquier carpeta):  python validar_variantes.py
Sale con código 1 si algo falla. No importa nada del proyecto: solo lee los JSON.
"""
import ast
import glob
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
TIPOS_GIMBAL = {"basecam", "servo", "mixto", "servo_sobre_basecam", "fijo"}


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
    if v["GIMBAL_TIPO"] == "fijo" and not (v["GIMBAL_MIN"] <= v["CAM_PRINCIPAL_PITCH_FIJO_DEG"] <= v["GIMBAL_MAX"]):
        e.append("cámara fija: su pitch debe quedar dentro de −45°..+15°")
    if v["GIMBAL_TIPO"] not in ("basecam", "fijo") and not v["GIMBAL_TOPES_MECANICOS"]:
        e.append("un gimbal por servo debe llevar topes mecánicos")
    if v["PAN_ACTIVO_EN_ENTRENAMIENTO"] and not v["PAN_DISPONIBLE"]:
        e.append("PAN activo sin estar disponible")
    if v["PAN_DISPONIBLE"] and not (-90.0 <= v["PAN_MIN"] < v["PAN_MAX"] <= 90.0):
        e.append("PAN fuera de ±90°")
    if v["CAM_PISO_ACTIVA"] and v["CAM_PISO_PITCH"] != -90.0:
        e.append("la cámara al piso va recta a −90°")
    if v["CAM_PISO_ACTIVA"] and v["CAM_PISO_PUERTO"] == v["CAM_FRONTAL_ANCHA_PUERTO"]:
        e.append("dos cámaras CSI en el mismo puerto")
    if v["LIDAR_TF03_MONTAJE"] in ("chasis", "base_fija") and not -5.0 <= v["LIDAR_TF03_PITCH_DEG"] <= 5.0:
        e.append("TF03 fijo al chasis: cabeceo de montaje debe quedar entre −5° y +5°")
    if v["LIDAR_TF03_MONTAJE"] in ("chasis", "base_fija") and not v["LIDAR_DESCARTE_SUELO_CON_ACTITUD"]:
        e.append("TF03 al chasis exige descartar impactos al suelo con la actitud")
    if v["LIDAR_TF03_MONTAJE"] in ("chasis", "base_fija") and v["LIDAR_TF03_SIGUE_GIMBAL"]:
        e.append("TF03 al chasis no puede seguir al gimbal")
    return e


SIM = os.path.join(AQUI, "..", "03_SIMULACION_RL")
BC, MX = "control.GimbalBaseCam.", "control.GimbalMixto."


def constantes(archivo, prefijo):
    """Asignaciones literales de módulo (NOMBRE) y de clase (Clase.NOMBRE) de un .py, sin ejecutarlo."""
    out = {}

    def tomar(nodos, pre):
        for n in nodos:
            if isinstance(n, ast.Assign) and len(n.targets) == 1:
                t = n.targets[0]
                nombres = [t] if isinstance(t, ast.Name) else (t.elts if isinstance(t, ast.Tuple) else [])
                try:
                    v = ast.literal_eval(n.value)
                except ValueError:
                    continue
                vals = [v] if isinstance(t, ast.Name) else (list(v) if isinstance(v, tuple) else [])
                for nom, val in zip(nombres, vals):
                    if isinstance(nom, ast.Name):
                        out[pre + nom.id] = val  # la última asignación gana, como en Python
            elif isinstance(n, ast.ClassDef):
                tomar(n.body, f"{prefijo}{n.name}.")

    with open(archivo, encoding="utf-8") as f:
        tomar(ast.parse(f.read()).body, "" if prefijo == "entorno." else prefijo)
    return out


def contra_simulacion(v, c):
    """Lista de (clave JSON, valor JSON, constante, valor de la simulación, estado) para una variante."""
    eq = v["GIMBAL_TIPO_EQUIVALENTE_V16"]
    g = ((MX + "SERVO_VEL", MX + "RETARDO", MX + "SERVO_BANDA") if eq == "servo" else (None, None, None) if eq == "fijo"
         else (BC + "VEL_MAX", BC + "TAU_ESTAB", None))
    filas = [
        ("GIMBAL_MIN", v["GIMBAL_MIN"], "GIMBAL_MIN", None),
        ("GIMBAL_MAX", v["GIMBAL_MAX"], "GIMBAL_MAX", None),
        ("GIMBAL_VEL_DPS", v["GIMBAL_VEL_DPS"], g[0], None),
        ("GIMBAL_RETARDO_S", tuple(v["GIMBAL_RETARDO_S"]), g[1], "tupla"),
        ("GIMBAL_ZONA_MUERTA_DEG", v["GIMBAL_ZONA_MUERTA_DEG"], g[2], None),
        ("CAM_PRINCIPAL_HFOV", v["CAM_PRINCIPAL_HFOV"], "HFOV", None),
        ("CAM_PRINCIPAL_VFOV", v["CAM_PRINCIPAL_VFOV"], "VFOV", None),
        ("CAM_PISO_HFOV", v["CAM_PISO_HFOV"], "CAM_PISO_HFOV", None),
        ("CAM_PISO_VFOV", v["CAM_PISO_VFOV"], "CAM_PISO_VFOV", None),
        ("CAM_PISO_PITCH", v["CAM_PISO_PITCH"], "CAM_PISO_PITCH", None),
        ("LIDAR_TF03_PITCH_DEG", v["LIDAR_TF03_PITCH_DEG"], "TF03_PITCH_V17", None),
        ("LIDAR_TF03_ALCANCE_M", v["LIDAR_TF03_ALCANCE_M"], "LIDAR_MAX", None),
        ("LIDAR_LUNA_ALCANCE_M", tuple(v["LIDAR_LUNA_ALCANCE_M"]), "LUNA_MAX", "tupla"),
        ("LIDAR_LUNA_PISO_ALTIMETRO", "luna" if v["LIDAR_LUNA_PISO_ALTIMETRO"] else "baro", "ALTIMETRO", None),
    ]
    res = []
    for clave, val, nom, _ in filas:
        if nom is None or nom not in c:
            res.append((clave, val, nom or "—", None, "sin constante"))
            continue
        sim = c[nom]
        sim = tuple(sim) if isinstance(sim, (list, tuple)) else sim
        if isinstance(val, tuple) and isinstance(sim, (int, float)):
            ok = all(abs(x - sim) < 1e-9 for x in val)  # BaseCam: un solo retardo (TAU_ESTAB) para los dos extremos
        else:
            ok = (val == sim) if isinstance(val, (tuple, str)) or isinstance(sim, (tuple, str)) else abs(val - sim) < 1e-9
        res.append((clave, val, nom, sim, "OK" if ok else "DIFIERE"))
    # el tipo de gimbal: la V17 entrena "mixto", que incluye BaseCam y servo
    tipo = c.get("GIMBAL_TIPO")
    res.append(("GIMBAL_TIPO_EQUIVALENTE_V16", v["GIMBAL_TIPO_EQUIVALENTE_V16"], "GIMBAL_TIPO", tipo,
                "OK" if tipo == eq or (tipo == "mixto" and eq in ("basecam", "servo")) else "DIFIERE"))
    return res


def informe_simulacion(datos):
    ent, ctl = os.path.join(SIM, "entorno.py"), os.path.join(SIM, "control.py")
    if not (os.path.exists(ent) and os.path.exists(ctl)):
        print("\n(no se encontró 03_SIMULACION_RL: se omite la comparación con la simulación)")
        return 0
    c = {**constantes(ent, "entorno."), **constantes(ctl, "control.")}
    dif = 0
    for nombre in ("variante_G.json", "variante_H.json"):
        print(f"\n== {nombre} contra 03_SIMULACION_RL ==")
        for clave, val, nom, sim, est in contra_simulacion(datos[nombre], c):
            dif += est == "DIFIERE"
            print(f"  {est:13} {clave} = {val}  |  {nom} = {sim}")
        print("  sin constante en la simulación (según PROGRESO_V17): PAN_*, CAM_FRONTAL_ANCHA_*, CAM_PISO_ACTIVA, YOLO_FPS_*, MASA_*,")
        print("  LIDAR_TF03_MONTAJE y LIDAR_LUNA_MONTAJE: no se comprueban aquí.")
    return dif


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
    informe_simulacion(datos)
    return 1 if malo else 0


if __name__ == "__main__":
    sys.exit(main())
