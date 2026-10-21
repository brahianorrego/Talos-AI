# 06 · Anexos sugeridos (el documento tiene un máximo de 100 páginas)

Regla del proyecto (memoria `documento-tesis-plan`): el código va en anexos, no en el cuerpo. Propuesta de qué anexar y cuánto ocupa aproximadamente; los tamaños son **estimaciones mías**
(no medí páginas). El cuerpo debe quedar con las figuras, las tablas de resultados y la discusión.

| Anexo | Contenido | Archivo de origen | Páginas (estimadas) |
|---|---|---|---:|
| A | Historial de la parte física, con los fallos | `docs/HISTORIAL_PRUEBAS_FISICAS.md` | 3-4 |
| B | Procedimiento para replicar el montaje | `docs/PROCEDIMIENTO_REPLICABLE.md` | 5-6 |
| C | Configuración de la Pixhawk y de la Jetson (sin IPs ni claves) | `02_JETSON_A_BORDO/` y `docs/PROCEDIMIENTO_REPLICABLE.md` §3 | 2 |
| D | Lógica del mínimo (reglas, decisor MLP y envolvente) | `03_SIMULACION_RL/minimo_tesis/decisor_ia.py`, `sistema.py` (solo funciones clave) | 4-5 |
| E | Resultados del protocolo del comité y del decisor | `03_SIMULACION_RL/informes/minimo_tesis_protocolo.md`, `minimo_tesis_decisor_ia.md` | 3-4 |
| F | Mundo simulado del plus: constantes, sensores, ladrón, recompensas | `03_SIMULACION_RL/entorno.py` (resumen en tabla, no el código entero) | 4-5 |
| G | Líneas base y mediciones del plus (tablas con 512 partidas) | `03_SIMULACION_RL/informes/v17/*.json`, `docs/PROGRESO_V17.md` | 3-4 |
| H | Diagnóstico de la V15 | `03_SIMULACION_RL/informes/diagnostico_v17_ia_aporta.md`, `informes/barrido_v15.md` | 2-3 |
| I | Decisiones de diseño (D-001 a D-080) | `docs/DECISIONES.md` | 8-10 |
| J | Variantes de hardware G y H, cobertura y piezas 3D | `05_HARDWARE_Y_VARIANTES/VARIANTES.md`, `COBERTURA.md` | 4-5 |
| K | Calibración de ángulos de la cámara y del LiDAR | `08_EVIDENCIA_Y_DIAGRAMAS/calibracion_angulos_2026-10-20/` | 2 |
| L | Estación de tierra y motor gráfico (capturas) | `04_VISOR_Y_MOTOR_GRAFICO/`, `docs/MATERIAL_PARA_DOCUMENTO/05_motor_grafico_y_juego.md` | 3-4 |

Total estimado de anexos: ~45-55 páginas, que dejan ~45-55 para el cuerpo. **Ajustar con las páginas reales** cuando Tania maquete.

## Qué no va

- Código completo de `entorno.py` (más de 3 500 líneas) ni de la estación web.
- Fotos de personas reales, datos de red, IPs, usuarios y claves (`docs/PLAN_GITHUB_NUEVO.md` §3).
- Cifras sin archivo de origen; todo lo "[pendiente]" de `docs/SECCION_PLUS_DOCUMENTO.md` hasta que se llene.
