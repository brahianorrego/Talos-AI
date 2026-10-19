# Une los cuadros JPEG o PNG (de Blender o de Unreal) en un MP4 (H.264) con el editor de video de Blender.
# Uso: blender --background --factory-startup --python unir_video.py -- <carpeta_de_cuadros> <salida.mp4> [fps] [letreros.json]
# letreros.json (opcional): lista de {"f0", "f1", "titulo", "sub", "color": [r, g, b]} con cuadros desde 0; se escriben sobre el video (fases de la misión).
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
if len(args) > 3:
    import json
    with open(args[3], encoding="utf-8") as f:
        letreros = json.load(f)
    for i, l in enumerate(letreros):
        for nombre, texto, tam, y, canal in (("t", l["titulo"], 54, 0.955, 2), ("s", l.get("sub", ""), 30, 0.862, 3)):
            if not texto:
                continue
            t = coleccion.new_effect(f"letrero{nombre}{i}", "TEXT", channel=canal, frame_start=l["f0"] + 1, length=l["f1"] - l["f0"] + 1)
            t.text, t.font_size, t.location, t.anchor_x, t.anchor_y = texto, tam, (0.5, y), "CENTER", "TOP"
            t.color = tuple(l.get("color", [1, 1, 1])) + (1.0,) if nombre == "t" else (0.88, 0.92, 0.96, 1.0)
            t.use_box, t.box_color, t.box_margin = True, (0.03, 0.05, 0.08, 0.72), 0.012

ancho, alto = tira.elements[0].orig_width or 1920, tira.elements[0].orig_height or 1080
esc.render.resolution_x, esc.render.resolution_y, esc.render.resolution_percentage = ancho, alto, 100
im = esc.render.image_settings
if hasattr(im, "media_type"):                    # Blender 5: el video es un tipo de medio aparte
    im.media_type = "VIDEO"
im.file_format = "FFMPEG"
esc.render.ffmpeg.format = "MPEG4"; esc.render.ffmpeg.codec = "H264"; esc.render.ffmpeg.constant_rate_factor = "HIGH"
esc.render.filepath = SALIDA
if os.environ.get("DRONIA_FOTO"):                 # prueba: un solo cuadro (n, desde 1) a PNG en SALIDA
    esc.frame_set(int(os.environ["DRONIA_FOTO"]))
    if hasattr(im, "media_type"):
        im.media_type = "IMAGE"
    im.file_format = "PNG"
    bpy.ops.render.render(write_still=True); print("FOTO", SALIDA); sys.exit(0)
bpy.ops.render.render(animation=True)
print("VIDEO", SALIDA, len(cuadros), "cuadros")
