# -*- coding: utf-8 -*-
"""Ensambla un MetaHuman ya con rig (MH_<preset>) en calidad media, canal OPTIMIZED. Lista lo que se creó. Salida: _cache/metahuman_armado.txt
Uso (con Unreal CERRADO): DRONIA_PRESET=Mateo ejecutar_en_unreal.bat armar_persona.py"""
import os
import time
import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
out = []
t0 = time.time()
log = lambda *a: out.append("%.0fs " % (time.time() - t0) + " ".join(str(x) for x in a))     # noqa: E731
nombre = os.environ.get("DRONIA_PRESET", "Mateo")
sub = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
ruta = "/Game/DronIA/Personas/MH_" + nombre
ch = unreal.load_asset(ruta)
log("cargado", ch, "add_to_edit", sub.try_add_object_to_edit(ch), "can_build", sub.can_build_meta_human(ch, True))
est = {"lanzado": False, "ult": 0}


def terminar():
    unreal.unregister_slate_post_tick_callback(est["h"])
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    for a in reg.get_assets_by_path("/Game/DronIA/Personas", recursive=True):
        log("asset", a.asset_class_path.asset_name, a.package_name)
    unreal.EditorAssetLibrary.save_directory("/Game/DronIA/Personas")
    with open(os.path.join(AQUI, "_cache", "metahuman_armado.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")


def tick(dt):
    if time.time() - est["ult"] < 3:
        return
    est["ult"] = time.time()
    if not est["lanzado"]:
        if not sub.can_build_meta_human(ch, False):
            if time.time() - t0 > 20:
                log("no se puede armar (sin rig)")
                terminar()
            return
        p = unreal.MetaHumanCharacterEditorBuildParameters()
        p.set_editor_property("pipeline_type", unreal.MetaHumanDefaultPipelineType.OPTIMIZED)
        p.set_editor_property("pipeline_quality", unreal.MetaHumanQualityLevel.MEDIUM)
        p.set_editor_property("name_override", "BP_" + nombre)
        try:
            sub.build_meta_human(ch, p)
            log("build lanzado")
        except Exception as e:  # noqa: BLE001
            log("ERR build", repr(e))
            terminar()
            return
        est["lanzado"] = True
        est["t_build"] = time.time()
    elif time.time() - est["t_build"] > 90:
        terminar()


est["h"] = unreal.register_slate_post_tick_callback(tick)
