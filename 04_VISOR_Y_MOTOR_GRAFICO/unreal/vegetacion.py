# -*- coding: utf-8 -*-
"""
Árboles, arbustos, piedras y plantas en el nivel Cancha_V17 (fase 1 de PLAN_UNREAL.md), con las mallas de Epic del complemento
"PCG Biome Sample" que trae Unreal 5.8 (gratis, sin cuenta; mallas Nanite). Se pone por instancias (una sola pieza por tipo).
  - árboles: en dos hileras irregulares alrededor de la cancha de fútbol, fuera de las líneas y a >= 10 m de la zona de IA (D-051);
  - plantas bajas (apagadas por ahora, PLANTAS = 0; "pasto" cuando haya contenido realista de Fab): sobre el césped, alrededor de la zona de IA pero FUERA de las V
    (nunca dentro de 1.5 m de un panel, para no tapar al ladrón ni al dron en las cámaras);
  - piedras: unas pocas en el borde.
Se puede correr de nuevo: quita lo que puso antes (carpeta "Vegetacion" del nivel) y vuelve a ponerlo. Semilla fija = mismo bosque.

Dentro de Unreal: Herramientas -> Ejecutar script de Python -> este archivo.
Sin abrir el editor:  UnrealEditor-Cmd.exe DronIA_Cancha.uproject -run=pythonscript -script="...\\vegetacion.py"
"""
import math
import os
import random
import sys

import unreal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dronia_ue as D  # noqa: E402

NIVEL = D.CARPETA + "/Mapas/Cancha_V17"
BASE = "/PCGBiomeSample/Meshes/"
LX, LY, CX = 90.0, 60.0, -22.5                      # la cancha de fútbol (por medir), como en dronia_ue.cancha()
V = ((-5.0, 0.0), (5.0, 0.0))                        # vértices de las dos V
ZONA = 15.0                                          # medio lado de la zona de IA (30 x 30 m)
PLANTAS = 0       # las plántulas de Epic son de bajo detalle (hojas como cartulina): apagadas hasta tener pasto realista de Fab


def en_cancha(x, y, margen=0.0):
    return CX - LX / 2 - margen <= x <= CX + LX / 2 + margen and -LY / 2 - margen <= y <= LY / 2 + margen


def cerca_de_v(x, y, r=2.4):
    return any(math.hypot(x - vx, y - vy) < r for vx, vy in V)


def instancias(etiqueta, malla, lista):
    if not lista:
        return None
    """lista = [(x, y, escala, giro_grados)] en metros de la simulación; devuelve el actor con sus instancias."""
    m = unreal.load_asset(BASE + malla)
    if not m or not lista:
        unreal.log_warning(f"DRONIA: sin malla {malla}")
        return None
    a = D.actores.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
    a.set_actor_label("Veg_" + etiqueta)
    a.set_folder_path("Vegetacion")
    try:
        c = a.add_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent, False, unreal.Transform(), False)
        c.set_static_mesh(m)
        for x, y, s, g in lista:
            c.add_instance(unreal.Transform(D.ue(x, y, 0), unreal.Rotator(0, 0, g), unreal.Vector(s, s, s)))
        a.static_mesh_component.set_static_mesh(None)
        return a
    except Exception as e:                                                          # noqa: BLE001
        unreal.log_warning("DRONIA: instancias no disponibles (" + repr(e) + "); se ponen como actores sueltos")
        a.destroy_actor()
        for k, (x, y, s, g) in enumerate(lista):
            b = D.actores.spawn_actor_from_class(unreal.StaticMeshActor, D.ue(x, y, 0), unreal.Rotator(0, 0, g))
            b.static_mesh_component.set_static_mesh(m)
            b.set_actor_scale3d(unreal.Vector(s, s, s))
            b.set_actor_label(f"Veg_{etiqueta}_{k}")
            b.set_folder_path("Vegetacion")
        return None


def main():
    nivel = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not D.biblioteca.does_asset_exist(NIVEL):
        raise RuntimeError("Primero corra crear_cancha.py (no existe " + NIVEL + ")")
    nivel.load_level(NIVEL)
    for a in D.actores.get_all_level_actors():                                        # lo de antes se quita
        if str(a.get_folder_path()) == "Vegetacion":
            D.actores.destroy_actor(a)

    r = random.Random(2026)
    # --- árboles alrededor de la cancha, en 2 hileras irregulares (la de afuera, más densa y con árboles grandes)
    grupos = {"Tree_01": [], "Tree_02": [], "Pine_01": [], "Spruce_01": [], "Sapling_02": []}
    nombres = list(grupos)
    pesos = (3, 3, 2, 2, 2)
    x0, x1, y0, y1 = CX - LX / 2, CX + LX / 2, -LY / 2, LY / 2
    perimetro = [((x0, y1), (x1, y1)), ((x1, y1), (x1, y0)), ((x1, y0), (x0, y0)), ((x0, y0), (x0, y1))]
    for (xa, ya), (xb, yb) in perimetro:
        L = math.hypot(xb - xa, yb - ya)
        nx, ny = -(yb - ya) / L, (xb - xa) / L                                        # hacia afuera (sentido horario)
        k = 0.0
        while k < L:
            f = k / L
            for fila, (d0, d1) in enumerate(((5.0, 9.0), (11.0, 20.0))):
                if fila == 1 and r.random() < 0.35:
                    continue
                d = r.uniform(d0, d1)
                x, y = xa + (xb - xa) * f + nx * d + r.uniform(-1.5, 1.5), ya + (yb - ya) * f + ny * d + r.uniform(-1.5, 1.5)
                n = r.choices(nombres, pesos)[0]
                grupos[n].append((x, y, r.uniform(0.85, 1.25), r.uniform(0, 360)))
            k += r.uniform(5.0, 8.5)
    n_arb = 0
    for n, lista in grupos.items():
        n_arb += len(lista)
        instancias(n, "PCG_" + n, lista)

    # --- plantas bajas sobre el césped, alrededor de la zona de IA y la mitad de la cancha, nunca junto a las V
    plantas = {"Seedling_01": [], "Seedling_02": []}
    for _ in range(PLANTAS):
        x, y = r.uniform(CX - 38, CX + 52), r.uniform(-28, 28)
        if not en_cancha(x, y, 2.0) or cerca_de_v(x, y):
            continue
        if abs(x) < 3.0 and abs(y) < 3.0:
            continue
        plantas[r.choice(list(plantas))].append((x, y, r.uniform(0.7, 1.6), r.uniform(0, 360)))
    n_pl = 0
    for n, lista in plantas.items():
        n_pl += len(lista)
        instancias(n, "PCG_" + n, lista)

    # --- unas piedras en el borde (nunca en la zona de IA)
    piedras = []
    for _ in range(14):
        a = r.uniform(0, 2 * math.pi)
        d = r.uniform(34, 52)
        x, y = CX + math.cos(a) * d * 1.3, math.sin(a) * d * 0.9
        if abs(x) < ZONA + 6 and abs(y) < ZONA + 6:
            continue
        piedras.append((x, y, r.uniform(0.4, 0.9), r.uniform(0, 360)))
    instancias("Boulder_01", "PCG_Boulder_01", piedras)

    nivel.save_current_level()
    unreal.log(f"DRONIA: vegetación puesta: {n_arb} árboles, {n_pl} plantas, {len(piedras)} piedras")


if __name__ == "__main__":
    main()
