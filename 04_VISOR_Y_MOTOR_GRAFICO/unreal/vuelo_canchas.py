# -*- coding: utf-8 -*-
"""
Crea la Level Sequence /Game/DronIA/Secuencias/Vuelo_entre_canchas: la cámara de cine parte de la cancha de fútbol (sobre la zona de IA),
sube, cruza y baja hasta las canchas cerradas, y vuelve. Es la misma curva que usa la tecla T de la estación web (estacion/universidad.js):
una curva de Bézier con altura de vuelo y mirada que gira con suavidad; las dos vistas y la altura salen de entorno/entorno_u.json.
Se renderiza igual que una repetición: ejecutar_en_unreal.bat renderizar.py /Game/DronIA/Secuencias/Vuelo_entre_canchas <carpeta>
"""
import os
import sys

import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import dronia_ue as D  # noqa: E402
import entorno_u_ue as EU  # noqa: E402
from importar_repeticion import continuo, pista_transformacion, poner  # noqa: E402

NIVEL = D.CARPETA + "/Mapas/Cancha_V17"
FPS = 24


def suave(t):
    return t * t * (3 - 2 * t)


def tramo(a, b, alto, u):
    """Posición y punto de mira (en metros de la simulación) a mitad de camino u entre dos vistas."""
    w, e = 1 - suave(u), suave(u)
    c1, c2 = (a["pos"][0], a["pos"][1], max(a["pos"][2], alto)), (b["pos"][0], b["pos"][1], max(b["pos"][2], alto))
    pos = [w ** 3 * a["pos"][i] + 3 * w * w * e * c1[i] + 3 * w * e * e * c2[i] + e ** 3 * b["pos"][i] for i in range(3)]
    v = suave(min(1.0, u * 1.15))
    mira = [a["mira"][i] * (1 - v) + b["mira"][i] * v for i in range(3)]
    return pos, mira


def main():
    E = EU.cargar()
    P = E["poses"]
    nivel = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not D.biblioteca.does_asset_exist(NIVEL):
        raise RuntimeError("Primero corra crear_cancha.py")
    nivel.load_level(NIVEL)
    for a in D.actores.get_all_level_actors():
        if str(a.get_folder_path()) == "Vuelo":
            D.actores.destroy_actor(a)
    cam = D.actores.spawn_actor_from_class(unreal.CineCameraActor, unreal.Vector(0, 0, 500))
    cam.set_actor_label("Camara_vuelo")
    cam.set_folder_path("Vuelo")
    cc = cam.get_cine_camera_component()
    cc.set_editor_property("current_focal_length", 22.0)
    f = cc.get_editor_property("focus_settings")
    f.set_editor_property("focus_method", unreal.CameraFocusMethod.DISABLE)
    cc.set_editor_property("focus_settings", f)

    seg = P["segundos"]
    n_t = int(seg * FPS)
    espera_a, espera_b = int(1.0 * FPS), int(2.0 * FPS)
    total = espera_a + n_t + espera_b + n_t + int(1.0 * FPS)
    ruta = D.CARPETA + "/Secuencias/Vuelo_entre_canchas"
    if D.biblioteca.does_asset_exist(ruta):
        D.biblioteca.delete_asset(ruta)
    sec = D.herramientas.create_asset("Vuelo_entre_canchas", D.CARPETA + "/Secuencias", unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
    sec.set_display_rate(unreal.FrameRate(FPS, 1))
    sec.set_playback_start(0)
    sec.set_playback_end(total)
    b, ch = pista_transformacion(sec, cam, total)
    A, B = P["campo"], P["cancha_cerrada"]
    yaw = None
    for f in range(total + 1):
        if f < espera_a:
            pos, mira = A["pos"], A["mira"]
        elif f < espera_a + n_t:
            pos, mira = tramo(A, B, P["altura_de_vuelo"], (f - espera_a) / n_t)
        elif f < espera_a + n_t + espera_b:
            pos, mira = B["pos"], B["mira"]
        elif f < espera_a + n_t + espera_b + n_t:
            pos, mira = tramo(B, A, P["altura_de_vuelo"], (f - espera_a - n_t - espera_b) / n_t)
        else:
            pos, mira = A["pos"], A["mira"]
        p, m = D.ue(*pos), D.ue(*mira)
        rot = unreal.MathLibrary.find_look_at_rotation(p, m)
        yaw = continuo(yaw, rot.yaw)
        poner(ch, f, (p.x, p.y, p.z, 0.0, rot.pitch, yaw))
    corte = sec.add_track(unreal.MovieSceneCameraCutTrack)
    s = corte.add_section()
    s.set_range(0, total)
    try:
        s.set_camera_binding_id(sec.get_portable_binding_id(sec, b))
    except AttributeError:
        s.set_camera_binding_id(unreal.MovieSceneSequenceExtensions.get_binding_id(sec, b))
    D.biblioteca.save_loaded_asset(sec)
    nivel.save_current_level()
    unreal.log(f"DRONIA: secuencia lista {ruta} ({total} cuadros a {FPS} cps, {total / FPS:.0f} s)")


if __name__ == "__main__":
    main()
