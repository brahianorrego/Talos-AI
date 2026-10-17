# Recursos del visor V16 y sus licencias

| Archivo | Origen | Licencia |
|---|---|---|
| `three/three.module.min.js`, `three/three.core.min.js`, `three/addons/…` | three.js 0.185.1 (npm `three`) | MIT (ver `three/LICENSE`) |
| `cielo/spruit_sunrise_1k.hdr` | Poly Haven, "Spruit Sunrise" (Greg Zaal), copia del repositorio de ejemplos de three.js | CC0 |
| `cielo/quarry_01_1k.hdr` | Poly Haven, "Quarry 01" (Greg Zaal), copia del repositorio de ejemplos de three.js | CC0 |
| `texturas/*.jpg` | Generadas con `herramientas/generar_texturas.py` (ruido fractal, autoría propia) | CC0 |

Las personas, el dron, los árboles y los escenarios de la vista previa se construyen con código en `visor/` (sin modelos
descargados). Desde la nube no hubo acceso a ambientCG, Kenney ni Quaternius; si más adelante se quieren texturas o
modelos de esos sitios, van en esta carpeta y se anotan en esta tabla.

## Agregado el 2026-10-17 (fase V2, personas vestidas)

| Archivo | Origen | Licencia |
|---|---|---|
| `three/addons/loaders/GLTFLoader.js`, `three/addons/utils/SkeletonUtils.js` | three.js 0.185.1 (npm `three`, vía cdn.jsdelivr.net) | MIT |
| `personas/Casual_Hoodie.glb`, `Worker.glb`, `Casual_2.glb`, `Suit.glb`, `Farmer.glb` | Quaternius, "Ultimate Modular Characters" (quaternius.com), sin animaciones, exportados con Blender | CC0 |
| `personas/animaciones.glb` | Quaternius, "Universal Animation Library" 1 y 2 (14 animaciones), redirigidas a los personajes con `04_VISOR_Y_MOTOR_GRAFICO/blender/redirigir_animaciones.py` | CC0 |
| `naturaleza/` (CommonTree_1, CommonTree_3, CommonTree_5, Pine_2, Grass_Common_Short, con sus texturas; corteza reducida a 512 px) | Quaternius, "Stylized Nature MegaKit" (quaternius.com), copia de `LICENCIA_Quaternius.txt` | CC0 |
