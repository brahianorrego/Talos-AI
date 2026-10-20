# -*- coding: utf-8 -*-
"""
Instala (una sola vez, sin cuentas) la extension OFICIAL "Sapling Tree Gen" de Blender desde extensions.blender.org, para generar los arboles del campus.
    blender --background --factory-startup --python instalar_sapling.py
Deja la extension en la carpeta de usuario de Blender (fuera del repositorio).
"""
import sys

import bpy

bpy.context.preferences.system.use_online_access = True
try:
    bpy.ops.extensions.repo_sync_all()
except Exception as e:                                           # noqa: BLE001
    print("SYNC", repr(e))
try:
    r = bpy.ops.extensions.package_install(repo_index=0, pkg_id="sapling_tree_gen", enable_on_install=True)
    print("INSTALAR", r)
except Exception as e:                                           # noqa: BLE001
    print("FALLO", repr(e))
    sys.exit(1)
print("TIENE tree_add:", hasattr(bpy.ops.curve, "tree_add"))
bpy.ops.wm.save_userpref()
