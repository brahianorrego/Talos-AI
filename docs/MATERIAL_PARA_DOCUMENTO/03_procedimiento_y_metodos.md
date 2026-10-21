# 03 · Procedimiento y métodos

Para repetir el trabajo desde cero. Lo físico está paso a paso en `docs/PROCEDIMIENTO_REPLICABLE.md` (12 secciones, de preparar la Jetson a "lo que falló"); no se copia aquí.
Esta nota resume **cómo se midió** y deja los comandos de la simulación.

## 1. Idea del método

1. **Líneas base antes de la IA.** Cada política se compara con acciones fijas ("solo reglas": quedarse quieto; azar; reglas de posicionamiento; ruta de Brahian) con las
   mismas partidas y las mismas semillas. Si la política no las supera, no aporta (D-052). Fuente: `docs/PLAN_V17_REFUERZO.md` §2.
2. **Métrica principal (M1, D-059):** porcentaje de partidas de 5 min con una racha de 30 s seguidos con el ladrón a la vista y el ID correcto. Secundarias: re-adquisición en ≤ 10 s y rendición. Seguridad: alcanzado, choques, geocerca y gimbal (`docs/DECISIONES.md`).
3. **Tamaño de muestra:** 512 partidas por fila, semilla 123; el margen de error de M1 es de unos ±3 a ±4 puntos (`03_SIMULACION_RL/informes/diagnostico_v17_ia_aporta.md`, `docs/PROGRESO_V17.md`).
4. **Reglas duras como pruebas** que no se relajan: gimbal/tilt dentro de sus topes, geocerca, búsqueda determinista (salvo la prueba reversible D-069/D-070), humano en el lazo, árbitro. 143 pruebas pasaron (`docs/PROGRESO_V17.md`; el resultado con el despeje de paneles **está pendiente de leer**).
5. **Se mide en lugar de suponer:** campo de visión de la cámara, ángulos del LiDAR y del montaje se midieron con la interfaz `/calibrar` (D-078); las cifras nominales se descartaron.

## 2. Comandos de la simulación (Windows, desde `03_SIMULACION_RL\`)

```
.venv\Scripts\python.exe -m unittest discover -s tests
.venv\Scripts\python.exe herramientas\medir_ia_aporta.py mision --pol b0,b3 --n 512 --salida informes\v17\x.json
.venv\Scripts\python.exe herramientas\evaluar_politica.py --modelo modelos_v15\ultimo.zip --version v15
.venv\Scripts\python.exe -m minimo_tesis.protocolo_comite --sin-degradadas
```

Las líneas base (B0 a B5), los resultados y sus archivos están en `03_SIMULACION_RL/informes/` y en `docs/PROGRESO_V17.md`; la sección redactada del plus, en
`docs/SECCION_PLUS_DOCUMENTO.md`.

## 3. Cómo se midieron los ángulos del dron (20-oct)

Dron sobre el escritorio, pared lisa a 2.0 m, marcas en la pared, el dedo y líneas verticales; la interfaz `/calibrar` con lupa para los clics y la cuenta comprobada con casos
inventados de respuesta conocida. Resultado: campo de visión de la CSI 68.3° × 54.0°, cámara a −2.4°, rayo del TF03 a −6.7°, giro de la cámara +1.5° (una línea, por confirmar).
Fuentes: `08_EVIDENCIA_Y_DIAGRAMAS/calibracion_angulos_2026-10-20/`, `docs/DECISIONES.md` (D-078).

## 4. Qué no se verificó

El mínimo no ha volado con la Jetson; el plus no se ha construido ni volado; la CSI#2 no se midió; los paneles reales no se han medido con cinta (alto, ancho y color);
el alcance del TF-Luna según el color del panel viene de la hoja de datos con interpolación propia. Ver `docs/ESTADO_FISICO_20OCT.md` y `docs/HISTORIAL_PRUEBAS_FISICAS.md`.
