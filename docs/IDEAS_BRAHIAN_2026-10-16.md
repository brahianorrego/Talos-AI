# Ideas de Brahian · 16 de octubre de 2026 (dictadas por voz)

Encargo para el plus (simulación). Lo ordena el Arquitecto en el plan V17; aquí queda tal como lo pidió Brahian.

## Meta

Que el plus sea "una cosa de locos": simulación mucho más realista, entrenamiento más avanzado y un motor gráfico que se
vea real, para un proyecto de grado **laureado**.

## Escenario real (lo que se va a montar)

- **Dónde:** canchas de la Universidad de San Buenaventura.
  - **Cancha de fútbol:** césped, abierta, muy grande, con **árboles alrededor**. Es la principal.
  - **Cancha cerrada:** piso pintado de colores (tipo cancha de tenis), encerrada. Alternativa.
- **Paneles:** se piden prestados **dos conjuntos de dos paneles** de exposición de la universidad (4 paneles). Cada
  conjunto son dos paneles unidos con un ángulo, en forma de **V o de L**, para que no se caigan (derechos se van hacia
  adelante o hacia atrás). Foto de referencia: `08_EVIDENCIA_Y_DIAGRAMAS/paneles_de_exposicion_universidad.png` (privada:
  salen personas). **El Arquitecto decide y le dice a Brahian el ángulo y la disposición** (distancias, orientación).

## La misión completa

1. El piloto despega el dron.
2. **Tránsito:** en el camino se encuentra un **árbol**, una **persona**, **los dos al tiempo** o un **panel**. Ahí actúa
   el sistema del mínimo (detenerse y subir).
3. Llega a cierta zona y el piloto **activa la IA manualmente** desde el control (radio).
4. **Zona de IA:** los dos conjuntos de paneles, **un ladrón y un civil normal**. El ladrón intenta esconderse; el dron lo
   tiene que buscar.
5. La confirmación del sospechoso llega **al computador** (humano en el lazo).

## Interfaz en el computador

No solo Mission Planner: una interfaz propia donde se vea **lo que ven las cámaras**, el visualizador, el mapa, etc.

## Opciones de hardware a estudiar (variantes)

- **LiDAR:** TF03 (largo alcance, cable grueso) y TF-Luna (liviano).
- **Cámaras:** hasta **tres**: dos CSI por cable flex en **CAM0 y CAM1** de la Jetson + la USB actual.
- **Gimbal:** dejarlo o quitarlo.
- **Pan-tilt de dos servomotores** en una estructura impresa en 3D, con el LiDAR y la cámara encima, controlado por la
  Pixhawk o por la Jetson. Opciones: el pan-tilt **sobre el estabilizador** (para que lo estabilice), **solo el pan-tilt**
  sin estabilizador, u otras combinaciones.
- Hay que comparar dónde va cada cámara y cada LiDAR. Foto del pan-tilt de referencia:
  `08_EVIDENCIA_Y_DIAGRAMAS/pan_tilt_servos.png`.

## Lo que NO va aquí

Lo físico del dron, el mínimo indispensable y el documento escrito se trabajan en la conversación en la nube de la cuenta
de Tania. Aquí solo simulación y plus.
