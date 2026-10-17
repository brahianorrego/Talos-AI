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

### Personas vestidas: Ultimate Modular Characters (CC0, bajado el 2026-10-17 con permiso de Brahian)

- **De dónde:** carpeta pública de Google Drive que enlaza la página oficial `quaternius.com/packs/ultimatemodularcharacters.html`;
  licencia CC0 1.0 (`License.txt`). Se bajaron los 11 personajes en glTF (Adventurer, Beach, Casual_2, Casual_Hoodie,
  Farmer, King, Punk, Spacesuit, Suit, Swat, Worker; 35 MB) a `recursos_quaternius\ultimate-modular-characters\`.
- **Traen 24 animaciones propias** (Idle, Walk, Run, Roll, Wave, Interact…), pero **otro esqueleto** (62 huesos, piernas
  con IK) que no coincide con el de la Universal Animation Library (1 hueso en común).
- **Redirección:** `blender/redirigir_animaciones.py` pasa las animaciones de la librería a estos personajes (giro de cada
  hueso en el mundo × la diferencia entre las poses de referencia; IK apagado). Ya están pasadas **41**: 23 de la UAL1 en
  `recursos_quaternius\animaciones_UMC_UAL1.blend` y 18 de la UAL2 en `animaciones_UMC_UAL2.blend` (terminan en `_UMC`).
  Unos 10 s por librería.
- **Prueba:** `blender/prueba_vestidos.py` → `mediciones/capturas/blender_prueba_vestidos.jpg` (correr, agachado junto
  al panel, salto). Revisado a ojo en un cuadro; falta ver las animaciones en movimiento (pies que patinan, manos).

Nota: `descarga.zip` (15.9 MB), que apareció en la raíz del proyecto el 17-oct a las 9:04, era una copia repetida de la
Universal Animation Library [Standard]. La bajó el navegador interno cuando se probó el botón "Download" de itch.io. Se
movió a `recursos_quaternius\_duplicados\` (no se borró) y no entró a Git.

## V2 · Personas vestidas en el visor (2026-10-17)

- `v16/simulacion/visor/personas_gltf.js` (`FiguraGLTF`): misma interfaz que `Humano`, con los modelos y animaciones de
  `v16/simulacion/recursos/personas/` (4.4 MB, CC0; los exporta `blender/exportar_personas_glb.py`). El ladrón es
  `Casual_Hoodie`; los civiles, `Worker`, `Casual_2`, `Suit` y `Farmer` según su ID.
- Animación según la postura de `foto()`: de pie (quieto, caminar, trotar, correr, acelerando con la velocidad),
  agachado (quieto o avanzando), recostado (brazos cruzados), salto (impulso, aire, caída) y civil grabando (celular).
  **Gatear usa por ahora la marcha agachada** (no hay animación de gateo gratis).
- Para ver las figuras de antes (hechas con código): `http://127.0.0.1:8766/?personas=codigo`.
- Medido con la RTX en la cancha V17: 126 cps (con el render de Blender usando la misma tarjeta), sin errores; las cajas
  de YOLO se ajustan a las personas nuevas.

## V6 · Video de la cancha V17 en Blender (2026-10-17)

- `blender/video_cancha_v17.py` arma la escena (cancha, V de 90°, árboles, arbustos y matas de pasto de Quaternius,
  dron, ladrón y civil con la coreografía de la vista previa "cancha") y renderiza con Cycles en la RTX, cuadro por cuadro
  (si se corta, se relanza y sigue). `blender/unir_video.py` une los cuadros en MP4.
- Medido: ~28 s por cuadro a 1920 × 1080 con 32 muestras (el video completo de 80 s serían ~15 h). Se renderiza el
  tramo de 20 a 60 s a 1280 × 720 (~3-4 h), fuera del repositorio, en la carpeta `Videos\dron_ia` del usuario.

## V4 · Interfaz de 3 modos (2026-10-17)

Pestañas arriba a la derecha (o teclas **1**, **2** y **3**; la **I** abre y cierra ingeniería), y el modo elegido se
recuerda. Boceto: `boceto_interfaz.svg`. Capturas: `mediciones/capturas/v4_modo_*.jpg`.

| Modo | Qué muestra |
|---|---|
| **1 Dron** | Cámara del dron con YOLO, cámara al piso, espacio para la cámara USB (solo si la variante la lleva), **mapa de puntos del LiDAR** (impactos del TF03 en naranja y del TF-Luna en azul, acumulados; los viejos se apagan) y **órdenes de la Jetson**: quién manda, vx/vy/vz, giro, gimbal en grados y en PWM de AUX1, altura pedida, modo de ArduPilot y 10 s de historial (`visor/vista_dron.js`) |
| **2 Tierra** | La estación del operador, como antes: cámara grande con el clic de confirmación, vista externa, cámara al piso, mapa y telemetría |
| **3 Ingeniería** | Vista externa grande con el panel de estados, árbitro, personas, recompensa y bitácora |
| **clásico ↗** | Abre el visor de siempre (`03_SIMULACION_RL`, en el puerto 8765 con `ABRIR_VISOR.bat`) |

**Pendiente de la simulación:** las repeticiones no traen la nube de puntos ni las órdenes. La nube se arma acumulando
`lh`/`luna`, y las órdenes se **aproximan con la telemetría**, y así lo dice la pantalla. Cuando `foto()` traiga `cmd`
y `arb` (encargo a Simulación V17), `vista_dron.js` ya usa `cmd` sin más cambios. Medido con la RTX: 73-85 cps en la
partida `sim_v16_semilla3` a 4× (con el render de Blender en la misma tarjeta), sin errores.

## V3 · Árboles y pasto de verdad en el visor (2026-10-17)

- `v16/simulacion/visor/naturaleza.js`: los árboles hechos con código (misión, campo y cancha) se cambian por 4 árboles
  del "Stylized Nature MegaKit" de Quaternius (CC0) en las mismas posiciones, y se siembran 22 000 matas de pasto en
  60 × 60 m alrededor de la zona. Todo con instancias. Recursos: `v16/simulacion/recursos/naturaleza/` (2 MB).
- Para ver los árboles de antes: `?naturaleza=codigo`.
- **Medido con la RTX, sin tope de pantalla** (misión de prueba, 1540 × 788): alta 134 cps, media 184, baja 258; cancha
  V17 con tope: 128 cps. Meta ≥ 60: cumplida. Sin errores. Capturas: `mediciones/capturas/v3_*.jpg`.
- Se probó el arbusto `Bush_Common` y se quitó: su textura es de hojas rojas de otoño.
- Shortcut: los árboles nuevos no tapan a las personas en la prueba de visibilidad de la vista previa (sería muy lenta con
  hojas detalladas); si hiciera falta, usar cilindros simples para esa prueba.

## V5 · Simulación en vivo (2026-10-17)

- **Cómo verla:** doble clic en `ABRIR_EN_VIVO.bat` (abre la simulación, el visor y Chrome en `?r=vivo`). O a mano:
  `03_SIMULACION_RL\.venv\Scripts\python.exe 04_VISOR_Y_MOTOR_GRAFICO\en_vivo.py` y, en el visor, la repetición
  "Simulación en vivo".
- `en_vivo.py` corre una partida del entorno de `03_SIMULACION_RL` (solo lo importa, no lo cambia) a tiempo real y manda
  cada `foto()` al navegador apenas ocurre (Server-Sent Events, solo biblioteca estándar, puerto 8767). Al terminar
  una partida empieza otra con la semilla siguiente. Opciones: `--nivel` (por defecto el de la V17), `--semilla`,
  `--velocidad` y `--politica modelos/dron_politica.json` (si no, acción 0: deciden las reglas). Mientras no haya una
  política V17 entrenada, lo honesto es mostrar las reglas.
- En el visor (`datos.js` → `conectarVivo`, `principal.js`), la partida crece con cada cuadro y la imagen va un cuadro
  detrás del último. Probado: 126 cps con la RTX, sin errores; la pestaña "1 Dron" muestra `cmd` y `arb` reales.
  Captura: `mediciones/capturas/v5_en_vivo_dron.jpg`.

## Regla dura 4 en la pantalla (revisión del Arquitecto, punto 9; 2026-10-17)

Debajo de la caja de YOLO del candidato se lee quién decide: **"Esperando confirmación del operador"** (amarillo), **"¿Es
el sospechoso? clic aquí"** cuando la repetición espera el clic, y **"Confirmado por el operador"** (verde) después; si el
clic lo dio el operador simulado (modo automático o en vivo), dice **"(simulado)"**. La IA nunca aparece como quien
confirma. Captura: `mediciones/capturas/regla4_esperando_operador.jpg`.
