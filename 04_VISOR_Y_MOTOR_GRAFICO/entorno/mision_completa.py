# -*- coding: utf-8 -*-
"""
La MISIÓN COMPLETA de punta a punta en el campus de la universidad, como una repetición que entienden la estación web y Unreal:

  1 DESPEGUE   el piloto despega del helipuerto, en el extremo sur de la cancha de fútbol, y sube a 2.3 m
  2 TRÁNSITO   el piloto avanza de frente hacia la zona de IA; en el camino hay un PANEL, un ÁRBOL y una PERSONA que cruza.
               El MÍNIMO INDISPENSABLE vigila: ante un riesgo frena, sube a 3.30 m y se retiene hasta que el operador lo libera
               (REANUDAR); el panel lo salta por arriba, al árbol lo rodea el piloto, y a la persona la deja pasar.
  3 ACTIVACIÓN en la zona el piloto activa la IA con el interruptor CH7 (CH8 sigue siendo la parada de emergencia)
  4 ZONA       una partida V17 completa (la que se pida: salida_v17_*/replay_v17.json), desde donde estaba el dron

El tránsito usa las MISMAS reglas y números del mínimo (01_MINIMO_INDISPENSABLE/minimo_tesis/sistema.py, solo lectura): riesgo por
obstáculo (distancia de frenado + margen, 2.5 s al choque o menos de 3 m) y por persona (menos de 3 m, o menos de 8 m acercándose a más de
0.4 m/s con el punto de máximo acercamiento a menos de 2 m en 6 s), frenada a 2.5 m/s², latencia 0.5 s y ascenso a 2.5 m/s. Es una versión
cinemática y sin ruido de esa lógica (el mínimo real es el simulado con ArduPilot en minimo_tesis/): la forma y los tiempos son los de la
regla, no una nueva medida. Marco del campus: x este, y norte, origen = centro de la zona de IA.

Escribe estacion/mision_completa.json (más grande que el límite de Git: va al .gitignore; se regenera con este archivo):
    03_SIMULACION_RL/.venv/Scripts/python.exe 04_VISOR_Y_MOTOR_GRAFICO/entorno/mision_completa.py [replay_v17.json] [segundos_de_zona]
"""
import json
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.normpath(os.path.join(AQUI, "..", "..", "03_SIMULACION_RL"))
MINIMO = os.path.normpath(os.path.join(AQUI, "..", "..", "01_MINIMO_INDISPENSABLE", "minimo_tesis", "replay", "replay_protocolo.json"))

DT = 0.1
# del mínimo (sistema.py)
Z_PILOTO, Z_SEGURA, RADIO_DRON = 2.3, 3.30, 0.4
D_CRITICA, D_AMENAZA, V_ACERCA, CPA_RIESGO, T_CPA, D_BLOQUEO = 3.0, 8.0, 0.4, 2.0, 6.0, 3.0
A_FRENO, T_LAG, MARGEN, TTC_RIESGO, VEL_ASCENSO = 2.5, 0.5, 1.5, 2.5, 2.5
GIMBAL = -5.0                       # cámara y LiDAR casi horizontales en el tránsito
HFOV = 38.9                         # cámara USB principal
# la misión
PAD = (0.0, -62.0)                  # helipuerto: extremo sur de la cancha de fútbol (hay 76.5 m hasta la línea de fondo sur)
V_CRUCERO = 3.0
OBSTACULOS = {
    "panel": [-1.1, -50.0, 1.1, -50.0, 2.25],         # [x1, y1, x2, y2, alto]: como los paneles de la zona
    "arbol": {"p": [0.0, -38.0], "r": 0.35, "alto": 9.0, "copa": 3.0},
}
PERSONA_90 = {"y": -24.0, "x0": -1.0, "x1": -9.0, "v": 1.3, "est": 1.72}   # espera al borde del camino y cruza cuando el dron está a ~11 m


def punto_en_panel_y_rayo(x, y, psi, p):
    """Distancia a lo largo del rayo (x, y, psi) hasta el segmento p = [x1, y1, x2, y2, h]; None si no lo toca."""
    dx, dy = math.cos(psi), math.sin(psi)
    ex, ey = p[2] - p[0], p[3] - p[1]
    den = dx * ey - dy * ex
    if abs(den) < 1e-9:
        return None
    t = ((p[0] - x) * ey - (p[1] - y) * ex) / den
    u = ((p[0] - x) * dy - (p[1] - y) * dx) / den
    return t if t > 0 and 0 <= u <= 1 else None


def lidar(x, y, z, psi, paneles, arboles, personas):
    """Distancia (m) del LiDAR de frente, con el cabeceo de la cámara de -5°: el rayo solo choca con lo que mide más que su altura ahí."""
    pend = math.tan(math.radians(-GIMBAL))
    mejor = 30.0
    for p in paneles:
        t = punto_en_panel_y_rayo(x, y, psi, p)
        if t is not None and z - t * pend <= p[4]:
            mejor = min(mejor, t)
    for a in arboles:
        t = _circulo(x, y, psi, a["p"], a["r"])
        if t is not None and z - t * pend <= a["alto"]:
            mejor = min(mejor, t)
    for q in personas:
        t = _circulo(x, y, psi, q["p"], 0.3)
        if t is not None and z - t * pend <= q["est"]:
            mejor = min(mejor, t)
    return mejor


def _circulo(x, y, psi, c, r):
    dx, dy = math.cos(psi), math.sin(psi)
    rx, ry = c[0] - x, c[1] - y
    t = rx * dx + ry * dy
    if t <= 0:
        return None
    h = abs(rx * dy - ry * dx)
    return t - math.sqrt(r * r - h * h) if h < r else None


def riesgo(x, y, z, psi, vx, vy, paneles, arboles, personas):
    """(riesgo?, que, distancia): las dos condiciones del mínimo con la verdad del simulador."""
    v_av = vx * math.cos(psi) + vy * math.sin(psi)
    L = lidar(x, y, z, psi, paneles, arboles, personas)
    if L < 30 and v_av > 0.05 and (L < v_av * T_LAG + v_av ** 2 / (2 * A_FRENO) + MARGEN + RADIO_DRON or L / v_av < TTC_RIESGO or L < D_BLOQUEO):
        return True, "obstáculo", L
    for q in personas:
        rx, ry = q["p"][0] - x, q["p"][1] - y
        d = math.hypot(rx, ry)
        ang = abs((math.degrees(math.atan2(ry, rx) - psi) + 180) % 360 - 180)
        if ang > HFOV / 2 or d > D_AMENAZA:                       # la cámara solo ve lo que está en su campo
            continue
        ux, uy = q["v"][0] - vx, q["v"][1] - vy
        cierre = -(rx * ux + ry * uy) / max(d, 1e-6)
        uu = ux * ux + uy * uy
        ts = min(max(-(rx * ux + ry * uy) / uu, 0.0), T_CPA) if uu > 1e-9 else 0.0
        cpa = math.hypot(rx + ux * ts, ry + uy * ts)
        if d < D_CRITICA or (cierre > V_ACERCA and cpa < CPA_RIESGO):
            return True, "persona", d
    return False, "", L


def plantilla():
    """Un cuadro con todos los campos que lee el visor (el de la repetición del mínimo, que ya los trae en reposo)."""
    with open(MINIMO, encoding="utf-8") as f:
        return json.load(f)["cuadros"][0]


def cuadro_zona_estatica(c0):
    return [dict(rol=p["rol"], id=p["id"], p=list(p["p"]), v=[0.0, 0.0], vis=False, tap=False, est=p.get("est", 1.72), pos0=0, pos=0, pt=1.0,
                 run=False, alto=p.get("alto", p.get("est", 1.72)), mira=p.get("mira", 0.0), graba=False, civ=p.get("civ"),
                 res=p.get("res"), hr=p.get("hr"), sz=0.0, fv=0.0, ign=False, cand=False, pos0_=0) for p in c0["pers"]]


def generar(replay_zona, segundos_zona=None):
    with open(replay_zona, encoding="utf-8") as f:
        zona = json.load(f)
    Z = zona["cuadros"]
    if segundos_zona:
        Z = Z[: int(segundos_zona / zona.get("dt", 0.1)) + 1]
    z0 = Z[0]
    x_f, y_f, z_f, psi_f = z0["d"][:4]
    base = plantilla()
    paneles_t = [OBSTACULOS["panel"]]
    arboles = [OBSTACULOS["arbol"]]
    cuadros, eventos, letreros = [], [], []

    # estado del dron (mundo del campus)
    x, y, z, psi = PAD[0], PAD[1], 0.0, math.pi / 2
    vx = vy = vz = 0.0
    quietos = cuadro_zona_estatica(z0)
    persona90 = {"rol": "peaton", "id": 90, "p": [PERSONA_90["x0"], PERSONA_90["y"]], "v": [0.0, 0.0], "est": PERSONA_90["est"]}
    cruza = False

    def marca(k, txt, col, marcar=True):
        eventos.append({"k": k, "txt": txt, "col": col, "marca": marcar})

    def emitir(fase_txt, sub, min_estado, ch7=0, piloto=(0.0, 0.0), msg="", bloq=False):
        k = len(cuadros)
        c = dict(base)
        pers = [dict(rol=persona90["rol"], id=90, p=[round(persona90["p"][0], 3), round(persona90["p"][1], 3)], v=[round(persona90["v"][0], 3), round(persona90["v"][1], 3)],
                     vis=False, tap=False, est=persona90["est"], pos0=0, pos=0, pt=1.0, run=False, alto=persona90["est"], mira=math.atan2(persona90["v"][1], persona90["v"][0]) if cruza else math.pi,
                     graba=False, civ=0)] + quietos
        L = lidar(x, y, z, psi, paneles_t, arboles, [persona90])
        c.update({"fase": 1, "eb": "MANUAL", "d": [round(x, 3), round(y, 3), round(z, 3), round(psi, 4)], "dv": [round(vx, 3), round(vy, 3)], "pers": pers,
                  "lid": round(L, 2), "ldt": round(L, 2), "lh": [round(x + math.cos(psi) * min(L, 29), 3), round(y + math.sin(psi) * min(L, 29), 3), 1.0],
                  "gmb": GIMBAL, "cp": round(-min(2.0, abs(vy) * 0.5) if vy else 0.0, 2), "cr": 0.0, "bloq": bloq, "msg": msg, "piloto": [round(piloto[0], 2), round(piloto[1], 2)],
                  "dm": 99.0, "letrero": [fase_txt, sub, min_estado], "ch7": ch7, "min": min_estado})
        cuadros.append(c)
        return k

    t = 0.0
    # --- 1 DESPEGUE
    marca(0, "DESPEGUE · modo MANUAL, el piloto al mando", "#8b9bb0")
    for _ in range(int(2.0 / DT)):
        emitir("DESPEGUE", "El piloto arma el dron en el helipuerto", "VIGILA")
    while z < Z_PILOTO - 1e-3:
        vz = min(1.0, (Z_PILOTO - z) * 2)
        z += vz * DT
        emitir("DESPEGUE", "El piloto sube a 2.3 m", "VIGILA", piloto=(0.0, 0.9))
    vz = 0.0
    z = Z_PILOTO

    # --- 2 TRÁNSITO (el piloto manda; el mínimo vigila)
    estado, t_lag, t_ret, intervenciones = "avance", 0.0, 0.0, 0
    ultimo, msg_riesgo, rodeo_hecho = "", "", False
    marca(len(cuadros), "TRÁNSITO · el piloto avanza hacia la zona de IA; el mínimo vigila (LiDAR + YOLO)", "#2db7ff")
    while len(cuadros) < 6000:
        if not cruza and y > PERSONA_90["y"] - 11.0:                      # la persona estaba parada al borde del camino y se pone a cruzar
            cruza = True
            persona90["v"] = [-PERSONA_90["v"], 0.0]
            marca(len(cuadros), "UNA PERSONA empieza a cruzar el camino, de frente al dron", "#f5c542", False)
        if cruza:
            persona90["p"][0] += persona90["v"][0] * DT
            if persona90["p"][0] <= PERSONA_90["x1"]:
                persona90["v"] = [0.0, 0.0]
        riesgo_ya, que, dist = riesgo(x, y, z, psi, vx, vy, paneles_t, arboles, [persona90])
        if estado in ("avance", "rodeo") and riesgo_ya:
            estado, t_lag, intervenciones, ultimo = "frenando", 0.0, intervenciones + 1, que
            msg_riesgo = f"RIESGO: {que} al frente · DETENCIÓN + ASCENSO a 3.30 m · espera al operador"
            marca(len(cuadros), f"MÍNIMO · RIESGO: {que} al frente a {dist:.1f} m → DETENCIÓN + ASCENSO a 3.30 m, espera al operador", "#ff4d4f")
        if estado == "frenando":
            t_lag += DT
            if t_lag >= T_LAG:                                            # la orden llega con 0.5 s de latencia
                vy = max(0.0, vy - A_FRENO * DT)
                vz = min(VEL_ASCENSO, max(0.0, (Z_SEGURA - z) * 4))
            if vy < 0.02 and z >= Z_SEGURA - 0.02:
                estado, t_ret, vy, vz = "retenido", 0.0, 0.0, 0.0
        elif estado == "retenido":
            t_ret += DT
            persona_pasando = cruza and persona90["v"][0] != 0.0
            if t_ret >= 2.0 and not persona_pasando:
                marca(len(cuadros), "OPERADOR · REANUDAR: se libera la intervención y el piloto sigue", "#33d17a")
                if ultimo == "obstáculo" and not rodeo_hecho and abs(y - OBSTACULOS["arbol"]["p"][1]) < 6.0:
                    estado, rodeo_hecho = "rodeo", True                   # el árbol: el piloto lo rodea por la izquierda
                    marca(len(cuadros), "PILOTO · rodea el árbol por la izquierda (lo lateral es del piloto)", "#8b9bb0", False)
                else:
                    estado = "avance"
        v_cmd = vl_cmd = 0.0
        if estado == "avance":
            v_cmd = V_CRUCERO
        elif estado == "rodeo":
            vl_cmd = -1.5 if x > -3.9 else 0.0
            v_cmd = V_CRUCERO if x <= -3.9 else 0.0
            if y > OBSTACULOS["arbol"]["p"][1] + 3.0:
                estado = "avance"
        if estado in ("avance", "rodeo"):
            vy += max(-0.5, min(0.5, v_cmd - vy)) * 0.5 if v_cmd > 0 else (v_cmd - vy) * 0.4        # el piloto acelera con suavidad
            vx += (vl_cmd - vx) * 0.4
            vz = (Z_SEGURA - z) * 2 if intervenciones and z < Z_SEGURA - 0.01 else 0.0
        x, y, z = x + vx * DT, y + vy * DT, z + vz * DT
        if estado in ("frenando", "retenido"):
            emitir("TRÁNSITO", "EL MÍNIMO INTERVIENE: frena y sube a 3.30 m", "INTERVIENE" if estado == "frenando" else "RETENIDO",
                   piloto=(0.3, 0.0), msg=msg_riesgo, bloq=True)
        else:
            emitir("TRÁNSITO", "El piloto manda; el mínimo vigila", "VIGILA", piloto=(v_cmd / 3.0 * 0.6, -0.3 if estado == "rodeo" else 0.0),
                   msg="Piloto: avance 3 m/s")
        if y >= -15.0 and estado == "avance" and intervenciones >= 3:
            break
    # --- ruta hasta el punto donde empieza la partida V17 (con el piloto), sin riesgos
    marca(len(cuadros), "LLEGA A LA ZONA DE IA · el piloto se pone en el punto de partida", "#2db7ff")
    inicio = (x, y, z, psi)
    n_ap = int(5.0 / DT)
    for i in range(1, n_ap + 1):
        s = i / n_ap
        e = s * s * (3 - 2 * s)
        px, py, pz = inicio[0] + (x_f - inicio[0]) * e, inicio[1] + (y_f - inicio[1]) * e, inicio[2] + (z_f - inicio[2]) * e
        dpsi = (psi_f - inicio[3] + math.pi) % (2 * math.pi) - math.pi
        vx, vy, vz = (px - x) / DT, (py - y) / DT, (pz - z) / DT
        x, y, z, psi = px, py, pz, inicio[3] + dpsi * e
        emitir("TRÁNSITO", "Llega a la zona de IA: el piloto se pone en el punto de partida", "VIGILA", piloto=(0.3, 0.0))
    vx = vy = vz = 0.0
    # --- 3 ACTIVACIÓN (CH7)
    marca(len(cuadros), "ACTIVACIÓN · el piloto activa la IA con el interruptor CH7 (CH8 sigue siendo la parada)", "#f5c542")
    for i in range(int(3.0 / DT)):
        emitir("ACTIVACIÓN", "El piloto activa la IA con el interruptor CH7", "VIGILA", ch7=1 if i >= 8 else 0)
    k_zona = len(cuadros)
    marca(k_zona, "ZONA DE IA · la IA toma el mando (GUIDED): giro de 360° y búsqueda", "#2db7ff")
    # --- 4 ZONA: la partida V17, tal cual (con las personas que ya estaban quietas en el tránsito)
    for c in Z:
        c = dict(c)
        c["fase"] = 2
        c["fase_v17"] = "zona"
        c["letrero"] = ["ZONA DE IA", "La IA manda · el operador confirma al sospechoso", c.get("eb", "")]
        c["ch7"] = 1
        c["min"] = "STANDBY"
        cuadros.append(c)
    # eventos de la zona
    paneles = list(zona.get("paneles", [])) + paneles_t
    meta = {k: zona[k] for k in ("adversaria", "guion", "resultado", "maniobras", "version", "nivel", "nombre_nivel", "clases", "t_rinde", "autor", "iteracion", "pasos") if k in zona}
    out = dict(meta)
    out.update({"dt": DT, "paneles": paneles, "arboles": arboles, "pad": list(PAD), "mision_completa": True, "k_zona": k_zona, "obst": [],
                "eventos_extra": eventos, "cuadros": cuadros, "fuente_zona": os.path.basename(os.path.dirname(replay_zona))})
    return out


def principal():
    sys.stdout.reconfigure(encoding="utf-8")
    ruta = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SIM, "salida_v17_2", "replay_v17.json")
    seg = float(sys.argv[2]) if len(sys.argv) > 2 else None
    datos = generar(ruta, seg)
    destino = os.path.join(AQUI, "..", "estacion", "mision_completa.json")
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(datos, f, separators=(",", ":"))
    # letreros para el video de Unreal (cuadros a 24 cps): unir_video.py los escribe sobre la imagen
    seg, previo = [], None
    for k, c in enumerate(datos["cuadros"]):
        l = c.get("letrero")
        if not l:
            continue
        interv = c.get("min") in ("INTERVIENE", "RETENIDO")
        clave = ("TRÁNSITO · MÍNIMO INTERVIENE" if interv else l[0], l[1])
        f = int(round(k * DT * 24))
        if clave != previo:
            if seg:
                seg[-1]["f1"] = f - 1
            seg.append({"f0": f, "f1": f, "titulo": clave[0], "sub": clave[1], "color": [1.0, 0.3, 0.31] if interv else ([0.96, 0.77, 0.26] if l[0] == "ACTIVACIÓN" else ([0.18, 0.72, 1.0] if l[0] == "ZONA DE IA" else [0.7, 0.75, 0.82]))})
            previo = clave
        else:
            seg[-1]["f1"] = f
    with open(os.path.join(AQUI, "..", "estacion", "mision_letreros.json"), "w", encoding="utf-8") as f:
        json.dump(seg, f, ensure_ascii=False)
    n = len(datos["cuadros"])
    print(f"mision completa: {n} cuadros ({n * DT:.0f} s); tránsito {datos['k_zona'] * DT:.0f} s + zona {(n - datos['k_zona']) * DT:.0f} s -> {os.path.normpath(destino)}")
    for e in datos["eventos_extra"]:
        print(f"  {e['k'] * DT:6.1f} s  {e['txt']}")


if __name__ == "__main__":
    principal()
