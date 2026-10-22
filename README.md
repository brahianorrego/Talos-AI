<div align="center">

<img src="08_EVIDENCIA_Y_DIAGRAMAS/portada/banner.png" width="100%" alt="Dron IA Vigilancia: detecta personas, evita obstáculos y decide con una red neuronal cuándo frenar y subir">

<br>

![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.14-EE4C2C?logo=pytorch&logoColor=white)
![Stable-Baselines3](https://img.shields.io/badge/Stable--Baselines3-PPO-0A7BBB)
![ArduPilot](https://img.shields.io/badge/ArduPilot-4.7-6CA43A)
![NVIDIA Jetson](https://img.shields.io/badge/NVIDIA-Jetson%20Orin%20Nano-76B900?logo=nvidia&logoColor=white)
![YOLO](https://img.shields.io/badge/YOLO26n-TensorRT%20FP16-00FFFF)
![Pruebas](https://img.shields.io/badge/pruebas-88%20pasan-brightgreen)
![Estado](https://img.shields.io/badge/estado-pruebas%20de%20campo-orange)
![Ayuda](https://img.shields.io/badge/se%20buscan-colaboradores-ff69b4)

**[El dron](#el-dron)** · **[Arquitectura](#arquitectura-percepción--decisión--control)** · **[Resultados](#resultados-en-simulación)** · **[IA de refuerzo](#-plus-ia-de-refuerzo-para-mantener-a-la-vista-a-un-sospechoso)** · **[Reprodúcelo](#cómo-reproducirlo)** · **[¿Quieres ayudar?](#-quieres-ayudar)**

</div>

> **En una frase:** el piloto vuela; una Jetson a bordo mira con una cámara y un LiDAR, y una red neuronal decide en
> milisegundos si hay que **frenar y subir a 3.30 m** para no chocar con una persona o un obstáculo. Las reglas de
> seguridad y el piloto siempre tienen la última palabra.
>
> El dron se llama **TALOS-AI** (la estación de tierra lleva ese nombre); el repositorio conserva el nombre `Dron-IA-Vigilancia`.

<div align="center">

| 🎯 **100 %** | 🚫 **0** | 🧠 **−17 %** | ⚡ **9-11 ms** |
|:---:|:---:|:---:|:---:|
| éxito en 1300 vuelos del protocolo del comité | activaciones falsas en 300 vuelos donde no debía actuar | choques de la IA frente a las reglas (117 → 97 en 3 840 vuelos de prueba) | por cuadro de YOLO en la Jetson |

<sub>Simulación con ruido de sensores y 100 ms de retardo · fuentes en <code>03_SIMULACION_RL/informes/</code></sub>

</div>

---

## Qué problema resuelve

Volar cerca de personas al aire libre exige que el dron **vea**, **decida** y **actúe a tiempo**. Muchos trabajos
detectan personas en un video, pero esa detección no llega a convertirse en una orden que la aeronave cumpla con un
retardo aceptable. Aquí sí: la Jetson detecta, decide y le ordena a la Pixhawk por MAVLink, y el piloto conserva
siempre la última palabra.

El proyecto tiene dos partes, claramente separadas:

| | 🟢 Mínimo indispensable | 🔵 Plus (trabajo complementario) |
|---|---|---|
| **Qué hace** | El piloto avanza en línea recta; el sistema solo **frena y sube a 3.30 m** ante un riesgo definido (persona u obstáculo) | El dron busca, sigue y **mantiene a la vista a un sospechoso** que huye y se esconde detrás de muros |
| **IA** | YOLO26n (preentrenada) + decisor MLP 15-32-16-1 | Política PPO 192-128-128-10 + reglas deterministas |
| **Lo pide** | El comité (objetivo del proyecto de grado) | Caso de uso policial, en simulación |
| **Estado** | Simulación terminada y congelada · pruebas físicas en curso | V15 entrenada 229 M pasos · V16 programada · V17 en plan |
| **Carpeta** | [`01_MINIMO_INDISPENSABLE/`](01_MINIMO_INDISPENSABLE/) | [`03_SIMULACION_RL/`](03_SIMULACION_RL/) |

**Objetivo general:** implementar un sistema experimental de detección de personas y evasión de obstáculos para un
cuadricóptero mediante inteligencia artificial preentrenada y sensores de proximidad en entornos exteriores
controlados.

## El dron

<table>
<tr>
<td><img src="08_EVIDENCIA_Y_DIAGRAMAS/fotos/08_dron_completo_frente.webp" width="260" alt="Dron de frente con el gimbal y la cámara abajo"></td>
<td><img src="08_EVIDENCIA_Y_DIAGRAMAS/fotos/10_dron_completo_lado.webp" width="260" alt="Dron de lado, se ve la placa del gimbal y la caja de la Jetson"></td>
<td><img src="08_EVIDENCIA_Y_DIAGRAMAS/fotos/13_peso_montaje_en_bascula.webp" width="300" alt="Gimbal con cámara y LiDAR apoyado en una tabla sobre la báscula"></td>
</tr>
<tr><td align="center">De frente</td><td align="center">De lado</td><td align="center">Pesaje del montaje</td></tr>
</table>

| Función | Componente | Detalle |
|---|---|---|
| Controladora de vuelo | Pixhawk 2.4.8 (fmuv3) · ArduPilot 4.7.0 | Quad X; modos por CH5, parada de emergencia CH8 |
| Computadora de a bordo | NVIDIA Jetson Orin Nano | JetPack 7, Python 3.12, TensorRT |
| Cámara | USB 640×480 | HFOV medido 38.9° |
| Detección de personas | YOLO26n · TensorRT FP16 | 9-11 ms por cuadro |
| Distancia frontal | LiDAR Benewake TF03 | 0.1-30 m, 100 Hz |
| Estabilizador | BaseCam SimpleBGC 2 ejes | Pitch por AUX1: `pwm = 1500 + θ·500/45` |
| Propulsión | 4 motores 2212/920 KV · variadores 40 A | Hélices 10" |
| Energía | LiPo 4S 6200 mAh · Power Module · buck 12 V para la Jetson | |
| Enlace Jetson ↔ Pixhawk | TELEM2 a 115200 baudios, MAVLink 2 | Sin 5 V (el USB retroalimentaba) |

Fuente: [`05_HARDWARE_Y_VARIANTES/hardware.md`](05_HARDWARE_Y_VARIANTES/hardware.md). Peso total en vuelo (con batería, Jetson, gimbal y LiDAR), medido en báscula: **2 371 g**
([foto](08_EVIDENCIA_Y_DIAGRAMAS/fotos/12_peso_bascula.webp)).

<img src="08_EVIDENCIA_Y_DIAGRAMAS/diagramas/09_conexiones.png" width="640" alt="Diagrama de conexiones eléctricas y de datos">

### Montaje por etapas

<table>
<tr>
<td><img src="08_EVIDENCIA_Y_DIAGRAMAS/fotos/01_armazon_en_el_laboratorio.webp" width="190" alt="Armazón de fibra de carbono con motores, sin electrónica"></td>
<td><img src="08_EVIDENCIA_Y_DIAGRAMAS/fotos/04_motor_2212_920kv.webp" width="190" alt="Motor 2212/920 KV en su bolsa"></td>
<td><img src="08_EVIDENCIA_Y_DIAGRAMAS/fotos/06_placa_de_distribucion.webp" width="190" alt="Placa de distribución de potencia soldada"></td>
<td><img src="08_EVIDENCIA_Y_DIAGRAMAS/fotos/05_power_module.webp" width="190" alt="Power Module con conectores XT60"></td>
</tr>
<tr><td align="center">1. Armazón</td><td align="center">2. Motores</td><td align="center">3. Distribución</td><td align="center">4. Power Module</td></tr>
<tr>
<td><img src="08_EVIDENCIA_Y_DIAGRAMAS/fotos/02_pixhawk_2.4.8.webp" width="190" alt="Controladora Pixhawk 2.4.8 en su caja"></td>
<td><img src="08_EVIDENCIA_Y_DIAGRAMAS/fotos/03_buzzer_y_switch_de_seguridad.webp" width="190" alt="Buzzer y switch de seguridad de la Pixhawk"></td>
<td><img src="08_EVIDENCIA_Y_DIAGRAMAS/fotos/11_gps_sobre_el_chasis.webp" width="190" alt="GPS montado sobre el chasis"></td>
<td><img src="08_EVIDENCIA_Y_DIAGRAMAS/fotos/07_gimbal_basecam_placa.webp" width="190" alt="Placa BaseCam del gimbal encendida"></td>
</tr>
<tr><td align="center">5. Pixhawk</td><td align="center">6. Buzzer y switch</td><td align="center">7. GPS</td><td align="center">8. Gimbal BaseCam</td></tr>
</table>

## Arquitectura: Percepción → Decisión → Control

```mermaid
flowchart LR
    subgraph P[Percepción · Jetson]
        CAM[Cámara USB 38.9°] --> YOLO[YOLO26n TensorRT<br/>9-11 ms/cuadro]
        LID[LiDAR TF03]
        PX[Pixhawk: velocidad, altura, modo]
    end
    subgraph D[Decisión · Jetson]
        YOLO --> DEC[Decisor MLP 15-32-16-1<br/>CONTINUAR / DETENER_Y_ASCENDER]
        LID --> DEC
        PX --> DEC
        DEC --> ENV[Envolvente de reglas duras<br/>LiDAR menor a 3 m, árbitro, CH8]
    end
    subgraph C[Control · Pixhawk]
        ENV -->|MAVLink GUIDED| AP[ArduPilot PID<br/>freno + subida a 3.30 m]
        OP[Piloto / operador] -->|CH5 retoma, CH8 corta| AP
    end
```

La IA **nunca toca los motores**: le pide a ArduPilot una consigna, y la estabilidad la dan sus PID. El piloto retoma
con el interruptor de modo (CH5) y corta motores con CH8.

<table>
<tr>
<td><img src="08_EVIDENCIA_Y_DIAGRAMAS/diagramas/01_arquitectura.png" width="400" alt="Diagrama de arquitectura del sistema"></td>
<td><img src="08_EVIDENCIA_Y_DIAGRAMAS/diagramas/02_estados.png" width="400" alt="Máquina de estados del sistema mínimo"></td>
</tr>
</table>

Explicación completa, con un diagrama por bloque: [`COMO_FUNCIONA_EL_CODIGO.md`](COMO_FUNCIONA_EL_CODIGO.md).

## 🟢 Mínimo indispensable

### Cómo opera

1. El piloto despega, sube a ~2.3 m y activa el **modo experimental** (CH7).
2. Avanza en línea recta (LOITER, ≤ 4 m/s) o deja el dron quieto (**modo estático**).
3. En cada cuadro, YOLO busca personas, el TF03 mide al frente y el **decisor MLP** calcula la probabilidad de que en
   los próximos 3 s haya un choque o una persona a menos de 2 m.
4. Si la probabilidad pasa de 0.7 durante 2 cuadros seguidos: **DETENCIÓN + ASCENSO VERTICAL** a 3.30 m (fuera del
   alcance de una persona saltando).
5. Las reglas duras mandan sobre la IA: el LiDAR a menos de 3 m frena siempre y el árbitro autoriza el ascenso.
6. Si alguien pasa de lado o lejos, no hace nada (también se mide: activaciones falsas).

### Por qué una IA y no solo reglas

Las medidas reales son ruidosas: la distancia por la caja de YOLO se equivoca de cerca, YOLO pierde cuadros y una
persona que cruza se parece a una que viene. Con umbrales fijos hay que adivinar números a mano; la red aprende la
frontera de decisión con ejemplos **etiquetados automáticamente en simulación** (nadie etiqueta a mano).

<img src="08_EVIDENCIA_Y_DIAGRAMAS/diagramas/04_porque_ia.png" width="560" alt="Diagrama de por qué usar IA para decidir">

### Resultados en simulación

**Protocolo del comité** ([`informes/minimo_tesis_protocolo.md`](03_SIMULACION_RL/informes/minimo_tesis_protocolo.md);
100 vuelos por variante, sensores con ruido y 100 ms de retardo, intervalos de confianza del 95 %):

| Escenario | ¿Debe activarse? | Éxito con el sistema | Vuelo seguro sin el sistema |
|---|:---:|---:|---:|
| a) Panel fijo, avance a 1, 2, 3 y 4 m/s | sí | 100 % [96, 100] en las 4 | 0 % |
| b) Persona quieta, avance a 1.5 y 3.0 m/s | sí | 100 % [96, 100] | 0 % |
| c) Persona de frente que camina o corre | sí | 100 % [96, 100] | 0 % |
| d) Persona que cruza lejos | no | 100 % [96, 100] | 100 % |
| e) Modo estático: persona que viene / que pasa a 5 m | sí / no | 100 % [96, 100] | 0 % / 100 % |

En total: **1300 vuelos, éxito 100 % [99.7, 100] y 0 activaciones falsas en 300**; con el operador solo, 23 % de
vuelos seguros.

**Reglas frente a IA** en 3 840 vuelos de mundos de prueba nunca vistos
([`informes/minimo_tesis_decisor_ia.md`](03_SIMULACION_RL/informes/minimo_tesis_decisor_ia.md)):

| Decisor | Choques | Persona a < 2 m bajo 3.30 m (vuelos) | Activaciones innecesarias |
|---|---:|---:|---:|
| Sin sistema | 1681 | 1488 | — |
| Reglas | 117 | 516 | 161 |
| **IA + envolvente** (la que va al dron) | **97** | **212** | **109** |

Clasificador en el conjunto de prueba: AUC-ROC 0.961, precisión 97.1 %, falsos positivos 0.3 % por cuadro.
Con el piloto a 4 m/s o menos la IA queda igual que las reglas en seguridad (11 riesgos contra 10); su ventaja clara es que frena menos veces sin necesidad.
Estas cifras usan la geometría medida el 20-oct (cámara 68.3° × 54.0°, sin gimbal). El 21-oct se vio que los ángulos del montaje estaban medidos
respecto al horizonte y no al chasis (LiDAR ≈ −9.0° y cámara ≈ −5.6° respecto al chasis, [D-082](docs/DECISIONES.md)): **se re-simula tras recalibrar el 22-oct**.

<img src="03_SIMULACION_RL/informes/minimo_tesis_decisor_curvas.png" width="640" alt="Curvas ROC y precisión-exhaustividad del decisor">

### Las redes, por dentro

`ver_redes.py` imprime capas y parámetros y dibuja cada red
([`06_REDES_NEURONALES_Y_MODELOS/`](06_REDES_NEURONALES_Y_MODELOS/)):

<table>
<tr>
<td><img src="08_EVIDENCIA_Y_DIAGRAMAS/redes/decisor_minimo_red.png" width="400" alt="Diagrama del decisor MLP 15-32-16-1"></td>
<td><img src="08_EVIDENCIA_Y_DIAGRAMAS/redes/decisor_minimo_pesos.png" width="400" alt="Histogramas de pesos del decisor"></td>
</tr>
<tr><td align="center">Decisor del mínimo: 1 057 parámetros</td><td align="center">Distribución de sus pesos</td></tr>
</table>

### Paso a paso en el dron real

| Paso | Qué | Estado |
|---|---|---|
| 0 | Inventario del código de la Jetson | ✅ |
| 1 | Percepción + registro en banco (`registro_minimo.py`) | ✅ |
| 2 | Gimbal con pitch fijo por AUX1 (−5°, 1444 µs) | ✅ |
| 3 | Intervención por MAVLink en banco, sin hélices (`intervencion_banco.py`) | ✅ 18 oct (17 intervenciones, 0 fallidas, latencia media 38 ms) |
| 4 | Datos reales con el dron sobre un carro, escenarios E0-E6 | En curso: 21-oct E1 ×5, E2 ×6, E3 ×5, E4 caminando ×7; faltan E0, E4 trotando, E5, E6 |
| 5 | Decisor en "modo sombra" (decide y registra, no manda) | Pendiente |
| 6 | Vuelos: panel de cartón → maniquí → persona | Pendiente |
| 7 | Protocolo del comité en campo (10 repeticiones por escenario) | Pendiente |

### Campo del 21-oct: primeras tomas reales (dron sin hélices, quieto, sobre un carro)

Informe completo y procedimiento: [`docs/INFORME_CAMPO_21OCT.md`](docs/INFORME_CAMPO_21OCT.md) · [`docs/PROCEDIMIENTO_REPLICABLE.md`](docs/PROCEDIMIENTO_REPLICABLE.md) · [`docs/HISTORIAL_PRUEBAS_FISICAS.md`](docs/HISTORIAL_PRUEBAS_FISICAS.md).

| Marca (m) | Persona detectada por YOLO | LiDAR contra la cinta |
|---:|---:|---:|
| 15 | 82 % | +0.02 m |
| 12 | 94 % | +0.02 m |
| 8 | 99 % | +0.07 m |
| 4 | 100 % | +0.05 m |
| 2 | 99 % | +0.16 m |

El rayo del LiDAR cae dentro de la persona que ve YOLO el 75-100 % de los cuadros (persona quieta) y ~80 % al caminar o trotar hacia el dron.
Hallazgo: el rayo apuntaba unos −9° respecto al chasis (no −6.7°): con el dron plano tocaba el suelo a ~12 m. Dron y estación se manejan con
la [estación de tierra TALOS-AI](04_VISOR_Y_MOTOR_GRAFICO/) (video 1280×960, LiDAR sobre la imagen, inclinación del dron, mapa GPS y control de tomas).

Plan completo: [`01_MINIMO_INDISPENSABLE/PLAN_MINIMO_FISICO.md`](01_MINIMO_INDISPENSABLE/PLAN_MINIMO_FISICO.md).

<img src="08_EVIDENCIA_Y_DIAGRAMAS/diagramas/03_experimento.png" width="560" alt="Diagrama del diseño experimental">

## 🔵 Plus: IA de refuerzo para mantener a la vista a un sospechoso

Un juego de **dron contra ladrón** en simulación (inspirado en el escondite de OpenAI, Baker et al. 2020). El ladrón
huye, se esconde detrás de muros, se cansa y ataca; el dron debe seguirlo sin perderlo hasta que se rinda. El operador
humano es quien dice cuál persona es el sospechoso.

- **Mundo** ([`entorno.py`](03_SIMULACION_RL/entorno.py)): NumPy vectorizado (512 partidas en paralelo), arena de 25 m,
  muros, civiles, cámara + YOLO estadístico, LiDAR de 10 rayos, Kalman y filtro de partículas, mapa LiDAR propio.
- **Control** ([`control.py`](03_SIMULACION_RL/control.py)): modelo de la cascada de ArduPilot y del gimbal real.
- **Red**: PPO de Stable-Baselines3, 192 entradas → 128 → 128 → 10 acciones; solo decide con el objetivo fijado.
- **Reglas alrededor**: búsqueda determinista tras perderlo, reflejo de punto ciego, árbitro y geocerca.
- **Currículo de 5 niveles**: duelo abierto → con civil → muro → muro y civil → misión completa.

<div align="center">
<img src="08_EVIDENCIA_Y_DIAGRAMAS/capturas/visor_plus_mision_completa.png" width="100%" alt="Visor 3D de la simulación: el dron verifica a una persona marcada como posible objetivo; a la derecha la cámara del dron con la detección y abajo el mapa LiDAR">
<sub>Visor 3D de la estación de tierra (three.js): el dron encontró a una persona y espera que el operador la confirme. A la derecha, lo que ve su cámara; abajo, el mapa del LiDAR.</sub>
</div>

### Dos configuraciones del dron: mínimo y plus

| | **Mínimo (variante G, el dron de hoy)** | **Plus (variante H)** |
|---|---|---|
| Cámara | CSI IMX219 fija, ~5° hacia abajo | CSI IMX219 en un **pan-tilt impreso de dos servos** (yaw y pitch, sin roll: el roll lo controla el dron) |
| LiDAR | TF03 fijo, paralelo a la cámara | TF03 fijo al chasis **+ TF-Luna junto a la cámara, en el pan-tilt** |
| Cámara al piso | no | segunda CSI fija mirando al piso |
| Gimbal | ninguno | ninguno: el tilt de los servos tiene topes mecánicos de −45° a +15° |

Las dos son configuraciones distintas: el mínimo es lo que el comité aprobó y ya está montado; el plus se entrena en la H y todavía no se ha construido
([`docs/DECISIONES.md`](docs/DECISIONES.md), D-074; estado físico en [`docs/ESTADO_FISICO_20OCT.md`](docs/ESTADO_FISICO_20OCT.md)).

### V17: la misión real en la cancha de la universidad

Desde la V17 el plus se mide en el escenario que se va a montar: una cancha de fútbol, una zona de 30 × 30 m con dos conjuntos
de dos paneles en V de 90° (cada panel de ~1.5 × 2.2-2.3 m, por confirmar con cinta), un ladrón y un civil. Plan:
[`docs/PLAN_V17_REFUERZO.md`](docs/PLAN_V17_REFUERZO.md) · dibujo: [`docs/v17_zona_ia.png`](docs/v17_zona_ia.png).

<div align="center">
<img src="08_EVIDENCIA_Y_DIAGRAMAS/capturas/unreal_partida_3000.jpg" width="49%" alt="Partida de la simulación dibujada en Unreal Engine 5: el dron sobre la cancha con las dos V de paneles">
<img src="08_EVIDENCIA_Y_DIAGRAMAS/capturas/unreal_maniquies_ladron_corriendo.jpg" width="49%" alt="El ladrón (maniquí) corre junto a una V de paneles mientras el dron lo sigue">
<br><sub>Mundo realista en Unreal Engine 5 (solo dibuja lo que dice la simulación). Los personajes son maniquíes, no personas reales.</sub>
</div>

<div align="center">
<img src="08_EVIDENCIA_Y_DIAGRAMAS/capturas/estacion_modo_dron.jpg" width="49%" alt="Estación de tierra, modo dron: lo que ve la cámara con la caja de YOLO y las órdenes de la Jetson">
<img src="08_EVIDENCIA_Y_DIAGRAMAS/capturas/estacion_modo_3d.jpg" width="49%" alt="Estación de tierra, modo 3D: el dron y el ladrón en el mundo simulado">
<br><sub>Estación de tierra web: el operador confirma al sospechoso con un botón (humano en el lazo).</sub>
</div>

<div align="center">
<img src="08_EVIDENCIA_Y_DIAGRAMAS/capturas/dron_real_lado.jpg" width="40%" alt="Modelo 3D del dron real, de lado: Jetson, gimbal, LiDAR y cámara">
<br><sub>Modelo 3D del dron real, usado en la estación y en Unreal.</sub>
</div>

**Con honestidad, resultados medidos (512 partidas por fila; margen de error de M1 ≈ ±4 puntos; informes en [`03_SIMULACION_RL/informes/`](03_SIMULACION_RL/informes/)):**

- **La V15 no aportaba nada:** su política rendía igual que "quedarse quieto" y que el azar (custodia de 60 s: 11.3 %, 10.2 % y
  7.8 %). Con el ladrón a la vista, 9 de sus 10 acciones hacían lo mismo ([diagnóstico](03_SIMULACION_RL/informes/diagnostico_v17_ia_aporta.md)).
- **La V17 lo corrige** (7 acciones con efecto, máscara de acciones, recompensa por racha de 30 s seguidos a la vista). A 50 M pasos
  en la cancha de prueba, la política da 54.3 % frente a 48.4 % de "solo reglas" y 56.2 % de "siempre subir": **supera a las reglas
  solas y empata con la mejor regla simple.**
- **Cancha real:** el escenario es mucho más difícil. M1: solo reglas 11.7 %, azar 13.5 %, posicionamiento 17.2 %, siempre subir
  24.6 %, la V17.2 sin afinar 19.3 %. Afinado y ruta de búsqueda de Brahian: ver [`docs/PROGRESO_V17.md`](docs/PROGRESO_V17.md) y
  [`docs/RUTA_BUSQUEDA_BRAHIAN.md`](docs/RUTA_BUSQUEDA_BRAHIAN.md).
- **Todo es simulación**; el plus no ha volado.

**Ruta de búsqueda enseñada** (consejos de Brahian, no reglas duras): 360° de entrada, ir detrás de cada V a 3.30 m, recorrer la
parte de atrás en cuadrado, mirar de frente con vaivén, pasar a la otra V, nunca quedarse quieto y que funcione también sin subir.

## Historial de versiones

| Versión | Fecha (2026) | Qué cambió |
|---|---|---|
| V1-V5 | 7 oct | Del "dron esquiva" al "dron mantiene al ladrón a la vista" con operador humano |
| V6-V9 | 8 oct | Mapa LiDAR, búsqueda tras los paneles, ladrón con saltos, gimbal con límite duro, 192 entradas |
| V10 | 8-10 oct | Stable-Baselines3 con transferencia desde la V9; 769.8 M pasos (etiqueta `v10-master-759M`) |
| V11-V12 | 10 oct | Gimbal estricto −45°..+15°, búsqueda determinista con memoria espacial, control jerárquico |
| V13-V14 | 10 oct | Currículo progresivo, interrupción táctica, oclusión entre personas |
| V15 | 10-12 oct | 5 niveles, rendición, Kalman + partículas, reconfirmación con el operador; 229.4 M pasos |
| Mínimo | 10-11 oct | Simulación del comité y decisor MLP (congelado) |
| V16 | 12 oct | Misión de 2 paneles, posturas humanas, visor realista (programada, sin entrenar) |
| V17 | 16-19 oct | Diagnóstico medido de la V15, 7 acciones con efecto, cancha real con dos V, líneas base B0-B4, estación de tierra y mundo en Unreal |

Detalle: [`docs/BITACORA.md`](docs/BITACORA.md) y [`docs/DECISIONES.md`](docs/DECISIONES.md).

## 🙌 ¿Quieres ayudar?

Este proyecto está abierto. Si sabes de drones, visión por computador, aprendizaje por refuerzo, three.js o diseño 3D,
hay trabajo interesante y concreto:

| | Reto | Por qué importa |
|---|---|---|
| 🧠 | **Hacer que la red PPO aprenda de verdad** (hoy decide casi al azar) | Es la diferencia entre "reglas con una red al lado" y una IA que aporta |
| 🛩️ | **Llevar el decisor a la Jetson en modo sombra** | Primer paso para validar la IA con datos reales |
| 🎮 | **Visor más realista**: personas animadas, cámara del dron fiel | Lo que ve el operador en vuelo, en virtual |
| 🔩 | **Soportes 3D**: pan-tilt de servos, TF-Luna en el gimbal | Libera el pitch del gimbal (hoy trabado en −10° por un cable) |
| 🌎 | **README en inglés** | Que lo entienda más gente |

Lee la guía [`CONTRIBUTING.md`](CONTRIBUTING.md), abre un *issue* con tu idea y ¡a volar! ⭐ Si te gusta, dale una
estrella: ayuda a que más gente lo encuentre.

### Hoja de ruta

- [x] Hardware integrado y probado en banco (Pixhawk, Jetson, LiDAR, gimbal, cámara)
- [x] Simulación del mínimo y decisor MLP (congelados)
- [x] IA de refuerzo V15 entrenada (229 M pasos)
- [ ] Paso 3: intervención por MAVLink en banco (sábado 17 oct)
- [ ] Paso 4: datos reales en campo (escenarios E0-E6)
- [ ] Pasos 5-7: modo sombra, vuelos y protocolo del comité en campo
- [ ] V17: diagnóstico del PPO y misión con paneles reales
- [ ] Visor realista y variantes de hardware

## Cómo reproducirlo

Windows, Python 3.14:

```
cd 03_SIMULACION_RL
py -m venv .venv
.venv\Scripts\python.exe -m pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu
.venv\Scripts\python.exe -m pip install numpy==2.5.3 gymnasium==1.4.0 stable_baselines3==2.9.0 scikit-learn==1.9.1 matplotlib==3.11.2 scipy==1.18.1

.venv\Scripts\python.exe -m unittest discover -s tests                     (88 pruebas, ~2.5 min)
.venv\Scripts\python.exe -m minimo_tesis.protocolo_comite --sin-degradadas  (protocolo del comité, 5 s)
ABRIR_VISOR.bat                                                             (visor 3D en http://127.0.0.1:8765/)
```

Los modelos entrenados (`.zip`) no están en el repositorio por su tamaño; se publican aparte.
Guion de demostración de 10 minutos: [`DEMOSTRACION_PARA_EL_INGENIERO.md`](DEMOSTRACION_PARA_EL_INGENIERO.md).

## Reglas duras (no negociables)

1. Gimbal entre −45° y +15°, pase lo que pase.
2. Geocerca: el dron no sale de la zona.
3. Búsqueda determinista al perder al objetivo.
4. Humano en el lazo: el operador confirma al sospechoso; la IA nunca lo elige.
5. Árbitro de seguridad: el LiDAR < 3 m y la parada CH8 mandan sobre la IA.
6. La red no estabiliza nada: eso lo hacen los PID de ArduPilot y del gimbal.

Todas tienen pruebas automáticas en [`03_SIMULACION_RL/tests/test_reglas_duras.py`](03_SIMULACION_RL/tests/test_reglas_duras.py).

## Organización del repositorio

| Carpeta | Contenido |
|---|---|
| [`01_MINIMO_INDISPENSABLE/`](01_MINIMO_INDISPENSABLE/) | Mínimo congelado, con huellas SHA-256 |
| [`02_JETSON_A_BORDO/`](02_JETSON_A_BORDO/) | Código que corre en la Jetson (época del gimbal) y, en [`minimo_sin_gimbal/`](02_JETSON_A_BORDO/minimo_sin_gimbal/), el del mínimo actual: panel de campo, `/calibrar`, registro con tomas |
| [`03_SIMULACION_RL/`](03_SIMULACION_RL/) | Simulación, entrenamiento, visor, pruebas e informes |
| [`04_VISOR_Y_MOTOR_GRAFICO/`](04_VISOR_Y_MOTOR_GRAFICO/) | Estación de tierra TALOS-AI (mínimo y plus), plan del visor y del motor gráfico |
| [`05_HARDWARE_Y_VARIANTES/`](05_HARDWARE_Y_VARIANTES/) | Hardware, Pixhawk y Jetson |
| [`06_REDES_NEURONALES_Y_MODELOS/`](06_REDES_NEURONALES_Y_MODELOS/) | `ver_redes.py` e índice de modelos |
| [`08_EVIDENCIA_Y_DIAGRAMAS/`](08_EVIDENCIA_Y_DIAGRAMAS/) | Fotos, diagramas y gráficas |
| [`docs/`](docs/) | Estado, bitácora, decisiones y planes |
| [`_archivo_versiones/`](_archivo_versiones/) | Versiones anteriores del código |

Qué es cada archivo: [`GUIA_DE_ARCHIVOS.md`](GUIA_DE_ARCHIVOS.md). Historial anterior a esta organización: repositorio
`Tesis-IA-Drone` (archivo).

## Créditos

- **Brahian Andrés Orrego Osorio**: autor, hardware, integración y pruebas.
- **Tania**: redacción del documento del proyecto de grado.
- Universidad de San Buenaventura, Ingeniería Aeronáutica.
- Desarrollo asistido por Claude (Anthropic).
