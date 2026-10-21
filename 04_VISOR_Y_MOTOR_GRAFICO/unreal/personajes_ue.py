# -*- coding: utf-8 -*-
"""Personas realistas por piezas (21-oct): el ladrón con chaqueta de cuero oscura, guantes y mochila (Survival Character) y los civiles con camisa clara y pantalón (Quantum Character).
Cada persona es un SkeletalMeshActor "maestro" (la pieza de cuerpo, que recibe las animaciones) y las demás prendas van pegadas a él con la pose del maestro (leader pose).
Los esqueletos de Survival y Quantum se declaran compatibles con el de Manny: así valen las animaciones del proyecto (caminar, trotar y la galería de posturas) sin retargeting."""
import unreal

import dronia_ue as D

Q, S = "/Game/QuantumCharacter/Mesh/", "/Game/Survival_Character/Meshes/"
MODELOS = {
    "ladron": {"partes": [S + "Modular_Parts/SK_Survival_Character_Body", S + "Modular_Parts/SK_Survival_Character_Jacket", S + "Modular_Parts/SK_Survival_Character_Jeans",
                          S + "Modular_Parts/SK_Survival_Character_Shoes", S + "Modular_Parts/SK_Survival_Character_Gloves", S + "Modular_Parts/SK_Survival_Character_Backpack"],
               "esqueleto": S + "SKEL_Survival_Character", "alto": 187.0},
    "peaton": {"partes": [Q + "Modules/SKM_Arms", Q + "Modules/SKM_Head", Q + "Modules/SKM_Jeans", Q + "Modules/SKM_Shirt_RolledUp_Blue"],
               "esqueleto": Q + "SK_Military_Character_Skeleton", "alto": 183.0},
}
MANNY = "/Game/Characters/Mannequins/Meshes/SK_Mannequin"
_listo = {"si": False}


def compatibilizar():
    """Declara compatible el esqueleto de Manny en los de Survival y Quantum (una vez por sesión del editor)."""
    if _listo["si"]:
        return
    manny = unreal.load_asset(MANNY)
    for m in MODELOS.values():
        unreal.load_asset(m["esqueleto"]).add_compatible_skeleton(manny)
    _listo["si"] = True


_mallas = {}


def malla_fusionada(rol):
    """Une las prendas del rol en UNA malla con esqueleto (SkeletalMergingLibrary): 1 componente por persona en vez de 4-6 con 'leader pose'. Se hace una vez por rol, en memoria."""
    if rol not in _mallas:
        compatibilizar()
        modelo = MODELOS.get(rol, MODELOS["peaton"])
        partes = [unreal.load_asset(r) for r in modelo["partes"]]
        P = unreal.SkeletalMeshMergeParams()
        P.set_editor_property("meshes_to_merge", partes)
        P.set_editor_property("skeleton", partes[0].get_editor_property("skeleton"))
        _mallas[rol] = unreal.SkeletalMergingLibrary.merge_meshes(P)
    return _mallas[rol]


def figura(etiqueta, rol, estatura, carpeta="Personas"):
    """Devuelve el actor con la malla fusionada del rol, a la escala de su estatura (m). Crea todo de golpe: solo antes de que empiece el dibujo en vivo."""
    for r in figura_por_pasos(etiqueta, rol, estatura, carpeta):
        pass
    return r


def figura_por_pasos(etiqueta, rol, estatura, carpeta="Personas"):
    """Igual que figura(), con un paso (yield) por cosa creada: con el dibujo en marcha, crear varias mallas con esqueleto en el mismo cuadro tumbó el editor.
    Cada paso devuelve None; el último devuelve el actor."""
    malla = malla_fusionada(rol)
    yield None
    a = D.actores.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 0))
    a.set_actor_label(etiqueta)
    a.set_folder_path(carpeta)
    a.skeletal_mesh_component.set_editor_property("skeletal_mesh_asset", malla)
    s = estatura * 100.0 / MODELOS.get(rol, MODELOS["peaton"])["alto"]
    a.set_actor_scale3d(unreal.Vector(s, s, s))
    yield a


def alto(rol):
    return MODELOS.get(rol, MODELOS["peaton"])["alto"]
