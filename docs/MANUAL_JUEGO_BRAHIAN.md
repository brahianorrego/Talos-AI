# Manual del juego (Brahian)

## Empezar en 3 pasos
1. Haz doble clic en `04_VISOR_Y_MOTOR_GRAFICO\VIVO_UNREAL.bat`. Abre la simulación, Unreal (a la izquierda) y la estación (a la derecha) en la misma pantalla. Espera 1-2 minutos a que Unreal cargue.
2. En la estación, entra a **Enseñar** (ya abre ahí) y pulsa el botón **Manual** (o la tecla **Tab**).
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
| 1 · 2 · 3 · 4 | cámara principal grande · cámara 2 grande · vista 3D que sigue · vista 3D libre |
| Tab | cambia entre Puntos (clic en el mapa) y Manual |
| R · G · B · P · Esc · H | ruta · la IA guía (otra vez te devuelve el control) · grabar tu demostración · pausa · salir · ocultar esta ayuda |

La ayuda también está en pantalla (esquina del mapa) mientras juegas.

## Cómo se juega la búsqueda
Mantén **F**: el dron gira 360°. Cuando aparezca una persona, sale marcada "posible objetivo". Haz **clic izquierdo** sobre ella: si es el sospechoso, el dron lo fija; si no, queda descartada. Con el clic derecho lo sueltas. **G** deja que la IA guíe y te muestra qué haría; vuelve a pulsar G para recuperar el control. **B** graba tu partida (queda en `03_SIMULACION_RL\demos_brahian\`).

## Si algo no va
- La estación dice "Falta la simulación en vivo": cierra todo y abre otra vez `VIVO_UNREAL.bat`.
- Unreal se ve lento: cierra otros programas pesados; mide ~60 fps con todo cerrado.
- Noche (opcional): `docs/PENDIENTES_BRAHIAN_NOCHE.md` y el modo `DRONIA_NOCHE=1` al armar el nivel; por defecto es de día.
