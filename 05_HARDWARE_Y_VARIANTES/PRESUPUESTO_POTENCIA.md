# Presupuesto de potencia y carga de la Jetson por variante

Escrito el 2026-10-19. **Nadie ha medido consumos en el dron:** los vatios son estimaciones de hoja de datos (de memoria) o mías, marcadas
"est.". Lo medido está marcado "medido" con su fuente. La conclusión no depende de los decimales: lo que se añade es pequeño frente a la
batería y a los motores; lo que importa es el peso (ver `VARIANTES.md` §4.1).

## Punto de partida

- Batería LiPo 4S de 6 200 mAh (≈ 92 Wh nominales), Power Module PM05 y un buck a 12.02 V para la Jetson (`README.md`, tabla de hardware).
- Jetson Orin Nano: modos de 7 W y de 15 W según NVIDIA (de memoria). Para el peor caso se cuenta **15 W**.
- La cámara USB gasta del orden de 1 W (est.; el puerto USB da hasta 2.5 W).

## Consumo de lo que se añade (est.)

| Elemento | Típico | Pico | Nota |
|---|---|---|---|
| Cámara CSI IMX219 | 0.8 W | 1 W | la alimenta la propia Jetson por el conector (3.3 V); est. |
| TF-Luna | 0.35 W | 0.4 W | 5 V, ≲ 70 mA según la hoja de datos (de memoria) |
| Servo MG90D (cada uno) | 0.3 W | 3.5 W | 4.8–6 V; ~0.7 A trabado (est.). El pico solo si el tope lo traba |
| BEC 5–6 V (pérdida) | 15 % de lo que alimenta | — | eficiencia ~85 % (est.); acepta 4S |
| TF03 | ≈ 1.5 W | — | ya está; se mueve de sitio, no suma |

## Por variante (diferencia contra A, en vatios desde la batería)

| | Qué se añade | Típico | Pico (peor caso) |
|---|---|---|---|
| A | — | 0 | 0 |
| B | 1 CSI | +0.8 | +1 |
| C | 1 CSI + TF-Luna | +1.2 | +1.4 |
| D | 1 CSI + TF-Luna + 2 servos + BEC, **− BaseCam (sin dato)** | +1.9 − BaseCam | +9.5 − BaseCam |
| E | igual que D, con la BaseCam puesta | +1.9 | +9.5 |
| F | D + 1 CSI + 2.º TF-Luna | +3.1 − BaseCam | +10.9 − BaseCam |

Pico de D: 2 servos trabados (7 W) + CSI + Luna (1.4 W) con pérdida del BEC ≈ 9.5 W. **Contra los cientos de vatios que gastan los
motores, es menos del 2 %**: la autonomía casi no cambia por electricidad; sí por el peso añadido (D: ≈ 8 % más de potencia, `VARIANTES.md` §4.1).

## Alimentación de los servos (variantes D, E, F)

- **BEC de 5 a 6 V y 3 A o más**, que acepte batería 4S (16.8 V): trabados, dos servos piden ≈ 1.4 A (est.), así que 3 A da ≈ 2× de margen.
- Tierra común con la Pixhawk; señal por AUX1 (tilt) y AUX2 (pan, bloqueado en la V17). **Nunca** alimentar los servos del 5 V de la Pixhawk
  ni del de la Jetson.
- Condensador de 470–1000 µF en el riel de los servos; cables de servo lejos del flex de las cámaras CSI y del cable USB.

## Carga de la Jetson (cuadros por segundo)

- Medido: **1 cámara** con YOLO26n TensorRT FP16, 9–11 ms por inferencia (`hardware.md`); 29.6–30.8 FPS en el registro de 10 min.
- Medido: **2 cámaras** con YOLO en paralelo, CSI 21.4 y USB 24.2 FPS (`_memoria_claude/jetson-conexion_SIN_SECRETOS.md`) = **45.6 inferencias/s**.
- Estimado: la GPU aguanta ≈ 90–110 inferencias/s (1 / 10 ms), así que con 45.6/s está a menos de la mitad. **El cuello es la CPU**: el
  procesamiento de cada cámara CSI sin Argus cuesta ≈ 12 ms por cuadro (~25 % de un núcleo a 21 FPS) más el hilo de Python.

| Variante | Cámaras | FPS con YOLO | Fuente |
|---|---|---|---|
| A | 1 (USB) | ≈ 30 | medido |
| B, C, D, E | USB + 1 CSI | USB 24.2 / CSI 21.4 | medido |
| F | USB + 2 CSI | ≈ 15 cada una si el tope total (45.6/s) se reparte; **si la del piso va a 10 FPS, la principal llega a ≈ 20–24** | **estimado, no medido** |

Para F habría que medir antes de decidir, y en ese caso: un proceso por cámara (para no depender del GIL de Python), la cámara del piso
a 10 FPS (solo sirve para el punto ciego) y el overlay de dos IMX219 (`IMX219 dual`; hoy solo está aplicado el de CAM0).


## Actualización 2026-10-20: variante H con pan y cabeceo activos (D-056 revocada)

**Potencia.** Con los dos servos moviéndose de verdad (seguimiento activo: ≈ 0.2 A cada uno a 5 V, ≈ 1 W cada uno; est.), el consumo típico de H sobre G sube a **≈ +3.5 W**
(CSI#2 0.8 + TF-Luna 0.35 + 2 servos 2.0 + pérdida del BEC 0.3) y el **pico a ≈ +9.5 W** (servos trabados). Sigue siendo **menos del 2 %** de lo que gastan los motores. El **BEC de 5–6 V y ≥ 3 A** de siempre aguanta:
trabados, dos servos piden ≈ 1.4 A (est.).

**Par de los servos (MG90D ≈ 2.2 kg·cm a 6 V, hoja de datos; de memoria).** Con la CSI#1 (3 g), el TF-Luna (8 g), la cuna (10 g) y el cable (5 g):

| Eje | Carga | Par estático | Con 2 g de vibración | Margen |
|---|---|---|---|---|
| **Tilt** | momento de ≈ 52 g·cm alrededor del eje (cargas a 1–3 cm) | ≈ 0.05 kg·cm | ≈ 0.15 kg·cm | más de 14× |
| **Pan** | inercia ≈ 2.3·10⁻⁵ kg·m² (plataforma 22 g, servo de tilt 13 g, cuna y carga 26 g a ≈ 2 cm) a 3 000 °/s² | ≈ 0.012 kg·cm | — | más de 100× |

El par sobra. **Lo que sí preocupa es el eje del servo de pan:** carga ≈ 100 g **en vertical** y el momento lateral del tilt; el eje del MG90D no está hecho para cargas laterales y la vibración lo desgasta. Mitigación: el pan-tilt va atornillado a la placa por una base ancha (64 × 56 mm), el centro de gravedad cerca del eje, y revisar el juego del eje tras las primeras pruebas.

**Velocidad.** MG90D ≈ 0.1 s por 60° sin carga (≈ 600 °/s). Con esta carga ligera se espera cerca de ese valor; `PAN_VEL_DPS = 600` y `GIMBAL_VEL_DPS = 600` en `variante_H.json` son los de `control.GimbalMixto.SERVO_VEL`, **sin medir con la carga**.

**Jetson (H).** Dos CSI con YOLO: **≈ 20 FPS la principal y ≈ 10 la del piso (ESTIMADO, no medido)**; el giro del pan no añade carga de cómputo (solo una orden de servo).
