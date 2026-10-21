# Pendientes de Brahian (noche del 20-21 oct)

Lo que no puedo hacer yo (necesita tu cuenta, una descarga que no verifiqué o un permiso). Lo demás sigue en marcha.

## MetaHuman (personas realistas en Unreal)
- **No verificado:** lo que sigue es de lo que sé de Unreal 5.x, no lo comprobé en esta máquina.
- Qué hace falta: iniciar sesión con tu cuenta de Epic en el editor (ya salió tu cuenta en el Crash Reporter, así que probablemente ya está iniciada) y bajar el personaje desde el
  **MetaHuman Creator / Fab** (desde UE 5.6 se importa dentro del editor: menú *Window → MetaHuman*).
- Tamaño: cada MetaHuman completo suele pesar **varios GB** (del orden de 2 a 6 GB) y es pesado para dibujar: con la RTX 3050 de 6 GB y Lumen, 2 personas en
  tiempo real pueden bajar mucho los fps. Recomiendo probar **uno** (el ladrón) y medir; el civil puede seguir con el maniquí.
- Pasos: (1) abrir el editor con `VIVO_UNREAL.bat`; (2) *Window → MetaHuman* e iniciar sesión; (3) elegir un personaje de los predefinidos y *Add to Project*;
  (4) avisarme el nombre de la carpeta que quedó en `Content/MetaHumans/` y yo lo conecto a `vivo_unreal.py` (se cambia la figura del ladrón y las animaciones de caminar/trotar).
- Lo puedo instalar yo solo si tu sesión de Epic ya está abierta en el editor; si pide clic en "Aceptar" o términos, eso lo tienes que hacer tú.

## Otros
- Fotos nocturnas: faltan ángulos de la **fachada de vidrio con franja naranja** y de la **escultura de la turbina** de cerca (para hacerlas más parecidas).
- Gamepad: probar con uno real (los gatillos suben y bajan; LB/RB giran el pan). Yo solo probé el teclado.

## Personajes y ambiente realistas (21-oct, lo que averigüé)

**Por qué la cola del Launcher dice "En cola":** en `C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests\Pending\` hay un solo elemento atascado: **Quixel Bridge 5.8** (250 MB, instalación incompleta). El registro del Launcher muestra advertencias `MainGameAppId mismatch` y `SDMeta download failed ... falling back to EMS` en todos los motores. Es el fallo conocido del Launcher después de actualizar UE 5.8.x (los foros de Unreal lo describen como "stuck on Resume / manifest commit never completes"; Epic lo cerró como duplicado, sin arreglo oficial) y la instalación de plugins "no hace nada" ([foro](https://forums.unrealengine.com/t/not-able-to-install-fab-and-quixel-bridge-plugins/2735299)). **No toqué los archivos del Launcher** (hay que cerrarlo y editar manifiestos; es riesgoso y es tu sesión). El **plugin de Fab ya está instalado** con UE 5.8 (aparece en el Launcher como "Fab UE Plugin"), así que no necesitas Quixel Bridge: usa Fab desde el editor.

**Lo que hace falta de tu cuenta de Epic (nadie más puede):**
1. **Fab dentro del editor** (para Megascans: árboles, pasto, adoquín, ladrillo, asfalto): abre el editor de Unreal → menú **Ventana → Fab** → inicia sesión con tu cuenta de Epic → busca "Megascans" → en cada resultado gratuito pulsa **Añadir a mi biblioteca** y luego **Añadir al proyecto** (proyecto `DronIA_Cancha`). Tamaño: cada material suele pesar de decenas a pocos cientos de MB; no verifiqué los tamaños exactos. No pide administrador. Recomendados: ladrillo rojo, adoquín gris, losas de concreto con pasto, asfalto, pasto/césped.
2. **MetaHuman** (personas realistas): desde UE 5.6 se importan dentro del editor. Con la sesión de Epic abierta: **Ventana → MetaHuman** (o Fab → buscar "MetaHuman") → elegir personajes predefinidos → **Añadir al proyecto**. Cada personaje completo pesa varios GB (no verifiqué el tamaño exacto). **Pide tu cuenta de Epic**, no administrador. Con la RTX 3050 de 6 GB conviene empezar con **uno solo** (el ladrón) y medir fps. Cuando estén en `Content/MetaHumans/`, avísame el nombre y yo los conecto a `vivo_unreal.py` con las animaciones de caminar/correr/agacharse/saltar (los esqueletos de MetaHuman no son los del maniquí: hay que retargetear).
3. Si el Launcher sigue "En cola": cerrar el Launcher del todo (también el ícono de la bandeja), abrirlo, ir a **Biblioteca → Unreal Engine → ⋯ → Opciones**, y volver a intentar; si no, la solución de los foros es un script de PowerShell no oficial (busca "UE 5.8 manifest commit workaround v2" en los foros de Unreal) que solo se debe usar después de revisar que el motor ya está en la versión nueva.

**Lo que bajé yo mismo (sin cuenta, licencia CC0, de [Poly Haven](https://polyhaven.com)):** texturas PBR reales (color, normal, rugosidad, AO a 2K) de ladrillo rojo, pasto, asfalto, adoquín, losas con pasto entre ellas y concreto, en `04_VISOR_Y_MOTOR_GRAFICO/assets_polyhaven/` (carpeta fuera de Git, con su licencia en cada subcarpeta). Script: `entorno/bajar_polyhaven.py`.
