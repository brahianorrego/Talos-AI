# Demostración para el Ing. Harold (10 minutos)

Guion para mostrar el proyecto sin tener que preguntar qué abrir. Todo corre en el portátil, sin internet.

## Antes de la reunión (2 minutos, una sola vez)

1. Abrir **PowerShell** y entrar a la carpeta:
   ```
   cd $HOME\Desktop\Dron-IA-Proyecto\03_SIMULACION_RL
   ```
2. Comprobar que todo funciona (18 s; debe terminar en `OK`):
   ```
   .venv\Scripts\python.exe -m unittest tests.test_reglas_duras tests.test_minimo_tesis
   ```
3. Dejar abierto el visor: doble clic en `03_SIMULACION_RL\ABRIR_VISOR.bat` (abre http://127.0.0.1:8765/ en el
   navegador; usar Chrome o Edge a pantalla completa).

## Minuto 0-1 · Qué es el proyecto

Abrir `README.md` (diagrama de arquitectura). Decir: *"El piloto vuela; el sistema detecta personas con YOLO, mide
obstáculos con el LiDAR, y una red neuronal decide si frenar y subir a 3.30 m. Las reglas de seguridad y el piloto
siempre mandan sobre la IA."*

## Minuto 1-4 · El mínimo indispensable (lo que pide el comité)

1. En el visor, selector de arriba a la derecha → **"Mínimo indispensable · protocolo del comité"**. Se ven el
   avance hacia el panel, la persona que viene de frente, la que cruza lejos (no se activa) y el modo estático.
2. Cambiar a **"Mínimo indispensable · decisor: reglas"** y luego **"decisor: IA + envolvente"** para comparar.
3. Correr el protocolo en vivo (5 s):
   ```
   .venv\Scripts\python.exe -m minimo_tesis.protocolo_comite --sin-degradadas
   ```
   Se imprime una línea por escenario: éxito, activación, choques.
   **Ojo:** esto reescribe `informes\minimo_tesis_protocolo.md` sin la sección de condiciones degradadas. Después,
   restaurarlo con:
   ```
   copy ..\01_MINIMO_INDISPENSABLE\informes\minimo_tesis_protocolo.md informes\
   ```
4. Mostrar el informe: `informes\minimo_tesis_protocolo.md` (1300 vuelos, éxito 100 % [99.7, 100], 0 activaciones
   falsas en 300; con el operador solo, 23 % de vuelos seguros) y `informes\minimo_tesis_decisor_ia.md` (la IA baja
   las activaciones innecesarias de 44 a 30 y los choques de 39 a 28 en mundos de prueba).

## Minuto 4-6 · "El código y la red"

Desde la raíz del proyecto (15 s):
```
cd $HOME\Desktop\Dron-IA-Proyecto
03_SIMULACION_RL\.venv\Scripts\python.exe 06_REDES_NEURONALES_Y_MODELOS\ver_redes.py
```
Muestra:
- **Decisor del mínimo:** 15 entradas → 32 → 16 → 1 (1057 parámetros), umbral 0.7 en 2 cuadros, y 6 escenas de
  prueba con su probabilidad y lo que decide.
- **Política PPO:** 192 entradas → 128 → 128 → 10 acciones (42 506 parámetros del actor) y lo que decide en una
  misión de ejemplo.

Las imágenes quedan en `08_EVIDENCIA_Y_DIAGRAMAS\redes\` (diagramas de las redes, histogramas de pesos y las
probabilidades por acción). Abrirlas con doble clic.

Código para mostrar si lo pide:
- Decisor: `03_SIMULACION_RL\minimo_tesis\decisor_ia.py` (función `predecir_json`: lo que corre en la Jetson).
- Mundo y recompensas: `03_SIMULACION_RL\entorno.py` (constantes `R_*` cerca de la línea 465).
- Entrenamiento: `03_SIMULACION_RL\entrenar_master.py` (PPO cerca de la línea 197).

## Minuto 6-8 · La IA de refuerzo (el plus), con honestidad

1. En el visor: **"Nivel 4 · Misión completa · en vivo"** y **"Misión completa (despegue)"**.
2. Decir la verdad que muestra `ver_redes.py`: *"La red PPO todavía decide casi al azar (su acción preferida tiene
   17 % de probabilidad; al azar sería 10 %). Los buenos números vienen de las reglas deterministas alrededor. Ya
   tenemos el diagnóstico y el plan para la V17."* (`docs/PLAN_V17_REFUERZO.md`, cuando esté.)
3. Gráfica: `08_EVIDENCIA_Y_DIAGRAMAS\redes\ppo_probabilidades.png`.

## Minuto 8-9 · Las reglas duras están probadas

```
cd 03_SIMULACION_RL
.venv\Scripts\python.exe -m unittest tests.test_reglas_duras -v
```
Cada línea es una regla verificada: gimbal nunca por debajo de −45° aunque se le ordene −120°, geocerca, búsqueda
determinista, humano en el lazo, árbitro solo ante amenaza real.

## Minuto 9-10 · Dónde está cada cosa

Abrir `GUIA_DE_ARCHIVOS.md`: carpetas 01 a 08, qué va a la Jetson y qué corre en el PC. El estado del día está en
`docs\ESTADO.md`.

## Si algo falla

| Síntoma | Qué hacer |
|---|---|
| El visor no abre | Cerrar la ventana negra "Servidor del visor" y volver a abrir `ABRIR_VISOR.bat` |
| `No module named ...` | Se está usando otro Python: escribir siempre `.venv\Scripts\python.exe` |
| `ver_redes.py` no encuentra un archivo | Ejecutarlo desde `Dron-IA-Proyecto`, no desde la 03 |
