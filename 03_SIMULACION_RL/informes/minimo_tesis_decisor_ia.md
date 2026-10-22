# Decisor IA del mínimo indispensable (fase G)

Generado por `minimo_tesis/evaluar_decisores.py` · 100 vuelos por variante · semilla base 2026 · 2026-10-20 · 505 s

Se comparan tres formas de DECIDIR la intervención (detención y ascenso), con los mismos sensores (ruido y retardo de 100 ms) y el mismo control de ArduPilot:

- **Reglas:** umbrales fijos (obstáculo por distancia de frenado y tiempo al choque; persona según el árbitro).
- **IA sola:** un clasificador MLP decide con las entradas que tiene la Jetson.
- **IA + envolvente:** la misma IA dentro de las reglas duras: el bloqueo frontal (LiDAR < 3 m avanzando) y la persona a menos de 3 m mandan siempre, y el ascenso por una persona solo lo autoriza el árbitro (< 3 m, o < 8 m acercándose); antes, la IA solo puede DETENER. Es la regla dura 5 tal como está escrita (el árbitro autoriza; el LiDAR y la parada mandan) y es la versión que iría al dron.
- **IA + envolvente estricta:** además, una persona a menos de 3 m obliga a detenerse (más estricto que la regla).

## 1. El clasificador

- Arquitectura: MLP de scikit-learn 32-16, ReLU; 15 entradas: detectada, alto_caja, ancho_caja, area_caja, angulo_abs, d_angulo_abs, confianza, cuadros_seguidos, lidar, lidar_util, v_propia, d_seguimiento, v_acercamiento, v_lateral, t_sin_deteccion.
- Datos: vuelos sin intervención en mundos aleatorios (velocidades de 0 a 8 m/s; personas quietas, que vienen, que cruzan, paralelas o al azar; panel o no; sensores degradados al azar). Etiqueta automática con la verdad del simulador: "si el piloto sigue igual, ¿en los próximos 3 s choca o una persona queda a menos de 2 m?".
- Separación por semillas (mundos distintos): entrenamiento 2551725 cuadros (13 % con riesgo), validación 499021, prueba 533085 (12 % con riesgo).
- Umbral 0.7 y 1 cuadro(s) seguidos, elegidos en lazo cerrado sobre mundos de VALIDACIÓN (no con este protocolo): el mínimo de activaciones innecesarias sin dejar pasar más riesgos que las reglas.

Desempeño en la PRUEBA (mundos nunca vistos), por cuadro:

| AUC-ROC | Precisión media (AP) | Exhaustividad | Precisión | Tasa de falsos positivos |
|---:|---:|---:|---:|---:|
| 0.961 | 0.874 | 67.4 % | 97.1 % | 0.3 % |

Matriz de confusión (prueba, por cuadro, con el umbral elegido):

| | Predice CONTINUAR | Predice DETENER |
|---|---:|---:|
| Sin riesgo real | 470519 | 1231 |
| Con riesgo real | 19990 | 41345 |

Curvas ROC y precisión-exhaustividad: `minimo_tesis_decisor_curvas.png`. La exhaustividad por cuadro no es la seguridad: un riesgo dura muchos cuadros y basta uno (o k seguidos) para intervenir; la seguridad se mide abajo, en lazo cerrado.

## 2. Mundos de prueba en lazo cerrado (la comparación menos sesgada)

3840 vuelos en 60 mundos aleatorios de PRUEBA (semillas que no se usaron ni para entrenar ni para elegir el umbral): velocidades de 0 a 8 m/s, todo tipo de personas, paneles y sensores degradados al azar. 2043 vuelos (53 %) habrían tenido riesgo físico sin sistema.

| Decisor | Riesgos no evitados | Choques | Persona a < 2 m bajo 3.30 m (vuelos) | Distancia mínima a personas bajo 3.30 m (p1 / mediana, m) | Activaciones innecesarias | Tiempo detenido sin necesidad (s) | Tiempo detenido total (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Sin sistema | 2043 | 1681 | 1488 | 0.08 / 3.30 | — | — | — |
| Reglas | 224 (11.0 %) | 117 | 516 | 0.27 / 6.05 | 161 | 2750 | 42978 |
| IA sola | 121 (5.9 %) | 94 | 118 | 0.78 / 9.10 | 102 | 1751 | 43436 |
| IA + envolvente | 148 (7.2 %) | 97 | 212 | 0.46 / 8.80 | 109 | 1887 | 43575 |
| IA + envolvente estricta | 148 (7.2 %) | 97 | 212 | 0.46 / 8.80 | 135 | 2407 | 44097 |
| IA + envolvente, ascenso sin veto del árbitro (solo referencia) | 121 (5.9 %) | 94 | 118 | 0.78 / 9.10 | 109 | 1887 | 43575 |

Por velocidad del piloto (vuelos con persona a < 2 m bajo 3.30 m / riesgos no evitados / choques):

| Decisor | Piloto ≤ 4 m/s (2212 vuelos) | Piloto > 4 m/s (1628 vuelos) |
|---|---:|---:|
| Sin sistema | 661 / 946 / 789 | 827 / 1097 / 892 |
| Reglas | 80 / 10 / 6 | 436 / 214 / 111 |
| IA sola | 26 / 11 / 6 | 92 / 110 / 88 |
| IA + envolvente | 34 / 11 / 6 | 178 / 137 / 91 |
| IA + envolvente estricta | 34 / 11 / 6 | 178 / 137 / 91 |
| IA + envolvente, ascenso sin veto del árbitro (solo referencia) | 26 / 11 / 6 | 92 / 110 / 88 |

Riesgo no evitado: con el decisor al mando, la persona igual quedó a menos de 2 m del dron (a su alcance) o el panel a menos de 0.5 m. Incluye los casos imposibles (un panel a 5 m con el dron a 8 m/s, una persona que corre hacia el dron desde muy cerca).

## 3. Protocolo del comité y escenarios de discriminación (nominal)

Éxito en el protocolo: si debe activarse, se activa y no choca; si no, no se activa y no choca. En los escenarios de discriminación (f) el éxito es la decisión correcta POR VUELO: activarse si y solo si en ese mismo vuelo, sin sistema, la persona habría quedado a menos de 2 m. Innecesarias: activaciones en vuelos que sin sistema no habrían tenido ese riesgo físico.

| Escenario | Éxito Reglas | Éxito IA sola | Éxito IA + envolvente | Éxito IA + envolvente estricta | Choques R/IA/IA+E/est. | Innecesarias R/IA/IA+E/est. | Riesgo → comando (s) R / IA / IA+E / est. |
|---|---:|---:|---:|---:|---:|---:|---:|
| a) Panel fijo, avance a 1 m/s | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0.09 / -1.22 / -1.22 / -1.22 |
| a) Panel fijo, avance a 2 m/s | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0.10 / -0.94 / -0.94 / -0.94 |
| a) Panel fijo, avance a 3 m/s | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0.10 / -0.79 / -0.79 / -0.79 |
| a) Panel fijo, avance a 4 m/s | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0.09 / -0.25 / -0.25 / -0.25 |
| b) Persona quieta, avance a 1.5 m/s | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0.08 / 1.01 / 1.01 / 1.01 |
| b) Persona quieta, avance a 3.0 m/s | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0.10 / -1.15 / -1.15 / -1.15 |
| c) Persona de frente que camina (1.4 m/s), avance a 1 m/s | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0.06 / -0.74 / -0.74 / -0.74 |
| c) Persona de frente que corre (3.3 m/s), avance a 1 m/s | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0.11 / -1.47 / -1.47 / -1.47 |
| d) Persona que cruza lejos y camina (1.4 m/s), avance a 1 m/s | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | — / — / — / — |
| d) Persona que cruza lejos y corre (3.3 m/s), avance a 1 m/s | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | — / — / — / — |
| e) Modo estático: persona que viene y camina (1.4 m/s) | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0.11 / 1.25 / 1.25 / 1.25 |
| e) Modo estático: persona que viene y corre (3.3 m/s) | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0.12 / -0.87 / -0.87 / -0.87 |
| e) Modo estático: persona que pasa de lado a 5 m (1.4 m/s) | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | — / — / — / — |
| f) Cruza 3-4 m por delante del dron y sigue (no debe activarse) | 75 % [66, 82] | 97 % [92, 99] | 97 % [92, 99] | 88 % [80, 93] | 0 / 0 / 0 / 0 | 25 / 3 / 3 / 12 | 0.09 / -0.33 / -0.33 / 1.07 |
| f) Cruza justo por donde pasa el dron (debe activarse) | 61 % [51, 70] | 70 % [60, 78] | 70 % [60, 78] | 68 % [58, 76] | 0 / 0 / 0 / 0 | 39 / 30 / 30 / 32 | -0.30 / -0.53 / -0.54 / -0.51 |
| f) Viene de frente, 3 m al costado de la trayectoria (no debe activarse) | 96 % [90, 98] | 96 % [90, 98] | 96 % [90, 98] | 96 % [90, 98] | 0 / 0 / 0 / 0 | 4 / 4 / 4 / 4 | -2.08 / -2.48 / -2.48 / -2.48 |
| f) Viene de frente, 1 m al costado (debe activarse) | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0.10 / -1.13 / -1.13 / -1.13 |
| f) Camina delante en el mismo sentido, más rápido que el dron (no debe activarse) | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 100 % [96, 100] | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | — / — / — / — |

| Total | Reglas | IA sola | IA + envolvente | IA + envolvente estricta |
|---|---:|---:|---:|---:|
| Éxito, 13 variantes del protocolo | 100.0 % [99.7, 100.0] | 100.0 % [99.7, 100.0] | 100.0 % [99.7, 100.0] | 100.0 % [99.7, 100.0] |
| Éxito, 5 de discriminación | 86.4 % [83.1, 89.1] | 92.6 % [90.0, 94.6] | 92.6 % [90.0, 94.6] | 90.4 % [87.5, 92.7] |
| Choques (todos) | 0 | 0 | 0 | 0 |
| Activaciones innecesarias (todos) | 68 | 37 | 37 | 48 |
| Tiempo detenido sin necesidad (s, todos) | 822 | 464 | 464 | 574 |
| Riesgos físicos omitidos (necesaria y no se activó) | 0 | 0 | 0 | 0 |
| Paradas del operador | 128 | 118 | 117 | 117 |
| Vuelos con persona a < 2 m bajo 3.30 m (todos) | 0 | 0 | 0 | 0 |

## 4. Condiciones degradadas

Por condición, sumando las 18 variantes (13 del protocolo + 5 de discriminación), 100 vuelos cada una: éxitos, choques e innecesarias.

| Condición | Reglas: éxito · choques · innec. | IA sola: éxito · choques · innec. | IA + envolvente: éxito · choques · innec. | IA + envolvente estricta: éxito · choques · innec. |
|---|---:|---:|---:|---:|
| C0 Nominal | 96.2 % · 0 · 68 | 97.9 % · 0 · 37 | 97.9 % · 0 · 37 | 97.3 % · 0 · 48 |
| C1 YOLO recall 0.85 (sol de frente) | 96.2 % · 0 · 69 | 97.8 % · 0 · 40 | 97.8 % · 0 · 40 | 97.2 % · 0 · 50 |
| C2 YOLO recall 0.70 (desenfoque) | 96.2 % · 0 · 69 | 97.6 % · 0 · 44 | 97.6 % · 0 · 44 | 97.1 % · 0 · 53 |
| C3 Oclusión: medio cuerpo visible | 95.6 % · 0 · 80 | 97.0 % · 0 · 54 | 96.4 % · 0 · 64 | 96.1 % · 0 · 71 |
| C4 Oclusión: solo torso visible | 95.6 % · 0 · 80 | 96.8 % · 0 · 58 | 96.2 % · 0 · 69 | 95.7 % · 0 · 78 |
| C5 LiDAR ruido ×3 y 5 % sin retorno | 96.3 % · 0 · 66 | 97.8 % · 0 · 40 | 97.8 % · 0 · 40 | 97.2 % · 0 · 51 |
| C6 Latencia total 200 ms | 96.2 % · 0 · 68 | 97.9 % · 0 · 37 | 97.9 % · 0 · 37 | 97.3 % · 0 · 48 |
| C7 Latencia total 300 ms | 96.2 % · 0 · 68 | 97.9 % · 0 · 37 | 97.9 % · 0 · 37 | 97.3 % · 0 · 48 |
| C8 Viento de cola 3 m/s con ráfagas | 95.1 % · 0 · 88 | 97.8 % · 0 · 40 | 97.7 % · 0 · 41 | 96.8 % · 0 · 57 |
| C9 Viento de cola 5 m/s con ráfagas | 95.2 % · 0 · 87 | 97.7 % · 0 · 42 | 97.6 % · 0 · 44 | 96.7 % · 0 · 60 |
| C10 Combinada: recall 0.85 + medio cuerpo + LiDAR + 200 ms + viento 4 m/s | 94.4 % · 0 · 101 | 96.6 % · 0 · 61 | 96.1 % · 0 · 71 | 95.5 % · 0 · 81 |
| C11 Extrema: YOLO recall 0.40 | 96.1 % · 0 · 71 | 95.4 % · 0 · 82 | 95.3 % · 0 · 84 | 95.2 % · 0 · 87 |
| C12 Extrema: solo cabeza y hombros (15 % del alto) | 95.2 % · 0 · 84 | 93.9 % · 1 · 108 | 93.6 % · 1 · 113 | 93.4 % · 1 · 116 |
| C13 Extrema: latencia total 500 ms | 96.2 % · 0 · 68 | 97.9 % · 0 · 37 | 97.9 % · 0 · 37 | 97.3 % · 0 · 48 |

## 5. Velocidad máxima segura (m/s, detenerse con margen en ≥ 95 %)

| Condición | Escenario | Reglas | IA sola | IA + envolvente | IA + envolvente estricta |
|---|---|---:|---:|---:|---:|
| C0 Nominal | Panel fijo | 5 | 5 | 5 | 5 |
| C0 Nominal | Persona quieta | 4 | 12 | 12 | 12 |
| C0 Nominal | Persona de frente corriendo | 8 | 12 | 12 | 12 |
| C7 Latencia total 300 ms | Panel fijo | 5 | 5 | 5 | 5 |
| C7 Latencia total 300 ms | Persona quieta | 4 | 12 | 12 | 12 |
| C7 Latencia total 300 ms | Persona de frente corriendo | 5 | 12 | 12 | 12 |
| C10 Combinada: recall 0.85 + medio cuerpo + LiDAR + 200 ms + viento 4 m/s | Panel fijo | 5 | 5 | 5 | 5 |
| C10 Combinada: recall 0.85 + medio cuerpo + LiDAR + 200 ms + viento 4 m/s | Persona quieta | 4 | 12 | 12 | 12 |
| C10 Combinada: recall 0.85 + medio cuerpo + LiDAR + 200 ms + viento 4 m/s | Persona de frente corriendo | 7 | 12 | 12 | 12 |
| C12 Extrema: solo cabeza y hombros (15 % del alto) | Panel fijo | 5 | 5 | 5 | 5 |
| C12 Extrema: solo cabeza y hombros (15 % del alto) | Persona quieta | 4 | 7 | 7 | 7 |
| C12 Extrema: solo cabeza y hombros (15 % del alto) | Persona de frente corriendo | 0 | 12 | 7 | 7 |

## 6. Lectura

- **Protocolo del comité (13 variantes):** los cuatro decisores cumplen el 100 %, sin choques y sin ninguna persona a menos de 2 m con el dron por debajo de 3.30 m. El protocolo no distingue entre ellos: sus escenarios son claros (panel o persona en la trayectoria, cruce lejano) y las reglas ya los resuelven.
- **Discriminación (personas cerca de la trayectoria que no van a chocar):** éxito por vuelo 86.4 % con las reglas, 92.6 % con la IA sola y 92.6 % con la IA + envolvente; activaciones innecesarias 68 / 37 / 37 y tiempo detenido sin necesidad 822 / 464 / 464 s. Riesgos omitidos: 0 / 0 / 0. La IA sola omitía riesgos con personas que entran de lado al campo de la cámara a 5-6 m; la salvaguarda geométrica de la envolvente (persona seguida que va a pasar a < 2 m en menos de 1.5 s) los recupera, a cambio de parte de las innecesarias.
- **La envolvente estricta** (persona a < 3 m obliga) vuelve a dar lo mismo que las reglas (48 innecesarias): las activaciones innecesarias de las reglas vienen justamente de personas que pasan a menos de 3 m sin llegar a 2 m. Por eso la regla dura 5 se aplica como está escrita: el árbitro autoriza, no obliga.
- **Anticipación (riesgo → comando, protocolo):** media 0.10 s con las reglas y -0.52 s con la IA + envolvente (negativo: la orden sale antes de que el riesgo, con los umbrales de las reglas, exista). La IA se adelanta casi en todos los escenarios; en los acercamientos lentos (persona quieta a 1.5 m/s, persona que camina hacia el dron quieto) decide más tarde que las reglas, pero igual con margen (sin choques ni personas a < 2 m).
- **Mundos de prueba (3840 vuelos nunca vistos):** con la IA + envolvente frente a las reglas: choques 117 → 97, riesgos no evitados 224 → 148, vuelos con una persona a < 2 m bajo 3.30 m 516 → 212, activaciones innecesarias 161 → 109 y tiempo detenido sin necesidad 2750 → 1887 s. Ninguno llega a cero: el conjunto incluye casos físicamente imposibles (panel a pocos metros con el dron a 8 m/s, persona que corre hacia el dron desde muy cerca).
- **Lo que NO mejora (honesto):** con el piloto a 4 m/s o menos (el LOIT_SPEED recomendado), la IA + envolvente deja 11 riesgos no evitados frente a 10 de las reglas (prácticamente igual), aunque 34 vuelos con persona a < 2 m bajo 3.30 m frente a 80: en la operación recomendada la mejora en seguridad es moderada y la ventaja más clara es la eficiencia (menos detenciones innecesarias). Por encima de 4 m/s la IA + envolvente deja 178 vuelos con persona a < 2 m y la IA sola 92: la diferencia es el veto del árbitro al ascenso (sube solo con la persona a < 8 m acercándose), que con acercamientos rápidos llega tarde; la variante de referencia sin ese veto da 92.
- **Condiciones degradadas (reglas → IA + envolvente):** YOLO recall 0.70 (desenfoque): éxito 96.2 → 97.6 %, innecesarias 69 → 44; Oclusión: medio cuerpo visible: éxito 95.6 → 96.4 %, innecesarias 80 → 64; Latencia total 200 ms: éxito 96.2 → 97.9 %, innecesarias 68 → 37; Combinada: recall 0.85 + medio cuerpo + LiDAR + 200 ms + viento 4 m/s: éxito 94.4 → 96.1 %, innecesarias 101 → 71. En las condiciones realistas la IA conserva su ventaja, sin choques. En la extrema de solo cabeza y hombros no: éxito 95.2 → 93.6 %, innecesarias 84 → 113, choques 0 → 1 (es el límite de la percepción para los dos).
- **Velocidad máxima segura (detenerse con margen):** con una persona quieta, 4 m/s con las reglas y 12 m/s con la IA + envolvente (la IA puede DETENER antes de los 8 m; las reglas no se activan antes); con una persona que corre hacia el dron, 8 → 12 m/s (con 300 ms de latencia, 5 → 12). Frente al panel son equivalentes (5 y 5 m/s; con la condición combinada la IA baja a 5 frente a 5 de las reglas).
- **Decisión pendiente (Brahian):** si el ascenso vertical de protección del mínimo cuenta como "evasión" (hoy lo veta el árbitro hasta los 8 m) o no. Con el LOIT_SPEED de 4 m/s recomendado el costo del veto es pequeño; por encima de 4 m/s es la principal fuente de personas a < 2 m.

## 7. Justificación del uso de IA en la decisión

En el mínimo indispensable del proyecto de grado, la inteligencia artificial no se limita a detectar personas: también decide si el dron debe intervenir. Esa decisión se modela como un problema de clasificación: a partir de las mediciones disponibles a bordo (la caja que entrega YOLO, la distancia del LiDAR, la velocidad estimada por ArduPilot y un seguimiento alfa-beta de la persona), un perceptrón multicapa estima la probabilidad de que, si el piloto mantiene su mando, en los próximos 3 s ocurra un choque o una persona quede a menos de 2 m del dron.

El uso de un modelo aprendido se justifica porque el riesgo depende de la combinación de varias magnitudes ruidosas (distancia estimada por el tamaño de la caja, rumbo, velocidad relativa, persistencia de la detección), y un conjunto de umbrales fijos debe elegir entre ser conservador, con detenciones innecesarias, o permisivo, con riesgos omitidos. El clasificador aprende esa frontera de decisión a partir de vuelos simulados etiquetados de forma automática con la verdad del simulador, sin intervención manual, y se evalúa en mundos que no participaron ni en el entrenamiento ni en la elección del umbral.

El aporte se observa en tres aspectos. Primero, en la discriminación: frente a personas que pasan cerca de la trayectoria sin riesgo real, el sistema con IA redujo las activaciones innecesarias de 68 a 37, y con ello el tiempo de misión perdido. Segundo, en la anticipación: la IA puede ordenar la detención antes del límite de 8 m que imponen las reglas, lo que eleva la velocidad de avance a la que el dron se detiene con margen frente a una persona inmóvil. En la simulación esa velocidad pasó de 4 m/s a 12 m/s. Tercero, en la operación con condiciones variadas: en 3840 vuelos de prueba los choques bajaron de 117 a 97 y los casos con una persona a menos de 2 m del dron por debajo de la altura segura, de 516 a 212.

La IA no reemplaza las reglas de seguridad: opera dentro de una envolvente de reglas duras. El bloqueo frontal por LiDAR y la parada del operador mandan siempre sobre ella; el árbitro de seguridad conserva la autoridad para autorizar el ascenso, y una salvaguarda geométrica detiene el dron si una persona seguida va a pasar a menos de 2 m en menos de 1.5 s. El operador humano puede intervenir en todo momento. Así, la IA aporta criterio donde las reglas fijas son ineficientes, y las reglas garantizan un comportamiento verificable donde la IA podría fallar.

Los resultados también muestran los límites del enfoque. Con la velocidad de avance recomendada (4 m/s), la IA deja prácticamente los mismos riesgos sin evitar que las reglas, aunque menos aproximaciones a menos de 2 m, y su ventaja más clara es la eficiencia. La percepción sigue siendo el límite cuando solo son visibles la cabeza y los hombros de la persona. Además, el detector se modeló estadísticamente, por lo que estos resultados deben confirmarse con el protocolo de campo descrito para el dron real.

## 8. Exportación a la Jetson

- `minimo_tesis/decision.pkl`: el modelo de scikit-learn con la normalización, el umbral y la persistencia.
- `minimo_tesis/decision.json`: pesos, sesgos, media y desviación de cada entrada, umbral, persistencia y el nombre y orden de las entradas. `decisor_ia.predecir_json` lo evalúa con NumPy puro (sin scikit-learn) y da lo mismo (prueba en `tests/test_decisor_ia.py`).
- En la Jetson, cada cuadro: calcular las 15 entradas con la caja de YOLO, el LiDAR, la velocidad del EKF y el seguimiento alfa-beta; evaluar la red (~1 000 multiplicaciones); si la probabilidad supera el umbral durante k cuadros, mandar la detención (y el ascenso si la envolvente lo autoriza). Las reglas duras corren al lado y mandan siempre.

Datos crudos: `minimo_tesis_decisor_ia.csv`. Repetición en el visor: grupo "Proyecto de grado", una opción por decisor.
