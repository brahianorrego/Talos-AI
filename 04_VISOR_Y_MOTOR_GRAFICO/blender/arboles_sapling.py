# -*- coding: utf-8 -*-
"""
Genera los ARBOLES del campus con la extension oficial "Sapling Tree Gen" de Blender (se instala una vez con instalar_sapling.py; sin cuentas), con hojas
(tarjetas con textura de hoja y transparencia) y corteza, de bajo poligonaje para que la estacion web los muestre en tiempo real, y los exporta:
    arboles/<nombre>.glb   (para la estacion web: three.js)         arboles/<nombre>.fbx + .png   (para Unreal)
Cada arbol queda de 1 m de alto con la base en el origen: los programas lo escalan al alto de cada arbol del campus.
    blender --background --factory-startup --python arboles_sapling.py -- <carpeta_de_salida> [vista.png]
Las formas salen de los presets de la extension (arce pequeno, abedul, alamo temblon, callistemon, pino pequeno, abeto de Douglas).
"""
import ast
import math
import os
import sys

import bpy
import numpy as np

SALIDA = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "arboles")
VISTA = sys.argv[sys.argv.index("--") + 2] if "--" in sys.argv and len(sys.argv) > sys.argv.index("--") + 2 else None
os.makedirs(SALIDA, exist_ok=True)

# (nombre, preset, tipo, ajustes sobre el preset para dejarlo LIVIANO (pocos miles de triangulos), color de la hoja)
BAJO = dict(bevelRes=0, resU=2)
ESPECIES = [("arce", "small_maple", "frondoso", dict(BAJO, levels=2, branches=(0, 34, 10, 0), curveRes=(6, 4, 3, 1), leaves=22, leafScale=1.15), (0.20, 0.42, 0.12)),
            ("abedul", "white_birch", "frondoso", dict(BAJO, levels=2, branches=(0, 30, 12, 0), curveRes=(8, 5, 3, 1), leaves=20, leafScale=1.0), (0.38, 0.55, 0.16)),
            ("alamo", "quaking_aspen", "frondoso", dict(BAJO, leaves=34, leafScale=0.95), (0.26, 0.48, 0.14)),
            ("callistemon", "callistemon", "frondoso", dict(BAJO, curveRes=(5, 3, 2, 1), leaves=40, leafScale=1.25), (0.22, 0.40, 0.15)),
            ("pino", "small_pine", "cipres", dict(BAJO, levels=2, branches=(0, 40, 6, 0), curveRes=(4, 3, 2, 1), leaves=60, leafScale=0.9), (0.07, 0.22, 0.10)),
            ("abeto", "douglas_fir", "cipres", dict(BAJO, levels=2, branches=(0, 50, 8, 0), curveRes=(8, 4, 2, 1), leaves=40, leafScale=0.8), (0.08, 0.26, 0.11))]


def presets_dir():
    for ext in bpy.utils.user_resource("EXTENSIONS"), os.path.join(os.path.dirname(bpy.utils.user_resource("CONFIG")), "extensions"):
        p = os.path.join(ext, "blender_org", "sapling_tree_gen", "presets")
        if os.path.isdir(p):
            return p
    raise RuntimeError("Falta la extension Sapling Tree Gen: correr instalar_sapling.py")


def imagen_hoja(nombre, rgb, rect=False):
    """Textura RGBA de una hoja (elipse puntiaguda con nervadura) o, si rect, de una ramita de agujas."""
    n = 128
    img = bpy.data.images.new(nombre, n, n, alpha=True)
    y, x = np.mgrid[0:n, 0:n].astype(float) / (n - 1)
    rng = np.random.default_rng(abs(hash(nombre)) % 2 ** 32)
    if rect:                                                       # ramita: tallo central y agujas finas a los lados
        a = np.zeros((n, n))
        for k in range(2, 30):
            yy = k / 30
            for lado in (-1, 1):
                for t in np.linspace(0, 1, 18):
                    xx, y2 = 0.5 + lado * 0.42 * t, yy + 0.05 * t
                    i, j = int(np.clip(y2, 0, 1) * (n - 1)), int(np.clip(xx, 0, 1) * (n - 1))
                    a[max(i - 1, 0):i + 2, max(j - 1, 0):j + 2] = 1
        a[:, n // 2 - 1:n // 2 + 2] = 1
    else:
        u, v = (x - 0.5) * 2, (y - 0.5) * 2
        a = ((np.abs(u) ** 1.7 / 0.82 ** 1.7 + np.abs(v) ** 2.2) < 1.0).astype(float)          # hoja ovalada
        a *= (1 - 0.35 * np.clip(v, 0, 1) ** 3) > 0                                              # punta
    nerv = np.abs(x - 0.5) < 0.012
    base = np.array(rgb)[None, None, :] * (0.75 + 0.5 * rng.random((n, n, 1)) * 0.5)
    base = np.where(nerv[..., None], np.array(rgb) * 1.35, base)
    px = np.concatenate([np.clip(base, 0, 1), a[..., None]], axis=2)
    img.pixels.foreach_set(px.ravel().tolist() if False else px.astype(np.float32).ravel())
    img.pack()
    return img


def imagen_corteza(nombre="corteza"):
    n = 128
    img = bpy.data.images.new(nombre, n, n)
    rng = np.random.default_rng(7)
    v = rng.random((n, 1)) * 0.5 + rng.random((n, n)) * 0.5
    v = np.cumsum(v, axis=0) % 1.0 * 0.5 + 0.5 * rng.random((n, n))
    c = np.stack([0.20 + 0.18 * v, 0.14 + 0.12 * v, 0.09 + 0.08 * v, np.ones_like(v)], axis=2)
    img.pixels.foreach_set(c.astype(np.float32).ravel())
    img.pack()
    return img


def material(nombre, imagen, hoja):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = imagen
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.85
    if hoja:
        nt.links.new(t.outputs["Alpha"], b.inputs["Alpha"])
        try:
            m.surface_render_method = "BLENDED"
        except Exception:                                          # noqa: BLE001
            pass
        m.blend_method = "HASHED" if hasattr(m, "blend_method") else None
    return m


def borrar_todo():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)


def generar(nombre, preset, tipo, ajustes, color, corteza, limpiar=True):
    if limpiar:
        borrar_todo()
    ruta = os.path.join(presets_dir(), preset + ".py")
    txt = open(ruta, encoding="utf-8").read()
    p = ast.literal_eval(txt[txt.index("{"):])
    validos = set(bpy.ops.curve.tree_add.get_rna_type().properties.keys())
    p = {k: v for k, v in p.items() if k in validos}
    p["showLeaves"] = True
    p["makeMesh"] = False
    p["bevel"] = True
    p["seed"] = {"arce": 3, "abedul": 11, "alamo": 5, "callistemon": 8, "pino": 2, "abeto": 4}[nombre]
    p.update({k: v for k, v in ajustes.items() if k in validos})
    antes = {o.name for o in bpy.data.objects}
    bpy.ops.curve.tree_add(**p)
    nuevos = [o for o in bpy.data.objects if o.name not in antes]
    rama = next(o for o in nuevos if o.name.startswith("tree"))
    hoja = next((o for o in nuevos if o.name.startswith("leaves")), None)
    bpy.context.view_layer.objects.active = rama
    rama.select_set(True)
    bpy.ops.object.convert(target="MESH")
    rama = bpy.context.view_layer.objects.active
    if hoja is not None and hoja.parent is not None:                   # las hojas cuelgan del árbol: se sueltan (conservando su lugar) para no escalarlas dos veces
        mw = hoja.matrix_world.copy()
        hoja.parent = None
        hoja.matrix_world = mw
    rama.data.materials.clear()
    rama.data.materials.append(material("corteza_" + nombre, corteza, False))
    objs = [rama]
    if hoja is not None:
        hoja.data.materials.clear()
        hoja.data.materials.append(material("hojas_" + nombre, imagen_hoja("hoja_" + nombre, color, tipo == "cipres"), True))
        objs.append(hoja)
    # tamano 1 m de alto, base en el origen
    zs = [(o.matrix_world @ v.co).z for o in objs for v in o.data.vertices]
    h = max(zs) - min(zs)
    for o in objs:
        o.scale = (1 / h,) * 3
        o.location.z -= min(zs) / h
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    tris = sum(len(o.data.polygons) * (2 if o.data.polygons and len(o.data.polygons[0].vertices) == 4 else 1) for o in objs)
    return objs, tris


def exportar(nombre, objs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(SALIDA, nombre + ".glb"), export_format="GLB", use_selection=True, export_apply=True)
    bpy.ops.export_scene.fbx(filepath=os.path.join(SALIDA, nombre + ".fbx"), use_selection=True, path_mode="COPY", embed_textures=True, axis_forward="-Y", axis_up="Z",
                             global_scale=1.0)


def main():
    bpy.ops.preferences.addon_enable(module="bl_ext.blender_org.sapling_tree_gen")        # la extension instalada por instalar_sapling.py
    corteza = imagen_corteza()
    info = []
    posiciones = []
    for k, (nombre, preset, tipo, ajustes, color) in enumerate(ESPECIES):
        objs, tris = generar(nombre, preset, tipo, ajustes, color, corteza)
        exportar(nombre, objs)
        os.makedirs(os.path.join(SALIDA, "tex"), exist_ok=True)                          # las texturas sueltas, para Unreal
        for im, nom in ((bpy.data.images.get("hoja_" + nombre), f"hoja_{nombre}.png"), (corteza, "corteza.png")):
            if im is not None:
                im.filepath_raw = os.path.join(SALIDA, "tex", nom)
                im.file_format = "PNG"
                im.save()
        info.append((nombre, tris))
        print("ARBOL", nombre, tris, "triangulos")
    if VISTA:                                                         # vista previa: todas las especies en fila
        borrar_todo()
        esc = bpy.context.scene
        for k, (nombre, preset, tipo, ajustes, color) in enumerate(ESPECIES):          # se vuelven a importar los .glb: así también se comprueba lo exportado
            antes = {o.name for o in bpy.data.objects}
            bpy.ops.import_scene.gltf(filepath=os.path.join(SALIDA, nombre + ".glb"))
            for o in [o for o in bpy.data.objects if o.name not in antes and o.parent is None]:
                o.scale = (10.0 if tipo == "frondoso" else 12.0,) * 3
                o.location.x = k * 8.0
        esc.render.engine = "BLENDER_EEVEE"
        bpy.ops.mesh.primitive_plane_add(size=120, location=(20, 0, 0))
        bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), 0, math.radians(30))); bpy.context.object.data.energy = 4
        bpy.ops.object.camera_add(location=(20, -62, 7), rotation=(math.radians(84), 0, 0)); esc.camera = bpy.context.object
        w = bpy.data.worlds.new("w"); w.use_nodes = True; esc.world = w
        w.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.72, 0.85, 1)
        esc.render.resolution_x, esc.render.resolution_y = 1800, 600
        esc.render.filepath = VISTA
        bpy.ops.render.render(write_still=True)
    print("LISTO", info)


main()
