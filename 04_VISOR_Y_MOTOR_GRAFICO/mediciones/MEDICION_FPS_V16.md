# Medición del visor V16 en el portátil (2026-10-16)

Visor traído con `git archive` de `origin/v16-visor` (71c55c2) y `docs/PROGRESO_V16.md` de `origin/v16-simulacion`
(0a46f1d) a `04_VISOR_Y_MOTOR_GRAFICO/v16/` (no está en Git todavía). Se abre con la configuración `visor-v16` de
`.claude/launch.json` (puerto 8766). Medido con `medir_fps.mjs` (Chrome visible, 1540 × 788 px, escala 1.25, partida
"Misión de prueba · 2 paneles" corriendo, 10 s por calidad). Datos en `fps_*.json`.

| Gráfica que usa Chrome | Alta | Media | Baja |
|---|---|---|---|
| Intel UHD (lo que Chrome usa **por defecto**) | 24 cps (p95 194 ms) | 26 cps | 38 cps |
| RTX 3050 6 GB Laptop (`--force_high_performance_gpu`) | 144 cps (tope de la pantalla) | 144 | 144 |
| RTX 3050 sin tope de pantalla | 202 cps (mediana 4.5 ms) | 203 | 228 |

- `nvidia-smi`: NVIDIA GeForce RTX 3050 6GB Laptop GPU, 6144 MiB, controlador 616.56, hasta 45 W.
- **Hallazgo clave:** Chrome y el panel del navegador de la app usan la Intel. Para el visor hay que darle a Chrome la
  RTX: Configuración de Windows → Sistema → Pantalla → Gráficos → Chrome → "Alto rendimiento" (lo hace Brahian).
- Con la RTX sobra margen (~5 veces sobre 30 cps y casi igual en alta y baja: el límite es el procesador, no la gráfica).
- El panel interno de la app con la ventana oculta da ~1 cps: no sirve para medir.
