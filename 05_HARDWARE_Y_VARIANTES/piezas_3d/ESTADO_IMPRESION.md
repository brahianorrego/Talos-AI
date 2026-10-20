# Estado de las piezas 3D (2026-10-17)

Compiladas con OpenSCAD 2021.01 (zip oficial, fuera del repositorio). **Todas compilan sin errores ni avisos y cada
una sale como un solo sólido.** Los `.stl` están en `stl/`.

| STL | Tamaño (mm, X × Y × Z) | Para qué |
|---|---|---|
| `pan_tilt_base.stl` | 64 × 56 × 22 | Placa al chasis + soporte del servo de giro |
| `pan_tilt_plataforma.stl` | 52 × 68 × 63 | Mesa que gira + mejillas del servo de subir-bajar y ranura del tope |
| `pan_tilt_cuna.stl` | 59 × 28 × 59 | Cuna que sube y baja: lleva cámara y TF-Luna y el pin del tope (impresa de lado, apoyada en la pared del cuerno) |
| `soporte_camara_frente.stl` | 47.5 × 52 × 32 | Cámara IMX219 mirando al frente (cuadrícula M2 de la cuna) |
| `soporte_camara_abajo.stl` | 49 × 44 × 6.5 | Cámara IMX219 al piso, bajo el chasis |
| `soporte_lidar_luna_pantilt.stl` | 40 × 42 × 16 | TF-Luna en la cuna del pan-tilt |
| `soporte_luna_pod.stl` | 58.5 × 45 × 29.8 | **Variante C:** TF-Luna en el pod de la BaseCam (≈ 8 g) |
| `soporte_tf03_colgante.stl` | 55.6 × 46.8 × 56.3 | **TF03 real al chasis, colgante, con sus roscas M3** (≈ 12 g) |

## Lo que sí se comprobó (en la computadora)

- **Los topes funcionan en el modelo:** se armó la plataforma con la cuna y se buscó si el pin choca con la mejilla.
  Libre a −44°, −43°, 0°, +13° y +14°. Choca a −46°, +15°, +16° y +25° (más allá del tope). Es decir, la cuna no pasa de
  −44°…+14° (1° dentro del rango de la regla dura, a propósito).
- La cuna no toca la plataforma en ningún punto de ese recorrido.

## Lo que NO se pudo comprobar (necesita la pieza real)

Medidas reales del servo MG90D, del cuerno y de la cámara; agujeros del chasis; tolerancia de tu impresora (los
agujeros de 1.8 mm para tornillos autorroscantes y los huecos con 0.3 mm de holgura pueden pedir ajuste); rigidez y
vibración; que el signo de `cabeceo_deg` del soporte del TF03 (nariz hacia abajo) esté bien; los pesos.

## Imprimir

PETG (o PLA+), capa 0.2 mm, 3 paredes, relleno 35 %. Piezas orientadas como salen del STL (base plana abajo; plataforma
sobre su mesa; cuna apoyada sobre su pared gruesa con el pin hacia arriba). Soportes: ninguno previsto, pero el
programa de corte puede pedirlos en los agujeros del servo; mira la vista previa. **Imprime primero una sola pieza** (la
plataforma, que lleva los dos huecos de servo) y prueba que el MG90D entra y que las orejas apoyan antes de seguir.

## Soporte del TF-Luna para el pod de la BaseCam (variante C), añadido el 2026-10-18

`soporte_luna_pod.scad`: placa de 47 × 38 × 2.4 mm con paredes cortas, dos ranuras de tornillo M2 largas en Y (para centrar el
Luna sobre la lente de la cámara), ranuras de amarra plástica y un puente trasero que sirve de alivio del cable fino. Pesa
≈ 6.5 g macizo, ≈ 4 g con 35 % de relleno (calculado del volumen del STL; el Luna aparte, ≈ 5 g más cable), así que casi no hace
palanca sobre el pitch. **Sin ver el pod no se puede verificar:** la altura libre y los tornillos del pod, que la cámara USB no
estorbe al Luna, la distancia real lente-Luna a lente-cámara, y si el cable fino del Luna (no el del TF03) deja moverse el
gimbal hasta −45°, que es la hipótesis de toda la variante C.

Peso estimado de los soportes (STL a 35 % de relleno): pan-tilt 48 g (base 12.7, plataforma 24.6, cuna 10.4); soporte del TF03 al
chasis ≈ 12 g (versión colgante con roscas M3; la antigua con paredes pesaba ≈ 32 g).

## Lo que se ve en las fotos reales del dron (08_EVIDENCIA_Y_DIAGRAMAS/fotos/14 a 18, 2026-10-18)

Lo que digo es lo que **se ve**; ninguna medida sale de las fotos salvo donde dice "de foto, aproximada".

- **TF03:** caja negra con etiqueta blanca (código de barras) en un lado y una ventana grande de esquinas redondeadas al frente.
  Cuelga **debajo** de una placa negra del pod del gimbal. *Tamaño: pendiente.*
- **Placa del pod:** placa negra con una **ranura larga (riel)** y un tornillo de cabeza cilíndrica en cada extremo de la ranura.
  *No puedo asegurar desde las fotos si la ranura va a lo largo de la mirada o de lado (en unas fotos parece una cosa y en otras
  la otra). Pendiente.*
- **Cámara USB:** placa **verde redonda** con un lente negro de tuerca hexagonal; va **encima** de la placa del pod, sujeta por el
  riel. Sus cables salen por detrás. *Diámetro: de foto, aproximada, ≈ 20–25 mm; pendiente medirlo.*
- El gimbal tiene el motor del pitch (negro, redondo) a un lado del pod; el cable amarillo/naranja/rojo de la BaseCam y un cable
  plano naranja pasan cerca. Hay una cinta de velcro azul que sujeta la batería abajo.

## Medidas de las fichas técnicas oficiales (08_EVIDENCIA_Y_DIAGRAMAS/fichas_tecnicas/) — ya usadas

- **TF03:** cuerpo 44 mm de ancho, 42.9 de largo y 31.8 de fondo; 6 roscas M3 de 3.5 mm de hondo en una cara de 44 × 42.9, en dos
  columnas a 38 mm de un borde (32 mm entre ellas) y tres filas a 10 mm. El eje óptico va a lo largo de los 42.9 (ventana en un
  extremo, cable en el otro). Las leí en el dibujo; el 38 y el 10 coinciden con el resumen del Coordinador.
- **TF-Luna:** 35 de ancho con orejas (26.5 sin ellas), 21.25 de alto, 13.5 de fondo con las lentes; 2 agujeros Φ2.2 en las orejas a
  30.5 mm entre ellos y 9 mm bajo el borde de arriba; orejas de 2 mm en la cara de atrás (los agujeros son paralelos a la mirada);
  lentes Φ10.5 a 10.5 mm entre centros; conector de 10.5 × 6.8 mm.

## Lo que ya no es relleno y lo que sigue siendo aproximado

| Dato | Estado |
|---|---|
| Medidas del TF03 y del TF-Luna | **De la ficha oficial** |
| Roscas M3 del TF03 (columnas, filas, hondo) | **De la ficha oficial** |
| Distancia de la primera fila de roscas al extremo de la ventana del TF03 (`fila0`) | **De dibujo, aproximada (≈ 7 mm, contada en píxeles)**; comprobar con el sensor |
| Altura de las filas respecto al borde: columnas a 6 mm de cada borde de los 44 mm | Deducida del "38": 44 − 38 = 6; comprobar |
| Dónde está el conector del TF-Luna respecto a la base (la ventana del suelo es de 14 × 10.5 mm) | **De dibujo, aproximada** |
| **Ranura (riel) del pod: distancia entre sus dos tornillos (`riel_sep`), orientación (`riel_eje`) y tamaño del tornillo (`tornillo_d`)** | **PENDIENTE (de las fotos de Brahian)** |
| **Placa verde de la cámara USB: diámetro y distancia del centro de la placa al centro del lente** | **PENDIENTE (de las fotos de Brahian)** |
| Altura libre entre el riel y lo que cuelga debajo | **PENDIENTE** |

**Lo único que Brahian tiene que medir ahora:** (1) distancia entre los centros de los dos tornillos del riel, (2) si la ranura va a lo
largo de la mirada o de lado y el tamaño de esos tornillos, (3) diámetro de la placa verde de la cámara. (Y comprobar `fila0` en
el TF03 cuando lo desmonte: de la ventana a la primera rosca.)

## Piezas de esta ronda (medidas de la ficha)

| Pieza | Para qué | Peso est. (35 % relleno) | Estado |
|---|---|---|---|
| `soporte_luna_pod.scad` | TF-Luna en el pod (variante C): una L con placa vertical trasera donde se atornilla el Luna **por delante** (2 × M2, agujeros de sus orejas a 30.5 mm), suelo con ventana para el conector y aleta con dos agujeros alargados para el riel (M3 con tuerca hundida) | 8 g | Compila, un solo sólido; `riel_*` de relleno |
| `soporte_tf03_colgante.scad` | **TF03 real** al chasis: el sensor se atornilla por sus 6 roscas M3 a una pared vertical que cuelga de una placa con 4 ranuras M3; `cabeceo_deg = −3` (signo por probar) | 12 g | Compila, un solo sólido; `fila0` aproximada |
| `soporte_lidar.scad` | TF-Luna sobre la cuna del pan-tilt (variante D): cuna abierta con amarras; dimensiones de la ficha | 6 g | Compila |

La versión anterior del TF03 con paredes y amarras (medidas inventadas) se retiró de la lista de piezas.

**Sin ver el pod y el sensor no se puede saber:** si los agujeros alargados caen sobre la ranura, si la placa cabe junto a la cámara USB, si el Luna queda alineado con la cámara, si `fila0` es correcta y si el cable fino del Luna deja bajar el gimbal a −45°.

## Vistas

Imágenes de cada pieza desde tres ángulos en `piezas_3d/vistas/` (hechas con OpenSCAD) y la página `../VISTA_3D.html`, que se abre con doble clic (necesita internet solo para cargar three.js 0.128 de cdnjs) y deja girar cada pieza con el mouse.

## Cómo imprimirlas (para Brahian)

- **Las hicimos nosotros: no se descargan de ningún sitio.** Los `.stl` ya están en `piezas_3d/stl/`.
- Material: **PETG** (o PLA+). Relleno: **30–40 %**. Altura de capa 0.2 mm, 3 paredes. Sin soportes en casi todo; si el programa
  de corte los pide en los agujeros del servo o de las tuercas, mira la vista previa antes.
- Imprime **una sola pieza primero** y pruébala (por ejemplo `soporte_luna_pod.stl`, que es pequeña) antes de seguir.
- Antes de imprimir las que dependen del riel (`soporte_luna_pod`, `soporte_tf03_colgante`), mide los puntos 1–5 de arriba y
  avísame: se cambian 3 números y se vuelve a exportar en un minuto.

## Rediseño estético del pan-tilt (2026-10-18, pedido de Brahian)

El pan-tilt (variante D) se rehízo con un diseño más trabajado, **sin tocar la mecánica**: placas de esquinas redondas con el canto de
arriba biselado, mejillas con perfil "alado" (esquinas cortadas en diagonal) y ventanas tipo estadio de aligeramiento en las
mejillas, en la base y en las paredes de la cuna. Los huecos de los servos, la ranura y el pin del tope, el pivote y la cuadrícula
M2 son los mismos: **se repitió la prueba de intersección y los topes siguen parando la cuna en −44°/+14°** (choca a −46° y +15°).
La versión anterior (cajas rectas) está en `piezas_3d/_v1/pan_tilt_servos_v1.scad`. El peso estimado del pan-tilt impreso pasa a
≈ 45 g (base 12, plataforma 23, cuna 10; 35 % de relleno). Las ventanas aligeran, pero **no se ha comprobado la rigidez** de las
mejillas con ventana: es lo primero que hay que mirar al imprimir.

`VISTA_3D.html` (se regenera con `python generar_vista_3d.py`) muestra ahora el **montaje completo** con PLA gris, blanco o negro, los
dos servos MG90D (con su etiqueta rosa y sus cables), el TF-Luna y la cámara USB como ilustración, sombras y un deslizador de
cabeceo que se detiene en los topes. Los servos, el TF-Luna y la cámara son formas aproximadas, no modelos exactos.

## Módulo colgado (de cabeza) y rango de cabeceo (2026-10-19, pedido de Brahian)

`pan_tilt_servos.scad` ahora tiene `colgado = true` (por defecto): la placa de la base se atornilla a la **cara de abajo del chasis**
y la cuna cuelga. Los ángulos de los topes se calculan para el **mundo** (cabeceo + = la cámara mira arriba): colgado, mirar hacia
abajo es el lado libre del giro (la cuna se aleja de la plataforma). Comprobado con la prueba de intersección en el modelo:

| Rango | Libre entre | Choca en |
|---|---|---|
| **Regla dura 1** (`rango_ancho = false`, por defecto) | −44° y +14° | −46° y +15° |
| **Ancho** (`rango_ancho = true`) | −89° y +44° | −90° y +46° (y libre en todo el intermedio) |

- **El rango ancho es solo capacidad mecánica y NO está aprobado:** la regla dura 1 (CLAUDE.md) fija −45°…+15° y la fórmula
  `pwm = 1500 + θ·500/45` no llega más allá de −45° (daría menos de 1000 µs). El STL `pan_tilt_plataforma_ancho_NO_APROBADA.stl`
  existe para poder verlo y decidir, **no para imprimir** mientras la regla siga. Ampliar la regla toca la simulación, las pruebas y
  la Jetson: lo decide el Supervisor/Brahian.
- **Consecuencias de ir colgado:** (1) la cámara USB queda de cabeza: se gira la placa 180° al montarla (o se voltea la imagen por
  software con una línea); (2) el servo del tilt gira al revés: se corrige con `SERVO9_REVERSED` al calibrar (guía §3.1); (3) los
  soportes de cámara y de LiDAR se atornillan a la cara de la cubierta que queda hacia la carga (ahora la de abajo); (4) el chasis
  tiene que tener espacio libre debajo del punto de montaje: **medir el dron** (patas, batería).
- La versión con el módulo hacia arriba quedó en `_v1/pan_tilt_servos_v2_recto.scad` (o `colgado = false`).
- `VISTA_3D.html` abre colgado bajo una placa de chasis de referencia y tiene botones para voltearlo y para ver el rango ancho.

## Soportes de las cámaras CSI (IMX219), 2026-10-19

`soporte_camara.scad` ahora usa las medidas del **dibujo mecánico oficial** del Raspberry Pi Camera Module 2 / V2.1 (placa de 23.862 × 25 mm,
4 agujeros de Φ2.2 a 12.5 × 21 mm entre centros, lente sobre la columna de agujeros de 14.5 mm y a mitad de los 25 mm):
<https://pip-assets.raspberrypi.com/categories/1205-design-files/documents/RP-008149-DS-1-camera-module-2-mechanical-drawing.pdf>. (Corregí un
error mío: la posición del lente estaba del lado contrario.) Modos: `frente`, `abajo` (cámara al piso) y **`doble`** (`soporte_csi_doble.stl`: placa
bajo el chasis con la cámara al piso y una pared colgante con la frontal ancha de la variante F; ≈ 10 g a 35 % de relleno, 66.5 × 49 × 35 mm).
**Pendiente:** los módulos IMX219 "para Jetson" de otras marcas pueden tener otras medidas (comprobar el que llegue); el espesor de la placa (1 mm) es
supuesto; el flex 15→22 pines (15–20 cm) sale por el borde de 25 mm de la placa y no entra en este diseño todavía.

## Pan-tilt rediseñado para la variante H: CSI + TF-Luna (2026-10-20, D-072)

Contexto (D-072): el gimbal y la cámara USB ya no están. Hoy hay una CSI IMX219 en CAM0 y el TF03, fijos en una base impresa; la meta (H) es un pan-tilt de
2 servos con **la CSI y el TF-Luna**, el TF03 fijo y una segunda CSI al piso. `pan_tilt_servos.scad` trae `carga = "csi_luna"` (por defecto; `carga = "usb"`
reproduce el diseño anterior).

**Qué cambió.** La cuna es más angosta (44 mm: antes 56) porque el TF-Luna (35 mm con orejas) y la CSI (25 mm) van **apilados** en una placa frontal, no lado a lado:
la CSI arriba (lente a +6 mm del eje del tilt) y el TF-Luna abajo (agujeros de sus orejas a −12.4 mm), con los lentes **paralelos** (separados 18.4 mm en vertical:
unos 0.3° de paralaje a 3.5 m). La CSI se atornilla con 4 M2 a separadores de 3.5 mm (medidas del dibujo oficial); el TF-Luna con 2 M2 por los agujeros de sus
orejas (30.5 mm, ficha oficial). La placa tiene un paso para el cable plano de la CSI (16 mm) y otro para el cable del Luna. El eje del tilt sube a 40 mm sobre la
plataforma para que la placa no toque al bajar. **Comprobado en el modelo** (intersección cuna–plataforma): libre entre −44° y +14° del mundo y topado más allá, tanto con el
módulo colgado como hacia arriba. Peso estimado a 35 % de relleno: base 12 g, plataforma 22 g, cuna 10 g (≈ 44 g).

**Riesgo nuevo y real:** la CSI **se mueve** con el pan-tilt y su cable plano no está hecho para doblarse una y otra vez. Hay que dejarle un **lazo flojo** (radio amplio, ≥ 15 mm, mi regla
práctica), sujetarlo a la base sin tensión y no pasarlo por el eje de giro con holgura justa. Si el cable falla, la solución es un cable plano más largo o una cámara USB/otra.

### Lo que se ve en las fotos 19 a 23 (solo describo lo que veo)

- **Arriba:** la Jetson dentro de una caja acrílica transparente, sobre cuatro separadores azules encima de la placa de arriba; la **CSI** está montada al frente-izquierda de la
  caja, con su **cable plano dorado** que sube y se curva hacia el puerto. Encima van las antenas y el GPS.
- **Abajo, al frente:** una **caja negra con etiqueta (el TF03)** colgada debajo de la placa de abajo, hacia el lado y el frente. No veo dónde ni cómo está atornillada.
- **Abajo, atrás:** la batería amarrada con velcro bajo el chasis, y un marco negro cuadrado con un agujero circular sobre ella (no sé para qué sirve).
- Las patas son tubos de carbono largos; los brazos y los variadores van al mismo nivel que las placas.
- **No se ve** la base impresa de la CSI + TF03 en estas fotos que revisé, ni su ancho, ni el ángulo: se necesitan medidas (ver `LISTA_PARA_BRAHIAN.md`).

### Dos opciones de montaje del pan-tilt (propuestas; no sé el espacio real)

| | **Opción 1 · arriba, en el morro** | **Opción 2 · abajo, colgado, adelante** |
|---|---|---|
| Dónde | Sobre la placa de arriba, delante de la caja acrílica de la Jetson (`colgado = false`) | Bajo la placa de abajo, adelante, donde hoy cuelga el TF03 (`colgado = true`) |
| A favor | Cable plano corto y limpio hacia la Jetson; vista libre hacia adelante y hacia abajo; no choca con el suelo al aterrizar | Más libertad de ángulo hacia el suelo (el lado libre del giro mira abajo); cerca del TF03 (misma línea de vista); centro de gravedad bajo |
| En contra | Las hélices y las antenas pueden entrar en el cuadro si se activa el pan; el peso queda arriba y adelante | Hay que dejar espacio sobre las patas y la batería; el cable hasta la Jetson es más largo; la CSI queda de cabeza (se gira la placa 180°) |
| Qué hay que medir | Espacio libre delante de la caja acrílica; altura de las antenas y del cable dorado | Espacio libre debajo (patas, batería, el TF03 actual); distancia al suelo |

Mi recomendación provisional es la **opción 2** (ya está colgado en el visor), **pero solo si el espacio bajo el chasis lo permite**; si no, la opción 1. Brahian decide con las medidas.

## Pan-tilt PLUS (variante H) con giro Y cabeceo, sin alabeo (2026-10-20; D-056 revocada)

Mínimo = variante G (CSI fija + TF03 fijo, sin gimbal). **Plus = variante H:** dos servos mueven el **giro (pan, yaw)** y el **cabeceo (tilt, pitch)**; **no hay alabeo (roll)**, ese y la estabilidad los lleva el dron.
En el pan-tilt van **solo la CSI#1 y el TF-Luna**; el TF03 queda fijo (lado derecho del chasis) y la CSI#2 fija mirando al piso (CAM1).

### Rangos mecánicos y topes (probados en el modelo por intersección)

| Eje | Rango útil | Tope | Cómo se probó |
|---|---|---|---|
| **Tilt** (cabeceo) | **−44° a +14°** del mundo (regla dura 1: −45°…+15°; el tope queda 1° adentro) | pin en la cuna + ranura de arco en la mejilla | libre dentro, choca a −46° y +15° (módulo hacia arriba) |
| **Pan** (giro) | **±89°** (≈ 178° en total; el tope queda 1° dentro de ±90°) | pin bajo la plataforma (radio 25 mm) contra dos **postes de la base** (a ±98° del centro, Ø5) | libre hasta 89° y −89°, choca desde 90° y −92° |

Pan: el recorrido real del MG90D (1 000–2 000 µs ≈ 90–120°; con 500–2 500 µs hasta ≈ 180°) **se confirma en banco** (calibración como en la guía §3.1, con `SERVO10_*`); si el servo no llega a ±90°, bajar `pan_min/pan_max` en el `.scad`
y volver a exportar. Los postes y el pin están por encima de las orejas del servo (sin roce).

### Plataforma: dos versiones según dónde va

El sentido de los topes del tilt cambia según el módulo vaya **arriba** (`colgado = false`, opción 1) o **colgado** (`colgado = true`, opción 2): **se imprime solo la que corresponde**
(`pan_tilt_plataforma_ARRIBA.stl` o `pan_tilt_plataforma_COLGADO.stl`); la base y la cuna son las mismas.

### Cable plano de la CSI#1 (que sobre para girar sin tensarse)

El flex acompaña al giro de ±89° y al cabeceo de −44°/+14°. Mi cálculo (supuesto: recorrido de ≈ 25 mm de radio alrededor del eje): el giro de 178° acorta/alarga el recorrido unos **8 cm** (π × 25 mm),
más ≈ 2 cm por el cabeceo: hay que dejar **≥ 10 cm de cable de sobra en lazo** (radio ≥ 15 mm, regla práctica mía), sujeto a la base con una amarra sin tensar. Cable **de 20 cm** para la opción 1 y **de 30 cm** para la 2
(más de 30 cm da problemas de señal). **Riesgo:** el cable plano no está hecho para doblarse una y otra vez (fatiga); si falla, se cambia o se acorta el giro.

### Dónde va el pan-tilt (viendo las fotos 19–23; lo que veo y lo que no)

Veo: la Jetson en una caja acrílica transparente sobre cuatro separadores azules encima de la placa de arriba, con la CSI al frente y su cable dorado en lazo; GPS y 2 antenas arriba; el TF03 (caja negra con etiqueta) fijo al lado
derecho del chasis a la altura de las placas; la batería colgada bajo el chasis con velcro azul y una pieza impresa negra con un agujero redondo en el frente; patas de carbono con espuma. **No tengo medidas del dron:** las posiciones de abajo son **provisionales**.

| | **Opción 1 · arriba, delante de la caja de la Jetson** (recomendada) | **Opción 2 · colgado, adelante de la batería** |
|---|---|---|
| Se atornilla a | La placa metálica de arriba, **no** a la caja de acrílico (no es estructural) | La placa de abajo, delante de la batería |
| Cable plano (CSI#1) | Corto: 20 cm sobran (la CSI de hoy ya está ahí, el puerto queda a pocos cm) | Largo: 30 cm, en el límite de la señal |
| Vista | Libre al frente y hacia abajo; sin patas ni batería en el cuadro | Ve patas y batería al girar; más libertad hacia el suelo |
| Centro de gravedad | Más alto, adelante | Más bajo, adelante |
| Riesgo | Hélices o antenas en el cuadro a pan grande (probar); sitio disponible delante de la caja | Altura libre bajo el chasis y sobre las patas |
| Qué medir | Espacio libre en la placa de arriba delante de la caja (largo × ancho) | Altura libre bajo la placa de abajo, y la pieza negra impresa del frente |

**Mi recomendación provisional: opción 1** (el flex corto pesa más que cualquier otra cosa por el riesgo de fatiga). Brahian decide con las medidas.

**CSI#2 al piso** (fija): bajo la placa de abajo, **a la izquierda del centro y un poco detrás** (propuesta provisional del Visor: x −0.010 m, y +0.060 m, z −0.034 m; origen en el centro de la placa del medio), para que la batería del centro no la tape y el TF03 de la derecha no le haga sombra. Alternativas: en una pata o inclinada si la placa no da espacio.

### Peso y centro de gravedad de H (estimados; nadie ha pesado)

Masa añadida **≈ 107 g**: pan-tilt impreso 44 g (base 12 + plataforma 22 + cuna 10), 2 servos MG90D 27 g, BEC y cables 15 g, CSI#1 + TF-Luna 11 g, CSI#2 con su soporte 10 g.
Posiciones supuestas (x hacia adelante desde el centro de la placa del medio): pan-tilt 0.075–0.105 m, BEC 0 m, CSI#2 −0.010 m. Resultado: **ΔCG ≈ +2.8 mm hacia adelante** (6 910 g·mm / 2 478 g).
Para anularlo, la batería (≈ 700 g, est.) se corre **≈ 10 mm hacia atrás**. *El Visor tenía provisionalmente 40 mm; con estas cuentas bastan ≈ 10 mm.*

### Pan 0° / tilt −5° = la cámara fija del mínimo

Con el pan en 0° y el tilt en −5° (`TILT_REPOSO_DEG = -5`) la cámara apunta con **la misma orientación** que en G (≈ 5° hacia abajo). Lo que cambia es **dónde está el lente** (en el eje del pan-tilt, no en la base de G)
y **la distancia al TF03** (que queda a ≈ 75 mm al costado): paralaje de ≈ 1.2° a 3.5 m y 0.7° a 6 m. El TF03 sigue paralelo a −5° como en G.

## CSI#2 al piso: inclinación y posición (respuesta al Coordinador, 2026-10-20)

Cálculo geométrico a 3.30 m, IMX219 62.2° × 48.8° nominal con el lado largo en vertical (hacia adelante-atrás): **recta abajo (−90°)** ve ±2.0 m hacia adelante/atrás y ±1.5 m de lado (a la altura de la cabeza, solo ±1.0 m);
**−60°** ve desde 0.06 m detrás del dron hasta **6.0 m adelante** (a la altura de la cabeza, hasta 3.0 m), ancho ≈ 3.5 m; **−45°** ve de 0.8 m a 13.4 m (deja ciega la zona justo bajo el dron). Recomendación: **−60°**, lado largo en vertical, delante o a un costado de
la batería para que no la tape (la posición exacta depende de medidas que no tengo). Pendiente: el soporte `soporte_camara.scad` modo `abajo` queda recto a −90°; para −60° se inclina la placa (cuña) en una próxima ronda.
