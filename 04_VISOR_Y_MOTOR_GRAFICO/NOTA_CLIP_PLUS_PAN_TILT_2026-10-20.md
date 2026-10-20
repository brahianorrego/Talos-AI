# Nota · repeticiones del plus (variante H) en la estación y en Unreal (2026-10-20)

Repeticiones de Simulación: `03_SIMULACION_RL/repeticiones_v17_h/` (V17.7 con la ruta de Brahian; fuera de Git): `cambio_de_v`, `civil_curioso`,
`reencuentro_alto` y `rendicion`. Se vieron con el dron PLUS (pan-tilt ARRIBA, CSI#1 + TF-Luna encima, CSI#2 al piso).

## Estación (`cambio_de_v.json`, cargada con el selector o `cargarPartida`)
- **"PAN ±x° · TILT ±y°"**: el **tilt se mueve** con la partida (medido: −11° al buscar, −44° al perseguir de cerca, −23° en el flanqueo, −45° en el tope, −26°,
  −25°…; dentro de −45°…+15°) y el modelo 3D inclina la cuna con él. El **pan vale 0° en todas las repeticiones**: `foto()` todavía no trae el campo `pan` (en la V17 el
  pan está bloqueado: `PAN_ACTIVO_EN_ENTRENAMIENTO = false` en `variante_H.json`); en cuanto aparezca `c.pan`, la estación y Unreal lo usan sin cambios.
- **Ruta de Brahian**: se dibuja (línea cian, 13 puntos blancos, abanicos amarillos del vaivén y anillo de la entrada); al reproducir, los puntos se ponen **verdes**
  cuando el dron pasa a menos de 1.5 m a más de 2.5 m de altura (medido: 0, 2 y 4 de 13 durante los primeros 40 s). Las repeticiones no traen el avance de la ruta
  (`ruta` es el flanqueo de la búsqueda, no la ruta de Brahian), así que los verdes salen de la posición real del dron, no de la intención de la política.
- Captura: `mediciones/capturas/estacion_plus_repeticion_h_ruta.jpg` (cenital con la ruta; a la izquierda la CSI en pan-tilt con "PAN +0° · TILT −23° · HFOV 62.2°").

## Unreal: `videos/clip_plus_pan_tilt.mp4` (fuera de Git)
- `civil_curioso.json`, de 55 a 175 s (120 s, 2 881 cuadros, 1080p, 64 MB; render de unos 14 min). Es el tramo con más flanqueo profundo y pérdida (286 de 1 200 cuadros)
  y más variación de tilt. Lleva el dron plus con el pan-tilt arriba, los dos maniquíes, las dos V y la ruta de Brahian dibujada.
- Captura: `mediciones/capturas/unreal_clip_plus_pan_tilt.jpg` (4 cuadros: 8 s, 41 s, 79 s y 108 s).
- **Límite honesto:** la cámara de cine sigue al ladrón y deja al dron lejos o fuera del cuadro; el movimiento del pan-tilt casi no se ve en este clip, y el pan es 0 en todo
  el clip. Para verlo de cerca, importar con `DRONIA_CAMARA=dron` (cámara cercana, delante y a la izquierda del dron, mirándolo): ya está en `importar_repeticion.py`, sin renderizar.
