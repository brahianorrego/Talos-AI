# Modelo 3D del dron real (hecho con primitivas)

Pedido por el Coordinador con las fotos de Brahian (`08_EVIDENCIA_Y_DIAGRAMAS/fotos/` 08, 09, 10, 14 a 18). **No es
fotorrealista**: es un modelo proporcionado de **77 piezas** (cajas y cilindros) con los colores del dron.

- Cuadricóptero en X de fibra de carbono, 4 brazos con motores rojos 2212, ESC de 40 A, hélices de 10″, Jetson en caja de
  acrílico transparente con ventilador, 2 antenas WiFi y GPS en mástil, batería LiPo azul con velcro azul debajo del chasis,
  patas de carbono con apoyos de espuma negra y anillos rojos, y el **gimbal BaseCam con el TF03 y la cámara USB encima**.
- `dron_real.py` es **la única fuente**: define las piezas y escribe `dron_real.json` (aquí y en `v16/simulacion/recursos/`).
  Lo usan Unreal (`unreal/dronia_ue.py`), Blender (`dron_blender.py` y `blender/video_cancha_v17.py`) y el visor V16
  (`v16/simulacion/visor/dron_real.js`; con `?dron=v16` se ve el de antes).
- Tamaño total: 0.59 × 0.59 m (de punta a punta de las hélices), 0.41 m de alto; el centro del chasis queda 0.265 m sobre el suelo.
- Vistas de prueba: `mediciones/capturas/dron_real_{tres_cuartos,lado,arriba}.jpg`; en Unreal: `unreal_dron_real.jpg`;
  en el visor: `dron_real_en_visor.jpg`.
- Para regenerar las vistas: `blender --background --factory-startup --python dron_blender.py -- <carpeta>`.

## Medidas que FALTAN (hoy son estimadas a ojo con las fotos; medir con cinta y pesar)

1. Distancia real entre motores opuestos (hoy 0.50 m, con la hélice de 10″ = 0.254 m como regla).
2. Tamaño de la placa del chasis, de la caja de acrílico de la Jetson y de la batería (hoy 0.19 / 0.105 × 0.085 / 0.155 × 0.05 × 0.045 m).
3. Altura de las patas (0.26 m) y largo de los apoyos de espuma (0.34 m).
4. Hacia dónde apunta el largo de la batería y cuál lado del TF03 es el frente.
5. Posición exacta del GPS, de la cámara USB y de los conectores XT60.
6. Cables: no se modelan.

Dato medido: 2 371 g con todo (báscula, fotos 12 y 13). El TF03 (74 × 47 × 36.5 mm) y el motor 2212 son de hoja de datos.

## Lo que mostró el modelo (útil para la variante C, que es de otra sesión)

- En el dron real **la batería cuelga justo debajo del chasis**, donde la variante C quiere la cámara al piso (IMX219): taparía
  su imagen. En el visor, la cámara al piso ignora la batería, pero en el dron real habría que ponerla fuera de la batería.
- El TF03 va en el gimbal con la cámara USB (como en las fotos), no fijo en la nariz como suponía la V16; ver VARIANTES.md.
- La estación de tierra (`estacion/`) usa todavía el dron decorativo del visor clásico; falta pasarle este modelo.

## Estado por programa (2026-10-18)

| Dónde | Archivo | Estado |
|---|---|---|
| Unreal | `unreal/dronia_ue.py` | usa el modelo |
| Blender y el video | `dron_blender.py`, `blender/video_cancha_v17.py` | usa el modelo |
| Visor V16 | `v16/simulacion/visor/dron_real.js` | usa el modelo (`?dron=v16` = el de antes) |
| **Estación de tierra** | `estacion/dron_real.js` | **usa el modelo** (`?dron=viejo` = el decorativo); hélices y gimbal siguen respondiendo |

Pruebas: `03_SIMULACION_RL\.venv\Scripts\python.exe -m unittest discover -s 04_VISOR_Y_MOTOR_GRAFICO/pruebas` (4 pruebas: las 3 copias del
JSON al día, piezas válidas, tamaño cercano al real, y el gimbal y la batería en su lugar).
