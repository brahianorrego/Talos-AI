# -*- coding: utf-8 -*-
"""Lista qué ofrece el plugin MetaHumanCharacter por Python (clases, funciones del subsistema). Salida: _cache/metahuman_api.txt"""
import os
import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
out = []
for n in sorted(dir(unreal)):
    if "metahuman" in n.lower():
        out.append(n)
        try:
            c = getattr(unreal, n)
            for m in sorted(dir(c)):
                if not m.startswith("_") and m not in ("cast", "static_class", "get_default_object"):
                    out.append("    " + m)
        except Exception as e:  # noqa: BLE001
            out.append("   ERR %r" % e)
reg = unreal.AssetRegistryHelpers.get_asset_registry()
for raiz in ("/MetaHumanCharacter", "/MetaHumanSDK"):
    try:
        a = reg.get_assets_by_path(raiz, recursive=True)
        out.append("%s: %d assets" % (raiz, len(a)))
        for x in list(a)[:0]:
            pass
    except Exception as e:  # noqa: BLE001
        out.append("ERR " + repr(e))
open(os.path.join(AQUI, "_cache", "metahuman_api.txt"), "w", encoding="utf-8").write("\n".join(out))
unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
