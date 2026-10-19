# Lista para Brahian: qué medir y qué comprar

Escrita el 2026-10-19, en sencillo. Está **en orden de importancia**: lo de arriba desbloquea lo de abajo. Los precios son aproximados, de
memoria, en dólares y **sin comprobar** (confírmalos en la tienda). Plan: primero la variante **C** (quitar el cable del TF03 y ver si el
gimbal baja a −45°); la variante **D** (pan-tilt de servos) es el plan B.

## Parte 1. Medir (no cuesta nada, pero decide si las piezas encajan)

Hace falta un **calibrador digital** (≈ 10–15 USD, si no tienes) y una **báscula de cocina de 0.1 g** (≈ 8–12 USD) para pesar las piezas pequeñas.

| # | Qué medir | Para qué |
|---|---|---|
| 1 | **Ranura del pod (riel) de la BaseCam:** distancia de centro a centro entre sus dos tornillos, ancho de la ranura y tamaño de los tornillos; y si la ranura va a lo largo de la mirada o de lado (foto desde arriba con una regla) | El soporte del TF-Luna se atornilla por ahí |
| 2 | **TF03:** de la ventana a la primera rosca (la fila más cercana al lente) | Las roscas M3 del soporte colgante |
| 3 | **Placa verde de la cámara USB:** diámetro, y de su centro al centro del lente | Soporte de la cámara |
| 4 | **Altura libre** entre el riel y lo que cuelga debajo, y el espacio libre bajo el chasis donde iría el pan-tilt | Que quepa |
| 5 | **Pesar:** el dron completo, la BaseCam (con su cableado), el TF03 con su cable, la cámara USB | Peso y centro de gravedad (hoy todo es estimado) |
| 6 | **Paneles de la universidad:** color (¿blancos, claros, oscuros?), ancho y alto reales | Alcance del TF-Luna y la simulación |
| 7 | Con un transportador (o un teléfono con nivel): **hasta qué ángulo baja hoy el gimbal** sin el cable del TF03 | Decide C o D |

## Parte 2. Comprar para la variante C (la recomendada)

| # | Qué | Cantidad | Precio aprox. | Ojo |
|---|---|---|---|---|
| 1 | **TF-Luna** (LiDAR liviano) con su cable | 1 | 20–25 USD | |
| 2 | **Adaptador USB-serie** (CP2102 o CH340) para el TF-Luna | 1 | 3–5 USD | puede pedir compilar un driver, como pasó con el del TF03 |
| 3 | **Cámara IMX219 para Jetson** (la de la Raspberry Pi v2 sirve) | 1 | 15–25 USD | revisar medidas al recibirla |
| 4 | **Cable flex plano de 22 a 15 pines** (0.5 mm a 1.0 mm), de **15–20 cm** | 1 (mejor 2) | 5–8 USD c/u | la Jetson tiene conector de 22 pines y la cámara de 15; hay reportes de cables que no funcionan, compra uno **marcado para Jetson Orin Nano** ([JetsonHacks](https://jetsonhacks.com/2023/04/05/using-the-jetson-orin-nano-with-csi-cameras/), [foro de NVIDIA](https://forums.developer.nvidia.com/t/jetson-orin-nano-cant-load-imx219-device-through-15-22-ribbon-cable/287776)) |
| 5 | **Tornillos M2 autorroscantes** (de 6–8 mm), surtido | 1 caja | ≈ 5 USD | servos y TF-Luna |
| 6 | **Tornillos M3** de 6, 8 y 10 mm con **tuercas** | 1 caja | ≈ 5 USD | chasis, riel, TF03 |
| 7 | **Amarras plásticas pequeñas** (2.5 mm de ancho) | 1 bolsa | ≈ 2 USD | |
| 8 | **Filamento PETG** (gris, blanco o negro) | 1 kg | ≈ 20 USD | se usan menos de 100 g |
| 9 | Cinta doble faz de espuma y **cinta de cobre adhesiva** | 1 | 3–5 USD | proteger el flex del ruido de los variadores |

El cable flex: largo de **15–20 cm** para la cámara del piso (la Jetson queda cerca); más de ~30 cm empieza a dar problemas de señal. **No se dobla en ángulo
agudo ni se mueve** (por eso las cámaras CSI van fijas al chasis, no al gimbal). Radio de curvatura: regla práctica mía de **no menos de 5 mm** y sin dobleces
justo en el conector; no es dato de la ficha.

## Parte 3. Comprar para la variante D (plan B: pan-tilt de servos)

| # | Qué | Cantidad | Precio aprox. | Ojo |
|---|---|---|---|---|
| 1 | **Servo MG90D** (engranes metálicos; como el de tu foto) | 3 (2 + 1 repuesto) | 3–6 USD c/u | no el SG90 de plástico |
| 2 | **BEC (fuente) de 5 a 6 V y 3 A o más** que acepte batería 4S | 1 | 5–10 USD | solo para los servos |
| 3 | **Condensador de 1000 µF, 10 V** | 1 | 1 USD | |
| 4 | Cables de extensión de servo | 2 | 2–3 USD | |
| 5 | Gomas o arandelas blandas antivibración | 1 juego | ≈ 5 USD | |
| 6 | Un **transportador** o buen nivel de teléfono | 1 | ≈ 2 USD | la prueba de banco de los topes |

## Parte 4. No comprar todavía

- **Segunda cámara CSI y TF-Luna al piso** (variante F): la tercera cámara no agrega cobertura (ver `COBERTURA.md`) y satura la CPU de la Jetson.
- **Servos sobre el gimbal** (variante E): más peso sobre unos motores pequeños.

## Qué hago yo con lo que me mandes

Mándame los números de la Parte 1 (basta con 1–3 y 7 para empezar) y cambio los tres o cuatro valores en las piezas, las exporto otra vez y
te dejo los `.stl` listos en `piezas_3d/stl/`. Las piezas están en `VISTA_3D.html` para verlas antes de imprimir.
