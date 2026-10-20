# -*- coding: utf-8 -*-
"""
Mide los cuadros por segundo del visor de Unreal (editor, viewport en tiempo real) con la cancha y dos maniquíes, para varias calidades.
  ejecutar_en_unreal.bat medir_fps.py
Resultado: _cache/fps.json (y líneas "DRONIA FPS ..." en el log del editor). Para cada configuración espera 3 s (calentar) y mide 6 s.
"""
import json
import os
import statistics
import time

import unreal

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "_cache", "fps.json")
cmd = lambda c: unreal.SystemLibrary.execute_console_command(None, c)       # noqa: E731

BASE = ["r.VSync 0", "t.MaxFPS 0"]
# (nombre, comandos). El tamaño del viewport lo da la ventana del editor; r.ScreenPercentage lo escala.
CALIDADES = {
    "alto (Lumen + sombras virtuales)": ["r.DynamicGlobalIlluminationMethod 1", "r.ReflectionMethod 1", "r.Shadow.Virtual.Enable 1", "sg.PostProcessQuality 3", "sg.ShadowQuality 3"],
    "medio (Lumen bajo, sombras medias)": ["r.DynamicGlobalIlluminationMethod 1", "r.ReflectionMethod 1", "r.Lumen.ScreenProbeGather.DownsampleFactor 32", "r.Shadow.Virtual.Enable 1",
                                           "sg.PostProcessQuality 2", "sg.ShadowQuality 2"],
    "bajo (sin Lumen, sombras clásicas)": ["r.DynamicGlobalIlluminationMethod 0", "r.ReflectionMethod 2", "r.Shadow.Virtual.Enable 0", "sg.PostProcessQuality 1", "sg.ShadowQuality 1"],
    "apagado (sin GI, sin sombras)": ["r.DynamicGlobalIlluminationMethod 0", "r.ReflectionMethod 2", "r.Shadow.Virtual.Enable 0", "r.ShadowQuality 0", "sg.PostProcessQuality 0"],
}
ESCALAS = [100, 150, 300, 500]                    # % de pantalla: 100 = el viewport tal cual; 150 = 2.25 veces los píxeles
res = {}
cola = [(c, e) for c in CALIDADES for e in ESCALAS]
est = {"i": -1, "t0": 0.0, "dts": [], "fase": "ini"}


def maniquies():
    for rol, p in (("ladron", (-300.0, 800.0)), ("peaton", (400.0, 1200.0))):
        malla = unreal.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple" if rol == "ladron" else "/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple")
        if malla:
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(p[0], p[1], 0))
            a.skeletal_mesh_component.set_skeletal_mesh_asset(malla)
            a.set_actor_label("FPS_" + rol)


def tick(dt):
    ahora = time.time()
    if est["fase"] == "ini":
        try:                                                  # el editor se limita a ~8 cuadros/s si su ventana no está al frente: se apaga
            cfg = unreal.get_default_object(unreal.EditorPerformanceSettings)             # no existe en 5.8 (la ventana ya queda al frente): solo se intenta
            cfg.set_editor_property("throttle_cpu_when_not_foreground", False)
        except Exception as e:                                # noqa: BLE001
            unreal.log("DRONIA FPS: no pude apagar el límite de fondo: " + repr(e))
        for c in BASE:
            cmd(c)
        unreal.EditorLoadingAndSavingUtils.load_map("/Game/DronIA/Mapas/Cancha_V17")
        maniquies()
        est["fase"], est["i"], est["t0"] = "esperar", -1, ahora
        return
    if est["fase"] == "esperar" and ahora - est["t0"] < 8:
        return
    if est["fase"] in ("esperar", "medido"):
        est["i"] += 1
        if est["i"] >= len(cola):
            json.dump(res, open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            unreal.log("DRONIA FPS: terminado")
            unreal.unregister_slate_post_tick_callback(est["h"])
            cmd("QUIT_EDITOR")
            return
        nombre, esc = cola[est["i"]]
        for c in CALIDADES[nombre] + ["r.ScreenPercentage %d" % esc]:
            cmd(c)
        est["fase"], est["t0"], est["dts"] = "calentar", ahora, []
        return
    if est["fase"] == "calentar" and ahora - est["t0"] > 4:
        est["fase"], est["t0"] = "medir", ahora
        return
    if est["fase"] == "medir":
        est["dts"].append(dt)
        if ahora - est["t0"] > 6:
            d = sorted(est["dts"])
            nombre, esc = cola[est["i"]]
            r = {"fps_medio": round(len(d) / sum(d), 1), "fps_p1_bajo": round(1 / d[int(len(d) * 0.99)], 1), "cuadros": len(d)}
            res["%s | %d%%" % (nombre, esc)] = r
            unreal.log("DRONIA FPS %s %d%%: %s" % (nombre, esc, r))
            est["fase"] = "medido"


est["h"] = unreal.register_slate_post_tick_callback(tick)
