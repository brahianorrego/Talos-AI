# Estado físico del dron · 20 de octubre

Arquitecto, por pedido del Coordinador. **Solo lectura:** reuní lo que ya está en el repositorio (documentos de `05_HARDWARE_Y_VARIANTES/`,
`docs/`, la memoria compartida y las fotos del 20-oct). **No leí las conversaciones de la cuenta de Tania** (`.claude-tania`): son de
otra persona y el pedido me llegó de otra sesión, no de Brahian. Si Brahian quiere que se cruce con ellas, que lo pida él directamente.
No hay IPs, usuarios ni claves en este archivo. Lo que sale de un solo dicho o de una foto lo marco.

> **Actualización (D-074, 20-oct, según el Coordinador: Brahian la aprobó en su chat):** son **dos configuraciones, una para cada parte del
> proyecto**, no "la de hoy" y "la meta" del mismo dron. **G = el mínimo** (CSI fija + TF03 fijo, sin gimbal; así queda físicamente).
> **H = el plus**: base impresa con **dos servos que mueven yaw (pan) y pitch (tilt), sin roll** (el roll lo controla el dron), con la CSI
> principal y el TF-Luna juntos en el pan-tilt, una **segunda CSI fija mirando al piso** (CAM0 y CAM1 por cable plano) y el TF03 fijo al chasis.
> El plus se entrena en H; G solo corre el mínimo.

## 0. Correcciones del 20-oct (las dicta la parte física; medidas en el dron)

1. **El mínimo no ha volado con la Jetson.** Lo que hubo: un vuelo de prueba **sin la Jetson** que terminó en **failsafe por batería**; desde entonces no se ha vuelto a volar. Todo lo demás es banco y tomas con el dron en el suelo (`Proyecto-Grado-Minimo/docs/ESTADO.md`).
2. **La cámara USB no se dañó:** se sobreexpone al sol porque su driver no expone la exposición (brillo y contraste no la arreglan). Sirve en interiores. Se descartó por eso.
3. **JetPack 6.2.1 en la Jetson reinstalada:** `nvargus` funciona; la CSI da ≈30 FPS de captura y **≈25 FPS con YOLO** (22-25 ms por cuadro, con seguimiento), con el ISP por hardware. El campo real de la CSI sigue sin medirse (62.2° × 48.8° es nominal).
4. **Pixhawk boca abajo** bajo la placa inferior: `AHRS_ORIENTATION = 8` (Roll180, verificado inclinando el dron). Motores **espejados y con el giro invertido** respecto a un X normal → `FRAME_TYPE = 18` (X_REV) y `SERVO1..4_FUNCTION = 36, 33, 34, 35` (prueba de motores sin hélices). Diagrama: `08_EVIDENCIA_Y_DIAGRAMAS/diagramas/10_motores_vista_superior.png`.
5. **Dónde va cada cosa** (de arriba abajo, `diagramas/11_ubicacion_componentes_vista_lateral.png`, fotos 24-27): GPS RadioLink SE100 en un vástago atrás, más alto que la caja · Jetson en caja de acrílico con 2 antenas WiFi y la CSI pegada al frente de la caja · placa superior · bloque de cables (placa de distribución, power module) con el **TF03 al frente, entre las placas** · placa inferior con la **Pixhawk pegada debajo** · placa de la batería con 2 correas de velcro (azul y negra) y la LiPo 4S.
6. **Medidas (Brahian, 20-oct):** placas de 15 × 15 cm; separación entre placas 3.85 cm (TF03: carcasa 44 × 43 × 32 mm, hoja técnica); caja de la Jetson 4.3 cm; GPS: 11.3 cm de la placa superior a su cima; eje del LiDAR a 28 cm y eje de la cámara a 33.5 cm de la superficie de apoyo (cámara 5.5 cm sobre el LiDAR). Diagrama lateral a escala: `diagramas/11_ubicacion_componentes_vista_lateral.png`.
7. **MEDIDO el 20-oct (`/calibrar`, marcas en la pared a 2.0 m):** campo de visión de la CSI **68.3° × 54.0°** (no 62.2° × 48.8°), cámara inclinada **−2.4°**, rayo del TF03 inclinado **−6.7°** y desviado −0.6° de lado. Cámara 6 cm detrás del frente del LiDAR (medido con regla; si estuviera adelante, los campos subirían ~3°). Datos: `Proyecto-Grado-Minimo/datos_campo/calibracion_2026-10-20/`. Vale para la cámara del mínimo; la CSI#2 del plus es del mismo modelo pero **no se midió**.
8. **Inclinaciones y campo de visión sin medir**: se medirán en el apartamento (pared a pared, ~10 m). El TF03 y la CSI van fijos al chasis; el punto donde pega el LiDAR en la imagen está en `~/alineacion_lidar.json` (provisional, 1 clic a 0.8 m).
9. **Altura del mínimo (por decidir, Brahian):** propone **2.0 m como máximo** y subir a ~3 m solo con peligro inminente. Choca con D-043 (3.30 m con personas a < 8 m) y con el montaje: con el TF03 a −6.5° (medido) desde 2.0 m, el rayo solo toca a una persona de 1.72 m si está a **más de ≈ 2.5 m** (cálculo; con −5° eran 3.2 m): a menos queda por encima de la cabeza.

## 1. Qué hardware tiene hoy el dron (variante G, la del mínimo)

| Pieza | Estado hoy | Fuente |
|---|---|---|
| **Gimbal BaseCam** | **Quitado** (Brahian lo descartó) | `05_HARDWARE_Y_VARIANTES/VARIANTES.md` §0 (D-072) |
| **Cámara USB** | **Quitada**: se sobreexpone al sol (no está dañada; ver §0) | `VARIANTES.md` §0 |
| **Cámara principal** | **CSI IMX219 en CAM0, fija a −2.4° (medido, §0; antes "~5°")**, sobre la caja acrílica de la Jetson, con su cable plano; placa `J8IM228-V3.0` (foto) | `VARIANTES.md` §0; `08_EVIDENCIA_Y_DIAGRAMAS/fotos/19_camara_csi_imx219_J8IM228_en_cam0.jpg` y `19_...20oct_1.webp` a `23_...` |
| **LiDAR TF03** | **Fijo**, en la misma base que la cámara, a −6.7° (medido, §0; no paralelo a la cámara, que va a −2.4°). Según el Coordinador, está **en el lado derecho** del dron; en las fotos no pude distinguirlo con seguridad | `VARIANTES.md` §0 y `config_sim/variante_G.json`; Coordinador (dicho) |
| **Jetson Orin Nano** | En caja acrílica transparente encima del chasis, con dos antenas WiFi y un módulo GPS Radiolink visibles | Fotos del 20-oct |
| **Batería LiPo** | Colgada **bajo el chasis**, entre las patas, con correa azul. Lo confirman las fotos `19_dron_sin_gimbal_20oct_2`, `_3` y `_4` | Fotos del 20-oct (`08_EVIDENCIA_Y_DIAGRAMAS/fotos/20_...`, `21_...`, `22_...`) |
| **Pixhawk** | Según el Coordinador, **boca abajo bajo el chasis, junto a la batería**. En las fotos se ve una caja negra en ese lugar, compatible con eso, **pero no puedo confirmar que sea la Pixhawk ni su orientación** | Coordinador (dicho); fotos 3-4 |
| **Cámara CSI al piso** | **No hay** (es de la meta H) | `variante_G.json` (`CAM_PISO_ACTIVA: false`) |

Masa: la G suma +5 g (CSI) y quita la BaseCam y la USB. **El peso total de hoy no está medido** (2 371 g era con gimbal; hay que pesar
el dron). Fuente: `VARIANTES.md` §0.

### Por qué el plus (H) lleva el TF03 fijo y el TF-Luna en el pan-tilt (D-075)

Decidido por el Coordinador por encargo de Brahian (20-oct), no medido por mí: (1) el TF03 es grande y de cable grueso (ya trabó el pitch del gimbal);
(2) la misión tiene **dos fases en el mismo vuelo**, y con el pan-tilt en pan 0°/tilt −5° el plus equivale a la cámara fija del mínimo, mientras el TF03
fijo conserva el frenado de seguridad; (3) el TF-Luna mide lo que mira la cámara, sin sincronizar los ángulos de los servos con el TF03.

## 2. Qué funcionó y qué no

| Resultado | Estado | Fuente |
|---|---|---|
| CSI sola con YOLO | **Funciona, ≈ 30.8 FPS medido** | `VARIANTES.md` §0 y §2 (medición del 11-oct) |
| CSI con ISP por software (sin `nvargus`, que no arranca en JetPack 7) | Funciona; gasta CPU (~12 ms por cuadro) | `VARIANTES.md` §2 |
| Gimbal (BaseCam) | Descartado: solo bajaba a −10° y el cable del TF03 lo frenaba | `VARIANTES.md` §2 |
| Cámara USB | Dañada por el sol (el sensor) | `VARIANTES.md` §0 |
| Dos cámaras CSI a la vez | **No probado hoy** (en el 11-oct: CSI 21.4 FPS y USB 24.2 FPS en paralelo) | `VARIANTES.md` §2 |
| Pruebas en el aire, pasos 4-7 del mínimo, registros de campo | **Sin fuente en este repositorio**: no sé qué se hizo. Lo que el Coordinador resumió ("pruebas físicas parciales") no consta en `docs/ESTADO.md` ni en `docs/BITACORA.md`, que terminan el 16-oct | revisé `docs/ESTADO.md` y `docs/BITACORA.md` |

## 3. Qué falta saber

1. **Qué pruebas físicas se hicieron hoy y con qué resultado.** Solo lo sabe la parte física (Tania) o Brahian.
2. Pesar el dron sin gimbal y dónde queda el centro de gravedad.
3. Confirmar en el dron: dónde está la Pixhawk y cómo, y que el TF03 quedó paralelo a la cámara a −5°.
4. Medir el campo real de la CSI (hoy 62.2° × 48.8° es nominal) y probar si el sol la sobreexpone, como a la USB.

## 4. Consecuencias para lo ya hecho

- **El plus (H) tiene pan y tilt libres:** D-056 (pan bloqueado) queda revocada (D-074). La zona ciega de G (~3.0 m) es la del mínimo; en H el tilt
  hasta −45° y la CSI al piso la quitan (`05_HARDWARE_Y_VARIANTES/COBERTURA.md`).

- El **mínimo** se entrenó con el TF03 alineado a una cámara USB de 38.9° a −5°: ahora la cámara es otra (62.2° × 48.8°). La regla del
  proyecto ya dice que un cambio de esos obliga a **re-simular el mínimo** (`CLAUDE.md`).
- Sin gimbal, con la cámara fija a −5°, el dron **no ve a menos de ~3.0 m ni el suelo hasta ~5.9 m** (`05_HARDWARE_Y_VARIANTES/COBERTURA.md`).

## 5. Lo que el simulador debe cambiar para parecerse al dron (G para el mínimo, H para el plus)

Para Simulación V17, **sin duplicar su encargo actual** (esto se hace después de cerrar la V17.5 y de la ruta de Brahian). Fuente de cada
valor: `05_HARDWARE_Y_VARIANTES/config_sim/variante_G.json` y `VARIANTES.md` §0. `validar_variantes.py` ya lista estas diferencias.

1. **Cámara principal:** CSI IMX219 de **62.2° × 48.8°** (nominal, sin medir) en lugar de la USB de 38.9° × 29.7° (`HFOV`, `VFOV`). Menos píxeles por
   grado: el YOLO simulado debe ver más chica a la persona lejana.
2. **Sin gimbal:** `GIMBAL_TIPO = "fijo"`, cámara a **−5°** y sin movimiento. Esto quita el seguimiento vertical con el gimbal: la persona
   queda en el cuadro solo por cómo vuelan el dron y su cabeceo. Hay que revisar lo que dependía del gimbal (el reflejo de punto ciego, el 360° de
   entrada a −3°/−12°, las acciones de la red). Es la diferencia más grande.
3. **TF03 fijo a −5°** paralelo a la cámara (hoy `TF03_PITCH_V17 = −3°`) y **sin TF-Luna** ni cámara al piso en G (`CAM_PISO_ACTIVA = false`).
4. **Zona ciega:** la cabeza se ve desde ~3.0 m y el suelo desde ~5.9 m (`COBERTURA.md`). La simulación debe dejar de ver a quien se acerca a menos de ~3 m.
5. **Imagen real:** la CSI tiene ISP por software (exposición y balance de blancos en la CPU, ~12 ms por cuadro): añadir **sobreexposición a pleno sol**
   (la USB se sobreexpone al sol) y pérdidas de detección por brillo; el YOLO medido es **30.8 FPS**, no más.
6. **El plus se entrena en H** (D-074): pan y tilt libres, CSI principal y TF-Luna juntos en el pan-tilt, segunda CSI fija al piso (62.2° × 48.8° a −90°), TF03 fijo al chasis, el roll lo controla el dron. **G solo corre el mínimo** (puntos 1-5 aplican a G y al re-simular el mínimo; la H usa la cámara de 62.2° × 48.8° con tilt libre).
7. **No cambiar** las reglas duras ni el árbitro; la simulación puede seguir acotando el gimbal virtual a −45°..+15° (más estricto que sin gimbal).
