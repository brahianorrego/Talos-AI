# -*- coding: utf-8 -*-
"""
Renderiza una Level Sequence de DronIA (la que crea importar_repeticion.py) a imágenes PNG con Movie Render Queue
(fase 1 de PLAN_UNREAL.md). Hay que correrlo con el EDITOR abierto (Movie Render Queue necesita ventana y tarjeta gráfica); lo más fácil:
  ejecutar_en_unreal.bat renderizar.py <secuencia> <carpeta_salida> [cuadro_inicial cuadro_final]
(no usar -ExecutePythonScript: cierra el editor al terminar el script y corta el render; ver init_unreal.py)
Si no se da carpeta, guarda en Videos/dron_ia/unreal del usuario. Sin cuadros: toda la secuencia. Con cuadros (ej. 100 100): solo ese tramo, para probar. Luego se une a MP4 con ffmpeg o con
04_VISOR_Y_MOTOR_GRAFICO/blender/unir_video.py (acepta JPG y PNG).
"""
import os
import sys

import unreal

args = [a for a in sys.argv[1:] if not a.startswith("-")]
secuencia = args[0] if args else "/Game/DronIA/Secuencias/Rep_replay_v17_salida_v17_1"
salida = args[1] if len(args) > 1 else os.path.join(os.path.expanduser("~"), "Videos", "dron_ia", "unreal").replace("\\", "/")
tramo = (int(args[2]), int(args[3])) if len(args) > 3 else None

sub = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
cola = sub.get_queue()
for t in list(cola.get_jobs()):
    cola.delete_job(t)
trabajo = cola.allocate_new_job(unreal.MoviePipelineExecutorJob)
trabajo.map = unreal.SoftObjectPath("/Game/DronIA/Mapas/Cancha_V17")
trabajo.sequence = unreal.SoftObjectPath(secuencia)
trabajo.job_name = "DronIA"
cfg = trabajo.get_configuration()

salida_cfg = cfg.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
salida_cfg.output_resolution = unreal.IntPoint(1920, 1080)
salida_cfg.output_directory = unreal.DirectoryPath(salida)
salida_cfg.file_name_format = "cuadro_{frame_number}"
if tramo:
    salida_cfg.use_custom_playback_range = True
    salida_cfg.custom_start_frame, salida_cfg.custom_end_frame = tramo

cfg.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
cfg.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
aa = cfg.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
aa.spatial_sample_count, aa.temporal_sample_count = 1, 4
aa.override_anti_aliasing = True
aa.anti_aliasing_method = unreal.AntiAliasingMethod.AAM_TSR

# La variable tiene que seguir viva mientras renderiza: si Python la borra al terminar el script, el render se corta
# a los pocos segundos ("PIE Ended while Movie Pipeline was still active").
EJECUTOR = unreal.MoviePipelinePIEExecutor()


def al_terminar(ejecutor, exito):
    unreal.log("DRONIA: render terminado (exito=%s) en %s" % (exito, salida))
    unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")


EJECUTOR.on_executor_finished_delegate.add_callable(al_terminar)
sub.render_queue_with_executor_instance(EJECUTOR)
unreal.log("DRONIA: render empezado -> " + salida)
