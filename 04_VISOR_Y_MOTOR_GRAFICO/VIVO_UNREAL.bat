@echo off
rem UNA SOLA PANTALLA: Unreal en vivo a la izquierda (60 %) y la estacion de tierra en modo Ensenar a la derecha (40 %).
rem Abre en_vivo.py (puerto 8767), el puente a Unreal (UDP 8770), la estacion (8768), un vigilante que cierra solo el Crash Reporter, la estacion en una ventana de Edge y el editor con vivo_unreal.py.
rem Variables opcionales: DRONIA_NOCHE=1 solo sirve al armar el nivel (crear_cancha.py); DRONIA_PANTALLA_UNREAL=70 cambia el porcentaje de la pantalla para Unreal.
cd /d "%~dp0.."
start "Simulacion en vivo" 03_SIMULACION_RL\.venv\Scripts\python.exe 04_VISOR_Y_MOTOR_GRAFICO\en_vivo.py
start "Puente a Unreal" 03_SIMULACION_RL\.venv\Scripts\python.exe 04_VISOR_Y_MOTOR_GRAFICO\puente_unreal.py
start "Estacion de tierra" 03_SIMULACION_RL\.venv\Scripts\python.exe 04_VISOR_Y_MOTOR_GRAFICO\estacion\servidor.py
start "Vigilante" /min powershell -NoProfile -WindowStyle Hidden -Command "while($true){Stop-Process -Name CrashReportClient -Force -ErrorAction SilentlyContinue; Start-Sleep 2}"
if "%DRONIA_PANTALLA_UNREAL%"=="" set DRONIA_PANTALLA_UNREAL=60
for /f "tokens=1,2" %%a in ('powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; $s=[System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea; Write-Output ($s.Width.ToString()+' '+$s.Height.ToString())"') do (set SW=%%a& set SH=%%b)
set /a UW=SW*%DRONIA_PANTALLA_UNREAL%/100
set /a EW=SW-UW
set DRONIA_RX=%UW%
set DRONIA_RY=%SH%
set DRONIA_WX=0
set DRONIA_WY=0
timeout /t 3 >nul
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
  start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app=http://127.0.0.1:8768/?modo=ens --window-position=%UW%,0 --window-size=%EW%,%SH%
) else (
  start "" "http://127.0.0.1:8768/?modo=ens"
)
start "Ventanas" /min powershell -NoProfile -WindowStyle Hidden -File "%~dp0acomodar_ventanas.ps1" -Porcentaje %DRONIA_PANTALLA_UNREAL%
call "%~dp0unreal\ejecutar_en_unreal.bat" "%~dp0unreal\vivo_unreal.py"
