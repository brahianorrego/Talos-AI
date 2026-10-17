# 04 · Visor y motor gráfico

**El visor que funciona hoy no está aquí:** es `03_SIMULACION_RL/index.html` (three.js) y se abre con
`03_SIMULACION_RL/ABRIR_VISOR.bat` en http://127.0.0.1:8765/. Se queda en la 03 porque lee
`salida/estado.json`, `salida/hitos/` y `minimo_tesis/replay/` por ruta relativa desde el mismo servidor.

| Qué | Dónde |
|---|---|
| Visor vigente | `03_SIMULACION_RL/index.html` |
| Versiones anteriores (v4 a v19) | `_archivo_versiones/codigo/index_v*.html` |
| Visor de la cámara real (en la Jetson) | `02_JETSON_A_BORDO/visor_web.py` |
| Visor realista V16 (three.js, en la nube, sin entrenar) | ramas `v16-visor` y `v16-simulacion` del repositorio `Tesis-IA-Drone` en GitHub |
| Contrato de datos simulación → visor (`foto()`) | `docs/PLAN_V16_REALISMO.md`, sección 3, fase A5 |

Aquí irá el plan del motor gráfico y de la interfaz de tres modos (Fase D, solo plan; no se construye todavía).
