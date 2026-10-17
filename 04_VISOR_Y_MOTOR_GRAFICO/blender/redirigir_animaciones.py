# Pasa animaciones de la Universal Animation Library (esqueleto tipo Unreal, 65 huesos) a los personajes vestidos de
# Ultimate Modular Characters (esqueleto propio de 62 huesos con IK en las piernas). Todo de Quaternius, CC0.
# Método: para cada hueso, giro en el mundo = giro de la fuente × (diferencia entre las dos poses de referencia).
# Referencia de la fuente: la acción "A_TPose" (cuadro 0); de destino: su pose de reposo.
#
# Uso: blender --background --factory-startup --python redirigir_animaciones.py -- <personaje.gltf> <UAL.glb> <salida.blend> [acción...]
import bpy, sys
from mathutils import Matrix

args = sys.argv[sys.argv.index("--") + 1:]
PJ, UAL, SALIDA, ACCIONES = args[0], args[1], args[2], args[3:]

MAPA = {"Body": "pelvis", "Abdomen": "spine_01", "Torso": "spine_02", "Chest": "spine_03", "Neck": "neck_01", "Head": "Head"}
for l, s in (("L", "l"), ("R", "r")):
    MAPA.update({f"Shoulder.{l}": f"clavicle_{s}", f"UpperArm.{l}": f"upperarm_{s}", f"LowerArm.{l}": f"lowerarm_{s}",
                 f"Wrist.{l}": f"hand_{s}", f"UpperLeg.{l}": f"thigh_{s}", f"LowerLeg.{l}": f"calf_{s}", f"Foot.{l}": f"foot_{s}"})
    for dedo, d in (("Index", "index"), ("Middle", "middle"), ("Ring", "ring"), ("Pinky", "pinky"), ("Thumb", "thumb")):
        for k in (1, 2, 3):
            MAPA[f"{dedo}{k}.{l}"] = f"{d}_0{k}_{s}"


def importar(f):
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=f)
    return next(o for o in bpy.data.objects if o not in antes and o.type == "ARMATURE")


bpy.ops.wm.read_factory_settings(use_empty=True)
dst = importar(PJ)
src = importar(UAL)
for pb in dst.pose.bones:                      # sin IK: cada hueso recibe su giro directo
    for c in pb.constraints:
        c.mute = True
if dst.animation_data:
    dst.animation_data.action = None
ACCIONES = ACCIONES or [a.name for a in bpy.data.actions if a.name.endswith(("_Loop", "_Start", "_Land")) or a.name in ("Roll", "Interact", "LayToIdle")]
vl = bpy.context.view_layer


def rot(m):
    return m.to_3x3().normalized().to_4x4()


def poner(accion, cuadro):
    src.animation_data.action = bpy.data.actions[accion]
    sl = bpy.data.actions[accion].slots
    if sl:
        src.animation_data.action_slot = sl[0]
    bpy.context.scene.frame_set(cuadro)


# poses de referencia: fuente en "A_TPose", destino en reposo
src.animation_data_create()
poner("A_TPose", 0)
ref_src = {b.name: rot(src.matrix_world @ b.matrix) for b in src.pose.bones}
ref_dst = {b.name: rot(dst.matrix_world @ b.bone.matrix_local) for b in dst.pose.bones}
off = {d: ref_src[s].inverted() @ ref_dst[d] for d, s in MAPA.items() if s in ref_src and d in ref_dst}
alto_src = (src.matrix_world @ src.pose.bones["pelvis"].head).z
alto_dst = (dst.matrix_world @ dst.pose.bones["Body"].bone.head_local).z
escala = alto_dst / max(alto_src, 1e-6)
orden = [b.name for b in dst.pose.bones if b.name in off]            # los padres van antes que los hijos

for nombre in ACCIONES:
    if nombre not in bpy.data.actions:
        print("FALTA", nombre)
        continue
    a = bpy.data.actions[nombre]
    f0, f1 = (int(x) for x in a.frame_range)
    nueva = bpy.data.actions.new(nombre + "_UMC")
    nueva.use_fake_user = True
    dst.animation_data_create().action = nueva
    for pb in dst.pose.bones:
        pb.matrix_basis = Matrix()
    for f in range(f0, f1 + 1):
        poner(nombre, f)
        for d in orden:
            pb, sb = dst.pose.bones[d], src.pose.bones[MAPA[d]]
            m = rot(src.matrix_world @ sb.matrix) @ off[d]
            if d in ("Body", "Foot.L", "Foot.R"):     # estos se mueven en el espacio: también la posición
                p = (src.matrix_world @ sb.head) * escala
            else:
                p = (dst.matrix_world @ pb.matrix).to_translation()
            m.translation = p
            pb.matrix = dst.matrix_world.inverted() @ m
            vl.update()
            pb.keyframe_insert("rotation_quaternion", frame=f)
            if d in ("Body", "Foot.L", "Foot.R"):
                pb.keyframe_insert("location", frame=f)
    print("OK", nombre, f1 - f0 + 1, "cuadros")

for o in list(bpy.data.objects):                  # en el archivo quedan solo las acciones nuevas
    bpy.data.objects.remove(o, do_unlink=True)
for a in list(bpy.data.actions):
    if not a.name.endswith("_UMC"):
        bpy.data.actions.remove(a)
bpy.ops.wm.save_as_mainfile(filepath=SALIDA)
print("GUARDADO", SALIDA, len(bpy.data.actions), "acciones")
