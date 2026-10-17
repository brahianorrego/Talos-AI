# Barrido de checkpoints en escenarios fijos · v15

Política determinista · 50 partidas por escenario · semillas 0.. · nivel de currículo 0.10 · máx. 120 s · 2026-10-17 02:27

Todos los números: `barrido_v15.csv`.

## Misiones cumplidas por escenario a lo largo del entrenamiento

| M pasos | abierto | cambio_brusco | tras_muro | detras_punta | cambia_lado | debajo | Media | Alcanzado (media) | Jitter yaw (media) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| base v9 | 1.00 | 1.00 | 1.00 | 0.98 | 1.00 | 0.82 | 0.97 | 0.00 | 1.67 |
| 25 | 1.00 | 1.00 | 1.00 | 0.98 | 1.00 | 0.80 | 0.96 | 0.00 | 1.65 |
| 50 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.80 | 0.97 | 0.00 | 1.78 |
| 100 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.84 | 0.97 | 0.00 | 1.63 |
| 150 | 1.00 | 1.00 | 1.00 | 1.00 | 0.98 | 0.80 | 0.96 | 0.00 | 1.76 |
| 200 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.84 | 0.97 | 0.00 | 1.64 |
| 230 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.84 | 0.97 | 0.00 | 1.61 |

## Detalle del último modelo (dron_master_229998592_steps.zip)

| Escenario | Cumplida | Perdido | Alcanzado | Panel | Geocerca | Tiempo agotado | Duración (s) | A la vista | Pérdidas | Re-adquiere | t re-adq. (s) | Dist. mín. (m) | Altura máx. (m) | Gimbal mín/máx (°) | Recompensa | de ella, control | Jitter cabeceo (°/paso) | Jitter yaw (°/s/paso) | Jitter gimbal (°/s/paso) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| abierto | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 31.4 | 0.97 | 0.02 | 0.02 | 0.1 | 4.5 | 3.8 | -45 / 8 | 82.0 | 0.0 | 3.04 | 1.05 | 4.52 |
| cambio_brusco | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 35.6 | 0.87 | 2.42 | 2.42 | 1.1 | 1.1 | 5.3 | -45 / 3 | 81.4 | 0.0 | 1.59 | 1.63 | 2.97 |
| tras_muro | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 50.9 | 0.73 | 1.28 | 1.28 | 10.4 | 2.9 | 4.2 | -45 / -1 | 81.4 | -0.0 | 0.46 | 0.45 | 1.29 |
| detras_punta | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 49.6 | 0.78 | 1.38 | 1.38 | 7.6 | 3.0 | 3.5 | -45 / 5 | 80.0 | -0.0 | 0.77 | 0.78 | 1.46 |
| cambia_lado | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 44.0 | 0.80 | 1.12 | 1.12 | 7.3 | 2.8 | 3.7 | -45 / 5 | 81.2 | 0.0 | 0.53 | 0.68 | 1.20 |
| debajo | 0.84 | 0.16 | 0.00 | 0.00 | 0.00 | 0.00 | 44.0 | 0.75 | 2.50 | 2.34 | 0.9 | 2.1 | 5.3 | -45 / -5 | 67.1 | 0.0 | 2.20 | 5.04 | 3.69 |

Acciones elegidas con la IA al mando (fracción):

| Escenario | MANTENER | EVADIR_IZQ | EVADIR_DER | DETENER_ASCENDER | GIRAR_IZQ | GIRAR_DER | AVANZAR | DESCENDER | GIMBAL_ARRIBA | GIMBAL_ABAJO |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| abierto | 0.01 | 0.20 | 0.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.08 | 0.05 | 0.49 |
| cambio_brusco | 0.01 | 0.18 | 0.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.12 | 0.02 | 0.64 |
| tras_muro | 0.05 | 0.12 | 0.04 | 0.02 | 0.00 | 0.00 | 0.00 | 0.12 | 0.32 | 0.33 |
| detras_punta | 0.01 | 0.10 | 0.11 | 0.04 | 0.00 | 0.00 | 0.00 | 0.06 | 0.08 | 0.60 |
| cambia_lado | 0.01 | 0.05 | 0.02 | 0.00 | 0.00 | 0.00 | 0.00 | 0.29 | 0.16 | 0.46 |
| debajo | 0.04 | 0.12 | 0.01 | 0.00 | 0.00 | 0.01 | 0.00 | 0.11 | 0.02 | 0.69 |
