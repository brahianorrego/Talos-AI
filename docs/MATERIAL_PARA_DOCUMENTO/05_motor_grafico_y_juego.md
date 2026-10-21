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
**Unreal en vivo en esta RTX: [pendiente]**; no hay una medición registrada en los documentos del repositorio. Si da menos de 15 cuadros por segundo, se deja como video (orden de Brahian, `docs/ORDENES_BRAHIAN_20OCT.md` §F).

## 4. Qué se pidió corregir (para contar el proceso)

Quitar el vuelo entre canchas (tecla T), un solo escenario seleccionable (cancha de fútbol o de tenis), árboles y edificios más realistas, mapa a pantalla completa, ingeniería fuera del primer plano, vista de vuelo real con cámara principal grande, mapa de los dos LiDAR de 1 haz y cámara 2 abajo, y quitar el botón "Dron: Mínimo/Plus" (`docs/ORDENES_BRAHIAN_20OCT.md` §F). Varias ya están hechas (commits `47f70ba`, `d44b52b`, `bb61d0c`, `81d71b2`).
