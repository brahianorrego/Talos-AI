# -*- coding: utf-8 -*-
"""
Modelo del DRON REAL como lista de piezas simples (cajas y cilindros), hecho a ojo con las fotos de
08_EVIDENCIA_Y_DIAGRAMAS/fotos (08, 09, 10, 14 a 18 y, desde el 20-oct, 19 a 23) y con los datos de 05_HARDWARE_Y_VARIANTES/hardware.md.
TRES VARIANTES (D-072): "minimo" (variante G, el dron de hoy: sin BaseCam ni cámara USB; cámara CSI IMX219 y TF03 fijos), "plus" (variante H, la
meta: pan-tilt de 2 servos con la CSI y el TF-Luna encima, una 2.ª CSI fija al piso y el TF03 fijo; la batería corrida hacia atrás) y "gimbal" (el
de antes, BaseCam + USB, solo historia). El JSON trae `piezas` (minimo), `piezas_plus` (con "grupo": "pan" o "tilt" en lo que se mueve y los `pivotes`
de los dos ejes) y `piezas_gimbal`. Los programas eligen con DRONIA_DRON=minimo|plus|gimbal (Unreal, Blender) o ?dron= (visores).
NO es fotorrealista: es proporcionado, con los colores del dron, y lo usan Unreal (unreal/dronia_ue.py), Blender
(blender/video_cancha_v17.py) y el visor web (modelo_dron/dron_real.json, que genera este archivo).

Marco del dron (como la simulación): x hacia ADELANTE (hacia donde mira la cámara), y a la IZQUIERDA, z ARRIBA; metros;
el origen es el centro de la placa del medio del chasis. Cada pieza:
  nombre, forma ("caja" | "cilindro"), centro (x, y, z), tamaño, color, y opcionalmente yaw (grados, antihorario visto desde arriba),
  inclinacion (grados, giro alrededor del eje x, sentido de la regla de la mano derecha; solo las patas), eje ("x" | "y" | "z", solo cilindros: hacia dónde apunta su largo).
  caja:      tamaño = (largo x, ancho y, alto z)
  cilindro:  tamaño = (diámetro, largo)         (el largo va sobre `eje`)
Los colores son nombres de COLORES (RGB lineal 0-1); "acrilico" va translúcido.

Cada medida lleva su origen en MEDIDAS: "foto" (estimada en las fotos), "datasheet" (hoja de datos, de memoria) o "medida"
(pesada o medida por Brahian). Lo que NO está medido está en FALTAN. Ejecutar este archivo escribe dron_real.json y lista el tamaño total.
"""
import json
import math
import os

COLORES = {
    "carbono": (0.020, 0.020, 0.025), "negro": (0.010, 0.010, 0.012), "rojo": (0.55, 0.030, 0.030), "dorado": (0.60, 0.40, 0.08),
    "turquesa": (0.03, 0.55, 0.60), "acrilico": (0.80, 0.85, 0.90), "azul": (0.03, 0.15, 0.70), "servo": (0.02, 0.05, 0.20), "gris": (0.20, 0.20, 0.22),
    "amarillo": (0.80, 0.50, 0.03), "verde": (0.03, 0.30, 0.08), "placa": (0.04, 0.10, 0.35), "espuma": (0.015, 0.015, 0.015), "flex": (0.70, 0.45, 0.06),
}

MEDIDAS = {
    "distancia entre motores opuestos 0.50 m": "foto (la hélice de 10″ como regla, ±10 %)",
    "hélice 10″ = 0.254 m": "hardware.md / VARIANTES.md",
    "motor 2212 de 920 KV (campana de 28 mm)": "foto 04 y hoja de datos",
    "tubo de carbono de 25 mm": "foto",
    "TF03 74 × 47 × 36.5 mm, 77 g": "datasheet, de memoria",
    "batería LiPo 4S de 6200 mAh (OVONIC), ≈ 155 × 50 × 45 mm": "etiqueta en la foto 16; medidas estimadas",
    "peso total en vuelo 2 371 g": "medida (báscula, foto 12 y 13)",
}

FALTAN = [
    "Distancia real entre motores opuestos (hoy 0.50 m a ojo): medir con cinta",
    "Tamaño de la placa del chasis, del acrílico de la Jetson y de la batería: medir (hoy estimados)",
    "Altura de las patas y largo de los apoyos de espuma (hoy 0.26 m y 0.34 m a ojo)",
    "Hacia dónde apunta el largo de la batería (hoy hacia adelante) y cuál lado del TF03 es el frente",
    "Posición exacta del GPS, de la cámara USB y de los 2 conectores amarillos (XT60)",
    "Cables: no se modelan",
    "Variante plus (H): las posiciones del pan-tilt, de la 2.ª CSI al piso, del TF03 y de la batería (corrida 10 mm atrás) salen de 05_/config_sim/variante_H.json (campos MONTAJE_*), que Hardware marca PROVISIONALES (nadie ha medido el dron). Hardware recomienda ahora el pan-tilt ARRIBA, sobre la placa de arriba delante de la caja de la Jetson; aquí se modela la opción 2, COLGADO bajo el chasis. Rangos: pan ±89°, tilt −44°…+14°",
    "Variante sin gimbal (foto 19 a 23): posición y tamaño de la base impresa, de la estructura volteada y de su agujero redondo (hoy a ojo); el lazo del flex y la inclinación de la CSI (la CSI va fija, pero hoy se modela vertical)",
]

R_MOTOR = 0.25            # distancia del centro al motor (la mitad de la distancia entre motores opuestos)
BRAZOS = (45, 135, 225, 315)


def _p(nombre, forma, centro, tam, color, **kw):
    d = {"nombre": nombre, "forma": forma, "centro": tuple(round(v, 4) for v in centro), "tam": tuple(round(v, 4) for v in tam), "color": color}
    d.update(kw)
    return d


def piezas(variante="minimo"):
    P = []
    variante = "minimo" if variante == "sin_gimbal" else variante
    # --- chasis: dos placas de carbono, el Pixhawk entre ellas y la placa de la batería
    P += [_p("placa_inferior", "caja", (0, 0, -0.025), (0.19, 0.19, 0.003), "carbono"),
          _p("placa_superior", "caja", (0, 0, 0.025), (0.17, 0.17, 0.003), "carbono"),
          _p("pixhawk", "caja", (-0.01, 0, 0.0), (0.082, 0.05, 0.016), "negro"),
          _p("placa_bateria", "caja", (0, 0, -0.078), (0.17, 0.09, 0.003), "carbono")]
    # --- 4 brazos de tubo de carbono, motores 2212, ESC de 40 A y hélices de 10″
    for k, a in enumerate(BRAZOS):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        en = lambda r, z: (r * ca, r * sa, z)                          # punto sobre el brazo, a r metros del centro
        P += [_p(f"brazo{k}", "cilindro", en(0.15, 0.0), (0.025, 0.20), "carbono", eje="x", yaw=a),
              _p(f"bisagra{k}", "caja", en(0.07, 0.0), (0.05, 0.04, 0.05), "negro", yaw=a),
              _p(f"soporte_motor{k}", "caja", en(R_MOTOR, -0.012), (0.04, 0.04, 0.03), "negro", yaw=a),
              _p(f"motor{k}", "cilindro", en(R_MOTOR, 0.018), (0.028, 0.032), "rojo", eje="z"),
              _p(f"motor_base{k}", "cilindro", en(R_MOTOR, 0.0), (0.024, 0.012), "negro", eje="z"),
              _p(f"esc{k}", "caja", en(0.13, 0.019), (0.055, 0.025, 0.012), "negro", yaw=a),
              _p(f"esc_etiqueta{k}", "caja", en(0.13, 0.026), (0.040, 0.018, 0.0015), "amarillo", yaw=a),
              _p(f"helice{k}", "caja", en(R_MOTOR, 0.046), (0.254, 0.020, 0.003), "negro", yaw=a + 20),
              _p(f"cono{k}", "cilindro", en(R_MOTOR, 0.052), (0.030, 0.030), "negro", eje="z")]
    # --- Jetson en caja de acrílico con ventilador, 2 antenas WiFi y GPS (fotos 09, 14, 15)
    P += [_p("placa_jetson", "caja", (0, 0, 0.073), (0.12, 0.10, 0.003), "carbono")]
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        P += [_p("separador_turquesa", "cilindro", (0.045 * sx, 0.04 * sy, 0.0605), (0.012, 0.020), "turquesa", eje="z"),
              _p("poste_dorado", "cilindro", (0.050 * sx, 0.040 * sy, 0.098), (0.005, 0.048), "dorado", eje="z")]
    P += [_p("jetson", "caja", (0, 0, 0.090), (0.10, 0.08, 0.020), "verde"),
          _p("caja_acrilico", "caja", (0, 0, 0.100), (0.105, 0.085, 0.045), "acrilico", translucido=True),
          _p("ventilador", "caja", (0.0, 0.0, 0.1285), (0.040, 0.040, 0.012), "negro"),
          _p("antena_izq", "cilindro", (0.0, 0.108, 0.115), (0.008, 0.11), "negro", eje="y"),
          _p("antena_der", "cilindro", (0.0, -0.108, 0.115), (0.008, 0.11), "negro", eje="y"),
          _p("gps_mastil", "cilindro", (-0.07, 0.0, 0.110), (0.010, 0.04), "negro", eje="z"),
          _p("gps", "cilindro", (-0.07, 0.0, 0.136), (0.050, 0.012), "negro", eje="z")]
    # --- batería LiPo 4S con velcro azul, colgando bajo el chasis
    P += [_p("bateria", "caja", (0.0, 0.0, -0.103), (0.155, 0.050, 0.045), "gris"),
          _p("velcro_azul", "caja", (0.0, 0.0, -0.103), (0.030, 0.054, 0.049), "azul")]
    # --- patas de carbono y apoyos de espuma con anillos rojos
    for sy in (1, -1):
        P += [_p("pata", "cilindro", (0.0, 0.14 * sy, -0.145), (0.016, 0.24), "carbono", eje="z", inclinacion=12 * sy),
              _p("apoyo_espuma", "cilindro", (0.0, 0.17 * sy, -0.245), (0.030, 0.34), "espuma", eje="x")]
        for ax in (-0.15, 0.0, 0.15):
            P += [_p("anillo_rojo", "cilindro", (ax, 0.17 * sy, -0.245), (0.033, 0.010), "rojo", eje="x")]
    if variante == "gimbal":
        # --- gimbal BaseCam (roll y pitch) con el TF03 y la cámara USB encima (fotos 15 a 18)
        P += [_p("gimbal_placa", "caja", (0.095, 0.0, -0.088), (0.085, 0.075, 0.003), "negro"),
              _p("gimbal_placa_azul", "caja", (0.045, 0.0, -0.092), (0.050, 0.040, 0.006), "placa"),
              _p("gimbal_motor_roll", "cilindro", (0.125, 0.0, -0.108), (0.058, 0.030), "negro", eje="x"),
              _p("gimbal_brazo", "caja", (0.150, 0.0, -0.160), (0.010, 0.014, 0.090), "negro"),
              _p("gimbal_motor_pitch", "cilindro", (0.150, 0.030, -0.200), (0.055, 0.030), "negro", eje="y"),
              _p("gimbal_plataforma", "caja", (0.185, 0.0, -0.200), (0.060, 0.050, 0.004), "negro"),
              _p("tf03", "caja", (0.200, 0.0, -0.222), (0.047, 0.074, 0.0365), "negro"),
              _p("camara_usb_placa", "caja", (0.193, 0.0, -0.1995), (0.026, 0.028, 0.002), "verde"),
              _p("camara_usb_lente", "cilindro", (0.206, 0.0, -0.1965), (0.016, 0.022), "negro", eje="x")]
    elif variante == "minimo":
        # --- 20-oct (fotos 19 a 23): sin gimbal ni cámara USB. TF03 fijo en una base impresa, al frente del lado DERECHO (y < 0), a la altura de las placas
        P += [_p("base_impresa", "caja", (0.112, -0.075, -0.032), (0.062, 0.088, 0.004), "negro"),
              _p("tf03", "caja", (0.118, -0.075, -0.011), (0.047, 0.074, 0.0365), "negro"),
              _p("tf03_ventana", "caja", (0.1418, -0.075, -0.011), (0.0012, 0.058, 0.022), "gris")]
        # --- cámara CSI IMX219 arriba de la caja de acrílico, al frente, mirando adelante; su cable flex dorado sube, da un lazo y entra a la Jetson
        P += [_p("csi_placa", "caja", (0.060, 0.0, 0.1385), (0.003, 0.024, 0.025), "verde"),
              _p("csi_lente", "cilindro", (0.0635, 0.0, 0.1385), (0.009, 0.004), "negro", eje="x"),
              _p("csi_flex_sube", "caja", (0.057, 0.0, 0.158), (0.001, 0.016, 0.030), "flex"),
              _p("csi_flex_lazo", "caja", (0.033, 0.0, 0.1735), (0.050, 0.016, 0.001), "flex"),
              _p("csi_flex_baja", "caja", (0.009, 0.0, 0.1535), (0.001, 0.016, 0.040), "flex")]
        # --- estructura impresa volteada bajo el chasis, sobre el frente de la batería, colgada con dos separadores dorados
        P += [_p("estructura_volteada", "caja", (0.075, 0.0, -0.0765), (0.075, 0.072, 0.012), "negro"),
              _p("estructura_agujero", "cilindro", (0.075, 0.0, -0.0702), (0.032, 0.0012), "gris", eje="z"),
              _p("estructura_poste", "cilindro", (0.060, 0.030, -0.056), (0.005, 0.045), "dorado", eje="z"),
              _p("estructura_poste", "cilindro", (0.060, -0.030, -0.056), (0.005, 0.045), "dorado", eje="z")]
    elif variante == "plus":
        P += [_p("tf03", "caja", TF03_PLUS, (0.047, 0.074, 0.0365), "negro"),          # TF03 fijo al chasis (−5°), donde está hoy: lado derecho
              _p("tf03_ventana", "caja", (TF03_PLUS[0] + 0.0238, TF03_PLUS[1], TF03_PLUS[2]), (0.0012, 0.058, 0.022), "gris")]
    if variante == "plus":
        P = [dict(p, centro=(p["centro"][0] + BATERIA_DX, p["centro"][1], p["centro"][2])) if p["nombre"] in ("bateria", "velcro_azul") else p for p in P]   # batería atrás por el CG
        P += _pantilt()
    return P


# pan-tilt de 2 servos (05_HARDWARE_Y_VARIANTES/piezas_3d/pan_tilt_servos.scad, solo como referencia de forma): colgado bajo el chasis, eje de pan vertical
# en x = 0.075, eje de tilt horizontal (a lo largo de y) 0.072 m más abajo; la cuna lleva la CSI y el TF-Luna. Medidas del scad (MG90D de la hoja de datos).
def _montaje():
    """Las posiciones del plus las fija Hardware en 05_HARDWARE_Y_VARIANTES/config_sim/variante_H.json (campos MONTAJE_*, PROVISIONALES, solo lectura aquí)."""
    por_omision = {"MONTAJE_EJE_PAN_M": [0.075, 0.0, -0.0365], "MONTAJE_EJE_TILT_M": [0.075, 0.0, -0.110], "MONTAJE_CSI2_PISO_M": [-0.010, 0.060, -0.034],
                   "MONTAJE_TF03_M": [0.118, -0.075, -0.011], "MONTAJE_BATERIA_DESPLAZ_X_M": -0.010}
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "05_HARDWARE_Y_VARIANTES", "config_sim", "variante_H.json"), encoding="utf-8") as f:
            d = json.load(f)
        por_omision.update({k: d[k] for k in por_omision if k in d})
    except (OSError, ValueError):
        pass
    return por_omision


_M = _montaje()
PIVOTE_PAN = tuple(_M["MONTAJE_EJE_PAN_M"])
PIVOTE_TILT = tuple(_M["MONTAJE_EJE_TILT_M"])
CSI_PISO = tuple(_M["MONTAJE_CSI2_PISO_M"])
TF03_PLUS = tuple(_M["MONTAJE_TF03_M"])
BATERIA_DX = _M["MONTAJE_BATERIA_DESPLAZ_X_M"]


def _pantilt():
    px, _, pz = PIVOTE_PAN
    tx, _, tz = PIVOTE_TILT
    return [
        # fijo al chasis
        _p("pantilt_base", "caja", (px, 0.0, -0.0345), (0.064, 0.056, 0.003), "negro"),
        _p("servo_pan", "caja", (px + 0.0055, 0.0, -0.0473), (0.0228, 0.0122, 0.0225), "servo"),
        _p("tf03_base", "caja", (TF03_PLUS[0] - 0.006, TF03_PLUS[1], TF03_PLUS[2] - 0.021), (0.052, 0.080, 0.003), "negro"),
        # gira con el PAN (yaw): plataforma, mejillas y servo del tilt
        _p("pan_plataforma", "caja", (px, 0.0, -0.0675), (0.052, 0.056, 0.003), "negro", grupo="pan"),
        _p("pan_mejilla_a", "caja", (px, -0.0285, -0.0875), (0.052, 0.004, 0.040), "negro", grupo="pan"),
        _p("pan_mejilla_b", "caja", (px, 0.0275, -0.0875), (0.052, 0.003, 0.040), "negro", grupo="pan"),
        _p("servo_tilt", "caja", (tx - 0.0055, -0.0315, tz), (0.0228, 0.0225, 0.0122), "servo", grupo="pan"),
        # gira con el PAN y el TILT (cabeceo, tope −44°/+14°): cuna con la CSI y el TF-Luna
        _p("cuna_cubierta", "caja", (tx + 0.015, 0.0, tz), (0.030, 0.044, 0.003), "negro", grupo="tilt"),
        _p("cuna_pared_izq", "caja", (tx + 0.015, 0.0215, tz), (0.030, 0.0025, 0.040), "negro", grupo="tilt"),
        _p("cuna_pared_der", "caja", (tx + 0.015, -0.0215, tz), (0.030, 0.0040, 0.040), "negro", grupo="tilt"),
        _p("cuna_frente", "caja", (tx + 0.030, 0.0, tz), (0.004, 0.044, 0.050), "negro", grupo="tilt"),
        _p("csi_placa", "caja", (tx + 0.0335, 0.0, tz + 0.013), (0.003, 0.024, 0.025), "verde", grupo="tilt"),
        _p("csi_lente", "cilindro", (tx + 0.0365, 0.0, tz + 0.013), (0.009, 0.004), "negro", eje="x", grupo="tilt"),
        _p("luna", "caja", (tx + 0.0425, 0.0, tz - 0.013), (0.0135, 0.035, 0.0213), "negro", grupo="tilt"),
        _p("luna_lente", "cilindro", (tx + 0.0502, 0.0, tz - 0.013), (0.008, 0.003), "gris", eje="x", grupo="tilt"),
        _p("csi_flex", "caja", (tx + 0.023, 0.0, tz + 0.034), (0.001, 0.016, 0.040), "flex", grupo="tilt"),
        # 2.ª CSI fija mirando al piso (CAM1, −90°): al costado izquierdo, fuera de la batería, bajo el chasis
        _p("csi_piso_soporte", "caja", (CSI_PISO[0], CSI_PISO[1], CSI_PISO[2] + 0.0047), (0.049, 0.044, 0.0065), "negro"),
        _p("csi_piso_placa", "caja", CSI_PISO, (0.025, 0.024, 0.003), "verde"),
        _p("csi_piso_lente", "cilindro", (CSI_PISO[0], CSI_PISO[1], CSI_PISO[2] - 0.0027), (0.009, 0.004), "negro", eje="z"),
    ]


def tamano_total():
    """Caja que contiene todo el dron: (x0, x1, y0, y1, z0, z1) en m. Aproximada: usa el tamaño de cada pieza girada."""
    x0 = y0 = z0 = 1e9
    x1 = y1 = z1 = -1e9
    for p in piezas():
        cx, cy, cz = p["centro"]
        a, b, c = p["tam"] if p["forma"] == "caja" else ((p["tam"][0], p["tam"][0], p["tam"][1]) if p.get("eje", "z") == "z" else
                                                          ((p["tam"][1], p["tam"][0], p["tam"][0]) if p["eje"] == "x" else (p["tam"][0], p["tam"][1], p["tam"][0])))
        y = math.radians(p.get("yaw", 0.0))
        hx, hy = (abs(a * math.cos(y)) + abs(b * math.sin(y))) / 2, (abs(a * math.sin(y)) + abs(b * math.cos(y))) / 2
        x0, x1, y0, y1 = min(x0, cx - hx), max(x1, cx + hx), min(y0, cy - hy), max(y1, cy + hy)
        z0, z1 = min(z0, cz - c / 2), max(z1, cz + c / 2)
    return x0, x1, y0, y1, z0, z1


if __name__ == "__main__":
    aqui = os.path.dirname(os.path.abspath(__file__))
    datos = {"unidades": "m", "marco": "x adelante, y izquierda, z arriba; origen = centro de la placa del medio",
             "colores": COLORES, "variante": "minimo", "piezas": piezas(), "piezas_plus": piezas("plus"), "pivotes_plus": {"pan": PIVOTE_PAN, "tilt": PIVOTE_TILT},
             "piezas_gimbal": piezas("gimbal"), "faltan": FALTAN}
    for destino in (os.path.join(aqui, "dron_real.json"),                                        # Unreal y Blender
                    os.path.join(aqui, "..", "v16", "simulacion", "recursos", "dron_real.json"),  # visor V16
                    os.path.join(aqui, "..", "estacion", "dron_real.json")):                      # estación de tierra
        with open(destino, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=1)
    x0, x1, y0, y1, z0, z1 = tamano_total()
    print(f"{len(piezas())} piezas · largo {x1 - x0:.3f} m · ancho {y1 - y0:.3f} m · alto {z1 - z0:.3f} m "
          f"(del apoyo a la antena/GPS) · el origen está {-z0:.3f} m sobre el suelo")
