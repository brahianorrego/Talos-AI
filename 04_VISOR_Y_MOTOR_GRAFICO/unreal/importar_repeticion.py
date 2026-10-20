# -*- coding: utf-8 -*-
"""
Convierte una repetición de la simulación (JSON de foto(), dt = 0.1 s) en una Level Sequence de Unreal, en el nivel
/Game/DronIA/Mapas/Cancha_V17 (fase 1 de PLAN_UNREAL.md, D-065): el dron, cada persona, los paneles de esa partida y una
cámara de cine que sigue al dron mirando hacia el ladrón. Unreal solo DIBUJA: no decide ni simula nada.

Uso dentro de Unreal (Herramientas -> Ejecutar script de Python), o sin abrir el editor:
  UnrealEditor-Cmd.exe DronIA_Cancha.uproject -run=pythonscript -script="...\\importar_repeticion.py <repeticion.json> [desde_s] [hasta_s]"
Si no se da la repetición, usa la última partida del entrenamiento V17 más reciente (03_SIMULACION_RL/salida_v17_*).

Las personas son los maniquíes Manny (ladrón) y Quinn (civil) que ya trae Unreal en la plantilla Third Person (maniquies_*.py): de la
estatura de cada persona, animados según su postura y velocidad (de pie, agachado, recostado, gateando, trotando, salto). Si falta el
contenido del maniquí, vuelven los cilindros de antes. Los MetaHumans quedan como mejora opcional (GUIA_BRAHIAN_UNREAL.md).
"""
import array
import glob
import json
import math
import os
import subprocess
import sys

import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import dronia_ue as D  # noqa: E402
import maniquies_unreal as MU  # noqa: E402

SIM = os.path.normpath(os.path.join(AQUI, "..", "..", "03_SIMULACION_RL"))
NIVEL = D.CARPETA + "/Mapas/Cancha_V17"
FPS = 24
ALTO_POSTURA = (1.0, 0.67, 1.0, 0.35)             # de pie, agachado, recostado, gateando (como el visor V16)
COLOR_ROL = {"ladron": (0.6, 0.04, 0.04), "peaton": (0.08, 0.2, 0.55)}


def ultima_repeticion():
    corridas = sorted(glob.glob(os.path.join(SIM, "salida_v17*", "replay_v17.json")), key=os.path.getmtime)
    if not corridas:
        raise RuntimeError("No hay repeticiones V17 en " + SIM)
    return corridas[-1]


def canales(seccion):
    """Los 9 canales de una sección de transformación: posición x, y, z; giro x (alabeo), y (cabeceo), z (guiñada); escala."""
    try:
        return seccion.get_channels_by_type(unreal.MovieSceneScriptingDoubleChannel)
    except AttributeError:
        return seccion.get_all_channels()


def pista_transformacion(secuencia, actor, n):
    b = secuencia.add_possessable(actor)
    pista = b.add_track(unreal.MovieScene3DTransformTrack)
    sec = pista.add_section()
    sec.set_range(0, n)
    return b, canales(sec)


def poner(ch, f, valores):
    """valores: (x, y, z, alabeo, cabeceo, guinada[, sx, sy, sz]) en unidades de Unreal; None = sin clave."""
    t = unreal.FrameNumber(f)
    for c, v in zip(ch, valores):
        if v is not None:
            c.add_key(t, v)


def continuo(previo, nuevo):
    """Guiñada sin saltos de 360° (para que Sequencer no dé la vuelta entera)."""
    if previo is None:
        return nuevo
    return previo + ((nuevo - previo + 180.0) % 360.0 - 180.0)


def dibujar_ruta(paneles, inicio, a_carpeta):
    """La ruta de búsqueda de Brahian (entorno/ruta_busqueda.py) como una línea y puntos de paso a 3.30 m, más el abanico del vaivén."""
    sys.path.insert(0, os.path.join(AQUI, "..", "entorno"))
    import ruta_busqueda as RB
    r = RB.ruta(paneles, inicio)
    cian = D.material("Ruta_cian", (0.1, 0.8, 1.0), 0.3)
    amarillo = D.material("Ruta_amarillo", (0.96, 0.77, 0.26), 0.3)
    blanco = D.material("Ruta_punto", (0.95, 0.95, 0.95), 0.3)

    def tramo(p0, p1, mat, ancho=0.04):
        a, b = D.ue(*p0), D.ue(*p1)
        L = max(math.sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2 + (b.z - a.z) ** 2) / D.M, 1e-3)
        rot = unreal.MathLibrary.find_look_at_rotation(a, b)
        c = D.forma("Cube", "Ruta_tramo", unreal.Vector((a.x + b.x) / 2, (a.y + b.y) / 2, (a.z + b.z) / 2), (L, ancho, ancho), mat, rot=(rot.roll, rot.pitch, rot.yaw))
        a_carpeta(c, "Ruta")

    pl = r["polilinea"]
    for p0, p1 in zip(pl[:-1], pl[1:]):
        tramo(p0, p1, cian)
    for v in r["v"]:
        for p in v["puntos"]:
            a_carpeta(D.forma("Sphere", "Ruta_punto", D.ue(p[0], p[1], p[2]), (0.2, 0.2, 0.2), blanco), "Ruta")
        vv = v["vaiven"]
        for sg in (-1, 1):
            ang = math.radians(vv["psi"] + sg * vv["amplitud"])
            tramo((vv["desde"][0], vv["desde"][1], 3.3), (vv["desde"][0] + math.cos(ang) * vv["largo"], vv["desde"][1] + math.sin(ang) * vv["largo"], 3.3), amarillo, 0.03)
    ex, ey, ez = r["entrada"]
    for k in range(24):                                      # el giro de 360° de entrada: un anillo de 1.5 m de radio
        t0, t1 = 2 * math.pi * k / 24, 2 * math.pi * (k + 1) / 24
        tramo((ex + 1.5 * math.cos(t0), ey + 1.5 * math.sin(t0), ez), (ex + 1.5 * math.cos(t1), ey + 1.5 * math.sin(t1), ez), amarillo, 0.03)
    unreal.log(f"DRONIA: ruta de búsqueda dibujada ({len(pl)} puntos, {len(r['v'])} V)")


def main(ruta=None, desde=0.0, hasta=None):
    ruta = ruta or ultima_repeticion()
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)
    C, dt = datos["cuadros"], datos.get("dt", 0.1)
    k0 = int(desde / dt)
    k1 = min(len(C), int(hasta / dt) + 1) if hasta else len(C)
    C = C[k0:k1]
    nombre = "Rep_" + os.path.splitext(os.path.basename(ruta))[0] + "_" + os.path.basename(os.path.dirname(ruta))
    if desde or hasta:
        nombre += f"_{int(desde)}-{int(hasta) if hasta else 'fin'}s"
    unreal.log(f"DRONIA: importando {ruta} ({len(C)} cuadros, {len(C) * dt:.1f} s)")

    nivel = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not D.biblioteca.does_asset_exist(NIVEL):
        raise RuntimeError("Primero corra crear_cancha.py (no existe " + NIVEL + ")")
    nivel.load_level(NIVEL)

    # lo de una importación anterior se quita; las V fijas del nivel se ocultan (esta partida trae las suyas)
    for a in D.actores.get_all_level_actors():
        carpeta = str(a.get_folder_path())
        if carpeta.startswith("Repeticion"):
            D.actores.destroy_actor(a)
        elif carpeta == "Paneles" or carpeta.startswith("Dron"):
            a.set_actor_hidden_in_game(True)
            a.set_is_temporarily_hidden_in_editor(True)

    def a_carpeta(a, sub):
        a.set_folder_path("Repeticion/" + sub)
        return a

    # paneles de esta partida
    D.paneles_de_foto(datos.get("paneles", []), D.mats_paneles())
    for a in D.actores.get_all_level_actors():
        if str(a.get_folder_path()) == "Paneles" and a.get_actor_label().startswith("panel_"):
            a_carpeta(a, "Paneles")

    if os.environ.get("DRONIA_SIN_RUTA") != "1" and datos.get("paneles"):
        c_ia = next((c for c in C if c.get("fase") in (2, "zona")), C[0])
        dibujar_ruta(datos["paneles"], c_ia["d"][:3], a_carpeta)

    # árboles y helipuerto de la misión completa (entorno/mision_completa.py)
    for i, ar in enumerate(datos.get("arboles", [])):
        malla = unreal.load_asset("/PCGBiomeSample/Meshes/PCG_Tree_02")
        if malla:
            esc = ar["alto"] / 12.5
            t = D.actores.spawn_actor_from_class(unreal.StaticMeshActor, D.ue(ar["p"][0], ar["p"][1], 0), unreal.Rotator(0, 0, 40))
            t.static_mesh_component.set_static_mesh(malla)
            t.set_actor_scale3d(unreal.Vector(esc, esc, esc))
            t.set_actor_label(f"Arbol_mision_{i}")
            a_carpeta(t, "Arboles")
    if datos.get("pad"):
        a_carpeta(D.forma("Cylinder", "Helipuerto", D.ue(datos["pad"][0], datos["pad"][1], 0.03), (2.6, 2.6, 0.06), D.material("Helipuerto", (0.18, 0.2, 0.25), 0.7)), "Paneles")

    # actores: dron y una figura por persona (por id)
    dron = D.dron("Dron_rep")
    for a in D.actores.get_all_level_actors():
        if str(a.get_folder_path()) == "Dron" and a.get_actor_label().startswith("Dron_rep"):
            a_carpeta(a, "Dron")
    # variante plus (H): el pan y el tilt del pan-tilt de 2 servos siguen a la partida (c["gmb"] = tilt en grados, c["pan"] = pan; hoy el pan es 0)
    pantilt = {g: next((a for a in D.actores.get_all_level_actors() if a.get_actor_label() == f"Dron_rep_{g}"), None) for g in ("pan", "tilt")}
    maniquies = MU.disponible() and os.environ.get("DRONIA_CILINDROS") != "1"
    n = int(round((len(C) - 1) * dt * FPS)) + 1
    personas, meta = {}, None
    if maniquies:                                       # NumPy no está en el Python de Unreal: se prepara afuera, con el del proyecto
        py = os.path.join(SIM, ".venv", "Scripts", "python.exe")
        orden = [py, "-I", os.path.join(AQUI, "maniquies_preparar.py"), ruta, str(desde)] + ([str(hasta)] if hasta else [])
        r = subprocess.run(orden, capture_output=True, text=True)
        unreal.log("DRONIA: " + (r.stdout.strip() or r.stderr.strip()[-600:]))
        with open(os.path.join(AQUI, "_cache", "preparado", "meta.json"), encoding="utf-8") as f:
            meta = json.load(f)
        pares = [(clave, rol, est) for clave, (rol, est) in meta["personas"].items()]
    else:
        pares = []
        for c in C:
            for p in c.get("pers", []):
                clave = str(p.get("id", p.get("rol")))
                if all(clave != q[0] for q in pares):
                    pares.append((clave, p.get("rol", "peaton"), p.get("est", 1.72)))
    for clave, rol, est in pares:
        color = COLOR_ROL.get(rol, (0.3, 0.3, 0.3))
        fig = MU.figura(f"{rol}_{clave}", rol, color, est) if maniquies else D.persona(f"{rol}_{clave}", est, color)
        personas[clave] = (a_carpeta(fig, "Personas"), est)
    unreal.log(f"DRONIA: {len(personas)} personas, {'maniquíes' if maniquies else 'cilindros'}")
    cam = D.actores.spawn_actor_from_class(unreal.CineCameraActor, unreal.Vector(0, 0, 500))
    cam.set_actor_label("Camara_cine")
    a_carpeta(cam, "Camara")
    cc = cam.get_cine_camera_component()
    cc.set_editor_property("current_focal_length", 28.0)
    enfoque = cc.get_editor_property("focus_settings")
    enfoque.set_editor_property("focus_method", unreal.CameraFocusMethod.DISABLE)
    cc.set_editor_property("focus_settings", enfoque)

    # secuencia
    carpeta = D.CARPETA + "/Secuencias"
    ruta_sec = carpeta + "/" + nombre
    if D.biblioteca.does_asset_exist(ruta_sec):
        D.biblioteca.delete_asset(ruta_sec)                 # es generada: se rehace siempre desde la repetición
    sec = D.herramientas.create_asset(nombre, carpeta, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
    sec.set_display_rate(unreal.FrameRate(FPS, 1))
    sec.set_playback_start(0)
    sec.set_playback_end(n)

    _, ch_dron = pista_transformacion(sec, dron, n)
    ch_pers = {k: pista_transformacion(sec, fig, n)[1] for k, (fig, _) in personas.items()}
    if maniquies:
        ruta_p = os.path.join(AQUI, "_cache", "preparado")
        for clave, (fig, est) in personas.items():
            plano = array.array("f")
            with open(os.path.join(ruta_p, f"anim_{clave}.f32"), "rb") as f:
                plano.frombytes(f.read())
            with open(os.path.join(ruta_p, f"tray_{clave}.json"), encoding="utf-8") as f:
                t = json.load(f)
            anim = MU.crear_anim(f"{nombre}_{clave}", plano, meta["n_anim"], meta["huesos"], meta["fps_anim"])
            MU.pista_animacion(sec, fig, anim, n)
            ch = ch_pers[clave]
            for f in range(n):
                if t["visible"][f]:
                    poner(ch, f, (t["x"][f] * D.M, -t["y"][f] * D.M, t["h"][f] * D.M, 0.0, 0.0, t["yaw"][f]))
                else:
                    poner(ch, f, (None, None, -5000.0))
        unreal.log("DRONIA: maniquíes animados")
    ch_pt = {g: pista_transformacion(sec, a, n)[1] for g, a in pantilt.items() if a}
    for g, a in pantilt.items():
        if a:
            a_carpeta(a, "Dron")
    b_cam, ch_cam = pista_transformacion(sec, cam, n)

    psi_prev, cam_pos, cam_mira, yaw_cam = None, None, None, None
    for k, c in enumerate(C):
        f = int(round(k * dt * FPS))
        x, y, z, psi = c["d"][:4]
        psi_prev = continuo(psi_prev, D.guinada(psi))
        poner(ch_dron, f, (x * D.M, -y * D.M, z * D.M, c.get("cr", 0.0), c.get("cp", 0.0), psi_prev))
        if ch_pt:                                                       # pitch hacia arriba positivo en la simulación y en Unreal; el yaw de Unreal es horario
            poner(ch_pt["pan"], f, (None, None, None, 0.0, 0.0, -float(c.get("pan", 0.0) or 0.0)))
            poner(ch_pt["tilt"], f, (None, None, None, 0.0, float(c.get("gmb", 0.0) or 0.0), 0.0))
        vistos = set()
        for p in (c.get("pers", []) if not maniquies else []):
            clave = str(p.get("id", p.get("rol")))
            vistos.add(clave)
            est = p.get("est", 1.72)
            alto = p.get("alto") or est * ALTO_POSTURA[int(p.get("pos", 0) or 0)]
            px, py = p["p"]
            poner(ch_pers[clave], f, (px * D.M, -py * D.M, alto / 2 * D.M, 0.0, 0.0, None, 0.45, 0.45, alto))
        for clave, ch in (ch_pers.items() if not maniquies else []):    # quien no está en este cuadro, bajo el piso
            if clave not in vistos:
                poner(ch, f, (None, None, -5000.0))
        # cámara de cine: detrás y un poco arriba del dron, mirando al punto entre el dron y el ladrón
        lad = next((p for p in c.get("pers", []) if p.get("rol") == "ladron" and math.hypot(p["p"][0] - x, p["p"][1] - y) < 25.0), None)   # lejos: mira hacia delante (tránsito)
        lx, ly = lad["p"] if lad else (x + math.cos(psi) * 5, y + math.sin(psi) * 5)
        ux, uy = x - lx, y - ly
        L = max(math.hypot(ux, uy), 1e-3)
        objetivo = unreal.Vector((x + ux / L * 4.5 + uy / L * 2.0) * D.M, -(y + uy / L * 4.5 - ux / L * 2.0) * D.M, (z + 0.6) * D.M)
        mira = unreal.Vector((0.4 * x + 0.6 * lx) * D.M, -(0.4 * y + 0.6 * ly) * D.M, (1.3 if lad else max(1.3, z - 0.5)) * D.M)   # en el tránsito mira al dron, no al suelo
        cam_pos = objetivo if cam_pos is None else cam_pos + (objetivo - cam_pos) * 0.12
        cam_mira = mira if cam_mira is None else cam_mira + (mira - cam_mira) * 0.15
        rot = unreal.MathLibrary.find_look_at_rotation(cam_pos, cam_mira)
        yaw_cam = continuo(yaw_cam, rot.yaw)
        poner(ch_cam, f, (cam_pos.x, cam_pos.y, cam_pos.z, 0.0, rot.pitch, yaw_cam))

    # corte de cámara: toda la secuencia por la cámara de cine
    try:
        corte = sec.add_track(unreal.MovieSceneCameraCutTrack)
    except AttributeError:
        corte = sec.add_master_track(unreal.MovieSceneCameraCutTrack)
    s = corte.add_section()
    s.set_range(0, n)
    try:
        s.set_camera_binding_id(sec.get_portable_binding_id(sec, b_cam))
    except AttributeError:
        s.set_camera_binding_id(unreal.MovieSceneSequenceExtensions.get_binding_id(sec, b_cam))

    D.biblioteca.save_loaded_asset(sec)
    nivel.save_current_level()
    unreal.log(f"DRONIA: secuencia lista {ruta_sec} ({n} cuadros a {FPS} cps)")
    return ruta_sec


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    main(args[0] if args else None, float(args[1]) if len(args) > 1 else 0.0, float(args[2]) if len(args) > 2 else None)
