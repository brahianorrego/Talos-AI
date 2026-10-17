# Resumen para Brahian (noche del 16 al 17 de octubre)

Lo escribe el **Supervisor nocturno**. No aprueba nada: las sesiones solo siguen con lo que tú aprobaste
(D-049 a D-056). Lo más nuevo va arriba. Nada se ha subido a GitHub (sin `git push`).

---

## 10:00 a. m. · Hardware entregó

- **Guía para ti:** `05_HARDWARE_Y_VARIANTES/GUIA_PARA_BRAHIAN.md`, con un dibujo de dónde va cada cosa en C y en D
  (`dibujo_C_y_D.svg`), la lista de compra y una comparación con diseños gratuitos de internet (commit `096f304`).
- **Pan-tilt listo para imprimir:** los 7 archivos de diseño compilan y los `.stl` están en
  `05_HARDWARE_Y_VARIANTES/piezas_3d/stl/`. En el modelo, los topes paran la cuna en −44° y +14°, dentro de la regla
  dura de −45°..+15°. **Nada está impreso ni probado.** Las medidas del servo MG90D, de la cámara IMX219 y del TF03 hay
  que verificarlas con calibrador antes de imprimir. Los precios son aproximados, sin comprobar. OpenSCAD quedó
  instalado fuera del repositorio.
- El TF03 a −3° (D-064) ya está en las configuraciones.
- **Turno del Visor:** video corto en Blender y luego las personas animadas en el visor.

---

## 9:40 a. m. · Decisiones que tomé yo (me lo pediste). Revísalas en la noche

Desde hoy no te pregunto: decido, anoto el motivo y tú me dices si algo no te gusta (D-060). Todo queda en `docs/DECISIONES.md`.

| # | Qué decidí | Por qué |
|---|---|---|
| D-061 | Nombres: la corrida de ahora es la **V17.0**; con el arreglo de D-059 será la **V17.1**; luego V17.2… | "todo" solo quería decir "con todas las piezas de la recompensa": era confuso |
| D-062 | Si la V17.1 le gana a "solo reglas" y a "siempre SUBIR", se lanza la de **50 M (~4 h)** sin esperarte. Si no aprende, se prueba el siguiente arreglo | Para que al llegar en la noche haya resultados |
| D-063 | Medir dos arreglos para que el dron no quede **de verdad** bajo 3.30 m cerca de personas, y quedarse con el mejor | Hoy pasa el 14 % del tiempo debajo por el error del barómetro, aunque solo lo pide el 2 % |
| D-064 | Hardware: variante C primero (quitar el TF03 del gimbal y poner un TF-Luna liviano); el pan-tilt de servos (D) lo imprimes tú desde ya como plan B; el TF03 va al chasis inclinado −3° | Con −3° el LiDAR ve el doble de los paneles (25 → 52 %) |

**Lo que no decido yo:** cambiar una regla dura, subir a GitHub y lo físico del dron. Para eso sí te pregunto.

**Hoy trabajan:** Simulación V17 (la V17.1 y el entrenamiento) y Hardware (una guía en español de qué cámara va dónde y
el pan-tilt listo para imprimir). Después rota el Visor (personas animadas e interfaz de la estación de tierra).

---

## 9:15 a. m. · Brahian ya despertó

- **Entrenamiento V17 corriendo desde las 9:05.** Es la corrida "todo" de 10 M pasos a ~3 300 pasos/s y termina hacia
  las 10:00. Está en la pestaña "V17 todo 10M" del panel Terminal, en `modelos_v17_todo` y `salida_v17_todo`, y su log
  es `03_SIMULACION_RL/modelos_v17_todo.log`. Usa la recompensa de **antes** de D-059: arrancó un minuto antes de tu
  aprobación (commit `6c21f79`). Sirve para ver si la red sigue quedándose quieta. La opción A todavía hay que programarla.
- **Botones fijos** (commits `7aadfac` y `84fc328`): solo "siempre SUBIR" se separa de "siempre QUEDARSE". Con SUBIR la
  racha ≥ 30 s es 61.9 % contra 51.8 %, se recuperan en ≤ 10 s el 83 % de las pérdidas contra 76 %, y la rendición es
  24 % contra 16 % (`docs/PROGRESO_V17.md`).
- **`descarga.zip`** en la raíz del proyecto: es el paquete gratuito (CC0) de animaciones de Quaternius. Le pedí al
  Visor que lo saque del repositorio, sin borrarlo.

---

## Revisión de las 8:51 a. m.

- Simulación V17 hizo commit de la medición de los 7 botones fijos y de `LANZAR_V17.bat` (commit `7aadfac`). El
  Arquitecto dejó D-059 abierta (commit `862cbce`).
- **A las 8:51 la corrida de 10 M todavía no corre.** No hay ningún proceso de Python ni carpeta `modelos_v17_todo`.
  Simulación V17 está lanzándola justo ahora en una pestaña del panel Terminal de la app. Puede que te pida aprobar ese
  comando en su chat.
- Límite de uso: 20 % del de 5 horas y 50 % del semanal.

---

## Revisión de las 7:52 a. m. · LO MÁS IMPORTANTE

- **Simulación V17 terminó la base de la V17** (commit `41a2ef6`, a las 4:17). Hizo esto:
  - trajo la V16;
  - programó la cancha con las dos V, los 7 botones, la evasión por regla, MaskablePPO y la partida desde la activación;
  - agregó 15 pruebas nuevas;
  - arregló 2 pruebas que fallaban en el PC. Una era de una regla dura (humano en el lazo) y **se arregló el código, no la
    prueba**.

  Detalle en `docs/PROGRESO_V17.md`. Entrena a ~3 600 pasos/s, casi 3 veces lo que hacía la V15: 10 M pasos son ~50 min y
  50 M son ~4 h.
- **El entrenamiento NO se lanzó de noche, y fue a propósito.** La sesión encontró dos problemas:
  1. Con la medida que aprobaste en D-052 (60 s seguidos a la vista), "solo reglas" da **1.2 %**, el azar **0.6 %** y la
     regla de posicionamiento **1.0 %**: las tres empatan (`informes/v17_linea_base.json`, 512 partidas). Con un número
     así no se puede saber si la IA aporta.
  2. En la prueba de humo, **la red aprendió a quedarse siempre quieta** a los 2.6 M pasos
     (`informes/v17/humo_2M.json`). Moverse no le gana nada y solo le cuesta multas.

  Lanzar las corridas así habría medido "quedarse quieto" siete veces. Después de las 4:37 el límite de uso la cortó,
  y se reinició a las 7:20.
- **Lo que pedí a las 7:52:** que lance **ya** la corrida "todo" de 10 M (~50 min), para que cuando te levantes haya
  aprendizaje en marcha y se vea si el problema sigue. Las de 50 M esperan a tu decisión.
- **Espera a Brahian · D-059 (la decisión clave de hoy): con qué número se mide "la IA aporta" y qué hacer para que
  moverse le sirva a la red.** Opciones de Simulación V17:
  (a) medir con "racha ≥ 30 s" en vez de 60 s: las tres líneas base dan ~52 %, así que deja margen para mejorar;
  (b) que la búsqueda no reinicie el contador al segundo de perder al ladrón;
  (c) un ladrón que se deje ver más tiempo.
  **Recomendación de Simulación V17: (a)**, probablemente junto con (b).
  **El Arquitecto ya la escribió como D-059** (`docs/DECISIONES.md`). Encontró un dato nuevo: con 30 s seguidos, "siempre
  SUBIR" da **62 %** frente al **52 %** de las reglas, y la rendición sube de 16 a 24 %. O sea, sí hay algo que aprender,
  pero hoy la recompensa no lo paga. Sus opciones:
  **A (recomendada):** medir 30 s seguidos, ajustar la recompensa a esa medida, poner "siempre SUBIR" como la línea base
  a superar y hacer una prueba de 10 M (~50 min).
  **B:** cambiar solo la medida; es barato, pero probablemente no sirve.
  **C:** que la red decida también los primeros 2-3 s después de perder al ladrón; esto toca la regla dura 3.
- **Espera a Brahian · seguridad (decisión abierta de la V16, el altímetro):** el dron pasa el **13-14 %** del tiempo
  realmente por debajo de 3.30 m con alguien a menos de 8 m, aunque solo lo pide el ~2 %. La diferencia es el error del
  barómetro (`informes/v17_linea_base.json`).
- **Otra propuesta, para la parte física:** inclinar el TF03 −3° duplicaría cuánto de los paneles de 2 m se mapea
  (25 → 52 %, `PROGRESO_V17.md`, paso 7). Cambiar ese montaje lo decides tú, y solo después de los pasos 4-7 del mínimo.

---

## Revisión de las 3:51 a. m.

- **Simulación V17** está corriendo la prueba de humo del entrenamiento: `entrenar_master.py` con 512 entornos, que
  arrancó a las 3:44 en una carpeta temporal. **El entrenamiento real todavía no está lanzado** y
  `docs/PROGRESO_V17.md` aún no existe. Le pedí que lo lance apenas el humo salga bien.
- **Límite de uso: 90 %** del de 5 horas, que se reinicia a las 7:20 a. m. Probablemente corte a las sesiones antes de esa
  hora. En la revisión de las 7:23 las reanudo y compruebo que el entrenamiento esté corriendo.

---

## Actualización de las 3:10 a. m.

- **Visor, con tu autorización en su chat:** instaló **Blender 5.2.2 LTS** portable, con el hash verificado. Blender usa
  la RTX para renderizar (commit `c7a5467`). También bajó los 4 paquetes CC0 de Quaternius que pediste: personajes,
  86 animaciones y naturaleza. Están fuera del repositorio y ya hay una prueba de render (commit `c00f813`). Después se
  detuvo. Con eso salen de la cola Blender y las personas realistas.

---

## Actualización de las 3:00 a. m.

- **Visor:** la cancha V17 ya está en el visor (commit `b3faf45`). Tiene la zona de 30 × 30 m con su geocerca, las dos V de
  90° con paneles de 1.0 × 2.0 m y vértices a 10 m, y árboles alrededor. Corre a 144 cuadros/s con la RTX. Las capturas
  están en `04_VISOR_Y_MOTOR_GRAFICO/mediciones/capturas/v17_cancha_*.jpg`. Las medidas de la cancha (90 × 60 m) están
  por confirmar. También trajo `generar_texturas.py`.
- **Espera a Brahian · personas realistas (sigue de D-057).** Opciones:
  (a) paquetes de Quaternius, CC0: se pueden subir al repositorio público, pero se ven de juego estilizado;
  (b) Mixamo, de Adobe: más realista, pero pide cuenta y sus archivos no se pueden subir al repositorio;
  (c) seguir con las personas hechas con código, que se ven de maniquí.
  **Recomendación del Visor: (a)**, y (b) solo para el video en Blender, que no se sube.
- **Espera a Brahian · Blender no se instaló.** El Visor necesita que tú le digas "sí" **en su propio chat**. Una
  autorización que le llega desde otra sesión no le basta, y está bien que sea así. Ya te dejó la pregunta lista allá:
  Blender LTS portable de blender.org, con el hash verificado, en `C:\Users\Brahi\Programas\Blender` y sin permisos de
  administrador.

---

## Actualización de las 2:55 a. m. · lo que pediste antes de dormir

- **Entrenamiento V17: lo autorizaste tú.** Le pasé a Simulación V17 tus palabras ("que empiece su aprendizaje por
  refuerzo, que cuando yo me levante a las 8-9 ya haya iniciado"). Lo lanza apenas estén listos E1-E6 con las pruebas
  pasando, la línea base B0 y la prueba de humo de 15 minutos. El orden es el del plan V17, §6: primero las corridas de
  10 M; si todavía no están programadas, la corrida principal con la regla de parada de D-052 a los 50 M. Corre aparte
  de la sesión, así que sigue aunque se acabe el límite de uso. El comando y la carpeta quedarán en `docs/PROGRESO_V17.md`.
- **Programas del motor gráfico: lo autorizaste tú.** El único programa que hace falta es **Blender**; three.js no se
  instala y Unreal quedó descartado (D-057). El Visor lo baja de blender.org en versión portable (sin permisos de
  administrador), verifica el hash y anota la ruta en `04_VISOR_Y_MOTOR_GRAFICO/_LEEME.md`. Después se detiene.
- **Riesgo:** a las 2:52 ya íbamos en 58 % del límite de 5 horas, que se reinicia a las 7:20. Por eso dejé trabajando
  casi solo a Simulación V17. Si el límite la corta antes de lanzar, el lanzamiento queda para después de las 7:20.

---

## Actualización de las 2:50 a. m.

- **Tú aprobaste D-057 y D-058** directamente: en el chat del Arquitecto escribiste "Apruebo D-057 y D-058", y en el
  del Visor pediste el commit del visor V16. Quedaron anotadas en `docs/DECISIONES.md` (commit `daf5903`). Por eso salen
  de la cola y **ya no es un problema** el commit `3c38f66`: lo pediste tú.
- El **Arquitecto** se detuvo: no le queda trabajo aprobado hasta que Simulación V17 entregue algo.
- **Reactivé al Visor** para que haga la escena V17 (la cancha de D-051) en three.js (D-057) y traiga
  `generar_texturas.py`. Siguen trabajando 2 sesiones: Simulación V17 y Visor.
- **En la cola solo quedan** los puntos 3 y 4 de abajo (variante D y pedidos a la parte física).

---

## Revisión de las 2:42 a. m.

### Qué hizo cada sesión

- **Arquitecto:** entregó el plan V17 (commit `95f033d`). Midió que la IA de la V15 no aporta: custodia ≥ 60 s de
  11.3 % con la IA, 10.2 % con "siempre MANTENER" y 7.8 % al azar, en 256 partidas
  (`03_SIMULACION_RL/informes/diagnostico_v17_ia_aporta.md`). Anotó tus aprobaciones D-049 a D-056 (commits `db4063d` y
  `b5affbb`) y dejó abiertas D-057 y D-058 para ti (commit `8ba0aca`).
- **Simulación V17:** está en el paso E1, traer el código de la V16 a `03_SIMULACION_RL/`. Ya cambió `entorno.py`,
  `control.py`, `entrenar_master.py` y las pruebas, y guardó copias `_v15` en `_archivo_versiones/codigo/`. Todavía no
  ha hecho commit ni ha informado si pasan las 118 pruebas.
- **Visor y motor gráfico:** entregó su plan (commit `e2b69a3`). El visor V16 da 144 cuadros/s con la tarjeta RTX y
  24 con la Intel (`04_VISOR_Y_MOTOR_GRAFICO/mediciones/MEDICION_FPS_V16.md`). Recomienda seguir con three.js y usar
  Blender para el video. Revisó las licencias de `v16/`: no hay fotos de personas, los cielos son CC0 (Poly Haven),
  three.js es MIT y las texturas son propias (commit `5e8cde3`). **Lo pausé** porque había 3 sesiones trabajando a la vez
  y lo que le falta depende de tus decisiones.
- **Hardware y variantes:** entregó la matriz de variantes A-F (commits `ebc3b9f` y `a9d4c39`). El chequeo
  `validar_variantes.py` pasa en las 6. Está quieta: lo que le falta depende de ti o de la parte física.

### Espera a Brahian

1. **D-057 · Motor gráfico.** Opciones: (a) seguir con three.js (el visor V16) para la estación de tierra y usar
   Blender para el video realista; (b) Unreal 5; (c) Godot o Unity. **Recomendación del Visor: (a).** Unreal no va
   cómodo con 16 GB de RAM y 6 GB de video, y obligaría a empezar de cero (`04_VISOR_Y_MOTOR_GRAFICO/PLAN_MOTOR_GRAFICO.md`).
2. **D-058 · ¿El visor V16 (9.9 MB) entra a `main`?** El Visor **ya hizo el commit** (`3c38f66`) antes de que tú
   decidieras, pero no lo subió a GitHub. Opciones: (a) dejarlo; (b) deshacerlo con un commit que lo revierta.
   **Recomendación del Arquitecto: (a), sí entra,** después de revisar licencias y fotos. Esa revisión ya está hecha y
   salió limpia (`04_VISOR_Y_MOTOR_GRAFICO/_LEEME.md`). Si dices que sí, falta además traer `generar_texturas.py`.
3. **Hardware · ¿comprar o imprimir la variante D (pan-tilt) desde ya, como plan B?** Cuesta poco. La sesión no dejó
   recomendación (`05_HARDWARE_Y_VARIANTES/VARIANTES.md`, §8).
4. **Pedidos a la parte física, para cuando termine el mínimo:** pesar la BaseCam, el TF03 y la cámara USB; medir si
   el pod baja a −45° sin el TF03; anotar el color real de los paneles (afecta el alcance del TF-Luna). Están en
   `docs/PEDIDOS_A_LA_PARTE_FISICA.md`.

### Problemas

- **Cortes por el límite de uso:** las sesiones ya están activas otra vez, después del reinicio de las 2:20.
  A las 2:42 iba en 41 % del límite de 5 horas (se reinicia a las 7:20) y en 37 % del semanal.
- **3 sesiones trabajando a la vez** (el máximo es 2): pausé al Visor. Siguen Simulación V17 y el Arquitecto.
- **Commit del visor V16 antes de la decisión D-058:** queda como está hasta que decidas (punto 2 de arriba).
- Las piezas 3D (`.scad`) no se han compilado porque en el PC no está instalado OpenSCAD.
