@echo off
rem Simulacion EN VIVO dentro de Unreal: abre en_vivo.py (puerto 8767), el puente a Unreal (UDP 8770), la estacion web (8768, para Ensenar y mandos) y el editor con vivo_unreal.py.
cd /d "%~dp0.."
start "Simulacion en vivo" 03_SIMULACION_RL\.venv\Scripts\python.exe 04_VISOR_Y_MOTOR_GRAFICO\en_vivo.py
start "Puente a Unreal" 03_SIMULACION_RL\.venv\Scripts\python.exe 04_VISOR_Y_MOTOR_GRAFICO\puente_unreal.py
start "Estacion de tierra" 03_SIMULACION_RL\.venv\Scripts\python.exe 04_VISOR_Y_MOTOR_GRAFICO\estacion\servidor.py
rem vigilante: cierra solo la ventana del Crash Reporter para que nada se quede esperando un clic
start "Vigilante" /min powershell -NoProfile -WindowStyle Hidden -Command "while($true){Stop-Process -Name CrashReportClient -Force -ErrorAction SilentlyContinue; Start-Sleep 2}"
timeout /t 3 >nul
call "%~dp0unreal\ejecutar_en_unreal.bat" "%~dp0unreal\vivo_unreal.py"
