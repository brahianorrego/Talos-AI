# -*- coding: utf-8 -*-
"""Parámetros de los materiales de Fab y tamaños de los árboles. Salida: _cache/fab_detalle.txt"""
import os
import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
mel = unreal.MaterialEditingLibrary
out = []
MIS = ["/Game/Fab/Megascans/Surfaces/Uncut_Grass_oilpt20/Medium/oilpt20_tier_2/Materials/MI_oilpt20", "/Game/SM_Roads_05/Materials/Roads_05/MT00036-Asphalt/MI_MT00036_Asphalt",
       "/Game/SM_Roads_05/Materials/Roads_05/MT00133-Cobblestone_01/MI_MT00133_Cobblestone_01", "/Game/SM_Roads_05/Materials/Roads_05/MT00050-Pavement/MI_MT00050_Pavement",
       "/Game/Megaplant_Library/Tree_Black_Alder/Materials/MI_Black_Alder_Bark_01", "/Game/Megaplant_Library/Tree_Black_Alder/Materials/MI_Black_Alder_Foliage_01"]
for r in MIS:
    mi = unreal.load_asset(r)
    out.append("== %s  padre=%s" % (r, mi.get_editor_property("parent").get_path_name() if mi else None))
    if not mi:
        continue
    for nombre in mel.get_scalar_parameter_names(mi.get_editor_property("parent")) if hasattr(mel, "get_scalar_parameter_names") else []:
        pass
    try:
        for p in mi.get_editor_property("scalar_parameter_values"):
            out.append("  escalar %s = %s" % (p.parameter_info.name, p.parameter_value))
        for p in mi.get_editor_property("texture_parameter_values"):
            out.append("  textura %s = %s" % (p.parameter_info.name, p.parameter_value.get_name() if p.parameter_value else None))
        for p in mi.get_editor_property("vector_parameter_values"):
            out.append("  vector %s = %s" % (p.parameter_info.name, p.parameter_value))
    except Exception as e:
        out.append("  ERR %r" % e)
for r in ["/Game/Megaplant_Library/Tree_Black_Alder/Tree_Black_Alder_01/Tree_Black_Alder_01_A", "/Game/Megaplant_Library/Tree_Black_Alder/Tree_Black_Alder_01/Tree_Black_Alder_01_D",
          "/Game/Megaplant_Library/Tree_Hornbeam/Tree_Hornbeam_01/Tree_Hornbeam_01_A", "/Game/Megaplant_Library/Tree_Hornbeam/Tree_Hornbeam_01/Tree_Hornbeam_01_D",
          "/Game/Mobile_Trees_44/Meshes/SM_Mobile44_1", "/Game/HighPoly_Tree_Model/Meshes/SM_HP_Tree"]:
    m = unreal.load_asset(r)
    if m:
        b = m.get_bounds()
        out.append("%s  clase=%s origen=%s extension=%s" % (r.split("/")[-1], m.get_class().get_name(), b.origin, b.box_extent))
        try:
            out.append("   materiales: " + ", ".join(s.material_interface.get_name() if s.material_interface else "None" for s in m.get_editor_property("materials")))
        except Exception as e:
            out.append("   mat ERR %r" % e)
open(os.path.join(AQUI, "_cache", "fab_detalle.txt"), "w", encoding="utf-8").write("\n".join(out))
unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
