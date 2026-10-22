# Dificultades de la parte física y cómo se resolvieron (6 al 21 de octubre de 2026)

Brahian pidió que se cuente todo lo que costó: los fallos son parte del resultado y de la metodología. Cada fila sale de `docs/HISTORIAL_PRUEBAS_FISICAS.md`, `docs/ESTADO.md` o de los datos de campo; las cifras de tiempo de trabajo, en `docs/HORAS_DE_TRABAJO.md`.
Para la parte de simulación (entrenamientos, versiones del visor, Unreal) ver `Dron-IA-Proyecto/docs/MATERIAL_PARA_DOCUMENTO/02_errores_y_lecciones.md`.

| Fecha | Qué falló o costó | Causa | Cómo se resolvió |
|---|---|---|---|
| 6-7 oct | El control del gimbal por serie no respondía; los pines PWM de la Jetson no daban señal | Firmware sin ese control; el overlay del PWM dejaba la salida desconectada | Pitch del gimbal desde la Pixhawk (AUX1) |
| 7 oct | La Pixhawk no entendía a la Jetson por TELEM2 | A 460800 y 921600 baudios la Jetson transmite con error | 115200 baudios (`SERIAL2_BAUD = 115`) |
| 7 oct | LiPo sobredescargada | Sin vigilar el voltaje | Se retiró; desde entonces se vigila por MAVLink (aviso 14.4 V, corte 14.0 V) |
| 7 oct | La cámara USB mostraba una cuadrícula y se quemaba al sol | Sin filtro IR-cut; el driver no deja controlar la exposición | Se cambió a la cámara CSI IMX219 (19-oct) |
| 18 oct | La Jetson no arrancaba tras instalar JetPack 6 desde microSD | La imagen buscaba su disco en la ranura interna | Reflasheo en modo recuperación desde Ubuntu "live" en el PC |
| 18 oct | El PC no arrancaba la USB; BitLocker pidió la clave; una USB de 4 GB corrompía archivos | Secure Boot (error 0x1A), disco cifrado, una memoria de 4 GB que corrompía los archivos grandes | Secure Boot desactivado un rato, clave a mano, USB de mayor capacidad |
| 18 oct | El LiDAR no aparecía | El kernel de JetPack 6 no trae el driver `pl2303` | Compilado con las fuentes del kernel (`jp6_driver_pl2303.sh`) |
| 19 oct | La Jetson no conectó a la red <red del conjunto> en el campo | Sin averiguar | Hotspot del celular |
| 19 oct | La imagen salía casi blanca al sol | Exposición fija de la USB | Cámara CSI con exposición automática: 0 % de píxeles quemados |
| 19 oct | La CSI no se podía leer con OpenCV | El OpenCV del entorno no trae GStreamer | Lectura por una tubería de `gst-launch` (`CamaraTuberiaGst`) |
| 19 oct | El video iba con segundos de atraso | JPEG de calidad 92 en WiFi de celular | Calidad 55, buffer chico y codificación en otro hilo |
| 19 oct | El LiDAR casi nunca le pegaba a la persona | No estaba alineado con la cámara | Visor `/alinear` y luego `/calibrar` |
| 20 oct | Los motores giraban espejados | Disposición X_REV por la Pixhawk al revés | `FRAME_TYPE = 18` y reasignar salidas, solo por software |
| 20 oct | El script de calibración del acelerómetro falló | La Pixhawk repetía la petición de posición | Se calibró en Mission Planner |
| 20 oct | Los clics sobre marcas de 3 píxeles eran imprecisos | Marcas muy chicas | Lupa en `/calibrar` |
| 20 oct | La re-simulación del mínimo dio las mismas cifras de antes | El entrenamiento reutilizó datos guardados del 11-oct | Se apartaron y se repitió (D-079) |
| 21 oct | El portátil se apagó 3 veces en el campo y la Jetson perdió la energía | Batería del portátil y alimentación | Se cargó un rato y se siguió; faltaron las últimas pruebas (E0, E4 trotando, E5, E6) |
| 21 oct | Una toma "fantasma" y videos sin cerrar tras los apagones | El archivo de control de tomas seguía en disco; el AVI no se cierra con un apagón | El servicio borra el archivo al arrancar; los videos se leen en secuencia |
| 21 oct | Video grande a 15 fps y un reinicio cada 27 s | Un error de ritmo del codificador; una lectura de temperatura que lanzaba `TypeError` | Corregidos y medidos (29 fps) |
| 21 oct | El rayo del LiDAR tocaba el suelo a ~12 m en vez de 17 m | Los ángulos del escritorio estaban medidos respecto al horizonte, no al chasis | Se descubrió con el cabeceo de la Pixhawk (D-082); se recalibra el 22-oct |
