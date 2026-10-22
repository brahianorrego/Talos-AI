@echo off
rem Estacion de tierra del MINIMO: la interfaz TALOS-AI conectada a la Jetson real (panel de campo, puerto 8080).
rem Requiere que el portatil y la Jetson esten en la misma red (hotspot). Direccion de la Jetson: variable DRONIA_JETSON (por defecto talos-jetson.local:8080).
cd /d "%~dp0.."
if "%DRONIA_JETSON%"=="" set DRONIA_JETSON=talos-jetson.local:8080
start "Estacion minimo" /min 03_SIMULACION_RL\.venv\Scripts\python.exe 04_VISOR_Y_MOTOR_GRAFICO\estacion\servidor.py --puerto 8768
timeout /t 3 >nul
start "" "http://127.0.0.1:8768/minimo.html"
