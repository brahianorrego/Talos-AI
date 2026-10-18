# Une los cuadros JPEG o PNG (de Blender o de Unreal) en un MP4 (H.264) con el editor de video de Blender.
# Uso: blender --background --factory-startup --python unir_video.py -- <carpeta_de_cuadros> <salida.mp4> [fps]
import bpy, sys, os
args = sys.argv[sys.argv.index("--") + 1:]
CARPETA, SALIDA = args[0], args[1]
FPS = int(args[2]) if len(args) > 2 else 24
cuadros = sorted(f for f in os.listdir(CARPETA) if f.lower().endswith((".jpg", ".png")) and os.path.getsize(os.path.join(CARPETA, f)) > 0)
esc = bpy.context.scene
esc.render.fps = FPS
ed = esc.sequence_editor_create()
coleccion = ed.strips if hasattr(ed, "strips") else ed.sequences     # Blender 5 la llama strips (empieza vacía)
tira = coleccion.new_image("cuadros", os.path.join(CARPETA, cuadros[0]), channel=1, frame_start=1)
for f in cuadros[1:]:
    tira.elements.append(f)
esc.frame_start, esc.frame_end = 1, len(cuadros)
ancho, alto = tira.elements[0].orig_width or 1920, tira.elements[0].orig_height or 1080
esc.render.resolution_x, esc.render.resolution_y, esc.render.resolution_percentage = ancho, alto, 100
im = esc.render.image_settings
if hasattr(im, "media_type"):                    # Blender 5: el video es un tipo de medio aparte
    im.media_type = "VIDEO"
im.file_format = "FFMPEG"
esc.render.ffmpeg.format = "MPEG4"; esc.render.ffmpeg.codec = "H264"; esc.render.ffmpeg.constant_rate_factor = "HIGH"
esc.render.filepath = SALIDA
bpy.ops.render.render(animation=True)
print("VIDEO", SALIDA, len(cuadros), "cuadros")
