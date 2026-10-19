# Guía para Brahian · Unreal

**Ya no tienes que hacer nada en Unreal para que los videos salgan.** Desde el 19-oct las personas son los maniquíes
**Manny** (ladrón) y **Quinn** (civil) que **ya vienen con Unreal 5.8** (plantilla Third Person): sin cuenta, sin
descargas y sin tocar el editor. Lo de MetaHumans y Fab queda como **mejora opcional para más adelante** (al final de
esta guía), solo si quieres personas con cara y ropa realistas.

## Qué ya está hecho

- Unreal Engine **5.8.3** instalado (lo hiciste tú) y el proyecto **DronIA_Cancha** en `Documentos\Unreal Projects\`
  (fuera del repositorio, porque pesa mucho).
- Nivel **Cancha_V17**: el campus de la universidad en un solo entorno (cancha de fútbol, canchas cerradas, edificios,
  parqueadero, cerros), las dos V de 90° (paneles de 1.5 × 2.25 m, D-066), el dron real, sol, cielo y nubes.
- **Maniquíes animados** (`04_VISOR_Y_MOTOR_GRAFICO/unreal/maniquies_*.py`): cada persona de la repetición es un maniquí de
  **su estatura** (foto() trae `est`), y su postura sale de foto(): `pos` (de pie, agachado, recostado, gateando),
  el avance `pt` de la transición, la velocidad y el salto.
- Videos (en `04_VISOR_Y_MOTOR_GRAFICO/videos/`, fuera de Git; ábrelos con cualquier reproductor):
  - `zona_de_paneles_maniquies.mp4`: 35 s de una partida V17 con el ladrón y el civil como maniquíes.
  - `galeria_posturas_maniquies.mp4`: el ladrón pasa por todas las posturas y movimientos, uno tras otro.
  - `partida_v17_unreal.mp4` y `vuelo_entre_canchas_unreal.mp4`: del campus (con cilindros en vez de personas).

## Qué trae Unreal y qué es "a mano"

| Postura o movimiento de foto() | De dónde sale | Notas |
|---|---|---|
| Quieto de pie | Animación de la plantilla (`MM_Idle`) | Con su respiración |
| Caminar y trotar | Plantilla (`MF_Unarmed_Walk_Fwd`, `Jog_Fwd`) | La amplitud y el ritmo del paso siguen la velocidad real (para que no patine); trota por encima de 2.4 m/s |
| Salto (impulso, vuelo, aterrizaje) | Plantilla (`MM_Jump`, `MM_Fall_Loop`, `MM_Land`) | La altura la pone `h` de foto(), no la animación |
| **Agachado** | **A mano** (pose procedural) | La plantilla no tiene agacharse: cuclillas con tronco inclinado, altura 0.67 de la estatura; camina agachado con el paso de la plantilla en pequeño |
| **Recostado contra el panel** | **A mano** (pose simple) | Tronco echado hacia atrás, un pie adelante: es una pose simple, se nota poco |
| **Gateando** | **A mano** (pose procedural con ciclo) | Rodillas y antebrazos en el suelo, altura 0.35 de la estatura |
| Transiciones entre posturas | Mezcla de poses con `pt` | Igual que el alto de foto() (lineal) |

Todo se calcula con NumPy y se convierte en una animación por persona (`maniquies_preparar.py`); el contenido de la
plantilla (126 MB) se copió a `Content/Characters/Mannequins/` del proyecto (licencia del contenido de la plantilla de
Epic; no va al repositorio). **Limitaciones:** son figuras sin cara ni ropa (de un solo color: rojo el ladrón, azul el
civil), los dedos no se mueven, el civil que graba con el celular no tiene animación propia y las poses a mano son
sencillas.

## Comandos que usa Claude (por si quieres repetirlos)

Desde la carpeta `04_VISOR_Y_MOTOR_GRAFICO\unreal`, en una consola (CMD o PowerShell):

```
:: 0. una sola vez (o si cambia la versión de Unreal): volcar el esqueleto y las animaciones de la plantilla
"C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "%USERPROFILE%\Documents\Unreal Projects\DronIA_Cancha\DronIA_Cancha.uproject" -run=pythonscript -script="%CD%\maniquies_volcar.py" -unattended -nopause

:: 1. convertir una repetición (o un tramo: desde 55 s hasta 90 s) en una secuencia con maniquíes
"C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "%USERPROFILE%\Documents\Unreal Projects\DronIA_Cancha\DronIA_Cancha.uproject" -run=pythonscript -script="%CD%\importar_repeticion.py ..\..\03_SIMULACION_RL\salida_v17_todo\replay_v17.json 55 90" -unattended -nopause

:: 2. renderizar (abre el editor, saca los cuadros y se cierra solo)
ejecutar_en_unreal.bat renderizar.py /Game/DronIA/Secuencias/Rep_replay_v17_salida_v17_todo_55-90s %USERPROFILE%/Videos/dron_ia/clip
```

No cierres la ventana de Unreal a mano mientras renderiza: se corta. Para unir los cuadros en un MP4:
`blender\unir_video.py` (ver `_LEEME.md`). La galería de posturas se arma con `galeria_posturas.py` (hace un
`replay_v17.json` sintético) y se importa y renderiza igual.

---

## Opcional más adelante: personas con cara y ropa (MetaHuman + animaciones de Fab)

Solo si quieres que el video se parezca más a un juego. **No hace falta para el proyecto de grado.** Son ≈ 1 hora, casi
todo esperando descargas, y necesita tu cuenta de Epic (Claude no crea cuentas ni inicia sesión por ti).

1. **MetaHuman Creator Core Data.** En el *Epic Games Launcher*: *Unreal Engine → Biblioteca → ▾ junto a Unreal 5.8 →
   Opciones* y marca "MetaHuman Creator Core Data" (el nombre puede variar un poco).
2. **Animaciones.** En el editor: *Ventana → Fab*, inicia sesión con tu cuenta de Epic y busca **"Game Animation Sample
   Project"** (Epic Games, gratis) → "Add to Project" → DronIA_Cancha. Antes de usar algo de Fab, anota su licencia en
   `unreal/LICENCIAS.md`. Nada de Fab se sube al repositorio.
3. **Crear 2 MetaHumans** (`MH_Ladron`, `MH_Civil`): en `Content/DronIA`, clic derecho → MetaHuman → MetaHuman Character;
   estatura cercana a 1.72 m; el ladrón con ropa oscura y el civil con ropa clara; "Assemble". La RTX 3050 tiene 6 GB (Epic
   pide 8): si se pone lenta, baja la calidad de la vista (Scalability → Medio) y avisa.
4. Dile a Claude **"MetaHumans listos"**: cambia los maniquíes por tus MetaHumans (las animaciones se pasan de un esqueleto al otro
   con "retargeting") y vuelve a sacar el video.

## Si algo sale mal

| Pasa esto | Haz esto |
|---|---|
| Unreal se cierra al abrir el proyecto | No lo reabras diez veces; avísale a Claude con el texto del error (carpeta `Saved\Logs` del proyecto) |
| "Falta un complemento" | Dile que sí a habilitarlo y reiniciar el editor |
| Las personas salen como cilindros | Falta `Content/Characters/Mannequins` o `unreal/_cache/maniquies.json`: Claude repite el paso 0 |
| Se acaba el disco | Cada MetaHuman completo pesa varios GB; hay 280 GB libres al 17-oct |
