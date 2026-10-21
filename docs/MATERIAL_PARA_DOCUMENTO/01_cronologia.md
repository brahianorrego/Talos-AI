# 01 · Cronología (16 al 20 de octubre de 2026)

Fuente: `git log` de `Dron-IA-Proyecto` (4, 57, 20, 20 y 45 commits los días 16, 17, 18, 19 y 20) y `docs/DECISIONES.md`. Antecedentes del 5 al 15-oct:
`docs/BITACORA.md` y `docs/HISTORIAL_PRUEBAS_FISICAS.md`. Las pruebas físicas están en el historial de la parte física; aquí va lo de simulación y coordinación.

| Fecha | Qué pasó | Fuente |
|---|---|---|
| 16-oct | Migración a la carpeta definitiva `Dron-IA-Proyecto`: se copiaron 4 119 archivos, 88 pruebas pasan, snapshot congelado del mínimo | `docs/ESTADO.md` |
| 17-oct | **Diagnóstico medido de la V15:** su política rendía igual que quedarse quieto y que el azar. Plan V17 y decisiones D-049 a D-059 | `03_SIMULACION_RL/informes/diagnostico_v17_ia_aporta.md`, `docs/PLAN_V17_REFUERZO.md` |
| 17-oct | Código de la V16 traído; cancha con dos V; 7 acciones con efecto; máscara de acciones; línea base B0-B2; visor V16 en el repositorio | `docs/PROGRESO_V17.md` |
| 17-oct | Variantes de hardware A-F y piezas 3D del pan-tilt | `05_HARDWARE_Y_VARIANTES/VARIANTES.md` |
| 18-oct | V17.2 a 50 M pasos: 54.3 % contra 56.2 % de "siempre subir". V17.3 colapsó. Compuerta B4 cerrada (D-067/D-068). Reinstalación de la Jetson | `docs/PROGRESO_V17.md`, `docs/HISTORIAL_PRUEBAS_FISICAS.md` |
| 19-oct | Pruebas de campo: la cámara USB salía casi blanca; se cambió a la CSI. Ruta de búsqueda de Brahian (D-071), D-069/D-070. Se decide quitar el gimbal y la USB | `docs/HISTORIAL_PRUEBAS_FISICAS.md`, `docs/DECISIONES.md` |
| 20-oct | Pixhawk boca abajo y motores espejados corregidos por software; medición de ángulos de la CSI (68.3° × 54.0°); mínimo re-simulado (D-078, D-079); mínimo = variante G y plus = variante H (D-074, D-075); altura del plus (D-080) | `docs/HISTORIAL_PRUEBAS_FISICAS.md`, `docs/DECISIONES.md` |
| 20-oct | Órdenes de Brahian sobre paneles de 2.30 × 1.50 × 0.05 m, búsqueda detrás del panel, modo de juego en la estación | `docs/ORDENES_BRAHIAN_20OCT.md` |
| 20-oct | Mediciones del plus en H: B0 72.9 %, B5' 84.2 %, V17.7 85.4 % de racha de 30 s; con despeje de paneles, choques 0 % (la tabla justa con el mismo despeje está **pendiente**) | `03_SIMULACION_RL/informes/v17/n_b0.json`, `n_b5p.json`, `n_v177.json` |

Línea de decisiones (resumen, `docs/DECISIONES.md`): D-049 siete acciones; D-050 máscara de acciones; D-051/D-066 paneles; D-052 criterio "la IA aporta";
D-059 métrica de 30 s; D-062 plan de entrenamiento; D-067/D-068 altura cerrada; D-069/D-070 la red decide al perderlo; D-071 ruta de Brahian; D-072/D-074 variantes G y H;
D-075 TF03 fijo y TF-Luna en el pan-tilt; D-076 y D-080 órdenes y altura.
