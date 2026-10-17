@echo off
rem Simulacion EN VIVO en el visor V16 (fase V5). Abre dos ventanas: la simulacion (puerto 8767) y el visor (puerto 8766).
rem Para ver la RTX y no la Intel, Chrome debe estar en "Alto rendimiento" (ver PLAN_MOTOR_GRAFICO.md, seccion 2).
cd /d "%~dp0.."
start "Simulacion en vivo" 03_SIMULACION_RL\.venv\Scripts\python.exe 04_VISOR_Y_MOTOR_GRAFICO\en_vivo.py
start "Visor V16" 03_SIMULACION_RL\.venv\Scripts\python.exe 04_VISOR_Y_MOTOR_GRAFICO\v16\simulacion\servidor_visor.py --puerto 8766
timeout /t 3 >nul
start "" "http://127.0.0.1:8766/?r=vivo"
