# Prueba: personaje de Quaternius con animaciones de la Universal Animation Library, sobre pasto, render con la RTX.
# Uso: blender --background --factory-startup --python prueba_render.py -- <recursos_quaternius> <salida.png>
import bpy, sys, math
R, SALIDA = sys.argv[sys.argv.index("--") + 1:]
UAL1 = R + "/universal-animation-library/Universal Animation Library[Standard]/Unreal-Godot/UAL1_Standard.glb"
PJ = R + "/universal-base-characters/Universal Base Characters[Standard]/Base Characters/Godot - UE/"
ARBOL = R + "/stylized-nature-megakit/glTF/CommonTree_1.gltf"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=UAL1)
for o in list(bpy.context.selected_objects):          # solo se quieren las acciones, no el maniquí
    bpy.data.objects.remove(o, do_unlink=True)

def persona(archivo, accion, x, y, giro, cuadro):
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=PJ + archivo)
    nuevos = [o for o in bpy.data.objects if o not in antes]
    arm = next(o for o in nuevos if o.type == "ARMATURE")
    arm.location = (x, y, 0); arm.rotation_euler[2] = giro
    arm.animation_data_create().action = bpy.data.actions[accion]
    if arm.animation_data.action_slot is None and bpy.data.actions[accion].slots:
        arm.animation_data.action_slot = bpy.data.actions[accion].slots[0]
    return arm

persona("Superhero_Male_FullBody.gltf", "Sprint_Loop", 0, 0, math.radians(90), 8)
persona("Superhero_Female_FullBody.gltf", "Crouch_Idle_Loop", 2.2, 1.5, math.radians(200), 1)
persona("Superhero_Male_FullBody.gltf", "Jump_Loop", -2.0, 1.2, math.radians(30), 5)
try:
    for k, (x, y) in enumerate([(-6, 8), (5, 9), (9, 4)]):
        antes = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=ARBOL)
        for o in bpy.data.objects:
            if o not in antes and o.parent is None: o.location = (x, y, 0)
except Exception as e:
    print("sin árbol:", e)

bpy.ops.mesh.primitive_plane_add(size=80)
pasto = bpy.data.materials.new("pasto"); pasto.use_nodes = True
pasto.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.13, 0.32, 0.08, 1)
pasto.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1
bpy.context.object.data.materials.append(pasto)
# panel en V de 90° (1.0 × 2.0 m)
for giro in (45, -45):
    bpy.ops.mesh.primitive_cube_add(size=1)
    p = bpy.context.object; p.scale = (1.0, 0.03, 2.0); p.rotation_euler[2] = math.radians(giro)
    p.location = (3.5 + 0.35 * math.copysign(1, giro), 3 + 0.35, 1.0)
bpy.ops.object.light_add(type="SUN"); sol = bpy.context.object
sol.data.energy = 4; sol.rotation_euler = (math.radians(50), 0, math.radians(35))
mundo = bpy.data.worlds.new("cielo"); mundo.use_nodes = True
mundo.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.7, 0.95, 1)
bpy.context.scene.world = mundo
bpy.ops.object.camera_add(location=(0.5, -7.5, 2.4), rotation=(math.radians(80), 0, math.radians(4)))
cam = bpy.context.object; cam.data.lens = 32
esc = bpy.context.scene
esc.camera = cam; esc.frame_set(8)
esc.render.engine = "CYCLES"; esc.cycles.device = "GPU"; esc.cycles.samples = 64; esc.cycles.use_denoising = True
pr = bpy.context.preferences.addons["cycles"].preferences; pr.compute_device_type = "OPTIX"; pr.get_devices()
for d in pr.devices: d.use = d.type == "OPTIX"
esc.render.resolution_x, esc.render.resolution_y = 1280, 720
esc.render.filepath = SALIDA
bpy.ops.render.render(write_still=True)
print("LISTO", SALIDA)
