# Plan de la noche · 19 de octubre

Pedido del Coordinador (Brahian trabaja toda la noche). Cada paso dice quién lo hace y **qué número decide**. Todo con
512 partidas por política y las mismas semillas; el margen de error de M1 es de unos ±4 puntos. Sin `git push`; reglas
duras de `CLAUDE.md` intactas.

Punto de partida (cancha real, paneles de 1.5 × 2.2-2.3 m, `informes/v17/v173_base_b*.json` y `b4_real_*.json`):
M1 B0 11.7 %, B1 13.5 %, B2 17.2 %, **B3 24.6 %**, B4 19.5 %, B4\* 22.5 %.

| # | Paso | Quién | Número que decide |
|---|---|---|---|
| 1 | Medir en la cancha real la V17.2 (50 M) y la V17.3 (10 M) | Simulación V17 | M1 de la V17.2 frente a B3 (24.6 %): si ya llega a 22-27 %, no hay que reentrenar para adaptarla |
| 2 | Probar D-059 C (D-069, aprobada por Brahian según el Coordinador): la red decide el tramo tras perderlo con el interruptor `PERDIDA_IA`; **corrida aparte y reversible**, con la búsqueda determinista como control y `CLAUDE.md` sin tocar | Simulación V17 | M1 con D-059 C frente al mismo modelo sin él. Se queda si sube ≥ 5 puntos y la seguridad sigue en 0 |
| 3 | Afinar la V17.2 en la cancha real (V17.4, 10 M, suavidad vertical 0.1), con D-059 C si el paso 2 lo aprobó | Simulación V17 | M1 de la V17.4 frente a B3. Si no colapsa (probabilidad de la preferida < 0.9) y M1 ≥ B3, es la política V17 |
| 4 | Revisión de cada resultado con `supervisor-rl` y aviso al Coordinador solo si hay un número decisivo o un problema | Arquitecto | M1, vaivén de altura (cambios de sentido por minuto) y seguridad (alcanzado, choques, gimbal, geocerca) |
| 5 | Grabar con la política elegida las repeticiones para Unreal (rendición, re-encuentro, salto, civil curioso, cambio de V) en `repeticiones_v17/` | Simulación V17 | Cada una dura ≥ 60 s y trae los campos de `foto()` |
| 6 | Campus y mundo realista en Unreal con esas repeticiones; modelo del dron y pan-tilt en la estación | Visor, Hardware | El importador reproduce una repetición completa sin errores, a ≥ 24 cuadros por segundo con la RTX |

**Qué cuenta como éxito de la noche:** una política V17 medida en la cancha real contra B0-B4, con su informe, y las
repeticiones grabadas. **Qué obliga a parar:** un choque, una salida de la geocerca, el gimbal fuera de −45°..+15° o una
violación de la regla 3 fuera de la corrida de prueba del paso 2.
