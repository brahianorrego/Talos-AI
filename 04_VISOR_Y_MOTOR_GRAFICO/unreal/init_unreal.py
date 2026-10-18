# -*- coding: utf-8 -*-
"""
Unreal corre este archivo solo al arrancar el editor (el proyecto DronIA_Cancha lo encuentra por AdditionalPaths).
Si la variable de entorno DRONIA_ORDEN trae "script.py|argumento|argumento...", espera a que el editor termine de cargar
y corre ese script; así se pueden lanzar importar_repeticion.py y renderizar.py desde la línea de comandos SIN que el
editor se cierre solo (lo que hace -ExecutePythonScript). Sin esa variable no hace nada.
"""
import os
import runpy
import sys

import unreal

ORDEN = os.environ.get("DRONIA_ORDEN")
_estado = {"ticks": 0, "globales": None, "tick": None}


def _arrancar(dt):
    _estado["ticks"] += 1
    if _estado["ticks"] < 150:                 # unos segundos después de abrir: ya cargó el mapa y los complementos
        return
    unreal.unregister_slate_post_tick_callback(_estado["tick"])
    partes = ORDEN.split("|")
    sys.argv = partes
    try:
        _estado["globales"] = runpy.run_path(partes[0], run_name="__main__")      # se guarda: el render lo necesita vivo
    except Exception as e:                                                          # noqa: BLE001
        unreal.log_error("DRONIA: falló " + partes[0] + ": " + repr(e))
        if os.environ.get("DRONIA_SALIR", "1") == "1":
            unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")


if ORDEN:
    _estado["tick"] = unreal.register_slate_post_tick_callback(_arrancar)
