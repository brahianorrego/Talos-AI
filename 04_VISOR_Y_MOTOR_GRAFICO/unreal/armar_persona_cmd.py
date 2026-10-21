# -*- coding: utf-8 -*-
"""Ensambla un MetaHuman con rig SIN abrir el editor (UnrealEditor-Cmd -run=pythonscript): ahí el ensamblado no se cae (dentro del editor da 'NotNull' en la barra de progreso).
Variables: DRONIA_PRESET (Mateo | Jorge). Salida: _cache/metahuman_armado.txt"""
import os
import time
import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
out = []
log = lambda *a: out.append(" ".join(str(x) for x in a))     # noqa: E731
nombre = os.environ.get("DRONIA_PRESET", "Mateo")
sub = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
log("subsistema", sub)
ch = unreal.load_asset("/Game/DronIA/Personas/MH_" + nombre)
log("cargado", ch, "add", sub.try_add_object_to_edit(ch), "can_build", sub.can_build_meta_human(ch, True))
if sub.can_build_meta_human(ch, False):
    p = unreal.MetaHumanCharacterEditorBuildParameters()
    p.set_editor_property("pipeline_type", unreal.MetaHumanDefaultPipelineType.OPTIMIZED)
    p.set_editor_property("pipeline_quality", unreal.MetaHumanQualityLevel.MEDIUM)
    p.set_editor_property("name_override", "BP_" + nombre)
    sub.build_meta_human(ch, p)
    log("build terminado")
reg = unreal.AssetRegistryHelpers.get_asset_registry()
for a in reg.get_assets_by_path("/Game/DronIA/Personas", recursive=True):
    log("asset", a.asset_class_path.asset_name, a.package_name)
unreal.EditorAssetLibrary.save_directory("/Game/DronIA/Personas")
with open(os.path.join(AQUI, "_cache", "metahuman_armado.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
