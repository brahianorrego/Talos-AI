# -*- coding: utf-8 -*-
"""Busca IK Rigs / Retargeters de Manny y de MetaHuman. Salida: _cache/retarget_info.txt"""
import os
import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
out = []
reg = unreal.AssetRegistryHelpers.get_asset_registry()
for raiz in ("/Game", "/MetaHumanCharacter", "/Engine"):
    for a in reg.get_assets_by_path(raiz, recursive=True):
        c = str(a.asset_class_path.asset_name)
        if c in ("IKRigDefinition", "IKRetargeter"):
            out.append("%s\t%s" % (c, a.package_name))
rt = unreal.load_asset("/MetaHumanCharacter/Animation/Retargeting/RTG_MH_IKRig")
if rt:
    try:
        ctl = unreal.IKRetargeterController.get_controller(rt)
        out.append("src rig %r" % ctl.get_ik_rig(unreal.RetargetSourceOrTarget.SOURCE))
        out.append("dst rig %r" % ctl.get_ik_rig(unreal.RetargetSourceOrTarget.TARGET))
    except Exception as e:  # noqa: BLE001
        out.append("ERR %r" % e)
with open(os.path.join(AQUI, "_cache", "retarget_info.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
