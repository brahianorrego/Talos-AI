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
