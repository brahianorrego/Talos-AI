@echo off
rem V17 · plan 5.2: una corrida de 10 M pasos con TODO y una sin cada regla de recompensa, misma semilla, cada una en su
rem carpeta. Las corre una tras otra (de noche). SOLO con aprobación de Brahian (o del Supervisor delegado).
rem Comandos y tiempos en docs\PROGRESO_V17.md. Para correr una sola: copiar su línea en la consola, desde 03_SIMULACION_RL.
cd /d %~dp0
set PY=.venv\Scripts\python.exe -u entrenar_master.py --pasos 1e7 --envs 512 --semilla 17 --repeticiones 0
%PY% --salida salida_v17_todo   --dir-master modelos_v17_todo   --dir-modelos modelos_v17_todo   > modelos_v17_todo.log 2>&1
%PY% --salida salida_v17_sin_R1 --dir-master modelos_v17_sin_R1 --dir-modelos modelos_v17_sin_R1 --set K_COB=0 > modelos_v17_sin_R1.log 2>&1
%PY% --salida salida_v17_sin_R2 --dir-master modelos_v17_sin_R2 --dir-modelos modelos_v17_sin_R2 --set K_ESC=0 > modelos_v17_sin_R2.log 2>&1
%PY% --salida salida_v17_sin_R3 --dir-master modelos_v17_sin_R3 --dir-modelos modelos_v17_sin_R3 --ent 0.01 > modelos_v17_sin_R3.log 2>&1
%PY% --salida salida_v17_sin_R4 --dir-master modelos_v17_sin_R4 --dir-modelos modelos_v17_sin_R4 --set R_READQ_V17=8 > modelos_v17_sin_R4.log 2>&1
%PY% --salida salida_v17_sin_R5 --dir-master modelos_v17_sin_R5 --dir-modelos modelos_v17_sin_R5 --set K_JERK_V16=0 > modelos_v17_sin_R5.log 2>&1
%PY% --salida salida_v17_sin_R6 --dir-master modelos_v17_sin_R6 --dir-modelos modelos_v17_sin_R6 --set R_SOBREVUELO=0 --set R_ANGULO_GMB=0 > modelos_v17_sin_R6.log 2>&1
rem (opcional) lo mismo que "todo", pero copiando las capas ocultas de la V15 (E4: medir si la transferencia ayuda)
rem %PY% --salida salida_v17_desde_v15 --dir-master modelos_v17_desde_v15 --dir-modelos modelos_v17_desde_v15 --desde modelos_v15\ultimo.zip > modelos_v17_desde_v15.log 2>&1
echo Listo. Medir cada modelos_v17_*\ultimo.zip con herramientas\medir_ia_aporta.py v17 (ver docs\PROGRESO_V17.md).
