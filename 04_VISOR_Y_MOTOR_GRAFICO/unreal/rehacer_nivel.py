# -*- coding: utf-8 -*-
"""Arma el nivel con crear_cancha.py y cierra el editor (para correrlo sin vigilarlo). Antes hay que borrar Cancha_V17.umap (queda respaldo en _cache/respaldo)."""
import os
import runpy

import unreal

try:
    runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "crear_cancha.py"), run_name="__main__")
except Exception as e:  # noqa: BLE001
    unreal.log_error("DRONIA: falló crear_cancha: " + repr(e))
unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
