# Diagramas del documento

Cada diagrama tiene su fuente Mermaid (`.mmd`, se puede editar en https://mermaid.live) y su imagen (`.png`, lista para
pegar en Word). Todos son de autoría propia: según la plantilla USB no hace falta la nota "Elaboración propia".

| Archivo | En el documento (versión 2) | Qué muestra |
|---|---|---|
| `01_arquitectura` | Figura 14 (2.2.6) | Percepción (cámara, YOLO, LiDAR, EKF) → Jetson (15 entradas, MLP, envolvente de reglas) → Pixhawk en GUIDED; el piloto siempre manda |
| `02_estados` | Figura 15 (2.2.6) | Estados de la intervención: PILOTO, VIGILANDO, DETENER, DETENER Y ASCENDER, RETENIDO y PARADA |
| `03_experimento` | Figura 17 (2.3.1) | Secuencia de validación en dos filas: sin vuelo autónomo (simulación, banco, datos reales) y en vuelo (modo sombra, vuelos, protocolo de campo) |
| `04_porque_ia` | No se usa en la versión 2 | Reglas solas frente a IA con envolvente en los escenarios de discriminación |
| `05_metodologia_corregida.png` | Figura 5 (1.9.3) | La figura original con dos textos corregidos: "computadora de a bordo" y "entorno exterior" en vez de "Raspberry Pi" y "entorno indoor" |
| `06_caja_negra` | Figura 6 (2.1.1) | Entradas y salidas del sistema visto como caja negra |
| `07_caja_transparente` | Figura 7 (2.1.1) | Los cuatro subsistemas (potencia, percepción, decisión, control) y sus dos respuestas |
| `08_funcional` | Figura 8 (2.1.2) | Descomposición funcional en F1 percibir, F2 decidir y F3 responder |
| `09_conexiones` | Figura 10 (2.2.2) | Conexiones eléctricas (líneas gruesas) y de datos (líneas delgadas) |
| `10_motores_vista_superior` | Nueva (2.2.2) | Motores vistos desde arriba: número, lugar, giro, hélice y salida de la Pixhawk (`FRAME_TYPE = 18`). Hay `.svg` editable y `.png` |
| `11_ubicacion_componentes_vista_lateral` | Nueva (2.2.2) | De arriba abajo: GPS, Jetson y antenas, placa superior, bloque de cables y TF03, placa inferior, Pixhawk, batería. Esquema sin escala (`.svg` y `.png`) |

Los diagramas 06 a 09 reemplazan figuras de la versión anterior que tenían errores (Raspberry Pi, textos ilegibles o
datos que no coincidían con el montaje real). Se diseñaron para que, al tamaño de la página, la letra quede cerca de
9 pt (mínimo legible según APA).

Para regenerar las imágenes (necesita Node y el navegador Chromium):

```
npx -y @mermaid-js/mermaid-cli@11.4.2 -i 01_arquitectura.mmd -o 01_arquitectura.png -s 2 -w 5000 -H 5000 -b white
```

Se usó el tema `neutral` con letra Times New Roman (la misma del documento).

**20-oct:** `01`, `07` y `09` se actualizaron (cámara CSI en lugar de la USB y sin el estabilizador BaseCam; YOLO ~22 ms). Las versiones anteriores están en `_versiones_anteriores/`. La altura de intervención (3.30 m) no se tocó: está por decidir (D-077).
