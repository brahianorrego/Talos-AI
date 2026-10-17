# Prueba: personas vestidas (Ultimate Modular Characters) con animaciones redirigidas por redirigir_animaciones.py.
# Uso: blender --background --factory-startup --python prueba_vestidos.py -- <recursos_quaternius> <acciones.blend> <salida.png>
import bpy, sys, math
R, BLEND, SALIDA = sys.argv[sys.argv.index("--") + 1:]
UMC = R + "/ultimate-modular-characters/glTF/"
ARBOL = R + "/stylized-nature-megakit/glTF/CommonTree_1.gltf"

bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(BLEND) as (origen, destino):
    destino.actions = list(origen.actions)


def persona(archivo, accion, x, y, giro, cuadro):
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=UMC + archivo)
    arm = next(o for o in bpy.data.objects if o not in antes and o.type == "ARMATURE")
    for pb in arm.pose.bones:
        for c in pb.constraints:
            c.mute = True
    arm.location = (x, y, 0); arm.rotation_euler[2] = giro
    a = bpy.data.actions[accion + "_UMC"]
    arm.animation_data_create().action = a
    if a.slots:
        arm.animation_data.action_slot = a.slots[0]
    # cada persona en su propio cuadro de la animación
    arm.animation_data.action_extrapolation = "HOLD"
    for fc in getattr(a, "fcurves", []):
        pass
    arm["cuadro"] = cuadro
    return arm


gente = [persona("Casual_Hoodie.gltf", "Sprint_Loop", 0, 0, math.radians(90), 6),
         persona("Worker.gltf", "Crouch_Idle_Loop", 2.4, 1.6, math.radians(200), 10),
         persona("Suit.gltf", "Jump_Loop", -2.2, 1.4, math.radians(30), 20)]
for k, (x, y) in enumerate([(-6, 8), (5, 9), (9, 4)]):
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=ARBOL)
    for o in bpy.data.objects:
        if o not in antes and o.parent is None:
            o.location = (x, y, 0)
bpy.ops.mesh.primitive_plane_add(size=80)
pasto = bpy.data.materials.new("pasto"); pasto.use_nodes = True
pasto.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.13, 0.32, 0.08, 1)
pasto.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1
bpy.context.object.data.materials.append(pasto)
for giro in (45, -45):                          # V de 90° (alas de 1.0 m, 2.0 m de alto)
    bpy.ops.mesh.primitive_cube_add(size=1)
    p = bpy.context.object; p.scale = (1.0, 0.03, 2.0); p.rotation_euler[2] = math.radians(giro)
    p.location = (3.5 + 0.35 * math.copysign(1, giro), 3.35, 1.0)
bpy.ops.object.light_add(type="SUN"); sol = bpy.context.object
sol.data.energy = 4; sol.rotation_euler = (math.radians(50), 0, math.radians(35))
mundo = bpy.data.worlds.new("cielo"); mundo.use_nodes = True
mundo.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.7, 0.95, 1)
esc = bpy.context.scene
esc.world = mundo
bpy.ops.object.camera_add(location=(0.5, -7.5, 2.4), rotation=(math.radians(80), 0, math.radians(4)))
cam = bpy.context.object; cam.data.lens = 32; esc.camera = cam
# un solo cuadro de la escena: cada persona con el cuadro de su animación (desplazando la acción con una tira NLA)
for arm in gente:
    ad = arm.animation_data; a = ad.action; ad.action = None
    t = ad.nla_tracks.new(); tira = t.strips.new(a.name, 1, a)
    if a.slots:
        tira.action_slot = a.slots[0]
    tira.frame_start = 1 - arm["cuadro"] + a.frame_range[0]
esc.frame_set(1)
esc.render.engine = "CYCLES"; esc.cycles.device = "GPU"; esc.cycles.samples = 64; esc.cycles.use_denoising = True
pr = bpy.context.preferences.addons["cycles"].preferences; pr.compute_device_type = "OPTIX"; pr.get_devices()
for d in pr.devices:
    d.use = d.type == "OPTIX"
esc.render.resolution_x, esc.render.resolution_y = 1280, 720
esc.render.filepath = SALIDA
bpy.ops.render.render(write_still=True)
print("LISTO", SALIDA)
