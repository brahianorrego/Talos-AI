# CLAUDE.md

Guía para Claude Code en la carpeta de trabajo definitiva del proyecto de grado. Estado actual: @docs/ESTADO.md
Mapa de archivos: @GUIA_DE_ARCHIVOS.md · Nombres viejos → nuevos: `INDICE_NOMBRES.md`.

Esta carpeta se armó el 2026-10-16 **copiando** (no moviendo) `Desktop\Claude\Tesis-IA-Drone`, que queda intacta
como respaldo y archivo histórico (repositorio viejo `Tesis-IA-Drone`). Esta carpeta es el repositorio
**`Dron-IA-Vigilancia`** (por ahora solo local; plan en `docs/PLAN_GITHUB_NUEVO.md`).

## Qué es este proyecto

Proyecto de grado de Ingeniería Aeronáutica (Universidad de San Buenaventura): un cuadricóptero que **detecta
personas y evita obstáculos** (mínimo aprobado por el comité) y, como trabajo complementario ("plus"), **mantiene a la
vista a un sospechoso** en exteriores. Jetson Orin Nano + Pixhawk (ArduPilot 4.7) por MAVLink, YOLO26n, LiDAR TF03,
gimbal BaseCam. Autor: Brahian Andrés Orrego Osorio. Tania redacta el documento.

Dos IAs en el mínimo (YOLO preentrenado + decisor MLP) y una IA de refuerzo (PPO) en el plus, siempre con reglas
deterministas alrededor y un operador humano.

## Convenciones

- Escribir **"proyecto de grado"**, nunca "tesis" (salvo nombres ya existentes: `Tesis-IA-Drone`, `minimo_tesis/`).
- Español, lenguaje sencillo: Brahian no es programador.
- Pedir confirmación antes de lo irreversible o hacia afuera: `git push`, `gh repo create`, Releases, subir archivos,
  borrar, merge.
- Pruebas físicas: un paso a la vez, con instrucciones exactas, esperando confirmación.
- No cambiar la lógica de los scripts salvo que se pida. Antes de reescribir un archivo, copia `_vN` en
  `_archivo_versiones/codigo/`.
- No inventar números: toda cifra en un documento lleva el archivo de donde sale.
- El repositorio futuro es **público**: nada de IPs, usuarios, contraseñas, WiFi, seriales, rutas `C:\Users\...`,
  fotos de personas, Word ni PDFs del comité.

## Reglas duras del sistema (no negociables)

1. **Gimbal entre −45° y +15°**, pase lo que pase (`GIMBAL_MIN`, `GIMBAL_NADIR`, `GIMBAL_TACTICO` en `entorno.py` y
   `control.GimbalBaseCam.MIN`, D-014). PWM de AUX1: `pwm = 1500 + θ·500/45`. Prohibido ampliar el mapeo.
2. **Geocerca:** el dron no sale de la arena (`ARENA = 25 m`); salir = misión fallida, `R_GEOCERCA = -5`. En el dron
   real la fija ArduPilot.
3. **Búsqueda determinista al perder el objetivo** (`PERDIDA_IA = False`, D-015). La política solo decide con el
   objetivo fijado.
4. **Humano en el lazo:** la IA nunca decide quién es el sospechoso; lo confirma el operador con un clic.
5. **Árbitro de seguridad:** solo autoriza evadir ante amenaza real (persona a < 3 m, o a < 8 m acercándose). El
   bloqueo frontal por LiDAR (< 3 m) y la parada de emergencia (CH8) mandan sobre la IA.
6. La red **no estabiliza nada**: eso lo hacen los PID de ArduPilot y del gimbal.

Además: **`01_MINIMO_INDISPENSABLE/` está CONGELADO** (ver su `_LEEME.md`). No se mueve el TF03 ni el gimbal hasta
terminar los pasos 4-7 del mínimo; si se cambian, hay que re-simular el mínimo.

## Comandos (Windows, desde `03_SIMULACION_RL\`)

```
:: comprobar que el entorno importa
.venv\Scripts\python.exe -c "import entorno"

:: pruebas (reglas duras, entorno, mínimo, herramientas)
.venv\Scripts\python.exe -m unittest discover -s tests

:: mínimo indispensable: protocolo del comité (~10 s con --sin-degradadas; completo ~5 min)
.venv\Scripts\python.exe -m minimo_tesis.protocolo_comite --sin-degradadas

:: visor 3D en http://127.0.0.1:8765/
ABRIR_VISOR.bat

:: informe de un entrenamiento y evaluación en escenarios fijos -> informes\
.venv\Scripts\python.exe herramientas\resumir_metricas.py
.venv\Scripts\python.exe herramientas\evaluar_politica.py --barrido 25 --version v10-master

:: ver las redes (desde la raíz del proyecto)
03_SIMULACION_RL\.venv\Scripts\python.exe 06_REDES_NEURONALES_Y_MODELOS\ver_redes.py

:: entrenar (SOLO con aprobación de Brahian)
.venv\Scripts\python.exe -u entrenar_master.py
```

- `.venv` no se copia: `py -m venv .venv` y `pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu`
  + `numpy==2.5.3 gymnasium==1.4.0 stable_baselines3==2.9.0 scikit-learn==1.9.1 matplotlib==3.11.2 scipy==1.18.1`
  (mismas versiones que el original).
- Con un entrenamiento en marcha, `modelos_v15\ultimo.zip` y `salida\` cambian a cada rato: no copiarlos sin pararlo.
- Si falla una prueba de reglas duras, no se relaja la prueba: se consulta a Brahian.

## Ciclo de mejora

`resumir_metricas.py` + `evaluar_politica.py` → agente `supervisor-rl` (diagnóstico, máximo 3 cambios) → Brahian
aprueba → agente `implementador` (cambio, pruebas, bitácora) → reentrenar. Cerrar cada sesión con `/cierre-sesion`.
