# -*- coding: utf-8 -*-
"""
Construye en Blender el dron real desde dron_real.json (ver dron_real.py) y, ejecutado como script, saca 3 vistas de prueba.
  blender --background --factory-startup --python dron_blender.py -- <carpeta_de_salida>
Desde otro script de Blender:  sys.path.insert(0, ".../modelo_dron"); import dron_blender; raiz = dron_blender.construir()
"""
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

AQUI = os.path.dirname(os.path.abspath(__file__))


def _material(nombre, color, translucido=False, cache={}):
    if nombre in cache:
        return cache[nombre]
    m = bpy.data.materials.new("dron_" + nombre)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Roughness"].default_value = 0.25 if nombre in ("carbono", "rojo", "espuma") else 0.5
    if nombre in ("dorado",):
        b.inputs["Metallic"].default_value = 0.9
    if translucido:
        b.inputs["Alpha"].default_value = 0.22
        b.inputs["Roughness"].default_value = 0.05
    cache[nombre] = m
    return m


def construir(nombre="dron", modelo=None):
    """Crea todas las piezas y las cuelga de un objeto vacío (la raíz). Devuelve la raíz."""
    if modelo is None:
        with open(os.path.join(AQUI, "dron_real.json"), encoding="utf-8") as f:
            modelo = json.load(f)
    raiz = bpy.data.objects.new(nombre, None)
    bpy.context.scene.collection.objects.link(raiz)
    for p in modelo["piezas"]:
        x, y, z = p["centro"]
        yaw, incl = math.radians(p.get("yaw", 0.0)), math.radians(p.get("inclinacion", 0.0))
        if p["forma"] == "caja":
            bpy.ops.mesh.primitive_cube_add(size=1)
            o = bpy.context.object
            o.scale = tuple(p["tam"])
            giro = Matrix.Rotation(yaw, 3, "Z")
        else:
            d, h = p["tam"]
            bpy.ops.mesh.primitive_cylinder_add(radius=d / 2, depth=h, vertices=24)
            o = bpy.context.object
            eje = p.get("eje", "z")
            base = Matrix.Rotation(math.pi / 2, 3, "Y") if eje == "x" else (Matrix.Rotation(math.pi / 2, 3, "X") if eje == "y" else Matrix.Identity(3))
            giro = Matrix.Rotation(yaw, 3, "Z") @ Matrix.Rotation(incl, 3, "X") @ base
        o.rotation_euler = giro.to_euler()
        o.location = (x, y, z)
        o.name = p["nombre"]
        o.data.materials.append(_material(p["color"], modelo["colores"][p["color"]], p.get("translucido", False)))
        if p.get("translucido"):
            try:
                o.data.materials[0].surface_render_method = "BLENDED"
            except Exception:
                pass
        o.parent = raiz
    return raiz


def _vistas(salida):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    esc = bpy.context.scene
    construir()
    bpy.ops.mesh.primitive_plane_add(size=6)
    piso = bpy.context.object
    piso.location.z = -0.265
    m = bpy.data.materials.new("piso"); m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.35, 0.37, 0.4, 1)
    piso.data.materials.append(m)
    bpy.ops.object.light_add(type="AREA", location=(1.2, -1.6, 2.4)); l = bpy.context.object
    l.data.energy = 220; l.data.size = 2.5; l.rotation_euler = (math.radians(35), 0, math.radians(35))
    bpy.ops.object.light_add(type="AREA", location=(-1.5, 1.2, 1.4)); l2 = bpy.context.object
    l2.data.energy = 90; l2.data.size = 2.0; l2.rotation_euler = (math.radians(55), 0, math.radians(-125))
    w = bpy.data.worlds.new("w"); w.use_nodes = True; esc.world = w
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.75, 0.8, 0.85, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.7
    bpy.ops.object.camera_add(); cam = bpy.context.object; esc.camera = cam; cam.data.lens = 45
    esc.render.engine = "CYCLES"; esc.cycles.device = "GPU"; esc.cycles.samples = 48; esc.cycles.use_denoising = True
    pr = bpy.context.preferences.addons["cycles"].preferences; pr.compute_device_type = "OPTIX"; pr.get_devices()
    for d in pr.devices:
        d.use = d.type == "OPTIX"
    esc.render.resolution_x, esc.render.resolution_y = 1200, 900
    # tres vistas: 3/4 delantera, de lado y desde arriba (el dron mira a +x)
    for nombre, pos, mira in (("tres_cuartos", (1.05, -0.95, 0.55), (0.0, 0.0, -0.05)), ("lado", (0.0, -1.6, -0.02), (0.0, 0.0, -0.02)),
                              ("arriba", (0.001, -0.001, 1.55), (0.0, 0.0, 0.0))):
        cam.location = pos
        d = (-pos[0] + mira[0], -pos[1] + mira[1], -pos[2] + mira[2])
        cam.rotation_euler = (Vector(mira) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
        esc.render.filepath = os.path.join(salida, f"dron_real_{nombre}.png")
        bpy.ops.render.render(write_still=True)
        print("VISTA", esc.render.filepath)


if __name__ == "__main__":
    _vistas(sys.argv[sys.argv.index("--") + 1])
