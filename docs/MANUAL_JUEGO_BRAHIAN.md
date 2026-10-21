# Manual del juego (Brahian)

## Empezar en 3 pasos
1. Haz doble clic en `04_VISOR_Y_MOTOR_GRAFICO\VIVO_UNREAL.bat`. Abre la simulación, Unreal (a la izquierda, el mundo) y la estación de tierra (a la derecha), sin ventanas negras de consola. Espera 1-2 minutos a que Unreal cargue.
2. La estación abre en la **cámara del dron** y la IA guía el dron. Pulsa cualquier tecla de vuelo (W, A, S, D…) o **G** para tomar el mando.
3. Vuela con las teclas de abajo. Si algo falla, vuelve a abrir el `.bat` (el aviso de error de Unreal se cierra solo).

Mantén la ventana de la estación al frente al teclear: las teclas las lee ella, no Unreal.

## La pantalla (una sola, para volar, enseñar y operar)
- **Izquierda (~68 %):** la cámara principal (CSI#1, en el pan-tilt, 68.3° × 54.0°) con el horizonte, el rumbo, las cajas de YOLO, el modo y el objetivo. La imagen es un render de Unreal desde el dron; sin Unreal dice "sin señal de video".
- **Derecha, tres casillas fijas:** la cámara al piso (CSI#2); el mapa de los dos LiDAR de 1 haz (TF03 azul, TF-Luna gris claro, los puntos se acumulan); y la telemetría (altura, velocidad, batería, GPS, enlace, modo de vuelo, distancias, geocerca) con el indicador de actitud (el dron visto desde atrás) y el minimapa de la cancha con la geocerca.
- **Barra de arriba:** el nombre del dron, modo, control, enlace, hora y los botones Pausa, Ruta, Grabar y Ajustes. Todo lo demás está en **Ajustes (Esc)**: vistas, control del dron, misión (en vivo o repeticiones), ruta, cámara asistida, escena y teclas.
- **Mapa táctico (para enseñar):** con **Tab** (o la tecla **1**) el lado izquierdo cambia al mapa visto desde arriba; ahí haces clic para poner puntos de paso y arrastras el círculo para girar la flecha. **4** o Tab otra vez vuelve a la cámara.

## Teclas
| Tecla / mouse | Hace |
|---|---|
| W S · A D | adelante y atrás · de lado |
| Q E | girar |
| Espacio · C | subir · bajar |
| Shift · Ctrl | rápido · lento y preciso |
| **F (mantener)** | giro de 360° buscando |
| **Clic izquierdo** | fija a la persona resaltada ("posible objetivo") |
| Clic derecho | suelta el objetivo |
| **Botón central del mouse, arrastrando** | mueve la cámara (pan y tilt) |
| V · flechas | cámara asistida (sigue sola al objetivo) · pan y tilt con el teclado |
| **G** | la IA guía el dron · otra vez te devuelve el mando |
| M | cambia entre Puntos de paso y Manual |
| Tab · 1 · 4 | alterna cámara ⇄ mapa · mapa · cámara |
| R · B · P | ruta de búsqueda · grabar tu demostración · pausa |
| Rueda | zoom del mapa táctico |
| **X** · K | cámara al piso (CSI#2) a pantalla grande y volver · cuadrícula de distancia en esa cámara |
| Esc | Ajustes y ayuda |

## Cómo se juega la búsqueda
Mantén **F**: el dron gira 360°. Cuando aparezca una persona, sale en una caja de YOLO y marcada "posible objetivo". Haz **clic izquierdo** sobre ella: si es el sospechoso, el dron lo fija; si no, queda descartada. Con el clic derecho lo sueltas. **B** graba tu partida (queda en `03_SIMULACION_RL\demos_brahian\`).

## Si algo no va
- Dice "SIN ENLACE" o no hay datos: cierra todo y abre otra vez `VIVO_UNREAL.bat`.
- "Sin señal de video": Unreal todavía está cargando (o está cerrado). La telemetría y los mapas siguen funcionando.
- Noche (opcional): `docs/PENDIENTES_BRAHIAN_NOCHE.md` y el modo `DRONIA_NOCHE=1` al armar el nivel; por defecto es de día.
- La estación anterior (con el mundo 3D propio, Ingeniería, etc.) sigue en `http://127.0.0.1:8768/` por si hiciera falta; la de operación es `operacion.html`.
