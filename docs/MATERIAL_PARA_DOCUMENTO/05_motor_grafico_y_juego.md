# 05 · Motor gráfico y juego

Fuente: `04_VISOR_Y_MOTOR_GRAFICO/_LEEME.md`, `PLAN_MOTOR_GRAFICO.md`, `PLAN_UNREAL.md`, `mediciones/` y `docs/ORDENES_BRAHIAN_20OCT.md`. Todo es simulación.

## 1. Qué hay y para qué sirve cada cosa

- **Simulación (Python/NumPy):** decide y entrena. Es la única que manda; el resto solo dibuja lo que dice `foto()` (`04_VISOR_Y_MOTOR_GRAFICO/PLAN_UNREAL.md`).
- **Estación de tierra (web, three.js):** la interfaz que irá con la Jetson. Cinco modos (cámara del dron con las cajas de YOLO y las órdenes de la Jetson, mundo 3D, mapa, ingeniería y vuelo real), teclas 1 a 5 y botones arriba.
  El operador confirma al sospechoso con un botón (regla: humano en el lazo). Capturas: `08_EVIDENCIA_Y_DIAGRAMAS/capturas/estacion_modo_dron.jpg` y `estacion_modo_3d.jpg`.
- **Mundo realista en Unreal Engine 5 (D-065):** campus de la universidad (con medidas de Google Earth), canchas, paneles, árboles de Blender y maniquíes con las posturas del ladrón; se alimenta de las repeticiones de la simulación.
- **Blender:** videos a partir de las repeticiones (`04_VISOR_Y_MOTOR_GRAFICO/blender/`); el primero con personajes de paquete fue rechazado por Brahian ("parece hecho a punta de figuras geométricas"), fuente `docs/DECISIONES.md` D-065.

## 2. El juego (orden de Brahian, 20-oct noche, `docs/ORDENES_BRAHIAN_20OCT.md` §G)

Meta: poder **jugar** la simulación, como será en la realidad, **de día** (las fotos nocturnas solo dan la distribución).

1. **Manejo manual:** altura (arriba y abajo), adelante, atrás, lado y giro. La altura manual es solo del humano; la IA no controla la altura (§D). Siguen los límites duros: geocerca, piso y techo, paneles.
2. **Tecla 360 (mantenida):** el dron gira 360° buscando. Si aparece una persona, el juego la marca "posible objetivo"; Brahian da **clic** para confirmar "ese es el objetivo". Al confirmar termina el 360 y Brahian toma el control (humano en el lazo, regla 4).
3. **Ruta de búsqueda** (§C, consejos y no reglas): al activar, 360°; ir al panel más cercano y detrás; seguir al ladrón; de esquina en esquina; mirar de frente con vaivén; pasar al otro panel; nunca quedarse quieto. Brahian juega para ver y comparar con la IA. Diagrama: `docs/RUTA_BUSQUEDA_BRAHIAN.md`.
4. **Modo Enseñar** (tecla E en la estación; commit `81d71b2`): mapa con puntos de paso y rumbo, manejo manual con teclado o gamepad y grabación de la demostración.

## 3. Cuadros por segundo medidos

Fuente: `04_VISOR_Y_MOTOR_GRAFICO/mediciones/MEDICION_FPS_V16.md` (visor three.js, `medir_fps.mjs`, Chrome 1540 × 788):

| Tarjeta | Alta | Media | Baja |
|---|---:|---:|---:|
| Intel UHD (la que Chrome usa por defecto) | 24 | 26 | 38 |
| RTX 3050 6 GB, con tope de pantalla | 144 | 144 | 144 |
| RTX 3050 sin tope | 202 | 203 | 228 |

Hay que poner Chrome en "Alto rendimiento" (configuración de gráficos de Windows). Portátil: i5-12450HX, 16 GB de RAM, RTX 3050 de 6 GB.
**Unreal en vivo en esta RTX (medido 20-21 oct, ver sección 5):** 60 cuadros por segundo (tope de la pantalla) en 1280×720 y en 1920×1080; con la partida en vivo, entre 52 y 60. Como pasa de 15, **va en vivo** (no hace falta dejarlo como video).

## 4. Qué se pidió corregir (para contar el proceso)

Quitar el vuelo entre canchas (tecla T), un solo escenario seleccionable (cancha de fútbol o de tenis), árboles y edificios más realistas, mapa a pantalla completa, ingeniería fuera del primer plano, vista de vuelo real con cámara principal grande, mapa de los dos LiDAR de 1 haz y cámara 2 abajo, y quitar el botón "Dron: Mínimo/Plus" (`docs/ORDENES_BRAHIAN_20OCT.md` §F). Varias ya están hechas (commits `47f70ba`, `d44b52b`, `bb61d0c`, `81d71b2`).

## 5. Estado final del motor gráfico y el juego (20-21 oct)

**Cuadros por segundo de Unreal** (RTX 3050 6 GB, editor en tiempo real, cancha completa + 2 maniquíes + 4 paneles; `04_VISOR_Y_MOTOR_GRAFICO/unreal/medir_fps.py`, resultados en `unreal/_cache/fps_1280x720.json` y `fps_1920x1080.json`):
- Alta (Lumen y sombras virtuales), media, baja y apagado: **60.0 fps** medio en 720p y en 1080p, con el 1 % de cuadros más lentos entre 55 y 58 fps (tiempo por cuadro 16.7 ms; el 99 % tarda menos de 18.2 ms).
- Es un **tope** (la frecuencia de la pantalla), no el rendimiento máximo: la tarjeta iba al 49-61 % de uso, lo que sugiere margen hasta unos 100 fps. Los cambios de calidad no movieron la carga, así que no se distingue 720p de 1080p ni Lumen sí o no.
- **Con la simulación en vivo** (`vivo_unreal.py`): 52 a 60 fps; dibujar cada cuadro cuesta entre 1.5 y 2.8 ms (dron, personas y cámara). Hay datos de la prueba de 7 minutos con 42 a 48 fps y la simulación a 3× velocidad, sin caídas.
- Aviso: si la ventana de Unreal pierde el foco, el editor baja a 3-8 fps; se desactivó el límite de fondo (`EditorSettings.ini`, `bThrottleCPUWhenNotForeground=False`). Los 0.6 s por cuadro de los videos eran el Movie Render Queue (muchas muestras por cuadro), no el visor.

**Cadena en vivo:** `en_vivo.py` (simulación, puerto 8767) → `puente_unreal.py` (UDP 8770, 10 pasos por segundo) → `unreal/vivo_unreal.py` dentro del editor (interpola a 30-60 cuadros por segundo). La estación web (Enseñar) manda las órdenes por POST a `en_vivo.py`. `VIVO_UNREAL.bat` abre todo y deja Unreal (60 %) y la estación (40 %) lado a lado en una pantalla (medido en 1536×864: Unreal de 0 a 922 px, Edge de 922 a 1536 px).

**Caída del editor y su arreglo:** `Assertion failed: VertexFactory == nullptr || VertexFactory->IsReadyForStaticMeshCaching()`. Causa: crear o destruir mallas (los paneles de cada partida y las personas con esqueleto) mientras Unreal dibuja. Arreglo: todo se crea una sola vez y las personas se crean de a una con espera; después solo se mueven transformaciones. Prueba: 7 minutos con muchas partidas nuevas, 0 errores en el registro. Además el editor arranca con `-unattended` y un vigilante cierra solo la ventana del Crash Reporter.

**Mapa de teclas final** (Enseñar → Manual; solo teclado y mouse, orden §G.1):
| Tecla / mouse | Hace |
|---|---|
| W S · A D | adelante y atrás · de lado |
| Q E | girar |
| Espacio · C | subir · bajar (techo 7 m) |
| Shift · Ctrl | rápido · lento y preciso |
| F (mantener) | giro de 360° buscando |
| Botón central arrastrado | pan y tilt de la cámara |
| Clic izquierdo | fija al "posible objetivo" resaltado (regla 4: lo decide el humano) |
| Clic derecho | suelta el objetivo (`env.soltar_sospechoso`) |
| Rueda | zoom del mapa |
| V · flechas | cámara asistida · pan y tilt alternativo |
| Tab | alterna centinela (mundo 3D) ⇄ **Vista del dron** |
| 1 · 3 · 4 · 5 | mapa y cámaras · centinela que sigue · **Vista del dron** · centinela libre |
| X · M | CSI#2 grande · Puntos⇄Manual |
| R · G · B · P · Esc · H | ruta · la IA guía (otra vez devuelve) · grabar · pausa · salir del juego · ocultar la chuleta |

**Pruebas hechas con el flujo completo** (VIVO_UNREAL.bat recién abierto, 37 pruebas automáticas OK, y la estación manejada con eventos reales de teclado y mouse):
- Adelante + altura: el dron avanzó y subió de 1.8 a 3.9 m en 3 s; F mantenida: `f360` activo y +131° en 2.5 s.
- Con dos personas a la vista, clic izquierdo sobre el ladrón: el dron pasó de BUSCAR a PERSECUCION; clic derecho: VERIFICAR (objetivo soltado).
- G: la simulación pasó a modo `auto` (la IA guía) y volvió a `ensenar` al presionar G otra vez.
- Botón central arrastrado: el pan y el tilt de la simulación siguieron el arrastre (en la prueba, pan 72° y tilt −29°).
- Maniquíes: el salto se ve en el aire con su sombra; agacharse, caminar agachado, recostarse y gatear se verificaron en la lógica (`pruebas/test_posturas_vivo.py`) pero no tengo una foto clara de cada una.

**Capturas** (todas en `04_VISOR_Y_MOTOR_GRAFICO/mediciones/capturas/`): `unreal_juego_en_vivo.png` (dron plus volando en vivo con paneles y personas), `unreal_en_vivo_dron_cerca.png`, `estacion_ensenar_mapa.png` (mapa con puntos de paso), `unreal_campus_dia2_1.png` y `unreal_campus_dia2_3.png` (adoquín, losas y canaleta), `unreal_campus_fachada2_0.png` y `_1.png` (fachadas de vidrio y de ladrillo), `unreal_campus_halos_0.png` (turbina y luminaria de noche).

**Limitaciones sin resolver:** MetaHuman no se instaló (necesita la cuenta de Epic de Brahian; `docs/PENDIENTES_BRAHIAN_NOCHE.md`); no se probó con un gamepad real (el gamepad es opcional); el clic sobre una persona se probó con el ladrón real a la vista, pero el resaltado de "posible objetivo" en el mapa solo se vio por datos, no en una captura.

## 6. La Vista del dron con imagen real de Unreal (21 oct)

- **Cámaras:** dos `SceneCapture2D` en Unreal (`unreal/vivo_unreal.py`): CSI#1 en el pan-tilt con 68.3° × 54.0° (640×480), inclinación de montaje −2.4° más el tilt y el pan; CSI#2 mirando al piso. Se redibujan a ~10 Hz (CSI#2 ~5 Hz) y se guardan como JPG en `unreal/_cache/cam/`; el servidor de la estación las entrega en `/unreal_cam/cam0.jpg` y `cam1.jpg` (prueba `pruebas/test_camara_unreal.py`). Con Unreal apagado, la estación muestra su propio render 3D.
- **Interfaz:** en la Vista del dron la CSI#1 ocupa la mayor parte de la pantalla con YOLO y la telemetría encima, la CSI#2 es un cuadro pequeño y el mapa de los dos LiDAR va al lado (o debajo si la ventana es angosta). Con Tab se alterna centinela ⇄ Vista del dron sin soltar el dron; las teclas de vuelo valen en las dos.
- **Una sola pantalla:** `VIVO_UNREAL.bat` (sin ventanas de consola, ver `VIVO_UNREAL.ps1`) deja Unreal en el 50 % izquierdo y la estación (Edge) en el 50 % derecho. Evidencia: `04_VISOR_Y_MOTOR_GRAFICO/mediciones/capturas/una_pantalla_juntas.png`, `una_pantalla_estacion_dron.png` y `una_pantalla_unreal.png`.
- **Límite conocido:** la captura de Unreal sale oscura (no tiene la adaptación automática de exposición del viewport); los intentos de fijar la exposición por código no cambiaron nada, así que la estación aclara la imagen con un filtro de brillo (`estacion/modos.css`, clase `.cam-unreal`).
- **Cuadros por segundo con las dos cámaras del dron capturando** (CSI#1 640×480 a 10 Hz y CSI#2 480×360 a 5 Hz, mismo campo de visión 68.3° × 54.0°), mientras la simulación en vivo y un entrenamiento corrían al lado: 37 muestras de 5 s, **mínimo 43.5 y media 54.7 fps** (antes, sin cámaras, 52-60). Por encima de los 30 pedidos, así que no hizo falta bajar más la resolución. Foto final: `04_VISOR_Y_MOTOR_GRAFICO/mediciones/capturas/vista_del_dron_final.png`.
- **Cajas de YOLO:** salen de la proyección de las personas del simulador sobre la cámara con el mismo campo de visión y la misma inclinación (−2.4° + tilt) que el render de Unreal; en la foto final las cajas coinciden con las personas del render.
