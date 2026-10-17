# Cómo ayudar

¡Gracias por querer aportar! Este es un proyecto de grado real, con un dron real: cualquier ayuda bien hecha se nota.
Puedes escribir en español o en inglés.

## En qué hace falta ayuda

| Área | Qué hay que hacer | Nivel | Dónde |
|---|---|---|---|
| 🧠 IA de refuerzo | Averiguar por qué la política PPO no baja la entropía (decide casi al azar) y proponer cambios medibles | Avanzado | `03_SIMULACION_RL/entrenar_master.py`, `entorno.py` |
| 🛩️ Jetson | Portar el decisor del mínimo a la Jetson en "modo sombra" (`sistema_minimo.py`, paso 5) | Intermedio | `02_JETSON_A_BORDO/`, `03_SIMULACION_RL/minimo_tesis/decisor_ia.py` |
| 🎮 Visor 3D | Mejorar el visor three.js: personas animadas, cámara del dron realista, interfaz más limpia | Intermedio | `03_SIMULACION_RL/index.html`, `04_VISOR_Y_MOTOR_GRAFICO/` |
| 🔩 Hardware | Diseñar en OpenSCAD los soportes: pan-tilt de 2 servos, TF-Luna en el gimbal, TF03 fijo al chasis | Intermedio | `05_HARDWARE_Y_VARIANTES/` |
| 📊 Datos | Analizar los datos de campo del mínimo y compararlos con la simulación | Intermedio | `01_MINIMO_INDISPENSABLE/` |
| 📝 Documentación | Traducir el README al inglés, mejorar diagramas, corregir explicaciones | Principiante | Raíz y `docs/` |
| 🧪 Pruebas | Añadir pruebas a lo que no las tiene | Principiante | `03_SIMULACION_RL/tests/` |

## Antes de empezar

1. Lee [`COMO_FUNCIONA_EL_CODIGO.md`](COMO_FUNCIONA_EL_CODIGO.md) y la sección **Reglas duras** del [README](README.md).
2. Prepara el entorno (Windows o Linux, Python 3.14):
   ```
   cd 03_SIMULACION_RL
   python -m venv .venv
   .venv/bin/pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu      (en Windows: .venv\Scripts\pip)
   .venv/bin/pip install numpy==2.5.3 gymnasium==1.4.0 stable_baselines3==2.9.0 scikit-learn==1.9.1 matplotlib==3.11.2 scipy==1.18.1
   .venv/bin/python -m unittest discover -s tests
   ```
   Deben pasar las 88 pruebas.
3. Abre un *issue* contando qué quieres hacer antes de un cambio grande, para no duplicar trabajo.

## Reglas para los cambios

- **Las reglas duras no se relajan.** Gimbal entre −45° y +15°, geocerca, búsqueda determinista, humano en el lazo,
  árbitro de seguridad, la red no estabiliza. Si una prueba de `tests/test_reglas_duras.py` falla, se arregla el código,
  no la prueba.
- **`01_MINIMO_INDISPENSABLE/` está congelada**: es lo que se presenta al comité. Los cambios van en
  `03_SIMULACION_RL/minimo_tesis/` y se discuten antes.
- **Cifras con fuente:** si un número va en un documento, di de qué informe o script sale.
- **Nada privado:** ni IPs, ni usuarios, ni claves, ni fotos de personas sin permiso.
- Commits y textos en español (o inglés), en frases claras. Un cambio por *pull request*, con las pruebas pasando.

## Flujo

1. Haz un *fork* y crea una rama (`mejora-visor`, `jetson-modo-sombra`...).
2. Haz el cambio y corre las pruebas.
3. Abre el *pull request* explicando qué cambia, cómo lo probaste y qué números midió (si aplica).

## Seguridad

Este código mueve un dron con hélices. **Nunca** pruebes cambios de control en un dron real sin hélices retiradas
primero, en banco, y con alguien en la parada de emergencia.
