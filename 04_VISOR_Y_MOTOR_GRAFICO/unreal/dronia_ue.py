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
ALA, ALTO_PANEL = 1.5, 2.25                         # D-066 (hasta medirlos con cinta)

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


# ------------------------------------------------------------------------------------------------ actores simples
def forma(nombre_forma, etiqueta, centro, escala, mat, guinada_grados=0.0, carpeta="Cancha"):
    """Forma básica del motor (Cube, Cylinder, Plane, Sphere: miden 100 cm) con su escala en m y su material."""
    a = actores.spawn_actor_from_class(unreal.StaticMeshActor, centro, unreal.Rotator(0, 0, guinada_grados))
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
        caja(f"{nombre}_panel_{'izq' if lado < 0 else 'der'}", cx, cy, ALTO_PANEL / 2 + 0.03, ALA - 0.04, 0.035, ALTO_PANEL - 0.08, tablero, psi, "Paneles")
        for z in (0.06, ALTO_PANEL - 0.02):
            caja(f"{nombre}_marco", cx, cy, z, ALA, 0.05, 0.04, marco, psi, "Paneles")
        caja(f"{nombre}_bolsa", xb, yb, 0.07, 0.45, 0.30, 0.14, arena, psi, "Paneles")
    caja(f"{nombre}_bolsa_vertice", xv, yv, 0.07, 0.45, 0.30, 0.14, arena, 0.0, "Paneles")


def paneles_de_foto(paneles, mats):
    """Los paneles tal como vienen en la repetición: [x1, y1, x2, y2, alto] (la verdad de esa partida)."""
    tablero, marco, _ = mats
    for i, (x1, y1, x2, y2, h) in enumerate(paneles):
        L, psi = math.hypot(x2 - x1, y2 - y1), math.atan2(y2 - y1, x2 - x1)
        caja(f"panel_{i}", (x1 + x2) / 2, (y1 + y2) / 2, h / 2, L, 0.035, h, tablero, psi, "Paneles")
        caja(f"panel_{i}_marco", (x1 + x2) / 2, (y1 + y2) / 2, h - 0.02, L, 0.05, 0.04, marco, psi, "Paneles")


def dron(etiqueta="Dron"):
    """Cuadricóptero de ~0.5 m hecho con formas (provisional, hasta tener el modelo del dron real)."""
    carbono, rojo, gris = material("Carbono", (0.02, 0.02, 0.025), 0.4), material("Rojo", (0.55, 0.03, 0.03), 0.4), material("Gris", (0.5, 0.5, 0.52), 0.35, 0.6)
    # La raíz es un punto SIN forma y con escala 1: Sequencer escribe escala 1 en lo que mueve, y si la raíz tuviera la del
    # cuerpo, todas las piezas hijas se agrandarían (el dron salía gigante).
    raiz = actores.spawn_actor_from_class(unreal.StaticMeshActor, ue(0, 0, 3.3), unreal.Rotator(0, 0, 0))
    raiz.set_actor_label(etiqueta)
    raiz.set_folder_path("Dron")
    piezas = [caja(f"{etiqueta}_cuerpo", 0, 0, 3.3, 0.22, 0.15, 0.06, carbono, 0.0, "Dron")]
    for k in range(4):
        ang = math.radians(45 + 90 * k)
        bx, by = 0.25 * math.cos(ang), 0.25 * math.sin(ang)
        piezas.append(caja(f"{etiqueta}_brazo", bx / 2, by / 2, 3.3, 0.26, 0.025, 0.02, rojo if k < 2 else carbono, ang, "Dron"))
        piezas.append(forma("Cylinder", f"{etiqueta}_motor", ue(bx, by, 3.33), (0.045, 0.045, 0.04), gris, 0.0, "Dron"))
        piezas.append(forma("Cylinder", f"{etiqueta}_helice", ue(bx, by, 3.355), (0.22, 0.22, 0.004), carbono, 0.0, "Dron"))
    for sy in (-1, 1):
        piezas.append(caja(f"{etiqueta}_pata", 0, sy * 0.09, 3.21, 0.2, 0.012, 0.012, carbono, 0.0, "Dron"))
    piezas.append(caja(f"{etiqueta}_camara", 0.12, 0, 3.24, 0.05, 0.06, 0.05, gris, 0.0, "Dron"))
    for p in piezas:
        p.attach_to_actor(raiz, "", unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
    return raiz


def persona(etiqueta, estatura, color):
    """Persona provisional (cilindro de su estatura) hasta tener los MetaHumans; ver PLAN_UNREAL.md, paso 8."""
    return forma("Cylinder", etiqueta, ue(0, 0, estatura / 2), (0.45, 0.45, estatura), material("Persona_" + etiqueta, color, 0.7), 0.0, "Personas")


# ------------------------------------------------------------------------------------------------ cielo y luz
def cielo_y_luz():
    """Sol, cielo físico, luz del cielo en tiempo real, niebla y nubes (Lumen, como en el paso 9 del plan)."""
    sol = actores.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 1000), unreal.Rotator(0, -38, 215))
    sol.set_actor_label("Sol")
    luz = sol.get_component_by_class(unreal.DirectionalLightComponent)
    luz.set_editor_property("intensity", 9.0)
    luz.set_editor_property("atmosphere_sun_light", True)
    luz.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    actores.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0)).set_actor_label("Atmosfera")
    cielo = actores.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 500))
    cielo.set_actor_label("Luz_del_cielo")
    c = cielo.get_component_by_class(unreal.SkyLightComponent)
    c.set_editor_property("real_time_capture", True)
    c.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    actores.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0)).set_actor_label("Niebla")
    actores.spawn_actor_from_class(unreal.VolumetricCloud, unreal.Vector(0, 0, 0)).set_actor_label("Nubes")
    for a in (sol,):
        a.set_folder_path("Luz")


# ------------------------------------------------------------------------------------------------ cancha
def cancha():
    """Césped, líneas y arcos de la cancha de 90 x 60 m (por medir), con la zona de IA en el centro de la mitad este."""
    cesped = material("Cesped", (0.045, 0.11, 0.025), 0.95)
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
    return (material("Panel", (0.78, 0.77, 0.74), 0.7), material("Marco", (0.7, 0.72, 0.75), 0.3, 0.9), material("Arena", (0.35, 0.27, 0.16), 1.0))


def nivel_nuevo(ruta):
    """Crea el nivel; si ya existe NO lo toca (ahí pueden estar los árboles y MetaHumans que puso Brahian) y devuelve None."""
    if biblioteca.does_asset_exist(ruta):
        unreal.log_warning(f"DRONIA: {ruta} ya existe; no se rehace (bórrelo a mano si quiere armarlo de nuevo)")
        return None
    nivel = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    nivel.new_level(ruta)
    return nivel
