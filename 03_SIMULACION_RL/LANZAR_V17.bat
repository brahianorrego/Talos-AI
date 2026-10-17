@echo off
rem V17 · entrenamiento principal (plan 6): 50 M pasos (~4 h a ~3 600 pasos/s), regla de parada D-052 a los 50 M.
rem Carpetas propias: modelos_v17\ y salida_v17\ (no toca modelos_v15). Para detenerlo: Ctrl+C en su ventana.
rem Para seguir después: el mismo comando (retoma modelos_v17\ultimo.zip). Avance: entrenamiento_v17.log
cd /d %~dp0
start "Entrenamiento V17" cmd /k ".venv\Scripts\python.exe -u entrenar_master.py --pasos 5e7 --envs 512 --semilla 17 --salida salida_v17 --dir-master modelos_v17 --dir-modelos modelos_v17 > entrenamiento_v17.log 2>&1"
