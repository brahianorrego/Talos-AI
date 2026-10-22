# CLAUDE.md

Guía para Claude Code en la carpeta de trabajo definitiva del proyecto de grado. Estado actual: @docs/ESTADO.md
Mapa de archivos: @GUIA_DE_ARCHIVOS.md · Nombres viejos → nuevos: `INDICE_NOMBRES.md`.

Esta carpeta se armó el 2026-10-16 **copiando** (no moviendo) `Desktop\Claude\Tesis-IA-Drone`, que queda intacta
como respaldo y archivo histórico (repositorio viejo `Tesis-IA-Drone`). Esta carpeta es el repositorio
**`Dron-IA-Vigilancia`** (por ahora solo local; plan en `docs/PLAN_GITHUB_NUEVO.md`).

## División del trabajo (desde 2026-10-16)

**Aquí (cuenta de Brahian) solo se trabaja la simulación y el plus.** La parte física del dron, el mínimo
indispensable y el documento se trabajan en la nube de la cuenta de Tania. Por eso aquí no se usa SSH con la Jetson y
no se tocan `01_MINIMO_INDISPENSABLE/`, `02_JETSON_A_BORDO/` ni `07_DOCUMENTO_PROYECTO_DE_GRADO/`. Equipo de sesiones,
roles y reglas: `docs/EQUIPO_Y_SESIONES.md`. Ideas nuevas de Brahian: `docs/IDEAS_BRAHIAN_2026-10-16.md`.

> **Sesión de simulación: lee primero `docs/RELEVO_SESION_FISICA_20OCT.md`** (qué se cambió, resultados D-079 y qué revisar).

> **21-oct (campo): los ángulos de la tabla de abajo (cámara −2.4°, LiDAR −6.7°) estaban medidos respecto al HORIZONTE, no al chasis.** Respecto al chasis salen **cámara ≈ −5.6° y LiDAR ≈ −9.0°** (provisional; el 22-oct se recalibra con la Pixhawk). Ver `docs/DECISIONES.md` D-082. La simulación del mínimo (D-079) sigue con −6.7° / −2.4° y hay que re-simularla con los valores definitivos; el campo de visión (68.3° × 54.0°) no cambia.

## DRON REAL DEL MÍNIMO · MEDICIONES DEL 20-OCT (obligatorias: mandan sobre cualquier valor nominal)

Las midió Brahian en el dron real (ver `docs/DECISIONES.md` D-078 y D-079; detalle y fuentes en `docs/ESTADO_FISICO_20OCT.md` §0).
**Toda simulación del mínimo debe usarlas**; no volver a los valores de la cámara USB (38.9° × 29.7°) ni a "cámara y LiDAR a −5°".

| Qué | Valor medido |
|---|---|
| Hardware del mínimo (variante G) | **Sin gimbal y sin cámara USB.** Cámara CSI IMX219 y TF03 **fijos al chasis** |
| Campo de visión de la CSI | **68.3° horizontal × 54.0° vertical** (el nominal 62.2° × 48.8° era falso) |
| Inclinación de la cámara | **−2.4°** respecto al chasis |
| Inclinación del rayo del TF03 | **−6.7°** (4.3° por debajo del eje de la cámara); desvío lateral −0.6° |
| Posición | LiDAR a 27.5 cm y cámara a 32 cm sobre la superficie de apoyo; la cámara 6 cm detrás del frente del LiDAR |
| Giro de la cámara sobre su eje | +1.5° (provisional, una línea) |
| Pixhawk | Boca abajo bajo la placa inferior (`AHRS_ORIENTATION = 8`); motores `X_REV` (`FRAME_TYPE = 18`) |
| Placas | 15 × 15 cm; separación entre placas 3.85 cm |
| Altura del mínimo | Brahian: **2.0 m como máximo** (antes 2.3 m). La altura segura sigue en **3.30 m** (D-043) hasta que él decida otra por escrito |

Consecuencias que ya están en `03_SIMULACION_RL/minimo_tesis/` (re-simulado el 20-oct; las versiones anteriores, con la USB y el gimbal,
quedaron en `minimo_tesis/_antes_20oct/` e `informes/_antes_20oct/`):
- `sensores.py`: `HFOV, VFOV = 68.3, 54.0`; `CAM_PITCH_MONTAJE = -2.4`; `LIDAR_PITCH_MONTAJE = -6.7`; el LiDAR tiene su propia inclinación.
- `sistema.py`: sin gimbal, la cámara y el TF03 **siguen el cabeceo del chasis** (nariz abajo al acelerar, arriba al frenar). `Z_PILOTO = 2.0`.
- El decisor MLP se reentrenó con esa geometría: el tamaño de la caja ya no se normaliza con los 38.9° de la USB.
  Resultados (D-079): protocolo del comité 100 % con 0 activaciones falsas; velocidad segura frente al panel 5 m/s (antes 11); en 3840 vuelos de prueba la IA+envolvente deja 148 riesgos no evitados contra 224 de las reglas. Con el piloto ≤ 4 m/s la IA queda igual que las reglas (11 contra 10).
- **El plus (variante H) usa la misma CSI**: su campo de visión es **68.3° × 54.0°**, no 62.2° × 48.8°. La CSI#2 es del mismo modelo pero no se midió:
  hasta medirla, asumir lo mismo y avisarle a Brahian. Si cambian esas cifras en la simulación del plus, anotarlo en `docs/DECISIONES.md`.
- La cuenta de Tania (parte física) hizo estos cambios aquí **por orden de Brahian**; aceptarlos y no revertirlos. Si algo en la simulación
  contradice estas mediciones, gana la medición.

## Qué es este proyecto

Proyecto de grado de Ingeniería Aeronáutica (Universidad de San Buenaventura): un cuadricóptero que **detecta
personas y evita obstáculos** (mínimo aprobado por el comité) y, como trabajo complementario ("plus"), **mantiene a la
vista a un sospechoso** en exteriores. Jetson Orin Nano + Pixhawk (ArduPilot 4.7) por MAVLink, YOLO26n, LiDAR TF03,
gimbal BaseCam. Autor: Brahian Andrés Orrego Osorio. Tania redacta el documento.

Dos IAs en el mínimo (YOLO preentrenado + decisor MLP) y una IA de refuerzo (PPO) en el plus, siempre con reglas
deterministas alrededor y un operador humano.

## Convenciones

- Escribir **"proyecto de grado"**, nunca "tesis" (salvo nombres ya existentes: `Tesis-IA-Drone`, `minimo_tesis/`).
- Español, lenguaje sencillo: Brahian no es programador.
- **Decisiones del plus (D-060, 17-oct):** no se le pregunta a Brahian con cuadros de sí o no. La sesión decide la mejor
  opción y anota el motivo. Si de verdad no puede decidir sola, le pregunta al Supervisor por `SendMessage`
  (`docs/EQUIPO_Y_SESIONES.md`). Brahian autoriza bajar e instalar programas gratuitos y de buena reputación desde su
  página oficial, sin permisos de administrador y fuera del repositorio.
- Pedir confirmación antes de lo irreversible o hacia afuera: `git push`, `gh repo create`, Releases, subir archivos,
  borrar, merge.
- Pruebas físicas: un paso a la vez, con instrucciones exactas, esperando confirmación.
- No cambiar la lógica de los scripts salvo que se pida. Antes de reescribir un archivo, copia `_vN` en
  `_archivo_versiones/codigo/`.
- No inventar números: toda cifra en un documento lleva el archivo de donde sale.
- El repositorio futuro es **público**: nada de IPs, usuarios, contraseñas, WiFi, seriales, rutas `C:\Users\...`,
  fotos de personas, Word ni PDFs del comité.

## Reglas duras del sistema (no negociables)

1. **Gimbal entre −45° y +15°**, pase lo que pase (`GIMBAL_MIN`, `GIMBAL_NADIR`, `GIMBAL_TACTICO` en `entorno.py` y
   `control.GimbalBaseCam.MIN`, D-014). PWM de AUX1: `pwm = 1500 + θ·500/45`. Prohibido ampliar el mapeo.
2. **Geocerca:** el dron no sale de la arena (`ARENA = 25 m`); salir = misión fallida, `R_GEOCERCA = -5`. En el dron
   real la fija ArduPilot.
3. **Búsqueda determinista al perder el objetivo** (`PERDIDA_IA = False`, D-015). La política solo decide con el
   objetivo fijado.
4. **Humano en el lazo:** la IA nunca decide quién es el sospechoso; lo confirma el operador con un clic.
5. **Árbitro de seguridad:** solo autoriza evadir ante amenaza real (persona a < 3 m, o a < 8 m acercándose). El
   bloqueo frontal por LiDAR (< 3 m) y la parada de emergencia (CH8) mandan sobre la IA.
6. La red **no estabiliza nada**: eso lo hacen los PID de ArduPilot y del gimbal.

Además: **`01_MINIMO_INDISPENSABLE/` está CONGELADO** (ver su `_LEEME.md`): es la versión histórica con la cámara USB y el gimbal. El dron real ya no
tiene gimbal ni USB (20-oct): el mínimo vigente es `03_SIMULACION_RL/minimo_tesis/` con las mediciones de arriba.

## Comandos (Windows, desde `03_SIMULACION_RL\`)

```
:: comprobar que el entorno importa
.venv\Scripts\python.exe -c "import entorno"

:: pruebas (reglas duras, entorno, mínimo, herramientas)
.venv\Scripts\python.exe -m unittest discover -s tests

:: mínimo indispensable: protocolo del comité (~10 s con --sin-degradadas; completo ~5 min)
.venv\Scripts\python.exe -m minimo_tesis.protocolo_comite --sin-degradadas

:: visor 3D en http://127.0.0.1:8765/
ABRIR_VISOR.bat

:: informe de un entrenamiento y evaluación en escenarios fijos -> informes\
.venv\Scripts\python.exe herramientas\resumir_metricas.py
.venv\Scripts\python.exe herramientas\evaluar_politica.py --barrido 25 --version v10-master

:: ver las redes (desde la raíz del proyecto)
03_SIMULACION_RL\.venv\Scripts\python.exe 06_REDES_NEURONALES_Y_MODELOS\ver_redes.py

:: entrenar (SOLO con aprobación de Brahian)
.venv\Scripts\python.exe -u entrenar_master.py
```

- `.venv` no se copia: `py -m venv .venv` y `pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu`
  + `numpy==2.5.3 gymnasium==1.4.0 stable_baselines3==2.9.0 scikit-learn==1.9.1 matplotlib==3.11.2 scipy==1.18.1`
  (mismas versiones que el original).
- Con un entrenamiento en marcha, `modelos_v15\ultimo.zip` y `salida\` cambian a cada rato: no copiarlos sin pararlo.
- Si falla una prueba de reglas duras, no se relaja la prueba: se consulta a Brahian.

## Ciclo de mejora

`resumir_metricas.py` + `evaluar_politica.py` → agente `supervisor-rl` (diagnóstico, máximo 3 cambios) → Brahian
aprueba → agente `implementador` (cambio, pruebas, bitácora) → reentrenar. Cerrar cada sesión con `/cierre-sesion`.
