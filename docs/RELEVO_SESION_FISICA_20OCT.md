# Relevo de la sesión física (cuenta de Tania) a la sesión de simulación · 20-oct-2026

Brahian cierra la sesión física y deja esta sesión sola para que, al reiniciarse el uso (~4:30 p. m.), **lea esto, revise, apruebe y siga con la simulación del plus**.
Todo lo de abajo ya está hecho y guardado; no hay nada a medias salvo lo marcado "pendiente".

## 1. Lo que cambió en `03_SIMULACION_RL/` (por orden de Brahian; aceptar, no revertir)

La geometría medida del dron real (D-078, tabla en `CLAUDE.md`) ya está en la simulación del mínimo:
- `minimo_tesis/sensores.py`: `HFOV, VFOV = 68.3, 54.0`; `CAM_PITCH_MONTAJE = -2.4`; `LIDAR_PITCH_MONTAJE = -6.7`; el LiDAR tiene inclinación propia.
- `minimo_tesis/sistema.py`: sin gimbal, cámara y LiDAR siguen el cabeceo del chasis (`self.cam`, `self.lid_pitch`, `suelo_lidar(m)`); `Z_PILOTO = 2.0` (variable `MINIMO_Z_PILOTO`); `Z_SEGURA = 3.30` (D-043).
- `decisor_ia.py`, `protocolo_comite.py`, `tests/test_minimo_tesis.py`, `tests/test_decisor_ia.py` adaptados (13 + 6 pruebas pasan). El texto del informe del comité se genera con las constantes, ya no trae números fijos.
- Nuevo: `minimo_tesis/dividir_replays.py` (parte los replays en un archivo por escenario) y, en `index.html`, el grupo **"Mínimo · por escenario"** del selector; `evaluar_decisores.py` ahora guarda `inicio` en los replays.
- Copias de lo anterior: `minimo_tesis/_antes_20oct/` e `informes/_antes_20oct/`.

## 2. Resultados con la geometría medida (D-079)

- Protocolo del comité: 13 escenarios, **100 %**, 0 choques, 0 activaciones falsas. Velocidad segura máxima frente al panel: **5 m/s** (antes 11): el rayo del LiDAR a −6.7° desde 2.0 m toca el suelo a ~17 m (antes ~26 m con el gimbal).
- Decisor MLP **reentrenado** (2.55 M cuadros; AUC 0.961, antes 0.974). En 3840 vuelos de prueba: riesgos no evitados 224 (reglas) → 148 (IA + envolvente); choques 117 → 97; persona a < 2 m bajo 3.30 m 516 → 212. Con el piloto ≤ 4 m/s la IA queda igual que las reglas (11 contra 10).
- **Trampa que ya pasó (no repetir):** `entrenar_decisor.py` reutiliza `datos/*.npz` y `datos/clf_*.pkl` si existen; la primera corrida salió con los de la geometría vieja. Al cambiar la geometría, apartarlos antes de entrenar. Quedó en el README del mínimo.
- `decision.pkl` y `decision.json` nuevos están listos; **no hay `sistema_minimo.py`** para la Jetson todavía.

## 3. Para que revises y apruebes

1. Que `docs/DECISIONES.md` D-077, D-078 y D-079 (escritas por la sesión física) no choquen con tus decisiones; si algo choca, gana la medición.
2. **Altura del mínimo:** Brahian propone 2.0 m como máximo; D-043 dice 3.30 m. Sigue pendiente su decisión por escrito; mientras tanto el simulador usa 2.0 m (`MINIMO_Z_PILOTO`).
3. `01_MINIMO_INDISPENSABLE/minimo_tesis/` es la copia **congelada** (con huellas SHA-256) y **no** se tocó: es la versión previa a la geometría medida. Decide si se re-congela con la nueva.
4. `02_JETSON_A_BORDO/` sigue de la época del gimbal (config, README). La carpeta viva y actual del código de la Jetson es `Proyecto-Grado-Minimo/02_JETSON_MINIMO/`.
5. El plus (variante H) usa la misma CSI: 68.3° × 54.0° (la CSI#2 no se midió; asumir lo mismo hasta medirla).

## 4. Ver el mínimo en el visor (pedido de Brahian)

`03_SIMULACION_RL\ABRIR_VISOR.bat` → http://127.0.0.1:8765/ → selector arriba → grupos **"Mínimo · por escenario · …"** (un escenario por opción, con el decisor que se elija: comité/reglas, IA sola, IA + envolvente, estricta) o "Proyecto de grado" (los 13 seguidos).
Al terminar cada escenario sale "ESCENARIO TERMINADO". Si se vuelven a correr `protocolo_comite` o `evaluar_decisores`, correr después `.venv\Scripts\python.exe -m minimo_tesis.dividir_replays`.
La simulación **en vivo** (`04_VISOR_Y_MOTOR_GRAFICO/en_vivo.py`) corre el entorno de RL "dron vs ladrón", no el mínimo: el mínimo se ve como repetición, no en vivo.

## 5. Lo físico que sigue (no es tuyo; solo para que lo sepas)

Calibrar acelerómetro y brújula (Brahian, Mission Planner); probar CH8 y batería baja; repetir las tomas de campo con la geometría medida; `sistema_minimo.py` en modo sombra; primer vuelo con la Jetson (el mínimo **nunca ha volado con ella**).
Documentos de la parte física: `Proyecto-Grado-Minimo/docs/PROCEDIMIENTO_REPLICABLE.md` y `HISTORIAL_PRUEBAS_FISICAS.md` (copias en `docs/` y `08_EVIDENCIA_Y_DIAGRAMAS/`); evidencia en `08_EVIDENCIA_Y_DIAGRAMAS/anexo_historial_octubre_2026/INDICE.md`.
