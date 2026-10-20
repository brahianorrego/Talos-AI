# -*- coding: utf-8 -*-
"""
El campus de la universidad en Unreal, desde la MISMA especificación que usa la estación web (entorno/entorno_u.json, que sale de las
fotos y las mediciones de Google Earth de Brahian). Se llama desde crear_cancha.py. Marco de la simulación: x este, y norte, metros;
Unreal: centímetros con Y a la derecha, por eso dronia_ue.ue() invierte y.

Árboles: mallas del complemento "PCG Biome Sample" de Epic (gratis, Nanite, de bajo detalle: provisionales hasta tener árboles de Fab).
Fachadas: texturas que genera entorno/fachadas.py (ladrillo con ventanas, una por pared).
"""
import json
import math
import os
import random

import unreal

import dronia_ue as D

AQUI = os.path.dirname(os.path.abspath(__file__))
ENTORNO = os.path.normpath(os.path.join(AQUI, "..", "entorno"))
TEX = D.CARPETA + "/Texturas"
M = D.M


def cargar():
    with open(os.path.join(ENTORNO, "entorno_u.json"), encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------------------------------------ materiales de las fachadas
def material_fachada():
    ruta = D.CARPETA + "/Materiales/M_Fachada"
    if D.biblioteca.does_asset_exist(ruta):
        return unreal.load_asset(ruta)
    mat = D.herramientas.create_asset("M_Fachada", D.CARPETA + "/Materiales", unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property("two_sided", True)
    t = D.mel.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -500, 0)
    t.set_editor_property("parameter_name", "Textura")
    r = D.mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -500, 250)
    r.set_editor_property("r", 0.92)
    D.mel.connect_material_property(t, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    D.mel.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS)
    D.mel.recompile_material(mat)
    D.biblioteca.save_loaded_asset(mat)
    return mat


def textura(nombre):
    """Importa entorno/texturas/<nombre>.png a /Game/DronIA/Texturas (una vez) y la devuelve."""
    ruta = f"{TEX}/{nombre}"
    if D.biblioteca.does_asset_exist(ruta):
        return unreal.load_asset(ruta)
    png = os.path.join(ENTORNO, "texturas", nombre + ".png")
    if not os.path.exists(png):
        unreal.log_warning("DRONIA: falta la textura " + png + " (correr entorno/fachadas.py)")
        return None
    t = unreal.AssetImportTask()
    for k, v in (("filename", png), ("destination_path", TEX), ("destination_name", nombre), ("automated", True), ("save", True), ("replace_existing", True)):
        t.set_editor_property(k, v)
    D.herramientas.import_asset_tasks([t])
    return unreal.load_asset(ruta)


def mat_fachada(nombre):
    ruta = D.CARPETA + "/Materiales/MI_F_" + nombre
    if D.biblioteca.does_asset_exist(ruta):
        return unreal.load_asset(ruta)
    t = textura(nombre)
    if t is None:
        return D.material("Ladrillo", (0.45, 0.14, 0.07), 0.9)
    mi = D.herramientas.create_asset("MI_F_" + nombre, D.CARPETA + "/Materiales", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    D.mel.set_material_instance_parent(mi, material_fachada())
    D.mel.set_material_instance_texture_parameter_value(mi, "Textura", t)
    D.biblioteca.save_loaded_asset(mi)
    return mi


# ------------------------------------------------------------------------------------------------ piezas
def linea(xa, ya, xb, yb, mat, z=0.035, ancho=0.12, carpeta="Entorno/Lineas", n="Linea"):
    L = math.hypot(xb - xa, yb - ya)
    D.caja(n, (xa + xb) / 2, (ya + yb) / 2, z, L + ancho, ancho, 0.01, mat, math.atan2(yb - ya, xb - xa), carpeta)


def rect_lineas(x0, y0, x1, y1, mat, **kw):
    linea(x0, y0, x1, y0, mat, **kw); linea(x1, y0, x1, y1, mat, **kw); linea(x1, y1, x0, y1, mat, **kw); linea(x0, y1, x0, y0, mat, **kw)


def campo(E):
    c, t, J = E["campo"]["centro"], E["campo"]["tam"], E["campo"]["juego"]
    cal = D.material("Cal", (0.85, 0.85, 0.82), 0.9)
    D.forma("Plane", "Cancha_futbol", D.ue(c[0], c[1], 0.02), (t[0], t[1], 1), D.material_cesped(), 0.0, "Entorno/Campo")
    cy = c[1]
    rect_lineas(-J["x"], J["y0"], J["x"], J["y1"], cal)
    linea(-J["x"], cy, J["x"], cy, cal)
    for k in range(72):                                                          # círculo central
        a0, a1 = 2 * math.pi * k / 72, 2 * math.pi * (k + 1) / 72
        linea(9.15 * math.cos(a0), cy + 9.15 * math.sin(a0), 9.15 * math.cos(a1), cy + 9.15 * math.sin(a1), cal, n="Circulo")
    for yl, d in ((J["y1"], -1), (J["y0"], 1)):                                  # áreas (d = hacia el centro)
        rect_lineas(-20.15, yl, 20.15, yl + d * 16.5, cal)
        rect_lineas(-9.16, yl, 9.16, yl + d * 5.5, cal)
        tubo = D.material("Arco", (0.92, 0.92, 0.92), 0.3, 0.2)
        for x in (-3.66, 3.66):
            D.forma("Cylinder", "Arco_poste", D.ue(x, yl, 1.22), (0.12, 0.12, 2.44), tubo, 0.0, "Entorno/Arcos")
        D.caja("Arco_travesano", 0, yl, 2.44, 0.12, 7.44, 0.12, tubo, 0.0, "Entorno/Arcos")
    # la zona de IA queda discreta en el piso (esquinas naranja) para que se vea dónde es la misión
    z = E["campo"]["zona_ia"] / 2
    naranja = D.material("ZonaIA", (0.85, 0.35, 0.02), 0.6)
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        linea(sx * z, sy * z, sx * z - sx * 3, sy * z, naranja, 0.04, 0.2, "Entorno/ZonaIA", "Esquina")
        linea(sx * z, sy * z, sx * z, sy * z - sy * 3, naranja, 0.04, 0.2, "Entorno/ZonaIA", "Esquina")


def canchas(E):
    cal = D.material("Cal", (0.85, 0.85, 0.82), 0.9)
    rojo = D.material("PisoRojo", (0.22, 0.045, 0.035), 0.8)
    verde = D.material("PisoVerde", (0.05, 0.14, 0.09), 0.8)
    for cn in E["canchas"]:
        cx, cy = cn["centro"]; w, h = cn["tam"]
        D.caja("Cancha_" + cn["nombre"], cx, cy, 0.02, w, h, 0.04, rojo, 0.0, "Entorno/Canchas")
        if cn["tipo"] == "tenis":
            cw, ch = 10.97, 23.77
            D.caja("Cancha_tenis_centro", cx, cy, 0.05, cw + 6, ch + 8, 0.02, verde, 0.0, "Entorno/Canchas")
            rect_lineas(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2, cal, z=0.07)
            rect_lineas(cx - cw / 2 + 1.37, cy - ch / 2, cx + cw / 2 - 1.37, cy + ch / 2, cal, z=0.07)
            linea(cx - cw / 2 + 1.37, cy + 6.4, cx + cw / 2 - 1.37, cy + 6.4, cal, 0.07)
            linea(cx - cw / 2 + 1.37, cy - 6.4, cx + cw / 2 - 1.37, cy - 6.4, cal, 0.07)
            linea(cx, cy - 6.4, cx, cy + 6.4, cal, 0.07)
            red = D.material_translucido("Red", (0.9, 0.9, 0.88), 0.45)
            D.caja("Red_tenis", cx, cy, 0.5, 12.8, 0.03, 0.9, red, 0.0, "Entorno/Canchas")
        else:
            D.caja("Cancha_multiple_centro", cx, cy, 0.05, w - 2, h - 3, 0.02, verde, 0.0, "Entorno/Canchas")
            rect_lineas(cx - w / 2 + 1, cy - h / 2 + 1.5, cx + w / 2 - 1, cy + h / 2 - 1.5, cal, z=0.07)
            linea(cx - w / 2 + 1, cy, cx + w / 2 - 1, cy, cal, 0.07)
            for k in range(36):
                a0, a1 = 2 * math.pi * k / 36, 2 * math.pi * (k + 1) / 36
                linea(cx + 3 * math.cos(a0), cy + 3 * math.sin(a0), cx + 3 * math.cos(a1), cy + 3 * math.sin(a1), cal, 0.07, n="Circulo")
            gris, blanco = D.material("Poste", (0.2, 0.21, 0.22), 0.5, 0.6), D.material("Tablero", (0.9, 0.92, 0.94), 0.4)
            for s in (-1, 1):
                D.forma("Cylinder", "Poste_baloncesto", D.ue(cx, cy + s * (h / 2 - 0.4), 1.5), (0.14, 0.14, 3.0), gris, 0.0, "Entorno/Canchas")
                D.caja("Tablero", cx, cy + s * (h / 2 - 1.0), 3.0, 1.8, 0.05, 1.05, blanco, 0.0, "Entorno/Canchas")


def vallas(E):
    malla = D.material_translucido("Malla", (0.02, 0.03, 0.03), 0.28)
    poste = D.material("PosteCerco", (0.12, 0.13, 0.14), 0.5, 0.5)
    muro = D.material("MuroOscuro", (0.045, 0.025, 0.02), 0.9)
    for v in E["vallas"]:
        pts = [tuple(p) for p in v["p"]] + ([tuple(v["p"][0])] if v["cerrado"] else [])
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            L, ang = math.hypot(bx - ax, by - ay), math.atan2(by - ay, bx - ax)
            if v["tipo"] == "malla":
                D.caja("Malla", (ax + bx) / 2, (ay + by) / 2, v["alto"] / 2, L, 0.03, v["alto"], malla, ang, "Entorno/Cercos")
                for d in range(0, int(L) + 1, 4):
                    D.forma("Cylinder", "Poste", D.ue(ax + math.cos(ang) * d, ay + math.sin(ang) * d, v["alto"] / 2), (0.1, 0.1, v["alto"]), poste, 0.0, "Entorno/Cercos")
            else:
                D.caja("Muro", (ax + bx) / 2, (ay + by) / 2, v["alto"] / 2, L, 0.35, v["alto"], muro, ang, "Entorno/Cercos")


def suelos(E):
    mats = {"asfalto": D.material("Asfalto", (0.03, 0.033, 0.036), 0.9), "via": D.material("Via", (0.03, 0.033, 0.036), 0.9), "adoquin": D.material("Adoquin", (0.28, 0.25, 0.21), 0.9)}
    amarillo = D.material("LineaAmarilla", (0.55, 0.38, 0.02), 0.6)
    for s in E["suelos"]:
        z = 0.04 if s["tipo"] == "adoquin" else 0.025
        D.caja("Suelo_" + s["nombre"], s["centro"][0], s["centro"][1], z / 2, s["tam"][0], s["tam"][1], z, mats[s["tipo"]], 0.0, "Entorno/Suelos")
        if s["nombre"] == "parqueadero":
            for f in range(4):
                for k in range(15):
                    x, y0 = s["centro"][0] - 24.5 + k * 3.6, s["centro"][1] - 11.3 + f * 5.6
                    D.caja("Puesto", x, y0 + 2.4, 0.04, 0.1, 4.8, 0.01, amarillo, 0.0, "Entorno/Suelos")
        elif s["tipo"] == "via":
            largo_x = s["tam"][0] > s["tam"][1]
            D.caja("Linea_via", s["centro"][0], s["centro"][1], 0.035, s["tam"][0] if largo_x else 0.15, 0.15 if largo_x else s["tam"][1], 0.01, amarillo, 0.0, "Entorno/Suelos")


def edificios(E):
    gris = D.material("TechoGris", (0.12, 0.125, 0.135), 0.7)
    claro = D.material("TechoClaro", (0.72, 0.74, 0.76), 0.7)
    oscuro = D.material("Cubierta", (0.045, 0.048, 0.052), 0.55)
    for b in E["edificios"]:
        cx, cy = b["centro"]; sx, sy = b["tam"]
        cuerpo = b["alto"] - 3.0 if b["tipo"] == "coliseo" else b["alto"]
        # cuatro paredes (planos con su textura) y el techo: las ventanas no se estiran porque cada pared tiene su imagen
        for lado, (px, py, ancho, yaw) in {"n": (cx, cy + sy / 2, sx, 0.0), "s": (cx, cy - sy / 2, sx, 0.0), "e": (cx + sx / 2, cy, sy, 90.0), "o": (cx - sx / 2, cy, sy, 90.0)}.items():
            m = mat_fachada(f"{b['nombre']}_{'ns' if lado in 'ns' else 'eo'}")
            D.forma("Plane", f"{b['nombre']}_{lado}", D.ue(px, py, cuerpo / 2), (ancho, cuerpo, 1), m, 0.0, "Entorno/Edificios", rot=(90.0, 0.0, -yaw))
        D.caja(b["nombre"] + "_techo", cx, cy, cuerpo + 0.15, sx, sy, 0.3, claro if b["tipo"] == "laboratorio" else gris, 0.0, "Entorno/Edificios")
        if b["tipo"] == "coliseo":
            D.caja("coliseo_cubierta", cx, cy, cuerpo + 1.5, sx + 1.6, sy + 1.6, 3.0, oscuro, 0.0, "Entorno/Edificios")
        if b["tipo"] == "caseta":
            D.caja("caseta_alero", cx, cy, cuerpo + 0.15, sx + 1.2, sy + 1.2, 0.25, D.material("Alero", (0.4, 0.4, 0.38), 0.8), 0.0, "Entorno/Edificios")


def arboles(E):
    """Los árboles de Sapling Tree Gen (importar_arboles.py: 6 especies con hojas y corteza, de 1 m de alto); si no están importados, los del complemento PCG."""
    r = random.Random(11)
    esp = {"frondoso": ["arce", "abedul", "alamo", "callistemon"], "cipres": ["pino", "abeto"]}
    cache = {}
    n = 0
    for a in E["arboles"]:
        nombre = r.choice(esp[a["tipo"]])
        if nombre not in cache:
            cache[nombre] = unreal.load_asset(D.CARPETA + "/Arboles/" + nombre)
        malla = cache[nombre]
        if malla is None:
            return arboles_pcg(E)
        ancho = a["alto"] * min(1.1, max(0.5, a["copa"] * 2 / (a["alto"] * 0.85)))
        b = D.actores.spawn_actor_from_class(unreal.StaticMeshActor, D.ue(a["p"][0], a["p"][1], 0), unreal.Rotator(0, 0, r.uniform(0, 360)))
        b.static_mesh_component.set_static_mesh(malla)
        b.set_actor_scale3d(unreal.Vector(ancho, ancho, a["alto"]))                      # la malla mide 1 m de alto (100 cm)
        b.set_actor_label(f"Arbol_{n}")
        b.set_folder_path("Entorno/Arboles")
        n += 1
    return n


def arboles_pcg(E):
    r = random.Random(11)
    mallas = {"frondoso": [("PCG_Tree_01", 9.6), ("PCG_Tree_02", 12.5)], "cipres": [("PCG_Pine_01", 16.0)]}
    cache = {}
    n = 0
    for a in E["arboles"]:
        nombre, h0 = r.choice(mallas[a["tipo"]])
        if nombre not in cache:
            cache[nombre] = unreal.load_asset("/PCGBiomeSample/Meshes/" + nombre)
        if cache[nombre] is None:
            continue
        s = a["alto"] / h0
        b = D.actores.spawn_actor_from_class(unreal.StaticMeshActor, D.ue(a["p"][0], a["p"][1], 0), unreal.Rotator(0, 0, r.uniform(0, 360)))
        b.static_mesh_component.set_static_mesh(cache[nombre])
        b.set_actor_scale3d(unreal.Vector(s, s, s))
        b.set_actor_label(f"Arbol_{n}")
        b.set_folder_path("Entorno/Arboles")
        n += 1
    return n


def carros(E):
    mats = {}
    for k, c in enumerate(E["carros"]):
        clave = tuple(c["color"])
        if clave not in mats:
            mats[clave] = D.material(f"Auto_{len(mats)}", clave, 0.3, 0.3)
        psi = math.radians(c["rot"])
        D.caja(f"Auto_{k}", c["p"][0], c["p"][1], 0.62, 4.3, 1.75, 0.75, mats[clave], psi, "Entorno/Autos")
        D.caja(f"Auto_{k}_cabina", c["p"][0] - 0.2 * math.cos(psi), c["p"][1] - 0.2 * math.sin(psi), 1.3, 2.2, 1.55, 0.62, D.material("Vidrio", (0.02, 0.03, 0.04), 0.1, 0.5), psi, "Entorno/Autos")


def cerros(E):
    verde = D.material("Cerro", (0.07, 0.125, 0.05), 1.0)
    for h in E["cerros"]:
        D.forma("Sphere", "Cerro", D.ue(h["centro"][0], h["centro"][1], -h["alto"] * 0.12), (2 * h["radio"][0], 2 * h["radio"][1], 2 * h["alto"]), verde, 0.0, "Entorno/Cerros")


def extras(E):
    for x in E["extras"]:
        px, py = x["p"]; yaw = -x["rot"]
        D.caja("Motor_losa", px, py, 0.06, 5.5, 3.2, 0.12, D.material("Concreto", (0.28, 0.285, 0.27), 0.9), math.radians(x["rot"]), "Entorno/Extras")
        D.caja("Motor_base", px, py, 0.45, 3.4, 1.3, 0.14, D.material("Estructura", (0.65, 0.42, 0.02), 0.5), math.radians(x["rot"]), "Entorno/Extras")
        D.forma("Cylinder", "Motor_carcasa", D.ue(px, py, 1.1), (1.24, 1.24, 3.2), D.material("MotorNegro", (0.012, 0.015, 0.02), 0.4, 0.6), 0.0, "Entorno/Extras", rot=(0.0, 90.0, yaw))
        D.forma("Cylinder", "Motor_turbina", D.ue(px - 1.75 * math.cos(math.radians(x["rot"])), py - 1.75 * math.sin(math.radians(x["rot"])), 1.1), (1.32, 1.32, 0.5),
                D.material("MotorRojo", (0.45, 0.02, 0.02), 0.4), 0.0, "Entorno/Extras", rot=(0.0, 90.0, yaw))


def construir():
    E = cargar()
    D.cielo_y_luz()
    cerros(E)
    D.forma("Plane", "Terreno", D.ue(0, 0, 0.0), (6000, 6000, 1), D.material("Terreno", (0.07, 0.12, 0.04), 1.0), 0.0, "Entorno/Campo")
    campo(E); canchas(E); suelos(E); vallas(E); edificios(E); carros(E); extras(E)
    n = arboles(E)
    unreal.log(f"DRONIA: entorno de la universidad: {len(E['edificios'])} edificios, {n} árboles, {len(E['carros'])} autos, {len(E['cerros'])} cerros")
    return E
