# Exporta las personas vestidas de Quaternius (CC0) y sus animaciones redirigidas a GLB para el visor three.js (fase V2).
# Salida: <destino>/<Personaje>.glb (malla + esqueleto, sin animaciones) y <destino>/animaciones.glb (solo el esqueleto
# con una animación por pista; three.js las aplica a cualquier personaje porque los huesos se llaman igual).
#
# Uso: blender --background --factory-startup --python exportar_personas_glb.py -- <recursos_quaternius> <destino>
import bpy, sys, os
R, DEST = sys.argv[sys.argv.index("--") + 1:]
UMC = R + "/ultimate-modular-characters/glTF/"
PERSONAJES = ["Casual_Hoodie", "Worker", "Casual_2", "Suit", "Farmer"]
CLIPS = ["Idle_Loop", "Walk_Loop", "Jog_Fwd_Loop", "Sprint_Loop", "Crouch_Idle_Loop", "Crouch_Fwd_Loop",
         "Jump_Start", "Jump_Loop", "Jump_Land", "Roll", "Idle_TalkingPhone_Loop", "Idle_FoldArms_Loop", "LayToIdle", "Interact"]
os.makedirs(DEST, exist_ok=True)


def limpio():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def importar(nombre):
    bpy.ops.import_scene.gltf(filepath=UMC + nombre + ".gltf")
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    for pb in arm.pose.bones:                     # sin IK: las animaciones ya traen el giro de cada hueso
        for c in list(pb.constraints):
            pb.constraints.remove(c)
    if arm.animation_data:
        arm.animation_data.action = None
        for t in list(arm.animation_data.nla_tracks):
            arm.animation_data.nla_tracks.remove(t)
    for a in list(bpy.data.actions):
        bpy.data.actions.remove(a)
    for pb in arm.pose.bones:
        pb.matrix_basis.identity()
    return arm


def exportar(ruta, animar):
    bpy.ops.export_scene.gltf(filepath=ruta, export_format="GLB", export_animations=animar,
                              export_animation_mode="NLA_TRACKS", export_apply=False, export_yup=True)
    print("GLB", ruta, round(os.path.getsize(ruta) / 1e6, 2), "MB")


for nombre in PERSONAJES:
    limpio()
    importar(nombre)
    exportar(f"{DEST}/{nombre}.glb", False)

# animaciones: el esqueleto solo, con una pista NLA por animación
limpio()
arm = importar(PERSONAJES[0])
for o in list(bpy.data.objects):
    if o.type == "MESH":
        bpy.data.objects.remove(o, do_unlink=True)
for lib in ("animaciones_UMC_UAL1.blend", "animaciones_UMC_UAL2.blend"):
    with bpy.data.libraries.load(f"{R}/{lib}") as (src, dst):
        dst.actions = [a for a in src.actions if a[:-4] in CLIPS and a.endswith("_UMC")]
arm.animation_data_create()
vistos = set()
for a in sorted(bpy.data.actions, key=lambda x: x.name):
    clip = a.name.split("_UMC")[0]
    if clip in vistos or clip not in CLIPS:
        continue
    vistos.add(clip)
    pista = arm.animation_data.nla_tracks.new(); pista.name = clip
    s = pista.strips.new(clip, int(a.frame_range[0]), a)
    if a.slots:
        s.action_slot = a.slots[0]
print("CLIPS", sorted(vistos), "faltan", sorted(set(CLIPS) - vistos))
exportar(f"{DEST}/animaciones.glb", True)
