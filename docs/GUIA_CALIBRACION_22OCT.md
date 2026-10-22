# Calibración del montaje · jueves 22-oct

Para recalibrar **después de mover la cámara o el LiDAR** (otro ángulo u otra posición). Sirve en la habitación y en el parqueadero.

## Lo que cambió desde el 20-oct (importante)
Los ángulos de la calibración del escritorio estaban medidos **respecto al horizonte**, pero la simulación los necesita **respecto al chasis del dron**. El 21-oct se vio que la diferencia era de ~2.5-3° (el dron en el escritorio no estaba plano). Ahora `/calibrar` lee la inclinación de la **Pixhawk** y guarda las dos versiones: por eso **hay que tener la batería del dron conectada** (la Pixhawk encendida) cuando se calibra.
Valores provisionales sacados del parqueadero: **cámara −5.6°, LiDAR −9.0° respecto al chasis** (antes −2.4° y −6.7°, que eran respecto al horizonte).

## Qué ángulo darle al LiDAR (decisión de Brahian)
El rayo toca el suelo a `altura del eje ÷ tan(ángulo)`. Con el eje a ~1.83 m y el dron **plano**:

| Ángulo del rayo (respecto al chasis) | Suelo a |
|---:|---:|
| −5° | 20.9 m |
| −6° | 17.4 m |
| −7° | 14.9 m |
| −9° (como estaba) | 11.6 m |

Para que el rayo siga sobre el piso más allá de los 15 m de las pruebas, conviene **−5° a −6°** (levantar la punta del LiDAR ~3° con una cuña). Con −9° el dron plano ve el suelo a ~12 m y hay que calzarlo hacia arriba (como hoy). En vuelo, al avanzar la nariz baja unos grados y el suelo se acerca; la simulación ya lo modela.

## Qué recalibrar según lo que muevas
| Qué cambió | Qué hacer |
|---|---|
| Solo el ángulo del LiDAR | Paso 6 (suelo) y paso 3 (punto del LiDAR en la imagen) |
| El ángulo de la cámara | Paso 5 (persona) o paso 2 (marcas) y luego paso 3 |
| La posición de la cámara o del LiDAR | Medir de nuevo "eje de la cámara", "eje del LiDAR" y "cuántos cm detrás del frente" y repetir el paso 3 |
| Nada de lo anterior, solo el roll | Paso 4 (línea vertical) |
El **campo de visión (68.3° × 54°) no cambia** si no se cambia el lente: no hace falta repetir el paso 1.

## En la habitación (más preciso, ~10 min)
1. Conectar la **batería del dron** (Pixhawk encendida) y esperar el aviso "Inclinación del dron" con números (no "sin Pixhawk").
2. Abrir la **estación** (`ABRIR_ESTACION_MINIMO.bat`) y tocar **Calibrar montaje** (arriba a la derecha): la calibración se abre dentro de la misma estación (y **Alinear LiDAR** para el punto con un cartón). Respaldo, sin la estación: `http://talos-jetson.local:8080/calibrar`.
3. Escribir las medidas del dron (altura de la superficie, eje de la cámara y del LiDAR sobre ella, cm detrás del frente del LiDAR).
4. Con el dron **quieto**: paso 2 (dos marcas en la pared medidas desde el suelo), paso 3 (dedo a 1, 1.5 o 2 m delante del LiDAR; clic cuando el número se ponga verde), paso 4 si hay una línea vertical.
5. Mirar el cuadro "Respecto al chasis": ese es el que se guarda. **Guardar calibración.**

## En el parqueadero (con el dron ya montado, ~10 min)
1. Batería conectada, dron quieto. Medir con el metro la **altura del lente** y la del **eje del LiDAR** (el lente queda ~5 cm más arriba).
2. **Paso 6 · LiDAR contra el suelo:** sin nadie delante, escribir la altura del eje y "Medir el suelo 3 s". Si la lectura varía más de 1 m, hay un carro o un bordillo en el camino: mover el dron o esperar.
3. **Paso 5 · Cámara con una persona:** una persona entera (con los pies visibles) sobre una marca medida con cinta desde el frente del LiDAR, a 8 m; escribir la altura del lente y la distancia; "Medir 3 s". Repetir a 12 m y comparar (deben dar lo mismo ±0.3°).
4. **Paso 3 · Punto del LiDAR:** con un cartón o la mano a 2-3 m delante del LiDAR (el número verde) hacer 3 o más clics en el punto donde cae el rayo.
5. **Guardar calibración.**

Precisión esperada: ±0.3° a 0.5° en cualquiera de los dos lugares. En el parqueadero la limitan la altura (±2 cm), el suelo (que sea plano) y la talla de la persona; en la habitación, el ancho de los clics sobre marcas de 3 píxeles (use la lupa).

## Después de guardar
- La estación y el horizonte dibujado usan los nuevos valores solos (se leen cada 3 s).
- Los números de `config.py` (`CAMARA_PITCH_DEG`, `LIDAR_PITCH_DEG`) quedan como respaldo; Claude los actualiza con lo que se guardó y re-simula el mínimo con esa geometría.
- Después de calibrar: **repetir las tomas** (E0, E2, E3, E4 caminando y trotando, E5, E6) con el montaje definitivo, con la altura del lente escrita **antes** de la primera toma.
