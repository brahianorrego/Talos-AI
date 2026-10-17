# Resumen de entrenamiento · v10-master-231M

Corrida: salida\metricas.json · 3520 iteraciones · 230.7 M pasos · motor Stable-Baselines3 PPO · nivel de currículo actual 0.19.
Ventana actual = últimas 50 iteraciones (3.3 M pasos, 1534 partidas de entrenamiento, política estocástica).

## Indicadores (ventana actual vs anterior)

| Indicador | Actual | Anterior | Inicio de la corrida | Cambio |
|---|---:|---:|---:|---|
| Misión cumplida (éxito) | 45 % | 47 % | 85 % | peor |
| Perdido (búsqueda agotada) | 2 % | 3 % | 9 % | = |
| No encontrado | 4 % | 4 % | 0 % | = |
| Alcanzado por el ladrón | 1 % | 1 % | 0 % | = |
| Choque con peatón (partidas con peatones) | 0 % | 0 % | 2 % | = |
| Choque con panel | 0 % | 0 % | 0 % | = |
| Sale de la geocerca | 0 % | 0 % | 0 % | = |
| Tiempo con el objetivo a la vista | 50 % | 51 % | 84 % | = |
| Duración media de la partida (s, estimada) | 213.6 | 208.1 | 160.3 |  |
| Recompensa total por partida | 48.70 | 49.97 | 46.19 | peor |
|   de ella, castigo de control (jitter + esfuerzo) | 0.99 | 0.92 | 0.77 | = |
| Pérdidas del objetivo por partida | 15.78 | 15.12 | 6.50 | peor |
| Re-adquisiciones por partida | 9.84 | 9.32 | 2.07 | mejor |
| Jitter: Σ|Δu| por paso con la IA al mando (3 ejes) | 0.006 | 0.006 | 0.004 | = |
| Entropía de la política (máx. 2.30) | 2.12 | 2.12 | 1.97 |  |

Acciones (ventana actual, %): decide con el objetivo fijado / en la búsqueda tras perderlo.

| MANTENER | EVADIR_IZ | EVADIR_DE | DETENER_A | GIRAR_IZQ | GIRAR_DER | AVANZAR | DESCENDER | GIMBAL_AR | GIMBAL_AB |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 11 / 0 | 14 / 0 | 10 / 0 | 8 / 0 | 6 / 0 | 10 / 0 | 0 / 0 | 12 / 0 | 15 / 0 | 13 / 0 |
En la búsqueda casi nunca usa: MANTENER, EVADIR_IZQ, EVADIR_DER, DETENER_ASCENDER, GIRAR_IZQ, GIRAR_DER, AVANZAR.

## Tendencia por tramos de 50 M pasos

| M pasos | Cumplida | Perdido | Alcanzado | Panel | Geocerca | Dur. (s) | Recompensa | Σ|Δu|/paso | Entropía | Nivel |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0-50 | 60 % | 7 % | 1 % | 0 % | 0 % | 195 | 42.1 | 0.002 | 1.93 | 0.34 |
| 50-100 | 47 % | 2 % | 1 % | 0 % | 0 % | 211 | 50.2 | 0.003 | 2.00 | 0.27 |
| 100-150 | 47 % | 2 % | 1 % | 0 % | 0 % | 211 | 49.7 | 0.006 | 2.07 | 0.27 |
| 150-200 | 46 % | 2 % | 1 % | 0 % | 0 % | 212 | 49.5 | 0.006 | 2.10 | 0.26 |
| 200-231 | 46 % | 2 % | 1 % | 0 % | 0 % | 211 | 49.4 | 0.006 | 2.12 | 0.26 |
Pendiente de la tasa de cumplidas en los últimos 100 M pasos: -0.9 puntos por cada 100 M (ruido por iteración ±9 puntos).

## Escenarios fijos (evaluar_politica.py)

Fuente: `barrido_v10-master.csv` (política determinista, mismas semillas).

| M pasos | cumplida abierto | cumplida cambio_brusco | cumplida tras_muro | cumplida debajo | alcanzado | jitter cab/yaw/gmb |
|---:|---:|---:|---:|---:|---:|---:|
| 125 | 100 % | 0 % | 0 % | 2 % | 0 % | 0.98 / 0.25 / 1.26 |
| 150 | 100 % | 0 % | 0 % | 2 % | 6 % | 0.98 / 0.30 / 1.29 |
| 175 | 100 % | 0 % | 0 % | 14 % | 0 % | 0.98 / 0.25 / 1.27 |
| 200 | 100 % | 0 % | 0 % | 0 % | 0 % | 1.00 / 0.25 / 1.26 |
| 225 | 100 % | 0 % | 0 % | 6 % | 0 % | 0.97 / 0.25 / 1.27 |

## Lo que no se registra (y cómo registrarlo en el próximo entrenamiento)

- No hay logs de TensorBoard (SB3 se lanzó sin `tensorboard_log`).
- Duración real de la partida: aquí se estima como pasos / partidas terminadas. Guardar `ep_len` en `VecDron.fin` (entrenar_master.py) y su media en `resumen()`.
- Recompensa por componente: solo se separa el castigo de control. Acumular cada término de `rew_d` (vista, rango, guía, descubre, pierde, maniobra, éxito, fallas, control) en `info["r_comp"]` dentro de `entorno.step` y promediarlo por partida en `VecDron`.
- Jitter por eje (cabeceo, yaw, gimbal): hoy se guarda la suma de los 3. Devolver `|u - u_prev|` por eje en `info` y guardar 3 promedios en `m["control"]`. Mientras tanto, el barrido de escenarios fijos sí lo mide.
- Gimbal mínimo alcanzado (regla dura -45°): guardar `min(cam_pitch)` por iteración.
