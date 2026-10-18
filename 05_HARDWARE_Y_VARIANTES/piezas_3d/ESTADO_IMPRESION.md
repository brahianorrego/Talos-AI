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
| `soporte_luna_pod.stl` | 47 × 38 × 9.4 | **Variante C:** TF-Luna en el pod de la BaseCam (≈ 4–6 g, un solo sólido) |
| `soporte_tf03_colgante.stl` | ver abajo | **TF03 real al chasis, colgante** (medidas de relleno) |
| `soporte_lidar_tf03_chasis.stl` | 102 × 64 × 32 | TF03 al chasis a −3° (medidas del TF03 provisionales) |

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
chasis ≈ 32 g (grande para un sensor de 77 g: se aligera cuando se mida el TF03).

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

## Lo que FALTA medir (lista corta para Brahian, con calibrador)

1. **TF03:** largo (en la dirección en la que mira), ancho y alto. *Pendiente.*
2. **Distancia entre los dos tornillos del riel** (de centro a centro). *Pendiente.* → `riel_sep`.
3. **Ancho de la ranura** y **tamaño de los tornillos** (¿M3? ¿cabeza de cuántos mm?). *Pendiente.* → `tornillo_d`.
4. **¿La ranura va a lo largo de la mirada o de lado?** (basta con una foto desde arriba con una regla al lado). *Pendiente.* → `riel_eje`.
5. **Diámetro de la placa verde de la cámara** y distancia entre su centro y el centro del lente. *Pendiente.*
6. **Altura libre entre el riel y la placa donde cuelga el TF03** (para que el TF-Luna y su soporte quepan).
7. Pesar el TF03, la cámara USB y el pod con todo (pedido de pesaje ya hecho a la parte física).

## Piezas nuevas de esta ronda

| Pieza | Para qué | Estado |
|---|---|---|
| `soporte_luna_pod.scad` (v2) | TF-Luna en el pod, atornillado por el **riel** con dos agujeros alargados (`riel_sep`, `riel_eje`, `tornillo_d`: **de relleno**) y bolsillo para las tuercas bajo el Luna | Compila, un solo sólido |
| `soporte_tf03_colgante.scad` | El **TF03 real** cuelga de esta placa (como hoy del pod) y la placa va al chasis con 4 ranuras M3, con `cabeceo_deg = −3`. Mucho más liviana que la versión con paredes (el signo del cabeceo sigue sin probar) | Compila, un solo sólido; tamaños **de relleno** |

La versión anterior del TF03 (`soporte_lidar.scad` con `modelo="tf03"`, con paredes y amarras) queda de respaldo; sus medidas eran inventadas y por eso la nueva es la que hay que mirar.

**Qué no se puede saber sin la medida real:** si los agujeros alargados caen sobre la ranura, si la placa cabe bajo la cámara USB, si el Luna queda alineado con la cámara y si el cable fino deja bajar el gimbal.

## Vistas

Imágenes de cada pieza desde tres ángulos en `piezas_3d/vistas/` (hechas con OpenSCAD) y la página `../VISTA_3D.html`, que se abre con doble clic (necesita internet solo para cargar three.js 0.128 de cdnjs) y deja girar cada pieza con el mouse.

## Cómo imprimirlas (para Brahian)

- **Las hicimos nosotros: no se descargan de ningún sitio.** Los `.stl` ya están en `piezas_3d/stl/`.
- Material: **PETG** (o PLA+). Relleno: **30–40 %**. Altura de capa 0.2 mm, 3 paredes. Sin soportes en casi todo; si el programa
  de corte los pide en los agujeros del servo o de las tuercas, mira la vista previa antes.
- Imprime **una sola pieza primero** y pruébala (por ejemplo `soporte_luna_pod.stl`, que es pequeña) antes de seguir.
- Antes de imprimir las que dependen del riel (`soporte_luna_pod`, `soporte_tf03_colgante`), mide los puntos 1–5 de arriba y
  avísame: se cambian 3 números y se vuelve a exportar en un minuto.
