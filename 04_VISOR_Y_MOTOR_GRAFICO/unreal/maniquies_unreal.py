# -*- coding: utf-8 -*-
"""
Maniquíes de Unreal (Manny y Quinn, de la plantilla Third Person que ya trae el motor; sin cuentas ni descargas) para las personas de
la repetición. Este archivo corre DENTRO del editor (cuyo Python no tiene NumPy): convierte la animación que dejó maniquies_preparar.py
en un AnimSequence, pone la figura y le agrega la pista de animación a la Level Sequence. Lo usa importar_repeticion.py.
"""
import os
import sys

import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

MALLA = {"ladron": "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple", "peaton": "/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple"}
ESQUELETO = "/Game/Characters/Mannequins/Meshes/SK_Mannequin"
CARPETA_ANIM = "/Game/DronIA/Anim"
ALTO_MANIQUI = 175.0            # cm: la pose de pie del maniquí mide 174.7 cm (cabeza + 15 cm; maniquies_animar.Animador.alto_pie)


def disponible():
    return unreal.EditorAssetLibrary.does_asset_exist(ESQUELETO) and os.path.exists(os.path.join(AQUI, "_cache", "maniquies.json"))


def crear_anim(nombre, plano, n, huesos, fps=24):
    """plano: array('f') con n cuadros x len(huesos) x 7 (x y z qx qy qz qw, locales) -> AnimSequence nuevo."""
    sk = unreal.load_asset(ESQUELETO)
    nombre = nombre.replace("-", "_")
    ruta = f"{CARPETA_ANIM}/{nombre}"
    if unreal.EditorAssetLibrary.does_asset_exist(ruta):
        unreal.EditorAssetLibrary.delete_asset(ruta)
    f = unreal.AnimSequenceFactory()
    f.set_editor_property("target_skeleton", sk)
    anim = unreal.AssetToolsHelpers.get_asset_tools().create_asset(nombre, CARPETA_ANIM, unreal.AnimSequence, f)
    ctrl = anim.controller
    H = len(huesos)
    ctrl.open_bracket("DronIA " + nombre, False)
    ctrl.set_frame_rate(unreal.FrameRate(fps, 1))
    ctrl.set_number_of_frames(unreal.FrameNumber(n - 1))
    unos = [unreal.Vector(1, 1, 1)] * n
    for i, hueso in enumerate(huesos):
        ctrl.add_bone_curve(hueso)
        b = i * 7
        pos = [unreal.Vector(plano[k * H * 7 + b], plano[k * H * 7 + b + 1], plano[k * H * 7 + b + 2]) for k in range(n)]
        rot = [unreal.Quat(plano[k * H * 7 + b + 3], plano[k * H * 7 + b + 4], plano[k * H * 7 + b + 5], plano[k * H * 7 + b + 6])
               for k in range(n)]
        ctrl.set_bone_track_keys(hueso, pos, rot, unos)
    ctrl.close_bracket(False)
    unreal.EditorAssetLibrary.save_loaded_asset(anim)
    return anim


def figura(etiqueta, rol, color, estatura, carpeta="Personas"):
    """SkeletalMeshActor con el maniquí del rol, a la escala de su estatura (m), con un material liso del color del rol."""
    import dronia_ue as D
    malla = unreal.load_asset(MALLA.get(rol, MALLA["peaton"]))
    a = D.actores.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 0))
    a.set_actor_label(etiqueta)
    a.set_folder_path(carpeta)
    c = a.skeletal_mesh_component
    c.set_editor_property("skeletal_mesh_asset", malla)
    mat = D.material("Persona_" + etiqueta, color, 0.65)
    for k in range(c.get_num_materials()):
        c.set_material(k, mat)
    s = estatura * 100.0 / ALTO_MANIQUI
    a.set_actor_scale3d(unreal.Vector(s, s, s))
    return a


def pista_animacion(sec, actor, anim, n):
    """Agrega a la Level Sequence la pista de animación del maniquí: toda la animación a lo largo de los n cuadros."""
    b = sec.add_possessable(actor.skeletal_mesh_component)
    pista = b.add_track(unreal.MovieSceneSkeletalAnimationTrack)
    s = pista.add_section()
    s.set_range(0, n)
    p = s.get_editor_property("params")
    p.set_editor_property("animation", anim)
    s.set_editor_property("params", p)
    return b
