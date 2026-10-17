# Encargo para la sesión "Simulación V17"

Del Arquitecto, 2026-10-17. **Empezar solo cuando Brahian apruebe D-049 a D-054** (`docs/DECISIONES.md`). Antes de
programar, leer: `CLAUDE.md`, `docs/EQUIPO_Y_SESIONES.md`, `docs/PLAN_V17_REFUERZO.md` (sobre todo las secciones 2, 4 y 5)
y `03_SIMULACION_RL/informes/diagnostico_v17_ia_aporta.md`.

## Qué hacer, en orden (detalle en el plan, sección 4)

1. **E1 · Traer la V16.** El código está en la rama `v16-simulacion` del repo viejo
   (`Desktop\Claude\Tesis-IA-Drone`, carpeta `simulacion/`; el repo viejo no se modifica). Llevar a `03_SIMULACION_RL/` lo
   que cambió respecto de `v15-curriculo` (`git diff v15-curriculo origin/v16-simulacion -- simulacion/`), con copias `_v15`
   de cada archivo que se reescriba en `_archivo_versiones/codigo/`. `01_` y `minimo_tesis/` no se tocan. Las 118 pruebas
   de esa rama deben pasar aquí.
2. **E6 · Escenario de la cancha** (D-051): zona 30 × 30 m; dos V de 90° (`ANCHO_PANEL_V17 = 1.0`, `ALTO_PANEL_V17`
   aleatorio 1.9-2.2 m) con vértices a 10 m y bocas opuestas, con azar de ±2 m y ±20° por conjunto; 1 ladrón y 1 civil.
3. **E2 + E3 · Botones** (D-049): con el objetivo fijado, QUEDARSE, RODEAR_IZQ, RODEAR_DER, ACERCARSE, ALEJARSE, SUBIR, BAJAR.
   La evasión la elige el árbitro por regla. Prueba nueva: con una amenaza real, la evasión ocurre sea cual sea el botón.
4. **E4 · Máscara** (D-050): `MaskablePPO` de `sb3-contrib` (fijar la versión que corresponda a SB3 2.9.0 en
   `CLAUDE.md`). Un solo botón permitido en los pasos sin decisión; BAJAR prohibido con alguien a < 8 m o a 3.30 m.
   La política nueva arranca de cero en la capa de salida (cambió el número de botones); de la V16 se puede transferir
   el resto si ayuda: medirlo.
5. **E5 · Partidas desde la activación** (D-053).
6. **E7 · Ajustes por paneles de 2 m:** 360° de entrada (altura y pitch para que el LiDAR los mapee), búsqueda tras el panel
   (rodear la V a 4-5 m en lugar del muro de canto), stand-off. Medir antes y después.
7. **E8 · Línea base:** programar B2 (regla de posicionamiento por cobertura) y extender
   `herramientas/medir_ia_aporta.py` a la misión V17 (512 partidas). Medir **B0, B1 y B2** y escribirlos en
   `docs/PROGRESO_V17.md`. Si B0 da > 80 % de custodia ≥ 60 s, avisar al Arquitecto antes de seguir.
8. **Reglas del ladrón y del civil (plan 5.1)**, una por una, con B0 y B2. Informe con la tabla con y sin cada una.
9. **Preparar las corridas de la sección 5.2** (constantes `--set`, carpetas por corrida) y dejar los comandos exactos en
   `docs/PROGRESO_V17.md`. Solo prueba de humo (≤ 15 min); **los entrenamientos los aprueba y lanza Brahian**.

## Reglas

- Solo escribir en `03_SIMULACION_RL/` y en `docs/PROGRESO_V17.md`. Commits de sus propios archivos; nunca `git push` sin
  que Brahian lo confirme en el chat.
- Reglas duras de `CLAUDE.md` como pruebas; si una falla, no se relaja: se consulta a Brahian.
- Toda cifra con el archivo de donde sale. Español sencillo; "proyecto de grado", nunca "tesis".
- Al terminar cada paso, avisar al Arquitecto con `SendMessage` (su id está en `docs/EQUIPO_Y_SESIONES.md`).
