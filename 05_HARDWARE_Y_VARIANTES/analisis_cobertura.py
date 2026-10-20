"""Análisis geométrico de cobertura de cámaras por variante (A-F). Solo geometría: sin simulación, sin red, sin ruido.

Uso (con el Python del proyecto, que ya trae matplotlib):
    03_SIMULACION_RL\\.venv\\Scripts\\python.exe 05_HARDWARE_Y_VARIANTES\\analisis_cobertura.py
Lee config_sim/variante_*.json y escribe cobertura/*.png y cobertura/tablas.md.

Supuestos (marcados en la salida): dron a H = 3.30 m, persona de pie de 1.72 m (cabeza = centro a 1.62 m, torso = centro a 1.25 m,
ESTIMADOS), cámaras en el CG del dron (sin desplazamiento), pitch táctico −45° donde el gimbal lo permite.
"""
import glob
import json
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "cobertura")
H = 3.30
CABEZA, TORSO, ESTATURA = 1.62, 1.25, 1.72
PANEL_ALTO = 2.25
D_MAX = 15.0


def cargar():
    v = {}
    for f in sorted(glob.glob(os.path.join(AQUI, "config_sim", "variante_*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        v[d["VARIANTE"]] = d
    return v


def camaras(v):
    """Lista de cámaras: nombre, pitch (° hacia abajo negativo), vfov, hfov, color, eje largo longitudinal."""
    fijo = v["GIMBAL_TIPO"] == "fijo"
    pitch = v["CAM_PRINCIPAL_PITCH_FIJO_DEG"] if fijo else max(v["GIMBAL_TOPE_FISICO_MIN"], -45.0)
    nom = "Principal " + ("CSI" if v["CAM_PRINCIPAL_TIPO"] == "csi" else "USB")
    cs = [dict(n=nom, gimbal=not fijo, p=pitch, vf=v["CAM_PRINCIPAL_VFOV"], hf=v["CAM_PRINCIPAL_HFOV"], c="tab:blue")]
    if v["CAM_PISO_ACTIVA"]:
        cs.append(dict(n="Piso CSI", p=v["CAM_PISO_PITCH"], vf=v["CAM_PISO_HFOV"], hf=v["CAM_PISO_VFOV"], c="tab:green"))
    if v["CAM_FRONTAL_ANCHA_ACTIVA"]:
        cs.append(dict(n="Frontal ancha CSI", p=v["CAM_FRONTAL_ANCHA_PITCH"], vf=v["CAM_FRONTAL_ANCHA_VFOV"],
                       hf=v["CAM_FRONTAL_ANCHA_HFOV"], c="tab:orange"))
    return cs


def ve(cam, d, z, libre=False):
    """¿La cámara (en el origen, a altura H) ve un punto a distancia horizontal d (hacia adelante) y altura z? Solo plano vertical.
    libre=True: el gimbal puede tomar cualquier pitch entre su tope bajo y +15° (solo la cámara principal); False: pitch fijo."""
    dz = H - z
    ang = math.degrees(math.atan2(-dz, d))  # elevación del punto vista desde la cámara (negativa = abajo)
    if libre and cam.get("gimbal"):
        return cam["p"] - cam["vf"] / 2 <= ang <= 15 + cam["vf"] / 2
    return abs(ang - cam["p"]) <= cam["vf"] / 2


def intervalos(cs, z, paso=0.01, libre=False):
    """Distancias en [0, D_MAX] donde alguna cámara ve el punto a altura z, como lista de (d0, d1)."""
    ds = np.arange(0, D_MAX + paso, paso)
    vis = np.array([any(ve(c, d, z, libre) for c in cs) for d in ds])
    out, ini = [], None
    for d, a in zip(ds, vis):
        if a and ini is None:
            ini = d
        if not a and ini is not None:
            out.append((round(ini, 2), round(d - paso, 2)))
            ini = None
    if ini is not None:
        out.append((round(ini, 2), D_MAX))
    return out


def txt(iv):
    return "; ".join(f"{a:.1f}–{b:.1f} m" if b < D_MAX else f"{a:.1f}–más de {D_MAX:.0f} m" for a, b in iv) or "no lo ve"


def sombra_panel(dp, z):
    """Distancia DETRÁS del panel hasta donde queda oculto un punto a altura z (línea desde la cámara que roza el borde del panel)."""
    return (PANEL_ALTO - z) * dp / (H - PANEL_ALTO)


def figura(k, v, cs):
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(10, 8.2), gridspec_kw={"height_ratios": [3.0, 1.3]})
    ax.set_title(f"Variante {k}: {v['NOMBRE']}", fontsize=11)
    for c in cs:
        a0, a1 = c["p"] - c["vf"] / 2, c["p"] + c["vf"] / 2
        pts = [(0, H)]
        for a in np.linspace(a0, a1, 40):
            t = math.tan(math.radians(a))
            x = D_MAX if abs(a) < 1e-6 or a > -1e-6 else min(D_MAX, H / -t)
            if a >= -1e-6:
                x = D_MAX
            y = H + t * x
            pts.append((x, max(y, 0)))
        ax.fill(*zip(*pts), color=c["color"] if "color" in c else c["c"], alpha=0.28, label=f"{c['n']} (pitch {c['p']:.0f}°, V {c['vf']:.1f}°)")
    ax.plot([0], [H], "ks", ms=8)
    ax.axhline(0, color="k", lw=1)
    for d in (2, 4, 6, 8, 10):                       # personas de pie de referencia
        ax.plot([d, d], [0, ESTATURA], color="gray", lw=2)
        ax.plot(d, ESTATURA, "o", color="gray", ms=5)
    dp = 4.5
    ax.plot([dp, dp], [0, PANEL_ALTO], color="saddlebrown", lw=5)
    ax.plot([dp, dp + sombra_panel(dp, 0)], [PANEL_ALTO, 0], "--", color="saddlebrown", lw=1)
    ax.text(dp + 0.1, PANEL_ALTO + 0.1, f"panel {PANEL_ALTO} m a {dp} m", color="saddlebrown", fontsize=8)
    ax.set_xlim(-1, D_MAX)
    ax.set_ylim(-0.3, H + 1.2)
    ax.set_xlabel("distancia horizontal al frente del dron (m)")
    ax.set_ylabel("altura (m)")
    ax.set_aspect("equal")
    ax.legend(loc="upper right", fontsize=8)
    # tiras de visibilidad: cabeza y torso, con el pitch táctico fijo y con el gimbal libre (entre su tope bajo y +15°)
    ds = np.arange(0, D_MAX, 0.05)
    filas = (("cabeza, pitch táctico fijo", CABEZA, False), ("cabeza, gimbal libre", CABEZA, True),
             ("torso, pitch táctico fijo", TORSO, False), ("torso, gimbal libre", TORSO, True))
    for fila, (nom, z, libre) in enumerate(filas):
        vis = np.array([[any(ve(c, d, z, libre) for c in cs)] for d in ds]).T
        ax2.imshow(vis, extent=[0, D_MAX, fila, fila + 0.8], aspect="auto", cmap="Greens", vmin=0, vmax=1.4, origin="lower")
        ax2.text(-0.2, fila + 0.4, nom, ha="right", va="center", fontsize=8)
    ax2.set_xlim(-1, D_MAX)
    ax2.set_ylim(0, 4)
    ax2.set_yticks([])
    ax2.set_xlabel("verde = la ve alguna cámara (solo el plano vertical; sin contar el campo horizontal)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, f"cobertura_variante_{k}.png"), dpi=110)
    plt.close(fig)


def main():
    os.makedirs(OUT, exist_ok=True)
    var = cargar()
    L = ["# Cobertura geométrica por variante (generado por `analisis_cobertura.py`)", "",
         f"Supuestos: dron a **{H} m**; persona de pie de **{ESTATURA} m** (cabeza = centro a {CABEZA} m y torso = centro a {TORSO} m: "
         "**estimados**); cámaras en el centro del dron; pitch táctico −45° donde el gimbal lo permite (A y B: −10°, el tope real de hoy); "
         "solo plano vertical (se ignora que el objetivo esté fuera del campo horizontal). Campos: USB HFOV 38.9° × VFOV 29.7° (medido); "
         "IMX219 62.2° × 48.8° (**nominal, sin medir**), con su lado largo a lo largo del vuelo.", "",
         "## Tabla de cobertura vertical (distancias horizontales a las que alguna cámara ve el punto)", "",
         "«Pitch fijo» = la cámara principal quieta en su pitch táctico. «Gimbal libre» = la cámara principal puede tomar cualquier pitch "
         "entre su tope bajo y +15° (lo que hace el seguimiento). La diferencia más importante entre variantes es **la distancia mínima**: "
         "con el tope bajo, A/B no ven la cabeza a menos de ~3.6 m y C-F sí desde ~1 m.", "",
         "| Var. | Cámaras | Cabeza: pitch fijo | Cabeza: gimbal libre | Torso: gimbal libre | Suelo: ciego hasta |", "|---|---|---|---|---|---|"]
    for k, v in var.items():
        cs = camaras(v)
        c0 = cs[0]
        ciego = ""
        # suelo (z=0): ciego = distancia mínima a la que alguna cámara ve el suelo
        iv0 = intervalos(cs, 0.0)
        ciego = f"{iv0[0][0]:.1f} m" if iv0 else "siempre"
        L.append(f"| **{k}** | " + " + ".join(f"{c['n']} ({c['p']:.0f}°)" for c in cs) + f" | {txt(intervalos(cs, CABEZA))} | {txt(intervalos(cs, CABEZA, libre=True))} | {txt(intervalos(cs, TORSO, libre=True))} | {ciego} |")
        figura(k, v, cs)
    L += ["", "## Cámara al piso: huella a 3.30 m", ""]
    for z, nom in ((0.0, "suelo"), (CABEZA, "cabeza"), (TORSO, "torso")):
        dz = H - z
        L.append(f"- A la altura del {nom}: ±{dz*math.tan(math.radians(31.1)):.2f} m a lo largo del vuelo y ±{dz*math.tan(math.radians(24.4)):.2f} m de lado "
                 f"(huella {2*dz*math.tan(math.radians(31.1)):.2f} × {2*dz*math.tan(math.radians(24.4)):.2f} m).")
    L += ["", "## Ancho lateral que ve la cámara principal (campo horizontal 38.9°)", ""]
    for p in (-45.0, -10.0):
        for z, nom in ((CABEZA, "cabeza"), (TORSO, "torso")):
            dz = H - z
            r = dz / math.sin(math.radians(abs(p)))
            L.append(f"- Pitch {p:.0f}°, mirando al {nom} en el eje: distancia en línea recta {r:.2f} m → ancho {2*r*math.tan(math.radians(19.45)):.2f} m.")
    L += ["", "## Mirar detrás de un panel de 2.25 m desde 3.30 m", "",
          "Línea de vista desde la cámara que roza el borde de arriba del panel: hasta qué distancia DETRÁS del panel queda oculto cada punto.", "",
          "| Postura (altura del punto) | Panel a 4 m | Panel a 5 m |", "|---|---|---|"]
    for nom, z in (("De pie, cabeza (1.62 m)", CABEZA), ("De pie, torso (1.25 m)", TORSO), ("Agachado (1.1 m)", 1.1), ("Gateando (0.6 m)", 0.6)):
        L.append(f"| {nom} | {sombra_panel(4, z):.1f} m | {sombra_panel(5, z):.1f} m |")
    L += ["", "Para ver a alguien oculto hay que acercarse o subir; subir ya está permitido solo sin personas a menos de 8 m (altura segura 3.30 m)."]
    open(os.path.join(OUT, "tablas.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    # figura del escenario del panel
    fig, ax = plt.subplots(figsize=(10, 4.6))
    for dp, col in ((4, "tab:purple"), (5, "tab:red")):
        ax.plot([dp, dp], [0, PANEL_ALTO], color=col, lw=5)
        ax.plot([0, dp + sombra_panel(dp, 0)], [H, 0], "--", color=col, lw=1)
        for nom, z in (("cabeza", CABEZA), ("agachado", 1.1), ("gateando", 0.6)):
            ax.plot(dp + sombra_panel(dp, z), z, "o", color=col)
    ax.plot([0], [H], "ks", ms=9)
    ax.axhline(0, color="k", lw=1)
    ax.set_xlim(-1, 18)
    ax.set_ylim(-0.3, H + 0.8)
    ax.set_aspect("equal")
    ax.set_title("Mirar detrás de un panel de 2.25 m desde 3.30 m (paneles a 4 m y a 5 m)")
    ax.set_xlabel("distancia horizontal (m)")
    ax.set_ylabel("altura (m)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "panel_sombra.png"), dpi=110)
    print("listo:", OUT)


if __name__ == "__main__":
    main()
