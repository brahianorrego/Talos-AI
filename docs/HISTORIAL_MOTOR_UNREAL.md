# Historial del motor gráfico de Unreal (pausado el 21-oct-2026)

Brahian pausó el motor de Unreal. Todo queda guardado y se puede retomar. Mientras tanto se juega con la estación web (`JUGAR_Y_ENSENAR.bat`, mundo three.js).

## Qué se construyó
- **Proyecto** `DronIA_Cancha` en `Documentos\Unreal Projects\` (no está en el repositorio; los scripts sí: `04_VISOR_Y_MOTOR_GRAFICO/unreal/`). Unreal 5.8.3, RTX 3050 6 GB.
- **Campus real** (`entorno/entorno_u.py` → `entorno_u.json`): 51 edificios, estanque, parqueadero, vías, canchas, avión Searca y turbina, medidos sobre una vista satelital (Esri z19) y el mapa de la USB. Árboles: Megaplants (Fab) cerca del campo y árboles de baja malla lejos.
- **Materiales**: césped PBR único (Megascans Uncut Grass) en campo y terreno, adoquín/asfalto de Roads 05, fachadas de ladrillo por pared, techos de concreto (`unreal/entorno_u_ue.py`, maestro `M_SueloPBR`).
- **Personas**: ladrón (Survival Character: chaqueta oscura, mochila) y civiles (Quantum Character: camisa clara), fundidos en una malla (`unreal/personajes_ue.py`); animaciones del proyecto sin retargeting (esqueleto declarado compatible con Manny).
- **Cámaras del dron** (SceneCapture → JPG): CSI#1 512×384 a 8 Hz, CSI#2 320×240 a 2.5 Hz y vista «Mundo 3D» 640×360 a 4 Hz bajo demanda; gamma 2.0 en el origen (`unreal/vivo_unreal.py`).
- **Rendimiento medido** (2 cámaras, 4 personas, estación abierta): **45–49 cuadros/s** (media 47.5, mínimo 41). Tabla y causas en `docs/MATERIAL_PARA_DOCUMENTO/05_motor_grafico_y_juego.md` §8-9.
- **Estación** (`estacion/operacion.html`): interfaz negra TALOS-AI, PFD, mapa satelital (tecla 3), pestaña Entrenamiento (5), ayuda de cada dato, CSI#2 4:3 con cuadrícula (K) y ampliar (X).

## Qué quedó pendiente
- **MetaHuman**: plugin y 29 presets instalados; `MH_Mateo` (rig recuperado de un autosave) y `MH_Jorge` en `/Game/DronIA/Personas`. El ensamblado desde Python se cae dentro del editor y en modo sin ventana no genera texturas: hay que hacerlo con clics (abrir el asset → Ensamblar, calidad media, canal Optimizado) y luego fundir/retargetear.
- **Edificios más fieles** (fachadas con vidrio y cubiertas inclinadas; ahora son cajas con ladrillo), pasto de cancha de tenis/múltiple con textura.
- **Rediseño final** de la interfaz y mapa satelital con GPS real (`SAT.gps({lat,lon,rumbo})` ya listo).
- Licencias de Survival, Quantum y Free Shrubs por confirmar (`docs/MATERIAL_PARA_DOCUMENTO/08_creditos_y_licencias_fab.md`).

## Cómo reanudarlo (Windows)
- **Todo en una sola ventana (estación + Unreal minimizado):** doble clic en `04_VISOR_Y_MOTOR_GRAFICO\VIVO_UNREAL.bat` (cierra copias viejas, abre simulación, servidor, puente, editor minimizado y la estación). `DRONIA_PANTALLA_UNREAL=50` lo parte en dos ventanas; `DRONIA_DEPURAR=1` abre la estación con puerto de depuración (9222) para capturas con `capturar_estacion_cdp.mjs`.
- **Reconstruir el nivel** (con Unreal cerrado): borrar `...\DronIA_Cancha\Content\DronIA\Mapas\Cancha_V17.umap`, poner `DRONIA_REHACER=1` y correr `unreal\ejecutar_en_unreal.bat rehacer_nivel.py` (~8 min, se cierra solo). Antes regenerar datos: `python entorno\entorno_u.py` y `python entorno\fachadas.py` (con el `.venv` de `03_SIMULACION_RL`).
- **Probar sin reiniciar el editor:** escribir órdenes en `unreal\_cache\consola.txt` (una por línea; `py <código>` ejecuta Python; `QUIT_EDITOR` lo cierra con orden suave). Cámara del visor: `_cache\camara.txt` = `x,y,z,rumbo,cabeceo`; foto: crear `_cache\captura.txt`.
- **Reglas aprendidas:** nunca cerrar `UnrealEditor.exe` a la fuerza (se pierde el trabajo sin guardar: ya se perdió el rig de MH_Jorge); no crear mallas con esqueleto en el mismo cuadro durante el dibujo; cada captura de cámara cuesta ~20 ms fijos, por eso 8/2.5/4 Hz; la estación a 20 cuadros/s para no quitarle GPU a Unreal.
