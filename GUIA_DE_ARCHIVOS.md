# Guía de archivos

Qué es cada carpeta y archivo importante, quién lo usa, dónde corre y si es del **mínimo** (lo que pide el comité)
o del **plus** (IA de refuerzo, trabajo complementario). Para saber de dónde salió cada cosa: `INDICE_NOMBRES.md`.

## 1. Raíz

| Archivo | Qué es | Quién lo usa |
|---|---|---|
| `README.md` | Portada del proyecto | Cualquiera que llegue |
| `CLAUDE.md` | Reglas duras, convenciones y comandos | Claude Code (lo lee solo al abrir la carpeta) |
| `GUIA_DE_ARCHIVOS.md` | Este archivo | Brahian, Tania, Claude |
| `COMO_FUNCIONA_EL_CODIGO.md` | Cómo está construido el sistema, con diagramas | Brahian, el Ing. Harold, Tania |
| `DEMOSTRACION_PARA_EL_INGENIERO.md` | Guion de 10 minutos con los comandos exactos | Brahian, el día de la reunión |
| `INDICE_NOMBRES.md` | Ruta vieja → ruta nueva | Para encontrar algo de antes |
| `_copia_log.txt` | Registro de la copia del 2026-10-16 | Auditoría de la migración |

## 2. Carpetas

| Carpeta | Qué hay | Corre en | Mínimo / plus | ¿A Git (repo público)? |
|---|---|---|---|---|
| `01_MINIMO_INDISPENSABLE/` | Foto **congelada** del mínimo: simulación, decisor, informes, scripts de a bordo. Ver su `_LEEME.md` | — (referencia) | Mínimo | Sí, salvo `registros_campo/` con personas |
| `02_JETSON_A_BORDO/` | Código que se copia a la Jetson | Jetson (y `campo.py` en el PC) | Los dos | Sí (sin seriales ni IPs: ya vienen como `<...>`) |
| `03_SIMULACION_RL/` | Simulación, entrenamiento PPO, visor, pruebas, informes, modelos | PC | Los dos (`minimo_tesis/` = mínimo; el resto = plus) | Código sí; `modelos*`, `salida*`, `.venv` no |
| `04_VISOR_Y_MOTOR_GRAFICO/` | Plan del visor nuevo (el vigente está en la 03) | — | Plus | Sí |
| `05_HARDWARE_Y_VARIANTES/` | `hardware.md`, `pixhawk.md`, `jetson.md`; luego variantes A-F | — | Los dos | Sí |
| `06_REDES_NEURONALES_Y_MODELOS/` | `ver_redes.py` e índice de modelos | PC | Los dos | Sí (los modelos no) |
| `07_DOCUMENTO_PROYECTO_DE_GRADO/` | Word, cartas y PDFs del comité | — | — | **Nunca** (privado) |
| `08_EVIDENCIA_Y_DIAGRAMAS/` | Fotos, diagramas, gráficas (`redes/` la genera `ver_redes.py`) | — | Los dos | Sí, sin fotos de personas |
| `docs/` | `ESTADO.md`, `BITACORA.md`, `DECISIONES.md`, planes V15 y V16, informe de jornada | — | Los dos | Sí |
| `_archivo_versiones/` | Versiones viejas (`entorno_v2..v15`, `index_v4..v19`, logs, modelos y salidas v1-v14) | — | Plus | Código sí; modelos no |
| `_memoria_claude/` | Copia de la memoria de Claude Code (`jetson-conexion` sin secretos) | — | — | No (notas personales) |
| `.claude/` | Agentes (`arquitecto`, `supervisor-rl`, `implementador`), skill `cierre-sesion`, permisos, visor | Claude Code | — | Agentes y skill sí; `settings.local.json` no |

## 3. `03_SIMULACION_RL/` archivo por archivo

| Archivo / carpeta | Qué hace | Mínimo / plus |
|---|---|---|
| `entorno.py` | El mundo simulado en NumPy (miles de partidas a la vez): dron, ladrón, civiles, muros, cámara + YOLO estadístico, LiDAR, mapa, máquina de estados de búsqueda, recompensas, currículo | Plus |
| `control.py` | Modelo de los controladores reales: ArduPilot (posición y actitud) y PID del gimbal BaseCam (−45°..+15°) | Plus |
| `entrenar_master.py` | Entrena la política PPO (Stable-Baselines3), currículo, checkpoints y exporta `dron_politica.json` | Plus |
| `entrenar.py` | PPO propio en torch (v1-v9); el master reutiliza utilidades | Plus |
| `mision.py` | Misión completa para el visor (fase 1 piloto + fase 2 IA) | Plus |
| `evaluar.py` | IA vs reglas (desactualizado; revisar antes de usar) | Plus |
| `index.html` + `ABRIR_VISOR.bat` | Visor 3D (three.js) en http://127.0.0.1:8765/ | Los dos |
| `CONTINUAR_ENTRENAMIENTO.bat` | Retoma `entrenar_master.py` | Plus |
| `herramientas/resumir_metricas.py` | Informe corto de un entrenamiento → `informes/resumen_*.md` | Plus |
| `herramientas/evaluar_politica.py` | Escenarios fijos (abierto, cambio brusco, tras muro, debajo) → `informes/evaluacion_*`, `barrido_*` | Plus |
| `minimo_tesis/sistema.py` | Mundo del mínimo y `SistemaMinimo` (la lógica que correría en la Jetson) | **Mínimo** |
| `minimo_tesis/sensores.py` | Cámara + YOLO, LiDAR TF03 y retardo de 100 ms | **Mínimo** |
| `minimo_tesis/control.py` | Copia congelada del control (no depende del `control.py` del plus) | **Mínimo** |
| `minimo_tesis/protocolo_comite.py` | Protocolo del comité: escenarios a-e, métricas, CSV y repetición | **Mínimo** |
| `minimo_tesis/decisor_ia.py`, `entrenar_decisor.py`, `evaluar_decisores.py` | Decisor MLP: entradas, entrenamiento, comparación con las reglas | **Mínimo** |
| `minimo_tesis/decision.json` / `.pkl` | El decisor entrenado | **Mínimo** |
| `tests/` | 88 pruebas (reglas duras, entorno, mínimo, decisor, V13-V15, herramientas); ~2.5 min | Los dos |
| `informes/` | Resultados medidos: `minimo_tesis_*` (mínimo), `evaluacion_*`, `resumen_*`, `barrido_*`, `diagnostico_*` (plus) | Los dos |
| `modelos_v15/` | Última política PPO (`ultimo.zip`) y sus checkpoints | Plus |
| `modelos_master/`, `modelos_v12/`, `modelos_v14/`, `modelos/` | Políticas anteriores y la exportación para la Jetson | Plus |
| `salida/` | Lo que lee el visor: `estado.json`, `metricas.json`, `hitos/` | Plus |

## 4. `02_JETSON_A_BORDO/` archivo por archivo

| Archivo | Qué hace | Mínimo / plus |
|---|---|---|
| `config.py` | Puertos, umbrales y velocidades. **En la Jetson tiene los seriales reales; aquí van como `<NUMERO_DE_SERIE>`** | Los dos |
| `lidar_tf.py` | Lee el TF03 (trama de 9 bytes, 100 Hz) | Mínimo |
| `percepcion.py` | Cámara USB/CSI + YOLO26n con seguimiento de ID | Mínimo |
| `camara_csi.py` | Cámara IMX219 con ISP por software (nvargus no arranca en JetPack 7) | Respaldo |
| `capturar_patron.py`, `correccion_camara.py` | Quitan la cuadrícula de la cámara USB sin filtro IR | Opcional |
| `gimbal_basecam.py` | Lee los ángulos de la BaseCam (`REALTIME_DATA`); el pitch se manda por AUX1 | Mínimo (pitch fijo −5°) |
| `sensores.py`, `comun.py` | Unen cámara + YOLO + LiDAR + gimbal; entradas y carga del modelo de la **IA #2 vieja** | Plus / histórico |
| `registro_minimo.py` | Pasos 1 y 4: registra cada cuadro (YOLO, LiDAR, gimbal, Pixhawk) sin mandar nada | **Mínimo** |
| `intervencion_banco.py` | Paso 3: freno + subida por MAVLink en banco, sin hélices | **Mínimo** |
| `herramientas/campo.py` | Paso 4: maneja las tomas E0-E6 **desde el portátil** (pitidos, iniciar/terminar, descargar) | **Mínimo** |
| `herramientas/visor.sh`, `visor_web.py` | Visor de la cámara en el navegador (puerto 8080) | Los dos |
| `vuelo_evasion.py` | Percepción → MLP viejo → árbitro → MAVLink GUIDED; giro de yaw hacia la persona | Plus / histórico |
| `grabar_dataset.py`, `entrenar_mlp.py` | Dataset etiquetado a mano y MLP de la IA #2 vieja (reemplazado por `minimo_tesis/`) | Histórico |
| `requirements_jetson.txt` | Dependencias (**desactualizado**: dice Python 3.8 y scikit-learn 1.3.2; la Jetson tiene Python 3.12) | — |

Falta escribir `sistema_minimo.py` (paso 5: el decisor del mínimo en modo sombra en la Jetson). Hoy ningún script de
a bordo carga el `decision.json` del mínimo.

## 5. Qué sube a la Jetson y qué no

| (a) Sí se copia a la Jetson | (b) Corre solo en el PC | (c) Es de simulación pero se **replica** en la Jetson |
|---|---|---|
| Todo `02_JETSON_A_BORDO/*.py` **menos `config.py`** (el de la Jetson tiene los seriales reales; si cambia algo, se edita allá a mano) | `03_SIMULACION_RL/entorno.py`, `control.py`, `entrenar_master.py`, `entrenar.py`, `mision.py`, `evaluar.py` | Las **15 entradas del decisor** (`minimo_tesis/decisor_ia.py`, función que arma `X`): alto/ancho/área de la caja, ángulo, confianza, cuadros seguidos, LiDAR útil, velocidad propia, seguimiento alfa-beta. Deben normalizarse con `media` y `desv` de `decision.json` |
| `03_SIMULACION_RL/minimo_tesis/decision.json` → `~/Escritorio/dron_ia/minimo/` (no junto al `decision.pkl` viejo) | `herramientas/`, `tests/`, `informes/`, visor `index.html` | El **filtro alfa-beta** de distancia y velocidad de la persona y la distancia por ancho de hombros cuando la caja sale cortada (`minimo_tesis/sensores.py` y `decisor_ia.py`) |
| `decision.pkl` solo si la Jetson tiene scikit-learn **1.9.1** (si no, usar el JSON con `decisor_ia.predecir_json`, NumPy puro; verificado: diferencia 5e-7) | `06_REDES_NEURONALES_Y_MODELOS/ver_redes.py`, `campo.py` (corre en el portátil y habla con la Jetson) | La **envolvente de reglas duras**: LiDAR < 3 m frena, árbitro (< 3 m, o < 8 m acercándose), CH8, regla de 2 cuadros sobre el umbral 0.7 |
| `modelos/dron_politica.json` **solo si algún día** se vuela la política PPO (hoy no: no es del mínimo) | Modelos `.zip` de Stable-Baselines3 | Si se vuela el PPO: las **192 entradas** deben calcularse igual que `entorno.py` (`_sensores`, `OBS_DRON = 21 + 7 + 8 + 2 + 10 + 144`: persona, memoria, 8 sectores del LiDAR, predicción, estado propio, grilla de 12×12 celdas de 1.5 m). Hoy **no existe** ese código en la Jetson |
| `yolo26n.engine`: no se copia, se regenera en la Jetson (`yolo export model=yolo26n.pt format=engine half=True`) | | Mapeo del gimbal `pwm = 1500 + θ·500/45` y límites −45°..+15° (ya está en `gimbal_basecam.py` y `config.py`) |

**Comando para copiar a la Jetson** (desde la raíz del proyecto, en PowerShell; pide la clave SSH si no hay llave):

```
cd 02_JETSON_A_BORDO
scp camara_csi.py capturar_patron.py comun.py correccion_camara.py entrenar_mlp.py gimbal_basecam.py grabar_dataset.py intervencion_banco.py lidar_tf.py percepcion.py registro_minimo.py sensores.py visor_web.py vuelo_evasion.py <usuario>@<IP-de-la-Jetson>:~/Escritorio/dron_ia/
ssh <usuario>@<IP-de-la-Jetson> "mkdir -p ~/Escritorio/dron_ia/minimo"
scp ..\03_SIMULACION_RL\minimo_tesis\decision.json <usuario>@<IP-de-la-Jetson>:~/Escritorio/dron_ia/minimo/
```

Antes de copiar, respaldar en la Jetson: `cp -r ~/Escritorio/dron_ia ~/Escritorio/dron_ia_respaldo_$(date +%F)`.
Ojo: la Jetson puede tener cambios que no están aquí (se editó en vivo por SSH): comparar primero con
`ssh ... "md5sum ~/Escritorio/dron_ia/*.py"` contra `certutil -hashfile` en el PC.
