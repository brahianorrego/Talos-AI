# Estado del proyecto

Actualizado: 2026-10-16 (noche), migración a la carpeta `Dron-IA-Proyecto` (sesión Organizador, cuenta de Brahian).

## Migración 2026-10-16 (Fases A y B)

- **Carpeta nueva verificada:** los 4 119 archivos de `Tesis-IA-Drone` y los 4 de `Documentacion-Tesis` están en la
  copia (mismo nombre y tamaño); solo faltaban `README.md`, `CLAUDE.md` y `.gitignore` de la raíz (los dos primeros ya
  se escribieron; `.gitignore` queda para la Fase E). Sin IPs, usuarios ni claves en los archivos de texto. El original
  no se tocó.
- **`.venv` nuevo** en `03_SIMULACION_RL` con las mismas versiones del original (torch 2.14.1+cpu, SB3 2.9.0,
  scikit-learn 1.9.1, numpy 2.5.3). `import entorno` OK y **88 pruebas pasan** en la copia (149 s) sin cambiar archivos.
  El protocolo del comité re-corrido da un CSV idéntico byte por byte al original.
- **Snapshot congelado** del mínimo en `01_MINIMO_INDISPENSABLE/` con `HUELLAS_SHA256.txt` (33 archivos).
- Memoria copiada a `C--Users-Brahi-Desktop-Dron-IA-Proyecto` (con `jetson-conexion.md` sin secretos);
  `.claude/settings.local.json` y `launch.json` reescritos sin IP ni usuario.
- Fase B: `GUIA_DE_ARCHIVOS.md`, `COMO_FUNCIONA_EL_CODIGO.md`, `DEMOSTRACION_PARA_EL_INGENIERO.md`,
  `06_REDES_NEURONALES_Y_MODELOS/ver_redes.py` (15 s) y `_LEEME` en 01, 04 y 06.

### Plan V17 (Arquitecto, 2026-10-17)

- **Medido: la política PPO de la V15 no aporta.** Misión completa del nivel 4, 256 partidas: custodia ≥ 60 s 11.3 % (V15),
  10.2 % (siempre MANTENER), 7.8 % (azar); cumplida 33.2 / 34.0 / 32.8 %. Escenarios fijos iguales; barrido de
  checkpoints V15 plano (0.96-0.97 de 7 a 230 M, `informes/barrido_v15.md`, reemplaza la tabla de la V10 de
  `resumen_v15-231M.md`). Causa: 9 de 10 botones hacen lo mismo con el ladrón a la vista y PPO aprende de pasos sin
  decisión (`informes/diagnostico_v17_ia_aporta.md`).
- Plan `docs/PLAN_V17_REFUERZO.md`: 7 botones con efecto, máscara de acciones, criterio "la IA aporta", cancha con dos V de
  90° a 10 m (paneles ~2.0 m, `docs/v17_zona_ia.png`), reglas una por una, 50 M pasos con regla de parada. Decisiones
  D-049 a D-054 **abiertas**. Encargo para la sesión de simulación: `docs/ENCARGO_SIMULACION_V17.md`.

### Hallazgos de la revisión (para decidir)

1. **Este ESTADO estaba desactualizado:** decía "V15 entrenando". La V15 se detuvo el 12-oct en 229.4 M pasos, en el
   nivel 4 desde los 24.4 M (`modelos_v15/estado_entrenamiento.json`). (Una sesión anterior dijo "180 M"; el archivo
   dice 229.4 M.)
2. **La política PPO decide casi al azar:** acción preferida 0.17 de probabilidad en promedio, entropía 2.14 de 2.30
   (`ver_redes.py`); el resumen del entrenamiento da misión cumplida 45 % y entropía subiendo de 1.97 a 2.12
   (`informes/resumen_v15-231M.md`). El "92 %" citado en la migración es otra medida: misión completa con el criterio
   de la V14 y el modelo de la V14 **antes** de entrenar la V15 (`evaluacion_v15-comparacion-v14.md`); la custodia
   ~89 % a 60 s también es sin reentrenar (D-046). No mezclarlas al presentarlas.
3. `informes/resumen_v15-231M.md` trae una tabla de "escenarios fijos" tomada de `barrido_v10-master.csv`: son
   checkpoints de la **V10**, no de la V15. Hay que rehacer ese barrido con `modelos_v15`.
4. **Jetson:** `requirements_jetson.txt` fija scikit-learn 1.3.2 y Python 3.8 (la Jetson tiene 3.12) y el decisor se
   entrenó con 1.9.1: en la Jetson usar `decision.json`. Además ya hay un `decision.pkl` **distinto** (IA #2 vieja de
   `vuelo_evasion.py`): copiar el del mínimo a `~/Escritorio/dron_ia/minimo/`. Falta escribir `sistema_minimo.py`
   (paso 5).
5. **WiFi de la Jetson:** el 13-oct no se conectó al hotspot del celular (sesión "Parte Física"). Bloquea el sábado.
6. El 94 % y los 3 840 vuelos del decisor están marcados "sin verificar" en `ENCARGO_TESIS_NUBE.md`;
   `ver_redes.py` da 96.8 % de acierto **por cuadro** en el conjunto de prueba, que es otra medida.

---

## Estado anterior (2026-10-10, sin cambios)

## Resumen

Dron autónomo que busca, fija y mantiene a la vista a un sospechoso (PPO + reglas + operador humano).
El hardware está configurado y probado en banco; la IA se entrena en simulación y aún no vuela.

## Simulación y entrenamiento

- **Mínimo indispensable del proyecto de grado** (`simulacion/minimo_tesis/`, carpeta congelada e independiente del
  entrenamiento). El piloto avanza de frente; el sistema solo frena y sube a 3.30 m ante un riesgo definido (obstáculo
  por LiDAR, persona por YOLO según el árbitro); el operador siempre manda; modo estático. Protocolo del comité
  (`informes/minimo_tesis_protocolo.md`, CSV y repetición en el visor): 1300 vuelos, éxito 100 % [99.7, 100], 0
  activaciones falsas en 300; con el operador solo, 23 % de vuelos seguros. Condiciones degradadas y velocidad máxima
  segura (detenerse con margen): panel 11 m/s (alcance del LiDAR), persona quieta 4 m/s (regla de los 8 m), persona que
  corre de frente 10 m/s (7 con 300 ms de latencia); se rompe con solo cabeza y hombros a la vista. 13 pruebas.
  - Fase G · decisor IA (`informes/minimo_tesis_decisor_ia.md`): MLP con las entradas de la Jetson dentro de la envolvente
    de reglas duras. Protocolo 100 % como las reglas; discriminación 91.2 → 94.0 %, activaciones innecesarias 44 → 30;
    mundos de prueba: choques 39 → 28, personas a < 2 m bajo 3.30 m 420 → 218. Abierta D-048 (veto del árbitro al ascenso).
- **V15 · nivel 4** (C1-C3, `informes/evaluacion_v15-nivel4-C1-C3.md`): pausa de 4 s, tope terminal, custodia como número
  principal (~89 % a 60 s). El entrenamiento se retomó con esos cambios.

- **V15** (plan `docs/PLAN_V15_CURRICULO.md`, fases A-E implementadas y medidas; informes `simulacion/informes/
  evaluacion_v15-fase-{A..E}.md`). **Entrenando**: la lanzó el arquitecto a las 16:45 y la retomó a las 19:17 con D-041
  (`informes/evaluacion_v15-ajustes-D041.md`). Sale del último
  checkpoint de la V14 (`modelos_v14/`, 7.0 M) y empieza en el nivel 0. Copias previas: `*_v14.py`, `index_v17.html`.
  - A: LiDAR 30 m y 10 rayos/paso, 360° de entrada bajo (2.5 m, −3°) y de búsqueda alto (3.3 m, −12°), cuerpo colombiano
    (altura segura 3.30 m), cansancio y pulso, muros de 0.2 m, detección por alto y ancho.
  - B: Kalman (con compuerta y distancia geométrica), 200 partículas con información negativa, búsqueda guiada por la nube,
    anti-cenit predictivo, distancia adaptativa. Escenario "debajo": 2 → 68 % (82 % al final de la fase E).
  - C: cambio de ID en cruces, estado RECONFIRMAR con el operador: 0 cambios sin detectar en 1 556 partidas.
  - D: secuencia tras el muro (lado proyectado → otro extremo → muro de canto → 360°); tras muro 10.2 → 9.6 s.
  - E: rendición (contador continuo, 20 s + 100 s × reserva, tope 5 min), 5 niveles, ataques desde el nivel 2, guardas de
    geocerca y de personas, visor con una pestaña por nivel. **Decisiones abiertas** en el informe de la fase E (cansancio,
    civil distractor, choques en partidas largas).
  - Ajustes del arquitecto (`informes/evaluacion_v15-ajustes-arquitecto.md`): altura nominal 3.30 m salvo el 360° de
    entrada (D-043); muro de canto a 6 m con desplazamiento lateral de 1 m a cada lado (D-044). Geocerca en cenit y
    "debajo": 0 %; choques con peatones 0-0.6 %. Rendición por nivel: 89 / 51 / 66 / 9 / 12 %. 62 pruebas pasan.
  - Comparación con la V14 (`informes/evaluacion_v15-comparacion-v14.md`): con el mismo criterio de éxito la V15 gana en
    todos los niveles (misión completa 62 % → 92 %); la rendición baja por el contador de ~2 min y los civiles parecidos
    (D-041). Abierta D-045 (pitch del 360°: −8° o −12°).

- **V14 · Currículo progresivo** (2026-10-10, listo y probado, sin lanzar). Incluye todo lo de la V13. Parte del
  checkpoint más nuevo de la V12 (10.1 M pasos; la V12 está detenida). Copias previas: `*_v13.py`, `index_v16.html`.
  - Niveles (en `reset()`): 0 Duelo abierto (sin muros ni civiles; ladrón en huida zigzag, 30 % cenit), 1 Muro único,
    2 Ruido visual (muro + civil que cruza la línea de vista), 3 Misión completa. 25 % de partidas repasan niveles
    anteriores. Oclusión entre personas (nueva) y civil distractor que no se acerca a menos de 3 m del dron.
  - `CurriculumCallback`: sube con éxito ≥ 85 % en las últimas 1000 partidas del nivel (sin repaso ni cenit), con
    mínimo 2 M pasos por nivel y paciencia de 50 M. Log `>>> NIVEL SUPERADO … <<<`. Guarda el nivel para continuar.
  - Competencia dron vs ladrón en `salida/estado.json`; visor con barra "Dominio táctico" y nivel actual.
  - Medido con el modelo de la V12 (192 entornos × 150 s): N0 huida 97 %, **N0 cenit 0 %**, N1 90 %, N2 89 %,
    N3 55 %. El modelo ya domina 0-2: subirá rápido; el trabajo real está en el nivel 3 y en el cenit. 38 pruebas pasan.

- **V13 · Currículo y geometría de la búsqueda** (2026-10-10, código listo y probado; NO se lanzó: la V12 sigue
  entrenando hasta que Brahian decida). Copias previas: `*_v12.py` e `index_v15.html`.
  - Currículo: 30 % de las partidas con "Un Solo Muro" (baja a 10 % al subir el nivel); métricas `cumplida_un_muro`.
  - GIRO_360 con altura y gimbal fijos y 90°/s, con tope `RATE_Y_MAX = 120°/s` en `control.py`. Valores por defecto
    **3.0 m y -15°** (el pedido era 2.5 m y 0°: dentro del salto del ladrón, alcanzado 48 %; ver D-027).
  - Interrupción táctica: si YOLO ve al ID designado en cualquier estado de búsqueda, PERSECUCIÓN en el mismo cuadro.
  - Stand-off por FOV: 2.4 m por fuera de la esquina y 0.8 m detrás del muro (2.53 m en diagonal).
  - Detección parcial: basta el 15 % del bounding box (12 muestras del cuerpo; dentro de la imagen y sin tapar).
  - Despeje ampliado a 1.2 m, también contra la nube de puntos (evita bajar sobre un muro tras una interrupción).
  - Con el modelo actual de la V12 (sin reentrenar), entorno general 192 × 150 s: cumplida 33.5 % → **67 %**,
    alcanzado 22.8 % → 18 %, panel 7.1 % → 3 %, perdido 22.8 % → 7 %. Escenarios fijos: cambio brusco 58 % → **100 %**,
    debajo 0 % → 8 %, abierto y tras muro 100 % (`informes/evaluacion_v13-con-modelo-v12.md`). 30 pruebas pasan.
  - Al lanzarla: retoma sola `modelos_v13/ultimo.zip` o, la primera vez, arranca del checkpoint más nuevo de
    `modelos_v12/` y guarda la salida de la V12 en `salida_v12/`.

- **V12 · Control jerárquico híbrido** (2026-10-10, código listo y probado; el entrenamiento lo lanza Brahian):
  - **Fine-tuning estricto** desde el último checkpoint de la V10 (`dron_master_769612800_steps.zip`, 769.6 M pasos).
    Capa inferior del actor congelada entera (24 704 parámetros, verificado: cambio 0); solo se afinan la capa táctica
    y la salida (17 802) y el crítico. Modelos nuevos en `simulacion/modelos_v12/` (fuera de Git), tasa 1e-4.
  - **Recompensa:** la multa de suavidad solo cobra lo que comanda la red (en "abierto": -18.9 → -0.5 por partida, mismo
    jitter físico). Bono de re-adquisición +8 y multa -8 por el MISMO evento (oculto más de 1 s). `info` registra
    `t_ep`, `r_comp` (8 componentes), `du` (jitter físico por eje) y `gmb_min`.
  - **Gimbal:** barrera dura de -45° también después del PID (prueba con comandos de -120° y cabeceo de ±25°).
    **Reflejo de punto ciego:** retrocede a d = h / tan(45° + VFOV/2) + 1 m si el objetivo va a quedar debajo.
  - **Búsqueda determinista con memoria espacial** (`PERDIDA_IA = False`): PERSECUCIÓN → PÉRDIDA → FLANQUEO_PROFUNDO →
    GIRO_360 → SIGUIENTE_OBSTÁCULO → … → ALTURA_TÁCTICA → MISIÓN_PERDIDA a los 90 s; histéresis de 1 s por estado;
    raycasting contra la nube del LiDAR para elegir el muro y para que la ruta no roce las esquinas.
  - **Visor:** paneles "Búsqueda · estados" y "Mapa SLAM · LiDAR 1D" (minimapa con nube de puntos, barrido del rayo,
    muros, zona ciega) y datos brutos del LiDAR. Arreglado: la nube nunca llegaba al visor (clave `lm` repetida).
  - **Mismo modelo de la V10, sin reentrenar** (entorno general, 256 partidas): cumplida 13 % → **43.5 %**, perdido
    62.5 % → 21.8 %. Escenarios fijos (`informes/evaluacion_v12-sin-reentrenar-769M.md`): abierto 100 %, tras muro
    100 % (antes 94 %), cambio brusco 56 %, **debajo sigue en 0 %** (el ladrón del escenario persigue al dron y se mete
    debajo desde 3.5 m a 3.5 m/s; el dron, con el jerk limitado, no alcanza a apartarse). 24 pruebas pasan.
- Rama `v11-hibrido`: gimbal estricto en **-45°..+15°** (D-014) y búsqueda tras perder el objetivo
  **determinista**, `PERDIDA_IA = False` (D-015). Probado: el gimbal toca -45,00° y nunca baja; con la
  bandera en False se recorren PREDECIR, INVESTIGAR, ASOMO y VENTAJA_ALTURA. 17 pruebas pasan.
- Código base: V10 (entorno `v8`/`v9` en el docstring): mapa LiDAR, 10 acciones, `OBS_DRON = 192`,
  controladores PSC/ATC y gimbal modelados en `control.py`. Copias previas a los cambios: `*_v10.py`.
- Entrenamiento V10 master **detenido** en 769.8 M pasos (2026-10-10). Su salida quedó en `simulacion/salida_v10/`.
- Referencia: V9 con pesos v8 sin reentrenar → cumplida 44 %, perdido 26 %, alcanzado 15 %.
- Evaluación en escenarios fijos y resúmenes: `simulacion/herramientas/` → `simulacion/informes/`.
  Pruebas: `simulacion/tests/`. Agentes: `.claude/agents/` (`supervisor-rl`, `implementador`).

## Modelos

- `simulacion/modelos_master/` (fuera de Git): V10, 761+ `.zip`, ~1,1 GB. Brahian los copia a mano a Google Drive.
- `simulacion/modelos_v12/` (fuera de Git): V12 (`base_v12.zip`, `ultimo.zip`, un checkpoint por millón de pasos).
- **Release `v10-master-759M`** en GitHub: 10 archivos, 12 MB (`ultimo.zip`, `base_v9.zip`,
  `ladron_congelado.pt` y un checkpoint cada 100 M pasos hasta 700 M).
- `simulacion/modelos/dron_politica.json`: pesos exportados para la Jetson (sí está en Git).

## Hardware

- Pixhawk (ArduPilot 4.7) ↔ Jetson por TELEM2 a 115200; pitch del gimbal por AUX1 (`pwm = 1500 + θ·500/45`).
- Batería LiPo 4S original sobredescargada: **retirada**; no volar con ella.
- Detalle en `hardware.md`, `pixhawk.md` y `jetson.md`.

## Git

- Rama actual: `v15-curriculo` (V12 a V15, mínimo indispensable, código de la Jetson y plan V16; `v11-hibrido` apunta a lo mismo). Etiqueta `v10-master-759M` (código de la V10, 759 M pasos).
- V16 en la nube: ramas `v16-simulacion` y `v16-visor` (`docs/PLAN_V16_REALISMO.md`); avance en `docs/PROGRESO_V16.md`.
- PR #2 (`docs/proyecto-completo-v6`) abierto, sin fusionar: lo hace Brahian en GitHub.

## Pendientes (por prioridad)

1. Brahian: revisar las decisiones abiertas de la fase E y confirmar el lanzamiento de la V15 (comando en `CLAUDE.md`).
2. Escenario "debajo" (0 %): decidir si se acepta como límite físico o si se agrega una regla anti-acecho en la búsqueda.
3. Brahian: copiar `modelos_master/` (1,1 GB) a Google Drive.
4. Ciclo de mejora: pasar `informes/resumen_*` y `barrido_*` a `supervisor-rl` y decidir sus cambios.
5. Fusionar el PR #2 a `main`.
6. Copiar el código de la Jetson (`~/Escritorio/dron_ia`) a `jetson/` cuando esté encendida.
7. Llevar la política a la Jetson: sus entradas deben calcularse igual que en `entorno.py`.
8. Validación sim-to-real con datos de campo; evaluar la cuadrícula de la cámara al sol.
