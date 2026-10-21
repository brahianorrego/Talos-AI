# -*- coding: utf-8 -*-
"""Lista las prendas y el pelo (MetaHumanWardrobeItem) del plugin y lo que ya trae la colección de MH_Mateo. Salida: _cache/metahuman_ropa.txt"""
import os
import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
out = []
reg = unreal.AssetRegistryHelpers.get_asset_registry()
for a in reg.get_assets_by_path("/MetaHumanCharacter", recursive=True):
    if str(a.asset_class_path.asset_name) == "MetaHumanWardrobeItem":
        out.append("W\t%s" % a.package_name)
ch = unreal.load_asset("/Game/DronIA/Personas/MH_Mateo")
out.append("ch %r" % ch)
try:
    col = ch.get_editor_property("internal_collection")
    out.append("coleccion %r" % col)
    out.append("slots %r" % list(col.get_slot_names()))
    for k in col.get_all_item_keys():
        out.append("item %r slot=%r nombre=%r" % (k, col.get_item_slot_name(k), col.get_item_display_name(k)))
except Exception as e:  # noqa: BLE001
    out.append("ERR coleccion %r" % e)
sub = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
out.append("add %r" % sub.try_add_object_to_edit(ch))
out.append("can_build %r" % sub.can_build_meta_human(ch, True))
with open(os.path.join(AQUI, "_cache", "metahuman_ropa.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
