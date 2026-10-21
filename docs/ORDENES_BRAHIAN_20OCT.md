# Órdenes de Brahian · 20 oct (después de ver la estación)

Archivo de trabajo para las sesiones (no es documentación). Brahian dictó esto mirando la estación de tierra; vale por encima
de lo anterior si lo contradice. **Menos documentos:** no escribir informes ni decisiones nuevas salvo una línea en
`docs/DECISIONES.md`; el trabajo va en código, datos y la estación.

## A. Hardware que existe (aclaraciones)
1. **No hay LiDAR de 360°.** Hay DOS LiDAR de **1 haz (1D)**: el **TF03 fijo apuntando siempre al frente** y el **TF-Luna** que va
   en el pan-tilt junto a la CSI#1 (mira lo mismo que la cámara). El "mapa de puntos" se arma moviendo el dron y el pan-tilt con
   esos dos haces; no es un LiDAR giratorio. Quitar todo rastro de "LiDAR 360°".
2. Dos cámaras CSI iguales (62.2° × 48.8° nominal): CSI#1 en el pan-tilt (pan y tilt, sin roll) y CSI#2 fija. La vista de la CSI#2
   se ve **borrosa** en el visor y no debe: es la misma cámara que la frontal; mismo render, mismo ruido.
3. Hardware debe decir **dónde conviene la CSI#2** (hoy al piso) y cómo combinar las 2 cámaras y los 2 LiDAR para que cada uno
   sirva de verdad (ver sección E).

## B. Paneles (escenario)
- Cada panel: **2.30 m de alto × 1.50 m de ancho × 5 cm de grosor** (casi sin grosor). Dos paneles unidos forman una V (3 m en
  total). **Abrir el ángulo lo más ancho posible** sin que se caigan: por omisión **160°**, y al azar entre **120° y 175°**.
- Los dos conjuntos **giran** (rotación al azar en cada partida), no están siempre igual. El mapa no debe verse siempre igual.
- Dos conjuntos separados (cada uno de 2 paneles), un ladrón y un civil.

## C. Lógica de búsqueda (consejos, no reglas duras)
No es un cuadrado literal. Lo que dicta Brahian:
1. Al activar la IA: 360° girando el dron para ubicar los paneles (con los dos LiDAR de 1 haz y las cámaras).
2. Si no ve al ladrón: **ir al panel más cercano** (elegir cuál de los dos está más cerca) y **colocarse DETRÁS** del panel,
   a buena distancia (más atrás = más rango visual y más tiempo de esquivar).
3. Si el ladrón está ahí: **ir detrás del ladrón** (seguirlo, no dejar que se vaya).
4. Si el ladrón rodea hacia la otra esquina del panel: **ir a la otra esquina** y buscar detrás de esa esquina; así de esquina en
   esquina.
5. Si no está detrás de ninguna parte: mirar de frente con vaivén; si no, **pasar al otro panel**. Movimientos rápidos.
6. **Nunca quedarse quieto**: siempre en movimiento.
7. Es una guía para que la red aprenda, no una regla dura; la red puede mejorarla.
La versión actual (cuadrado de 6.1 m) **está fallando**: reemplazarla por esta lógica y medirla contra la anterior.

## D. Altura
- **No más juego con la altura** (quitar SUBIR/BAJAR como botones de la red; ya no se entrena la altura).
- Altura base **2.0 m** (probar también 1.7 m y 2.6 m; Brahian prefiere 2.0 m: pasa sobre la cabeza de una persona y el TF03
  frontal alcanza a una persona). Solo si el ladrón está **muy cerca** (a ~4 m o menos, valor a medir) sube a **3.30 m**, que
  supera el salto de una persona. No volar a 3.30 m todo el tiempo.
- Con el dron más bajo, revisar de nuevo qué ve cada cámara y el TF03.

## E. Combinación de sensores (pregunta de Brahian, a responder con números)
Con altura baja (1.7–2.6 m) y un TF03 frontal horizontal: ¿para qué sirve cada LiDAR y cada cámara? Evaluar al menos:
(1) CSI#2 mirando al piso; (2) CSI#2 mirando atrás (el pan ±90° cubre ~240° y deja ~120° atrás sin ver); (3) CSI#2 hacia
abajo-atrás; TF-Luna en el pan-tilt (distancia al objetivo) y TF03 frontal (obstáculos y personas). Recomendar una.

## F. Estación de tierra (interfaz) y mundo
- **Quitar la tecla/botón de volar entre canchas** ("T"): es una bobada. Un solo escenario seleccionable (cancha de fútbol o
  cancha de tenis), no los dos a la vez.
- **Cancha de tenis**: piso de colores, rodeada de **malla metálica de ~10 m**; la separa de las canchas de baloncesto y fútbol la
  misma malla. El **hangar (edificio blanco) queda al lado izquierdo de la cancha de tenis, fuera de la malla**.
- Edificios y **árboles más realistas** (los árboles se ven horribles). Lo realista de verdad es Unreal; en la estación web,
  lo mejor posible.
- **Mapa**: debe llenar toda la pantalla (sin franjas negras); el dron, los paneles que giran y la ruta; sin cosas encimadas.
- **Ingeniería**: nadie entiende qué es; quitarla del primer plano o dejarla clara.
- **Vuelo real** (es el visualizador que se verá en campo): **cámara principal grande**; al lado el **mapa de los dos LiDAR 1D**;
  abajo la **cámara 2**. Cámaras con YOLO.
- **Misiones**: el desplegable de misiones se ve desordenado; reorganizarlo.
- **Quitar el botón "Dron: Mínimo/Plus"** de la interfaz principal (el plus es el dron del visor; el mínimo ya está hecho).
- **Vistas de la 3D**: dejar una o dos (seguir y libre); quitar 'cine' si no aporta.
- Pantalla arriba sobresaturada: ordenar. Todo más ágil, **en tiempo real**, con las animaciones del motor gráfico lo más reales
  posible; medir si Unreal puede correr en vivo en esta RTX 3050 (cuadros por segundo del visor de Unreal con calidad media) y,
  si da ≥ 15, conectar la simulación en vivo; si no, dejarlo como video y decirlo.

## G. El motor gráfico como juego (Brahian, 20-oct noche)
Meta: poder JUGAR la simulación en el motor gráfico, como será en la realidad. Simulación DE DÍA (las fotos nocturnas de la universidad solo dan la distribución y las formas).
1. Manejo manual completo: altura (arriba/abajo), adelante, atrás, lado, giro. (La altura manual es solo del humano; la IA sigue sin controlar la altura, §D. Límites duros siguen: geocerca, piso/techo, paneles.)
2. **Tecla 360 (mantener presionada):** el dron gira 360° buscando. Si mientras gira aparece una persona, el juego la marca ("posible objetivo") y Brahian da CLIC sobre ella para confirmar "ese es el objetivo". Al confirmar, termina el 360 y Brahian toma el control (humano en el lazo, regla 4).
3. La ruta de búsqueda es una guía (§C); la IA decide los movimientos más óptimos. Brahian juega para ver y comparar con la IA.
4. Todo se va anotando para el documento (la cuenta de Tania lo redacta): `docs/MATERIAL_PARA_DOCUMENTO/`.
### G.1 Controles: SOLO teclado y mouse (no hay gamepad; el gamepad queda como extra opcional)
Mano izquierda (teclado): W/S adelante-atrás · A/D lado · Q/E giro · Espacio subir · C bajar · Shift rápido · Ctrl lento/preciso · F (mantener) = giro 360° de búsqueda.
Mano derecha (mouse): mover = pan y tilt de la cámara · clic izquierdo = fijar objetivo (sobre la persona resaltada) · clic derecho = soltar objetivo · rueda = zoom de la vista.
Resto (cerca de la mano izquierda): V cámara asistida (el pan-tilt sigue al objetivo) · 1 cámara principal · 2 CSI#2 · 3 seguir al dron · 4 mapa/libre · Tab mapa y Enseñar · R ruta · G la IA guía (sugiere/toma) y G otra vez devuelve el control · B grabar demostración · P pausa · Esc menú · flechas = pan/tilt alternativo.
Altura: límites duros de piso/techo siguen; la IA no controla altura.
> **Decision de Visor (21-oct, Vista del dron):** Tab = centinela (mundo 3D) ⇄ Vista del dron (con las teclas de vuelo activas en las dos); 1 = mapa y camaras, 2 = Vista del dron, 3 = centinela que sigue, 4 = centinela libre; X = CSI#2 grande; M = Puntos ⇄ Manual (antes Tab). Boton central del mouse = pan/tilt. Ver docs/MANUAL_JUEGO_BRAHIAN.md.
