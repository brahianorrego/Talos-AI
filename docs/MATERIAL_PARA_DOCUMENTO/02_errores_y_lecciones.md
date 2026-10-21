# 02 · Errores y lecciones

Brahian pidió que se cuenten. Cada fila: qué falló, causa, arreglo y archivo. Lo que no tiene fuente en el repositorio se marca **[sin fuente]**.

## Parte física (de `docs/HISTORIAL_PRUEBAS_FISICAS.md` y `docs/PROCEDIMIENTO_REPLICABLE.md`)

| Fallo | Causa | Arreglo |
|---|---|---|
| LiPo 4S sobredescargada (7-oct) | Se dejó descargar; la batería original quedó dañada | Se retiró y no se vuela con ella (`docs/BITACORA.md`, 7 de octubre) |
| El único vuelo del dron (sin la Jetson) terminó en failsafe por batería | Batería baja | El mínimo **no ha volado con la Jetson** (`docs/HISTORIAL_PRUEBAS_FISICAS.md`, "Pendiente") |
| Gimbal solo bajaba a −10° | Hipótesis: el cable grueso del TF03 hacía palanca | Se descartó el gimbal (D-072, D-073) |
| Reinstalar la Jetson tomó más de un día | La imagen en microSD buscaba su disco raíz en otra ranura; Secure Boot rechazó el arranque; BitLocker pidió clave; una USB de 4 GB corrompía archivos | Se instaló en el NVMe con JetPack 6.2.1 (`08_EVIDENCIA_Y_DIAGRAMAS/reinstalacion_jetson/`) |
| LiDAR TF03 sin driver | El kernel de JetPack 6 no trae `pl2303` | Se compiló el driver con las fuentes del kernel 5.15.148 (`docs/HISTORIAL_PRUEBAS_FISICAS.md` cita el script `jp6_driver_pl2303.sh`, que **no está en este repositorio**: pedirlo a la parte física) |
| Cámara USB casi blanca al aire libre | Su driver no controla la exposición; a pleno sol 95 % de píxeles quemados (la CSI, 0 %) | Se cambió a la CSI IMX219; después se quitó la USB (el sensor se dañó con el sol) |
| Video lento por WiFi | JPEG de calidad 92 (~70 KB por cuadro) | Calidad 55 (~15-25 KB), buffer limitado y codificación en otro hilo |
| En las tomas de campo el LiDAR leía la pared a 58 m | No estaba alineado con la cámara | Se midieron los ángulos y se re-simuló el mínimo |
| Pixhawk marcaba roll 180° | Montada boca abajo | `AHRS_ORIENTATION = 8` |
| Motores espejados y con giro invertido | Respecto a un X normal | `FRAME_TYPE = 18`; se probó sin hélices |
| Medidas falsas de la cámara | Se usaba el campo nominal de 62.2° × 48.8° | Medido: 68.3° × 54.0°, cámara a −2.4° y rayo del LiDAR a −6.7° (D-078) |

## Simulación y entrenamiento (de `03_SIMULACION_RL/informes/` y `docs/PROGRESO_V17.md`)

| Fallo | Causa | Arreglo |
|---|---|---|
| La política de la V15 no aportaba nada, tras 222 M pasos | 9 de 10 acciones hacían lo mismo; el entrenamiento aprendía también de pasos sin decisión | Siete acciones con efecto y máscara de acciones (`informes/diagnostico_v17_ia_aporta.md`) |
| La V17.1 y la V17.3 colapsaron a "quedarse" | La multa de suavidad era demasiado fuerte al empezar (−170 por partida con acciones al azar) | Se bajó a la décima parte; la V17.2 no colapsó |
| Criterio de 60 s seguidos imposible | Casi nadie lo logra en esta cancha (1 %) | Se pasó a 30 s (D-059) |
| La regla "sigue igual" del operador dejaba que el seguimiento saltara al civil | Error de la V16 en una regla dura (humano en el lazo) | Se arregló el código, no la prueba |
| A 2.0 m el dron chocaba con los paneles (10-16 % al principio; 1.6-2.3 % en las mediciones de H) | Volaba más bajo que los paneles de 2.30 m | Despeje de paneles; choques en 0 % en las mediciones con despeje |
| Un error de comparación: archivos `d_r3_b0` y `d_r5_b0` eran en realidad B5' | Se mezclaron condiciones distintas al comparar con B0 | Se corrigió el mensaje; tabla justa pendiente (`docs/PROGRESO_V17.md`) |
| Se implementó 3.30 m fijo cuando la orden de Brahian era base 2.0 m | La orden se había implementado de otra forma | Se corrigió (D-080) |
| Documentos duplicados y carpetas confusas | Muchas sesiones escribiendo | Brahian pidió menos documentos: el trabajo va en código y datos |
| Caída de Unreal (20-oct): `assert VertexFactory` al abrir la simulación en vivo | La reportó Brahian; la fuente es el aviso del Coordinador, **no hay informe en el repositorio** | Arreglo en curso por el Visor (aún sin confirmar) |
| La altura del mínimo estaba sin decidir (3.30 m de D-043 contra 2.0 m de las mediciones) | La altura segura se pensó para el plus, con saltos de personas; el mínimo se calibró a 2.0 m | D-081: altura del mínimo = 2.0 m (a 2.0 m el TF03 a −6.7° alcanza a una persona de 1.70-1.72 m solo a más de ≈ 2.5 m). El plus se rige por D-080 |

## Lecciones

1. Medir antes de decir "la IA lo hace bien": las líneas base (quedarse quieto, azar, reglas) mostraron que la V15 no aportaba.
2. Si una acción no cambia el resultado, la red no puede aprender de ella.
3. Las cifras nominales (la cámara de 62.2°) no valen: se miden.
4. Comparar solo condiciones iguales y comprobar de qué política es cada archivo antes de concluir.
5. Lo que no se verificó se escribe como no verificado.
