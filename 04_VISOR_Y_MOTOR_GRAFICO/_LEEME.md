# 04 · Visor y motor gráfico

**El visor que funciona hoy no está aquí:** es `03_SIMULACION_RL/index.html` (three.js) y se abre con
`03_SIMULACION_RL/ABRIR_VISOR.bat` en http://127.0.0.1:8765/. Se queda en la 03 porque lee
`salida/estado.json`, `salida/hitos/` y `minimo_tesis/replay/` por ruta relativa desde el mismo servidor.

| Qué | Dónde |
|---|---|
| **Plan del motor gráfico y de la interfaz de 3 modos** (Fase D1-D2) | `PLAN_MOTOR_GRAFICO.md` |
| Boceto de la estación de tierra | `boceto_interfaz.svg` (y `.png`) |
| Cuadros por segundo del visor V16 en el portátil, capturas y el script que mide | `mediciones/` |
| Visor V16 traído de las ramas `v16-visor` y `v16-simulacion` (en `main` desde el commit 3c38f66, aprobado por Brahian el 17-oct) | `v16/` (configuración `visor-v16` de `.claude/launch.json`, puerto 8766) |
| Visor vigente | `03_SIMULACION_RL/index.html` |
| Versiones anteriores (v4 a v19) | `_archivo_versiones/codigo/index_v*.html` |
| Visor de la cámara real (en la Jetson) | `02_JETSON_A_BORDO/visor_web.py` |
| Contrato de datos simulación → visor (`foto()`) | `docs/PLAN_V16_REALISMO.md` (fase A5) y `v16/docs/PROGRESO_V16.md` |

Para ver el V16 con la RTX: Chrome tiene que usar la gráfica NVIDIA (ver `PLAN_MOTOR_GRAFICO.md`, sección 2).

## Revisión de `v16/` para el repositorio público (2026-10-17)

Sin fotos de personas: las personas, el dron, los árboles y los escenarios se dibujan con código. No se carga nada de
internet (todo es local). Archivos que no son código:

| Archivo | Origen | Licencia |
|---|---|---|
| `recursos/three/` (three.js 0.185.1) | npm `three` | MIT (`recursos/three/LICENSE`) |
| `recursos/cielo/spruit_sunrise_1k.hdr`, `quarry_01_1k.hdr` | Poly Haven (Greg Zaal) | CC0 |
| `recursos/texturas/*.jpg` (12: concreto, pasto, tierra) | Generadas con ruido fractal por `herramientas/generar_texturas.py` | Propias (CC0) |
| `replays_prueba/*.json` | Repeticiones de prueba de la V16; llevan el nombre de Brahian como autor | Propias |

Fuente: `v16/simulacion/recursos/LICENCIAS.md`. Pendiente: `generar_texturas.py` no se trajo de la rama `v16-visor`;
habría que copiarlo para que se vea cómo se hicieron las texturas.
