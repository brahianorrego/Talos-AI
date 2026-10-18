# Escribe en el registro de Unreal el tamaño (m) de las mallas de vegetación del complemento PCG Biome Sample.
import unreal
for n in ("PCG_Tree_01", "PCG_Tree_02", "PCG_Pine_01", "PCG_Spruce_01", "PCG_Sapling_01", "PCG_Sapling_02", "PCG_Seedling_01", "PCG_Seedling_02", "PCG_Boulder_01", "PCG_Cactus_01"):
    m = unreal.load_asset("/PCGBiomeSample/Meshes/" + n)
    if not m:
        unreal.log_warning("DRONIA: no existe " + n); continue
    b = m.get_bounds()
    unreal.log("DRONIA: malla %s extension(m)=%.1f x %.1f x %.1f origen_z(m)=%.1f nanite=%s" % (n, b.box_extent.x * 2 / 100, b.box_extent.y * 2 / 100, b.box_extent.z * 2 / 100, b.origin.z / 100,
               m.get_editor_property("nanite_settings").get_editor_property("enabled") if hasattr(m, "get_editor_property") else "?"))
