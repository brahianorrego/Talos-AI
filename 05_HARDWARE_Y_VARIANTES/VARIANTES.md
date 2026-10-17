# Variantes de hardware para el plus (cámaras, estabilización, LiDAR)

Sesión Hardware y variantes · 2026-10-17 · solo simulación y diseño. **Nada de esto se construyó ni se probó en el dron.**
Reglas que mandan sobre todo lo de abajo: gimbal −45°..+15° (`pwm = 1500 + θ·500/45`), el mínimo sigue con la
configuración actual (variante A) hasta terminar, y el TF03 y el gimbal no se tocan en el dron hasta entonces.

## 1. En pocas palabras (para Brahian)

- Hoy el gimbal solo baja a −10° porque el cable grueso del TF03 hace palanca. Para el plus se necesita llegar a −45°.
- Hay dos caminos: **liberar el gimbal** (sacar el TF03 del pod y poner un TF-Luna, que es liviano) o **cambiar el
  gimbal por un pan-tilt de 2 servos** impreso en 3D.
- **Mi recomendación para el plus: variante C** (liberar la BaseCam: TF03 al chasis, TF-Luna en el pod, cámara CSI al
  piso). Es lo más barato y no hay que imprimir nada. Si después de quitar el TF03 el pod sigue sin bajar a −45°,
  **pasar a la variante D** (pan-tilt de servos), cuyas piezas ya están diseñadas aquí.
- La simulación puede entrenar con `GIMBAL_TIPO = "mixto"` (BaseCam o servo al azar, ya existe en la V16). Así **el
  mismo entrenamiento sirve para C y para D** y la decisión se toma en el campo, sin reentrenar.
- **No recomiendo** E (pan-tilt sobre la BaseCam) ni F (3 cámaras) para este proyecto: más peso, más cables y más carga
  para poco beneficio (razones en las notas E y F de la sección 4).
- Lo que ya está medido y lo que **no**: ver sección 7 (y sección 2 para lo ya medido). Las piezas 3D no se han compilado ni impreso.

## 2. Qué se sabe (con su fuente)

| Dato | Valor | Fuente |
|---|---|---|
| Peso total en vuelo | 2 371 g (báscula) | `README.md`, tabla de hardware |
| Cámara USB | HFOV 38.9°, VFOV ≈ 29.7°, 640×480 | `hardware.md` |
| YOLO26n TensorRT FP16 | 9–11 ms por cuadro (una cámara) | `hardware.md` |
| CSI IMX219 en CAM0 | funciona por V4L2 (`camara_csi.py`): 29.5 FPS sola, 30.8 con YOLO. HFOV 62.2° **nominal, sin medir** | `_memoria_claude/jetson-conexion_SIN_SECRETOS.md` (2026-10-11) |
| Dos cámaras con YOLO en paralelo | CSI 21.4 FPS y USB 24.2 FPS | mismo archivo |
| Gimbal real | pitch tope ≈ −10°; el cable grueso del TF03 hace palanca (hipótesis de esa sesión; no se ha comprobado quitando el cable) | mismo archivo, 2026-10-11 |
| BaseCam | 8 bits, firmware 2.2b2; pitch por PWM de AUX1; zona muerta puesta en 0; 30°/s | `hardware.md`, `jetson-conexion…` |
| Sensores en la V16 | CAM_PISO IMX219 −90°, TF03 al chasis +1°, TF-Luna en el gimbal, `GIMBAL_TIPO` basecam/servo/mixto | `docs/PLAN_V16_REALISMO.md` §2, §6; `04_VISOR…/v16/docs/PROGRESO_V16.md` |

**Cómo se evitó el problema del CSI** (pantallas verdes y `nvargus-daemon` bloqueado): no se arregló Argus. En JetPack 7
(L4T R39) Argus da "No EGL device available". La solución fue **saltarse Argus**: se lee el sensor crudo (RAW10) por
V4L2 con `v4l2-ctl`, y la conversión de color, el balance de blancos y la exposición se hacen a mano en la CPU
(~12 ms por cuadro). Costo: no hay el procesador de imagen de la Jetson y cada cámara CSI gasta CPU. Pendiente de
verificar en el dron (lo hace la parte física): el archivo de prueba `egl-nvidia.conf` que se pidió borrar, y que
existe un overlay para **dos** IMX219 (hoy solo está aplicado el de CAM0).

## 3. Las variantes

| | Cámaras | Estabilización | LiDAR | Piezas nuevas |
|---|---|---|---|---|
| **A** (actual) | USB en el gimbal | BaseCam 2 ejes (pitch real ≥ −10°) | TF03 en el pod | — |
| **B** | A + **CSI al piso** (CAM0, −90°) | igual | igual | CSI + cable plano 15→22 pines + soporte |
| **C** | B | BaseCam **liberada** | **TF03 fijo al chasis** (−3°, D-064) + **TF-Luna en el pod** | B + TF-Luna + soporte LiDAR |
| **D** | USB en el pan-tilt + CSI piso | **Pan-tilt 2 servos, sin BaseCam**, Pixhawk estabiliza el tilt | TF03 chasis + TF-Luna en el pan-tilt | C + 2 servos MG90D + BEC + piezas impresas |
| **E** | igual que D | **Pan-tilt sobre la BaseCam**: la BaseCam sostiene el horizonte, el servo da el ángulo | igual que D | D, pero conservando la BaseCam |
| **F** | USB en pan-tilt + CSI piso (CAM0) + **CSI frontal ancha fija** (CAM1) | como D | como D + **TF-Luna al piso** (altímetro) | D + 1 CSI + 1 TF-Luna |

Descartada: **G = cámara fija sin estabilizar.** El chasis cabecea al acelerar (≈ atan(a/g)) y el objetivo se sale del
cuadro; la simulación lo modela con el retardo de compensación del gimbal.

### Dónde va cada cosa

- **Cámara USB:** siempre en la parte que gira (pod o pan-tilt), porque su cable es flexible.
- **CSI (IMX219):** **solo fijas al chasis.** El cable plano mide ~15–30 cm, no tolera giros repetidos y cuesta más
  largo (ruido). Al piso: bajo el chasis, centrada. Frontal (F): en el morro, a 0°.
- **Orientación de la cámara al piso:** con el lado largo (62.2°) **a lo largo del vuelo**, el borde delantero de su
  campo, a 3.30 m de altura, llega a 3.30·tan 31.1° = 1.99 m; el borde de abajo de la cámara principal en −45° toca el
  suelo a 3.30/tan 59.9° = 1.91 m. **Empalman** (cálculo mío). Con el lado largo cruzado, el borde llega a 1.50 m y queda
  un hueco de 0.4 m. A la altura de la cabeza (1.8 m más abajo) los bordes están en 1.04 m (principal) y 1.09 m (piso):
  también empalman. Parámetro `CAM_PISO_EJE_LARGO`.
- **TF03:** fijo al chasis, mirando al frente a −3° (D-064; el plan V16 decía +1°), en un soporte en el morro, **fuera del
  barrido de las hélices de 10″**. **TF-Luna:** al lado de la cámara, en el pod o en el pan-tilt (la separación de
  ~3 cm da 0.5° de paralaje a 3.5 m, menor que el haz de 2°).

## 4. Matriz comparativa

Peso: los gramos son **estimaciones** (hoja de datos o de memoria; hay que pesar cada pieza). Los desplazamientos del
centro de gravedad se calculan como ΔCG = m·d / (2 371 + m), con las distancias al CG **supuestas** (cámara/pod
120 mm adelante, cámara al piso 30 mm, TF03 a 150 mm; **medir**). Regla práctica mía: con menos de ~5 mm no hace falta
reequilibrar; la potencia en vuelo estacionario sube como m^1.5.

| | A | B | C | D | E | F |
|---|---|---|---|---|---|---|
| **Viabilidad** | existe | alta | alta si el cable era el culpable | media (impresión, servos, Pixhawk, código Jetson) | media-baja (carga sobre un gimbal chico) | baja-media |
| **Peso añadido (g, estim.)** | 0 | +5 | +13 | +85 y **−BaseCam (pesarla)** | +85 | +98 y −BaseCam |
| **Δ potencia en vuelo** | — | <0.1 % | ~0.8 % | ~5 % menos lo de la BaseCam | ~5 % | ~6 % menos la BaseCam |
| **Δ centro de gravedad** | — | 0.06 mm | ~1.4 mm (TF03 de 120→150 mm + TF-Luna) | ~3.5 mm menos lo que se quite | ~3.5 mm | ~4 mm |
| **Cableado nuevo** | — | flex CSI→CAM0 | + TF-Luna (UART) | + 2 señales a AUX1/AUX2, + BEC | igual que D | + CSI→CAM1, + TF-Luna piso |
| **Alimentación** | actual | CSI: 3.3 V de la Jetson | TF-Luna 5 V (~70 mA según hoja de datos) | **BEC 5–6 V ≥ 3 A solo para servos**, tierra común | igual | igual |
| **Carga de la Jetson** | 1 cámara: ~30 FPS (medido) | 2 cámaras: **USB 24.2 / CSI 21.4 FPS (medido)** | igual a B | igual a B | igual a B | 3 cámaras: **no medido**; si el tope es total (45.6 FPS) → ~15 FPS cada una |
| **Toca el mínimo congelado** | no | no (solo peso) | **sí** (TF03 deja de estar alineado con la cámara a −5°: re-simular `minimo_tesis/`) | sí | sí | sí |
| **Riesgo principal** | no baja a −45° | masa y flex cerca de ESC | que el cable no fuera la causa | sin estabilización inercial, sin compensar alabeo, vibración en la imagen | sobrecargar los motores de la BaseCam | CPU/USB saturados |

### Notas por variante

**B.** Es lo único que no mueve el TF03 ni el gimbal. Aun así cambia el avión: se hace después del mínimo. Cubre el punto ciego
bajo el dron. Blindar el flex del ruido de los variadores (cinta de cobre, alejarlo de cables de potencia).

**C.** Es la prueba más barata de la hipótesis "el cable del TF03 es lo que traba el pitch". Pasos y qué se mide en el
dron: lo ve la parte física. Si baja a −45°, queda el mejor equilibrio costo/estabilización (la BaseCam estabiliza con
motores sin escobillas). El gimbal sigue siendo lento (30°/s en la simulación, `GIMBAL_VEL`). Ojo: con el TF03 fijo al
chasis hay que descartar los impactos al suelo con la actitud de la Pixhawk (d < h/sin(cabeceo hacia abajo) − 0.4 m).

**D.** Ángulos exactos y **topes mecánicos reales** en −45°/+15° (la regla dura 1 queda también en el metal).
- *Servo:* MG90D (≈13 g, ≈2.2 kg·cm, engranes metálicos). Cálculo de par: carga de ~80 g con el CG 15 mm fuera del eje →
  0.12 kg·cm estático, 0.24 con 2 g de vibración, unas 9 veces de margen. El servo plástico SG90 no (se desgasta); los
  de clase 9 kg·cm pesan 55 g y no hacen falta.
- *Pixhawk como estabilizadora (MNT servo):* el tilt va por AUX1 (SERVO9, **la misma ley de PWM de hoy**), el pan por
  AUX2 (SERVO10). Para el tope por software: `SERVO9_MIN = 1000`, `SERVO9_MAX = 1667` (= −45° y +15°). Parámetros de
  montura de ArduPilot 4.7 (`MNT1_TYPE`, `SERVOn_FUNCTION` de tilt/pan, límites): **verificar nombres y valores en la
  documentación y en Mission Planner antes de aplicar; yo no los probé.** Para dejar que la Pixhawk estabilice, la Jetson
  tendría que mandar el ángulo con MAVLink de montura (`DO_MOUNT_CONTROL`) en vez de `DO_SET_SERVO`: **cambio de código
  de la Jetson**.
- *Límites de la estabilización:* la Pixhawk compensa con ~50–100 ms de retraso y ~600°/s (valores de la V16); con solo
  2 servos **no se compensa el alabeo**.
- *Alimentación:* los servos **no** se alimentan del 5 V de la Pixhawk. BEC de 5–6 V y ≥3 A (≈2× el consumo de dos
  servos trabados, ~0.7 A c/u según hoja de datos típica) que acepte 4S (16.8 V), tierra común con la Pixhawk, un
  condensador de 470–1000 µF en el riel y los cables de los servos lejos del flex CSI y del USB.
- *Pan:* ±60° como propuesta (**decisión para el Arquitecto/Brahian**; la regla dura 1 solo cubre el pitch). Para el
  primer entrenamiento el pan queda **bloqueado en 0°** (`PAN_ACTIVO_EN_ENTRENAMIENTO = false`): activarlo agrega una
  acción a la red y obliga a reentrenar. Posible extra: barrer el pan con el TF-Luna da una nube de puntos (1.8° por
  muestra a 100 Hz si el barrido de 180° dura 1 s; sin codificador, el ángulo es el ordenado, no el medido).
- *Topes:* los topes se diseñaron **1° dentro** del rango (−44°..+14°) para que la tolerancia de impresión nunca
  amplíe la regla; el comando por software debe quedar ≤ 1° dentro de eso para que el servo no empuje contra el tope.
  El cuerno de 25 dientes solo se posiciona en pasos de 14.4°: el cero se afina con `SERVO9_TRIM`.

**E.** Es la idea de Brahian de poner el pan-tilt sobre el estabilizador. Ventaja real: la BaseCam solo sostiene el
horizonte (no necesita bajar a −45°) y el servo da el ángulo exacto. Desventaja: +85 g sobre un gimbal chico cuya carga
máxima **no conozco**, más cables cruzando dos etapas móviles y, sin quitar el TF03 del pod, la palanca sigue ahí.
Solo vale la pena si C falla y la estabilización inercial se considera imprescindible.

**F.** Tres cámaras. La tercera (CSI frontal ancha, 62.2°) da vista de piloto/tránsito, pero con la medición de dos
cámaras (45.6 FPS en total) tres bajarían a ~15 FPS cada una. Se podría correr la del piso a 10 FPS, un proceso por
cámara y la CPU como cuello (la GPU gasta ~10 ms por inferencia, ~45 % ocupada a 45 FPS): **todo estimado, no medido**.
Los dos puertos CSI son los únicos de la Jetson (CAM0 y CAM1).

## 5. LiDAR: la recomendación del supervisor (V16 §6) revisada

- **TF03 fijo al chasis, a −3° (D-064; el plan V16 decía +1°):** la **valido**. Es el sensor de frenado y quita la palanca del cable del pod.
  Corrección: es un cambio que **sí obliga a re-simular el mínimo** (el decisor se entrenó con el TF03 alineado a la
  cámara a −5°).
- **TF-Luna en el pod, coaxial con la cámara:** la **valido**. Alcance de hoja de datos (de memoria): ~8 m con blanco
  claro y ~2.5 m con objetivo oscuro, menos a pleno sol. Cubre la zona de peligro (< 3–5 m). Ya está en la V16
  (`LIDAR_LUNA_ALCANCE_M` de 3 a 8 m).
- **Paneles reales de ~2.0 m (plan V17 §3.2 y §7.3): quién los mapea, C contra D.** El TF03 horizontal a 3.30 m pasa
  1.3 m por encima, y a 2.0 m de altura (la mínima permitida) apunta al borde de arriba del panel (con +1° sube 17 cm
  a 10 m): **en C y en D el TF03 no mapea paneles de 2.0 m a las alturas permitidas.** Los mapea el TF-Luna del pod, y
  solo si el pod está inclinado hacia abajo. Cálculo mío desde 3.30 m (rayo del Luna a −θ; el panel va de z = 0 a 2.0 m):

  | Pod | Distancia horizontal al panel | Distancia medida por el Luna (cara del panel) | Retorno del suelo |
  |---|---|---|---|
  | −15° | 4.9–12.3 m | 5.0–12.8 m: solo el tercio de arriba (z ≥ 1.2 m) entra en 8 m | 12.8 m: fuera de alcance |
  | −30° | 2.3–5.7 m | 2.6–6.6 m: **todo entra en 8 m** | 6.6 m |
  | −45° | 1.3–3.3 m | 1.8–4.7 m: entra; con objetivo oscuro (2.5 m) solo los 2.5 primeros | 4.7 m: hay que descartarlo con la altura y la actitud |

  Conclusión: con alcance de 8 m (blanco claro) el Luna ve paneles a **menos de ~6 m en horizontal** con el pod a −30°/−45°;
  más lejos, o con un panel oscuro/a pleno sol (≈2.5 m de hoja de datos), no. El color de los paneles reales no consta
  en mis archivos: **verificarlo** (la foto de referencia es privada). La simulación debería usar el alcance del Luna
  por partida de 3 a 8 m como ya hace la V16 y **no** más.
  - **C (BaseCam):** el pitch es lento (30°/s) y es el de la cámara, que lo decide quien sigue al ladrón; el Luna mapea
    paneles solo cuando la cámara apunta abajo y a su ritmo. A cambio, el ángulo está estabilizado por la BaseCam y el
    descarte del suelo es confiable.
  - **D (servos):** el pitch llega a ~600°/s y se podría hacer un barrido rápido de pitch (y de pan, ±60°) para
    mapear paneles sin mover la cámara de su objetivo... pero la cámara y el Luna comparten montura: mientras barre, la
    cámara no mira al objetivo. El ángulo es el ordenado (no medido), con ~50–100 ms de retraso y 1° de zona muerta
    (≈9 cm a 5 m), y sin compensar el alabeo: un alabeo de 5° tuerce el abanico del barrido.
  - **Opción barata para el 360° de entrada a 2.0–2.5 m:** montar el TF03 a −3° (`cabeceo_deg = -3` en
    `soporte_lidar.scad`): a 2.5 m el rayo baja de 2.0 m a ~9.5 m, como estima el plan; contra el suelo no hay problema
    (devuelve algo a más de 30 m). A 3.30 m no ayuda (llega a 2.0 m recién a ~25 m). Cambia otro número que el decisor
    del mínimo no conoce: re-simular el mínimo.
- **TF-Luna al piso como altímetro (F):** viable, pero **dos reservas**: sobre pasto el retorno es ruidoso y a pleno sol
  pierde alcance. Mejor conectarlo a la Pixhawk como telémetro (llega a la Jetson por MAVLink como
  `DISTANCE_SENSOR`) que a la Jetson. Confirmar qué puerto serie de la Pixhawk está libre (¿TELEM1?) y el valor de
  `RNGFND1_TYPE` para Benewake en 4.7.
- **Cómo conectar el TF-Luna del pod:** USB-TTL a la Jetson (como el TF03). Ojo: el PL2303 ya exigió **compilar un
  driver**; el CP2102/CH340 podría exigir lo mismo. Plan B: a la Pixhawk.

## 6. Qué cambia en la simulación

Archivos en `config_sim/variante_A.json` … `variante_F.json` (mismas claves en todos). `python validar_variantes.py`
comprueba la regla dura 1 (rango, PWM 1000–1667 µs, topes), cámara al piso a −90°, TF03 al chasis ±5°, claves iguales.
Pasa en los seis.

| Clave | Ya existe en la V16 | Nota |
|---|---|---|
| `GIMBAL_TIPO`, `CAM_PISO_HFOV/VFOV/PITCH` | sí | valores nuevos de `GIMBAL_TIPO`: `"servo_sobre_basecam"` (E) |
| `GIMBAL_TOPE_FISICO_MIN` | no | A y B = −10° (reproduce el campo de hoy); el resto −45° |
| `GIMBAL_VEL_DPS`, `GIMBAL_RETARDO_S`, `GIMBAL_ZONA_MUERTA_DEG` | casi (V16: 600°/s, 50–100 ms, 1°) | BaseCam 30°/s |
| `PAN_*` | no | acción nueva solo si se activa |
| `CAM_PISO_EJE_LARGO`, `CAM_FRONTAL_ANCHA_*`, `YOLO_FPS_*` | no | solo F usa la frontal |
| `LIDAR_TF03_*`, `LIDAR_LUNA_*` | sí, con otros nombres | **proponer a la sesión Simulación V17 el mapeo**; no vi el `entorno.py` de la V16 |

**Entrenamiento sugerido:** cámara al piso activa, LiDAR como en C, `GIMBAL_TIPO = "mixto"`. Cubre C y D. E equivale a
un servo rápido sin tope de cable; F pide una cámara más y el pan.

## 7. Piezas 3D (`piezas_3d/`)

| Archivo | Qué es | Notas |
|---|---|---|
| `pan_tilt_servos.scad` | Base (placa con ranuras M3 + soporte del servo de pan), plataforma con mejillas (servo de tilt) y cuna con **pin y ranura de arco que hacen el tope** en −44°/+14° | Parámetro `parte`; `angulo_vista` para ver el pin en cada tope. Cuna de 56 mm de ancho: TF-Luna + cámara CSI lado a lado. Alto ≈ 6.5 cm, ancho ≈ 7 cm |
| `soporte_camara.scad` | Placa con 4 separadores para IMX219 o una USB; modo `frente` (cuadrícula M2 de 10 mm de la cuna) y modo `abajo` (cámara al piso bajo el chasis) | Las medidas de la IMX219 son de un plano recordado |
| `soporte_lidar.scad` | Cuna abierta con ranuras para amarras: TF-Luna (35×18×21) o TF03; `cuadricula` o `chasis` con cuña de `cabeceo_deg` | Las medidas del TF03 son **provisionales** |

Impresión sugerida: PETG, 0.2 mm de capa, 3 perímetros, 30–40 % de relleno. Peso estimado del pan-tilt impreso: ~35 g
(el *slicer* da el número real). Montar sobre silicona o arandelas blandas contra la vibración.

### Qué no se puede verificar sin la pieza (ni sin OpenSCAD)

1. **Los `.scad` ya compilan** (OpenSCAD 2021.01, sin errores; STL en `piezas_3d/stl/`; los topes se comprobaron por intersección en el modelo, ver `piezas_3d/ESTADO_IMPRESION.md`). **Ninguna pieza se ha impreso.**
2. **Medidas del servo MG90D, su cuerno y los separadores:** de hoja de datos/memoria. Con calibrador en mano.
3. **Medidas de la IMX219 de la Jetson (clones distintos), de la cámara USB y del TF03:** provisionales.
4. **Agujeros del chasis** (ranuras M3 genéricas) y el espacio libre respecto a las hélices: no conozco la geometría.
5. **Precisión de los topes** (la tolerancia de impresión ~0.2 mm en R = 16 mm son ~0.7°; por eso el margen de 1°), la
   rigidez de las mejillas altas y la vibración: solo se ven al montar.
6. **El par real, el recorrido real del servo (1000–2000 µs ≈ 90°?)** y el consumo: medir.
7. **Que la BaseCam baje a −45° sin el cable del TF03** (C) y la carga que aguanta (E).
8. **Parámetros de ArduPilot 4.7 para montura y telémetro, y los FPS con 3 cámaras.**
9. Cualquier cifra de peso marcada como estimación.

## 8. Decisiones

**Aprobadas por Brahian (2026-10-17):**

- **D-055:** C primero, D como plan B, y se entrena con `GIMBAL_TIPO = "mixto"`.
- **D-056:** el pan queda **bloqueado** en la V17 (`PAN_ACTIVO_EN_ENTRENAMIENTO = false`); ±60° es solo un parámetro, no una regla dura, hasta que se construya D con topes mecánicos.

**Siguen abiertas:**

1. Pedir a la parte física (cuando termine el mínimo): pesar BaseCam, TF03 y cámara USB; medir si el pod baja a −45° sin el TF03; confirmar el overlay de dos IMX219 y el puerto libre de la Pixhawk. Quedó en `docs/PEDIDOS_A_LA_PARTE_FISICA.md`.
2. ¿Se compra o imprime D por adelantado como plan B? (costo bajo, decisión de Brahian).
3. Color real de los paneles (alcance del TF-Luna, §5).
4. El mapeo de los nombres `LIDAR_*` lo hace la sesión Simulación V17 al traer el código de la V16.
