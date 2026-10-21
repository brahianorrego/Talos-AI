# -*- coding: utf-8 -*-
"""Inventario de QuantumCharacter y Survival_Character: mallas, esqueletos, animaciones, blueprints. Salida: _cache/personajes_inv.txt"""
import collections
import os
import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
reg = unreal.AssetRegistryHelpers.get_asset_registry()
out = []
for raiz in ("/Game/QuantumCharacter", "/Game/Survival_Character"):
    cnt = collections.Counter()
    for a in reg.get_assets_by_path(raiz, recursive=True):
        c = str(a.asset_class_path.asset_name)
        cnt[c] += 1
        if c in ("SkeletalMesh", "Skeleton", "AnimSequence", "Blueprint", "AnimBlueprint", "IKRigDefinition", "IKRetargeter", "AnimMontage", "BlendSpace", "StaticMesh") and (c != "StaticMesh" or "Props" in str(a.package_name)):
            out.append("%s\t%s" % (c, a.package_name))
    out.insert(0, "%s %s" % (raiz, cnt.most_common(14)))
with open(os.path.join(AQUI, "_cache", "personajes_inv.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
