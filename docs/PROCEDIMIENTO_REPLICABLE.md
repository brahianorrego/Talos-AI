# Procedimiento para replicar el proyecto, paso a paso

Escrito el 2026-10-20. Es una tesis experimental: este documento dice **cómo se hizo cada cosa** con el orden, las herramientas, los
valores que se midieron y lo que falló, para que otra persona pueda repetirlo. Cada paso apunta al archivo que lo respalda.
Lo que **no** se midió o no se verificó está marcado como *(sin verificar)*. Las fotos, capturas y diagramas están en
`05_EVIDENCIA_Y_DIAGRAMAS/` (índice cronológico en `anexo_historial_octubre_2026/INDICE.md`).

No se publican aquí contraseñas, direcciones IP, nombres de redes ni números de serie: se reemplazan por `<...>`. Hay que poner los propios.

## 0. Qué se construye y con qué

Un dron cuadricóptero con piloto humano, al que un computador a bordo (Jetson) le agrega un **mínimo indispensable**: si ve una persona
cerca (cámara + LiDAR) y el piloto está en el modo habilitado, pide a la Pixhawk que **frene y suba**; nunca arma ni despega por su cuenta.

| Pieza | Modelo usado | Notas |
|---|---|---|
| Computador a bordo | Jetson Orin Nano Super, NVMe | JetPack 6.2.1 (L4T R36.4.3, Ubuntu 22.04) |
| Autopiloto | Pixhawk 2.4.8, ArduCopter 4.7.0 | Mission Planner 1.3.76 para configurar |
| LiDAR | Benewake TF03 | 115200 baudios, adaptador USB-serie PL2303; 100 Hz |
| Cámara | IMX219 (Raspberry Pi) en CAM0 de la Jetson | Cable CSI; antes se probó una USB Sonix y se descartó |
| Detector | YOLO26n (ultralytics) en TensorRT FP16 | ~19-25 ms por cuadro en la Jetson |
| Radio | Futaba (CH5 modos, CH7 habilita el modo experimental, CH8 paro de emergencia) | |
| ESC / batería | Readytosky 40 A / LiPo 4S | Batería original sobredescargada: se retiró (7-oct) |
| Estructura | Dos placas de 15 × 15 cm separadas 3.85 cm | Pixhawk abajo, Jetson y GPS arriba |

Diagramas: `diagramas/10_motores_vista_superior`, `11_ubicacion_componentes_vista_lateral`, `12_calibracion_disposicion`,
y los de conexiones `01`, `07`, `09`.

## 1. Preparar la Jetson (JetPack 6.2.1)

Se instaló JetPack 6 porque la cámara CSI IMX219 no funcionaba por Argus en JetPack 7 (R39). Detalle y alternativas: `docs/REINSTALAR_JETSON_JETPACK6.md`.

1. **Instalar por modo recuperación, no por microSD.** La imagen de microSD puesta en un lector USB buscaba su disco raíz en la ranura interna
   y dejó de arrancar tras los primeros reinicios. Lo que funcionó: PC con **Ubuntu "Probar" desde una USB** (no Windows ni máquina virtual),
   SDK Manager de NVIDIA, Jetson en **modo recuperación** (puente entre los pines FC REC y GND, cable USB-C al PC) y flasheo al NVMe.
   *Trampas del PC:* Secure Boot rechazaba el arranque de la USB (error 0x1A) y hubo que desactivarlo temporalmente; BitLocker pidió la clave de
   recuperación (tenerla a mano; al terminar, reactivar BitLocker y Secure Boot); una USB de 4 GB corrompió archivos grandes (usar una de ≥ 16 GB).
   Evidencia: `05_EVIDENCIA_Y_DIAGRAMAS/reinstalacion_jetson/` (01 a 08).
2. Primer arranque: crear el usuario, poner un nombre de equipo (`talos-jetson`) y conectar a una red. Guardar SSH por llave (`ssh-copy-id`).
3. Instalar el entorno (`02_JETSON_MINIMO/jp6_paso1_sudo.sh`, `jp6_paso2_python.sh`, `jp6_paso3_motor_yolo.sh`): CUDA 12.6, cuDNN 9, TensorRT 10.3,
   PyTorch 2.10 con GPU, `ultralytics`, `pymavlink`, `pyserial`; usuario en los grupos `dialout` y `video`; apagar `ModemManager`.
4. **Motor TensorRT:** `yolo export model=yolo26n.pt format=engine half=True` (~7 min, se hace en la propia Jetson; no se copia de otro equipo).
5. **Driver del LiDAR:** el kernel de JetPack 6 no trae `pl2303`. Se compiló con las fuentes del kernel (5.15.148):
   `jp6_driver_pl2303.sh` y `jp6_instalar_pl2303.sh`. **Hay que repetirlo si se actualiza el kernel.**
6. Modo de potencia: 25 W por defecto; `jp6_maximo_rendimiento.sh` pone el máximo (cuidado con el consumo del regulador del dron).
7. **Verificar:** `verificar_minimo.sh` (CUDA, TensorRT, puertos, cámaras).

## 2. Conexiones

- **Pixhawk ↔ Jetson:** TELEM2 con el UART del conector de 40 pines (`/dev/ttyTHS1`), TX con RX cruzados y GND común; **sin el cable de 5 V**.
  Parámetros: `SERIAL2_PROTOCOL = 2`, `SERIAL2_BAUD = 115`, `BRD_SER2_RTSCTS = 0`. A 460800 y 921600 la Pixhawk no entendió a la Jetson (6-7 oct).
  El USB Pixhawk-Jetson solo en banco: devuelve 5 V.
- **LiDAR:** por el adaptador PL2303 (ruta fija en `/dev/serial/by-id/`; `ls -l /dev/serial/by-id/` y copiar la propia a `config.py`).
- **Cámara CSI:** cable al puerto CAM0. Activar con `sudo /opt/nvidia/jetson-io/config-by-hardware.py -n 2='Camera IMX219-A'` y reiniciar.
  Aparece como `/dev/video0`; Argus (`nvarguscamerasrc`) controla bien la exposición.
- **OpenCV sin GStreamer:** el entorno virtual trae `opencv-python 5.0.0.93` sin GStreamer. Solución usada: leer la cámara por una **tubería de `gst-launch`**
  (`percepcion.py`, clase `CamaraTuberiaGst`, `CAMARA_TIPO = "csi_tuberia"`, captura 1640×1232 reducida a 640×480, antibandas `aeantibanding=2`).
  Con la USB Sonix a pleno sol el 95 % de los píxeles salían quemados; con la CSI, 0 % (`capturas/comparacion_camaras_USB_vs_CSI_2026-10-19.jpg`).
- **Montaje final (decisión del 19-oct):** sin gimbal y sin cámara USB; LiDAR y CSI fijos al chasis, apuntando al frente (se ven en `diagramas/11`).

## 3. Configurar la Pixhawk (Mission Planner + MAVLink)

Valores usados (los comprobó la Jetson por MAVLink con `herramientas/pixhawk_param.py` y `verificar_pixhawk.py`):

| Parámetro | Valor | Motivo |
|---|---|---|
| `FLTMODE1..6` | incluir STABILIZE, ALT_HOLD, LOITER y GUIDED | el piloto entra y sale de GUIDED con el interruptor CH5 |
| `GUID_TIMEOUT` | 3 | si la Jetson deja de enviar, el dron frena solo |
| `BATT_LOW_VOLT` / `BATT_CRT_VOLT` | 13.5 / 13.2 | falla por batería baja |
| `BATT_FS_VOLTSRC` | 1 | voltaje compensado por caída (evita aterrizajes falsos) |
| `AHRS_ORIENTATION` | 8 (Roll180) | la Pixhawk quedó **boca abajo** bajo la placa inferior |
| `FRAME_TYPE` | 18 (X_REV) | los motores estaban espejados y con giro invertido (ver §5) |
| `SERVO1..4_FUNCTION` | 36, 33, 34, 35 | reasigna las salidas a los motores, solo por software |

Calibrar el **acelerómetro** (seis posiciones) y la **brújula**: *(sin hacer al 20-oct; lo hará Brahian en Mission Planner)*. Mi script de acelerómetro
falló porque la Pixhawk repetía la petición de posición; se descartó y se hace con Mission Planner (`herramientas/calibrar_pixhawk.py` queda como intento).
Probar el paro de emergencia (CH8) y la falla por batería baja: *(sin verificar)*.

## 4. Verificar la orientación (dron en las manos, sin hélices)

`herramientas/probar_orientacion.py` y `foto_actitud.py` registran la actitud mientras se inclina el dron en posiciones indicadas. Resultado del 20-oct:
nariz arriba → pitch +21.7°; lado derecho abajo → roll +21.6°; giro a la derecha → rumbo +114°. Eso confirma `AHRS_ORIENTATION = 8`.

## 5. Probar los motores uno por uno (**sin hélices**, Futaba encendida y paro a la mano, botón de seguridad fijo)

1. `herramientas/probar_motor.py <n>` manda `MAV_CMD_DO_MOTOR_TEST` al 7 % por 3 s. El número sigue el orden A-B-C-D de ArduPilot (en el sentido de las manecillas desde el delantero derecho de un X normal).
2. El observador se ubica **detrás del dron, mirando hacia donde mira la nariz**, y dice qué motor giró y en qué sentido (anotar siempre desde qué lado se mira: hubo una confusión derecha/izquierda).
3. Hallazgo (20-oct): salida 1 = delantero izquierdo antihorario, 2 = trasero derecho antihorario, 3 = delantero derecho horario, 4 = trasero izquierdo horario.
   Es la disposición `X_REV` del código de ArduPilot (`AP_MotorsMatrix.cpp`). Se puso `FRAME_TYPE = 18` y se reasignaron las salidas; se repitió la prueba y salió como se esperaba.
4. **Hélices al montarlas:** giro horario en delantero derecho y trasero izquierdo; antihorario en delantero izquierdo y trasero derecho.
5. No se pueden leer ni cambiar los ESC Readytosky por la Pixhawk (exigen DShot y salidas AUX); quedó descartado.

## 6. El código del mínimo en la Jetson

Carpeta `02_JETSON_MINIMO/` (se sube a `~/Escritorio/dron_ia/`; el `config.py` de la Jetson lleva los seriales reales, el del repositorio los trae como `<NUMERO_DE_SERIE>`).

| Archivo | Función |
|---|---|
| `lidar_tf.py` | Lee las tramas de 9 bytes del TF03 |
| `percepcion.py` | Cámara + YOLO con seguimiento (`track()`, ByteTrack) |
| `registro_minimo.py` | Registra una fila por cuadro (CSV, video); con `--panel 8080` sirve el panel y con `--tomas` etiqueta las tomas |
| `panel_campo.py` | Panel web (Python `http.server`): `/` video con datos, `/persona` pantalla para quien camina, `/alinear`, `/calibrar`, `/toma/*` |
| `intervencion_banco.py` | Paso 3: lazo LiDAR → GUIDED → objetivo 3.30 m, medido en banco |
| `campo.service` | Servicio de usuario `systemd` que arranca el panel al encender (`loginctl enable-linger`) |

Panel de campo: `http://<nombre-de-la-jetson>.local:8080` (o la IP). Se accede desde el PC o el celular en la misma red.
**Transmisión del video:** JPEG calidad 92 (~70 KB por cuadro) se atrasaba en el WiFi del celular; con calidad 55, buffer de envío de 64 KB, codificación en otro hilo y
solo si hay espectadores, el cuadro baja a ~15-25 KB (`herramientas/medir_video.py` mide FPS, Mbps y atraso desde el PC).

## 7. Calibrar los ángulos de la cámara y del LiDAR (se hizo el 20-oct)

Se necesita un dron fijo sobre una superficie, una pared lisa a ~2 m, cinta, metro y el panel abierto en `/calibrar` (`02_JETSON_MINIMO/calibrar.html`).
Diagrama: `diagramas/12_calibracion_disposicion`. Datos de la corrida: `datos_campo/calibracion_2026-10-20/`; capturas: `05_EVIDENCIA_Y_DIAGRAMAS/calibracion_angulos_2026-10-20/`.

1. **Medidas del montaje:** altura del eje del LiDAR (27.5 cm sobre el escritorio) y del eje de la cámara (32.0 cm); la cámara queda **6 cm detrás** del frente del LiDAR.
2. **Marcas en la pared (cuatro cintas):** B a 40 cm y T a 150 cm sobre la línea central; L y R a 90 cm de la línea central cada una (180 cm entre sí), a 94.5 cm del piso.
   Distancia del frente del LiDAR a la pared: 200.5 cm con metro (el LiDAR dio 202.1 cm, +1.6 cm).
3. **Paso 1 y 2:** clic en L y R (separación conocida) → campo de visión horizontal; clic en B y T (alturas conocidas) → vertical e inclinación de la cámara. La interfaz trae lupa porque las marcas son de ~3 píxeles.
4. **Paso 3:** una línea vertical (plomada o esquina) → giro (roll) de la cámara.
5. **Paso 4:** el dedo delante del LiDAR; el número del panel se pone verde al tocarlo; clic en la punta del dedo. Siete clics a 1.0-1.5 m → punto del LiDAR en la imagen.
6. **Cuentas** (en `panel_campo.py`, `_api_calibrar`): tan(H/2) = S / (D · Δx_n); la inclinación del LiDAR sale de tan p_L = (D_cam · tan ε + (hc − hl)) / D_L. La cuenta se verificó con un caso inventado de respuesta conocida (recuperó 62.2°, 48.8°, −5°, −5°).
7. **Resultado:** campo de visión **68.3° × 54.0°** (nominal del fabricante: 62.2° × 48.8°), relación V/H 0.751 (ideal 4:3 → 0.750), inclinación de la cámara **−2.4°**, inclinación del rayo del LiDAR **−6.7°**, desvío horizontal −0.6°, giro **+1.5° (una sola línea, provisional)**.
   Se escribe en `config.py` (`CAMARA_HFOV_DEG`, `CAMARA_VFOV_DEG`, `CAMARA_PITCH_DEG`, `LIDAR_PITCH_DEG`).
   *Incertidumbre:* ≈ ±1.5° por la distancia lente–frente del LiDAR; no se repitió con otra distancia.

## 8. Tomas de campo (paso 4)

Desde el panel (`/`): elegir el escenario (E0-E6), la repetición, la altura y las notas; la pantalla del celular (`/persona`) guía a quien camina con cuenta regresiva, voz y vibración.
Cada toma guarda el CSV etiquetado, el `video.avi` y las filas `INICIO/FIN` en `tomas.csv`. `herramientas/resumir_tomas.py` las resume.
El 19-oct se grabaron 7 tomas con el dron desarmado en el suelo (`datos_campo/campo_2026-10-19/`); sirvieron para descubrir que el LiDAR no estaba alineado con la cámara.
**Hay que repetirlas con la geometría ya medida** *(pendiente)*.

## 9. Simulación del mínimo y entrenamiento del decisor

Carpeta del repositorio de simulación: `03_SIMULACION_RL/` (otro repositorio de trabajo, `Dron-IA-Proyecto`). Entorno: Python 3.11 con `.venv`.

1. **Simulador:** `minimo_tesis/sensores.py` (cámara con campo de visión medido, LiDAR con su inclinación, ruido y retardo de 100 ms), `sistema.py` (dron, chasis que cabecea, árbitro), `protocolo_comite.py` (13 escenarios con semillas fijas).
2. **Geometría que usa el simulador** (medida el 20-oct): `HFOV, VFOV = 68.3, 54.0`; cámara a −2.4°, LiDAR a −6.7° respecto al chasis (ambos siguen el cabeceo del chasis, no hay gimbal); altura de vuelo del mínimo 2.0 m (`MINIMO_Z_PILOTO`; la regla D-043 pide 3.30 m con alguien cerca).
3. Correr las pruebas: `.venv\Scripts\python.exe -m unittest discover -s tests -p test_minimo_tesis.py` y `-p test_decisor_ia.py` desde `03_SIMULACION_RL` (13 + 6 pasan al 20-oct).
4. **Protocolo del comité:** `.venv\Scripts\python.exe -u -m minimo_tesis.protocolo_comite` → `informes/minimo_tesis_protocolo.md` (13 escenarios: 100 % de éxito, 0 activaciones falsas con la geometría medida). Velocidad segura máxima del panel baja de 11 a 5 m/s porque el rayo del LiDAR a −6.7° toca el suelo a ~17 m.
5. **Decisor IA** (MLP de scikit-learn 32-16 con 15 entradas normalizadas por el campo de visión): `entrenar_decisor.py` genera los datos (vuelos sin intervención con etiquetas automáticas del simulador, separados por semillas), entrena y exporta `decision.pkl` y `decision.json`; `evaluar_decisores.py` lo compara con las reglas.
   **Cuidado:** `entrenar_decisor.py` reutiliza `datos/*.npz` y `clf_*.pkl` si existen. Al cambiar la geometría hay que **borrarlos o apartarlos**; el 20-oct el primer resultado salió con los datos viejos y por eso se repitió (ver `docs/DECISIONES.md` D-079); resultados con la geometría medida: protocolo 100 %, AUC 0.961, panel 5 m/s.
6. Regla dura (D-043): si hay una persona cerca, subir a 3.30 m; la IA no puede saltarse el árbitro (`árbitro de seguridad`).

## 10. Orden recomendado para repetirlo desde cero

1. Armar el dron y conectar (§0, §2). 2. Instalar la Jetson (§1). 3. Configurar la Pixhawk (§3) y verificar orientación (§4). 4. Probar motores sin hélices (§5).
5. Subir el código y comprobar el panel (§6). 6. Calibrar ángulos (§7). 7. Entrenar el decisor con esa geometría (§9). 8. Intervención en banco, tomas de campo, modo sombra (`sistema_minimo.py`, *sin escribir*), primer vuelo con piloto de seguridad.

## 11. Lo que falló y cómo se resolvió (para no repetirlo)

Ver `docs/HISTORIAL_PRUEBAS_FISICAS.md` (18-20 oct) y `docs/ESTADO.md` ("Qué se rompió el 18-oct"). Resumen: arranque por microSD, Secure Boot/BitLocker, USB de 4 GB, driver `pl2303`, cámara USB quemada al sol,
OpenCV sin GStreamer, video con atraso por WiFi del celular, motores espejados, orientación de la Pixhawk, script de acelerómetro, cuentas del campo de visión con marcas diminutas, geometría vieja en la simulación, caché de datos viejos en el entrenamiento.

## 12. Lo que todavía no está verificado

Calibración de acelerómetro y brújula; paro CH8; falla por batería baja; segunda línea vertical y LiDAR contra metro a 1 y 1.5 m; CSI#2 del plus; altura del mínimo (2.0 m contra 3.30 m); `sistema_minimo.py` en modo sombra;
**el mínimo no ha volado con la Jetson**; solo hubo un vuelo del dron sin ella, que terminó en falla por batería.
