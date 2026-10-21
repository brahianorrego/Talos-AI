@echo off
rem Reanuda el entrenamiento de la V17.9 (variante H, ruta B5') desde 03_SIMULACION_RL\modelos_v17_9\ultimo.zip.
rem Prioridad baja y 6 hilos para no quitarle fluidez a Unreal. Avance: 03_SIMULACION_RL\modelos_v17_9.log
cd /d %~dp003_SIMULACION_RL
start "Entrenamiento V17.9" /belownormal /min cmd /c ".venv\Scripts\python.exe -u entrenar_master.py --hw H --set BUSQUEDA_RUTA_V17=1 --pasos 1e7 --envs 512 --semilla 19 --ent 0.01 --hilos 6 --repeticiones 5 --salida salida_v17_9 --dir-master modelos_v17_9 --dir-modelos modelos_v17_9 >> modelos_v17_9.log 2>&1"
echo Entrenamiento lanzado en segundo plano.
rem el python de verdad es un proceso hijo del lanzador del .venv: se le baja la prioridad a el tambien
powershell -NoProfile -Command "Start-Sleep 8; Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | ? { $_.CommandLine -match 'entrenar_master' } | % { (Get-Process -Id $_.ProcessId).PriorityClass='BelowNormal' }"
