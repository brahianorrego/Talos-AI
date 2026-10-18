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
5. **Entrenando (17-oct, 09:05):** la corrida "todo" de 10 M pasos (~50 min), aprobada por Brahian vía el Supervisor,
   para ver si el colapso a "quedarse" sigue. El de 50 M y las otras 6 corridas esperan a que Brahian decida la M1.
6. **Lo único que se separa de "quedarse" es SUBIR**: racha ≥ 30 s 61.9 % contra 51.8 % (ver "Botones fijos").

## Entrenamiento en marcha (17-oct)

- **Comando** (en la pestaña "V17 todo 10M" del panel Terminal, desde `03_SIMULACION_RL`), inicio **2026-10-17 09:05**:
  `.venv\Scripts\python.exe -u entrenar_master.py --pasos 1e7 --envs 512 --semilla 17 --repeticiones 5 --salida salida_v17_todo --dir-master modelos_v17_todo --dir-modelos modelos_v17_todo *> modelos_v17_todo.log`
- **Carpetas:** `modelos_v17_todo\` (checkpoints cada 1 M, `ultimo.zip`), `salida_v17_todo\` (métricas y repeticiones). No
  toca `modelos_v15`.
- **Avance:** `modelos_v17_todo.log` (en UTF-16, lo escribe PowerShell; se abre bien con el Bloc de notas): una línea `it …`
  por iteración con pasos, pasos/s y entropía. Va a ~3 300 pasos/s: termina hacia las 10:00.
- **Detener:** Ctrl+C en esa pestaña. **Medirlo al terminar:**
  `.venv\Scripts\python.exe herramientas\medir_ia_aporta.py v17 --pol b0,modelos_v17_todo\ultimo.zip --n 512 --salida informes\v17_todo_10M.json`
- Otra forma de lanzar el entrenamiento principal (cuando se decida): doble clic en `03_SIMULACION_RL\LANZAR_V17.bat`.

## Botones fijos (pedido del Arquitecto, 17-oct)

La red reemplazada por **un solo botón siempre**, mismas 512 partidas y semilla que la línea base
(`informes/v17/fijo_<botón>.json`). Margen de error ±4.3 puntos en la racha ≥ 30 s. Un botón no permitido en ese paso se
toma como QUEDARSE (por eso BAJAR, siempre prohibido a la altura segura, da exactamente lo mismo que QUEDARSE).

| Botón fijo | Racha ≥ 30 s | M1 60 s | Vista total (s) | Racha media (s) | M2 ≤ 10 s | Re-adq. (s) | M3 rendición | Alcanzado | Decide en % del FIJADO |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| QUEDARSE (= B0) | 51.8 % | 1.2 % | 108.9 | 31.4 | 76.2 % | 6.6 | 15.6 % | 0 % | 46 % |
| RODEAR_IZQ | 49.0 % | 0.2 % | 110.6 | 31.3 | 76.6 % | 6.5 | 14.6 % | 0 % | 48 % |
| RODEAR_DER | 54.7 % | 0.2 % | 113.3 | 31.6 | 77.1 % | 6.4 | 13.3 % | 0.2 % | 48 % |
| ACERCARSE | 42.6 % | 0.4 % | 106.3 | 28.9 | 77.1 % | 6.5 | 12.9 % | 0.2 % | 39 % |
| ALEJARSE | 53.3 % | 0.8 % | 108.9 | 31.7 | 75.9 % | 6.5 | 16.2 % | 0.2 % | 46 % |
| **SUBIR** (a 5.5 m) | **61.9 %** | 0 % | 100.9 | 33.9 | **83.4 %** | **5.1** | **24.4 %** | 0.2 % | 65 % |
| BAJAR | 51.8 % | 1.2 % | 108.9 | 31.4 | 76.2 % | 6.6 | 15.6 % | 0 % | 46 % |

Choques con peatones, paneles y geocerca: 0 en todas; gimbal siempre dentro de −45..+15°.

- **SUBIR sí cambia algo, fuera del ruido:** +10 puntos de racha ≥ 30 s, M2 de 76 a 83 %, re-adquisición de 6.6 a 5.1 s y
  rendición de 16 a 24 %; ve por encima de las V. A cambio, menos vista total (101 s contra 109): desde 5.5 m lo pierde más
  veces por el borde de la imagen, pero lo recupera antes. ACERCARSE empeora (−9 puntos). Rodear y alejarse no se separan.
- **Cuánto decide de verdad la red:** en el 46 % del tiempo FIJADO (con QUEDARSE; el resto lo tiene oculto, en la memoria
  del tracker o con una maniobra), ~21 % de todo el tiempo de la partida.
- **Cuánto dura cada vez que lo ve:** mediana **0.5 s**, media 1.1 s seguidos con `visto` encendido. Ojo: no es el tiempo
  hasta que se esconde, porque `visto` parpadea por las pérdidas de detección de YOLO de un cuadro; lo que dura de verdad
  a la vista se ve mejor en la racha media del contador (~31 s, que tolera parpadeos).
- **Conclusión:** una palanca sí alcanza (la altura). Entonces el colapso a QUEDARSE del humo no se explica porque "no hay
  nada que ganar": SUBIR gana. Lo más probable es que la recompensa no lo pague. La recompensa por paso premia "a la vista"
  y la distancia de 3.5-5 m, y SUBIR baja la vista total. Además, con SUBIR la cámara cae fuera del rango del gimbal cuando
  está cerca, y eso tiene multa (R6).

## V17.1 · M1 = racha ≥ 30 s y recompensa alineada (D-059 A, D-061, D-064; 17-oct)

**Nombres (D-061):** la corrida "todo" de 10 M con la recompensa original es la **V17.0** (`modelos_v17_todo`); la de esta
sección es la **V17.1**; cada arreglo siguiente, V17.2, …

**Cambios** (`entorno.py`, todo solo en la cancha; la V15 y la V16 no cambian):
- **M1 = racha de 30 s seguidos** con el ladrón a la vista y el ID correcto (`RACHA_M1_V17`; `m1` en `medir_ia_aporta`). Los
  60 s se siguen reportando (`custodia60`).
- **Recompensa alineada con M1:** bono `R_RACHA_V17 = 10` al completar la racha (una vez por racha) y potencial
  `K_RACHA_V17 = 3` × racha/30 (fórmula de Ng; al perder la racha el potencial cae y eso cobra).
- **R6 apagada en la cancha** (`R_SOBREVUELO_V17 = R_ANGULO_GMB_V17 = 0`): con ella, "siempre SUBIR" cobraba menos que
  "siempre QUEDARSE" aunque tenía más M1. El punto ciego y el ángulo los cuidan reglas (reflejo de punto ciego, barrera
  de −45°).
- **D-064: TF03 a −3° en la V17** (`TF03_PITCH_V17`): el 360° de entrada mapea el 49 % de las V (antes 24 %,
  `v171_base_b0.json`, `mapeo_entrada`).
- **B3 = siempre SUBIR** en `medir_ia_aporta.py` (`--pol b3`), más el retorno de cada partida y su desglose (`retorno`,
  `retorno_comp`).

**¿SUBIR cobra más que QUEDARSE?** Retorno medio por partida (256 partidas, `informes/v17/v171_rec_*.json` y
`v171_base_b*.json`):

| Recompensa | QUEDARSE | SUBIR | ¿SUBIR > QUEDARSE? |
|---|---:|---:|---|
| Bono 5, con R6 | 8.9 | 2.6 | No (la multa de ángulo: −18.3 contra −6.8) |
| Bono 5, sin multa de ángulo | 14.3 | 10.5 | No |
| Bono 10, sin multa de ángulo | 17.6 | 14.5 | No (queda la de sobrevuelo) |
| **Bono 10, sin R6 (V17.1)** | **20.4** | **24.1** | **Sí** |
| Bono 10, sin R6, potencial ×2 | 4.3 | 5.6 | Sí, pero por poco (descartado) |

**Línea base V17.1** (512 partidas, TF03 −3°, `informes/v17/v171_base_b*.json`; medida con bono 5 y R6, pero esas
constantes no cambian lo que hace una política fija, solo lo que cobra):

| | B0 QUEDARSE | B1 azar | B2 posicionamiento | B3 SUBIR |
|---|---:|---:|---:|---:|
| **M1 racha ≥ 30 s** | 47.5 % | 51.0 % | 51.8 % | **60.0 %** |
| Racha ≥ 60 s | 1.2 % | 0 % | 0.2 % | 0 % |
| Vista total (s) | 109.9 | 103.8 | 108.4 | 103.2 |
| M2 ≤ 10 s | 76.2 % | 78.6 % | 77.2 % | 83.7 % |
| M3 rendición | 11.5 % | 17.4 % | 15.6 % | 25.6 % |
| Alcanzado | 0.2 % | 0.2 % | 0 % | 0 % |

La IA tiene que superar a las cuatro, o sea a B3: **60.0 % + 5 puntos**.

### V17.0 (control, recompensa original) · resultado a los 10 M

Terminó a las 10:55 del 17-oct. Medida en el entorno V17.1 (mismas 512 partidas que B0-B3; `informes/v17/v170_10M.json`,
checkpoint `dron_master_9999360_steps.zip`): **M1 47.5 %, igual que B0; QUEDARSE en el 100 % de las decisiones**
(probabilidad de la preferida 1.000, entropía 0.002). El colapso del humo se confirmó a 10 M: con la recompensa original la
red aprende a no moverse.

### V17.1 en marcha

- **Inicio 2026-10-17 19:02** (la sesión estuvo detenida entre las 11:00 y las 19:00 por el límite de uso), pestaña
  "V17 todo 10M" del panel Terminal, desde `03_SIMULACION_RL`:
  `.venv\Scripts\python.exe -u entrenar_master.py --pasos 1e7 --envs 512 --semilla 17 --repeticiones 5 --salida salida_v17_1 --dir-master modelos_v17_1 --dir-modelos modelos_v17_1 *> modelos_v17_1.log`
- Carpetas `modelos_v17_1\` y `salida_v17_1\`. Detener: Ctrl+C en la pestaña. Al terminar, `entrenar_master.py` ahora
  guarda también `ultimo.zip` (antes solo cada 20 iteraciones).
- Medirla: `.venv\Scripts\python.exe herramientas\medir_ia_aporta.py v17 --pol modelos_v17_1\ultimo.zip --n 512 --salida informes\v17\v171_10M.json`
- D-062: si supera a B0 y a B3 en M1 (B3 = 60.0 %), o va claramente en subida, sigue la de 50 M.

### D-063 · Altura segura con el error del barómetro

B0, 256 partidas (`informes/v17/d063_*.json`). "Real bajo 3.30 m" = fracción del tiempo con alguien real a menos de 8 m y
el dron, en su altura REAL, por debajo de 3.25 m.

| Opción | Real bajo 3.30 m | M1 | M2 ≤ 10 s | Alcanzado |
|---|---:|---:|---:|---:|
| Sin margen (barómetro) | 13.6 % | 55.1 % | 76.5 % | 0.8 % |
| Margen 0.3 m | 2.9 % | 47.7 % | 72.3 % | 0.4 % |
| **Margen 0.5 m (queda)** | **0.5 %** | 53.5 % | 71.5 % | 0.4 % |
| Altímetro por LiDAR al piso (`ALTIMETRO="luna"`) | 0.4 % | 47.7 % | 84.3 % | 0 % |

Criterio de D-063: ≤ 2 % sin empeorar M1. Cumple el margen de 0.5 m (M1 dentro del ruido de ±6 puntos). El altímetro por
LiDAR también queda bajo el 2 %, pero baja M1 en 7 puntos. Queda **`MARGEN_BARO_V17 = 0.5`** para la V17.2 en adelante.
La V17.1 ya había arrancado sin margen, así que se mide igual que B0-B3, que tampoco lo tenían.

## Contrato `foto()` · campos nuevos de la V17 (para el visor)

Además de los de la V16 (`docs/PROGRESO_V16.md` de la rama `v16-simulacion`):

| Campo | Qué es |
|---|---|
| `v17` | `true` si la partida es la cancha V17 |
| `fase` | `"zona"` (la partida de entrenamiento empieza en la activación; tránsito y activación son de la misión del visor) |
| `z_v17` | Altura (m) que pide la red con SUBIR / BAJAR (3.30 a 5.5) |
| `cmd` | `[vx, vy, vz, guiñada, gimbal, modo, quién manda]`: velocidades en m/s (mundo) que se mandan a la Pixhawk, tasa de guiñada en °/s, ángulo pedido al gimbal en °, nombre del estado (`NOMBRE_ESTADO`) y `"red"`, `"regla"` o `"arbitro"` (el piloto no manda dentro de la zona de IA) |
| `arb` | Motivo del árbitro: `""` (nada), `"reflejo_ataque"`, `"evadiendo"`, `"amenaza"`, `"punto_ciego"`, `"perimetro"` |

Prueba: `tests/test_v17.py`, `TestFotoVisor` (salen en cada cuadro).

## Opciones para Brahian (no se cambió nada de esto)

| Opción | Qué cambia | Costo | Recomendación |
|---|---|---|---|
| A. M1 = racha ≥ 30 s | Solo la medida del criterio "la IA aporta" | Nada de código (ya se mide: `custodia30`) | **Sí.** Es la única que separa: B0 51.8 %, SUBIR fijo 61.9 % |
| B. Recompensa por racha (el contador) en vez de por paso a la vista | Paga mantenerlo, no solo verlo en el cuadro | ~1 h + pruebas + re-medir; cambia lo que aprende | **Sí, junto con A**: hoy la red aprende que moverse baja la vista por paso aunque suba la custodia |
| C. Que la búsqueda no reinicie el contador al segundo de perderlo (por ejemplo, pausarlo hasta 4 s como en RECONFIRMAR) | Más rachas largas para todos | Toca la regla 3 (búsqueda determinista): la decide Brahian | Solo si A y B no alcanzan; sube la vara de B0 sin que la IA haga nada |
| D. Ladrón más visible (más tiempo fuera del escondite) | Escenario más fácil | Toca el ladrón; hay que re-medir todo | No por ahora: SUBIR ya muestra que hay margen |
| E. Quitar o bajar la multa del ángulo del gimbal (R6) en la V17 | Deja de castigar mirar desde arriba | `--set R_ANGULO_GMB=0`, ya existe | Medirla en las corridas de 5.2 (es la corrida "sin R6") |

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

## Variantes de hardware → constantes del entorno (pedido del Arquitecto)

Claves de `05_HARDWARE_Y_VARIANTES/config_sim/variante_A..F.json` (solo leídas) y su constante en `03_SIMULACION_RL`.
**D-055/D-056 (aprobadas por Brahian):** la V17 entrena con `GIMBAL_TIPO = "mixto"`, LiDAR como la variante C (TF03 al chasis
a +1°, TF-Luna en el gimbal, 3-8 m) y cámara al piso activa, sin pan. **Son exactamente los valores por defecto de la V16
que ya usa la V17**: no hubo que cambiar nada.

| Clave del JSON | Constante del entorno | Nota |
|---|---|---|
| `GIMBAL_TIPO` / `GIMBAL_TIPO_EQUIVALENTE_V16` | `entorno.GIMBAL_TIPO` ("basecam", "servo", "mixto") | Usar la equivalente V16 |
| `GIMBAL_MIN`, `GIMBAL_MAX`, `GIMBAL_TOPE_FISICO_MIN` | `GIMBAL_MIN`, `GIMBAL_MAX`; `control.GimbalBaseCam.MIN/MAX` | Regla dura: −45..+15, no se cambia |
| `GIMBAL_VEL_DPS` | `GIMBAL_VEL` (lógica) y `control.GimbalBaseCam.VEL_MAX` (BaseCam), `control.GimbalMixto.SERVO_VEL` (servo) | |
| `GIMBAL_RETARDO_S` | `control.GimbalMixto.RETARDO` (servo); BaseCam: `control.GimbalBaseCam.TAU_ESTAB` | |
| `GIMBAL_ZONA_MUERTA_DEG` | `control.GimbalMixto.SERVO_BANDA` | Solo servo |
| `GIMBAL_ESTABILIZA`, `GIMBAL_TOPES_MECANICOS` | implícitos en el tipo (BaseCam inercial / servo con topes) | **Falta** como constante propia |
| `CAM_PRINCIPAL_HFOV`, `CAM_PRINCIPAL_VFOV` | `HFOV`, `VFOV` | |
| `CAM_PRINCIPAL_TIPO`, `CAM_PRINCIPAL_MONTAJE` | — | **Falta** (siempre USB en el gimbal) |
| `CAM_PISO_HFOV`, `CAM_PISO_VFOV`, `CAM_PISO_PITCH` | igual nombre | |
| `CAM_PISO_ACTIVA` | — | **Falta**: hoy siempre activa en V16/V17 |
| `CAM_PISO_EJE_LARGO`, `CAM_PISO_PUERTO` | — | No afectan la simulación |
| `CAM_FRONTAL_ANCHA_*` | — | **Falta** (no hay cámara frontal ancha en el entorno) |
| `LIDAR_TF03_PITCH_DEG` | `TF03_PITCH` | |
| `LIDAR_TF03_ALCANCE_M` | `LIDAR_MAX` | |
| `LIDAR_TF03_MONTAJE`, `LIDAR_TF03_SIGUE_GIMBAL` | implícito: V16+ al chasis, V15 en el gimbal (por nivel) | **Falta** como constante |
| `LIDAR_DESCARTE_SUELO_CON_ACTITUD` | implícito (siempre en V16+) | **Falta** como constante |
| `LIDAR_LUNA_ALCANCE_M` | `LUNA_MAX` | |
| `LIDAR_LUNA_MONTAJE` | implícito (gimbal) | **Falta** |
| `LIDAR_LUNA_PISO_ALTIMETRO` | `ALTIMETRO` ("baro" / "luna") | false → "baro" |
| `PAN_*` | — | **Falta** (sin pan; D-056 lo deja bloqueado) |
| `YOLO_FPS_PRINCIPAL`, `YOLO_FPS_PISO` | — | **Falta**: el entorno decide a 10 Hz (`DT = 0.1`) |
| `MASA_SUMA_G`, `MASA_QUITA_G` | — | **Falta** (la dinámica no depende de la masa) |

## Pendiente

- **Decisión del Arquitecto/Brahian:** qué M1 usar (racha ≥ 30 s, custodia de la V16 o ablandar al ladrón) antes de lanzar
  las corridas: con la M1 actual no se puede decidir ninguna regla de 5.2.
- Para la sesión de hardware: TF03 inclinado −3° duplica el mapeo de los paneles de 2 m (tabla de E7).
- `mision.py` (misión con piloto y el mínimo, para el visor) sigue con los 10 botones de antes: no se graba con la red de
  7. Las fases tránsito → activación → zona son del encargo del visor (plan 7.2); `foto()` ya trae `v17`, `fase` y `z_v17`.
- La política V17 para la Jetson (`dron_politica_v17.json`) tiene 195 entradas y 7 botones: la Jetson no tiene ese código.
