# -*- coding: utf-8 -*-
"""Pasa las animaciones del maniquí (Manny, esqueleto SK_Mannequin) al cuerpo MetaHuman: crea IK_Manny con las MISMAS cadenas del IK Rig de MetaHuman (los huesos se llaman igual),
un IK Retargeter Manny -> MetaHuman y duplica+retargetea idle, caminar, trotar y la galería de posturas. Salida: _cache/retarget_resultado.txt
Variable DRONIA_MH_MALLA = malla de cuerpo MetaHuman de destino (por defecto la plantilla del plugin)."""
import os
import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
out = []
log = lambda *a: out.append(" ".join(str(x) for x in a))     # noqa: E731
herr = unreal.AssetToolsHelpers.get_asset_tools()
bib = unreal.EditorAssetLibrary
CARP = "/Game/DronIA/Personas/Retarget"
bib.make_directory(CARP)
manny = unreal.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple")
destino = unreal.load_asset(os.environ.get("DRONIA_MH_MALLA", "/MetaHumanCharacter/Body/IdentityTemplate/SKM_Body"))
rig_mh = unreal.load_asset("/MetaHumanCharacter/Animation/Retargeting/IK_MH_IKRig")
log("manny", manny, "destino", destino, "esqueleto destino", destino.get_editor_property("skeleton").get_path_name() if destino else None)
log("esqueleto manny", manny.get_editor_property("skeleton").get_path_name())

# 1) IK Rig de Manny con las cadenas del de MetaHuman
if bib.does_asset_exist(CARP + "/IK_Manny"):
    bib.delete_asset(CARP + "/IK_Manny")
rig = herr.create_asset("IK_Manny", CARP, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
c = unreal.IKRigController.get_controller(rig)
c.set_skeletal_mesh(manny)
cm = unreal.IKRigController.get_controller(rig_mh)
c.set_retarget_root(cm.get_retarget_root())
n = 0
for nombre_c in cm.get_retarget_chains():
    try:
        c.add_retarget_chain(nombre_c, cm.get_retarget_chain_start_bone(nombre_c), cm.get_retarget_chain_end_bone(nombre_c), cm.get_retarget_chain_goal(nombre_c))
        n += 1
    except Exception as e:  # noqa: BLE001
        log("cadena", nombre_c, "ERR", repr(e))
log("cadenas copiadas", n, "raíz", cm.get_retarget_root())
bib.save_asset(CARP + "/IK_Manny")

# 2) Retargeter
if bib.does_asset_exist(CARP + "/RTG_Manny_a_MH"):
    bib.delete_asset(CARP + "/RTG_Manny_a_MH")
rtg = herr.create_asset("RTG_Manny_a_MH", CARP, unreal.IKRetargeter, unreal.IKRetargetFactory())
rc = unreal.IKRetargeterController.get_controller(rtg)
rc.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, rig)
rc.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, rig_mh)
try:
    rc.auto_map_chains(unreal.AutoMapChainType.EXACT, True)
except Exception as e:  # noqa: BLE001
    log("auto_map ERR", repr(e))
try:
    rc.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE, manny)
    rc.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET, destino)
except Exception as e:  # noqa: BLE001
    log("preview ERR", repr(e))
bib.save_asset(CARP + "/RTG_Manny_a_MH")

# 3) Animaciones
A = "/Game/Characters/Mannequins/Anims/Unarmed/"
lista = [A + "MM_Idle", A + "Walk/MF_Unarmed_Walk_Fwd", A + "Jog/MF_Unarmed_Jog_Fwd", "/Game/DronIA/Anim/Rep_replay_v17_galeria_1"]
anims = [unreal.load_asset(p) for p in lista]
log("animaciones", [a.get_name() if a else None for a in anims])
try:
    lote = unreal.Array(unreal.Object)
    for a in anims:
        if a:
            lote.append(a)
    res = unreal.IKRetargetBatchOperation.duplicate_and_retarget(lote, manny, destino, rtg, "", "", "", "_MH", True)
    log("retarget", [r.get_path_name() for r in res])
except Exception as e:  # noqa: BLE001
    log("retarget ERR", repr(e))
reg = unreal.AssetRegistryHelpers.get_asset_registry()
for a in reg.get_assets_by_path("/Game/DronIA/Personas", recursive=True):
    log("asset", a.asset_class_path.asset_name, a.package_name)
bib.save_directory("/Game/DronIA/Personas")
with open(os.path.join(AQUI, "_cache", "retarget_resultado.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
