# -*- coding: utf-8 -*-
"""Compara los huesos de Manny, Survival y Quantum y mira si Skeleton ofrece 'compatible skeletons'. Salida: _cache/esqueletos.txt"""
import os
import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
out = []
mallas = {"manny": "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple", "survival": "/Game/Survival_Character/Meshes/Modular_Parts/SK_Survival_Character_Body",
          "quantum": "/Game/QuantumCharacter/Mesh/SKM_QuantumCharacter", "mh_body": "/MetaHumanCharacter/Body/IdentityTemplate/SKM_Body"}
huesos = {}
for k, p in mallas.items():
    m = unreal.load_asset(p)
    if not m:
        out.append("%s: no existe" % k)
        continue
    sk = m.get_editor_property("skeleton")
    nombres = [str(n) for n in unreal.AnimationLibrary.get_skeleton_bone_names(sk)] if hasattr(unreal.AnimationLibrary, "get_skeleton_bone_names") else []
    if not nombres:
        try:
            nombres = [str(n) for n in unreal.SkeletalMeshLibrary.get_bone_names(m)] if hasattr(unreal, "SkeletalMeshLibrary") else []
        except Exception as e:  # noqa: BLE001
            out.append("ERR huesos %s %r" % (k, e))
    huesos[k] = nombres
    out.append("%s: esqueleto=%s huesos=%d bounds=%s" % (k, sk.get_path_name(), len(nombres), m.get_bounds().box_extent))
if "manny" in huesos:
    base = set(huesos["manny"])
    for k, v in huesos.items():
        out.append("%s comparte con manny: %d de %d; faltan en %s: %s" % (k, len(base & set(v)), len(v), k, sorted(base - set(v))[:10]))
sk = unreal.load_asset(mallas["survival"]).get_editor_property("skeleton")
out.append("métodos de Skeleton con 'compat': %s" % [m for m in dir(sk) if "compat" in m.lower()])
out.append("métodos AnimationLibrary con 'skeleton|retarget|compat': %s" % [m for m in dir(unreal.AnimationLibrary) if any(w in m.lower() for w in ("skeleton", "retarget", "compat"))])
with open(os.path.join(AQUI, "_cache", "esqueletos.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
