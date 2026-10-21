# -*- coding: utf-8 -*-
"""Lista qué trajeron los paquetes de Fab (materiales, texturas, mallas de árboles) para decidir cómo usarlos. Salida: _cache/fab_inventario.txt"""
import os
import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
reg = unreal.AssetRegistryHelpers.get_asset_registry()
lineas = []
for raiz in ["/Game/SM_Roads_05/Materials", "/Game/Pack_Bonus/Materials", "/Game/Fab/Megascans", "/Game/Megaplant_Library", "/Game/Mobile_Trees_44/Meshes", "/Game/Mobile_Trees_44/Materials"]:
    for a in reg.get_assets_by_path(raiz, recursive=True):
        c = str(a.asset_class_path.asset_name)
        if c in ("Texture2D",):
            continue
        lineas.append("%s\t%s" % (c, a.package_name))
open(os.path.join(AQUI, "_cache", "fab_inventario.txt"), "w", encoding="utf-8").write("\n".join(lineas))
unreal.log("DRONIA: inventario %d" % len(lineas))
unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
