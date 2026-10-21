# -*- coding: utf-8 -*-
import os
import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
out = []
S = unreal.MetaHumanCharacterEditorSubsystem
for m in ("build_meta_human", "can_build_meta_human", "spawn_meta_human_actor", "request_texture_sources", "assemble_for_preview", "try_add_object_to_edit"):
    out.append("== " + m + "\n" + str(getattr(S, m).__doc__))
for c in ("MetaHumanCharacterEditorBuildParameters", "MetaHumanCharacterAssemblySettings", "MetaHumanCharacterEditorPipeline"):
    k = getattr(unreal, c)
    out.append("== " + c + " props: " + ", ".join(m for m in dir(k) if not m.startswith("_"))[:1500])
sub = unreal.get_editor_subsystem(S)
ch = unreal.load_asset("/MetaHumanCharacter/Optional/Presets/Jorge")
out.append("preset: %r" % ch)
if ch:
    out.append("props: " + ", ".join(m for m in dir(ch) if not m.startswith("_"))[:2500])
    try:
        out.append("can_build: %r" % sub.can_build_meta_human(ch))
    except Exception as e:  # noqa: BLE001
        out.append("can_build ERR %r" % e)
open(os.path.join(AQUI, "_cache", "metahuman_doc.txt"), "w", encoding="utf-8").write("\n".join(out))
unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
