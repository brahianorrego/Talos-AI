@echo off
rem Corre un script de Python DENTRO del editor de Unreal (proyecto DronIA_Cancha) y espera a que el editor se cierre.
rem El script debe cerrar el editor al final (renderizar.py lo hace). Lo recoge init_unreal.py por la variable DRONIA_ORDEN.
rem Uso:  ejecutar_en_unreal.bat script.py [argumento ...]
rem Ej.:  ejecutar_en_unreal.bat renderizar.py /Game/DronIA/Secuencias/Rep_replay_v17_salida_v17_1 %USERPROFILE%/Videos/dron_ia/unreal 240 242
setlocal
if "%DRONIA_RX%"=="" set DRONIA_RX=1280
if "%DRONIA_RY%"=="" set DRONIA_RY=720
set "ORDEN=%~f1"
shift
:sig
if "%~1"=="" goto fin
set "ORDEN=%ORDEN%|%~1"
shift
goto sig
:fin
set "ORDEN=%ORDEN:\=/%"
set "DRONIA_ORDEN=%ORDEN%"
start "" /wait "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe" "%USERPROFILE%\Documents\Unreal Projects\DronIA_Cancha\DronIA_Cancha.uproject" -nosplash -windowed -unattended -NoVSync -ResX=%DRONIA_RX% -ResY=%DRONIA_RY%
endlocal
