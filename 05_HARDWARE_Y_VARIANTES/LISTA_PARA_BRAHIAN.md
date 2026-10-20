# Lista para Brahian: qué medir y qué comprar

Actualizada el 2026-10-20 (D-072: ya no hay gimbal ni cámara USB). En sencillo y **en orden de importancia**. Los precios son aproximados, de memoria, en dólares y
**sin comprobar** (confírmalos en la tienda).

**Dónde estamos:** hoy el dron es la **variante G** (una cámara CSI y el TF03 fijos en una base impresa). La **meta es la H**: un pan-tilt de 2 servos con la
CSI y el TF-Luna encima, el TF03 fijo, y una **segunda CSI (CAM1) mirando al piso**. Lo viejo del gimbal, el riel del pod y la cámara USB ya no hace falta medirlo.

## Parte 1. Medir (no cuesta nada)

Hace falta un **calibrador digital** (≈ 10–15 USD, si no tienes), una **báscula de cocina de 0.1 g** (≈ 8–12 USD) y un **nivel de teléfono** o transportador.

| # | Qué medir (de la base impresa actual) | Para qué |
|---|---|---|
| 1 | **Ancho, largo y alto de la base impresa** donde van la cámara y el TF03 | Saber qué tamaño de espacio hay y si el pan-tilt la puede reemplazar |
| 2 | **Separación entre el centro del lente de la cámara y el centro de la ventana del TF03** (en vertical y de lado) | Corregir la diferencia entre lo que ve la cámara y lo que mide el LiDAR |
| 3 | **Ángulo de la cámara y del TF03** con el nivel (¿de verdad ~5° hacia abajo? ¿están paralelos?) | La simulación lo usa (hoy supone −3° para el TF03) |
| 4 | **Espacio libre para el pan-tilt** (mira dos sitios): (a) **arriba, delante de la caja acrílica de la Jetson**: largo, ancho y altura libre hasta las antenas y el cable dorado; (b) **abajo, delante**: altura libre entre la placa de abajo y el suelo con las patas puestas, y dónde queda la batería | Decide la opción 1 (arriba) o 2 (abajo) del montaje |
| 5 | **Distancia de la Jetson (conector de la cámara) a cada punto de montaje**, siguiendo por dónde pasaría el cable | Largo del cable plano que hay que comprar |
| 6 | **Pesar:** el dron completo con la base actual, y la base impresa sola | Peso y centro de gravedad |
| 7 | **TF03:** de la ventana a la primera rosca (la fila más cercana al lente) | Soporte con sus roscas M3 |
| 8 | **Paneles de la universidad:** color y medidas reales | Alcance del TF-Luna y simulación |
| 9 | **¿Quedó medido el campo de visión real de la cámara CSI?** (62.2° × 48.8° es el del fabricante, sin medir) | La simulación aún usa los números de la cámara USB |

## Parte 2. Comprar para la variante H

| # | Qué | Cantidad | Precio aprox. | Ojo |
|---|---|---|---|---|
| 1 | **Segunda cámara IMX219** (CAM1, al piso) | 1 | 15–25 USD | revisar medidas al recibirla |
| 2 | **Cables planos de 22 a 15 pines** (0.5 mm a 1.0 mm) | **2 o 3**: uno de 15–20 cm para la del piso y uno **más largo (20–30 cm)** para la cámara que va en el pan-tilt, que se mueve | 5–8 USD c/u | compra cables **marcados para Jetson Orin Nano** ([JetsonHacks](https://jetsonhacks.com/2023/04/05/using-the-jetson-orin-nano-with-csi-cameras/), [foro de NVIDIA](https://forums.developer.nvidia.com/t/jetson-orin-nano-cant-load-imx219-device-through-15-22-ribbon-cable/287776)); más de ~30 cm da problemas de señal |
| 3 | **TF-Luna** (LiDAR liviano) con su cable | 1 | 20–25 USD | |
| 4 | **Adaptador USB-serie** (CP2102 o CH340) para el TF-Luna | 1 | 3–5 USD | puede pedir compilar un driver, como pasó con el del TF03 |
| 5 | **Servo MG90D** (engranes metálicos) | 3 (2 + 1 de repuesto) | 3–6 USD c/u | tienes uno en la foto; no el SG90 de plástico |
| 6 | **BEC (fuente) de 5 a 6 V y 3 A o más**, que acepte batería 4S | 1 | 5–10 USD | solo para los servos |
| 7 | **Condensador de 1000 µF, 10 V** | 1 | 1 USD | |
| 8 | **Tornillos M2 autorroscantes** de 6–8 mm, surtido | 1 caja | ≈ 5 USD | servos, CSI, TF-Luna |
| 9 | **Tornillos M3 con tuercas** de 6–10 mm | 1 caja | ≈ 5 USD | base, chasis |
| 10 | **Filamento PETG** | 1 kg | ≈ 20 USD | se usan ≈ 60 g (pan-tilt 44 g más soportes) |
| 11 | Extensiones de cable de servo, amarras plásticas pequeñas, cinta doble faz de espuma, **cinta de cobre** | 1 de cada | 10–15 USD | la cinta de cobre protege el flex del ruido de los variadores |
| 12 | Gomas o arandelas blandas antivibración | 1 juego | ≈ 5 USD | |

## Parte 3. Lo importante sobre el cable de la cámara que se mueve

La CSI en el pan-tilt **se mueve** y su cable plano no está hecho para doblarse muchas veces. Déjale un **lazo flojo** (radio amplio, mi regla práctica es ≥ 15 mm), sujétalo a la
base con una amarra sin tensarlo y evita doblarlo justo en el conector. Si más adelante falla, se cambia por un cable más largo.

## Parte 4. No comprar todavía

- **Gimbal, cámara USB, BaseCam:** descartados (D-072).
- **Tercera cámara o TF-Luna al piso:** no aportan lo suficiente (ver `COBERTURA.md`) y cargan la CPU de la Jetson.

## Qué hago yo con lo que me mandes

Con las medidas 1–5 ajusto la base del pan-tilt y el largo del cable, exporto los `.stl` otra vez y te los dejo listos en `piezas_3d/stl/`. Puedes verlas antes en `VISTA_3D.html`.
