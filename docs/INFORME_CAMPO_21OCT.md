# Informe de las pruebas de campo del 21-oct-2026 (paso 4 del mínimo)

Parqueadero del conjunto, **dron sin hélices, quieto, sobre el techo de un carro**, mirando por un pasillo de ~4.5-5 m de ancho. Brahian caminaba; Tatiana operaba.
Datos: `datos_campo/campo_2026-10-21/` (`datos.csv` y `tomas.csv` de cada sesión; los videos están en `privado_videos/`, con placas y personas: no se publican).
Herramientas del análisis: `02_JETSON_MINIMO/herramientas/analizar_campo.py` y `geometria_desde_campo.py`. Tablas completas: `analisis_tomas.md`, `geometria_desde_campo.md`, `resumen_E1_por_marca.md`.

## 1. Qué quedó grabado en la Jetson

| Carpeta (reloj de la Jetson) | Qué contiene | Duración real | Se usa |
|---|---|---|---|
| `20261021_172815` | Pruebas en la casa antes de salir (sin tomas), cabeceo 0.7° | ~21 min | No |
| `20261021_184014` | **Campo, sesión 1**: E2 ×6, E3 ×5, E1 R12 (cortada por el apagón) | ~15 min de datos | Sí |
| `19691231_190059` | **Campo, sesión 2** (el nombre dice 1969: el reloj arrancó sin hora): E1 ×5 completas, E4 ×7, y un fragmento sin valor (ver §5) | ~17 min de datos | Sí |
| `20261021_201113` | De vuelta en la casa, sin Pixhawk y sin tomas | ~2 h | No |
| Otras (`1969...`, `1724xx...`) | Arranques cortos y pruebas de hoy en la casa | — | No |

Sin batería de la Pixhawk **nunca se armó**; el voltaje fue de 16.1 V a 15.8 V en la sesión 1 y de 15.9 V a 15.75 V en la 2. GPS: 20-22 satélites, HDOP 0.7. Cámara y YOLO: 30 fps, YOLO ~23 ms (mediana), p95 27 ms. Temperatura de la Jetson normal.
Los dos videos (`video.avi`, 960×720) están completos: 31 373 y 27 648 cuadros, uno por fila del CSV. **Ojo:** el encabezado del AVI dice 12 732 cuadros porque el apagón impidió cerrarlo; hay que leerlo seguido (no saltar a un cuadro) o repararlo con `ffmpeg -i entrada.avi -c copy salida.avi`.

## 2. Tomas hechas contra lo que se quería (meta corta / completa)

| Escenario | Hechas y válidas | Meta | Falta |
|---|---|---|---|
| E0 · nadie delante | 0 | 2 / 3 | **todas** |
| E1 · quieta en cada marca | 5 completas (R1-R5) | 1 / 3 | — |
| E2 · camina 15 → 3 m | 6 (R1 sin altura del lente escrita) | 5 / 10 | 4 para la completa |
| E3 · trota 15 → 4 m | 5 | 5 / 10 | 5 para la completa |
| E4 · cruza (solo **caminando**) | 12 m ×2, 8 m ×2, 5 m ×3 | 6 / 30 | **trotando**, y las demás repeticiones |
| E5 · silla | 0 | 2 / 5 | todas |
| E6 · cartón | 0 | 2 / 5 | todas |

## 3. Resultados

**LiDAR contra la cinta (E1, persona quieta en cada marca, 5 repeticiones):** el rayo, cuando le pega a la persona, mide dentro de **+0.02 a +0.08 m** de la marca entre 4 y 15 m, y +0.16 m a 2 m (la persona queda un poco delante de la cinta, y el LiDAR mide hasta su cuerpo). Esto es la comprobación que faltaba del LiDAR contra el metro.

| Marca (m) | Persona detectada por YOLO | Confianza mediana | LiDAR en la persona (mediana, m) | Error (m) |
|---:|---:|---:|---:|---:|
| 15 | 82 % | 0.53 | 15.02 | +0.02 |
| 12 | 94 % | 0.57 | 12.02 | +0.02 |
| 10 | 96 % | 0.59 | 10.08 | +0.08 |
| 8 | 99 % | 0.69 | 8.07 | +0.07 |
| 6 | 99 % | 0.78 | 6.07 | +0.07 |
| 4 | 100 % | 0.86 | 4.05 | +0.05 |
| 2 | 99 % | 0.82 | 2.16 | +0.16 |

**Rayo dentro de la caja de la persona** (el LiDAR "ve" a la persona que YOLO ve): 75-100 % en E1 (a 15 m, 75 % con el punto fijo y 85 % corrigiendo por distancia), ~80 % caminando o trotando hacia el dron (E2, E3), **~9 % al cruzar de lado (E4)**, que es lo esperable: el rayo solo roza a la persona un instante.
**E2 y E3:** la persona se detectó en ~88 % y ~93 % de los cuadros; la lectura mínima del LiDAR fue ≈ 2.9-3.0 m (E2) y ≈ 3.9-5.2 m (E3), es decir, se pararon donde debían. **E4:** el LiDAR leyó la persona al cruzar a 4.8-4.9 m, 7.9 m y 11.8 m, o sea, 0.1-0.2 m antes de las líneas de 5, 8 y 12 m.
**Detección a distancia:** 82 % de los cuadros a 15 m, 94 % a 12 m, ≥ 96 % a 10 m o menos. A 12 m en E4 (persona de lado) baja a 64-71 %.

## 4. La inclinación del dron y la geometría real

**Lo que midió la Pixhawk durante las tomas:** cabeceo **+3.9° (sesión 1) y +4.2° (sesión 2)** (nariz arriba), alabeo **−2.2° y −2.5°** (el lado izquierdo más abajo). Es decir, el dron no estaba plano: Brahian lo calzó por atrás para que el rayo no tocara el suelo tan cerca.

**Por qué hizo falta calzarlo.** Con el eje del LiDAR a 1.83 m del suelo (el lente a 1.87-1.88 m, medido con metro y con el iPhone):
- Con el dron plano, el rayo tocaba el suelo a ~12 m (lo que viste). Eso da −atan(1.83 / 12) = **−8.7°** respecto al chasis.
- Con cabeceo +4.2° el suelo quedó a ~22.4 m: ángulo del rayo −4.67° sobre el horizonte, es decir **−8.9° respecto al chasis**. Con +4.5° → 21.9 m (−9.3°) y con +5.5° → 29.8 m (−9.0°). Tres cabeceos distintos dan el mismo ángulo del montaje: **LiDAR ≈ −9.0° ± 0.3° respecto al chasis**. A 15 m el rayo iba a unos 0.6 m del suelo (rodillas), y por eso le pegaba a la persona.
- **La cámara:** con los pies de la persona en la imagen (11 204 cuadros con el rayo dentro de la persona, 6-15 m) sale **−1.4° respecto al horizonte** y **−5.6° respecto al chasis**. A menos de 4.5 m no sirve: la parte baja de la imagen (~11 %) está tapada por el techo del carro, así que los pies no se ven y la caja se corta en y ≈ 0.89.
- La diferencia cámara-LiDAR sale −3.4° (en el escritorio dio −4.3°): coincide dentro de la incertidumbre.

**Qué significa.** En el escritorio se midió −2.4° (cámara) y −6.7° (LiDAR) **respecto al horizonte**, pero el dron debía de estar cabeceando unos +2.5° a +3° (se deduce de estos datos; el cabeceo no se registró en ese momento) y esos valores se tomaron como si fueran respecto al chasis. Los valores respecto al chasis son los que usa la simulación y no cambian cuando el dron se inclina: **cámara −5.6° y LiDAR −9.0°** (provisional). Eso cambia la simulación del mínimo (la regla de 17 m al suelo con el dron a 2 m pasaría a ~12.6 m con el dron plano); hay que **recalibrar con el montaje definitivo y re-simular** (ver `docs/DECISIONES.md`, D-082).

Límites de estas cifras: la altura se midió con metro (±2 cm); el suelo se supuso plano; el rayo apuntó a 12-22 m sobre adoquín con carros alrededor; la cámara se calculó con la persona real (talla ≈ 1.7 m, ±5 cm) y el campo de visión de 54°; la cámara tiene un alabeo sin corregir (el dron estaba inclinado −2.4° de lado).

## 5. Problemas de los datos (qué descartar o corregir)

1. **`E1-4A-R12` (sesión 1 cortada y fragmento de la sesión 2): descartar.** Tras cada apagón el archivo de control de tomas seguía en el disco y la siguiente corrida etiquetó ~2 min de cuadros como si hubiera una toma E1 a 4 m. Corregido: el servicio borra ese archivo al arrancar.
2. **Altura del lente en 0.0:** E2-R1 y E1-R1 a R4. Valen 1.88 m (era la misma). Corregir a mano al analizar.
3. **`E4-4A-12-R6` aparece dos veces:** el primer intento de 7 s se canceló y el segundo (15 s) es el bueno. Dividir por tiempo.
4. **El reloj de la Jetson arrancó sin hora** y saltó al sincronizar (un salto de ~36 min en la sesión 1 y de 56 años en la 2). Dentro de una sesión se alinea por `n` y `toma_id`; para la hora real usar `t_gps`.
5. **El apagón dejó el video sin cerrar** (ver §1).
6. **No se escribió la altura en las primeras repeticiones** porque el campo se llenaba a mano: queda anotada la regla "poner 1.88 antes de la primera toma".

## 6. ¿Alcanza o hay que repetir?

**Alcanza, como primera validación, para:** E1 (detección y LiDAR contra la cinta), E2 y E3 (aproximación caminando y trotando), E4 caminando. Ya sabemos que **el LiDAR coincide con la cinta, que YOLO detecta ≥ 94 % hasta 12 m y 82 % a 15 m, y que el rayo y la cámara ven a la misma persona ~80-100 % de las veces**.
**Hay que repetir o completar:** E0 (falsas alarmas, no se hizo), E4 trotando, E5 y E6, y repeticiones de E2/E3 para llegar a la meta completa.
**Y conviene repetir las tomas con el montaje definitivo**: el de hoy tenía el dron inclinado +4° y de lado −2.4°, distinto de lo que será el vuelo (chasis ~plano). Estas tomas se quedan como "montaje A, dron inclinado". La repetición de mañana, tras recalibrar con la Pixhawk, es la que debe compararse con la simulación.

## 7. Qué se cambió en el sistema por esto

- `config.py` (Jetson y repositorio): `CAMARA_PITCH_DEG = −5.6` y `LIDAR_PITCH_DEG = −9.0`, ahora **respecto al chasis** (respaldo `config.py.antes_calibracion_campo`). La estación y el horizonte dibujado usan el cabeceo de la Pixhawk más estos valores.
- Punto del LiDAR en la imagen **según la distancia** (`geometria_lidar.py`): el rayo cae más arriba cuanto más lejos mide; ya no es un punto fijo (la cruz del video y `lidar_en_caja`).
- `/calibrar` ahora lee la inclinación del dron (Pixhawk), guarda los ángulos respecto al chasis y tiene los pasos 5 (cámara con una persona) y 6 (LiDAR contra el suelo), que se pueden hacer en el parqueadero.
- El servicio borra el archivo de control de tomas al arrancar.
