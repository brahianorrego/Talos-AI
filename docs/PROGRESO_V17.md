# Progreso de la V17

Sesión **Simulación V17** (dueña de `03_SIMULACION_RL/`), encargo `docs/ENCARGO_SIMULACION_V17.md`, plan
`docs/PLAN_V17_REFUERZO.md`. Lo más reciente va abajo. Toda cifra lleva el archivo de donde sale.

## En cinco líneas (para Brahian)

1. El código de la V16 ya está aquí y la cancha de la V17 está programada: zona de 30 × 30 m, dos V de paneles de 2 m,
   1 ladrón y 1 civil; la partida empieza cuando el piloto activa la IA.
2. La red ahora tiene **7 botones que sí cambian algo** (quedarse, rodear por la izquierda o la derecha, acercarse,
   alejarse, subir, bajar). La esquiva ante un peligro la decide siempre el árbitro (regla), no la red.
3. Entrena con **MaskablePPO**: en los pasos donde la red no decide solo le queda "quedarse", así que no aprende ruido.
   La prueba de humo corre a ~3 600 pasos por segundo (casi 3 veces la V15).
4. **Medido: con la custodia como la define el plan (60 s seguidos a la vista), todas las líneas base dan ~1 %**: "solo
   reglas", azar y la regla de posicionamiento empatan. La cancha, con el ladrón escondiéndose detrás de las V, nunca deja
   60 s seguidos. Hay que decidir con qué número se mide (le pregunté al Arquitecto; ver abajo).
5. **Nada se entrenó** más allá de pruebas de humo. Los comandos de las corridas de 10 M están al final.

## Paso 1 · E1 · Código de la V16 (17-oct)

- Se trajo lo que cambió de `v15-curriculo` a `origin/v16-simulacion` (repo viejo, sin tocarlo): `entorno.py`, `control.py`,
  `entrenar_master.py`, `herramientas/evaluar_politica.py`, `medir_v16.py`, `politica_json.py`, `analizar_recompensa_v16.py`,
  dos informes y las pruebas. Copias previas en `_archivo_versiones/codigo/`: `entorno_v15b.py`, `control_v15.py`,
  `entrenar_master_v15b.py`, `evaluar_politica_v15.py` (idénticas a las de la rama) y `entrenar_master_v16.py` (antes de
  la V17).
- De las 118 pruebas de la rama, en el PC fallaban 2 (en la nube no se veían):
  1. **Regla dura "humano en el lazo"** (`test_reglas_duras`): cuando el operador respondía "sigue igual" a un
     RECONFIRMAR, el tracker no quedaba amarrado y en ese mismo cuadro saltaba al civil. **Se arregló el código, no la
     prueba**: "sigue igual" también amarra el tracker `T_CLIC_FIRME` s, como el "sí es" y el "no es" (`entorno.py`, línea
     del `t_clic` en RECONFIRMAR). Comprobado con la V16 original más este cambio: la violación desaparece.
  2. `test_entorno.test_modelo_sb3_carga_y_decide` cargaba `modelos_master/base_v9.zip` (192 entradas) contra un entorno
     de 195: ahora le pasa las 192 primeras.

## Pasos 2-6 · La cancha, los botones, la máscara y la partida desde la activación (17-oct)

Todo en `entorno.py` como el "nivel" `NIVEL_V17 = 6`, que hereda la física, los sensores y la recompensa de la V16 (los
`== NIVEL_V16` de la V16 pasaron a `>= NIVEL_V16`). La V16 y la V15 no cambian (la arena de 25 m sigue en `ARENA`).

- **E6 · Cancha (D-051):** `ARENA_V17 = 15` (geocerca), dos V de 90° con alas de `ANCHO_PANEL_V17 = 1.0` m y alto al azar
  entre 1.9 y 2.2 m, vértices a 10 m, la V del sur abierta hacia donde entra el dron y la del norte al revés, ±2 m y ±20°
  por conjunto; 1 civil. El ladrón nace en cualquier lugar de la zona a 8 m o más del dron.
- **E5 · Desde la activación (D-053):** el dron empieza en el borde sur (`Y_ACTIVA_V17 = -12.5`), mirando a las V, en el
  360° de entrada.
- **E2 · 7 botones (D-049):** `CLASES_V17`. Con el objetivo fijado, a la vista y sin amenaza: RODEAR a 1.5 m/s de lado (la
  guiñada lo mantiene centrado), ACERCARSE / ALEJARSE hasta 3.5 / 6 m **según la distancia que mide el dron** (la
  medida por la caja de YOLO sobreestima ~1 m a 4-5 m), SUBIR / BAJAR cambian 0.5 m la altura pedida entre 3.30 y 5.5 m. El
  bloqueo frontal del LiDAR, la geocerca, las guardas de personas y el reflejo de punto ciego siguen mandando.
- **E3 · Evasión por regla:** en la cancha la maniobra la elige siempre el árbitro. Se encontró y corrigió un punto débil:
  con la persona justo al frente, la regla elegía izquierda o derecha por el signo de una medida con ruido y no llegaba a
  confirmar 3 cuadros seguidos; ahora mantiene el lado mientras dure la amenaza (solo en la V17).
- **E4 · Máscara (D-050):** `action_masks()`: sin decisión solo QUEDARSE; con decisión nunca un botón sin efecto o prohibido
  (BAJAR a la altura segura, SUBIR a 5.5 m, ACERCARSE ya a 3.5 m, ALEJARSE ya a 6 m). `sb3-contrib==2.9.0` (la de SB3 2.9.0)
  instalado en el `.venv`. La red decide en ~21 % de los pasos (`informes/v17_linea_base.json`, `frac_decide`).
- **Recompensa:** la de la V16 (R1 coberturas, R2 lado de escape, R5 sacudida, R6 sobrevuelo y ángulo) más R3 (bono de
  entropía 0.003, `--ent`) y R4 (re-adquisición ±2, `R_READQ_V17`). La suavidad se mide sobre las consignas que da la red
  (adelante, de lado, altura pedida). En la V17 no se cobra el "esfuerzo" de volar parejo (ver la prueba de humo).
- **Pruebas nuevas** (`tests/test_v17.py`, 15): escenario, geocerca de 15 m, entrada completa, cada botón cambia algo,
  **la evasión ocurre sea cual sea el botón**, máscara, B2, reglas duras en la cancha con botones al azar (gimbal, altura
  segura, búsqueda determinista, árbitro solo ante amenaza, humano en el lazo), reglas del ladrón encendidas y apagadas, y
  MaskablePPO aprendiendo unos pasos.

## Paso 7 · E7 · Ajustes por paneles de 2 m (17-oct)

B0, 128 partidas de 5 min, todas las reglas del ladrón (`informes/v17/e7_*.json`). "Mapeo" = fracción de las 2 V que el
LiDAR dejó en el mapa al terminar el 360° de entrada.

| Variante | Mapeo | Racha media (s) | Alcanzado |
|---|---:|---:|---:|
| Como la V16 (la vuelta se corta al ver a alguien) | 5 % | 31.3 | 0 % |
| Vuelta completa, 2.0 m, TF03 +1° | 13 % | 30.1 | 0 % |
| **Vuelta completa, 1.8 m** (queda) | 25 % | 32.2 | 0 % |
| Vuelta completa, 2.0 m, TF03 −3° | 47 % | 31.5 | 0 % |
| Vuelta completa, 1.8 m, TF03 −3° | 52 % | 31.8 | 0 % |
| Vuelta a 3.3 m, TF03 −6° | 44 % | 28.2 | 0.8 % |

- **Hallazgo:** desde el borde sur casi siempre se ve a alguien al empezar y la vuelta de entrada se cortaba en el primer
  cuadro. En la V17 la vuelta se termina antes de verificar (`ENTRADA_COMPLETA_V17`) y se vuela a **1.8 m**
  (`Z_V17_ENTRADA`, el mínimo `Z_MIN`; solo sin nadie conocido a menos de 8 m). El TF03 a +1° pasa por encima de paneles de
  2 m: **inclinarlo −3° duplicaría el mapeo (25 → 52 %)**. Es un cambio de montaje: queda como propuesta para la sesión de
  hardware (no se cambió `TF03_PITCH`).
- **Búsqueda tras el panel:** mirar el "muro de canto" desde 4.5 m o saltarse ese paso no cambia nada medible (racha ≥30 s
  51.6 / 48.4 %, `e7_canto45.json`, `e7_sincanto.json`; misma fila con canto a 6 m en la línea base: 51.8 %). Se dejó como
  estaba, con `CANTO_V17` y `A_CANTO_V17` para cambiarlo.
- **Alturas bajas:** el tiempo bajo 3.30 m con alguien real a menos de 8 m es 14.1 % en altura REAL pero 2.0 % en la
  altura que se le PIDE a la Pixhawk (B0, `informes/v17_linea_base.json`): casi todo es el error del barómetro (decisión
  abierta de la V16, altímetro). Las alturas de inspección y tránsito quedan como en la V16 (`Z_V17_INSPECCION`,
  `Z_V17_TRANSITO`; `nan` = siempre a la altura segura).

## Paso 8 · Línea base B0 / B1 / B2 (17-oct)

512 partidas de 5 min, misma semilla, todas las reglas del ladrón (`informes/v17_linea_base.json`). Margen de error
(95 %): ±4.3 puntos cerca de 50 %, ±1 cerca de 0 %.

| | B0 solo reglas | B1 azar | B2 posicionamiento |
|---|---:|---:|---:|
| **M1 custodia (60 s seguidos)** | **1.2 %** | **0.6 %** | **1.0 %** |
| Racha ≥ 30 s | 51.8 % | 52.0 % | 52.7 % |
| Custodia de la V16 (rendición o 60 s de vista acumulada) | 96.5 % | 95.5 % | 96.5 % |
| Racha media (s) | 31.4 | 31.6 | 32.2 |
| M2 pérdidas recuperadas en ≤ 10 s | 76.2 % | 78.5 % | 77.8 % |
| Tiempo medio de re-adquisición (s) | 6.6 | 6.0 | 6.3 |
| M3 rendición | 15.6 % | 18.6 % | 17.2 % |
| Alcanzado / choque con peatón / panel / geocerca | 0 / 0 / 0 / 0 % | 0 / 0 / 0 / 0 % | 0.2 / 0 / 0 / 0 % |
| Gimbal fuera de −45..+15° | 0 | 0 | 0 |
| Bajo 3.30 m con alguien a < 8 m (pedido / real) | 2.0 / 14.1 % | 0.7 / 6.9 % | 1.4 / 10.5 % |
| La red decide en | 21.1 % de los pasos | 23.3 % | 21.6 % |
| Botones (donde decide) | QUEDARSE 100 % | parejos | QUEDARSE 63 %, RODEAR 28 %, ACERCARSE 7 %, SUBIR 2 % |

**B0 no pasa del 80 %: no hubo que avisar por eso.** Lo contrario: con la M1 del plan las tres empatan en ~1 %, así que el
criterio "la IA aporta" (M1 ≥ B0 + 5 puntos) no puede medirse bien. La racha ≥ 30 s es la única de las tres que queda en la
ventana 20-80 % y discrimina. **Consulta enviada al Arquitecto** (17-oct): fijar M1 = racha ≥ 30 s, o la custodia de la V16
(satura en 96 %), o ablandar al ladrón. Que B2 empate con B0 dice además que, con la búsqueda determinista mandando a 1 s de
perderlo, moverse alrededor del ladrón casi no cambia nada en una regla simple: queda por ver si una red lo aprovecha mejor.

## Paso 8 (cont.) · Reglas del ladrón y del civil, una por una

Tabla completa y propuesta en `03_SIMULACION_RL/informes/v17_reglas_ladron.md` (B0 y B2, 128 partidas cada fila).
Resumen: **ninguna de L1-L4 ni C1 cambia la dificultad fuera del ruido**; L2 deja "alcanzado" en 0 %, L3 aparece en
~98 % de las partidas, L4 sube RECONFIRMAR de 4.3 a 5.5 por partida sin ningún cambio de ID sin detectar. Propuesta:
dejarlas todas encendidas (son realismo). Las constantes para apagarlas: `POSTURAS_V17`, `SALTO_V17`, `RULETA_V17`,
`ESCUDO_V17`, `CURIOSO_V17` (`--set NOMBRE=0`).

## Paso 9 · Corridas de la sección 5.2 (listas, SIN lanzar)

Prueba de humo (13 min, 512 entornos, 8 hilos, en una carpeta temporal): arranca de cero, guarda checkpoints, `ultimo.zip`,
`dron_politica_v17.json`, métricas y repeticiones (`replay_v17.json`); **~3 200-4 400 pasos/s** (la V15 hacía ~1 220).
Con eso: **10 M pasos ≈ 45-50 min, 50 M ≈ 4 h**. El "CUSTODIA ≥60s" que imprime el log es la de la V16 (vista acumulada).

**Hallazgo del humo (importante antes de gastar 6 h):** la red **colapsa a "siempre QUEDARSE"**. La primera versión lo hizo
en 1.3 M pasos y cobraba el "esfuerzo" de volar parejo; se quitó esa multa en la V17 y se repitió: igual colapsa a los 2.6 M
pasos (13 min). Medido con 128 partidas, ese modelo es idéntico a B0: QUEDARSE en 100 % de las decisiones, probabilidad de la
preferida 0.998 (`informes/v17/humo_2M.json`; log `informes/v17/humo_log.txt`). Es coherente con la línea base: si B0, B1 y
B2 empatan, moverse no paga nada y lo único que queda por aprender es no pagar las multas de suavidad. **Con la cancha y la
recompensa de hoy, las corridas de 10 M van a medir "QUEDARSE" siete veces.** Antes de lanzarlas hace falta que moverse
importe (por ejemplo, la decisión de la M1, que la búsqueda no reinicie el contador al segundo, o un ladrón que se deje ver
más tiempo); consultado al Arquitecto.

**Comandos** (desde `03_SIMULACION_RL`, solo con aprobación de Brahian o del Supervisor delegado). Todas juntas, una tras
otra (~6 h): `CORRIDAS_V17_RECOMPENSA.bat`. Una por una:

```
.venv\Scripts\python.exe -u entrenar_master.py --pasos 1e7 --envs 512 --semilla 17 --repeticiones 0 --salida salida_v17_todo --dir-master modelos_v17_todo --dir-modelos modelos_v17_todo
.venv\Scripts\python.exe -u entrenar_master.py --pasos 1e7 --envs 512 --semilla 17 --repeticiones 0 --salida salida_v17_sin_R1 --dir-master modelos_v17_sin_R1 --dir-modelos modelos_v17_sin_R1 --set K_COB=0
.venv\Scripts\python.exe -u entrenar_master.py --pasos 1e7 --envs 512 --semilla 17 --repeticiones 0 --salida salida_v17_sin_R2 --dir-master modelos_v17_sin_R2 --dir-modelos modelos_v17_sin_R2 --set K_ESC=0
.venv\Scripts\python.exe -u entrenar_master.py --pasos 1e7 --envs 512 --semilla 17 --repeticiones 0 --salida salida_v17_sin_R3 --dir-master modelos_v17_sin_R3 --dir-modelos modelos_v17_sin_R3 --ent 0.01
.venv\Scripts\python.exe -u entrenar_master.py --pasos 1e7 --envs 512 --semilla 17 --repeticiones 0 --salida salida_v17_sin_R4 --dir-master modelos_v17_sin_R4 --dir-modelos modelos_v17_sin_R4 --set R_READQ_V17=8
.venv\Scripts\python.exe -u entrenar_master.py --pasos 1e7 --envs 512 --semilla 17 --repeticiones 0 --salida salida_v17_sin_R5 --dir-master modelos_v17_sin_R5 --dir-modelos modelos_v17_sin_R5 --set K_JERK_V16=0
.venv\Scripts\python.exe -u entrenar_master.py --pasos 1e7 --envs 512 --semilla 17 --repeticiones 0 --salida salida_v17_sin_R6 --dir-master modelos_v17_sin_R6 --dir-modelos modelos_v17_sin_R6 --set R_SOBREVUELO=0 --set R_ANGULO_GMB=0
```

Opcional (E4, medir si transferir ayuda): la de "todo" con `--desde modelos_v15\ultimo.zip` (copia las capas ocultas de la
V15; la salida de 7 botones arranca nueva) en `modelos_v17_desde_v15`.

**Medir cada una** (512 partidas, ~15 min cada una):

```
.venv\Scripts\python.exe herramientas\medir_ia_aporta.py v17 --pol b0,modelos_v17_todo\ultimo.zip,modelos_v17_sin_R1\ultimo.zip --n 512 --salida informes\v17_recompensa_10M.json
```

**Entrenamiento principal** (después de decidir las reglas; regla de parada D-052 a los 50 M):

```
.venv\Scripts\python.exe -u entrenar_master.py --pasos 5e7 --envs 512 --salida salida_v17 --dir-master modelos_v17
```

## Pendiente

- **Decisión del Arquitecto/Brahian:** qué M1 usar (racha ≥ 30 s, custodia de la V16 o ablandar al ladrón) antes de lanzar
  las corridas: con la M1 actual no se puede decidir ninguna regla de 5.2.
- Para la sesión de hardware: TF03 inclinado −3° duplica el mapeo de los paneles de 2 m (tabla de E7).
- `mision.py` (misión con piloto y el mínimo, para el visor) sigue con los 10 botones de antes: no se graba con la red de
  7. Las fases tránsito → activación → zona son del encargo del visor (plan 7.2); `foto()` ya trae `v17`, `fase` y `z_v17`.
- La política V17 para la Jetson (`dron_politica_v17.json`) tiene 195 entradas y 7 botones: la Jetson no tiene ese código.
