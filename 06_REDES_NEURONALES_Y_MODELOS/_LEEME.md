# 06 · Redes neuronales y modelos

Los modelos **se quedan en `03_SIMULACION_RL/`** porque los scripts los buscan ahí. Esta carpeta tiene la
herramienta para verlos (`ver_redes.py`) y este índice. Los `.zip`, `.pt` y `.pkl` pesados **no van a Git**
(van a Google Drive o a una Release de GitHub).

## Índice de modelos

| Archivo (en `03_SIMULACION_RL/`) | Qué es | Tamaño | ¿A la Jetson? |
|---|---|---|---|
| `minimo_tesis/decision.json` | Decisor MLP del **mínimo** (15 entradas → 32 → 16 → 1), pesos en JSON | 23 KB | **Sí** (se evalúa con NumPy) |
| `minimo_tesis/decision.pkl` | El mismo decisor en formato scikit-learn 1.9.1 | 21 KB | Solo si la Jetson tiene la misma versión de scikit-learn |
| `modelos_v15/ultimo.zip` | Política PPO de la **V15** (192 entradas → 128 → 128 → 10 acciones), 229.4 M pasos | 1.5 MB | No (PC) |
| `modelos_v15/checkpoints/` | Una copia de la V15 por cada millón de pasos (229 archivos) | — | No |
| `modelos_v15/base_v15.zip` | Punto de partida de la V15 (último de la V14) | 1.0 MB | No |
| `modelos_v15/ladron_congelado.pt` | Red del ladrón (no aprende durante la V15) | 170 KB | No |
| `modelos/dron_politica.json` | Pesos de la última política PPO exportados para la Jetson | 864 KB | Solo si algún día se usa la política |
| `modelos_master/` | V10 (769.8 M pasos, 761 checkpoints) | 1.2 GB | No |
| `modelos_v12/`, `modelos_v14/` | V12 y V14 | 18 y 14 MB | No |
| `modelos/ultimo.pt`, `modelos/bloques/` | PPO propio en torch (versiones v1-v9) | — | No |

Fuentes: tamaños medidos el 2026-10-16; pasos de la V15 en `modelos_v15/estado_entrenamiento.json`; arquitectura
PPO en `entrenar_master.py` (línea ~197); arquitectura del decisor en `minimo_tesis/decision.json`.

## Ver las redes

Desde la raíz del proyecto:
```
03_SIMULACION_RL\.venv\Scripts\python.exe 06_REDES_NEURONALES_Y_MODELOS\ver_redes.py
```
Imprime capas, neuronas y parámetros; guarda diagramas e histogramas en `08_EVIDENCIA_Y_DIAGRAMAS/redes/` y muestra
qué probabilidades da cada red en una escena de ejemplo.
