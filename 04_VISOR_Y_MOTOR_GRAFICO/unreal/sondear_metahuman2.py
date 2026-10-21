# -*- coding: utf-8 -*-
import os
import collections
import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
reg = unreal.AssetRegistryHelpers.get_asset_registry()
out = []
cuenta = collections.Counter()
for a in reg.get_assets_by_path("/MetaHumanCharacter", recursive=True):
    cuenta[str(a.asset_class_path.asset_name)] += 1
out.append(str(cuenta.most_common(30)))
for a in reg.get_assets_by_path("/MetaHumanCharacter", recursive=True):
    c = str(a.asset_class_path.asset_name)
    if c in ("MetaHumanCharacter", "SkeletalMesh", "Blueprint", "GroomAsset", "AnimSequence") or "reset" in str(a.package_name):
        out.append("%s\t%s" % (c, a.package_name))
open(os.path.join(AQUI, "_cache", "metahuman_assets.txt"), "w", encoding="utf-8").write("\n".join(out[:600]))
unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
