# -*- coding: utf-8 -*-
"""
Importa a Unreal los arboles que genera blender/arboles_sapling.py (extension oficial Sapling Tree Gen de Blender; 6 especies de 1 m de alto, con hojas y
corteza): los FBX de ../arboles/ como mallas en /Game/DronIA/Arboles/<especie>, sus texturas PNG y los materiales (corteza opaca; hoja con mascara por la
transparencia de la textura y a dos caras). Despues entorno_u_ue.arboles() y importar_repeticion.py los usan en vez de los del complemento PCG.
    UnrealEditor-Cmd.exe DronIA_Cancha.uproject -run=pythonscript -script=".../importar_arboles.py"
"""
import os
import sys

import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import dronia_ue as D  # noqa: E402

ORIGEN = os.path.normpath(os.path.join(AQUI, "..", "arboles"))
ESPECIES = ["arce", "abedul", "alamo", "callistemon", "pino", "abeto"]
CARPETA = D.CARPETA + "/Arboles"
mel = unreal.MaterialEditingLibrary


def tarea(archivo, destino, nombre, opciones=None):
    t = unreal.AssetImportTask()
    t.filename = archivo
    t.destination_path = destino
    t.destination_name = nombre
    t.replace_existing = True
    t.automated = True
    t.save = True
    if opciones is not None:
        t.options = opciones
    return t


def material(nombre, textura, hoja):
    ruta = CARPETA + "/Materiales/" + nombre
    if D.biblioteca.does_asset_exist(ruta):
        D.biblioteca.delete_asset(ruta)
    mat = D.herramientas.create_asset(nombre, CARPETA + "/Materiales", unreal.Material, unreal.MaterialFactoryNew())
    tx = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -500, 0)
    tx.set_editor_property("texture", textura)
    rug = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -300, 200)
    rug.set_editor_property("r", 0.9)
    mel.connect_material_property(tx, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(rug, "", unreal.MaterialProperty.MP_ROUGHNESS)
    if hoja:
        mel.connect_material_property(tx, "A", unreal.MaterialProperty.MP_OPACITY_MASK)
        mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
        mat.set_editor_property("two_sided", True)
    mel.recompile_material(mat)
    D.biblioteca.save_loaded_asset(mat)
    return mat


def main():
    opc = unreal.FbxImportUI()
    opc.set_editor_property("import_mesh", True)
    opc.set_editor_property("import_materials", False)
    opc.set_editor_property("import_textures", False)
    opc.set_editor_property("import_as_skeletal", False)
    opc.set_editor_property("automated_import_should_detect_type", False)
    opc.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
    opc.static_mesh_import_data.set_editor_property("combine_meshes", True)
    tareas = [tarea(os.path.join(ORIGEN, n + ".fbx"), CARPETA, n, opc) for n in ESPECIES]
    tareas += [tarea(os.path.join(ORIGEN, "tex", f), CARPETA + "/Tex", os.path.splitext(f)[0]) for f in sorted(os.listdir(os.path.join(ORIGEN, "tex")))]
    D.herramientas.import_asset_tasks(tareas)
    corteza = material("M_Corteza", unreal.load_asset(CARPETA + "/Tex/corteza"), False)
    for n in ESPECIES:
        malla = unreal.load_asset(f"{CARPETA}/{n}")
        hoja = material("M_Hoja_" + n, unreal.load_asset(f"{CARPETA}/Tex/hoja_{n}"), True)
        for i, sm in enumerate(malla.static_materials):
            nombre = str(sm.get_editor_property("material_slot_name"))
            malla.set_material(i, hoja if "hoja" in nombre.lower() else corteza)
        D.biblioteca.save_loaded_asset(malla)
        unreal.log(f"DRONIA: arbol {n}: {len(malla.static_materials)} materiales")
    unreal.log("DRONIA: arboles importados")


main()
