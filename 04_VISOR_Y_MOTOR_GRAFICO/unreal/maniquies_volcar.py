# -*- coding: utf-8 -*-
"""
Vuelca a un JSON (unreal/_cache/maniquies.json, fuera de Git) el esqueleto del maniquí de Unreal (Manny/Quinn de la plantilla
Third Person: jerarquía, pose de referencia) y las claves de las animaciones que se usan (reposo, caminar, trotar, salto, caída,
aterrizaje). Con esos datos maniquies_poses.py arma TODAS las animaciones (también las que no existen: agachado, recostado, gateando)
con matemática normal en NumPy, sin abrir el editor. Se corre una sola vez:
    UnrealEditor-Cmd.exe DronIA_Cancha.uproject -run=pythonscript -script=".../maniquies_volcar.py"
Antes hay que copiar a Content/Characters/Mannequins/ (Meshes, Rigs, Materials, Textures y Anims/Unarmed) lo que trae el motor en
Templates/TemplateResources/High/Characters/Content/Mannequins (ver _LEEME.md).
"""
import json
import os

import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
P = "/Game/Characters/Mannequins/"
CLIPS = {"reposo": "Anims/Unarmed/MM_Idle", "caminar": "Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd", "trotar": "Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd",
         "salto": "Anims/Unarmed/Jump/MM_Jump", "caida": "Anims/Unarmed/Jump/MM_Fall_Loop", "aterrizar": "Anims/Unarmed/Jump/MM_Land"}
AL = unreal.AnimationLibrary


def q(x):
    return [x.x, x.y, x.z, x.w]


def v(x):
    return [x.x, x.y, x.z]


def main():
    malla = unreal.load_asset(P + "Meshes/SKM_Manny_Simple")
    PE = unreal.AnimPoseExtensions
    huesos, sal_clips = {}, {}
    opc = unreal.AnimPoseEvaluationOptions()
    opc.set_editor_property("extract_root_motion", False)
    ref = None
    for nombre, ruta in CLIPS.items():
        a = unreal.load_asset(P + ruta)
        n = AL.get_num_frames(a)
        largo = AL.get_sequence_length(a)
        dt = largo / max(n - 1, 1)
        datos = {"largo": largo, "n": n, "cuadros": []}
        nombres = None
        for k in range(n):
            pose = a.get_anim_pose_at_time(k * dt, opc)
            if nombres is None:
                nombres = [str(x) for x in PE.get_bone_names(pose)]
                datos["huesos"] = nombres
                if ref is None:
                    ref = nombres
            fila = []
            for h in nombres:
                t = PE.get_bone_pose(pose, h, unreal.AnimPoseSpaces.LOCAL)
                fila.append(v(t.translation) + q(t.rotation))
            datos["cuadros"].append(fila)
        sal_clips[nombre] = datos
        unreal.log(f"DRONIA_V {nombre}: {n} cuadros, {largo:.3f} s, {len(nombres)} huesos")
    refpose = {}
    pose = PE.get_reference_pose(unreal.load_asset(P + "Meshes/SK_Mannequin"))
    for h in ref:
        t = PE.get_bone_pose(pose, h, unreal.AnimPoseSpaces.LOCAL)
        refpose[h] = v(t.translation) + q(t.rotation)
    padres = {}
    for h in ref:
        try:
            padres[h] = str(malla.get_bone_parent(h)) if hasattr(malla, "get_bone_parent") else None
        except Exception as e:                                              # noqa: BLE001
            unreal.log("DRONIA_V sin padre de " + h + ": " + repr(e))
            break
    sal = {"huesos": ref, "padres": padres, "ref": refpose, "clips": sal_clips}
    os.makedirs(os.path.join(AQUI, "_cache"), exist_ok=True)
    with open(os.path.join(AQUI, "_cache", "maniquies.json"), "w", encoding="utf-8") as f:
        json.dump(sal, f)
    unreal.log(f"DRONIA_V listo: {len(ref)} huesos, {len(padres)} padres")


main()
