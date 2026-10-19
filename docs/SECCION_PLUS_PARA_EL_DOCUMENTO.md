# Sección para el documento · El plus: mantener a la vista a un sospechoso

Borrador del Arquitecto para Tania. Todas las cifras llevan el archivo de donde salen; las del plus **se actualizan** cuando
termine el afinado en la cancha real (`docs/ENCARGOS_19OCT.md`). Escrito en simulación: el plus todavía no ha volado.

## 1. Qué se hizo y qué no

El mínimo del proyecto de grado (detenerse y subir ante un obstáculo o una persona) es independiente de esto. El **plus**
añade una segunda función: una vez que un operador confirma con un clic quién es el sospechoso, el dron lo mantiene a la
vista aunque se esconda tras unos paneles. Se desarrolló y se midió **solo en simulación** (mundo propio en NumPy, `03_SIMULACION_RL/entorno.py`);
no se ha probado en el dron.

El sistema combina **reglas deterministas** (seguimiento, búsqueda tras perder al objetivo, árbitro de seguridad, geocerca)
con **una política aprendida por refuerzo** (PPO) que, solo mientras el objetivo está fijado y a la vista, elige entre
siete acciones: quedarse, rodear a la izquierda o a la derecha, acercarse, alejarse, subir y bajar. Nunca decide quién es
el sospechoso (lo confirma el operador) ni la maniobra de evasión ante una amenaza (la elige el árbitro), ni la búsqueda
cuando lo pierde. La red no estabiliza nada: eso lo hacen los controladores de ArduPilot y del gimbal.

## 2. El juego dron-ladrón

- **Escenario real propuesto:** una cancha de fútbol, una zona de 30 × 30 m con dos conjuntos de dos paneles en V de 90°
  (cada panel de ~1.5 m de ancho y ~2.2-2.3 m de alto, medidas dadas por Brahian y por confirmar con cinta, D-066), un
  ladrón y un civil (`docs/PLAN_V17_REFUERZO.md` §3, dibujo `docs/v17_zona_ia.png`).
- **El ladrón** corre, se agacha, gatea, se recuesta contra el panel, salta para agarrar el dron y se esconde tras las V; el
  civil camina y a veces mira o graba al dron (`docs/PROGRESO_V16.md` de la rama `v16-simulacion`, fase A2).
- **Sensores simulados:** cámara principal de 38.9° (la USB real), cámara al piso, LiDAR TF03 al chasis y TF-Luna junto
  a la cámara, con ruido, retardo y pérdidas de detección.
- **Reglas duras que no se negocian:** gimbal entre −45° y +15°; el dron no sale de la zona; humano en el lazo;
  árbitro de seguridad; altura mínima de 3.30 m con personas a menos de 8 m (con margen de 0.5 m por el error del barómetro,
  D-063).

## 3. Cómo se mide si la IA aporta

**Métrica principal (M1, D-059):** porcentaje de partidas de 5 min con una racha de **30 s seguidos** con el ladrón a la vista y
el identificador correcto. Se probó primero con 60 s, pero casi nadie lo logra en esta cancha (1 % con las reglas solas,
`docs/PROGRESO_V17.md`, paso 8). Secundarias: re-adquisición en ≤ 10 s tras perderlo y rendición del ladrón.
Seguridad (alcanzado, choques, geocerca, gimbal) debe quedar igual.

**Líneas base** (la misma partida y las mismas reglas debajo; solo cambia quién elige la acción):

| Línea | Qué hace |
|---|---|
| B0 | Siempre quedarse (solo reglas) |
| B1 | Acción al azar |
| B2 | Regla de posicionamiento: la acción que más aumenta la fracción de la zona de escape que el dron ve |
| B3 | Siempre subir |
| B4 | Sube a 5.5 m si desde arriba ve más zona de escape y baja si no; B4\* usa la posición verdadera del ladrón (solo como techo) |

## 4. Resultados (512 partidas por fila)

**4.1 La política de la V15 no aportaba nada** (`03_SIMULACION_RL/informes/diagnostico_v17_ia_aporta.md`). Misión completa del
nivel 4, 256 partidas: custodia de 60 s: 11.3 % la política (229 M pasos), 10.2 % siempre quedarse, 7.8 % al azar
(margen ±3.9). Barrido de checkpoints plano: 0.96-0.97 de media de 7 M a 230 M (`informes/barrido_v15.md`). Causa
medida: con el ladrón a la vista, 9 de las 10 acciones de la V15 hacían lo mismo, y el entrenamiento aprendía también de
pasos en los que la red no decidía.

**4.2 La V17 (7 acciones con efecto, máscara de acciones, recompensa por la racha de 30 s)**, cancha con paneles de
1.0 m (`informes/v17/v172_50M_*.json`):

| | M1 | Rendición | Alcanzado |
|---|---:|---:|---:|
| V17.2 a 50 M pasos (red, determinista) | 54.3 % | 22.5 % | 0.2 % |
| B0 siempre quedarse | 48.4 % | 14.5 % | 0.2 % |
| B3 siempre subir | 56.2 % | 22.3 % | 0.2 % |

La red supera a "solo reglas" por 5.9 puntos y **empata con "siempre subir"** (diferencia de 1.9 puntos, dentro del ruido
de ±4.3).

**4.3 Con los paneles reales** (1.5 × 2.2-2.3 m, `informes/v17/v173_base_b*.json`, `b4_real_*.json`): el escenario es
mucho más difícil. M1: B0 11.7 %, B1 13.5 %, B2 17.2 %, **B3 24.6 %**, B4 19.5 %, B4\* 22.5 %. La V17.2 y el afinado en
esta cancha se medirán esta noche: **[pendiente: completar con `informes/v17/v172_real_*.json`]**.

**4.4 Compuerta de la altura (D-067/D-068):** ni la regla B4\*, con la posición verdadera del ladrón, supera a "siempre
subir". Con la búsqueda determinista volviendo a 3.30 m cada vez que lo pierde, subir siempre ya es casi lo mejor que
se obtiene de la altura.

## 5. Qué se puede afirmar (y qué no)

- La política aprendida **supera a no hacer nada** (por 5.9 puntos en M1, cancha vieja) y **aprendió sola una estrategia
  equivalente a la mejor regla simple** (subir). Es un resultado modesto y honesto.
- **No se puede afirmar** que supere a esa regla simple, ni que funcione en el dron: todo es simulación, con parámetros
  estimados (paneles por medir, alcance del TF-Luna según el color, retardos de los servos).
- La V15 mostraba "92 % de misión completa" y "~89 % de custodia a 60 s"; esas cifras son de otra versión y otro criterio (antes de
  entrenar, `evaluacion_v15-comparacion-v14.md`, D-046) y **no deben mezclarse** con las de la V17.
- Lo que sí aporta a la defensa: el diagnóstico medido de por qué la V15 no aprendía, el cambio de diseño que lo corrige y las
  líneas base que evitan el engaño de "la IA lo hace bien" cuando lo hacían las reglas.

## 6. Pendientes antes de dar esto por cerrado

1. Completar 4.3 con la V17.2/V17.4 en la cancha real.
2. Medir los paneles con cinta (alto, ancho, color) y repetir la línea base si cambian.
3. Probar D-059 C (decidir los primeros segundos tras perderlo), que toca la regla dura 3: solo con permiso explícito de Brahian.
4. Llevar la política a la Jetson exigiría calcular las mismas 195 entradas y 7 acciones allá; hoy ese código no existe.
