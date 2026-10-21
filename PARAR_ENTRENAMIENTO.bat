@echo off
rem Detiene el entrenamiento de la V17.9 guardando el ultimo modelo (03_SIMULACION_RL\modelos_v17_9\ultimo.zip).
rem Espera hasta 2 minutos a que termine solo; si no, lo cierra (se pierde como maximo lo de las ultimas 20 iteraciones).
rem Para seguir despues: REANUDAR_ENTRENAMIENTO.bat
cd /d %~dp0
echo parar > 03_SIMULACION_RL\modelos_v17_9\PARAR
echo Pidiendo al entrenamiento que se guarde y pare...
powershell -NoProfile -Command "$t=0; while((Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | ? { $_.CommandLine -match 'entrenar_master' }) -and $t -lt 120){ Start-Sleep 3; $t+=3 }; $q = Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | ? { $_.CommandLine -match 'entrenar_master' }; if($q){ $q | % { Stop-Process -Id $_.ProcessId -Force }; 'Se cerro a la fuerza (se guardo el ultimo punto automatico).' } else { 'Entrenamiento detenido y guardado.' }"
pause
