import bpy, sys
for f in sys.argv[sys.argv.index("--") + 1:]:
    antes = set(bpy.data.actions)
    bpy.ops.import_scene.gltf(filepath=f)
    nuevas = sorted(a.name for a in bpy.data.actions if a not in antes)
    print("ARCH", f.split("/")[-1], len(nuevas))
    print("ANIM", " | ".join(nuevas))
arm = [o for o in bpy.data.objects if o.type == "ARMATURE"]
print("ARMAS", [(a.name, len(a.data.bones)) for a in arm])
