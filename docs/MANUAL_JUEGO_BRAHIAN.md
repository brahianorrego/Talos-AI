# Manual del juego (Brahian)

## Empezar en 3 pasos
1. Haz doble clic en `04_VISOR_Y_MOTOR_GRAFICO\VIVO_UNREAL.bat`. Abre la simulación, Unreal (a la izquierda, el mundo) y la estación (a la derecha) en la misma pantalla, sin ventanas negras de consola. Espera 1-2 minutos a que Unreal cargue.
2. En la estación, entra a **Enseñar** (ya abre ahí) y pulsa el botón **Manual** (o la tecla **M**). Para ver lo que ve el dron pulsa **Tab** (otra vez Tab regresa al mundo).
3. Vuela con las teclas de abajo. Si Unreal se cierra o algo falla, vuelve a abrir el `.bat`; el aviso de error de Unreal se cierra solo.

Antes de jugar: mantén la ventana de la estación al frente al teclear (las teclas las lee ella, no Unreal).

## Teclas (mano izquierda en el teclado, mano derecha en el mouse)
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
| Rueda | acerca o aleja el mapa |
| V · flechas | cámara asistida (sigue sola al objetivo) · pan y tilt con el teclado |
| **Tab** | **alterna centinela (mundo 3D) ⇄ Vista del dron** (lo que ve el dron) |
| 1 | mapa y cámaras |
| 3 · 4 · 5 | centinela (mundo que sigue al dron) · **Vista del dron** · centinela libre |
| X | la cámara 2 pasa a ser la grande (en la pantalla de mapa y cámaras) |
| M | cambia entre Puntos (clic en el mapa) y Manual |
| R · G · B · P · Esc · H | ruta · la IA guía (otra vez te devuelve el control) · grabar tu demostración · pausa · salir · ocultar esta ayuda |

La ayuda también está en pantalla (esquina del mapa) mientras juegas.

## Cómo se juega la búsqueda
Mantén **F**: el dron gira 360°. Cuando aparezca una persona, sale marcada "posible objetivo". Haz **clic izquierdo** sobre ella: si es el sospechoso, el dron lo fija; si no, queda descartada. Con el clic derecho lo sueltas. **G** deja que la IA guíe y te muestra qué haría; vuelve a pulsar G para recuperar el control. **B** graba tu partida (queda en `03_SIMULACION_RL\demos_brahian\`).

## Si algo no va
- La estación dice "Falta la simulación en vivo": cierra todo y abre otra vez `VIVO_UNREAL.bat`.
- Unreal se ve lento: cierra otros programas pesados; mide ~60 fps con todo cerrado.
- Noche (opcional): `docs/PENDIENTES_BRAHIAN_NOCHE.md` y el modo `DRONIA_NOCHE=1` al armar el nivel; por defecto es de día.

## La Vista del dron (la de operación)
Es lo que ve el dron: la **CSI#1** (cámara principal en el pan-tilt, 68.3° × 54.0°) casi a pantalla completa, con las cajas de YOLO y la telemetría encima (modo, objetivo, tiempo a la vista, distancias del TF03 y del TF-Luna, pan/tilt, geocerca, batería simulada y fps); un cuadro pequeño con la **CSI#2** (mira al piso); y el **mapa de los dos LiDAR de 1 haz** (TF03 azul, TF-Luna ámbar). La imagen es un render de Unreal desde el punto de vista del dron. Si Unreal no está abierto, se ve el render 3D de la propia estación (la telemetría dice "imagen 3D").
