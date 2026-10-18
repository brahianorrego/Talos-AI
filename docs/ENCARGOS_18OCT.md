# Encargos del Arquitecto · 18 de octubre

Pedido del Coordinador: avanzar a fondo domingo y lunes. Cada sesión escribe solo en su carpeta, sin `git push`.

## 1. Hardware y variantes (`05_HARDWARE_Y_VARIANTES/`)

La variante recomendada es la **C** (D-055), pero sus piezas están incompletas: hay soporte para el TF03 al chasis y para
la cámara al piso, pero **no hay soporte del TF-Luna para el pod de la BaseCam**; el que existe es para el pan-tilt (D).

1. **Pieza de la variante C: soporte del TF-Luna en el pod de la BaseCam.** Abrazadera coaxial con la cámara USB, que no
   haga palanca sobre el pitch, con salida y alivio para el cable fino. `.scad` + `.stl`, comprobada como las demás
   (compila, un solo sólido) y con su peso estimado. Anotar en `ESTADO_IMPRESION.md` lo que no se puede verificar sin el
   pod en la mano.
2. **Calibración del servo de la variante D** (revisión del 17-oct, punto 8): procedimiento en banco, paso a paso, en
   `GUIA_PARA_BRAHIAN.md`. Con PWM 1000 µs el servo debe ir a −45° y con 1667 µs a +15° (`pwm = 1500 + θ·500/45`). Si no
   coincide, se ajustan los parámetros del servo en la Pixhawk (`SERVOx_MIN/MAX/TRIM`), **nunca la fórmula**.
3. **Comprobar que la simulación entrena con los valores de C y D** (`GIMBAL_TIPO = "mixto"`). Extender
   `validar_variantes.py` para que **lea** (sin escribir) las constantes de `03_SIMULACION_RL/entorno.py` y `control.py`
   con la tabla de equivalencias de `docs/PROGRESO_V17.md` ("Variantes de hardware → constantes del entorno"), y diga,
   para C y D, qué valor del JSON no coincide con el del entorno. Ejemplos: velocidad y retardo del servo, alcance del
   TF-Luna, TF03 a −3° (`TF03_PITCH_V17`). Las diferencias se las paso yo a Simulación V17; no se cambia `03_`.
4. **Peso y centro de gravedad de C y D**, con pesos de hoja de datos marcados "estimado" mientras la parte física no
   pese (pedido 2 de `docs/PEDIDOS_A_LA_PARTE_FISICA.md`): cuánto se mueve el centro de gravedad con el TF03 en la nariz.
5. **Alcance del TF-Luna según el color del panel**: una tabla de alcance por reflectividad (hoja de datos), para fijar
   `LUNA_MAX` cuando Brahian diga de qué color son los paneles.

## 2. Simulación V17 (`03_SIMULACION_RL/`)

1. **Repeticiones para Unreal (D-065):** una herramienta pequeña que corra partidas de la cancha V17 con los paneles
   reales (D-066) y una política dada, y guarde en `03_SIMULACION_RL/repeticiones_v17/` (fuera de Git: pesan ~6 MB cada
   una) **una partida de cada tipo**:
   - el ladrón se rinde;
   - se esconde tras una V y el dron lo re-encuentra subiendo;
   - salta para agarrar el dron;
   - un civil curioso que mira o graba;
   - cambia de V (regla L3).

   Mismo formato que `salida_*/replay_v17.json`, con un `LEEME.md` que diga qué es cada una, con qué modelo y con qué
   semilla. Ahora con la V17.2 de 50 M; cuando haya una política mejor, se graban de nuevo.
2. Al terminar la V17.3 de 10 M, medirla con las 512 partidas contra B0-B3 **con los paneles reales** y avisarle al
   Arquitecto. No lanzar la siguiente corrida hasta que el Arquitecto la revise con el agente `supervisor-rl`.

## 3. Visor (`04_VISOR_Y_MOTOR_GRAFICO/`)

- El contrato de `foto()` ya trae todo lo que pide `PLAN_UNREAL.md` §4. Por persona: `pos`, `pt`, `mira`, `civ`,
  `graba` y `alto`. En el cuadro: `salto` (fase, altura y `mano`), `cmd`, `arb`, `z_v17`, `alt_obj` y `cam_piso`. Además,
  `paneles` = [ax, ay, bx, by, alto]. Verificado en `salida_v17_2/replay_v17.json` (3 001 cuadros, `dt` = 0.1 s).
- Para `importar_repeticion.py` puedes empezar ya con `03_SIMULACION_RL/salida_v17_2/replay_v17.json` (es de solo
  lectura: no lo muevas). Las repeticiones escogidas llegan a `03_SIMULACION_RL/repeticiones_v17/` (encargo 2.1).
- Ojo: en las repeticiones de la V17.2 los paneles son los viejos (1.0 m). Las de `repeticiones_v17/` traerán los
  reales (1.5 × 2.2-2.3 m).
