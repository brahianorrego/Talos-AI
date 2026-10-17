# Índice de nombres: dónde quedó cada cosa

La carpeta se armó **copiando** desde `Desktop\Claude\` (el original sigue intacto). **Ningún archivo se renombró**:
solo cambiaron de carpeta. Así los scripts siguen funcionando sin tocar su lógica.

## Carpeta vieja → carpeta nueva

| Antes (`Desktop\Claude\...`) | Ahora (`Dron-IA-Proyecto\...`) | Para qué sirve |
|---|---|---|
| `Tesis-IA-Drone\simulacion\` (archivos vigentes) | `03_SIMULACION_RL\` | Simulación, entrenamiento, visor, pruebas e informes. Misma estructura interna |
| `Tesis-IA-Drone\simulacion\*_vN.py`, `index_vN.html`, `entrenamiento_vN.log`, `servidor.log` | `_archivo_versiones\codigo\` | Versiones viejas de cada archivo. No se editan |
| `Tesis-IA-Drone\simulacion\modelos_v1..v8*`, `salida_v1..v14*` | `_archivo_versiones\modelos_y_salidas\` | Modelos y salidas de versiones viejas |
| `Tesis-IA-Drone\simulacion\modelos_master\`, `modelos_v12\`, `modelos_v14\`, `modelos_v15\`, `modelos\`, `salida\` | `03_SIMULACION_RL\` (mismo nombre) | Los usan `entrenar_master.py`, `evaluar_politica.py` y las pruebas por ruta relativa |
| `Tesis-IA-Drone\simulacion\minimo_tesis\` | `03_SIMULACION_RL\minimo_tesis\` (el que se ejecuta) **y** `01_MINIMO_INDISPENSABLE\minimo_tesis\` (copia congelada) | El mínimo indispensable |
| `Tesis-IA-Drone\simulacion\informes\minimo_tesis_*` | `03_SIMULACION_RL\informes\` y copia en `01_MINIMO_INDISPENSABLE\informes\` | Resultados del protocolo y del decisor |
| `Tesis-IA-Drone\simulacion\tests\test_minimo_tesis.py`, `test_decisor_ia.py` | `03_SIMULACION_RL\tests\` y copia en `01_MINIMO_INDISPENSABLE\pruebas\` | Pruebas del mínimo |
| `Tesis-IA-Drone\jetson\` | `02_JETSON_A_BORDO\` | Código que corre en la Jetson |
| `Tesis-IA-Drone\jetson\registro_minimo.py`, `intervencion_banco.py`, `herramientas\campo.py` | también en `01_MINIMO_INDISPENSABLE\jetson_minimo\` (copia congelada) | Scripts de a bordo del mínimo |
| `Tesis-IA-Drone\docs\PLAN_MINIMO_FISICO.md` | `01_MINIMO_INDISPENSABLE\` | Pasos 0-8 del mínimo en el dron real |
| `Tesis-IA-Drone\docs\hardware.md`, `pixhawk.md`, `jetson.md` | `05_HARDWARE_Y_VARIANTES\` | Configuración del hardware |
| `Tesis-IA-Drone\docs\` (el resto) | `docs\` | ESTADO, BITÁCORA, DECISIONES, planes V15 y V16 |
| `Tesis-IA-Drone\.claude\agents\`, `skills\cierre-sesion\` | `.claude\` | Agentes `arquitecto`, `supervisor-rl`, `implementador` y la skill de cierre |
| `Desktop\Claude\.claude\settings.local.json` | `.claude\settings.local.json` | Permisos de Claude Code, **reescritos sin IP ni usuario** |
| `Desktop\Claude\.claude\launch.json` | `.claude\launch.json` | Servidor del visor para la app de Claude, con la ruta nueva |
| `Desktop\Claude\Documentacion-Tesis\` | `07_DOCUMENTO_PROYECTO_DE_GRADO\` | **PRIVADO**: Word, PDFs del comité, encargo de redacción. Nunca a Git |
| `Desktop\Claude\MIGRACION\imagenes\` | `08_EVIDENCIA_Y_DIAGRAMAS\` | Fotos de los paneles de la U y del pan-tilt |
| Memoria de Claude Code (`.claude\projects\C--Users-Brahi-Desktop-Claude\memory\`) | `.claude\projects\C--Users-Brahi-Desktop-Dron-IA-Proyecto\memory\` y copia en `_memoria_claude\` | Notas de memoria. `jetson-conexion.md` va **sin secretos** en las dos |
| `Tesis-IA-Drone\README.md`, `CLAUDE.md` | `README.md`, `CLAUDE.md` de la raíz (reescritos con rutas nuevas) | Portada y reglas |
| `Tesis-IA-Drone\.gitignore` | (no copiado todavía) | Se escribe en la Fase E, al preparar el repositorio nuevo |

## Lo que no se copió

| Qué | Por qué |
|---|---|
| `simulacion\.venv` | Se recrea con las mismas versiones (ver `CLAUDE.md`) |
| `__pycache__` | Se regenera solo |
| `.git` | Esta carpeta aún no es repositorio; el historial sigue en `Tesis-IA-Drone` |

## Diferencias con la estructura pedida

- `04_VISOR_Y_MOTOR_GRAFICO\`: el visor (`index.html`) **se queda en `03_SIMULACION_RL\`**, porque lee
  `salida\estado.json` y `minimo_tesis\replay\` con rutas relativas del mismo servidor. Sus versiones viejas están
  en `_archivo_versiones\codigo\index_v*.html`. La 04 queda para el plan del motor gráfico (Fase D).
- `06_REDES_NEURONALES_Y_MODELOS\`: los modelos se quedan en `03_SIMULACION_RL\modelos*\` (los scripts los buscan
  ahí). La 06 tiene `ver_redes.py` y el índice de modelos.

## Cambios de rutas hechos en la copia

Ninguno en el código: con la estructura de arriba, `python -c "import entorno"` y las pruebas corren tal cual (ver
`docs\ESTADO.md`, migración del 2026-10-16).
