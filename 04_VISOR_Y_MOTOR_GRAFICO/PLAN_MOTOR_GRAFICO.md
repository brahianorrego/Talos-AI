# Plan del motor gráfico y de la estación de tierra (Fase D1-D2)

Sesión "Visor y motor gráfico", 2026-10-17. **Solo plan y medición: no se construyó nada nuevo.** Lo que se aprueba
de aquí lo decide Brahian con el Arquitecto.

## 1. Resumen en tres líneas

1. El visor V16 (three.js, hecho en la nube) **sí corre en el portátil**, y sobrado: **144 cuadros por segundo**
   (el tope de la pantalla) en calidad alta con la RTX 3050. Sin ese tope llega a ~200 (`mediciones/MEDICION_FPS_V16.md`).
2. Hay una trampa: **Chrome usa la gráfica Intel por defecto** y ahí baja a 24 cuadros por segundo en alta. Se arregla
   con un ajuste de Windows (sección 2).
3. **Recomendación:** seguir con **three.js** para la estación de tierra y subirle la calidad con personas y
   animaciones de verdad (no hechas con código). Para el video "tipo GTA V" de la sustentación, **Blender** renderiza
   las mismas repeticiones con calidad de cine. Unreal 5 no se recomienda ahora (sección 3).

## 2. El portátil, medido

| Qué | Valor | De dónde sale |
|---|---|---|
| Procesador | Intel Core i5-12450HX (12 hilos) | `dxdiag` |
| RAM | 16 GB (15.7 GB para Windows) | `dxdiag` |
| Gráfica dedicada | NVIDIA GeForce RTX 3050 6GB Laptop, 6 GB, controlador 616.56, hasta 45 W | `nvidia-smi` |
| Gráfica integrada | Intel UHD (la pantalla está conectada a esta) | `dxdiag` |
| Pantalla | 1920 × 1080 a 144 Hz | `dxdiag` |
| Disco libre en C: | 289 GB | `df` |
| Motores instalados | Ninguno (ni Epic/Unreal, ni Unity, ni Godot) | `Program Files` |

**Visor V16 en Chrome, 1540 × 788 px con escala 1.25 (casi 1080p), partida de prueba corriendo, 10 s por calidad**
(`mediciones/fps_*.json`, script `mediciones/medir_fps.mjs`):

| Gráfica | Alta | Media | Baja |
|---|---|---|---|
| Intel UHD (por defecto) | 24 cps, saltos de hasta 194 ms | 26 | 38 |
| RTX 3050 | **144** (tope de la pantalla) | 144 | 144 |
| RTX 3050 sin tope | 202 (4.5 ms por cuadro) | 203 | 228 |

- Con la RTX, alta y baja dan casi lo mismo: el límite ya no es la gráfica sino el JavaScript. **Queda margen de
  sobra para personas con más detalle, pasto en 3D y efectos** (oclusión ambiental, brillo, desenfoque).
- **Ajuste que debe hacer Brahian una vez:** Configuración de Windows → Sistema → Pantalla → Gráficos → Google Chrome →
  "Alto rendimiento (NVIDIA)". Otra opción sin tocar Windows: abrir Chrome con `--force_high_performance_gpu` (solo
  funciona si Chrome estaba cerrado). Se comprueba en el panel de Ingeniería → Cuadros por segundo.
- El panel del navegador de la app de Claude usa la Intel y, con la ventana oculta, baja a ~1 cuadro por segundo: no
  sirve para medir.

Capturas (RTX, calidad alta) en `mediciones/capturas/`: `v16_camara_yolo.jpg` (cámara del dron con la caja de YOLO
y la pregunta al operador), `v16_externa_salto.jpg` (el ladrón junto al panel, el dron esquivando),
`v16_externa_paneles.jpg`, `v16_previa_hangar.jpg`, `v16_previa_campo.jpg`, y `v16_rtx_*` / `v16_intel_alta.jpg`
con el panel de Ingeniería abierto mostrando los cuadros por segundo.

**Qué se ve hoy (opinión, mirando las capturas):** buen nivel de "simulador técnico": sombras, pasto con textura, cielo
real, cámaras con el ángulo y el ruido del sensor, cajas de YOLO como en la Jetson. Lo que delata que es un juego
sencillo: **las personas** (maniquíes hechos con código, sin cara, ropa ni pliegues), **los árboles** (bolas verdes)
y el pasto plano. Todo eso es de **recursos** (modelos y texturas), no del motor: la V16 se hizo en la nube sin
acceso a sitios de modelos (`v16/simulacion/recursos/LICENCIAS.md`).

## 3. Comparación de motores

| | (a) three.js realista (V16) | (b) Unreal Engine 5 ligero | (c) Godot 4 / Unity |
|---|---|---|---|
| Calidad visual | Buena; con personas y árboles de verdad, "videojuego actual de gama media" | La mejor: luz global (Lumen), MetaHumans casi reales. Es el "tipo GTA V" | Godot: media-alta. Unity (HDRP): alta, pero pesado |
| ¿Corre en este portátil? | **Sí, medido: 144 cps** | El editor pide más de lo que hay: Epic recomienda 32 GB de RAM y 8 GB de memoria de video (este tiene 16 y 6; dato de su página de requisitos, por confirmar al instalar). MetaHumans y Lumen en una 3050 de 45 W: probablemente 20-40 cps con calidad recortada (**sin medir**) | Godot sí (liviano, ~150 MB). Unity URP sí; HDRP justo |
| Tamaño de la instalación | 0 (es una página web; ~10 MB de recursos) | ~60-100 GB entre el motor, el lanzador y los MetaHumans (aprox., sin medir) | Godot ~150 MB; Unity ~10-15 GB |
| Trabajo para llegar | Bajo: ya existe y funciona; falta cambiar recursos y la interfaz | Muy alto: proyecto nuevo en Blueprints/C++, importar repeticiones, rehacer cámaras, YOLO e interfaz. Semanas, con un lenguaje que nadie del equipo usa | Alto: proyecto nuevo en GDScript o C#, rehacer todo lo de la V16 |
| Conexión con la simulación | Ya lee el JSON de `foto()`; en vivo, por WebSocket desde Python (pocas líneas) | Leer el JSON con el complemento de JSON, o recibir por UDP/TCP. Hay que escribirlo | Godot: JSON y WebSocket incluidos. Unity: C# con `JsonUtility` |
| Interfaz de la estación (botones, paneles, mapa) | Lo más fácil: HTML. **Ya está hecha** | Incómoda (UMG) | Media |
| ¿Lo abre el jurado o Tania en otro PC? | Sí, con un navegador | No: hay que empaquetar un .exe de varios GB y una gráfica buena | Exportable a .exe o a web (Godot) |
| Riesgo | Bajo | Alto: el portátil no llega cómodo y la curva de aprendizaje es larga | Medio |

**(d) Complemento recomendado: Blender para el video.** Blender (gratis, ~1 GB, se programa en **Python**, igual que
la simulación) puede leer una repetición `foto()` y animar personas de Mixamo, un dron y los paneles, y renderizar con
calidad de cine (Cycles). No necesita ir en tiempo real: si un cuadro tarda 10 s en la 3050, un minuto de video sale
en una noche. Así se consigue la toma "tipo GTA V" para la sustentación y el README **sin cambiar de motor** la
estación. Trabajo: un script de importación + una escena; se planea aparte si Brahian lo aprueba.

### Recomendación

**(a) three.js para la estación de tierra, con mejores recursos, + (d) Blender para los videos.** Razones:

1. Ya corre, medido, a 144 cps; las otras opciones empiezan de cero.
2. La estación de tierra **es una interfaz** (cámaras, botones, mapa, confirmar al sospechoso), y eso se hace mejor
   en HTML. Además, la misma página puede mostrar la cámara real de la Jetson (`visor_web.py` ya sirve por web).
3. El salto visual que falta es de **recursos** (personas, árboles, pasto), no de motor. Eso se arregla en three.js.
4. Unreal 5 no cabe cómodo en 16 GB de RAM y 6 GB de video, y Brahian no es programador: sería meses en otra
   herramienta. Si después de la sustentación sobra tiempo, el contrato `foto()` permite hacer un reproductor en
   Unreal sin tocar la simulación.

## 4. Animaciones que hacen falta

Hoy la V16 las hace **con código** sobre un esqueleto de 22 huesos (`v16/simulacion/visor/humano.js`). Plan: usar
personas con esqueleto estándar (por ejemplo de Mixamo, gratis con cuenta de Adobe, o los paquetes CC0 de Quaternius;
licencias **por verificar** antes de subir nada al repositorio público: los archivos crudos de Mixamo no se pueden
redistribuir sueltos) y dejar el código solo para lo que ningún paquete trae (brazo hacia el dron, pies anclados).

| Animación | Campo de `foto()` que la dispara | Hoy (V16) | Fuente propuesta |
|---|---|---|---|
| Quieto, caminar, trotar, correr | velocidad de `pers[k].v` | Con código | Paquete (Mixamo / Quaternius) |
| Pararse ↔ agacharse, caminar agachado | `pos` 0↔1, `pos0`, `pt` | Con código | Paquete + mezcla con `pt` |
| Gatear | `pos` = 3 | Con código | Paquete |
| Recostarse contra el panel y asomarse | `pos` = 2, `mira` | Con código | Paquete ("espalda a la pared") + ajuste a la distancia del muro |
| Saltar para agarrar el dron | `salto.f` 1-3, `salto.mano` | Con código (la mejor que tiene) | Paquete para el cuerpo + IK del brazo hacia `salto.mano` (código propio) |
| Civil: transita, mira el dron, esquiva, se va | `civ` 0-4 | Con código | Paquete ("mirar arriba", "esquivar") |
| Civil graba con el celular | `civ` = 5, `graba` | Con código | Paquete ("sostener el teléfono") + modelo del celular |
| Rendirse | `rinde` | Con código | Paquete ("manos arriba") |

## 5. Interfaz de la estación de tierra: 3 modos

Boceto: **`boceto_interfaz.svg`** (los números que aparecen en el boceto son de ejemplo, no medidos). Se cambia de
modo con las teclas 1, 2 y 3 o con las pestañas de arriba. Un botón "clásico" abre el visor de hoy
(`03_SIMULACION_RL/index.html`) tal cual, como pide la Fase D2.

| Modo | Para quién | Qué muestra |
|---|---|---|
| **1 · Vista del dron** | Explicar qué ve y qué decide la máquina | Hasta **3 cámaras**: CAM0 CSI frontal (en el gimbal), CAM1 CSI al piso (punto ciego) y la USB; cada una con sus cajas de YOLO (ID, confianza, distancia) y sus cuadros por segundo, como `visor_web.py`. **Mapa de puntos del LiDAR** visto desde arriba (TF03 y TF-Luna). **Órdenes que manda la Jetson**: quién manda (piloto, IA, árbitro, bloqueo LiDAR, CH8), velocidades, yaw, gimbal en grados y en PWM, modo de ArduPilot, con un historial de 10 s |
| **2 · Estación de tierra** | El operador en vuelo | Cámara grande donde **un clic sobre la caja confirma al sospechoso** (y Enter/Esc para sí/no); vista externa o cámara al piso, intercambiables; mapa con geocerca y paneles; altura, batería, modo, objetivo, tiempo a la vista; botón grande "Soltar objetivo"; pocos avisos y grandes |
| **3 · Ingeniería** | El jurado y la depuración | Máquina de estados de la búsqueda, árbitro con el motivo de cada decisión, personas con la "verdad" del simulador, recompensa por componente, curvas del entrenamiento (custodia, entropía, nivel), vista 3D libre con capas (rayos, conos, partículas) y rendimiento |

**Qué datos faltan en `foto()`** (cambio en `03_SIMULACION_RL/`: se le pide al Arquitecto, no lo toca esta sesión):

| Falta | Para qué | Propuesta |
|---|---|---|
| Las órdenes que se mandan a la Pixhawk | Modo 1 | Campo `cmd`: `[vx, vy, vz, yaw_rate, gimbal_grados, modo, quien_manda]` |
| El motivo del árbitro | Modos 1 y 3 | Campo `arb`: texto corto ("persona a 2.4 m", "LiDAR 2.1 m", "CH8") |
| La tercera cámara (USB) | Modo 1 | Depende de la variante que elija la sesión de Hardware; mientras, el marco se oculta |
| Detecciones de la cámara principal ya están (`det`), las del piso también (`cam_piso`) | — | Nada |

## 6. Fases para construir (cuando se apruebe; no empezadas)

| Fase | Qué | Tamaño aproximado |
|---|---|---|
| V1 | Traer la V16 a la carpeta de trabajo y dejarla abrir con un `.bat` que pida la RTX | Pequeña |
| V2 | Personas con esqueleto estándar y animaciones de paquete, mezcladas con los campos de `foto()` | Mediana (la más visible) |
| V3 | Árboles y pasto de verdad (instanciados), oclusión ambiental y brillo; medir que siga ≥ 60 cps con la RTX | Mediana |
| V4 | Interfaz de 3 modos (sección 5) + botón "clásico" | Mediana |
| V5 | Modo en vivo: la simulación manda `foto()` por WebSocket al visor | Pequeña |
| V6 | Blender: importar una repetición y renderizar el video de la sustentación | Mediana |

## 7. Lo que no se verificó

- No se instaló Unreal, Unity, Godot ni Blender: sus cifras de rendimiento y tamaño son aproximadas.
- Las licencias de Mixamo y Quaternius para un repositorio público están por revisar.
- La V16 está en `04_VISOR_Y_MOTOR_GRAFICO/v16/` **sin subir a Git**: Brahian decide si entra a `main`.
- Medido solo con la partida de prueba "Misión de prueba · 2 paneles" (escrita a mano, no es la IA) y en una ventana
  de casi 1080p, no en pantalla completa.
