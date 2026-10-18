# Guía para Brahian · lo único que te toca hacer en Unreal

Claude ya hizo todo lo que se podía sin abrir el editor. **Te quedan 4 cosas** (≈ 1 hora, casi todo esperando descargas).
Antes de empezar, el resultado de lo ya hecho está en `mediciones/capturas/unreal_prueba_cuadro240.jpg`: la cancha con
las dos V de 90° (paneles de 1.5 × 2.25 m, D-066), el dron, el ladrón (cilindro rojo) y el civil (cilindro azul). Las
personas son cilindros **hasta que existan los MetaHumans**: eso es lo que sigue.

## Qué ya está hecho (no lo repitas)

- Unreal Engine **5.8.3** instalado (lo hiciste tú).
- Proyecto **DronIA_Cancha** creado en `Documentos\Unreal Projects\DronIA_Cancha\` (fuera del repositorio, porque pesa
  mucho), con los complementos activados: Python, Editor Scripting, Sequencer Scripting, Movie Render Queue,
  MetaHuman Creator y Remote Control.
- Nivel **Cancha_V17**: césped, líneas y arcos de la cancha de fútbol (90 × 60 m, por medir), las dos V a 10 m entre
  vértices, zona de IA de 30 × 30 m en la mitad este, sol, cielo, nubes y niebla.
- Scripts en `04_VISOR_Y_MOTOR_GRAFICO/unreal/`: crean la cancha, convierten **cualquier repetición de la simulación** en
  una secuencia de Unreal y la renderizan a 1080p. Probado: un cuadro de 1920 × 1080 tarda unos 4 s de render.

## Lo que te toca a ti

### 1. Abrir el proyecto (la primera vez tarda varios minutos)

Doble clic en `Documentos\Unreal Projects\DronIA_Cancha\DronIA_Cancha.uproject`. La primera vez Unreal compila
"shaders" (verás una barra de progreso); es normal, y con 16 GB de RAM puede tardar 10-20 minutos. Se abre en el nivel
**Cancha_V17**. Si pregunta por actualizar o convertir el proyecto, di que **no**; si pide guardar algo, di que sí.

### 2. Bajar el contenido de MetaHuman (una vez)

Unreal avisa en su registro que falta el contenido opcional de MetaHuman. En el **Epic Games Launcher**:
*Unreal Engine → Biblioteca → la flecha ▾ junto al botón de Unreal Engine 5.8 → Opciones* y marca
**"MetaHuman Creator Core Data"** (el nombre exacto puede variar un poco). Aplica y espera la descarga. *(Según la
documentación de Epic, ese contenido es un requisito para crear MetaHumans; no pude comprobar el menú en la 5.8.)*

### 3. Entrar a Fab y bajar las animaciones

En el editor: menú **Ventana → Fab** (o en el navegador, fab.com) e **inicia sesión con tu cuenta de Epic**. Busca
**"Game Animation Sample Project"** (Epic Games, gratis: más de 500 animaciones de caminar, correr, agacharse y saltar).
Botón **"Add to Project" / "Agregar al proyecto"** y elige **DronIA_Cancha**. Es grande: déjalo descargando.
**Antes de usar cualquier cosa de Fab, mira la licencia en su ficha y anótala** en
`04_VISOR_Y_MOTOR_GRAFICO/unreal/LICENCIAS.md` (Claude te ayuda a hacer ese archivo). Nada de Fab se sube al repositorio.

### 4. Crear los 2 MetaHumans (el ladrón y el civil)

En el **Content Browser** (abajo): entra a la carpeta `Content/DronIA`, clic derecho → **MetaHuman → MetaHuman
Character**. Ponle el nombre **MH_Ladron** y haz doble clic: se abre el creador.
- Elige una persona de las de ejemplo (la estatura debe parecerse a **1.72 m**), pelo y **ropa de calle**. El ladrón con
  ropa oscura y el civil con ropa clara, para distinguirlos en el video.
- Cuando termines, botón **"Assemble"** (ensamblar) o equivalente. Necesita internet: Epic hace parte del proceso en sus
  servidores.
- Repite con **MH_Civil**.
- Si el computador se pone muy lento (la RTX 3050 tiene 6 GB, Epic pide 8), baja la calidad de la vista del editor
  (botón de la esquina del visor → Scalability → Medio) y **avísale a Claude**: se prueba con modelos más livianos.

### 5. Avísale a Claude

Dile solo: **"MetaHumans listos"** (y si Fab o MetaHuman te pidieron algo raro, qué fue). Claude hace el resto:
cambiar los cilindros por tus MetaHumans, ponerles las animaciones según la postura, el salto y el civil que graba, y
sacar el primer video de la cancha para compararlo con el de Blender.

## Si algo sale mal

| Pasa esto | Haz esto |
|---|---|
| Unreal se cierra al abrir el proyecto | No lo reabras diez veces; avísale a Claude con el texto del error (carpeta `Saved\Logs` del proyecto) |
| "Falta un complemento" | Dile que sí a habilitarlo y reiniciar el editor |
| Fab no te deja iniciar sesión | Usa la misma cuenta del Launcher; si no, avísale a Claude |
| Se acaba el disco | Cada MetaHuman completo pesa varios GB; hay 280 GB libres al 17-oct |

## Comandos que usa Claude (por si quieres repetirlos)

Desde la raíz del proyecto, en una consola (CMD o PowerShell):

```
:: 1. convertir una repetición de la simulación en una secuencia (usa la última partida V17 si no das el archivo)
"C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "%USERPROFILE%\Documents\Unreal Projects\DronIA_Cancha\DronIA_Cancha.uproject" -run=pythonscript -script="04_VISOR_Y_MOTOR_GRAFICO\unreal\importar_repeticion.py" -unattended -nopause

:: 2. renderizar (abre el editor, saca los cuadros y se cierra solo); los cuadros 240 a 242 son una prueba de 3 cuadros
04_VISOR_Y_MOTOR_GRAFICO\unreal\ejecutar_en_unreal.bat renderizar.py /Game/DronIA/Secuencias/Rep_replay_v17_salida_v17_1 %USERPROFILE%/Videos/dron_ia/unreal 240 242
```

No cierres la ventana de Unreal a mano mientras renderiza: se corta. Para unir los cuadros en un MP4:
`blender\unir_video.py` (ver `_LEEME.md`).
