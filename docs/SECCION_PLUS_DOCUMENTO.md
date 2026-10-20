# Sección para el documento · El plus: mantener a la vista a un sospechoso

Texto para que Tania lo copie al Word. Las cifras llevan el archivo de donde salen (carpeta `03_SIMULACION_RL/informes/` salvo
que se diga otra). **Todo es simulación; el plus no ha volado.** Las filas marcadas **[pendiente]** se llenan cuando
Simulación V17 termine las corridas de la noche (`docs/ENCARGOS_19OCT.md`). Las capturas están en
`08_EVIDENCIA_Y_DIAGRAMAS/capturas/` (todas son imágenes de la simulación o del modelo 3D: no hay fotos de personas reales).

## 1. Qué es el plus y qué no

El mínimo del proyecto de grado (detenerse y subir ante un obstáculo o una persona) es independiente de esta parte.
El **plus** añade una función: cuando el operador confirma con un clic quién es el sospechoso, el dron lo mantiene a la
vista aunque se esconda tras unos paneles. Se desarrolló y se midió **solo en simulación** (mundo propio en NumPy,
`entorno.py`). El sistema combina **reglas deterministas** con **una política aprendida por refuerzo** (PPO).

- La **política** elige, solo mientras el objetivo está fijado y a la vista, entre siete acciones: quedarse, rodear a la
  izquierda o a la derecha, acercarse, alejarse, subir y bajar.
- Las **reglas** hacen el seguimiento fino, la búsqueda tras perder al objetivo, el árbitro de seguridad, la geocerca y la
  evasión ante una amenaza.
- **El humano** decide quién es el sospechoso. La IA nunca lo decide.
- **La red no estabiliza nada:** eso lo hacen los controladores de ArduPilot (incluido el roll) y los servos del pan-tilt.

Reglas duras que nunca se relajan: tilt del pan-tilt entre −45° y +15° (con topes mecánicos); el dron no sale de la zona; humano en el lazo; árbitro de
seguridad; altura mínima de 3.30 m con personas a menos de 8 m (con 0.5 m de margen por el error del barómetro, D-063).

## 2. El juego dron-ladrón

- **Escenario:** una cancha de fútbol con una zona de 30 × 30 m, dos conjuntos de dos paneles en V de 90° (cada panel de
  ~1.5 m de ancho y ~2.2-2.3 m de alto, medidas dadas por Brahian y por confirmar con cinta, D-066), un ladrón y un civil.
  Dibujo: `docs/v17_zona_ia.png`. Captura: `capturas/v17_cancha_arriba.jpg`.
- **Ladrón:** corre, se agacha, gatea, se recuesta contra el panel, salta para agarrar el dron y se esconde tras las V.
  **Civil:** camina y a veces mira o graba al dron (`docs/PROGRESO_V16.md` de la rama `v16-simulacion`, fase A2).
- **El dron del plus (variante H, D-074):** una base impresa con **dos servos que mueven el yaw (pan) y el pitch (tilt)**, sin roll (el roll lo
  controla el dron); en ella van la cámara CSI principal y el LiDAR TF-Luna **juntos**; una **segunda CSI fija mirando al piso**; y el TF03 fijo
  al chasis. El mínimo usa otra configuración (variante G: CSI fija y TF03 fijo, sin gimbal). El plus se entrena en H.
- **Por qué el TF03 va fijo y el TF-Luna en el pan-tilt (D-075):** el TF03 es grande y de cable grueso (ya trabó el pitch del gimbal anterior);
  la misión tiene dos fases en el mismo vuelo y, con el pan-tilt en pan 0° y tilt −5°, el plus equivale a la cámara fija del mínimo mientras el TF03
  conserva el frenado de seguridad; y el TF-Luna mide lo que mira la cámara sin sincronizar ángulos de servo con el TF03.
- **Sensores simulados (H):** cámara principal CSI de 62.2° × 48.8° (nominal, sin medir) con pan y tilt, cámara al piso, TF03 al chasis y TF-Luna
  junto a la cámara, con ruido, retardo y pérdidas de detección. **Ojo:** las corridas de la V17 de este documento se entrenaron antes con la cámara
  USB de 38.9° y un gimbal virtual; hay que repetirlas con H (**[pendiente]**).
- **Gana el dron** si mantiene al ladrón a la vista hasta que se rinde; **gana el ladrón** si alcanza al dron, si lo pierde o si
  no lo encuentra (D-035).

## 3. Cómo se mide si la IA aporta

**Métrica principal (M1, D-059):** porcentaje de partidas de 5 min con una racha de **30 s seguidos** con el ladrón a la vista
y el identificador correcto. Con 60 s casi nadie lo logra en esta cancha (1 % con las reglas solas, `docs/PROGRESO_V17.md`,
paso 8). Secundarias: re-adquisición en ≤ 10 s tras perderlo y rendición del ladrón. Seguridad (alcanzado, choques, geocerca,
gimbal) debe quedar igual. El margen de error de M1 con 512 partidas es de unos ±4 puntos.

**Líneas base** (misma partida y mismas reglas debajo; solo cambia quién elige la acción):

| Línea | Qué hace |
|---|---|
| B0 | Siempre quedarse (solo reglas) |
| B1 | Acción al azar |
| B2 | Regla de posicionamiento: la acción que más aumenta la fracción de la zona de escape que el dron ve |
| B3 | Siempre subir (a 5.5 m) |
| B4 | Sube a 5.5 m si desde arriba ve más zona de escape y baja si no; B4\* usa la posición verdadera del ladrón (solo como techo) |
| B5 | **[pendiente]** maestro que sigue la ruta de búsqueda de Brahian (sección 5) |

## 4. Resultados, tal cual (incluidos los malos)

**4.1 La política de la V15 no aportaba nada** (`informes/diagnostico_v17_ia_aporta.md`). Misión completa del nivel 4, 256
partidas: custodia de 60 s: 11.3 % la política (229 M pasos), 10.2 % siempre quedarse, 7.8 % al azar (margen ±3.9). El barrido
de checkpoints es plano: 0.96-0.97 de media de 7 M a 230 M pasos (`informes/barrido_v15.md`). Causa medida: con el ladrón a la
vista, 9 de las 10 acciones hacían lo mismo, y el entrenamiento aprendía también de pasos en los que la red no decidía.

**4.2 La V17.2 en la cancha de prueba (paneles de 1.0 m), 512 partidas** (`informes/v17/v172_50M_*.json`):

| | M1 | Rendición | Alcanzado |
|---|---:|---:|---:|
| V17.2 a 50 M pasos (red, determinista) | 54.3 % | 22.5 % | 0.2 % |
| B0 siempre quedarse | 48.4 % | 14.5 % | 0.2 % |
| B3 siempre subir | 56.2 % | 22.3 % | 0.2 % |

La red supera a "solo reglas" por 5.9 puntos y **empata con "siempre subir"** (1.9 puntos, dentro del ruido de ±4.3).

**4.3 La cancha real, con paneles de 1.5 × 2.2-2.3 m, 512 partidas** (`informes/v17/v173_base_b*.json`, `b4_real_*.json`,
`v172_real_*.json`). El escenario es mucho más difícil: tapa más.

| | M1 | Vista total (s) | Re-adquisición ≤ 10 s | Alcanzado |
|---|---:|---:|---:|---:|
| B0 siempre quedarse | 11.7 % | 84.6 | 60.0 % | 0 % |
| B1 azar | 13.5 % | 82.6 | 61.6 % | 0 % |
| B2 posicionamiento | 17.2 % | 86.2 | 60.0 % | 0 % |
| **B3 siempre subir** | **24.6 %** | 87.3 | 68.3 % | 0 % |
| B4 altura por cobertura | 19.5 % | 85.9 | 63.3 % | 0 % |
| B4\* con la posición verdadera | 22.5 % | 87.0 | 64.0 % | 0.2 % |
| V17.2 (50 M, sin afinar en esta cancha) | 19.3 % | 86.5 | 63.0 % | 0 % |
| V17.2 estocástica | 19.1 % | 83.9 | 62.8 % | 0 % |
| V17.3 (10 M, multa vertical 0.5) | 11.7 % | 84.6 | 60.0 % | 0 % |
| V17.4 / con D-069 | **[pendiente]** | | | |

Lectura honesta: en la cancha real la V17.2 sin afinar queda **7.6 puntos sobre "solo reglas"** y **5.3 por debajo de
"siempre subir"**. La V17.3 se quedó quieta (colapsó) porque la multa por mover la altura era demasiado fuerte.

**4.4 La altura ya no da más (D-067/D-068).** Ni la regla B4\*, con la posición verdadera del ladrón, supera a "siempre subir". Con
la búsqueda determinista volviendo a 3.30 m cada vez que lo pierde, subir siempre es casi lo mejor que se obtiene de la altura.
Por eso no se entrena más la altura: lo que queda es adaptar la política a la cancha real y probar que la red decida también el
tramo tras perder al ladrón (D-069, reversible).

## 5. La ruta de búsqueda de Brahian

Brahian dictó una ruta de búsqueda como **consejos, no como reglas duras**, para enseñársela a la red por imitación
(D-071, `docs/RUTA_BUSQUEDA_BRAHIAN.md`, con diagrama):

1. giro de 360° y mapa de puntos de los paneles;
2. ir detrás de cada V a 3.30 m y a unos 4-5 m;
3. recorrer la parte de atrás como un cuadrado por las esquinas;
4. mirar de frente con vaivén izquierda-derecha;
5. pasar a la otra V;
6. moverse rápido y nunca quedarse quieto;
7. que funcione también sin poder subir.

Las distancias son valores de partida, no medidos. **La ruta cuenta como aporte de la IA** si la red supera a "siempre subir" y a
"solo reglas" por 5 puntos de M1, o si B5 es mejor que B3 y la red queda a menos de 3 puntos de B5. **Resultado: [pendiente].**

## 6. El motor gráfico y la estación de tierra

- **Estación de tierra (web, la que irá en la Jetson):** cinco modos (cámara del dron con las cajas de YOLO y las órdenes
  que manda la Jetson, mundo 3D, mapa de puntos, ingeniería y vuelo real). El operador confirma al sospechoso con un botón.
  Capturas: `capturas/estacion_modo_dron.jpg`, `capturas/estacion_modo_3d.jpg`.
- **Mundo realista en Unreal Engine 5** (D-065), alimentado por las repeticiones de la simulación (que solo se dibujan; Unreal
  no decide nada): la cancha, las V, el dron y los maniquíes con las posturas. Capturas: `capturas/unreal_partida_3000.jpg`,
  `capturas/unreal_maniquies_ladron_corriendo.jpg`, `capturas/unreal_vuelo_cruce.jpg`.
- **Modelo 3D del dron real** para la estación y para Unreal: `capturas/dron_real_lado.jpg`.

## 7. Qué se puede afirmar y qué no

- **Se puede afirmar:** el diagnóstico medido de por qué la V15 no aprendía; el rediseño que lo corrige (acciones con efecto,
  máscara de acciones, recompensa por racha); y que la política V17.2 **supera a "solo reglas"** en las dos canchas.
- **No se puede afirmar:** que supere a "siempre subir", ni que funcione en el dron: todo es simulación con parámetros estimados
  (paneles por medir, alcance del TF-Luna según el color, retardos de los servos).
- Las cifras de la V15 ("92 % de misión completa", "~89 % de custodia a 60 s") son de otra versión y otro criterio (antes de
  entrenar, `evaluacion_v15-comparacion-v14.md`, D-046): **no deben mezclarse** con las de la V17.
- Llevar la política a la Jetson exigiría calcular allá las mismas 195 entradas y los 7 botones; hoy ese código no existe.

## 8. Antes de dar esto por cerrado

1. Llenar los **[pendiente]** de 4.3 y de la sección 5 con los informes de la noche.
2. Medir los paneles con cinta (alto, ancho y color) y repetir las líneas base si cambian.
3. Brahian confirma por escrito D-069 (que la red decida tras perder al ladrón), que toca la regla dura 3.
