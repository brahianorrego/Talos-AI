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

**Resultado de la V17.1:** a los 1.3 M pasos ya elegía QUEDARSE en el 100 % (probabilidad 0.98, entropía 0.12; revisión
con 64 partidas). **Se detuvo a los ~2.4 M** (D-062: si colapsa, se ajusta la recompensa o la entropía).

## V17.2 · suavidad más liviana y más entropía (D-062; 17-oct)

**Por qué colapsaba:** con botones al azar (que es como empieza la red) la multa de suavidad costaba **−170 por partida**
(B1, `informes/v17/v171_base_b1.json`, componente `control`), contra ~+35 de la vista. Al principio del entrenamiento eso
aplasta todo y empuja a un solo botón; QUEDARSE es el único siempre permitido.

**Cambios:** `K_SUAVE_V17 = 0.1` (la multa por cambiar de botón y por la sacudida pesa la décima parte en la cancha),
bono de entropía `--ent 0.01` y `MARGEN_BARO_V17 = 0.5` (D-063). Retornos con botones fijos (128 partidas,
`informes/v17/v172_rec_*.json`): **QUEDARSE 19.1, azar −1.6 (suavidad −16), SUBIR 31.1**.

**En marcha desde 2026-10-17 19:39**, misma pestaña del Terminal:
`.venv\Scripts\python.exe -u entrenar_master.py --pasos 1e7 --envs 512 --semilla 17 --ent 0.01 --repeticiones 5 --salida salida_v17_2 --dir-master modelos_v17_2 --dir-modelos modelos_v17_2 *> modelos_v17_2.log`

A 1.3 M pasos (64 partidas) todavía elige QUEDARSE en modo determinista, pero **sin colapsar**: probabilidad de la
preferida 0.68 y entropía 0.98 (la V17.1 tenía 0.98 y 0.12 en el mismo punto).

**Línea base V17.2** (512 partidas, con el margen de 0.5 m; `informes/v17/v172_base_b*.json`): M1 B0 48.4 %, B1 45.9 %,
B2 53.1 %, **B3 56.2 %**. El tiempo real bajo 3.30 m con alguien a < 8 m queda en 0.4-0.5 % en todas.

**Resultado a los 10 M** (512 partidas, `informes/v17/v172_10M_det.json` y `_est.json`; terminó 21:17):

| | M1 | Vista (s) | M2 ≤ 10 s | Rendición | Alcanzado | Botones donde decide |
|---|---:|---:|---:|---:|---:|---|
| V17.2 determinista | 50.0 % | 100.9 | 71.5 % | 15.0 % | 0.4 % | SUBIR 52 %, BAJAR 48 % |
| V17.2 estocástica (como entrena) | 55.3 % | 100.2 | 73.4 % | 15.4 % | 0.2 % | SUBIR 42 %, BAJAR 37 %, QUEDARSE 19 % |
| B0 / B3 | 48.4 / 56.2 % | 102.6 / 96.0 | 70.3 / 78.8 % | 14.5 / 22.3 % | 0.2 / 0.2 % | — |

- **Ya no colapsa:** maneja la altura (SUBIR y BAJAR) en vez de quedarse quieta; probabilidad de la preferida 0.55, entropía
  0.95 de 1.95. A 1.3 M y 3.3 M elegía QUEDARSE (M1 37.5 % en 64 partidas).
- **Todavía no aporta:** empata con B0-B3 dentro del ruido (±4.3) y no le gana a "siempre SUBIR". Sube y baja a partes casi
  iguales, como si no supiera todavía cuándo conviene estar arriba.
- **Decisión (D-062, delegada al Supervisor/sesión):** se **continúa la V17.2 hasta 50 M** (es la única corrida que muestra
  aprendizaje) con la regla de parada de D-052: si a los 50 M no supera a B0 por ≥ 3 puntos **y** a B3, se para y se prueba
  la **V17.3** (`--gamma 0.995`, ya programado en `entrenar_master.py`: horizonte de ~20 s, porque la ventaja de estar
  arriba aparece en rachas de 30 s).

**V17.2 hasta 50 M, en marcha desde 2026-10-17 22:29** (misma pestaña del Terminal; termina hacia las 02:00):
`.venv\Scripts\python.exe -u entrenar_master.py --continuar --pasos 4e7 --envs 512 --semilla 17 --ent 0.01 --repeticiones 5 --salida salida_v17_2 --dir-master modelos_v17_2 --dir-modelos modelos_v17_2 *> modelos_v17_2_50M.log`
(con `--continuar`, `--pasos` son los pasos que se AGREGAN: 10 M + 40 M = 50 M). Medirla al terminar:
`.venv\Scripts\python.exe herramientas\medir_ia_aporta.py v17 --pol modelos_v17_2\ultimo.zip,modelos_v17_2\ultimo.zip-est --n 512 --salida informes\v17\v172_50M.json`
Los checkpoints de cada millón quedan en `modelos_v17_2\checkpoints\` para ver la curva.

### V17.2 a los 50 M (terminó 02:49 del 18-oct)

512 partidas en su misma cancha (paneles de 1.0 × 1.9-2.2 m, `--set ANCHO_PANEL_V17=1.0 --set ALTO_PANEL_V17=1.9,2.2`),
B0 y B3 re-medidos con las métricas de suavidad (`informes/v17/v172_50M_*.json`):

| | M1 | Vista (s) | M2 | Rendición | Altura recorrida (m/min) | Cambios de sentido de la altura (/min) | Jitter cabeceo / guiñada / gimbal (/s) | Botones donde decide |
|---|---:|---:|---:|---:|---:|---:|---|---|
| V17.2 determinista | **54.3 %** | 99.4 | 74.0 % | 22.5 % | 17.0 | 16.8 | 1.25 / 0.86 / 1.21 | QUEDARSE 71 %, SUBIR 17 %, BAJAR 13 % |
| V17.2 estocástica | 53.7 % | 100.5 | 73.3 % | 18.0 % | 17.0 | 42.7 | 1.26 / 0.86 / 1.22 | QUEDARSE 48 %, SUBIR 27 %, BAJAR 23 % |
| B0 QUEDARSE | 48.4 % | 102.6 | 70.3 % | 14.5 % | 9.7 | 0 | 1.19 / 0.76 / 1.18 | — |
| B3 SUBIR | 56.2 % | 96.0 | 78.8 % | 22.3 % | 13.5 | 8.2 | 1.34 / 0.99 / 1.20 | — |

- **Supera a B0 por 5.9 puntos** (cumple la regla de parada de D-052), **pero no supera a B3** (−1.9, dentro del ruido de
  ±4.3). La IA aprendió algo (de 50 % a los 10 M a 54 % a los 50 M), pero no más que una regla fija.
- **La altura es un vaivén:** 16.8 cambios de sentido por minuto, el doble que B3 (los de B3 son las vueltas a 3.30 m al
  perderlo). El jitter de cabeceo, guiñada y gimbal queda entre el de B0 y el de B3: la suavidad ×0.1 no lo empeoró.
- **Decisión (D-062):** se para la V17.2 y va la **V17.3**.

## V17.3 · paneles reales (D-066) y suavidad vertical (18-oct)

- **Paneles reales (D-066):** `ANCHO_PANEL_V17 = 1.5`, `ALTO_PANEL_V17 = (2.2, 2.3)`. **Qué corrida usó qué paneles:**
  V17.0, V17.1 y V17.2 con 1.0 m × 1.9-2.2 m; desde la V17.3, 1.5 m × 2.2-2.3 m. Prueba nueva:
  `test_v17.TestCancha.test_paneles_reales_d066`.
- **Suavidad vertical:** `K_SUAVE_Z_V17 = 0.5` (cabeceo y lado siguen en 0.1), por el vaivén de la V17.2.
- `--set` acepta pares (`--set ALTO_PANEL_V17=1.9,2.2`) para medir en la cancha vieja.
- Dos pruebas de botones dependían de la semilla (los paneles más grandes cambian cuántos números al azar se gastan al ubicar
  al ladrón); ahora usan más partidas y sacan las V de la zona. La comprobación de fondo (con 3 cuadros de amenaza real la
  esquiva arranca siempre, sea cual sea el botón) no cambió.
- **En marcha desde 2026-10-18 10:32** (pestaña del Terminal; la sesión estuvo pausada entre las 03:30 y las 10:30), desde cero:
  `.venv\Scripts\python.exe -u entrenar_master.py --pasos 1e7 --envs 512 --semilla 17 --ent 0.01 --repeticiones 5 --salida salida_v17_3 --dir-master modelos_v17_3 --dir-modelos modelos_v17_3 *> modelos_v17_3.log`
- **Línea base con los paneles reales** (512 partidas, `informes/v17/v173_base_b*.json`). **La cancha se vuelve mucho más
  difícil**: alas de 1.5 m y 2.2-2.3 m de alto tapan bastante más que 1.0 × 2.0 m.

  | | M1 | Vista total (s) | M2 ≤ 10 s | Rendición | Alcanzado | Mapeo de las V en la entrada |
  |---|---:|---:|---:|---:|---:|---:|
  | B0 QUEDARSE | 11.7 % | 84.6 | 60.0 % | 1.6 % | 0 % | 61 % |
  | B1 azar | 13.5 % | 82.6 | 61.6 % | 2.3 % | 0 % | 61 % |
  | B2 posicionamiento | 17.2 % | 86.2 | 60.0 % | 2.3 % | 0 % | 61 % |
  | **B3 SUBIR** | **24.6 %** | 87.3 | 68.3 % | 4.1 % | 0 % | 61 % |

  Ahora **subir dobla la custodia** de quedarse (+12.9 puntos; con los paneles viejos eran +7.8): la altura pesa mucho más
  y hay más espacio para que la IA aporte. B0 queda bajo el 20 % que el plan pedía para las reglas del ladrón (5.1), pero
  esta cancha es la real (D-066), así que no se ablanda.

- **La V17.3 colapsó** a QUEDARSE a los ~2-3 M pasos (64 partidas: probabilidad de la preferida 0.97, entropía 0.16;
  la V17.2 tenía 0.80 en el mismo punto): con la multa vertical en 0.5 vuelve a aplastar el aprendizaje. Se deja terminar
  los 10 M como control (D-067).

## D-067 · Compuerta B4 / B4* (18-oct)

`entorno.regla_b4()` y `--pol b4,b4o` en `medir_ia_aporta.py`. **B4** sube a 5.5 m si, desde arriba, ve al menos `B4_SUBE`
más de la zona de escape del ladrón (cobertura) y vuelve a 3.30 m si ve `B4_BAJA` o menos, con histéresis entre los dos.
**B4\*** hace lo mismo con la posición verdadera del ladrón: solo sirve para medir el techo. Prueba nueva: B4 nunca aprieta
un botón prohibido (`test_regla_b4_nunca_prohibido`). Medidas nuevas: vaivén de la red (solo lo que ella aprieta) y altura
pedida con el ladrón a < 3 m de una V contra en campo abierto.

**Ajuste de los umbrales con otra semilla** (7, 256 partidas, cancha real, `informes/v17/b4_ajuste_*.json`), M1: B3 20.7 %;
B4 con `B4_SUBE` = 0.02 / **0.05** / 0.10 → 20.3 / **21.9** / 18.0 %; B4\* → 17.2 / 20.7 / 17.2 %. Quedan 0.05 y 0.02.

**Medición oficial** (semilla 123, 512 partidas; `informes/v17/b4_real_*.json`, `b4_vieja_*.json`; B3 de
`v173_base_b3.json` y `v172_50M_b3.json`):

| | M1 cancha real | M1 cancha vieja | Altura pedida cerca de una V / en campo abierto (real) |
|---|---:|---:|---|
| B3 siempre SUBIR | **24.6 %** | **56.2 %** | 5.4 / 5.4 m |
| B4 altura por cobertura | 19.5 % | 54.1 % | 4.3 / 4.1 m |
| B4\* con la posición verdadera | 22.5 % | 51.4 % | 4.3 / 4.1 m |
| V17.2 a los 50 M (red) | — | 54.3 % | — |

**Resultado de la compuerta: cerrada.** Ni decidiendo la altura con la posición verdadera del ladrón se le gana a "siempre
subir" (B4\* queda 2.1 puntos debajo en la cancha real y 4.8 en la vieja). En esta cancha, con la búsqueda determinista
volviendo a 3.30 m en cada pérdida, **subir siempre ya es casi lo mejor que da la altura**. Por D-067 no se entrena más la
altura (la V17.4 con los cambios del diagnóstico no se lanza). Lo honesto para el documento:
**"la IA aprendió sola lo que hace la mejor regla simple"** (V17.2: 54.3 % contra 56.2 % de B3, empate dentro del ruido; le
gana a "solo reglas" por 5.9 puntos).

La palanca grande que queda (D-059 C: que la red decida los primeros 2-3 s tras perderlo) toca la regla dura 3: **la decide
Brahian**.

## V17.3 a los 10 M y análisis del vaivén (19-oct)

**V17.3** (paneles reales, suavidad vertical 0.5; 512 partidas, `informes/v17/v173_10M_det.json` y `_est.json`): **igual
a B0**. QUEDARSE en el 100 % (determinista) y el 99.6 % (estocástica) de las decisiones, probabilidad de la preferida 0.996,
entropía 0.03. M1 11.7 % / 10.9 % contra B0 11.7 %, B3 24.6 %, B4 19.5 %, B4\* 22.5 %. Altura pedida siempre 3.30 m.
Seguridad igual a B0 (alcanzado 0-0.2 %, choque con panel 0-0.2 %). **Conclusión:** con la multa vertical de 0.5 la red no
sale nunca de QUEDARSE. No se lanza nada más hasta que el Arquitecto lo revise con `supervisor-rl`.

**Vaivén de la V17.2 a los 50 M, separado** (cancha vieja, 512 partidas, `informes/v17/v172_50M_det_vaiven.json`):
- De los 16.8 cambios de sentido por minuto, **13.8 son de la red** (SUBIR después de BAJAR o al revés, en los pasos donde
  decide) y ~3 son de la vuelta a 3.30 m de la búsqueda.
- **Altura pedida donde decide:** 4.13 m con el ladrón a menos de 3 m de una V y 4.33 m en campo abierto. **No se pone más
  alta cerca de las V**: sube y baja sin atar la altura a la situación. B4 sí lo hace un poco (4.3 contra 4.1 m en la cancha
  real), y aun así no le gana a B3.

**Por qué colapsó la V17.3 con la suavidad vertical en 0.5:** la red empieza eligiendo casi al azar. Con 0.5, cada SUBIR
o BAJAR cuesta cinco veces más que en la V17.2. En los primeros millones de pasos, lo único seguro que aprende es que tocar
la altura cuesta y QUEDARSE no, y llega a QUEDARSE 100 % antes de descubrir que estar arriba paga (rachas de 30 s). Es el
mismo mecanismo que hizo colapsar la V17.1 con toda la suavidad. Por eso `K_SUAVE_Z_V17` volvió a 0.1 (D-068).

## La V17.2 en la cancha real (19-oct)

512 partidas, paneles reales de 1.5 × 2.2-2.3 m (`informes/v17/v172_real_det.json` y `_est.json`; B0-B4 de
`v173_base_b*.json` y `b4_real_*.json`):

| | M1 | Vista (s) | M2 ≤ 10 s | Rendición | Vaivén de la red (/min) | Altura pedida cerca de una V / abierto | Alcanzado, choques, geocerca, gimbal |
|---|---:|---:|---:|---:|---:|---|---|
| V17.2 determinista | **19.3 %** | 86.5 | 63.0 % | 2.3 % | 10.2 | 4.10 / 4.29 m | 0 |
| V17.2 estocástica | 19.1 % | 83.9 | 62.8 % | 3.7 % | 30.9 | 4.16 / 4.31 m | 0 |
| B0 / B3 / B4 | 11.7 / **24.6** / 19.5 % | 84.6 / 87.3 / 85.9 | 60.0 / 68.3 / 63.3 % | 1.6 / 4.1 / 2.1 % | 0 / 0 / 4.9 | — | 0 |

Le gana a "solo reglas" por 7.6 puntos, empata con B4 y queda 5.3 puntos debajo de "siempre subir": **no se adapta sola**
a los paneles reales. Hay que afinarla en la cancha real (V17.4).

## D-069 · La red decide durante la PÉRDIDA (D-059 C), experimento reversible (19-oct)

- **Cómo:** interruptor `PERDIDA_RED_V17` (en `False` por defecto). Con `True`, en la cancha, la red sigue decidiendo con sus
  7 botones durante la fase PÉRDIDA (PREDECIR: los ~1-4 s después de perder al ladrón, mientras el dron va tras la
  predicción). QUEDARSE ahí significa "seguir la regla" (ir tras la predicción). ACERCARSE, ALEJARSE y RODEAR se miden
  respecto al punto donde el dron cree que está el ladrón, y SUBIR y BAJAR siguen igual. Después de la PÉRDIDA sigue la
  búsqueda determinista de siempre (flanqueo, 360°, siguiente panel). El árbitro, el reflejo de punto ciego y las guardas
  mandan sobre la red, igual que con el objetivo a la vista.
- **Por qué un interruptor aparte y no `PERDIDA_IA`:** `PERDIDA_IA = True` (V15) entrega a la red hasta 60 s de búsqueda con
  los 10 botones viejos y **sin** búsqueda determinista: no es D-059 C y dejaría sin control. Así, `PERDIDA_IA` y su prueba de
  regla dura no cambian.
- **Pruebas:** `test_v17.TestPerdidaRed`. Apagado (por defecto), la red solo decide con el objetivo fijado y a la vista.
  Encendido, decide solo en FIJADO y en la PÉRDIDA, nunca en el flanqueo ni en el 360°, y la búsqueda determinista sigue
  apareciendo. Pasan todas las de reglas duras.
- `--desde` ahora carga modelos MaskablePPO y copia también la salida cuando ya era de 7 botones: arranca decidiendo
  exactamente igual que el modelo de origen (diferencia de logits 0).

### V17.4 · afinado en la cancha real con D-069 (en marcha)

Desde la V17.2 de 50 M (todos los pesos), paneles reales, suavidad vertical 0.1, entropía 0.01, `PERDIDA_RED_V17=1`,
10 M pasos. **Inicio 2026-10-19 10:57**, pestaña "V17 entrenamiento" del Terminal:
`.venv\Scripts\python.exe -u entrenar_master.py --desde modelos_v17_2\ultimo.zip --pasos 1e7 --envs 512 --semilla 17 --ent 0.01 --set PERDIDA_RED_V17=1 --repeticiones 5 --salida salida_v17_4 --dir-master modelos_v17_4 --dir-modelos modelos_v17_4 *> modelos_v17_4.log`

Se medirá el **mismo modelo** con el interruptor encendido y apagado (512 partidas, semilla 123). D-069 se queda solo si M1
sube ≥ 5 puntos con él y la seguridad sigue en 0.

**Resultado:** la corrida se cortó a los 8.2 M pasos (se reinició la sesión que la había lanzado en el Terminal). Se midió el
checkpoint de 8.0 M (`modelos_v17_4\checkpoints\dron_master_7999488_steps.zip`), el mismo modelo con el interruptor
encendido y apagado (512 partidas, `informes/v17/v174_8M_con.json` y `_sin.json`):

| | M1 | Vista (s) | M2 ≤ 10 s | Rendición | Vaivén de la red (/min) | Seguridad |
|---|---:|---:|---:|---:|---:|---|
| V17.4 **con** D-069 | **20.7 %** | 88.4 | 65.6 % | 2.0 % | 12.9 | 0 |
| V17.4 **sin** D-069 | 17.8 % | 86.2 | 61.9 % | 3.3 % | 8.5 | 0 |
| B3 siempre SUBIR | 24.6 % | 87.3 | 68.3 % | 4.1 % | 0 | 0 |

- **D-069 no se queda:** sube M1 en +2.9 puntos, debajo de los 5 que pide el criterio. `PERDIDA_RED_V17` queda en `False`.
- Ni siquiera en la pérdida la red usa rodear ni acercarse: solo SUBIR, BAJAR y QUEDARSE (75 %). No colapsa (probabilidad de
  la preferida 0.66).

## D-071 · Ruta de búsqueda de Brahian (B5) (19-oct)

`BUSQUEDA_RUTA_V17` (en `False` por defecto) cambia la búsqueda determinista por la ruta de `docs/RUTA_BUSQUEDA_BRAHIAN.md`.
Al perderlo, el dron va a la V donde lo vio por última vez y recorre su parte de atrás (la que no ve) de esquina a esquina, a
`D_RUTA_B5` = 4.5 m y a la altura segura, mirando hacia donde vuela. Después se pone de frente a la boca con un vaivén de
±30° durante 3 s, pasa a la otra V y repite hasta encontrarlo (o hasta los 90 s de siempre). Sigue siendo una regla
determinista, así que la regla 3 no cambia. Prueba: `test_v17.TestRutaB5`.

**¿La ruta vale la pena?** (512 partidas, cancha real, `informes/v17/ruta_b5.json` y `ruta_b5s.json`):

| | M1 | Vista (s) | M2 ≤ 10 s | Rendición | Misión perdida | Seguridad |
|---|---:|---:|---:|---:|---:|---|
| **B5** ruta + SUBIR | 20.1 % | 78.8 | 60.7 % | 5.3 % | 3.9 % | 0 |
| **B5s** ruta sin subir | 10.5 % | 71.9 | 50.3 % | 1.0 % | 5.7 % | alcanzado 0.2 % |
| B3 / B0 (búsqueda de siempre) | 24.6 / 11.7 % | 87.3 / 84.6 | 68.3 / 60.0 % | 4.1 / 1.6 % | — | 0 |

Con los valores de partida, **la ruta no le gana a la búsqueda actual**: B5 queda 4.5 puntos debajo de B3 y B5s 1.2 debajo de
B0. En las dos baja la vista total: el recorrido largo pierde al ladrón que se queda cerca. Como las distancias eran valores
de partida, se prueba `D_RUTA_B5` = 3.0 / 4.5 / 6.0 m con otra semilla (7, 256 partidas,
`informes/v17/ruta_ajuste_d*.json`) antes de cerrar.

**Ajuste** (semilla 7, 256 partidas), M1 de B5 con `D_RUTA_B5` = 3.0 / 4.5 / 6.0 m: **18.4** / 17.2 / 9.0 %, contra 20.7 % de
B3 con la misma semilla. Más cerca es mejor, pero ninguna distancia llega a B3. **Medición oficial con 3.0 m** (semilla 123,
512 partidas, `informes/v17/ruta_b5_d3.json`): **M1 22.7 %**, vista 88.6 s, M2 65.6 %, rendición 4.5 %, seguridad 0. B3
saca 24.6 %.

**Cierre de D-071 (criterio de `docs/RUTA_BUSQUEDA_BRAHIAN.md`):** B5 no supera a B3 + 5 puntos, sino que queda 1.9 puntos
debajo, dentro del ruido. Resultado honesto: **"la ruta de Brahian no mejora a subir siempre en esta cancha"**. Por eso no se
entrena la imitación de B5 ni el bono de progreso. La ruta queda en el código, apagada (`BUSQUEDA_RUTA_V17 = False`), con
`D_RUTA_B5 = 3.0` m (la mejor medida), por si se cambia la cancha.

## D-072 · Hardware actual: cámara fija, sin gimbal (20-oct)

Brahian cambió el dron: no hay gimbal ni cámara USB. Ahora tiene una CSI IMX219 (62.2° × 48.8°) **fija** al chasis,
inclinada ~5° hacia abajo, con el TF03 paralelo en la misma base y sin TF-Luna. La cámara al piso está planeada pero todavía
no montada.

- **En la simulación:** `entorno.aplicar_hw("ACTUAL")`, o `--hw ACTUAL` en `medir_ia_aporta.py` y `entrenar_master.py`.
  - Cámara a `CAM_FIJA_PITCH = −5°` más el cabeceo del chasis; el seguimiento vertical ya no la mueve.
  - FOV de la IMX219, TF03 a −5°, sin TF-Luna (la distancia láser la da el TF03).
  - Cámara al piso apagada (`--set CAM_PISO_ACTIVA=1` para la planeada).
  - Zona ciega con la inclinación real (a 3.8 m: 7.7 m, antes 3.2 m).
  - Las demás variantes quedan como están (`aplicar_hw("BASE")` = gimbal V16) y el pan-tilt queda para después (D-056).
  - **Regla dura 1:** la barrera −45..+15° se conserva sobre la cámara aunque hoy no haya gimbal.
  - Prueba: `test_v17.TestHardwareActual`.
- **Por qué murieron la V17.4 y la V17.5 a los 8.2 M:** las dos se cortaron a los ~61 min de lanzarse, sin ningún error en
  su registro: algo cierra los procesos hijos de la sesión de Claude. Desde la V17.6 los entrenamientos se crean **vía WMI**
  (`Invoke-CimMethod Win32_Process Create`), que no cuelgan del árbol de procesos de la sesión.

**Línea base con la cámara fija** (cancha real, 512 partidas, semilla 123, `informes/v17/actual_*.json`):

| | M1 (30 s) | Racha media (s) | Vista (s) | M2 ≤ 10 s | Misión perdida | Seguridad |
|---|---:|---:|---:|---:|---:|---|
| B0 quedarse | **3.7 %** | 13.6 | 63.5 | 76.4 % | 4.9 % | alcanzado 0.4 % |
| B1 azar | 1.6 % | — | 60.2 | 76.7 % | 7.6 % | alcanzado 0.2 % |
| B3 siempre subir | 0.8 % | — | 55.8 | 77.7 % | 10.0 % | alcanzado 0.2 % |
| B5 ruta de Brahian (3.0 m) | 1.8 % | 12.1 | **66.3** | 78.3 % | **0.8 %** | 0 |
| V17.2 (50 M, sin reentrenar) | 2.5 % | 12.4 | 60.5 | 76.7 % | 8.2 % | alcanzado 0.2 % |

- Con la cámara fija **todo cae**: la racha media es de ~12-13 s y casi nunca hay 30 s seguidos. **Subir ahora empeora**,
  porque la cámara ya no mira hacia abajo. La ruta de Brahian da la mayor vista total y casi nunca pierde la misión (0.8 %,
  contra 4.9 % de B0), aunque no gana en M1.
- M1 (30 s) vuelve a estar casi en 0: desde ahora la herramienta reporta también `custodia15` (racha ≥ 15 s) como apoyo.
  La M1 sigue siendo la de D-059.

**V17.6 en marcha** (afinado de la V17.2 con el hardware actual, 10 M, entropía 0.01, sin D-069). **Inicio 2026-10-20 01:38**,
creado vía WMI. Registro `03_SIMULACION_RL\modelos_v17_6.log`, modelos en `modelos_v17_6\`. Comando (PowerShell, desde
`03_SIMULACION_RL`):
`Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine='cmd.exe /c ".venv\Scripts\python.exe -u entrenar_master.py --hw ACTUAL --desde modelos_v17_2\ultimo.zip --pasos 1e7 --envs 512 --semilla 17 --ent 0.01 --repeticiones 5 --salida salida_v17_6 --dir-master modelos_v17_6 --dir-modelos modelos_v17_6 > modelos_v17_6.log 2>&1"'; CurrentDirectory=(Get-Location).Path}`
Si se corta, cambiar `--desde modelos_v17_2\ultimo.zip` por `--continuar`. Medirla con
`herramientas\medir_ia_aporta.py v17 --hw ACTUAL --pol modelos_v17_6\ultimo.zip,modelos_v17_6\ultimo.zip-est --n 512 --salida informes\v17\actual_v176.json`.

**Aclaración (Coordinador, por Brahian):** la cámara fija (`--hw ACTUAL`, también `--hw G`) es el dron del **MÍNIMO**. El
**PLUS** es la variante **H** (D-074/D-075). La V17.6 queda como control del mínimo. Medida con 512 partidas
(`informes/v17/g_v176.json`): **idéntica a B0** (M1 3.7 %, racha media 13.6 s), es decir, colapsó a QUEDARSE con la
cámara fija.

## D-075 · Variante H, el plus: pan-tilt de 2 servos (20-oct)

`--hw H` (`entorno.aplicar_hw("H")`), con los rangos de `05_HARDWARE_Y_VARIANTES/config_sim/variante_H.json`:
- **CSI#1 + TF-Luna** juntos en el pan-tilt (62.2° × 48.8°): la cámara y el TF-Luna miran a `rumbo + pan`.
- **Tilt:** servo de 600°/s, retardo de 50-100 ms y zona muerta de 1°, entre −45° y +15° (la barrera de la regla dura 1
  se conserva).
- **Pan:** ±90° (**provisional**, Hardware lo confirma en banco), 600°/s, zona muerta de 1°, con topes mecánicos.
- **TF03** fijo al chasis a −5° (frenado de seguridad, mapa 360° girando el dron). **CSI#2** fija al piso, activa.
- **El pan lo mueve una regla:** con alguien en foco (el ladrón fijado o un candidato) lo centra en la imagen, y la nariz del
  dron lo sigue más despacio con la guiñada de siempre. Buscando, apunta al punto que se revisa (la predicción, el panel o el
  muro), así que **mira detrás de la V sin volar hasta ahí**. En el 360° vuelve a 0.
- La red ve el ángulo del pan (en la casilla que la V17 no usaba). La opción de que la red decida el pan al buscar
  necesita botones nuevos: queda pendiente.
- Prueba: `test_v17.TestVarianteH` (el pan respeta ±PAN_MAX, el tilt la barrera y el pan sí se mueve).

**Medición en G (mínimo) y H (plus)**, cancha real, 512 partidas, semilla 123 (`informes/v17/actual_*.json`,
`g_v176.json`, `h_*.json`):

| | M1 (30 s) en G | M1 en H | Racha ≥ 15 s en H | Racha media en H (s) | Vista en H (s) | M2 en H | Rendición en H | Misión perdida en H |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 QUEDARSE | 3.7 % | **62.3 %** | 95.7 % | 33.4 | 126.4 | 91.6 % | 20.9 % | 3.5 % |
| B3 siempre SUBIR | 0.8 % | **78.3 %** | 96.9 % | 37.8 | 119.2 | 92.0 % | 38.7 % | 3.5 % |
| **B5 ruta de Brahian** (+ SUBIR) | 1.8 % | **92.0 %** | 98.2 % | 41.7 | 126.4 | 99.3 % | 59.8 % | **0 %** |
| B5s ruta de Brahian + QUEDARSE | — | **87.3 %** | — | 39.7 | 137.3 | 99.3 % | 44.9 % | 0 % |
| V17.2 (50 M, sin reentrenar) | 2.5 % | **72.7 %** | 97.1 % | 36.5 | 123.0 | 91.6 % | 31.4 % | 2.9 % |
| V17.6 (red entrenada en G) | 3.7 % | — | — | — | — | — | — | — |

Seguridad en H: alcanzado 0-0.2 %, choque con panel 0-0.2 %, geocerca y gimbal fuera de rango en 0.

- **El pan-tilt es la diferencia grande:** B0 pasa de 3.7 % a 62.3 % de M1. Es el argumento para el documento de por qué el
  plus necesita el pan-tilt.
- **La ruta explica casi todo:** B5s (la ruta sin subir, `h_b5s.json`) da 87.3 % (+25 puntos sobre B0), y subir agrega
  +4.7 hasta el 92.0 % de B5.
- **Con el pan, la ruta de Brahian sí gana:** B5 saca 92.0 %, 13.7 puntos sobre B3, y no pierde ninguna misión. Cumple el
  primer criterio de D-071 (B5 ≥ B3 + 5). Sin pan no ganaba, porque había que volar hasta detrás de la V para mirar.
- **Métricas:** en H la M1 de 30 s separa bien (62 a 92 %), y la racha ≥ 15 s se satura (96-98 %). En G pasa al revés: la de
  30 s queda en ~0 y la de 15 s separa (B0 31.6 %). Propuesta: M1 = 30 s para el plus (H) y M1' = 15 s solo para la
  cámara fija (G).

**V17.7 · entrenamiento en H con la ruta de Brahian como búsqueda** (desde la V17.2 de 50 M, 10 M, entropía 0.01,
`--set BUSQUEDA_RUTA_V17=1`). La ruta es determinista, así que la regla 3 no cambia; con el pan es la mejor regla medida. La
red decide igual que antes (con el ladrón a la vista); la referencia que tiene que superar es **B5 (92.0 %)**.
**Inicio 2026-10-20 06:43**, vía WMI, registro `03_SIMULACION_RL\modelos_v17_7.log`. Una primera V17.7 con la búsqueda vieja
se detuvo a 1.3 M para relanzarla así. Comando (PowerShell, desde `03_SIMULACION_RL`):
`Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine='cmd.exe /c ".venv\Scripts\python.exe -u entrenar_master.py --hw H --set BUSQUEDA_RUTA_V17=1 --desde modelos_v17_2\ultimo.zip --pasos 1e7 --envs 512 --semilla 17 --ent 0.01 --repeticiones 5 --salida salida_v17_7 --dir-master modelos_v17_7 --dir-modelos modelos_v17_7 > modelos_v17_7.log 2>&1"'; CurrentDirectory=(Get-Location).Path}`
Medirla: `herramientas\medir_ia_aporta.py v17 --hw H --set BUSQUEDA_RUTA_V17=1 --pol modelos_v17_7\ultimo.zip,modelos_v17_7\ultimo.zip-est --n 512 --salida informes\v17\h_v177.json`

**Resultado de la V17.7 a los 10 M** (terminó 07:50; 512 partidas, `informes/v17/h_v177_det.json` y `_est.json`; sobrevivió
pasando los 8.2 M gracias al lanzamiento vía WMI):

| | M1 | Racha media (s) | Vista (s) | M2 | Rendición | Misión perdida | Vaivén de la red (/min) | Seguridad |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| **V17.7 determinista** | **91.0 %** | 41.8 | 128.1 | 99.4 % | 59.0 % | 0.2 % | 30.6 | 0 |
| V17.7 estocástica | 92.6 % | 41.7 | 126.3 | 99.4 % | 60.4 % | 0.2 % | 42.7 | alcanzado 0.2 % |
| B5 ruta + SUBIR | 92.0 % | 41.7 | 126.4 | 99.3 % | 59.8 % | 0 % | 0 | 0 |
| B5s ruta + QUEDARSE | 87.3 % | 39.7 | 137.3 | 99.3 % | 44.9 % | 0 % | 0 | 0 |
| B3 / B0 (búsqueda de siempre) | 78.3 / 62.3 % | 37.8 / 33.4 | 119.2 / 126.4 | 92.0 / 91.6 % | 38.7 / 20.9 % | 3.5 / 3.5 % | 0 | 0 |

- **Empata con B5** (±2.4 puntos de ruido cerca del 92 %) y le gana a B3 por 12.7 y a B0 por 28.7 puntos.
- **Lo honesto para el documento:** el salto viene del **pan-tilt** (B0: 3.7 → 62.3 %) y de la **ruta de Brahian** (+25
  puntos, y es una regla). Encima de eso, la red rinde lo mismo que "siempre subir": aprendió sola la mejor regla simple, pero
  sube y baja de más (30.6 cambios por minuto). Con el criterio de `RUTA_BUSQUEDA_BRAHIAN.md`: la red ≥ max(B3, B0) + 5 ✔ y la
  red ≥ B5 − 3 ✔. No supera a B5 (misma búsqueda).
- Se elige la **V17.7 como política del plus por ahora**. Las repeticiones con ella se graban en
  `03_SIMULACION_RL\repeticiones_v17_h\` (fuera de Git), con
  `herramientas\grabar_repeticiones_v17.py --modelo modelos_v17_7\ultimo.zip --hw H --set BUSQUEDA_RUTA_V17=1 --salida repeticiones_v17_h`.
  Las de la V17.2 (sin pan) quedan en `repeticiones_v17\`.
  **Grabadas** (08:36, semillas 500-501): rendición, re-encuentro estando alto, civil curioso y cambio de V. **El salto no salió
  en 80 partidas**: con el pan-tilt el dron casi siempre está alto y el ladrón casi no intenta saltar (para Unreal sirve el
  `salto.json` de `repeticiones_v17\`, que es de la V17.2).

### Verificación del pan y desglose (20-oct, alerta del Visor)

- **El pan sí se mueve.** En H con la ruta (64 partidas): |pan| medio 11.8°, 8.9° con el objetivo fijado y 25.3° en la búsqueda.
  Pasa de 10° el 24 % del tiempo y llega a ±90°. Se aplica en `entorno.py`: la regla del pan está en el paso del gimbal y la
  cámara y el TF-Luna miran a `rumbo + pan` en `_sensores`. El visor veía 0 porque `foto()` no traía el campo: ahora trae
  **`pan`** y **`pan_meta`** (°, + = a la izquierda de la nariz), con prueba. Las repeticiones de `repeticiones_v17_h\` se
  regrabaron con el campo (en la de rendición, el pan llega a ±90°).
- **Cuánto aporta cada pieza** (512 partidas; `h_sinpan_*.json` = H con `--set PAN_ACTIVO=0`):

  | M1 | G (cámara fija) | H sin pan (cámara 62.2° + tilt) | H con pan |
  |---|---:|---:|---:|
  | B0 | 3.7 % | 25.2 % | 62.3 % |
  | B5 ruta de Brahian | 1.8 % | 60.2 % | 92.0 % |

  El pan aporta +37 puntos en B0 y +32 en B5; la cámara ancha con el tilt aporta el resto.

### Robustez de B5 y V17.7 en H (20-oct)

256 partidas por escenario, con la ruta, `informes/v17/rob_*.json`. Perillas nuevas: `N_CIVILES_V17`, `FACTOR_SERVO_H`
(servos `f` veces más lentos, con `f` veces el retardo y ruido de pan) y `RECALL_YOLO`.

| Escenario | M1 B5 | M1 V17.7 | Vista B5 / V17.7 (s) | Misión perdida B5 / V17.7 | Seguridad |
|---|---:|---:|---|---|---|
| Base | 93.8 % | 91.0 % | 122 / 127 | 0 / 0.4 % | 0 |
| (a) agachado y gateando más (`P_POSTURA_ESCONDIDO=0.05,0.45,0.5`, `P_GATEAR=0.6`) | 82.8 % | **86.3 %** | 131 / 133 | 0 / 0 | 0 |
| (b) 2 civiles curiosos (`N_CIVILES_V17=2`) | 89.5 % | 87.5 % | 128 / 136 | 0 / 0 | 0 |
| (c) V movidas ±3 m, ±30° (`AZAR_POS_V17=3`, `AZAR_ANG_V17=30`) | 91.0 % | 89.5 % | 123 / 119 | 0.8 / 0.8 % | 0 |
| (d) servos ×2 (`FACTOR_SERVO_H=2`) | 89.1 % | 89.8 % | 126 / 132 | 0 / 0.4 % | 0 |
| (e) YOLO con recall 0.7 (`RECALL_YOLO=0.7`) | 90.6 % | 89.1 % | 99 / 106 | 0 / 0 | alcanzado 0.4 % |

Con 256 partidas el margen es de ±3.5 puntos. **La ruta y la red aguantan** todos los escenarios: 83-94 % de M1 y ≤ 0.8 % de
misión perdida. La V17.7 empata con B5 en todos, y con el ladrón agachando y gateando más le saca +3.5 puntos.

### V17.8 · la red decide el pan (20-oct)

- `PAN_RED_V17` (en `False` por defecto) da 3 botones más: **PAN_IZQ, PAN_DER, PAN_CENTRO** (±20° sobre lo que pide la regla,
  o volver a 0). En la búsqueda la red **solo apunta la cámara**: no puede mover el dron, porque los botones de mover quedan
  bloqueados y la ruta de Brahian sigue volando (búsqueda determinista). Con el ladrón a la vista, la regla centra la cámara.
- `K_VAIVEN_V17`: multa por cada cambio de sentido de la altura que pide la red (V17.8: 0.1).
- `--desde` copia las 7 salidas de la V17.7; los 3 botones nuevos arrancan con probabilidad baja (1.2 %). Prueba:
  `test_v17.TestPanRed` (buscando, la red no mueve el dron; con el objetivo, el pan es de la regla).
- **Criterio (Coordinador):** supera a B5 por ≥ 3 puntos, o iguala con menos de 15 cambios de altura por minuto.
- **En marcha desde 2026-10-20 09:04**, vía WMI, registro `03_SIMULACION_RL\modelos_v17_8.log`. Comando (PowerShell, desde
  `03_SIMULACION_RL`):
  `Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine='cmd.exe /c ".venv\Scripts\python.exe -u entrenar_master.py --hw H --set BUSQUEDA_RUTA_V17=1 --set PAN_RED_V17=1 --set K_VAIVEN_V17=0.1 --desde modelos_v17_7\ultimo.zip --pasos 1e7 --envs 512 --semilla 17 --ent 0.01 --repeticiones 5 --salida salida_v17_8 --dir-master modelos_v17_8 --dir-modelos modelos_v17_8 > modelos_v17_8.log 2>&1"'; CurrentDirectory=(Get-Location).Path}`
  Medirla con las mismas `--set` y `--pol modelos_v17_8\ultimo.zip`.
- No se hizo la imitación de la ruta, porque la ruta ya es la búsqueda (regla) y la red solo apunta la cámara encima de
  ella.

## Entrenamiento en marcha y cómo retomarlo (19-oct)

Los entrenamientos y mediciones se lanzan ahora **desacoplados de la sesión** (PowerShell `Start-Process -WindowStyle Hidden`,
con el registro en un archivo): siguen corriendo aunque se cierre o se reinicie Claude Code.

- **V17.5 · afinado en la cancha real, sin D-069** (desde la V17.2 de 50 M, suavidad vertical 0.1, entropía 0.01, 10 M
  pasos). Es la candidata a política V17 en la cancha real. **Inicio 2026-10-19 13:37.** Registro:
  `03_SIMULACION_RL\modelos_v17_5.log` (errores en `modelos_v17_5.err`); modelos en `modelos_v17_5\`.
- **Lanzarlo igual desde PowerShell** (desde `03_SIMULACION_RL`):
  `Start-Process -FilePath .venv\Scripts\python.exe -ArgumentList "-u entrenar_master.py --desde modelos_v17_2\ultimo.zip --pasos 1e7 --envs 512 --semilla 17 --ent 0.01 --repeticiones 5 --salida salida_v17_5 --dir-master modelos_v17_5 --dir-modelos modelos_v17_5" -WorkingDirectory . -RedirectStandardOutput modelos_v17_5.log -RedirectStandardError modelos_v17_5.err -WindowStyle Hidden`
- **Si se corta, retomarlo desde su último modelo:** el mismo comando cambiando `--desde modelos_v17_2\ultimo.zip` por
  `--continuar` (retoma `modelos_v17_5\ultimo.zip`; con `--continuar`, `--pasos` son los pasos que se agregan).
- **Ver el avance:** la última línea `it …` del registro (pasos, pasos/s, entropía). **Detenerlo:** en el Administrador de
  tareas, el `python.exe` que más memoria usa (~400 MB), o `Stop-Process -Id <PID>` (el PID sale al lanzarlo).
- **Medirlo al terminar:**
  `.venv\Scripts\python.exe herramientas\medir_ia_aporta.py v17 --pol modelos_v17_5\ultimo.zip,modelos_v17_5\ultimo.zip-est --n 512 --salida informes\v17\v175_10M.json`

## Repeticiones escogidas (D-065)

`herramientas/grabar_repeticiones_v17.py`: corre partidas de una en una (1 hilo) con una política en la cancha V17 con
los paneles reales y guarda en `repeticiones_v17/` (fuera de Git) la primera de cada tipo, en el formato de
`replay_v17.json` más `tipo`, `descripcion`, `semilla` y `modelo`, con un `LEEME.md`. Tipos: rendición, re-encuentro
estando alto (> 4 m), salto, civil curioso (mira o graba) y cambio de V (L3). `grabar_nivel` (`entrenar_master.py`) recibe
ahora un gancho opcional `al_paso` para esto.
`.venv\Scripts\python.exe herramientas\grabar_repeticiones_v17.py --modelo modelos_v17_2\ultimo.zip`

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

**2026-10-20 18:24 · V17.9 en pausa a 2.6 M (por pedido del Coordinador, para que Unreal mida fps sin carga).** Se retoma de `modelos_v17_9/ultimo.zip` (guardado 18:21) con el mismo comando, desde `03_SIMULACION_RL` por WMI: `.venv\Scripts\python.exe -u entrenar_master.py --hw H --set BUSQUEDA_RUTA_V17=1 --desde modelos_v17_9\ultimo.zip --pasos 1e7 --envs 512 --semilla 19 --ent 0.01 --repeticiones 5 --salida salida_v17_9 --dir-master modelos_v17_9 --dir-modelos modelos_v17_9 > modelos_v17_9.log 2>&1` (usa `>>` para no borrar el registro). También se cortaron las mediciones de escenarios (`informes/v17/t_sindesp_*`, `t_dosciv_*`, `t_juntos_*`): se relanzan con `/tmp`-script equivalente: `herramientas\medir_ia_aporta.py v17 --hw H --n 512 --semilla 123 --set BUSQUEDA_RUTA_V17=1 --set R_DESPEJE_V17=0 | N_CIVILES_V17=2 | SEP_V17=6.0 --pol b0 | modelos_v17_7\ultimo.zip` (B0 sin la ruta).
**2026-10-20 · Segunda pausa (orden del Coordinador: prioridad única = motor gráfico).** La V17.9 se reanudó 3 min y se paró otra vez; el contador de pasos reinicia en 0 con los pesos de `modelos_v17_9\ultimo.zip` (se suman a los 2.6 M de antes). Para retomarla, el mismo comando de la nota anterior. Las mediciones de escenarios (`t_sindesp_*`, `t_dosciv_*`, `t_juntos_*`) y la suite con las físicas nuevas siguen pendientes.

**2026-10-21 01:07 · V17.9 reanudada (el motor gráfico quedó listo).** Cómo verla: `03_SIMULACION_RL\modelos_v17_9.log` (una línea `it N | M pasos` por iteración; meta 10 M), o `salida_v17_9\` y el visor. Variante H, ruta B5', geometría medida (CSI 68.3° × 54.0°, TF03 −6.7°), altura base 2.0 m. Corre en prioridad baja (BelowNormal) con 6 hilos para no quitarle fluidez a Unreal.
**Un clic:** `PARAR_ENTRENAMIENTO.bat` (raíz del proyecto) pide parar, guarda `modelos_v17_9\ultimo.zip` y, si en 2 min no termina, lo cierra; `REANUDAR_ENTRENAMIENTO.bat` lo retoma desde ese archivo. Nota: el contador de pasos arrancó en 0.1 M porque `ultimo.zip` se había sobrescrito en el arranque anterior (los pesos sí traen lo aprendido: base V17.7 + ~2.6 M pasos).
**Mediciones pendientes** de la tabla justa (sin despeje, dos civiles, paneles juntos; B0, B5', V17.7): después del entrenamiento, no en paralelo (orden del Coordinador).
