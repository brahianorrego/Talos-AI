# Video de la cancha V17 (D-051) con personas de Quaternius (CC0), renderizado con la RTX (fase V6 del plan del visor).
# Reproduce la misma escena de ejemplo que la vista previa "cancha" del visor (v16/simulacion/visor/previa.js, ESCENAS.cancha):
# el dron entra por el sur y rodea las V; el ladrón, agachado detrás de V1, corre a esconderse detrás de V2; un civil
# cruza caminando a 8 m. NO es una partida de la IA: es una coreografía fija para mostrar el escenario.
# Coordenadas como la simulación: x al este, y al norte, z arriba (m); la zona de IA de 30 × 30 m centrada en el origen.
#
# Uso: blender --background --factory-startup --python video_cancha_v17.py -- <recursos_quaternius> <salida> [opciones]
#   --desde S --hasta S   tramo de la escena (s)          --fps N        cuadros por segundo (24)
#   --muestras N          muestras de Cycles (32)         --ancho N --alto N  resolución (1920 × 1080)
#   --cuadros a,b,c       solo esos cuadros, como PNG (prueba); si no, el video completo en MP4
#   --guardar archivo.blend   guarda la escena armada (para abrirla en Blender)
import bpy, sys, os, math, random, argparse
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
ap = argparse.ArgumentParser()
ap.add_argument("recursos"); ap.add_argument("salida")
ap.add_argument("--desde", type=float, default=0); ap.add_argument("--hasta", type=float, default=80)
ap.add_argument("--fps", type=int, default=24); ap.add_argument("--muestras", type=int, default=32)
ap.add_argument("--ancho", type=int, default=1920); ap.add_argument("--alto", type=int, default=1080)
ap.add_argument("--cuadros", default=""); ap.add_argument("--guardar", default="")
O = ap.parse_args(a)
R = O.recursos
NAT = R + "/stylized-nature-megakit/glTF/"
UMC = R + "/ultimate-modular-characters/glTF/"
rnd = random.Random(17)

# ------------------------------------------------------------------------------------------------ escena de ejemplo
# (t, x, y) como en previa.js
DRON = [(0, 0, -12), (10, -2, -6), (24, -9, 1), (34, -6, 6), (46, 4, 6), (58, 10, 0), (70, 6, -6), (80, 0, -12)]
LADRON = [(0, -5, 0.9), (40, -5, 0.9), (43, 5, -0.9), (80, 5, -0.9)]
CIVIL = [(0, -15, 8), (40, 15, 8), (42, 15, 8), (80, -15, 8)]
Z_DRON = 3.3


def recorrido(pts, t):
    for (t0, x0, y0), (t1, x1, y1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            f = (t - t0) / max(t1 - t0, 1e-6)
            return x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, (x1 - x0) / max(t1 - t0, 1e-6), (y1 - y0) / max(t1 - t0, 1e-6)
    t0, x0, y0 = pts[-1]
    return x0, y0, 0.0, 0.0


# ------------------------------------------------------------------------------------------------ mundo
bpy.ops.wm.read_factory_settings(use_empty=True)
esc = bpy.context.scene
esc.render.fps = O.fps
for lib in ("animaciones_UMC_UAL1.blend", "animaciones_UMC_UAL2.blend"):
    with bpy.data.libraries.load(R + "/" + lib) as (src, dst):
        dst.actions = list(src.actions)


def material(nombre, color, rug=0.8, metal=0.0):
    m = bpy.data.materials.new(nombre); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rug; b.inputs["Metallic"].default_value = metal
    return m


# cielo físico (con respaldo a un color si esta versión no trae el modelo)
mundo = bpy.data.worlds.new("cielo"); mundo.use_nodes = True; esc.world = mundo
nt = mundo.node_tree
try:
    cielo = nt.nodes.new("ShaderNodeTexSky")
    cielo.sun_elevation = math.radians(32); cielo.sun_rotation = math.radians(215)
    nt.links.new(cielo.outputs["Color"], nt.nodes["Background"].inputs["Color"])
    nt.nodes["Background"].inputs["Strength"].default_value = 0.25
except Exception as e:
    print("cielo simple:", e)
    nt.nodes["Background"].inputs[0].default_value = (0.55, 0.7, 0.95, 1)
bpy.ops.object.light_add(type="SUN"); sol = bpy.context.object
sol.data.energy = 2.6; sol.data.angle = math.radians(1.5)
sol.rotation_euler = (math.radians(58), 0, math.radians(215))

# césped: color con manchas (ruido) y relieve fino
bpy.ops.mesh.primitive_plane_add(size=400)
piso = bpy.context.object
m = bpy.data.materials.new("cesped"); m.use_nodes = True; n = m.node_tree.nodes; l = m.node_tree.links
b = n["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.95
ruido = n.new("ShaderNodeTexNoise"); ruido.inputs["Scale"].default_value = 0.08
rampa = n.new("ShaderNodeValToRGB")
rampa.color_ramp.elements[0].color = (0.035, 0.09, 0.015, 1); rampa.color_ramp.elements[1].color = (0.07, 0.15, 0.03, 1)
l.new(ruido.outputs["Fac"], rampa.inputs["Fac"]); l.new(rampa.outputs["Color"], b.inputs["Base Color"])
fino = n.new("ShaderNodeTexNoise"); fino.inputs["Scale"].default_value = 60
relieve = n.new("ShaderNodeBump"); relieve.inputs["Strength"].default_value = 0.25
l.new(fino.outputs["Fac"], relieve.inputs["Height"]); l.new(relieve.outputs["Normal"], b.inputs["Normal"])
piso.data.materials.append(m)

# líneas de la cancha (90 × 60 m, por medir; centro en x = -22.5 para que la zona quede en el centro de la mitad este)
cal = material("cal", (0.92, 0.92, 0.9), 0.9)
LX, LY, CX = 90, 60, -22.5
x0, x1 = CX - LX / 2, CX + LX / 2


def linea(xa, ya, xb, yb, ancho=0.12):
    L = math.hypot(xb - xa, yb - ya)
    bpy.ops.mesh.primitive_plane_add(size=1, location=((xa + xb) / 2, (ya + yb) / 2, 0.006))
    o = bpy.context.object; o.scale = (L + ancho, ancho, 1); o.rotation_euler[2] = math.atan2(yb - ya, xb - xa)
    o.data.materials.append(cal)


def caja(xa, ya, xb, yb):
    linea(xa, ya, xb, ya); linea(xb, ya, xb, yb); linea(xb, yb, xa, yb); linea(xa, yb, xa, ya)


caja(x0, -LY / 2, x1, LY / 2); linea(CX, -LY / 2, CX, LY / 2)
for xa, s in ((x0, 1), (x1, -1)):
    caja(xa, -20.15, xa + s * 16.5, 20.15); caja(xa, -9.15, xa + s * 5.5, 9.15)
N = 96
for k in range(N):
    a0, a1 = 2 * math.pi * k / N, 2 * math.pi * (k + 1) / N
    linea(CX + 9.15 * math.cos(a0), 9.15 * math.sin(a0), CX + 9.15 * math.cos(a1), 9.15 * math.sin(a1))
# arcos
tubo = material("tubo", (0.95, 0.95, 0.95), 0.3, 0.2)
for xa in (x0, x1):
    for y in (-3.66, 3.66):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=2.44, location=(xa, y, 1.22)); bpy.context.object.data.materials.append(tubo)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=7.44, location=(xa, 0, 2.44), rotation=(math.pi / 2, 0, 0))
    bpy.context.object.data.materials.append(tubo)

# paneles de exposición en V de 90° (alas de 1.5 m, 2.25 m de alto, D-066) con bolsas de arena
tablero = material("tablero", (0.86, 0.85, 0.82), 0.7)
marco = material("marco", (0.7, 0.72, 0.75), 0.3, 0.9)
arena = material("arena", (0.42, 0.33, 0.2), 1.0)
ALA, ALTO = 1.5, 2.25
d = ALA / math.sqrt(2)
for xv, s in ((-5, -1), (5, 1)):          # V1 abre al sur, V2 al norte
    for lado in (-1, 1):
        xa, ya, xb, yb = xv, 0, xv + lado * d, s * d
        c = ((xa + xb) / 2, (ya + yb) / 2); rot = math.atan2(yb - ya, xb - xa)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(*c, ALTO / 2 + 0.03)); p = bpy.context.object
        p.scale = (ALA - 0.04, 0.03, ALTO - 0.1); p.rotation_euler[2] = rot; p.data.materials.append(tablero)
        for z in (0.06, ALTO - 0.02):
            bpy.ops.mesh.primitive_cube_add(size=1, location=(*c, z)); q = bpy.context.object
            q.scale = (ALA, 0.05, 0.04); q.rotation_euler[2] = rot; q.data.materials.append(marco)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(xb, yb, 0.07)); q = bpy.context.object
        q.scale = (0.45, 0.3, 0.14); q.rotation_euler[2] = rnd.random() * 3; q.data.materials.append(arena)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(xv, 0, 0.07)); q = bpy.context.object
    q.scale = (0.45, 0.3, 0.14); q.data.materials.append(arena)


# naturaleza de Quaternius: se importa cada modelo una vez y se instancia (copias enlazadas)
def modelo(nombre):
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=NAT + nombre + ".gltf")
    nuevos = [o for o in bpy.data.objects if o not in antes]
    col = bpy.data.collections.new(nombre)
    for o in nuevos:
        for c in o.users_collection:
            c.objects.unlink(o)
        col.objects.link(o)
    return col


def instancia(col, x, y, giro=0.0, esc_=1.0):
    e = bpy.data.objects.new(col.name + "_i", None)
    e.instance_type = "COLLECTION"; e.instance_collection = col
    e.location = (x, y, 0); e.rotation_euler[2] = giro; e.scale = (esc_,) * 3
    esc.collection.objects.link(e)


arboles = [modelo(f"CommonTree_{k}") for k in (1, 2, 3, 4, 5)] + [modelo("TwistedTree_1"), modelo("Pine_2")]
arbustos = [modelo("Bush_Common"), modelo("Bush_Common_Flowers")]
pastos = [modelo("Grass_Common_Short"), modelo("Grass_Wispy_Short")]   # fuera de la escena: solo se ven sus copias


def borde(xa, ya, xb, yb):
    L = math.hypot(xb - xa, yb - ya); k = 0.0
    nx, ny = -(yb - ya) / L, (xb - xa) / L
    while k <= L:
        f = k / L; fuera = 4 + rnd.random() * 5 + (8 if rnd.random() < 0.45 else 0)
        instancia(rnd.choice(arboles), xa + (xb - xa) * f + nx * fuera, ya + (yb - ya) * f + ny * fuera,
                  rnd.random() * 6.28, 0.9 + rnd.random() * 0.6)
        if rnd.random() < 0.5:
            instancia(rnd.choice(arbustos), xa + (xb - xa) * f + nx * (fuera - 2.5), ya + (yb - ya) * f + ny * (fuera - 2.5), rnd.random() * 6.28)
        k += 5 + rnd.random() * 3


borde(x0, LY / 2, x1, LY / 2); borde(x1, LY / 2, x1, -LY / 2); borde(x1, -LY / 2, x0, -LY / 2); borde(x0, -LY / 2, x0, LY / 2)
for _ in range(14000):                             # matas de pasto bajas alrededor de la zona de IA (donde mira la cámara)
    x, y = rnd.uniform(-24, 24), rnd.uniform(-24, 24)
    instancia(rnd.choice(pastos), x, y, rnd.random() * 6.28, 0.12 + rnd.random() * 0.1)   # césped de cancha: matas bajas


# ------------------------------------------------------------------------------------------------ dron real (modelo_dron/dron_real.py)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "modelo_dron"))
import dron_blender                                  # noqa: E402  (el mismo modelo que usan Unreal y el visor)
DRONE = dron_blender.construir("dron")


# ------------------------------------------------------------------------------------------------ personas
def persona(archivo):
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=UMC + archivo)
    arm = next(o for o in bpy.data.objects if o not in antes and o.type == "ARMATURE")
    for pb in arm.pose.bones:
        for c in pb.constraints:
            c.mute = True
    arm.animation_data_create(); arm.animation_data.action = None
    for t in list(arm.animation_data.nla_tracks):
        arm.animation_data.nla_tracks.remove(t)
    return arm


def tira(arm, accion, f0, f1, mezcla=6):
    """Pone la animación `accion` (redirigida, en bucle) de f0 a f1 en una pista NLA propia, con fundido."""
    act = bpy.data.actions[accion + "_UMC"]
    pista = arm.animation_data.nla_tracks.new()
    s = pista.strips.new(accion, int(f0), act)
    if act.slots:
        s.action_slot = act.slots[0]
    largo = act.frame_range[1] - act.frame_range[0]
    s.repeat = max((f1 - f0) / max(largo, 1), 0.05)
    s.blend_in = s.blend_out = mezcla
    s.use_auto_blend = False
    s.extrapolation = "NOTHING"


fps = O.fps
F = lambda t: 1 + round(t * fps)
T_FIN = O.hasta
ladron, civil = persona("Casual_Hoodie.gltf"), persona("Worker.gltf")
# ladrón: agachado escondido, corre de V1 a V2 entre los 40 y 43 s, otra vez agachado
tira(ladron, "Crouch_Idle_Loop", F(0), F(40.2)); tira(ladron, "Sprint_Loop", F(39.8), F(43.2)); tira(ladron, "Crouch_Idle_Loop", F(42.8), F(81))
# civil: camina, se para a mirar el dron (40-42 s) y vuelve
tira(civil, "Walk_Loop", F(0), F(40.2)); tira(civil, "Idle_TalkingPhone_Loop", F(39.8), F(42.2)); tira(civil, "Walk_Loop", F(41.8), F(81))


def rumbo(vx, vy, previo):
    return math.atan2(vy, vx) + math.pi / 2 if math.hypot(vx, vy) > 0.1 else previo   # el personaje mira a +y en reposo


psi = None; gl = gc = 0.0
for f in range(F(0), F(T_FIN) + 1):
    t = (f - 1) / fps
    dx, dy, dvx, dvy = recorrido(DRON, t)
    lx, ly, lvx, lvy = recorrido(LADRON, t)
    cx, cy, cvx, cvy = recorrido(CIVIL, t)
    obj = math.atan2(ly - dy, lx - dx)
    psi = obj if psi is None else psi + math.remainder(obj - psi, 2 * math.pi) * 0.08
    v = math.hypot(dvx, dvy)
    DRONE.location = (dx, dy, Z_DRON + 0.05 * math.sin(t * 2.3))
    DRONE.rotation_euler = (-0.05 * dvy / max(v, 1e-3) * min(v, 1.5), 0.05 * dvx / max(v, 1e-3) * min(v, 1.5), psi)
    DRONE.keyframe_insert("location", frame=f); DRONE.keyframe_insert("rotation_euler", frame=f)
    # el ladrón escondido mira hacia el dron; corriendo, hacia donde corre
    gl = rumbo(lvx, lvy, math.atan2(dy - ly, dx - lx) + math.pi / 2)
    ladron.location = (lx, ly, 0); ladron.rotation_euler = (0, 0, gl)
    ladron.keyframe_insert("location", frame=f); ladron.keyframe_insert("rotation_euler", frame=f)
    gc = rumbo(cvx, cvy, math.atan2(dy - cy, dx - cx) + math.pi / 2)
    civil.location = (cx, cy, 0); civil.rotation_euler = (0, 0, gc)
    civil.keyframe_insert("location", frame=f); civil.keyframe_insert("rotation_euler", frame=f)

# ------------------------------------------------------------------------------------------------ cámara de cine
# detrás y por encima del dron, mirando el punto medio entre el dron y el ladrón; movimiento suavizado
cam_d = bpy.data.cameras.new("cine"); cam_d.lens = 28
cam = bpy.data.objects.new("cine", cam_d); esc.collection.objects.link(cam); esc.camera = cam
mira = bpy.data.objects.new("mira", None); esc.collection.objects.link(mira)
c = cam.constraints.new("TRACK_TO"); c.target = mira; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
pc = pm = None
for f in range(F(0), F(T_FIN) + 1):
    t = (f - 1) / fps
    dx, dy, *_ = recorrido(DRON, t); lx, ly, *_ = recorrido(LADRON, t)
    ux, uy = dx - lx, dy - ly; L = max(math.hypot(ux, uy), 1e-3)
    objetivo_c = Vector((dx + ux / L * 4.5 + uy / L * 2.0, dy + uy / L * 4.5 - ux / L * 2.0, Z_DRON + 0.6))
    objetivo_m = Vector((dx * 0.4 + lx * 0.6, dy * 0.4 + ly * 0.6, 1.3))
    pc = objetivo_c if pc is None else pc.lerp(objetivo_c, 0.04)
    pm = objetivo_m if pm is None else pm.lerp(objetivo_m, 0.06)
    cam.location = pc; mira.location = pm
    cam.keyframe_insert("location", frame=f); mira.keyframe_insert("location", frame=f)

# ------------------------------------------------------------------------------------------------ render
esc.frame_start, esc.frame_end = F(O.desde), F(O.hasta)
esc.render.engine = "CYCLES"; esc.cycles.device = "GPU"
esc.cycles.samples = O.muestras; esc.cycles.use_denoising = True
pr = bpy.context.preferences.addons["cycles"].preferences; pr.compute_device_type = "OPTIX"; pr.get_devices()
for dv in pr.devices:
    dv.use = dv.type == "OPTIX"
esc.render.resolution_x, esc.render.resolution_y = O.ancho, O.alto
try:
    esc.view_settings.view_transform = "AgX"; esc.view_settings.look = "AgX - Punchy"; esc.view_settings.exposure = -0.6
except Exception:
    pass
esc.render.use_motion_blur = True
if O.guardar:
    bpy.ops.wm.save_as_mainfile(filepath=O.guardar)
if O.cuadros:
    for f in (int(x) for x in O.cuadros.split(",")):
        esc.frame_set(f); esc.render.filepath = f"{O.salida}_{f:05d}.png"
        bpy.ops.render.render(write_still=True)
        print("CUADRO", f, esc.render.filepath)
else:
    # cuadro por cuadro en JPEG: si se corta, al relanzar sigue donde iba (no sobrescribe); luego unir_video.py hace el MP4
    esc.render.image_settings.file_format = "JPEG"; esc.render.image_settings.quality = 92
    esc.render.use_overwrite = False; esc.render.use_placeholder = True
    esc.render.filepath = O.salida
    bpy.ops.render.render(animation=True)
print("LISTO", O.salida)
