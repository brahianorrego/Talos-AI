# -*- coding: utf-8 -*-
"""Ranuras de material de cada pieza de Quantum y Survival y los materiales disponibles. Salida: _cache/mat_personajes.txt"""
import os
import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
out = []
reg = unreal.AssetRegistryHelpers.get_asset_registry()
for a in reg.get_assets_by_path("/Game/QuantumCharacter", recursive=True) + reg.get_assets_by_path("/Game/Survival_Character", recursive=True):
    c = str(a.asset_class_path.asset_name)
    if c == "SkeletalMesh":
        m = a.get_asset()
        out.append("MESH %s slots=%s" % (a.package_name, [(str(s.material_slot_name), s.material_interface.get_path_name().split("/")[-1] if s.material_interface else None) for s in m.get_editor_property("materials")]))
    elif c in ("Material", "MaterialInstanceConstant"):
        out.append("MAT %s %s" % (c, a.package_name))
with open(os.path.join(AQUI, "_cache", "mat_personajes.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
