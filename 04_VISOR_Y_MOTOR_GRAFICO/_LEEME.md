# 04 · Visor y motor gráfico

**El visor que funciona hoy no está aquí:** es `03_SIMULACION_RL/index.html` (three.js) y se abre con
`03_SIMULACION_RL/ABRIR_VISOR.bat` en http://127.0.0.1:8765/. Se queda en la 03 porque lee
`salida/estado.json`, `salida/hitos/` y `minimo_tesis/replay/` por ruta relativa desde el mismo servidor.

| Qué | Dónde |
|---|---|
| **Plan del motor gráfico y de la interfaz de 3 modos** (Fase D1-D2) | `PLAN_MOTOR_GRAFICO.md` |
| Boceto de la estación de tierra | `boceto_interfaz.svg` (y `.png`) |
| Cuadros por segundo del visor V16 en el portátil, capturas y el script que mide | `mediciones/` |
| Visor V16 traído de las ramas `v16-visor` y `v16-simulacion` (en `main` desde el commit 3c38f66, aprobado por Brahian el 17-oct) | `v16/` (configuración `visor-v16` de `.claude/launch.json`, puerto 8766) |
| Visor vigente | `03_SIMULACION_RL/index.html` |
| Versiones anteriores (v4 a v19) | `_archivo_versiones/codigo/index_v*.html` |
| Visor de la cámara real (en la Jetson) | `02_JETSON_A_BORDO/visor_web.py` |
| Contrato de datos simulación → visor (`foto()`) | `docs/PLAN_V16_REALISMO.md` (fase A5) y `v16/docs/PROGRESO_V16.md` |

Para ver el V16 con la RTX: Chrome tiene que usar la gráfica NVIDIA (ver `PLAN_MOTOR_GRAFICO.md`, sección 2).

## Revisión de `v16/` para el repositorio público (2026-10-17)

Sin fotos de personas: las personas, el dron, los árboles y los escenarios se dibujan con código. No se carga nada de
internet (todo es local). Archivos que no son código:

| Archivo | Origen | Licencia |
|---|---|---|
| `recursos/three/` (three.js 0.185.1) | npm `three` | MIT (`recursos/three/LICENSE`) |
| `recursos/cielo/spruit_sunrise_1k.hdr`, `quarry_01_1k.hdr` | Poly Haven (Greg Zaal) | CC0 |
| `recursos/texturas/*.jpg` (12: concreto, pasto, tierra) | Generadas con ruido fractal por `herramientas/generar_texturas.py` | Propias (CC0) |
| `replays_prueba/*.json` | Repeticiones de prueba de la V16; llevan el nombre de Brahian como autor | Propias |

Fuente: `v16/simulacion/recursos/LICENCIAS.md`. El script que hizo las texturas está en `v16/simulacion/herramientas/generar_texturas.py`.

## Cancha V17 en el visor (D-057, 2026-10-17)

En `v16/`, escenario **"Vista previa · cancha V17, dos V de 90° (no entrenado)"** (`visor/previa.js`, `crearCancha`):
cancha de fútbol con líneas y arcos (90 × 60 m, **medidas por medir**), zona de IA de 30 × 30 m en el centro de la mitad
este (geocerca roja en la vista externa y en el mapa pequeño), dos V de 90° de paneles de exposición de 1.0 × 2.0 m con
bolsas de arena, vértices a 10 m (V1 abre al sur, V2 al norte) y árboles fuera de la cancha (≥ 10 m de la geocerca).
Escena de ejemplo: el ladrón agachado detrás de V1 se cambia a V2 y el civil cruza a 8 m. Fuente: `docs/PLAN_V17_REFUERZO.md`
§3.3 y D-051. Medido con la RTX: 144 cps y sin errores (`mediciones/medir_fps.mjs cancha`). Capturas:
`mediciones/capturas/v17_cancha_*.jpg`. Las fases de la misión (tránsito → CH7 → zona) y el estado "IA activada" esperan
los campos nuevos de `foto()` de la Simulación V17.

## Blender instalado (D-057, 2026-10-17)

- **Versión:** Blender 5.2.2 LTS (compilación d13f752e3b9c, 2026-09-15), Python 3.13.13 por dentro, importador FBX activo.
- **De dónde:** `download.blender.org/release/Blender5.2/blender-5.2.2-windows-x64.zip` (404 MB), versión portable
  (no pide administrador).
- **SHA256:** `3849d17a682cba006075aaa3f3597ecb5c9c30ec31035b2e092c53e40679b535`, igual al publicado en
  `blender-5.2.2.sha256` de la misma página.
- **Dónde quedó:** en la carpeta `Programas\Blender` del usuario (fuera del repositorio, 925 MB). Se abre con
  `blender.exe`; en consola: `blender.exe --background --version`.
- **Gráfica:** Cycles ve la RTX 3050 por OptiX y por CUDA (para renderizar el video con la tarjeta).

## Paquetes de Quaternius (CC0), bajados el 2026-10-17 con permiso de Brahian

Fuera del repositorio, en la carpeta `Programas\recursos_quaternius` del usuario (≈ 375 MB descomprimidos). Bajados de
la página oficial de cada paquete en `quaternius.itch.io` (versión gratis "Standard", sin cuenta). Cada uno trae su
licencia: **CC0 1.0** (dominio público). Se pueden usar y subir al repositorio, pero se dejan fuera por tamaño.

| Paquete | Qué trae (versión gratis) |
|---|---|
| Universal Base Characters | 2 cuerpos (hombre y mujer) con esqueleto de 65 huesos, 6 peinados, cejas; **sin ropa** (en ropa interior) |
| Universal Animation Library 1 | 43 animaciones: `Idle_Loop`, `Walk_Loop`, `Jog_Fwd_Loop`, `Sprint_Loop`, `Crouch_Idle_Loop`, `Crouch_Fwd_Loop`, `Jump_Start/Loop/Land`, `Roll`, `Interact`… |
| Universal Animation Library 2 | 43 más: `Idle_TalkingPhone_Loop`, `LayToIdle` (de acostado a de pie), `ClimbUp_1m`, `NinjaJump_*`, `Slide_*`, `Idle_FoldArms_Loop`, `Idle_Rail_Loop`… |
| Stylized Nature MegaKit | 68 modelos: árboles, arbustos, flores, piedras, pasto (glTF, FBX, OBJ) |

Todo usa el **mismo esqueleto**: las animaciones se ponen directo en los personajes (comprobado en Blender con
`blender/listar_anim.py`). Prueba de render con la RTX (Cycles + OptiX, 1280 × 720, 64 muestras, ~12 s en total):
`blender/prueba_render.py` → `mediciones/capturas/blender_prueba_quaternius.jpg`.

**Qué falta para las animaciones de la sección 4 de `PLAN_MOTOR_GRAFICO.md`:** gatear, recostarse contra el panel,
rendirse (manos arriba) y grabar con el celular no vienen en la versión gratis (hay parecidas: `LayToIdle`,
`Idle_Rail_Loop`, `Idle_TalkingPhone_Loop`); se arman con código sobre los mismos huesos. **Falta ropa:** sugerencia,
el paquete gratis CC0 "Ultimate Modular Characters" de Quaternius (personas vestidas); no se bajó porque no estaba en
lo autorizado.
