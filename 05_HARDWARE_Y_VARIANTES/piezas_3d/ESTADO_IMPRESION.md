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
