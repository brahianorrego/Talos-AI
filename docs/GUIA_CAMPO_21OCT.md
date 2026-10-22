# Guía de campo · miércoles 21-oct · pruebas del mínimo en el parqueadero

Para Brahian y Tatiana. Reemplaza a `HOJA_DE_CAMPO_19OCT.docx` en lo que cambió: **ya no hay gimbal ni cámara USB**, la cámara es la CSI con la geometría medida,
y el dron va sin hélices sobre el carro. Las pruebas son las mismas del plan (E0 a E6); el detalle del panel está en `PLAN_CAMPO_19OCT.md`.

## 0. Estado verificado hoy (16:25, por SSH)
- Jetson encendida, el servicio `campo` activo y el panel respondiendo. Cámara CSI a **25 FPS** con YOLO a 18 ms; LiDAR leyendo (0.7 m dentro de la casa).
- Configuración cargada: campo de visión **68.3° × 54.0°**, cámara a −2.4°, LiDAR a −6.7°, punto del LiDAR en la imagen (49.6 %, 59.5 %).
- **La Pixhawk no responde ahora** (sin batería del dron): en el campo se alimenta todo con la batería del dron por el convertidor (§2). Sin ella no hay voltaje ni modo en el panel.
- La Jetson se conecta sola a las redes guardadas los hotspots guardados (el del celular de Brahian y el de Tatiana); en el parqueadero no habrá la red de la casa.

**Versión para imprimir o leer en el celular, con dibujos y explicada para quien no es ingeniero:** `docs/guia_campo_21oct/GUIA_CAMPO_21OCT.pdf`.
**Pantalla nueva:** doble clic en `ABRIR_ESTACION_MINIMO.bat` (Escritorio) abre la estación TALOS-AI conectada a la Jetson (video, LiDAR, tomas). El panel de siempre `http://talos-jetson.local:8080` queda de respaldo.

## 0 bis. Cambios del 21-oct por la tarde (pantalla y video)
- **Sin gimbal en las pantallas** (el mínimo lleva cámara y LiDAR fijos al chasis). La pantalla vieja muestra "Enlaces e inclinación"; la nueva no tiene nada de gimbal.
- **Video más grande** (la cámara ahora entrega 1280×960 y YOLO sigue viendo 640×480): en la estación nueva, selector **Video**: Normal 640×480, Alta 960×720 (la que queda por defecto), Máxima 1280×960. Medido por WiFi: Normal 29 fps ≈ 5 Mbps, **Alta 29 fps ≈ 12 Mbps**, Máxima 29 fps ≈ 23 Mbps. Había un error propio que dejaba las grandes en 15 fps (el reloj del codificador se tomaba al terminar y saltaba un cuadro de cada dos); ya corregido. Si el video se atrasa por el hotspot, bajar a Normal. La Jetson graba `video.avi` a 960×720: ≈ 60-100 MB por minuto (3-6 GB por hora).
- **Roles de hoy:** Tatiana opera el portátil (elige la toma, INICIAR, grita las instrucciones; botón **Sonido** para que el portátil hable y pite) y Brahian camina **sin celular**; ya no se usa `/persona`.
- **Red:** usar **solo un hotspot, el de Tatiana** (apagar el del celular de Brahian): la Jetson y el portátil conocen las dos redes y, si ambas están, la Jetson puede escoger la equivocada. La estación tiene un aviso naranja con **Buscar Jetson** (recorre la red) y un campo para escribir la dirección si `talos-jetson.local` no resuelve.
- **Mapa GPS** (esquina del video, clic = grande) y tarjetas de **velocidad de avance, ascenso, altura, rumbo, satélites y HDOP**: vienen de la Pixhawk (probado con datos reales: 3D+DGPS, 8-9 satélites, HDOP ≈ 1.5-2). El mapa usa teselas de internet con caché en el portátil; las del lugar de hoy ya están guardadas.
- **Qué abrir:** la estación nueva se abre con `ABRIR_ESTACION_MINIMO.bat` (Escritorio). **No** es `http://talos-jetson.local:8080`, que es la pantalla vieja de la Jetson (sin mapa ni los cuadros nuevos; queda de respaldo). En pantallas anchas (≥ 1500 px) la estación usa tres columnas (video | tomas | telemetría) y cabe todo sin bajar con la rueda; el mapa es pequeño en la esquina del video.
- **Fluidez medida:** 60 s de video Alta por el camino real (portátil → estación → Jetson): 29.9 fps, hueco más largo 0.07 s, ningún hueco de más de 0.3 s.
- **Sobre el video:** el número del LiDAR (esquina y junto a la cruz azul), cada persona con su distancia "por la cámara" (orientativa, ~ o >), el aviso **LiDAR EN LA PERSONA** y el horizonte según la inclinación del dron.
- **Instrumentos nuevos** (estación): inclinación del dron (cabeceo/alabeo con la Pixhawk; sirve para nivelar), rayo del LiDAR y suelo esperado (con la altura medida), medidas de la persona (ángulo, cámara vs LiDAR, ¿el rayo le pega?), exposición de la imagen (gris medio, % quemado/oscuro), temperatura de la Jetson y progreso de las tomas contra la meta corta/completa.
- **Despliegue:** archivos nuevos copiados a la Jetson (`panel_campo.py`, `percepcion.py`, `registro_minimo.py`, `config.py`); respaldos `*.antes_hd` en `~/Escritorio/dron_ia/`. Para volver atrás: copiar cada `.antes_hd` sobre su archivo y `systemctl --user restart campo`.
- **Sin verificar:** después del despliegue la Jetson quedó fuera de red (¿desconectada para salir?), así que no se probó el servicio más de ~10 minutos ni el video grabado a 960×720 (peso y que se reproduzca).

## 1. Antes de salir (10 min)
1. Batería del dron 4S **cargada**, portátil con cargador, los dos celulares cargados, power bank si hay, bolsa ignífuga.
2. **Cinta métrica de 15 m o más**, 7 marcas (conos, botellas, tiza o cinta) para 2, 4, 6, 8, 10, 12 y 15 m, un cartón grande (~1.5 × 1 m) para E6, un nivel (el del celular sirve), cinta o cuerda para amarrar el dron.
3. Hélices **puestas aparte, en la casa**: el dron va SIN hélices, con el Futaba apagado.
4. En el celular de quien camina: pantalla sin apagarse automático, volumen alto y modo silencio apagado.
5. Si queda poca luz: el orden de prioridad es **E0, E2, E3, E1, E4, E5, E6**. Con el sol bajo la cámara baja de FPS; si el panel muestra menos de 20 FPS, se para (no sirve de dato).

## 2. Montaje (≈ 20 min)
1. **Elige el eje de la prueba**: la línea recta del pasillo con ≥ 15 m despejados delante del dron. Sol de lado o a la espalda del dron, nunca de frente.
2. El dron va sobre el carro (como en la foto del 21-oct), **mirando hacia el pasillo**, y bien amarrado.
3. **Nivelarlo.** El techo del carro es curvo e inclinado: si el dron queda con la nariz arriba o abajo, el LiDAR deja de apuntar a −6.7° y se pierde la calibración.
   Pon el nivel sobre la placa superior: debe marcar 0° (±1°). Si no, calza con cartón o cinta hasta que quede nivelado.
4. **Mide y anota**: altura del eje del LiDAR al suelo (el lente de la cámara está 4.5–5.5 cm más arriba). Esa cifra va en el campo "Altura cámara" del panel.
   Regla útil: el rayo toca el suelo a unos **8.5 × la altura** (altura 2.0 m → 17 m; 1.5 m → 12.8 m). Más allá de esa distancia el LiDAR lee el piso, no a la persona: es lo esperado, no una falla.
5. **Marcas**: desde el frente del LiDAR, con cinta tensa, pon 2, 4, 6, 8, 10, 12 y 15 m sobre el eje del pasillo. Anota si alguna no se pudo (por ejemplo, si el pasillo mide menos).
6. **Línea de cruce de E4**: la franja azul del piso sirve como línea (§4). Mide desde el frente del LiDAR hasta esa franja y anota la distancia real; esa es la "línea" de las tomas, aunque no sea exactamente 5, 8 o 12 m.
7. **Energía**: conecta la batería del dron al convertidor de la Jetson (como ya se probó). Esperar **3 minutos** a que arranque. Debe prender sola, sin tocar nada.
8. **Red**: Tatiana (o Brahian) enciende el **hotspot de su celular antes** de la Jetson o a la vez (el de Tatiana). Portátil y celular de la persona se conectan a ese mismo hotspot.
9. Portátil: `http://talos-jetson.local:8080`. Si no abre, la IP que muestre el celular en "dispositivos conectados". Celular de quien camina: la misma dirección terminada en `/persona` → pulsar **"Activar sonido y voz"**.

## 3. Comprobaciones antes de empezar (5 min)
| Revisar | Debe verse |
|---|---|
| Video | Imagen bien expuesta, ≥ 24 FPS, YOLO ~20 ms |
| LiDAR | Mide algo coherente; con la mano a 1 m marca ~1 m |
| Pixhawk | Modo, voltaje ~16 V, sin avisos de batería |
| **Punto del LiDAR (`/alinear`)** | Con una persona a 4 m, el punto cae **sobre su cuerpo** y la distancia dice ~4 m. Si no cae, avisar antes de seguir: el dron se movió o no está nivelado |
| Toma de prueba | Una E0 (20 s, nadie delante): graba, el celular habla y la repetición sube sola |

## 4. Las tomas, en orden (cada una: persona en su marca → INICIAR → 5 s → señales del celular → pitido largo = fin)
Regla de oro: **la persona nunca a menos de 3 m del dron** (sin hélices se puede llegar a 2 m solo en E1).

| # | Toma | Qué hace la persona | Repeticiones (corta / completa) |
|---|---|---|---|
| 1 | **E0** · nadie delante | Fuera del campo de la cámara (detrás del dron o a un lado) 20 s | 2 / 3 |
| 2 | **E2** · camina 15 → 3 m | Parada en la marca de 15 m, de frente; al "¡Camina!" avanza a paso normal y se detiene en 3 m | 5 / 10 |
| 3 | **E3** · trota 15 → 4 m | Igual, pero trotando; se detiene en 4 m | 5 / 10 |
| 4 | **E1** · quieta en cada marca | Parada en 15 m; cada 9 s suena y pasa a 12, 10, 8, 6, 4 y 2 m, 5 s quieta en cada una (63 s) | 1 / 3 |
| 5 | **E4** · cruza de lado | Ver abajo | 3 caminando + 3 trotando / 5 de cada combinación |
| 6 | **E5** · silla con el dron hacia persona quieta | Solo si hay silla con ruedas y alguien que empuje; sino se salta | 2 / 5 |
| 7 | **E6** · cartón acercándose | Cartón en 15 m; quien empuja va escondido detrás; para a 3 m | 2 / 5 |

### E4 en este parqueadero (la franja azul)
- **Línea**: la franja azul del piso. Mide con la cinta su distancia desde el frente del LiDAR. El panel solo ofrece 5, 8 o 12 m: elige la más cercana y **escribe la real en la nota** junto a "camina" o "trota" (ejemplo: `camina 7.3m`; la nota admite 40 caracteres). Si la franja queda lejos de las tres (más de 1 m), mejor marca la línea con cinta a 5, 8 o 12 m exactos y usa la franja solo como referencia visual.
- **Sentido** (suponiendo que el dron mira hacia ti, como en la foto): ponte en el extremo de **TU DERECHA** del pasillo, de frente al dron, y al "¡Cruza!" camina o trota hacia **TU IZQUIERDA**, hacia el lado de la franja azul. Así el panel te ve moverte de izquierda a derecha en la imagen.
- **Ancho**: el pasillo mide ~4.5–5 m; basta. Cruza por el **espacio libre**, no por detrás de los carros.
- **Variante realista (opcional, después de las normales)**: salir de entre dos carros hacia el pasillo. Es un escenario distinto: se anota en la nota **"sale_de_entre_carros"** y se hace aparte, para no mezclarlo con el E4 limpio.
- Un carro delante del LiDAR hace que mida el carro, no a la persona; por eso la línea de E4 va por donde el pasillo está libre.

### Lo que hace cada rol
- **Operador (Brahian, junto al dron con el portátil)**: elige el escenario y la repetición, revisa que el panel esté verde, vigila LiDAR y FPS, cancela una toma mala.
- **Persona (Tatiana o Brahian)**: en la marca con el celular en `/persona`; obedece la voz, los pitidos y la vibración. Con una sola persona: se elige el escenario en el portátil, camina a la marca y **pulsa INICIAR en el celular**.
- Si algo sale mal (alguien se cruza, se mueve el dron, el celular no suena): **CANCELAR**, queda anotada y se repite.

## 5. Qué anotar en papel (o en la nota del panel)
Altura real del eje del LiDAR; nivel del dron (grados); hora de inicio y fin; clima (sol / nublado / sombra); distancia real de la franja azul; marcas que no se pudieron poner; cualquier incidente (viento, alguien que se cruzó, el dron se movió).

## 6. Si algo falla
| Problema | Qué hacer |
|---|---|
| El panel no abre | Probar la IP; que portátil, celular y Jetson estén en el mismo hotspot; esperar 3 min tras encender; último recurso: cable de red entre portátil y Jetson |
| El celular no suena | Pulsar "Activar sonido y voz" una vez, subir volumen; la vibración funciona sin sonido |
| FPS bajos | Falta luz o hay contraluz; moverse a la sombra o esperar; no es falla del sistema |
| LiDAR "sin retorno" o lee el piso | Normal más allá de ~8.5 × la altura; si la persona está más cerca y no la ve, revisar nivel y punto en `/alinear` |
| La Pixhawk no aparece | Revisar la batería y el cable TELEM2; las tomas se pueden grabar sin ella pero no habrá voltaje ni modo |
| Batería baja | Aviso a 14.4 V; desconectar a 14.0 V y parar aunque falten tomas |
| Huele a quemado o se calienta mucho | Desconectar la batería ya |

## 7. Al terminar
1. Foto de la pantalla del panel y del montaje (evidencia). **El video y las fotos del parqueadero muestran placas y personas**: se guardan en `05_EVIDENCIA_Y_DIAGRAMAS/privado/`, no en las carpetas públicas.
2. Desconectar la batería del dron y guardarla en la bolsa ignífuga.
3. En casa: bajar los datos (desde `~/Escritorio/dron_ia/registros/<fecha>/`: `datos.csv`, `tomas.csv`, `video.avi`) y correr el resumen de tomas. Yo lo hago si me avisas que la Jetson está encendida en casa.
4. **Nunca se mezclan** estas tomas con el 94 %/91 % de la simulación: son un experimento aparte. Sí se comparan después con la simulación hecha con la misma geometría (D-079).

## 8. Qué se va a comprobar con estos datos (hipótesis, para anotar si se cumplen)
- La persona se detecta con YOLO en ≥ 91 % de los cuadros desde 12 m (resultado del 19-oct).
- Con el dron nivelado y a la altura h, el LiDAR toca a la persona desde ~2.4 m (si h = 2.0 m) hasta ~8.5 × h; antes de eso lee el piso o el fondo. En el 19-oct no le pegaba a la persona: esta vez debería, porque ya se alineó.
- El punto del LiDAR cae dentro de la caja de la persona (`lidar_en_caja = 1`) en la mayoría de los cuadros entre 3 y la distancia de arriba.
- Si no se cumple algo, no se corrige en el campo: se anota y se analiza.
