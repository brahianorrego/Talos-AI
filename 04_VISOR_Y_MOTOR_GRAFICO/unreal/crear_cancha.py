# -*- coding: utf-8 -*-
"""
Arma el nivel /Game/DronIA/Mapas/Cancha_V17 (fase 1 de PLAN_UNREAL.md): césped, líneas y arcos de la cancha, las dos V de
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

RUTA = D.CARPETA + "/Mapas/Cancha_V17"

nivel = D.nivel_nuevo(RUTA)
if nivel:
    D.cielo_y_luz()
    D.cancha()
    mats = D.mats_paneles()
    D.panel_v("V1", -5.0, 0.0, True, mats)                # abre al sur, hacia donde entra el dron
    D.panel_v("V2", 5.0, 0.0, False, mats)                # abre al norte
    D.dron()
    nivel.save_current_level()
    unreal.log("DRONIA: nivel creado " + RUTA)
    import vegetacion                                      # árboles y piedras (PCG Biome Sample de Epic)
    vegetacion.main()
