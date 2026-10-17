# V17 · Reglas del ladrón y del civil, una por una (plan 5.1)

Sesión Simulación V17, 2026-10-17. Misión de la cancha (`NIVEL_V17`), partidas de 5 min, misma semilla (123) para todas
las filas. Herramienta: `herramientas/medir_ia_aporta.py v17 --pol b0|b2 --n 128 [--set REGLA=0]`. Datos crudos:
`informes/v17/l_*.json` (B0 = `l_<fila>.json`, B2 = `l_<fila>_b2.json`). Con 128 partidas el margen de error (95 %) de
un porcentaje cercano a 50 % es **±8.7 puntos**; cerca de 0 % o 100 %, ±2-4.

- **M1** = custodia: 60 s **seguidos** con el ladrón a la vista y el ID correcto (definición del plan, sección 2).
- **Racha ≥ 30 s** y **custodia V16** (rendición o 60 s de vista acumulada) se agregaron porque M1 queda en ~0 % en todas
  las filas (ver la conclusión).
- **M2** = pérdidas de más de 1 s recuperadas en 10 s o menos. **M3** = rendición.

## Solo reglas (B0: siempre QUEDARSE)

| Fila | M1 ≥60 s seguidos | Racha ≥30 s | Custodia V16 | Racha media (s) | M2 ≤10 s | Pérdidas/partida | M3 rendición | Alcanzado | RECONFIRMAR/partida | Cambios de ID sin detectar | Ruleta (partidas) | Escudo (partidas) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Todas las reglas | 0.8 % | 43.0 % | 95.3 % | 29.6 | 76.6 % | 21.4 | 14.8 % | 0 % | 5.5 | 0 | 97.7 % | 82.8 % |
| Sin L1 (posturas) | 1.6 % | 48.4 % | 96.1 % | 30.9 | 76.8 % | 20.0 | 19.5 % | 0.8 % | 5.1 | 0 | 97.7 % | 77.3 % |
| Sin L2 (salto) | 0.8 % | 42.2 % | 97.7 % | 30.1 | 76.7 % | 21.5 | 14.8 % | 0 % | 5.6 | 0 | 98.4 % | 81.2 % |
| Sin L3 (ruleta) | 0.8 % | 44.5 % | 93.0 % | 30.7 | 73.6 % | 19.2 | 17.2 % | 0 % | 5.2 | 0 | 0 % | 78.1 % |
| Sin L4 (escudo) | 0 % | 38.3 % | 95.3 % | 28.0 | 72.5 % | 20.3 | 14.1 % | 0 % | 4.3 | 0 | 97.7 % | 0 % |
| Sin C1 (civil curioso) | 0 % | 46.9 % | 94.5 % | 29.8 | 80.7 % | 24.5 | 13.3 % | 0.8 % | 10.1 | 0 | 96.9 % | 96.9 % |
| Ninguna | 0.8 % | 43.0 % | 91.4 % | 28.4 | 77.0 % | 22.3 | 12.5 % | 0 % | 7.0 | 0 | 0 % | 0 % |

## Regla de posicionamiento (B2)

| Fila | M1 | Racha ≥30 s | Custodia V16 | Racha media (s) | M2 | M3 | Alcanzado |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas las reglas | 0 % | 54.7 % | 93.0 % | 31.6 | 76.6 % | 22.7 % | 0 % |
| Sin L1 | 0 % | 55.5 % | 93.0 % | 31.1 | 78.3 % | 20.3 % | 0 % |
| Sin L2 | 1.6 % | 55.5 % | 96.1 % | 32.4 | 77.1 % | 19.5 % | 0 % |
| Sin L3 | 0.8 % | 46.1 % | 92.2 % | 30.3 | 76.0 % | 12.5 % | 0.8 % |
| Sin L4 | 1.6 % | 49.2 % | 93.0 % | 30.2 | 73.9 % | 19.5 % | 0.8 % |
| Sin C1 | 0.8 % | 50.8 % | 97.7 % | 31.2 | 79.6 % | 15.6 % | 0 % |
| Ninguna | 0 % | 38.3 % | 94.5 % | 27.5 | 75.3 % | 9.4 % | 0 % |

## Qué dice, regla por regla (criterios del plan, 5.1)

| Regla | Criterio del plan | Medido | Propuesta |
|---|---|---|---|
| L1 posturas | B0 entre 20 y 80 % | M1 ≈ 0 % con y sin ella; racha ≥30 s 43 % con ella, 48 % sin ella (dentro del ruido) | **Se queda** (realismo; no cambia la dificultad de forma medible) |
| L2 salto | Alcanzado de B0 ≤ 5 % | 0 % con salto (a 3.30 m no llega) | **Se queda** |
| L3 ruleta | Como L1 y aparece en ≥ 30 % de las partidas | Aparece en 98 % de las partidas; no mueve la custodia fuera del ruido | **Se queda** |
| L4 escudo | Dispara RECONFIRMAR sin cambios de ID sin detectar | RECONFIRMAR 4.3 → 5.5 por partida; 0 cambios sin detectar en las 2 944 partidas con escudo (1 536 de la línea base, `v17_linea_base.json`, y 1 408 de esta tabla) | **Se queda** (humano en el lazo intacto) |
| C1 civil curioso | No baja la custodia de B0 más de 3 puntos | Racha ≥30 s 46.9 % sin él y 43.0 % con él (3.9 puntos, dentro del ruido de ±8.7) | **Se queda**; confirmar con 512 partidas si se quiere el umbral de 3 puntos exacto |

## Conclusión (para el Arquitecto)

1. **Ninguna regla del ladrón cambia la dificultad fuera del ruido.** Lo que hace difícil la cancha es la base: el ladrón
   táctico se esconde detrás de una V cada pocos segundos (en una revisión de diagnóstico de 64 partidas sin reglas nuevas,
   la mayoría de las pérdidas lo encontraban "escondido" y tapado por el panel; no se guardó como informe) y, al pasar 1 s
   sin verlo, la búsqueda determinista reinicia el contador. Hay ~21 pérdidas de más de 1 s por partida (tabla de arriba).
2. **Con la M1 del plan (60 s seguidos) todas las filas dan 0-1.6 %**, también B2: la métrica está saturada y no puede
   decidir nada (ni las reglas de 5.1 ni, después, si la IA aporta). La racha ≥ 30 s queda entre 38 y 56 %, en la ventana
   20-80 % que el plan pide para que haya algo que mostrar; la custodia de la V16 (vista acumulada) queda en 91-98 %,
   demasiado fácil.
3. Por eso se consultó al Arquitecto qué M1 usar (opciones: racha ≥ 30 s, custodia de la V16, o ablandar al ladrón).
