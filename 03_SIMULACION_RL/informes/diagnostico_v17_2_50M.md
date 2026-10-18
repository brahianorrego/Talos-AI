# Diagnóstico de la V17.2 a los 50 M pasos (supervisor-rl, 2026-10-18)

Solo lectura: no se cambió código ni se corrió nada. Toda cifra lleva su archivo. Carpeta de datos:
`03_SIMULACION_RL/informes/v17/`. Las cifras de 50 M son de la cancha vieja (paneles de 1.0 × 1.9-2.2 m), 512 partidas,
misma semilla para todas las políticas. Margen de error de una política sola: ±4.3 puntos en M1 (`docs/PROGRESO_V17.md`).

## 0. En cinco líneas (para Brahian)

1. La IA **sí aprendió algo**: a los 50 M le gana a "siempre quedarse" (B0) por 5.9 puntos, pero **no le gana** a "siempre
   subir" (B3): 54.3 % contra 56.2 %. Esa diferencia cabe en el ruido, así que lo honesto es decir que **empata con B3**.
2. No es solo B3 con ruido. Consigue el 75 % de lo que B3 gana en M1 y la misma rendición, pero pierde al ladrón menos veces.
   Eso indica que ya sube **a veces**, en los momentos que sirven. Le falta afinarlo.
3. Hay tres causas probables, en este orden. (a) En esta cancha, con la altura como única palanca que sirve, "subir siempre"
   podría estar cerca de lo mejor posible. Todavía no se sabe y hay que medirlo antes de seguir. (b) A la red le falta un
   dato clave: no sabe qué altura ya pidió. (c) La entropía la mantiene indecisa desde los 25 M.
4. El "vaivén" de 16.8 cambios por minuto está inflado: parte la causa la búsqueda, que baja el dron a 3.30 m cada vez que
   pierde al ladrón. Lo que es de la red se estima en ~10 por minuto, contra ~0 de B3.
5. Antes de entrenar la V17.4 hay que medir una regla nueva, **B4**, que pone el dron alto o bajo según la cobertura. Si ni
   siquiera B4 con información perfecta le gana a B3, no tiene sentido entrenar más la altura.

## 1. Lo que dicen los números

| | M1 racha ≥ 30 s | Vista (s) | Pérdidas / partida | Re-adq. ≤ 10 s | t re-adq. (s) | Rendición | Retorno | Cambios de sentido (/min) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| V17.2 determinista | **54.3 %** | 99.4 | 22.05 | 74.0 % | 6.09 | 22.5 % | 22.99 | 16.8 |
| V17.2 estocástica (como entrena) | 53.7 % | 100.5 | 22.41 | 73.3 % | 6.15 | 18.0 % | **18.30** | 42.7 |
| B0 siempre QUEDARSE | 48.4 % | 102.6 | 21.46 | 70.3 % | 6.71 | 14.5 % | 18.40 | 0 |
| B3 siempre SUBIR | **56.2 %** | 96.0 | 25.14 | 78.8 % | 5.39 | 22.3 % | **23.35** | 8.2 |
| B2 posicionamiento (base V17.2) | 53.1 % | 98.9 | 20.71 | 70.1 % | 6.80 | 17.2 % | 16.02 | — |

Fuentes: `v172_50M_det.json`, `v172_50M_est.json`, `v172_50M_b0.json`, `v172_50M_b3.json`, `v172_base_b2.json`.

**Qué mejoró (10 M → 50 M):** M1 de 50.0 % a 54.3 %, rendición de 15.0 % a 22.5 %, retorno de 13.9 a 23.0
(`v172_10M_det.json` contra `v172_50M_det.json`). La preferida pasó de probabilidad 0.55 a 0.63 y la entropía donde decide
bajó de 0.95 a 0.78 (de 1.95 posible). A los 10 M subía y bajaba casi por igual: SUBIR 52 % y BAJAR 48 %. A los 50 M
elige QUEDARSE 71 %, SUBIR 17 % y BAJAR 13 %.

**Qué tan parecida es a B3** (dónde cae la IA entre B0 = 0 y B3 = 1, cuentas propias con los mismos archivos):

| Métrica | Fracción del camino de B0 a B3 |
|---|---:|
| M1 | 0.75 |
| Rendición | 1.0 |
| Re-adquisición ≤ 10 s | 0.44 |
| Tiempo de re-adquisición | 0.47 |
| Vista total perdida | 0.49 |
| Pérdidas de más | **0.16** |

Una mezcla al azar de B0 y B3 debería caer más o menos en el mismo punto en todas las filas. La IA se lleva casi todo lo
bueno de subir (M1 y rendición) y paga poco de lo malo (pérdidas). Es la huella de una estrategia que **depende de la
situación**, aunque todavía floja. Es una señal, no una prueba: la diferencia en M1 está dentro del ruido.

**Qué empeoró:** el vaivén y la suavidad. La guiñada pasa de 0.76/s en B0 a 0.86/s en la IA (B3: 0.99/s). Cabeceo y gimbal
quedan entre B0 y B3. Suavidad ×0.1 no la empeoró (`v172_50M_*.json`, `jitter_por_s`).

**Seguridad igual a B0 y B3:** alcanzado 0.2 % en las tres. Choques con peatones y paneles, geocerca y gimbal fuera de
−45..+15°: 0. Tiempo real bajo 3.30 m con alguien a < 8 m: IA 0.46 %, B0 0.52 %, B3 0.36 % (mismos archivos).

**Entropía en el entrenamiento** (`salida_v17_2/metricas.json`, campo `entropia`, promedio de todos los pasos con los
pasos sin decisión en 0): 0.35 a los 0.6 M, 0.25 a los 10.8 M, 0.20 a los 25.8 M, 0.25 a los 38.3 M y 0.22 a los 50 M.
**Desde los ~25 M está plana:** la red dejó de afilarse.

### El vaivén está inflado por la búsqueda

`medir_ia_aporta.py` (líneas 206-208) cuenta los cambios de sentido de `z_v17`, la altura que pide la red. Pero
`entorno.py` (línea 3078) pone `z_v17 = 3.30 m` cada vez que se pierde el objetivo. Por eso **B3, que nunca aprieta BAJAR,
marca 8.2 cambios por minuto**: todos salen de ese reinicio. B3 pierde 5.7 veces por minuto (25.14 en 265 s), lo que da
~1.45 cambios por pérdida. La IA pierde 4.96 veces por minuto. Con la misma proporción, ~7 de sus 16.8 cambios serían del
reinicio y **~10 por minuto serían de la red**. Es una estimación: la herramienta no los separa.

## 2. Pregunta 1: ¿por qué no le gana a B3?

| Hipótesis | Qué dicen los datos | Veredicto |
|---|---|---|
| **"Subir siempre" ya es casi lo mejor en esa cancha** | De los 7 botones fijos, solo SUBIR se separa del ruido (`fijo_*.json`). La única palanca es la altura, con dos opciones: arriba o abajo. Además la altura vuelve a 3.30 m en cada pérdida (~22 por partida), y B3 es la forma más rápida de volver a subir. B3 paga más pérdidas (25.1 contra 21.5) y menos vista (96 contra 103 s): **hay algo que ganar estando abajo a veces**, pero nadie ha medido cuánto | **Posible y sin medir.** Es lo primero que hay que medir (B4 y B4*, sección 3) |
| **Le falta información** | La altura propia **sí** entra a la red (`entorno.py` línea 1893: `dz + e_baro − 2.3`), con el ruido del barómetro. La **altura pedida `z_v17` no entra.** La casilla de la línea 1919 lleva `z_ia`, la altura de la búsqueda por IA de la V15, que está muerta en la V17 porque `PERDIDA_IA = False`. Con la rampa de altura y el ruido del barómetro, la red no sabe si ya pidió subir. Eso calza con el vaivén. La **distancia del ladrón a la V** tampoco entra directa: la red tendría que combinar la grilla de 144 casillas con la distancia y el ángulo al ladrón. Además la grilla solo tiene los paneles que el LiDAR alcanzó a mapear, y el 360° de entrada mapea el 53 % (`v172_50M_det.json`, `mapeo_entrada`) | **Sí, falta.** Es barato de arreglar |
| **Horizonte corto (gamma 0.99)** | 0.99 equivale a ~10 s. La racha exige 30 s, pero el potencial de la racha (`K_RACHA_V17 = 3`) paga cada décima de segundo, y perder la racha cobra en el momento. La ventaja de estar arriba (no perderlo cuando corre a la otra V, ~3 s) cabe en 10 s. **Ojo: la V17.3 corre sin `--gamma`** (`PROGRESO_V17.md` línea 198), así que la idea de gamma 0.995 de D-062 sigue sin probarse | **Secundario.** Si se prueba, hay que cambiar también `GAMMA_GUIA` (cambio 3) |
| **Le sobra entropía (0.01)** | La política estocástica, que es la que se entrena, cobra **18.30, lo mismo que B0 y 5 puntos menos que B3 (23.35)**. La determinista cobra 22.99. La diferencia sale de la rendición y la racha (17.9 contra 22.1) y de la suavidad (−2.27 contra −0.22). Su vaivén es de 42.7 por minuto. La entropía está plana desde los 25 M | **Sí contribuye.** La red se queda indecisa justo donde tendría que decidir. Pero bajarla desde el arranque colapsó la V17.1 (0.003 → QUEDARSE a los 1.3 M) |

**Respuesta corta.** Lo más probable es una mezcla. La altura sola da poco margen sobre B3 (cuánto, no se sabe). La red no
ve la altura que pidió ni la geometría ladrón-V. Y la entropía la tiene indecisa. **El problema no es la recompensa**: el
retorno ordena las políticas casi igual que M1 (B3 23.35 > IA 22.99 > B0 18.40; B2 cae por la multa de suavidad). La
recompensa no esconde una política mejor que la red no encuentre por culpa de ella.

## 3. Pregunta 2: ¿qué tendría que aprender para ganarle a B3? Línea base B4

**Lo que habría que aprender:** estar arriba (5.5 m) cuando el ladrón está cerca de una V y puede esconderse detrás, y abajo
(3.30 m) en campo abierto, donde desde arriba se pierde más por el borde de la imagen. Desde ahí, no apretar botones si la
situación no cambió.

**B4 · regla de altura por cobertura** (la competidora honesta; usa lo mismo que B2):
- Solo cuando la red decidiría, con la misma máscara.
- Con la posición donde el dron **cree** que está el ladrón (`ult_x`, `ult_y`, como B2) y desde su posición horizontal
  actual, calcula `c_bajo = _cobertura(P, dx, dy, 3.30)` y `c_alto = _cobertura(P, dx, dy, 5.5)`.
- Altura meta: 5.5 m si `c_alto − c_bajo ≥ 0.05`. 3.30 m si `c_alto − c_bajo ≤ 0.02`. Entre esos dos valores, conserva la
  meta anterior (histéresis contra el vaivén).
- Botón: SUBIR si `z_v17` está más de 0.25 m bajo la meta, BAJAR si está más de 0.25 m arriba, QUEDARSE si no.
- **B4\* (oráculo, solo para medir el techo):** lo mismo con la posición verdadera del ladrón. No puede volar; dice cuánto
  rinde, como mucho, decidir bien la altura.
- Dónde va: `entorno.regla_b4()` al lado de `regla_b2` y `--pol b4,b4o` en `medir_ia_aporta.py`. Es trabajo del
  implementador, con una prueba que verifique que B4 nunca aprieta un botón prohibido.
- **Sin hacerse trampa:** los umbrales (0.05 y 0.02) se ajustan con otra semilla (`--semilla 7`, 256 partidas, probando
  0.02, 0.05 y 0.10). El informe se hace con la semilla de siempre y 512 partidas. Se mide en la cancha de la V17.3 (paneles
  reales) y en la vieja (`--set ANCHO_PANEL_V17=1.0 --set ALTO_PANEL_V17=1.9,2.2`) para comparar con la V17.2.

**Compuerta de decisión** (antes de gastar pasos en la V17.4):
- **B4\* ≤ B3 + 3 puntos:** decidir bien la altura casi no da nada en esta cancha. Entonces "siempre subir" es casi lo mejor,
  y entrenar más la altura no va a mostrar que la IA aporta. Lo honesto para el documento es: "la IA aprende sola lo que hace
  la mejor regla simple" (plan, sección 2, defendible). La siguiente palanca grande sería D-059 C (que la red decida los
  primeros 2-3 s tras perderlo). Eso toca la regla dura 3 y **solo lo decide Brahian**. No lo propongo aquí.
- **B4 > B3 + 5 puntos:** hay una estrategia que vale la pena aprender. Se hace la V17.4 (sección 4), y la IA tiene que
  ganarle a **B4**, no solo a B3.
- **En medio:** se hace la V17.4, sabiendo que el margen esperado es chico.

## 4. Pregunta 3: tres cambios para la V17.4

Se parte de la V17.3 (paneles reales y suavidad vertical ×0.5), que es el control. Cada cambio va en una corrida propia con
la semilla 17, 512 entornos y la cancha de la V17.3. Todo se mide con
`herramientas/medir_ia_aporta.py v17 --pol b0,b3,b4,<modelo>,<modelo>-est --n 512`.

**Dos agregados de medida** (no entrenan nada; los necesitan los criterios):
1. Vaivén **de la red**: contar cambios de sentido solo en los pasos donde decide la red (`d17`), sin el reinicio de la
   búsqueda.
2. Altura pedida media cuando el ladrón está a < 3 m de una V, contra la de cuando está en campo abierto.

Con 512 partidas, 3 puntos de M1 no se distinguen del ruido. Por eso a los 10 M se decide con señales internas y M1 solo
cuenta a los 50 M.

### Cambio 1 · Darle a la red la altura pedida y la distancia del ladrón a la V

- **Hipótesis:** la red no puede atar la altura a la situación si no ve qué altura ya pidió ni dónde está el ladrón respecto
  a la V. Por eso aprieta SUBIR y BAJAR de más.
- **Archivo y función:** `entorno.py`, `_sensores()`. Se reusan dos casillas muertas en la V17, así `OBS_DRON` sigue en 195
  y la V15 y la V16 no cambian:
  - Línea 1919, `(z_ia − dz)/2`. En la V17 pasa a ser la altura pedida: `(z_v17 − Z_SEGURA) / (Z_MAX_V17 − Z_SEGURA)`.
  - Línea 1904, `modo == BUSQUEDA_IA`, que siempre vale 0 porque `PERDIDA_IA = False`. En la V17 pasa a ser la distancia
    horizontal entre la posición estimada del ladrón y el punto **del mapa LiDAR** más cercano, dividida por 5 m y recortada a
    1 (1 si no hay nada mapeado). Usa solo lo que la Jetson tendría: no usa la verdad del simulador.
  - Prueba nueva: en la V17 las dos casillas valen eso, y en la V15 y la V16 la observación no cambia.
- **Pasos:** 10 M desde cero (~50 min), contra la V17.3 a los 10 M.
- **Se acepta si:** el vaivén de la red baja ≥ 50 % frente a la V17.3, **y** la altura pedida cerca de la V queda ≥ 1 m más
  alta que en campo abierto, **y** M1 no cae más de 3 puntos.

### Cambio 2 · Entropía en rampa: 0.01 al principio, 0.003 al final

- **Hipótesis:** 0.01 sirve para no colapsar al principio (la V17.1 con 0.003 colapsó a los 1.3 M), pero desde los 25 M
  mantiene la política indecisa. Lo que entrena cobra 18.30 contra 23.35 de B3. Bajarla tarde deja que se comprometa con lo
  que ya aprendió.
- **Archivo y función:** `entrenar_master.py`. Un callback que cambia `model.ent_coef` según `num_timesteps`: 0.01 hasta
  los 10 M, baja en línea recta hasta 0.003 a los 20 M y se queda ahí. Banderas nuevas `--ent-final 0.003` y
  `--ent-rampa 1e7,2e7`. No toca el entorno.
- **Pasos:** se continúa desde el checkpoint de 10 M de la mejor corrida (V17.3 o cambio 1) hasta los 25 M, con rampa y sin
  rampa (~75 min cada una).
- **Se acepta si:** el retorno **estocástico** llega al menos al de B3 en la misma cancha (eso dice que, para su propia
  recompensa, ya es tan buena como B3), **y** la probabilidad de la preferida es ≥ 0.75, **y** M1 no queda peor que sin
  rampa.

### Cambio 3 · Horizonte de ~20 s, con la guía coherente

- **Hipótesis:** el beneficio de estar arriba se cobra en rachas de 30 s, y con gamma 0.99 la red ve ~10 s.
- **Archivo y función:** `entrenar_master.py` con `--gamma 0.995` (ya existe) **y además** `GAMMA_GUIA = 0.995` en
  `entorno.py` (línea 684; probar `--set GAMMA_GUIA=0.995`). Las dos van juntas. Con gamma 0.995 y `GAMMA_GUIA` en 0.99, los
  potenciales dejan de ser neutros: cada paso cobra de más −0.005 × potencial. Con el de la racha en 3, eso es hasta −0.015
  por paso, unas −4.5 por cada racha de 30 s, casi la mitad del bono de 10. Sería un castigo escondido a las rachas largas.
- **Pasos:** 10 M desde cero, contra la V17.3 a los 10 M. Se hace solo si con los cambios 1 y 2 todavía no le gana a B3.
- **Se acepta si:** M1 sube ≥ 3 puntos, o empata en M1 con mejor retorno estocástico y menos vaivén de la red.

**Después:** los cambios que pasen se juntan en una corrida de 50 M (~4 h) con la regla de D-052. **Aporta** si M1 ≥ el
mayor de B3 y B4 + 5 puntos, con M2, M3 y seguridad no peores. Si le gana a B3 pero empata con B4, el resultado es "aprendió
sola lo que hace la regla diseñada".

**Reglas duras:** ninguno de los tres cambios toca el gimbal (−45..+15°), la geocerca, la búsqueda determinista
(`PERDIDA_IA = False`), el árbitro, el humano en el lazo ni la altura segura. La casilla que se reusa de `BUSQUEDA_IA` solo
cambia lo que la red ve: la búsqueda sigue siendo la regla.

## 5. Lo que no se puede saber con estos datos

- **Dónde está la IA cuando decide:** no hay histograma de `z_v17`. No se sabe si su QUEDARSE (71 %) es "quedarse arriba" o
  "quedarse abajo".
- **Si seguía mejorando:** solo hay dos puntos (10 y 50 M). Los checkpoints de cada millón están en
  `modelos_v17_2/checkpoints/`. Un barrido de 10, 20, 30, 40 y 50 M con 256 partidas lo diría. La entropía plana desde los 25 M
  sugiere que no.
- **Cuánto más se puede ganar con la altura:** lo dirá B4\*.
- **Si esto vale con los paneles reales:** con paneles más grandes, subir pesa más y B3 probablemente sube. Hay que esperar
  `v173_base_b*.json` (todavía no existen).
- **El ruido del retorno:** los JSON dan medias sin desviación. La diferencia de retorno entre la IA determinista y B3 (22.99
  contra 23.35) no se puede calificar.
- **La comparación pareada:** todas las políticas usan las mismas 512 semillas. Una prueba pareada partida por partida
  (McNemar) daría un margen menor que ±4.3, pero `medir_ia_aporta.py` no guarda el resultado de cada partida.
