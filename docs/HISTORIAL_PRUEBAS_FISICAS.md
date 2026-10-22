# Historial de la parte física · 18 al 20 de octubre de 2026

Registro cronológico de lo que se hizo con el dron real, lo que salió mal y cómo se resolvió. Sirve como evidencia del proceso
(anexos del proyecto de grado): los pasos intermedios, incluidos los fallos, forman parte del resultado. Cada fila apunta al archivo
que la respalda. Lo que no se midió se dice así. Fuente de las cifras: `docs/ESTADO.md`, `datos_campo/` y `05_EVIDENCIA_Y_DIAGRAMAS/`.

## 5 al 17-oct · Antecedentes (resumen de la bitácora de simulación y del primer hardware)

| Fecha | Qué se hizo | Evidencia |
|---|---|---|
| 5-oct | Hardware configurado; arranca la hoja de ruta (validar el LiDAR) | `anexo_historial_octubre_2026/01_gimbal_y_cableado_6a7_oct/` |
| 6-oct | LiDAR TF03 validado con el driver `pl2303`; gimbal BaseCam de 2 ejes: se lee por USB pero el control por serie no respondió | `01_gimbal_y_cableado_6a7_oct/` |
| 7-oct | El proyecto pasa a exteriores (GPS, GUIDED). Pixhawk: modos por CH5, paro CH8, TELEM2 a 115200. Pitch del gimbal por AUX1 (los pines PWM de la Jetson no daban señal). Cámara USB: campo de visión medido 38.9°. LiPo 4S sobredescargada: retirada | `02_pruebas_de_camara_7_a_19_oct/` |
| 8-oct | Dron armado con el gimbal; simulación RL v6-v9 | `03_dron_con_gimbal_8_oct/`, `05_simulacion_y_visor_7_a_11_oct/` |
| 10-oct | Mínimo indispensable en simulación (protocolo del comité: 1300 vuelos sin choques ni activaciones falsas) | `docs/DECISIONES_COMPLETO_SOLO_CONSULTA.md` |
| 11-oct | Decisor IA (MLP) del mínimo; configuración de la batería en Mission Planner | `04_mission_planner_y_simplebgc_11_oct/` |
| 12-17-oct | Planes V15-V17 de la simulación, repositorio en GitHub, pan-tilt del plus en OpenSCAD | `06_pan_tilt_del_plus_18_a_20_oct/`, `09_repositorio_github_17_oct/` |

Fuente completa: `Dron-IA-Proyecto/docs/BITACORA.md`. Los pasos para repetir todo están en `docs/PROCEDIMIENTO_REPLICABLE.md`.

## Domingo 18-oct · Reinstalar la Jetson y verificar el sistema

| Qué se hizo | Dificultad o hallazgo | Evidencia |
|---|---|---|
| Reinstalar la Jetson con JetPack 6.2.1 (L4T R36.4.3, Ubuntu 22.04) en el disco NVMe, para que lea las cámaras CSI | La imagen en microSD por lector USB buscaba su disco raíz en la ranura interna y no arrancaba tras los primeros reinicios; se resolvió **reflasheando en modo recuperación** desde Ubuntu "live" en el PC | `05_EVIDENCIA_Y_DIAGRAMAS/reinstalacion_jetson/` (01 a 08), `docs/REINSTALAR_JETSON_JETPACK6.md` |
| Preparar el PC para arrancar Ubuntu desde USB | El Secure Boot del portátil rechazaba el arranque (error 0x1A), BitLocker pidió la clave de recuperación y una USB de 4 GB corrompía los archivos grandes | `reinstalacion_jetson/07, 08` |
| LiDAR TF03 | El kernel de JetPack 6 no trae el driver `pl2303` del adaptador: se **compiló** con las fuentes del kernel 5.15.148 | `02_JETSON_MINIMO/jp6_driver_pl2303.sh` |
| Verificar con hardware real | LiDAR a 100 Hz; YOLO26n en TensorRT 19-21 ms por cuadro; gimbal y Pixhawk (TELEM2) responden | `capturas/panel_campo_REAL_2026-10-18.jpg` |
| **Paso 3 · intervención en banco** (sin hélices, desarmado) | 17 intervenciones, 0 fallidas, 0 rechazos de GUIDED. Latencia LiDAR → objetivo: media 37.9 ms, máxima 57.3 ms | `01_MINIMO_CONGELADO/registros_campo/paso3_*.log` |
| Cámara USB | Los cuadros por segundo dependían de la luz: 11-15 FPS en interiores y 27-30 FPS con una linterna encima | `docs/ESTADO.md` |

## Lunes 19-oct · Pruebas de campo

| Qué se hizo | Dificultad o hallazgo | Evidencia |
|---|---|---|
| Red en el campo | La Jetson no se conectó a la red del conjunto (no se averiguó por qué); se usó el hotspot del celular | `privado/wifi_<red>_propiedades_2026-10-19.png` (datos de red, no publicar) |
| Panel de campo con control de tomas y pantalla para quien camina (celular) | La imagen de la cámara USB salía **casi blanca** al aire libre: su driver no deja controlar la exposición | `capturas/panel_usb_sobreexpuesto_2026-10-19.png` |
| Probar ajustes de la USB (brillo −64, contraste 64) | Mejoró, pero seguía quemada al sol | `capturas/panel_usb_persona_detectada_2026-10-19.webp` |
| **Cambiar a la cámara CSI IMX219 (CAM0)** | Se activó con `jetson-io` y reinicio; el OpenCV del entorno no trae GStreamer, así que se leyó por una tubería de `gst-launch`. A pleno sol: USB 95 % de píxeles quemados, CSI 0 % | `fotos/19_camara_csi_imx219_J8IM228_en_cam0.jpg`, `capturas/comparacion_camaras_USB_vs_CSI_2026-10-19.jpg` |
| **Tomas del paso 4** (dron desarmado, en el suelo) | 7 tomas: E0 (USB), E1 ×3, E2, E3, E4 (CSI). La persona se detectó en el 91-100 % de los cuadros desde 12 m y a ~25 FPS. El LiDAR casi nunca le daba a la persona (leía la pared a 58 m): **no estaba alineado con la cámara** | `datos_campo/campo_2026-10-19/`, `privado/panel_csi_*_2026-10-19.webp` |
| Transmisión del video lenta | El video iba en JPEG de calidad 92 (~70 KB por cuadro) y el WiFi del celular no lo llevaba: se acumulaba atraso. Se bajó a calidad 55 (~15-25 KB), se limitó el buffer y se codifica en otro hilo | `docs/ESTADO.md`, `02_JETSON_MINIMO/herramientas/medir_video.py` |
| **Decisión de Brahian:** quitar la cámara USB y el gimbal y fijar LiDAR y CSI al chasis | Menos peso y consumo; el gimbal ya no se necesita para el mínimo | `docs/ESTADO.md` |

## Martes 20-oct · Reacomodo, motores, medición de ángulos y re-simulación

| Qué se hizo | Dificultad o hallazgo | Evidencia |
|---|---|---|
| Voltear la estructura: Pixhawk boca abajo bajo la placa inferior, Jetson y GPS arriba | La Pixhawk marcaba roll 180°. Se puso `AHRS_ORIENTATION = 8` y se verificó inclinando el dron (nariz arriba +21.7°, lado derecho abajo +21.6°, giro a la derecha +114°) | `fotos/24` a `27`, `docs/ESTADO.md` |
| **Prueba de motores** (sin hélices, 7 % por 3 s) | Los motores quedaron **espejados y con el giro invertido** respecto a un X normal; volarlo así lo habría volteado. Se corrigió por software (`FRAME_TYPE = 18`, `SERVO1..4_FUNCTION = 36, 33, 34, 35`) y se comprobó cada salida | `diagramas/10_motores_vista_superior.png` |
| Documentar la ubicación de cada componente | Medidas: placas de 15 × 15 cm, 3.85 cm entre placas, caja de la Jetson 4.3 cm, GPS 11.3 cm sobre la placa, ejes del LiDAR y la cámara | `diagramas/11_ubicacion_componentes_vista_lateral.png` |
| Interfaz `/calibrar` para medir ángulos con marcas en la pared, el dedo y líneas verticales | Los clics sobre marcas de 3 píxeles obligaron a agregar una lupa. La cuenta se comprobó con casos inventados de respuesta conocida | `diagramas/12_calibracion_disposicion.png`, `calibracion_angulos_2026-10-20/` |
| **Medición de ángulos** (dron sobre el escritorio, pared lisa a 2.0 m) | Campo de visión de la CSI **68.3° × 54.0°** (no 62.2° × 48.8°), cámara a −2.4°, rayo del LiDAR a −6.7°, giro de la cámara +1.5° (una línea, por confirmar). El LiDAR dio +1.6 cm sobre el metro a 2 m | `datos_campo/calibracion_2026-10-20/`, `calibracion_angulos_2026-10-20/06, 07` |
| **Re-simular el mínimo** con esa geometría | La simulación suponía cámara USB de 38.9° y un gimbal que estabilizaba cámara y LiDAR; ahora ambos van fijos al chasis y siguen su cabeceo | `docs/DECISIONES.md` D-078 y D-079, `03_SIMULACION_RL/minimo_tesis/` |

## Miércoles 21-oct · Preparación del campo con el mínimo sin gimbal

| Qué se hizo | Dificultad o hallazgo | Evidencia |
|---|---|---|
| Verificar la Jetson por SSH antes de salir | Cámara CSI a 25 FPS, YOLO 18 ms, LiDAR leyendo, geometría medida cargada. La Pixhawk no respondía por no tener la batería del dron conectada | `docs/GUIA_CAMPO_21OCT.md` §0 |
| Guía de campo para el parqueadero (pasillo de ~4.5-5 m de ancho, dron sobre el carro, franja azul como línea de E4) | El techo del carro es inclinado: hay que nivelar el dron o se pierde el −6.7° del LiDAR; el panel solo admite 5, 8 o 12 m en E4 | `docs/GUIA_CAMPO_21OCT.md`, `privado/2026-10-21_parqueadero_pasillo_con_dron_en_el_carro.webp` |
| Estación de tierra TALOS-AI adaptada al mínimo (`estacion/minimo.html`) y guía de campo en PDF con diagramas | Se reutilizó la interfaz del plus conectada a la Jetson real mediante un reenvío en `servidor.py`; el panel vivo tiene un detalle: ignora valores vacíos en la URL (la nota no se puede borrar; se manda un espacio) | `Dron-IA-Proyecto/04_VISOR_Y_MOTOR_GRAFICO/estacion/`, `docs/guia_campo_21oct/` |
| Video grande (1280×960), LiDAR y cajas sobre el video, inclinación del dron y más instrumentos de medición; gimbal quitado de las pantallas | La cámara pasó a entregar 1280×960 (YOLO sigue en 640×480). Medido por WiFi de la casa: Normal 29 fps (5 Mbps), Alta 29 fps (12 Mbps), Máxima 29 fps (23 Mbps) después de corregir un error del codificador que las dejaba en 15 fps. Hubo un fallo propio: `/sys/class/thermal` lanzó un `TypeError` y el servicio se reiniciaba cada ~27 s hasta que se corrigió | `docs/GUIA_CAMPO_21OCT.md` §0 bis, `Dron-IA-Proyecto/04_VISOR_Y_MOTOR_GRAFICO/estacion/minimo.*` |
| Mapa GPS, velocidades (avance y ascenso), GPS (satélites, HDOP) y sonido del portátil en la estación; Tatiana opera el portátil y Brahian camina sin celular | La Pixhawk entrega 3D+DGPS con 8-9 satélites y HDOP ≈ 1.5-2 (probado con la batería y la Futaba; Brahian armó sin hélices, subió potencia y cortó con CH8: respondió). Se agregaron GPS_RAW_INT y VFR_HUD al lector MAVLink y 8 columnas nuevas al `datos.csv` | `Dron-IA-Proyecto/04_VISOR_Y_MOTOR_GRAFICO/estacion/minimo.*`, `02_JETSON_MINIMO/registro_minimo.py` |
| **Campo del 21-oct (paso 4)**: 22 tomas válidas (E1 ×5, E2 ×6, E3 ×5, E4 caminando ×7) con el dron sin hélices sobre el techo de un carro; faltaron E0, E4 trotando, E5 y E6 por los apagones del portátil | El LiDAR coincidió con la cinta (+0.02 a +0.08 m); YOLO 82 % a 15 m. La Pixhawk dio cabeceo +4° y alabeo −2.4°: de ahí salió que el montaje real es LiDAR −9.0° y cámara −5.6° respecto al chasis (el escritorio dio −6.7° y −2.4° respecto al horizonte). Un apagón dejó una toma "fantasma" y los videos sin cerrar | `datos_campo/campo_2026-10-21/INFORME_CAMPO_21OCT.md`, D-082 |
| Evidencia del campo del 21-oct (4 fotos, 2 videos de WhatsApp → 3 GIF y 7 cuadros) y autorización de rostros de Brahian y Tatiana; índice maestro, horas de trabajo (141 h de actividad, ~82 h de reloj) y dificultades | Placas difuminadas; interiores de la vivienda, redes y terceros siguen privados | `05_EVIDENCIA_Y_DIAGRAMAS/campo_2026-10-21/`, `rostros_autorizados/`, `docs/INDICE_MAESTRO_PARA_EL_DOCUMENTO.md` |

## Pendiente a esta fecha
- Calibrar acelerómetro y brújula de la Pixhawk; probar el paro de emergencia (CH8) y la falla por batería baja.
- Confirmar el giro de la cámara con una segunda línea vertical; comparar el LiDAR con el metro a 1 y 1.5 m.
- Re-simulación del mínimo y comparación de decisores: **hecha** (D-079); falta escribir `sistema_minimo.py` (modo sombra).
- Decidir por escrito la altura del mínimo (2.0 m propuesta; la regla D-043 pide 3.30 m de altura segura).
- Repetir E0, E4 trotando, E5, E6 y completar E2/E3 con el montaje definitivo (tras recalibrar el 22-oct); medir la CSI#2 del plus.
- Antes del primer vuelo: el mínimo **no ha volado con la Jetson**. Solo hubo un vuelo del dron sin ella que terminó en failsafe por batería.
