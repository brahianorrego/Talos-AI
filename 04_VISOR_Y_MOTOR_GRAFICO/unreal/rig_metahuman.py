# -*- coding: utf-8 -*-
"""Arma dos MetaHumans (ladrón y civil) desde presets del plugin: pide el auto-rigging en la nube de MetaHuman, espera a que termine y los ensambla
(calidad media, canal OPTIMIZED). Deja los resultados en /Game/DronIA/Personas y el informe en _cache/metahuman_rig.txt. Espera hasta 12 min."""
import os
import time
import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
PERSONAS = {"ladron": os.environ.get("DRONIA_MH_LADRON", "Mateo"), "civil": os.environ.get("DRONIA_MH_CIVIL", "Jorge")}
out = []
log = lambda *a: out.append("%.0fs " % (time.time() - t0) + " ".join(str(x) for x in a))     # noqa: E731
t0 = time.time()
sub = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
bib = unreal.EditorAssetLibrary
est = {}
bib.make_directory("/Game/DronIA/Personas")
for rol, preset in PERSONAS.items():
    ruta = "/Game/DronIA/Personas/MH_" + preset
    if not bib.does_asset_exist(ruta):
        bib.duplicate_asset("/MetaHumanCharacter/Optional/Presets/" + preset, ruta)
        bib.save_asset(ruta)
    ch = unreal.load_asset(ruta)
    est[rol] = {"ch": ch, "ruta": ruta, "estado": "rig" if sub.try_add_object_to_edit(ch) else "ERR_add"}
    if est[rol]["estado"] == "rig":
        sub.request_auto_rigging(ch, unreal.MetaHumanCharacterAutoRiggingRequestParams())
    log(rol, preset, est[rol]["estado"])


def terminar():
    unreal.unregister_slate_post_tick_callback(est["h"])
    for e in [v for v in est.values() if isinstance(v, dict)]:
        bib.save_asset(e["ruta"])
    with open(os.path.join(AQUI, "_cache", "metahuman_rig.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")


def tick(dt):
    if time.time() - est.get("ult", 0) < 4:
        return
    est["ult"] = time.time()
    pend = 0
    for rol, e in [(k, v) for k, v in est.items() if isinstance(v, dict)]:
        if e["estado"] == "rig":
            pend += 1
            if sub.can_build_meta_human(e["ch"], False):
                p = unreal.MetaHumanCharacterEditorBuildParameters()
                p.set_editor_property("pipeline_type", unreal.MetaHumanDefaultPipelineType.OPTIMIZED)
                p.set_editor_property("pipeline_quality", unreal.MetaHumanQualityLevel.MEDIUM)
                p.set_editor_property("absolute_build_path", unreal.Paths.project_content_dir() + "DronIA/Personas")
                p.set_editor_property("name_override", "MH_" + rol)
                try:
                    sub.build_meta_human(e["ch"], p)
                    e["estado"] = "armado"
                    log(rol, "build_meta_human lanzado")
                except Exception as ex:  # noqa: BLE001
                    e["estado"] = "ERR_build"
                    log(rol, "ERR build", repr(ex))
    if pend == 0 or time.time() - t0 > 720:
        log("fin; estados:", {k: v["estado"] for k, v in est.items() if isinstance(v, dict)})
        if "fin_t" not in est:
            est["fin_t"] = time.time()
        if time.time() - est["fin_t"] > 45 or pend:
            terminar()


est["h"] = unreal.register_slate_post_tick_callback(tick)
