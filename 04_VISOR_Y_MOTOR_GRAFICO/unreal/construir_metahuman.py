# -*- coding: utf-8 -*-
"""Prueba: arma un MetaHuman desde un preset local del plugin (sin MetaHuman Creator en la nube). Salida: _cache/metahuman_build.txt"""
import os
import time
import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
out = []
log = lambda *a: out.append(" ".join(str(x) for x in a))     # noqa: E731
for n in sorted(dir(unreal)):
    if n.startswith("MetaHuman") and ("Quality" in n or "Pipeline" in n or "Animation" in n or "Type" in n):
        k = getattr(unreal, n)
        if hasattr(k, "__members__") or n.endswith(("Quality", "Type", "Level")):
            log("ENUM", n, [m for m in dir(k) if m.isupper()][:12])
S = unreal.MetaHumanCharacterEditorSubsystem
sub = unreal.get_editor_subsystem(S)
bib = unreal.EditorAssetLibrary
nombre = os.environ.get("DRONIA_PRESET", "Jorge")
destino = "/Game/DronIA/Personas/MH_" + nombre
if not bib.does_asset_exist(destino):
    bib.make_directory("/Game/DronIA/Personas")
    bib.duplicate_asset("/MetaHumanCharacter/Optional/Presets/" + nombre, destino)
ch = unreal.load_asset(destino)
log("duplicado", ch)
log("add_to_edit", sub.try_add_object_to_edit(ch))
log("can_build", sub.can_build_meta_human(ch, True))
try:
    sub.assemble_for_preview(ch)
    log("assemble_for_preview ok")
except Exception as e:  # noqa: BLE001
    log("assemble ERR", repr(e))
p = unreal.MetaHumanCharacterEditorBuildParameters()
log("params por defecto", p.to_dict() if hasattr(p, "to_dict") else p)
open(os.path.join(AQUI, "_cache", "metahuman_build.txt"), "w", encoding="utf-8").write("\n".join(out))
unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
