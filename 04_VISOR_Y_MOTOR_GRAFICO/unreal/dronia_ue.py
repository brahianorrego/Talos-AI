# -*- coding: utf-8 -*-
"""
Funciones comunes para Unreal Engine 5.8 (fase 1 de PLAN_UNREAL.md, D-065). Corren DENTRO de Unreal (Python del editor).

La simulación (03_SIMULACION_RL, foto()) usa metros, x al este, y al norte, z arriba y ángulos en radianes antihorarios
desde +x. Unreal usa centímetros, X adelante, Y a la DERECHA (mano izquierda) y Z arriba; por eso y_unreal = -y_sim y la
guiñada en Unreal es -psi (en grados).

Medidas de la cancha: D-051 y D-066 (paneles de 1.5 m x 2.25 m en V de 90°, vértices a 10 m, zona de IA de 30 x 30 m);
la cancha de fútbol (90 x 60 m) está por medir. Todo lo que no es de verdad (geocerca) no se dibuja aquí.
"""
import math

import unreal

M = 100.0                                           # 1 m = 100 cm
CARPETA = "/Game/DronIA"
FORMAS = "/Engine/BasicShapes/"
ALA, ALTO_PANEL, GROSOR_PANEL = 1.5, 2.30, 0.05          # paneles delgados de 5 cm, 1.50 m de ancho y 2.30 m de alto (Brahian, 20-oct)

actores = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
herramientas = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
biblioteca = unreal.EditorAssetLibrary


def ue(x, y, z=0.0):
    """Punto de la simulación (m) -> unreal.Vector (cm)."""
    return unreal.Vector(x * M, -y * M, z * M)


def guinada(psi):
    """Ángulo de la simulación (rad, antihorario desde +x) -> guiñada de Unreal (grados)."""
    return -math.degrees(psi)


# ------------------------------------------------------------------------------------------------ materiales
def material_base():
    """Material con parámetros 'Color' y 'Rugosidad' (una sola vez); los demás son instancias de este."""
    ruta = CARPETA + "/Materiales/M_Base"
    if biblioteca.does_asset_exist(ruta):
        return unreal.load_asset(ruta)
    mat = herramientas.create_asset("M_Base", CARPETA + "/Materiales", unreal.Material, unreal.MaterialFactoryNew())
    color = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -400, 0)
    color.set_editor_property("parameter_name", "Color")
    color.set_editor_property("default_value", unreal.LinearColor(0.5, 0.5, 0.5, 1))
    rug = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -400, 200)
    rug.set_editor_property("parameter_name", "Rugosidad")
    rug.set_editor_property("default_value", 0.8)
    met = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -400, 320)
    met.set_editor_property("parameter_name", "Metalico")
    met.set_editor_property("default_value", 0.0)
    mel.connect_material_property(color, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(rug, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(met, "", unreal.MaterialProperty.MP_METALLIC)
    mel.recompile_material(mat)
    biblioteca.save_loaded_asset(mat)
    return mat


def material(nombre, color, rugosidad=0.8, metalico=0.0):
    """Instancia de M_Base con un color (r, g, b en 0-1, lineal)."""
    ruta = CARPETA + "/Materiales/MI_" + nombre
    if biblioteca.does_asset_exist(ruta):
        return unreal.load_asset(ruta)
    mi = herramientas.create_asset("MI_" + nombre, CARPETA + "/Materiales", unreal.MaterialInstanceConstant,
                                   unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, material_base())
    mel.set_material_instance_vector_parameter_value(mi, "Color", unreal.LinearColor(color[0], color[1], color[2], 1))
    mel.set_material_instance_scalar_parameter_value(mi, "Rugosidad", rugosidad)
    mel.set_material_instance_scalar_parameter_value(mi, "Metalico", metalico)
    biblioteca.save_loaded_asset(mi)
    return mi


def material_cesped():
    """Césped de cancha de fútbol: franjas de corte de 5 m (claro y oscuro), variación fina con ruido y rugosidad alta.
    Es procedural (sin texturas): se ve parejo de cerca; para pasto realista hace falta contenido de Fab (PLAN_UNREAL.md, paso 7)."""
    ruta = CARPETA + "/Materiales/M_Cesped"
    if biblioteca.does_asset_exist(ruta):
        return unreal.load_asset(ruta)
    mat = herramientas.create_asset("M_Cesped", CARPETA + "/Materiales", unreal.Material, unreal.MaterialFactoryNew())
    crear = lambda clase, x, y: mel.create_material_expression(mat, clase, x, y)
    pos = crear(unreal.MaterialExpressionWorldPosition, -1400, 0)
    eje = crear(unreal.MaterialExpressionComponentMask, -1200, 0)
    eje.set_editor_property("r", False); eje.set_editor_property("g", True); eje.set_editor_property("b", False); eje.set_editor_property("a", False)   # franjas a lo largo de Y (norte-sur)
    seno = crear(unreal.MaterialExpressionSine, -1000, 0)
    seno.set_editor_property("period", 1000.0)                      # 10 m = dos franjas de 5 m (la posición está en cm)
    duro = crear(unreal.MaterialExpressionMultiply, -800, 0)
    duro.set_editor_property("const_b", 12.0)                        # endurece el borde de la franja
    medio = crear(unreal.MaterialExpressionAdd, -600, 0)
    medio.set_editor_property("const_b", 1.0)
    mitad = crear(unreal.MaterialExpressionMultiply, -450, 0)
    mitad.set_editor_property("const_b", 0.5)
    franja = crear(unreal.MaterialExpressionSaturate, -300, 0)
    claro = crear(unreal.MaterialExpressionConstant3Vector, -450, 150)
    claro.set_editor_property("constant", unreal.LinearColor(0.095, 0.24, 0.04, 1))
    oscuro = crear(unreal.MaterialExpressionConstant3Vector, -450, 280)
    oscuro.set_editor_property("constant", unreal.LinearColor(0.040, 0.105, 0.018, 1))
    mezcla = crear(unreal.MaterialExpressionLinearInterpolate, -150, 100)
    ruido = crear(unreal.MaterialExpressionNoise, -700, 450)
    ruido.set_editor_property("noise_function", unreal.NoiseFunction.NOISEFUNCTION_GRADIENT_ALU)   # el de por defecto dibujaba grietas (voronoi)
    ruido.set_editor_property("scale", 0.05)
    ruido.set_editor_property("levels", 3)
    ruido.set_editor_property("turbulence", True)
    ruido.set_editor_property("output_min", 0.82)
    ruido.set_editor_property("output_max", 1.12)
    var = crear(unreal.MaterialExpressionMultiply, 100, 150)
    rug = crear(unreal.MaterialExpressionConstant, 100, 350)
    rug.set_editor_property("r", 0.95)
    mel.connect_material_expressions(pos, "", eje, "")
    mel.connect_material_expressions(eje, "", seno, "")
    mel.connect_material_expressions(seno, "", duro, "A")
    mel.connect_material_expressions(duro, "", medio, "A")
    mel.connect_material_expressions(medio, "", mitad, "A")
    mel.connect_material_expressions(mitad, "", franja, "")
    mel.connect_material_expressions(oscuro, "", mezcla, "A")
    mel.connect_material_expressions(claro, "", mezcla, "B")
    mel.connect_material_expressions(franja, "", mezcla, "Alpha")
    mel.connect_material_expressions(mezcla, "", var, "A")
    mel.connect_material_expressions(ruido, "", var, "B")
    mel.connect_material_property(var, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(rug, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(mat)
    biblioteca.save_loaded_asset(mat)
    return mat


def material_translucido(nombre, color, opacidad=0.25):
    """Material translúcido (acrílico, vidrio): instancia de M_Translucido con Color y Opacidad."""
    ruta_base = CARPETA + "/Materiales/M_Translucido"
    if biblioteca.does_asset_exist(ruta_base):
        base = unreal.load_asset(ruta_base)
    else:
        base = herramientas.create_asset("M_Translucido", CARPETA + "/Materiales", unreal.Material, unreal.MaterialFactoryNew())
        base.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
        c = mel.create_material_expression(base, unreal.MaterialExpressionVectorParameter, -400, 0)
        c.set_editor_property("parameter_name", "Color")
        o = mel.create_material_expression(base, unreal.MaterialExpressionScalarParameter, -400, 200)
        o.set_editor_property("parameter_name", "Opacidad")
        o.set_editor_property("default_value", 0.25)
        r = mel.create_material_expression(base, unreal.MaterialExpressionConstant, -400, 320)
        r.set_editor_property("r", 0.05)
        mel.connect_material_property(c, "", unreal.MaterialProperty.MP_BASE_COLOR)
        mel.connect_material_property(o, "", unreal.MaterialProperty.MP_OPACITY)
        mel.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS)
        mel.recompile_material(base)
        biblioteca.save_loaded_asset(base)
    ruta = CARPETA + "/Materiales/MI_" + nombre
    if biblioteca.does_asset_exist(ruta):
        return unreal.load_asset(ruta)
    mi = herramientas.create_asset("MI_" + nombre, CARPETA + "/Materiales", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, base)
    mel.set_material_instance_vector_parameter_value(mi, "Color", unreal.LinearColor(color[0], color[1], color[2], 1))
    mel.set_material_instance_scalar_parameter_value(mi, "Opacidad", opacidad)
    biblioteca.save_loaded_asset(mi)
    return mi


# ------------------------------------------------------------------------------------------------ actores simples
def forma(nombre_forma, etiqueta, centro, escala, mat, guinada_grados=0.0, carpeta="Cancha", rot=None):
    """Forma básica del motor (Cube, Cylinder, Plane, Sphere: miden 100 cm) con su escala en m y su material."""
    a = actores.spawn_actor_from_class(unreal.StaticMeshActor, centro, unreal.Rotator(*(rot or (0, 0, guinada_grados))))   # rot = (roll, pitch, yaw) de Unreal
    a.static_mesh_component.set_static_mesh(unreal.load_asset(FORMAS + nombre_forma))
    a.set_actor_scale3d(unreal.Vector(*escala))
    a.static_mesh_component.set_material(0, mat)
    a.set_actor_label(etiqueta)
    a.set_folder_path(carpeta)
    return a


def caja(etiqueta, cx, cy, cz, largo, ancho, alto, mat, psi=0.0, carpeta="Cancha"):
    """Caja de largo x ancho x alto (m) centrada en (cx, cy, cz) de la simulación, girada psi (rad)."""
    return forma("Cube", etiqueta, ue(cx, cy, cz), (largo, ancho, alto), mat, guinada(psi), carpeta)


def panel_v(nombre, xv, yv, abre_al_sur, mats):
    """Una V de 90° de dos paneles de ALA x ALTO_PANEL, con marco y bolsas de arena en los 3 pies (D-051, D-066)."""
    tablero, marco, arena = mats
    s = -1 if abre_al_sur else 1
    d = ALA / math.sqrt(2)
    for lado in (-1, 1):
        xb, yb = xv + lado * d, yv + s * d
        cx, cy, psi = (xv + xb) / 2, (yv + yb) / 2, math.atan2(yb - yv, xb - xv)
        caja(f"{nombre}_marco", cx, cy, ALTO_PANEL / 2 + 0.03, ALA, GROSOR_PANEL, ALTO_PANEL - 0.04, marco, psi, "Paneles")             # marco negro (la tabla blanca sobresale 1 cm por cada cara)
        caja(f"{nombre}_panel_{'izq' if lado < 0 else 'der'}", cx, cy, ALTO_PANEL / 2 + 0.03, ALA - 2 * 0.04, GROSOR_PANEL + 0.02, ALTO_PANEL - 0.04 - 2 * 0.04, tablero, psi, "Paneles")
        caja(f"{nombre}_bolsa", xb, yb, 0.07, 0.45, 0.30, 0.14, arena, psi, "Paneles")
    caja(f"{nombre}_bolsa_vertice", xv, yv, 0.07, 0.45, 0.30, 0.14, arena, 0.0, "Paneles")


def paneles_de_foto(paneles, mats):
    """Los paneles tal como vienen en la repetición: [x1, y1, x2, y2, alto] (la verdad de esa partida)."""
    tablero, marco, _ = mats
    for i, (x1, y1, x2, y2, h) in enumerate(paneles):
        L, psi = math.hypot(x2 - x1, y2 - y1), math.atan2(y2 - y1, x2 - x1)
        caja(f"panel_{i}_marco", (x1 + x2) / 2, (y1 + y2) / 2, h / 2, L, GROSOR_PANEL, h, marco, psi, "Paneles")
        caja(f"panel_{i}", (x1 + x2) / 2, (y1 + y2) / 2, h / 2, L - 0.08, GROSOR_PANEL + 0.02, h - 0.08, tablero, psi, "Paneles")


def dron(etiqueta="Dron", z_centro=3.3):
    """El dron real hecho con primitivas, desde modelo_dron/dron_real.json (lo genera dron_real.py; fotos en 08_EVIDENCIA).
    Marco del modelo: x adelante, y izquierda, z arriba, centro = placa del medio del chasis."""
    import json
    import os
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "modelo_dron", "dron_real.json")
    with open(ruta, encoding="utf-8") as f:
        modelo = json.load(f)
    # La raíz es un punto SIN forma y con escala 1: Sequencer escribe escala 1 en lo que mueve, y si la raíz tuviera la del
    # cuerpo, todas las piezas hijas se agrandarían (el dron salía gigante).
    raiz = actores.spawn_actor_from_class(unreal.StaticMeshActor, ue(0, 0, z_centro), unreal.Rotator(0, 0, 0))
    raiz.set_actor_label(etiqueta)
    raiz.set_folder_path("Dron")
    mats = {}
    piezas = []
    var = os.environ.get("DRONIA_DRON", "plus")                                     # minimo (G) | plus (H) | gimbal (el de antes)
    grupos = {}
    if var == "plus":                                                               # pan y tilt: dos puntos sin forma que Sequencer puede girar (Dron_rep_pan y _tilt)
        for g in ("pan", "tilt"):
            pv = modelo["pivotes_plus_abajo" if os.environ.get("DRONIA_PAN_TILT") == "abajo" else "pivotes_plus"][g]
            a = actores.spawn_actor_from_class(unreal.StaticMeshActor, ue(pv[0], pv[1], z_centro + pv[2]), unreal.Rotator(0, 0, 0))
            a.set_actor_label(f"{etiqueta}_{g}")
            a.set_folder_path("Dron")
            grupos[g] = a
        grupos["tilt"].attach_to_actor(grupos["pan"], "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
        grupos["pan"].attach_to_actor(raiz, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
    clave = {"minimo": "piezas", "plus": "piezas_plus_abajo" if os.environ.get("DRONIA_PAN_TILT") == "abajo" else "piezas_plus", "gimbal": "piezas_gimbal"}.get(var, "piezas")
    for p in modelo[clave]:
        col = tuple(modelo["colores"][p["color"]])
        if p["color"] not in mats:
            mats[p["color"]] = (material_translucido("Dron_" + p["color"], col, 0.22) if p.get("translucido")
                                else material("Dron_" + p["color"], col, 0.25 if p["color"] in ("carbono", "rojo", "espuma") else 0.5,
                                              0.0))
        x, y, z = p["centro"]
        yaw, incl = p.get("yaw", 0.0), p.get("inclinacion", 0.0)
        if p["forma"] == "caja":
            escala, forma_ue, rot = tuple(p["tam"]), "Cube", (0.0, 0.0, -yaw)
        else:
            d, h = p["tam"]
            escala, forma_ue = (d, d, h), "Cylinder"
            eje = p.get("eje", "z")
            rot = (0.0, 90.0, -yaw) if eje == "x" else ((90.0, 0.0, -yaw) if eje == "y" else (incl, 0.0, -yaw))
        piezas.append((p.get("grupo"), forma(forma_ue, f"{etiqueta}_{p['nombre']}", ue(x, y, z_centro + z), escala, mats[p["color"]], 0.0, "Dron", rot=rot)))
    for grupo, pz in piezas:
        pz.attach_to_actor(grupos.get(grupo, raiz), "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
    return raiz


def persona(etiqueta, estatura, color):
    """Persona provisional (cilindro de su estatura) hasta tener los MetaHumans; ver PLAN_UNREAL.md, paso 8."""
    return forma("Cylinder", etiqueta, ue(0, 0, estatura / 2), (0.45, 0.45, estatura), material("Persona_" + etiqueta, color, 0.7), 0.0, "Personas")


# ------------------------------------------------------------------------------------------------ cielo y luz
def cielo_y_luz():
    """Sol, cielo físico, luz del cielo en tiempo real, niebla y nubes (Lumen, como en el paso 9 del plan)."""
    import os
    noche = os.environ.get("DRONIA_NOCHE") == "1"                                     # modo noche: el sol bajo el horizonte, una luna tenue y las luminarias del campus encendidas
    sol = actores.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 1000), unreal.Rotator(0, 25 if noche else -38, 215))
    sol.set_actor_label("Sol")
    luz = sol.get_component_by_class(unreal.DirectionalLightComponent)
    luz.set_editor_property("intensity", 7.0)
    if noche:
        luna = actores.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 1000), unreal.Rotator(0, -55, 40))
        luna.set_actor_label("Luna")
        lc = luna.get_component_by_class(unreal.DirectionalLightComponent)
        lc.set_editor_property("intensity", 0.35)
        lc.set_editor_property("light_color", unreal.Color(150, 175, 255, 255))
        lc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    luz.set_editor_property("atmosphere_sun_light", True)
    luz.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    actores.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0)).set_actor_label("Atmosfera")
    cielo = actores.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 500))
    cielo.set_actor_label("Luz_del_cielo")
    c = cielo.get_component_by_class(unreal.SkyLightComponent)
    c.set_editor_property("real_time_capture", True)
    if noche:
        c.set_editor_property("intensity", 0.25)
    c.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    actores.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0)).set_actor_label("Niebla")
    nubes = actores.spawn_actor_from_class(unreal.VolumetricCloud, unreal.Vector(0, 0, 0))
    nubes.set_actor_label("Nubes")
    mat_nubes = unreal.load_asset("/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst")
    if mat_nubes:
        nubes.get_component_by_class(unreal.VolumetricCloudComponent).set_editor_property("material", mat_nubes)
    for a in (sol,):
        a.set_folder_path("Luz")


# ------------------------------------------------------------------------------------------------ cancha
def cancha():
    """Césped, líneas y arcos de la cancha de 90 x 60 m (por medir), con la zona de IA en el centro de la mitad este."""
    cesped = material_cesped()
    cal = material("Cal", (0.85, 0.85, 0.82), 0.9)
    forma("Plane", "Cesped", ue(0, 0, 0), (400, 400, 1), cesped)
    LX, LY, CX = 90.0, 60.0, -22.5
    x0, x1 = CX - LX / 2, CX + LX / 2

    def linea(xa, ya, xb, yb, n="Linea"):
        L = math.hypot(xb - xa, yb - ya)
        caja(n, (xa + xb) / 2, (ya + yb) / 2, 0.003, L + 0.12, 0.12, 0.006, cal, math.atan2(yb - ya, xb - xa), "Cancha/Lineas")

    def rect(xa, ya, xb, yb):
        linea(xa, ya, xb, ya); linea(xb, ya, xb, yb); linea(xb, yb, xa, yb); linea(xa, yb, xa, ya)

    rect(x0, -LY / 2, x1, LY / 2)
    linea(CX, -LY / 2, CX, LY / 2)
    for xa, s in ((x0, 1), (x1, -1)):
        rect(xa, -20.15, xa + s * 16.5, 20.15)
        rect(xa, -9.15, xa + s * 5.5, 9.15)
    n = 64
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        linea(CX + 9.15 * math.cos(a0), 9.15 * math.sin(a0), CX + 9.15 * math.cos(a1), 9.15 * math.sin(a1), "Circulo")
    tubo = material("Tubo", (0.9, 0.9, 0.9), 0.3, 0.2)
    for xa in (x0, x1):
        for y in (-3.66, 3.66):
            forma("Cylinder", "Arco_poste", ue(xa, y, 1.22), (0.12, 0.12, 2.44), tubo, 0.0, "Cancha/Arcos")
        caja("Arco_travesano", xa, 0, 2.44, 0.12, 7.44, 0.12, tubo, 0.0, "Cancha/Arcos")


def mats_paneles():
    return (material("PanelBlanco", (0.9, 0.9, 0.88), 0.7), material("MarcoNegro", (0.012, 0.012, 0.012), 0.5, 0.0), material("Arena", (0.35, 0.27, 0.16), 1.0))


def nivel_nuevo(ruta):
    """Crea el nivel; si ya existe NO lo toca (ahí pueden estar los árboles y MetaHumans que puso Brahian) y devuelve None."""
    if biblioteca.does_asset_exist(ruta):
        unreal.log_warning(f"DRONIA: {ruta} ya existe; no se rehace (bórrelo a mano si quiere armarlo de nuevo)")
        return None
    nivel = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    nivel.new_level(ruta)
    return nivel
