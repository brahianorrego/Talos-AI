# Estado físico del dron · 20 de octubre

Arquitecto, por pedido del Coordinador. **Solo lectura:** reuní lo que ya está en el repositorio (documentos de `05_HARDWARE_Y_VARIANTES/`,
`docs/`, la memoria compartida y las fotos del 20-oct). **No leí las conversaciones de la cuenta de Tania** (`.claude-tania`): son de
otra persona y el pedido me llegó de otra sesión, no de Brahian. Si Brahian quiere que se cruce con ellas, que lo pida él directamente.
No hay IPs, usuarios ni claves en este archivo. Lo que sale de un solo dicho o de una foto lo marco.

## 1. Qué hardware tiene hoy el dron (variante G)

| Pieza | Estado hoy | Fuente |
|---|---|---|
| **Gimbal BaseCam** | **Quitado** (Brahian lo descartó) | `05_HARDWARE_Y_VARIANTES/VARIANTES.md` §0 (D-072) |
| **Cámara USB** | **Quitada**: el sensor se dañó con el sol | `VARIANTES.md` §0 |
| **Cámara principal** | **CSI IMX219 en CAM0, fija ~5° hacia abajo**, sobre la caja acrílica de la Jetson, con su cable plano; placa `J8IM228-V3.0` (foto) | `VARIANTES.md` §0; `08_EVIDENCIA_Y_DIAGRAMAS/fotos/19_camara_csi_imx219_J8IM228_en_cam0.jpg` y `19_...20oct_1.webp` a `23_...` |
| **LiDAR TF03** | **Fijo**, en la misma base que la cámara, paralelo a ella (−5°) | `VARIANTES.md` §0 y `config_sim/variante_G.json`. En las fotos no pude distinguirlo con seguridad |
| **Jetson Orin Nano** | En caja acrílica transparente encima del chasis, con dos antenas WiFi y un módulo GPS Radiolink visibles | Fotos del 20-oct |
| **Batería LiPo** | Colgada **bajo el chasis**, entre las patas, con correa azul (visible) | Fotos 2, 3 y 4 de la serie del 20-oct |
| **Pixhawk** | Según el Coordinador, **boca abajo bajo el chasis, junto a la batería**. En las fotos se ve una caja negra en ese lugar, compatible con eso, **pero no puedo confirmar que sea la Pixhawk ni su orientación** | Coordinador (dicho); fotos 3-4 |
| **Cámara CSI al piso** | **No hay** (es de la meta H) | `variante_G.json` (`CAM_PISO_ACTIVA: false`) |

Masa: la G suma +5 g (CSI) y quita la BaseCam y la USB. **El peso total de hoy no está medido** (2 371 g era con gimbal; hay que pesar
el dron). Fuente: `VARIANTES.md` §0.

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

- El **mínimo** se entrenó con el TF03 alineado a una cámara USB de 38.9° a −5°: ahora la cámara es otra (62.2° × 48.8°). La regla del
  proyecto ya dice que un cambio de esos obliga a **re-simular el mínimo** (`CLAUDE.md`).
- Sin gimbal, con la cámara fija a −5°, el dron **no ve a menos de ~3.0 m ni el suelo hasta ~5.9 m** (`05_HARDWARE_Y_VARIANTES/COBERTURA.md`).
