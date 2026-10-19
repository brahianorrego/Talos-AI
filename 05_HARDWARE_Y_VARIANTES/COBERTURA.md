# Cobertura de las cámaras por variante

Análisis **geométrico** (sin simulación): qué ve cada variante a 3.30 m de altura, dónde queda ciega y qué pasa al mirar detrás de un panel de
2.25 m. Se regenera con `03_SIMULACION_RL\.venv\Scripts\python.exe analisis_cobertura.py` (lee los `config_sim/variante_*.json`). El campo
del IMX219 (62.2° × 48.8°) es **nominal, sin medir**; las alturas de cabeza (1.62 m) y torso (1.25 m) de una persona de 1.72 m son **estimadas**.

## Lo que dice, en sencillo

1. **Hoy (A) hay un anillo ciego enorme:** con el gimbal que solo baja a −10°, la cámara principal no ve la cabeza de una persona a menos de ~3.6 m
   ni el suelo a menos de ~7 m. Una persona que se acerca al dron desaparece mucho antes de llegar.
2. **B (cámara al piso) tapa lo de justo debajo** (la cabeza hasta ~1 m, el torso hasta ~1.2 m), pero queda un **hueco entre 1 y 3.6 m**.
3. **C, D y E (gimbal que baja a −45° + cámara al piso) lo cierran:** con el gimbal libre la cabeza se ve desde 0 hasta más de 15 m, sin
   hueco. Con el pitch fijo en −45° solo se ve de 0 a 2.9 m: el seguimiento tiene que ir subiendo y bajando el pitch (para eso es el gimbal).
4. **F (tercera cámara frontal ancha) no agrega cobertura que C no tenga** en este plano vertical: confirma que no hace falta.
5. **Detrás del panel (2.25 m) desde 3.30 m:** una persona de pie queda oculta de 2.4 a 3.0 m detrás (paneles a 4 y 5 m); agachada, de
   4.4 a 5.5 m; gateando, de 6.3 a 7.9 m. Para verla hay que acercarse o subir: ninguna variante de cámaras lo cambia, depende de la
   maniobra del dron (ruta de búsqueda).

Las figuras (`cobertura/cobertura_variante_A.png` … `_F.png`) muestran los conos de cada cámara, personas de pie cada 2 m, el panel a 4.5 m y,
abajo, tiras verdes de dónde se ve cabeza y torso.

Supuestos: dron a **3.3 m**; persona de pie de **1.72 m** (cabeza = centro a 1.62 m y torso = centro a 1.25 m: **estimados**); cámaras en el centro del dron; pitch táctico −45° donde el gimbal lo permite (A y B: −10°, el tope real de hoy); solo plano vertical (se ignora que el objetivo esté fuera del campo horizontal). Campos: USB HFOV 38.9° × VFOV 29.7° (medido); IMX219 62.2° × 48.8° (**nominal, sin medir**), con su lado largo a lo largo del vuelo.

## Tabla de cobertura vertical (distancias horizontales a las que alguna cámara ve el punto)

«Pitch fijo» = la cámara principal quieta en su pitch táctico. «Gimbal libre» = la cámara principal puede tomar cualquier pitch entre su tope bajo y +15° (lo que hace el seguimiento). La diferencia más importante entre variantes es **la distancia mínima**: con el tope bajo, A/B no ven la cabeza a menos de ~3.6 m y C-F sí desde ~1 m.

| Var. | Cámaras | Cabeza: pitch fijo | Cabeza: gimbal libre | Torso: gimbal libre | Suelo: ciego hasta |
|---|---|---|---|---|---|
| **A** | Principal USB (-10°) | 3.6–más de 15 m | 3.6–más de 15 m | 4.4–más de 15 m | 7.1 m |
| **B** | Principal USB (-10°) + Piso CSI (-90°) | 0.0–1.0 m; 3.6–más de 15 m | 0.0–1.0 m; 3.6–más de 15 m | 0.0–1.2 m; 4.4–más de 15 m | 0.0 m |
| **C** | Principal USB (-45°) + Piso CSI (-90°) | 0.0–2.9 m | 0.0–más de 15 m | 0.0–más de 15 m | 0.0 m |
| **D** | Principal USB (-45°) + Piso CSI (-90°) | 0.0–2.9 m | 0.0–más de 15 m | 0.0–más de 15 m | 0.0 m |
| **E** | Principal USB (-45°) + Piso CSI (-90°) | 0.0–2.9 m | 0.0–más de 15 m | 0.0–más de 15 m | 0.0 m |
| **F** | Principal USB (-45°) + Piso CSI (-90°) + Frontal ancha CSI (0°) | 0.0–2.9 m; 3.7–más de 15 m | 0.0–más de 15 m | 0.0–más de 15 m | 0.0 m |

## Cámara al piso: huella a 3.30 m

- A la altura del suelo: ±1.99 m a lo largo del vuelo y ±1.50 m de lado (huella 3.98 × 2.99 m).
- A la altura del cabeza: ±1.01 m a lo largo del vuelo y ±0.76 m de lado (huella 2.03 × 1.52 m).
- A la altura del torso: ±1.24 m a lo largo del vuelo y ±0.93 m de lado (huella 2.47 × 1.86 m).

## Ancho lateral que ve la cámara principal (campo horizontal 38.9°)

- Pitch -45°, mirando al cabeza en el eje: distancia en línea recta 2.38 m → ancho 1.68 m.
- Pitch -45°, mirando al torso en el eje: distancia en línea recta 2.90 m → ancho 2.05 m.
- Pitch -10°, mirando al cabeza en el eje: distancia en línea recta 9.67 m → ancho 6.83 m.
- Pitch -10°, mirando al torso en el eje: distancia en línea recta 11.81 m → ancho 8.34 m.

## Mirar detrás de un panel de 2.25 m desde 3.30 m

Línea de vista desde la cámara que roza el borde de arriba del panel: hasta qué distancia DETRÁS del panel queda oculto cada punto.

| Postura (altura del punto) | Panel a 4 m | Panel a 5 m |
|---|---|---|
| De pie, cabeza (1.62 m) | 2.4 m | 3.0 m |
| De pie, torso (1.25 m) | 3.8 m | 4.8 m |
| Agachado (1.1 m) | 4.4 m | 5.5 m |
| Gateando (0.6 m) | 6.3 m | 7.9 m |

Para ver a alguien oculto hay que acercarse o subir; subir ya está permitido solo sin personas a menos de 8 m (altura segura 3.30 m).

## Panel de 2.25 m

![Sombra del panel](cobertura/panel_sombra.png)

## Figuras por variante

### Variante A

![Variante A](cobertura/cobertura_variante_A.png)

### Variante B

![Variante B](cobertura/cobertura_variante_B.png)

### Variante C

![Variante C](cobertura/cobertura_variante_C.png)

### Variante D

![Variante D](cobertura/cobertura_variante_D.png)

### Variante E

![Variante E](cobertura/cobertura_variante_E.png)

### Variante F

![Variante F](cobertura/cobertura_variante_F.png)

## Lo que NO cubre este análisis

El campo horizontal (que la persona esté en el cono lateral), el desplazamiento de las cámaras respecto al centro del dron, el balanceo y el cabeceo del chasis, la oclusión por las patas o las hélices, el ruido y la desenfoque, ni el tiempo que tarda el gimbal en llegar al pitch (30°/s la BaseCam, ~600°/s el servo). Es el techo geométrico, no un resultado de vuelo.
