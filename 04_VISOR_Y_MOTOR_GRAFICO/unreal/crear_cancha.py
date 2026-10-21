# -*- coding: utf-8 -*-
"""
Arma el nivel /Game/DronIA/Mapas/Cancha_V17 (fase 1 de PLAN_UNREAL.md): el campus de la universidad (entorno_u_ue.py), las dos V de
90° con paneles de 1.5 x 2.25 m (D-066) a 10 m entre vértices (V1 abre al sur, V2 al norte), el dron provisional, cielo
físico, sol, nubes y niebla. Si el nivel ya existe, no lo toca.

Dentro de Unreal: Herramientas -> Ejecutar script de Python -> este archivo.
Sin abrir el editor:  UnrealEditor-Cmd.exe DronIA_Cancha.uproject -run=pythonscript -script="...\\crear_cancha.py"
"""
import os
import sys

import unreal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dronia_ue as D  # noqa: E402
import entorno_u_ue as EU  # noqa: E402

RUTA = D.CARPETA + "/Mapas/Cancha_V17"
unreal.log("DRONIA: REHACER=%s existe=%s" % (os.environ.get("DRONIA_REHACER"), D.biblioteca.does_asset_exist(RUTA)))

if os.environ.get("DRONIA_REHACER") == "1" and D.biblioteca.does_asset_exist(RUTA):
    unreal.EditorLoadingAndSavingUtils.new_blank_map(False)          # salir del nivel antes de borrarlo
    unreal.log("DRONIA: respaldo %s" % D.biblioteca.duplicate_asset(RUTA, RUTA + "_respaldo"))      # por si Brahian le puso algo a mano
    unreal.log("DRONIA: borrado %s" % D.biblioteca.delete_asset(RUTA))
    nivel = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    nivel.new_level(RUTA)                                            # el registro aún cree que existe: se crea sin preguntarle
else:
    nivel = D.nivel_nuevo(RUTA)
if nivel:
    EU.construir()                                          # campus completo: cancha de fútbol, canchas cerradas, edificios, árboles, cerros
    mats = D.mats_paneles()
    D.panel_v("V1", -5.0, 0.0, True, mats)                # abre al sur, hacia donde entra el dron
    D.panel_v("V2", 5.0, 0.0, False, mats)                # abre al norte
    D.dron()
    nivel.save_current_level()
    unreal.log("DRONIA: nivel creado " + RUTA)
