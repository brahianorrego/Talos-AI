@echo off
rem MODO ENSENAR: estacion con la simulacion EN VIVO abierta en el modo Ensenar (ver ensenar.js). Abre la simulacion (puerto 8767), el servidor de la estacion
rem (puerto 8768) y Chrome. Para que use la RTX y no la Intel, Chrome debe estar en "Alto rendimiento"
rem (ver PLAN_MOTOR_GRAFICO.md, seccion 2). El visor V16 sigue en v16\simulacion (puerto 8766) si se quiere ver.
cd /d "%~dp0.."
start "Simulacion en vivo" 03_SIMULACION_RL\.venv\Scripts\python.exe 04_VISOR_Y_MOTOR_GRAFICO\en_vivo.py
start "Estacion de tierra" 03_SIMULACION_RL\.venv\Scripts\python.exe 04_VISOR_Y_MOTOR_GRAFICO\estacion\servidor.py
timeout /t 3 >nul
start "" "http://127.0.0.1:8768/?modo=ens"
