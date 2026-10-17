# Diagnóstico · ¿la política PPO de la V15 aporta algo?

Arquitecto, 2026-10-16/17. Modelo `modelos_v15/ultimo.zip` (229.4 M pasos, `modelos_v15/estado_entrenamiento.json`).
Herramienta: `herramientas/medir_ia_aporta.py` (nueva) y `herramientas/evaluar_politica.py`. Datos crudos:
`ia_aporta_v15_mision_n4.json`, `ia_aporta_v15_fijos.json`, `ia_aporta_v15_probs.json`, `barrido_v15.csv`.

**Respuesta corta: no.** La política V15 rinde lo mismo que "quedarse quieto siempre" y que elegir al azar. Todo el
desempeño lo dan las reglas deterministas. 222 M pasos de entrenamiento no cambiaron nada medible.

## 1. Misión completa (nivel 4), política contra "solo reglas" y azar

256 partidas de hasta 5 min por fila, mismas semillas (123), ladrón congelado del entrenamiento, dificultad 0.21.
"Mantener", "avanzar" y "evadir_izq" = la red reemplazada por esa acción fija (las reglas siguen igual). Margen de error
(95 %) con 256 partidas: ±5.8 puntos en "cumplida", ±3.9 en "custodia ≥ 60 s".

| Política | Cumplida (rendición) | Custodia ≥ 60 s | Racha máx. media (s) | Vista total (s) | Alcanzado | Pérdidas / partida | t re-adq. (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| V15 229 M (determinista) | 33.2 % | 11.3 % | 35.4 | 99 | 2.7 % | 17.9 | 7.7 |
| V15 229 M (estocástica, como entrena) | 31.2 % | 10.9 % | 35.0 | 97 | 3.1 % | 18.5 | 7.8 |
| V15 al empezar (`base_v15.zip`, 7 M de la V14) | 35.2 % | 13.7 % | 36.7 | 98 | 2.7 % | 18.1 | 7.5 |
| **Solo reglas: siempre MANTENER** | **34.0 %** | 10.2 % | 34.3 | 98 | 2.7 % | 18.3 | 8.1 |
| Siempre EVADIR_IZQ | 32.4 % | 12.1 % | 34.7 | 95 | 2.7 % | 17.8 | 8.0 |
| Al azar (uniforme) | 32.8 % | 7.8 % | 33.7 | 96 | 2.7 % | 18.5 | 7.4 |
| Siempre AVANZAR | 14.1 % | 0.0 % | 26.1 | 90 | 2.7 % | 26.5 | 7.6 |

Todas las diferencias entre V15, base, mantener, evadir y azar caben en el ruido. Solo "avanzar siempre" es peor.

## 2. Escenarios fijos (50 partidas, 120 s, éxito = 30 s seguidos a la vista)

Cumplida · fracción del tiempo a la vista.

| Escenario | V15 229 M | Siempre MANTENER | Siempre AVANZAR | Azar |
|---|---|---|---|---|
| abierto | 100 % · 0.97 | 100 % · 0.97 | 100 % · 0.95 | 100 % · 0.97 |
| cambio_brusco | 100 % · 0.88 | 100 % · 0.88 | 90 % · 0.77 | 100 % · 0.88 |
| tras_muro | 100 % · 0.71 | 100 % · 0.72 | 72 % · 0.63 | 100 % · 0.72 |
| detras_punta | 100 % · 0.80 | 98 % · 0.82 | 84 % · 0.62 | 100 % · 0.82 |
| cambia_lado | 98 % · 0.80 | 100 % · 0.81 | 72 % · 0.64 | 100 % · 0.79 |
| debajo | 88 % · 0.79 | 84 % · 0.75 | 4 % · 0.04 | 82 % · 0.73 |

**Barrido de checkpoints de la V15** (`barrido_v15.md`, rehecho con `modelos_v15`; reemplaza la tabla de
`resumen_v15-231M.md`, que venía de la V10): media de los 6 escenarios 0.97 · 0.96 · 0.97 · 0.97 · 0.96 · 0.97 · 0.97 en
7 (fila "base v9" del informe: es `base_v15.zip`, la etiqueta es de la herramienta) · 25 · 50 · 100 · 150 · 200 · 230 M.
Plano de principio a fin.

## 3. Por qué la red decide casi al azar (medido y leído en el código)

Probabilidades de la red en 41 641 estados reales donde decide (64 partidas del nivel 4, `ia_aporta_v15_probs.json`):
probabilidad de la acción preferida 0.19 en promedio, entropía 2.11 de 2.30. Probabilidad media de AVANZAR: **0.002**; las
otras nueve, entre 0.05 y 0.16.

1. **Nueve de diez acciones hacen lo mismo.** Con el ladrón fijado y a la vista (`entorno.py`, `step`): la guiñada y el
   gimbal los hace el seguimiento automático; GIRAR solo actúa si no lo ve; DESCENDER y GIMBAL_* no tienen efecto en
   FIJADO (comentario junto a `CLASES`); EVADIR_* y DETENER solo actúan si hay amenaza y la misma acción se repite 3 cuadros
   (`N_CONFIRMACION`). Sin amenaza, la única acción que cambia algo es AVANZAR. La red aprendió una sola cosa —no usar
   AVANZAR, que de verdad empeora (tabla 1)— y reparte el resto. Repartir parejo entre 9 acciones da ln 9 = 2.20: lo medido
   (2.11) es eso.
2. **Más de la mitad del lote de entrenamiento es ruido.** La red decide solo en el 43 % de los pasos
   (`mascara_decision`), pero `VecDron` (`entrenar_master.py`) entrega a PPO todos los pasos: en el 57 % restante la acción
   se ignora y su "ventaja" es azar.
3. **El bono de entropía empuja hacia el azar** (`ent_coef = 0.01`). Si las acciones casi no cambian el resultado, la
   ventaja normalizada no prefiere ninguna y lo único que queda es ese empuje: por eso la entropía sube de 1.97 a 2.12
   (`resumen_v15-231M.md`).
4. Consecuencia de seguridad: ante una amenaza, la maniobra la elige la red (`acc_ev = acc_dron` en FIJADO). Con una red al
   azar, 3 cuadros seguidos de la misma maniobra son poco probables; hoy salva al dron el **reflejo** del árbitro, que no
   depende de la red ("alcanzado" 2.7 % igual en todas las filas). La V17 debe dejar la maniobra de evasión a una regla.

La sesión de la V16 en la nube llegó al mismo hallazgo por otro camino (`docs/PROGRESO_V16.md` de la rama
`v16-simulacion`, fase A5: cuatro estilos de pilotaje dan 42-51 s de vista en 150 s).

## 4. Cómo se reproduce

```
cd 03_SIMULACION_RL
.venv\Scripts\python.exe herramientas\medir_ia_aporta.py mision --pol v15,v15-est,v15base,mantener,avanzar,evadir_izq,azar --n 256 --nivel 4 --salida informes\ia_aporta_v15_mision_n4.json
.venv\Scripts\python.exe herramientas\medir_ia_aporta.py fijos --pol v15,mantener,avanzar,azar --n 50 --salida informes\ia_aporta_v15_fijos.json
.venv\Scripts\python.exe herramientas\medir_ia_aporta.py probs --n 64 --salida informes\ia_aporta_v15_probs.json
.venv\Scripts\python.exe herramientas\evaluar_politica.py --modelo modelos_v15\base_v15.zip --modelo modelos_v15\checkpoints\dron_master_24728064_steps.zip ... --version v15
```

Tiempos en el portátil (con otra medición corriendo a la vez): misión 150-254 s por política (256 partidas de 5 min),
escenarios fijos 47-96 s por política (logs de la medición).
