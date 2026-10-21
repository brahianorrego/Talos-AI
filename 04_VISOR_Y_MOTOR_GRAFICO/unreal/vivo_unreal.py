# -*- coding: utf-8 -*-
"""
Simulación EN VIVO dentro de Unreal (fase mínima): dibuja la partida que corre en en_vivo.py. No bloquea el editor: se engancha al tick de Slate,
lee los paquetes UDP del puente (puente_unreal.py, 127.0.0.1:8770, 10 Hz) y mueve el dron, el pan-tilt, las personas y los paneles interpolando
entre un paso y el siguiente, así que se ve a la velocidad del motor (30-60 cuadros por segundo) aunque la simulación vaya a 10.
  ejecutar_en_unreal.bat vivo_unreal.py           (abre el editor y empieza solo; antes: en_vivo.py y puente_unreal.py, o VIVO_UNREAL.bat)
Cada 5 s escribe en el log "DRONIA VIVO fps ...". Cámara: detrás del dron (por defecto), o DRONIA_CAMARA=cenital|dron.
"""
import math
import os
import socket
import sys
import json
import time

import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import dronia_ue as D  # noqa: E402
import maniquies_unreal as MQ  # noqa: E402

PUERTO = int(os.environ.get("DRONIA_UDP", "8770"))
CAMARA = os.environ.get("DRONIA_CAMARA", "seguir")
ANIM = "/Game/Characters/Mannequins/Anims/Unarmed/"
N_PANELES = 4                       # entorno.py: hasta 4 muros
ROLES = ["ladron", "peaton", "peaton", "peaton"]
COLORES = {"ladron": (0.85, 0.12, 0.12), "peaton": (0.45, 0.55, 0.68)}

sock = None                                                 # se abre en preparar() (así el archivo se puede importar para probar la lógica de las posturas)

est = {"dron": None, "pan": None, "tilt": None, "pers": {}, "prev": None, "sig": None, "t_sig": 0.0, "dur": 0.1, "paneles": [], "cam": None, "fps_t": time.time(), "fps_n": 0, "ult": 0.0}


def preparar():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", PUERTO))
    sock.setblocking(False)
    unreal.EditorLoadingAndSavingUtils.load_map(D.CARPETA + "/Mapas/Cancha_V17")
    for a in D.actores.get_all_level_actors():                                     # lo provisional del nivel: el dron fijo y los paneles de 90°
        carpeta = str(a.get_folder_path())
        if a.get_actor_label().startswith("Dron") or carpeta in ("Paneles",) or carpeta.startswith(("Repeticion", "Dron", "Vivo")):
            D.actores.destroy_actor(a)
    est["dron"] = D.dron("Dron_vivo", 2.0)
    # Todo se crea UNA vez aquí; después solo se mueven transformaciones (crear o destruir mallas con el render en marcha tumbó el editor: Assertion VertexFactory...IsReadyForStaticMeshCaching)
    tablero, marco, _ = D.mats_paneles()
    est["pool_paneles"] = [(D.caja(f"Vivo_panel_{i}", 0, 0, -50, 1, 1, 1, tablero, 0.0, "Vivo"), D.caja(f"Vivo_panel_{i}_marco", 0, 0, -50, 1, 1, 1, marco, 0.0, "Vivo")) for i in range(N_PANELES)]
    est["n_listo"], est["ticks"] = 0, 0
    preparar_camaras()
    for c in ("r.Streaming.FullyLoadUsedTextures 1", "r.Streaming.PoolSize 3000"):       # que las texturas lleguen a su máxima resolución (sin esto se ven borrosas un buen rato)
        unreal.SystemLibrary.execute_console_command(None, c)
    for g in ("pan", "tilt"):
        est[g] = next((a for a in D.actores.get_all_level_actors() if a.get_actor_label() == f"Dron_vivo_{g}"), None)
    try:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_set_game_view(True)      # sin iconos ni rejilla del editor
    except Exception:                                                                              # noqa: BLE001
        pass
    anims()                                                  # las animaciones también se cargan ya, no a mitad de la partida
    unreal.log("DRONIA VIVO: escuchando UDP %d" % PUERTO)


# ---------------------------------------------------------------------------------------------------------------- cámaras del dron (lo que ve el dron)
# CSI#1: en el pan-tilt, 68.3° x 54.0° (640 x 480 da 68.3 x 53.9), inclinación -2.4° de montaje + el tilt. CSI#2: mira al piso (-90°), mismo modelo de cámara.
# Cada una es una SceneCapture que se redibuja ~10 Hz (CSI#2 ~5 Hz) y se guarda como JPG en _cache/cam/; la estación las muestra como la imagen de la cámara.
CAM_DIR = os.path.join(AQUI, "_cache", "cam")
HFOV_CSI, MONTAJE_PITCH = 68.3, -2.4


def preparar_camaras():
    os.makedirs(CAM_DIR, exist_ok=True)
    mundo = unreal.EditorLevelLibrary.get_editor_world()
    est["cams"] = []
    for nombre, (ancho, alto) in (("cam0", (640, 480)), ("cam1", (480, 360))):                     # CSI#2 más pequeña (mismo 4:3: mismo campo de visión)
        rt = unreal.RenderingLibrary.create_render_target2d(mundo, ancho, alto, unreal.TextureRenderTargetFormat.RTF_RGBA8)
        a = D.actores.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0, 0, 0))
        a.set_actor_label("Vivo_" + nombre)
        a.set_folder_path("Vivo")
        c = a.capture_component2d
        c.set_editor_property("texture_target", rt)
        c.set_editor_property("fov_angle", HFOV_CSI)
        c.set_editor_property("capture_every_frame", False)
        c.set_editor_property("capture_on_movement", False)
        c.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
        est["cams"].append({"actor": a, "comp": c, "rt": rt, "archivo": os.path.join(CAM_DIR, nombre + ".jpg"), "t": 0.0, "cada": 0.1 if nombre == "cam0" else 0.2})
    opt = unreal.ImageWriteOptions()
    opt.set_editor_property("format", unreal.DesiredImageFormat.JPG)
    opt.set_editor_property("compression_quality", 85)
    opt.set_editor_property("overwrite_file", True)
    opt.set_editor_property("async_", True)
    est["img_opt"] = opt


def capturar(c, ahora):
    """Pone las dos cámaras donde está el dron (con pan y tilt) y, cuando toca, las redibuja y las guarda."""
    x, y, z, psi = c["d"]
    pan, tilt = c["pan"], c["tilt"]
    for k, cam in enumerate(est.get("cams", [])):
        if ahora - cam["t"] < cam["cada"]:
            continue
        cam["t"] = ahora
        if k == 0:                                                       # CSI#1 al frente, en el pan-tilt
            pos = D.ue(x + 0.12 * math.cos(psi), y + 0.12 * math.sin(psi), z - 0.05)
            rot = unreal.Rotator(0.0, max(-90.0, min(30.0, tilt + MONTAJE_PITCH)), D.guinada(psi) - pan)
        else:                                                            # CSI#2 fija, al piso
            pos = D.ue(x, y, z - 0.12)
            rot = unreal.Rotator(0.0, -90.0, D.guinada(psi))
        cam["actor"].set_actor_location_and_rotation(pos, rot, False, False)
        cam["comp"].capture_scene()
        try:
            unreal.ImageWriteBlueprintLibrary.export_to_disk(cam["rt"], cam["archivo"], est["img_opt"])
        except Exception as e:                                           # noqa: BLE001
            if not est.get("err_cam"):
                est["err_cam"] = True
                unreal.log_warning("DRONIA VIVO: no pude guardar la cámara: " + repr(e))


def cargar_anim(nombre):
    return unreal.load_asset(ANIM + nombre)


def anims():
    if "anim" not in est:
        est["anim"] = {"idle": cargar_anim("MM_Idle"), "walk": cargar_anim("Walk/MF_Unarmed_Walk_Fwd"), "jog": cargar_anim("Jog/MF_Unarmed_Jog_Fwd")}
        est["gal"] = unreal.load_asset(GAL)
    return est["anim"]


# Las posturas salen de la galería (galeria_posturas.py), ya importada como animación: se "recorre" el tiempo de la animación a mano (velocidad de reproducción 0 y set_position).
# Tramos en s dentro de esa animación (suma de GUION): agacharse 9.0-10.2, agachado caminando 10.2-13.2, levantarse 13.2-14.4, recostarse 14.4-16.9, soltar el panel 16.9-18.1,
# gateo (arrancar) 18.1-19.6, gateando 19.6-23.1, de gateo a pie 23.1-24.6, salto 24.6-26.05.
GAL = "/Game/DronIA/Anim/Rep_replay_v17_galeria_1"
SEG = {"agacharse": (9.0, 10.2), "agachado": (10.2, 13.2), "levantarse": (13.2, 14.4), "recostarse": (14.4, 16.9), "soltar_panel": (16.9, 18.1),
       "gateo_ini": (18.1, 19.6), "gateo": (19.6, 23.1), "salir_gateo": (23.1, 24.6), "salto": (24.85, 26.05)}
ENTRADA = {1: "agacharse", 2: "recostarse", 3: "gateo_ini"}                 # de pie -> postura
SALIDA = {1: "levantarse", 2: "soltar_panel", 3: "salir_gateo"}              # postura -> de pie
FIJA = {1: 10.2, 2: 16.9, 3: 19.6}                                           # instante donde la postura queda quieta
BUCLE = {1: ("agachado", 0.8), 3: ("gateo", 0.45)}                           # postura en movimiento: tramo y velocidad (m/s) con la que fue animado


def scrub(p, t):
    comp = p["actor"].skeletal_mesh_component
    if p["anim"] != "gal":
        comp.play_animation(est["gal"], False)
        comp.set_play_rate(0.0)
        p["anim"] = "gal"
    comp.set_position(t, False)


def postura(p, q, dt):
    """Devuelve True si la persona está en una postura especial (agachado, gateo, recostado, salto) y ya puso su pose; False = de pie (caminar/trotar normal)."""
    pos, sz, vel = int(q.get("pos", 0)), float(q.get("sz", 0.0)), math.hypot(*q["v"])
    st = p.setdefault("st", {"pos": 0, "trans": None, "t": 0.0, "bucle": None, "salto": False})
    if st["salto"] or sz > 0.03:                                              # salto: de la fase en el aire hasta la caída, una sola vez (1.2 s)
        if not st["salto"]:
            st.update(salto=True, t=SEG["salto"][0])
        st["t"] += dt
        if st["t"] >= SEG["salto"][1]:
            st.update(salto=False, trans=None, bucle=None)
            p["anim"] = None
            return False
        scrub(p, st["t"])
        return True
    if st["trans"] is None and pos != st["pos"]:                              # cambió de postura: primero la transición (de pie -> postura, o postura -> de pie)
        nombre = ENTRADA.get(pos) if st["pos"] == 0 else SALIDA.get(st["pos"])
        st.update(destino=pos, trans=nombre, t=SEG[nombre][0] if nombre else 0.0, bucle=None)
        if nombre is None:
            st["pos"] = pos
    if st["trans"] is not None:
        st["t"] += dt
        if st["t"] >= SEG[st["trans"]][1]:
            st.update(pos=st["destino"], trans=None)
            if st["pos"] == 0:
                p["anim"] = None                                              # vuelve a las animaciones normales de pie
                return False
        else:
            scrub(p, st["t"])
            return True
    if st["pos"] == 0:
        return False
    if st["pos"] in BUCLE and vel > 0.15:                                     # agachado o gateando en movimiento: se repite el tramo al ritmo de su velocidad
        nombre, ref = BUCLE[st["pos"]]
        a, b = SEG[nombre]
        if st["bucle"] != nombre:
            st["bucle"], st["t"] = nombre, a
        st["t"] += dt * max(0.3, min(2.5, vel / ref))
        if st["t"] >= b:
            st["t"] = a + (st["t"] - b)
        scrub(p, st["t"])
    else:
        st["bucle"] = None
        scrub(p, FIJA[st["pos"]])
    return True


def persona(j, estatura):
    p = est["pers"][j]
    if abs(p["est"] - estatura) > 0.02:                     # la estatura de cada persona puede cambiar de una partida a otra
        k = estatura * 100.0 / MQ.ALTO_MANIQUI
        p["actor"].set_actor_scale3d(unreal.Vector(k, k, k))
        p["est"] = estatura
    return p


def poner_anim(p, nombre, vel):
    comp = p["actor"].skeletal_mesh_component
    if p["anim"] != nombre:
        a = anims().get(nombre)
        if a:
            comp.play_animation(a, True)
            p["anim"] = nombre
    comp.set_play_rate(max(0.4, min(2.2, vel / 1.4)) if nombre != "idle" else 1.0)


def paneles(lista):
    lista = lista[:N_PANELES]
    for i, (tab, mar) in enumerate(est["pool_paneles"]):
        if i >= len(lista):                                  # los que sobran se guardan bajo el piso
            tab.set_actor_location(D.ue(0, 0, -50), False, False)
            mar.set_actor_location(D.ue(0, 0, -50), False, False)
            continue
        x1, y1, x2, y2, h = lista[i]
        L, psi = math.hypot(x2 - x1, y2 - y1), math.atan2(y2 - y1, x2 - x1)
        cx, cy, rot = (x1 + x2) / 2, (y1 + y2) / 2, unreal.Rotator(0.0, 0.0, D.guinada(psi))
        mar.set_actor_scale3d(unreal.Vector(L, D.GROSOR_PANEL, h))                                                  # marco negro de 4 cm: la tabla blanca va dentro y sobresale 1 cm por cada cara
        mar.set_actor_location_and_rotation(D.ue(cx, cy, h / 2), rot, False, False)
        tab.set_actor_scale3d(unreal.Vector(max(L - 0.08, 0.1), D.GROSOR_PANEL + 0.02, max(h - 0.08, 0.1)))
        tab.set_actor_location_and_rotation(D.ue(cx, cy, h / 2), rot, False, False)
    est["paneles"] = lista


def lerp(a, b, k):
    return a + (b - a) * k


def lerp_ang(a, b, k):                       # radianes, por el camino corto
    return a + ((b - a + math.pi) % (2 * math.pi) - math.pi) * k


def mezclar(k):
    """Cuadro mostrado = cuadro anterior + k * (siguiente - anterior); k de 0 a 1 durante el paso."""
    a, b = est["prev"], est["sig"]
    if a is None:
        return b
    k = max(0.0, min(1.0, k))
    d = [lerp(a["d"][i], b["d"][i], k) for i in range(3)] + [lerp_ang(a["d"][3], b["d"][3], k)]
    por_rol = {(p["r"], j): p for j, p in enumerate(a["pers"])}
    pers = []
    for j, p in enumerate(b["pers"]):
        q = por_rol.get((p["r"], j))
        if q is None:
            pers.append(p)
            continue
        pers.append(dict(p, p=[lerp(q["p"][0], p["p"][0], k), lerp(q["p"][1], p["p"][1], k)], mira=lerp_ang(q["mira"], p["mira"], k)))
    return dict(b, d=d, pan=lerp(a["pan"], b["pan"], k), tilt=lerp(a["tilt"], b["tilt"], k), pers=pers)


T = {"dron": 0.0, "pers": 0.0, "cam": 0.0, "red": 0.0, "n": 0}


def dibujar(c):
    t0 = time.perf_counter()
    x, y, z, psi = c["d"]
    est["dron"].set_actor_location_and_rotation(D.ue(x, y, z), unreal.Rotator(0.0, 0.0, D.guinada(psi)), False, False)
    if est["pan"]:
        est["pan"].root_component.set_relative_rotation(unreal.Rotator(0.0, 0.0, -c["pan"]), False, False)
    if est["tilt"]:
        est["tilt"].root_component.set_relative_rotation(unreal.Rotator(0.0, c["tilt"], 0.0), False, False)
    capturar(c, time.time())
    t1 = time.perf_counter()
    T["dron"] += t1 - t0
    for j, p in est["pers"].items():
        if j >= len(c["pers"]):                              # persona que no está en esta partida: bajo el piso
            p["actor"].set_actor_location(D.ue(0, 0, -50), False, False)
    for j, q in enumerate(c["pers"][:len(ROLES)]):
        p = persona(j, q["est"])
        vel = math.hypot(*q["v"])
        especial = est.get("gal") is not None and postura(p, q, est["dt_dibujo"])
        if not especial:
            poner_anim(p, "idle" if vel < 0.3 else "walk" if vel < 2.4 else "jog", vel)
        p["actor"].set_actor_location_and_rotation(D.ue(q["p"][0], q["p"][1], float(q.get("sz", 0.0)) if especial else 0.0), unreal.Rotator(0.0, 0.0, D.guinada(q["mira"] if vel < 0.3 else math.atan2(q["v"][1], q["v"][0]))), False, False)
    t2 = time.perf_counter()
    camara(x, y, z, psi)
    T["pers"] += t2 - t1
    T["cam"] += time.perf_counter() - t2
    T["n"] += 1


def camara(x, y, z, psi):
    sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    modo = CAMARA
    try:                                                   # _cache/camara.txt (seguir | dron | cenital) cambia la cámara sin reiniciar
        modo = open(os.path.join(AQUI, "_cache", "camara.txt")).read().strip() or CAMARA
    except OSError:
        pass
    if "," in modo:                                        # "x,y,z,rumbo°,cabeceo°": cámara fija en un punto del campus (para las fotos de comparación); rumbo como en la simulación, cabeceo + = hacia abajo
        fx, fy, fz, frum, fcab = [float(v) for v in modo.split(",")]
        sub.set_level_viewport_camera_info(D.ue(fx, fy, fz), unreal.Rotator(0.0, -fcab, D.guinada(math.radians(frum))))
        return
    if modo == "cenital":
        pos, mira = D.ue(0, 0, 52), D.ue(0, 0.01, 0)
    elif modo == "dron":
        pos, mira = D.ue(x + math.cos(psi + 0.7) * 1.9, y + math.sin(psi + 0.7) * 1.9, z + 0.45), D.ue(x, y, z)
    else:
        pos, mira = D.ue(x - math.cos(psi) * 7.0, y - math.sin(psi) * 7.0, z + 2.8), D.ue(x + math.cos(psi) * 4.0, y + math.sin(psi) * 4.0, max(z - 0.8, 0.8))
    est["cam"] = pos if est["cam"] is None else est["cam"] + (pos - est["cam"]) * 0.12
    sub.set_level_viewport_camera_info(est["cam"], unreal.MathLibrary.find_look_at_rotation(est["cam"], mira))


FLAG = os.path.join(AQUI, "_cache", "captura.txt")                  # si existe este archivo se guarda una captura del viewport (Saved/Screenshots) y se borra


def crear_persona():
    j = est["n_listo"]
    est["pers"][j] = {"actor": MQ.figura(f"Vivo_{ROLES[j]}_{j}", ROLES[j], COLORES[ROLES[j]], 1.75, "Vivo"), "anim": None, "est": 1.75}
    est["pers"][j]["actor"].set_actor_location(D.ue(0, 0, -50), False, False)
    est["n_listo"] += 1


def tick(dt):
    ahora = time.time()
    est["dt_dibujo"] = min(dt, 0.1)
    if est["n_listo"] < len(ROLES):                          # una persona cada 45 cuadros, empezando a los 90: nunca dos mallas con esqueleto nuevas en el mismo cuadro
        est["ticks"] += 1
        if est["ticks"] >= 90 and (est["ticks"] - 90) % 45 == 0:
            crear_persona()
        return
    if os.path.exists(FLAG):
        os.remove(FLAG)
        unreal.SystemLibrary.execute_console_command(None, "HighResShot 1280x720")
    nuevo = None
    for _ in range(400):                                    # vaciar el buzón: solo importa lo último
        try:
            m = json.loads(sock.recv(65535))
        except BlockingIOError:
            break
        except ValueError:
            continue
        if m.get("t") == "cab":
            paneles(m["paneles"])
            est["prev"] = est["sig"] = None
        elif m.get("t") == "c":
            nuevo = m
    if nuevo is not None:
        est["prev"] = mezclar(1.0) if est["sig"] is not None else None       # desde lo que se está viendo ahora mismo
        est["prev"] = est["prev"] if est["prev"] is None else dict(est["prev"], pers=est["prev"]["pers"])
        est["dur"] = max(0.03, min(0.3, ahora - est["ult"])) if est["ult"] else 0.1
        est["ult"], est["sig"], est["t_sig"] = ahora, nuevo, ahora
    if est["sig"] is not None:
        dibujar(mezclar((ahora - est["t_sig"]) / est["dur"]))
    est["fps_n"] += 1
    if ahora - est["fps_t"] >= 5.0:
        n = max(1, T["n"])
        unreal.log("DRONIA VIVO fps %.1f · ms por tick: dron %.1f personas %.1f camara %.1f · cuadros dibujados %d" % (est["fps_n"] / (ahora - est["fps_t"]), 1000 * T["dron"] / n, 1000 * T["pers"] / n, 1000 * T["cam"] / n, T["n"]))
        T.update(dron=0.0, pers=0.0, cam=0.0, n=0)
        est["fps_t"], est["fps_n"] = ahora, 0


if __name__ == "__main__":
    preparar()
    est["h"] = unreal.register_slate_post_tick_callback(tick)
