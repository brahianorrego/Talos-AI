# -*- coding: utf-8 -*-
"""Prueba visual: pone cuatro combinaciones de Quantum y Survival en fila (con la animación de reposo de Manny, esqueleto compatible) y saca una foto.
Salida: foto en Saved/Screenshots y _cache/probar_personajes.txt. No guarda el nivel."""
import os
import unreal

import dronia_ue as D

AQUI = os.path.dirname(os.path.abspath(__file__))
out = []
log = lambda *a: out.append(" ".join(str(x) for x in a))     # noqa: E731
Q, S = "/Game/QuantumCharacter/Mesh/", "/Game/Survival_Character/Meshes/"
COMBOS = [
    ("Q_civil", [Q + "Modules/SKM_Arms", Q + "Modules/SKM_Head", Q + "Modules/SKM_Jeans", Q + "Modules/SKM_Shirt_RolledUp_Blue"]),
    ("Q_civil2", [Q + "Modules/SKM_Arms", Q + "Modules/SKM_Head", Q + "Modules/SKM_Jeans", Q + "Modules/SKM_Shirt_RolledUp_Blue", Q + "Modules/SKM_Patch_Back"]),
    ("S_ladron", [S + "Modular_Parts/SK_Survival_Character_Body", S + "Modular_Parts/SK_Survival_Character_Jacket", S + "Modular_Parts/SK_Survival_Character_Jeans",
                  S + "Modular_Parts/SK_Survival_Character_Shoes", S + "Modular_Parts/SK_Survival_Character_Gloves", S + "Modular_Parts/SK_Survival_Character_Backpack"]),
    ("S_gorro", [S + "Modular_Parts/SK_Survival_Character_Body", S + "Modular_Parts/SK_Survival_Character_Jacket", S + "Modular_Parts/SK_Survival_Character_Jeans",
                 S + "Modular_Parts/SK_Survival_Character_Shoes", S + "Modular_Parts/SK_Survival_Character_Gloves"]),
]
manny_sk = unreal.load_asset("/Game/Characters/Mannequins/Meshes/SK_Mannequin")
for p in (Q + "SK_Military_Character_Skeleton", S + "SKEL_Survival_Character"):
    sk = unreal.load_asset(p)
    for f in ("add_compatible_skeleton",):
        try:
            getattr(sk, f)(manny_sk)
            log("compatible", p.split("/")[-1], "<-", "Manny")
        except Exception as e:  # noqa: BLE001
            log("compat ERR", repr(e))
idle = unreal.load_asset("/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle")
actores = []
for i, (nombre, partes) in enumerate(COMBOS):
    x = (i - 1.5) * 0.9
    maestro = None
    for k, p in enumerate(partes):
        m = unreal.load_asset(p)
        if m is None:
            log("falta", p)
            continue
        a = D.actores.spawn_actor_from_class(unreal.SkeletalMeshActor, D.ue(x, -60.0, 0.0), unreal.Rotator(0, 0, 0))
        a.set_actor_label("Prueba_%s_%d" % (nombre, k))
        c = a.skeletal_mesh_component
        c.set_editor_property("skeletal_mesh_asset", m)
        if nombre == "S_gorro" and "Body" in p:                                            # prueba: el material "Haircap" en la ranura del pelo
            for j in range(c.get_num_materials()):
                if str(c.get_material_slot_names()[j]) == "Hair":
                    c.set_material(j, unreal.load_asset("/Game/Survival_Character/Materials/MI_Survival_Character_Haircap"))
        if maestro is None:
            maestro = c
            c.play_animation(unreal.load_asset("/Game/QuantumCharacter/Demo/Animations/A_MM_Idle") if nombre.startswith("Q") else idle, True)
        else:
            try:
                c.set_leader_pose_component(maestro)
            except Exception as e:  # noqa: BLE001
                log("leader ERR", repr(e))
        actores.append(a)
log("actores", len(actores))
est = {"n": 0}


def tick(dt):
    est["n"] += 1
    if est["n"] == 40:
        unreal.EditorLevelLibrary.set_level_viewport_camera_info(D.ue(0.0, -64.0, 1.3), unreal.Rotator(0, -2, -90))
    if est["n"] in (600, 700):
        unreal.SystemLibrary.execute_console_command(None, "HighResShot 1280x720")
    if est["n"] == 800:
        for a in actores:
            D.actores.destroy_actor(a)
        with open(os.path.join(AQUI, "_cache", "probar_personajes.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(out))
        unreal.unregister_slate_post_tick_callback(est["h"])
        unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")


est["h"] = unreal.register_slate_post_tick_callback(tick)
