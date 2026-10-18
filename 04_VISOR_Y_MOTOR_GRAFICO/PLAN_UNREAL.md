# Plan Unreal Engine 5 · la cancha realista (D-065)

Sesión Visor, 2026-10-17. Brahian pidió "algo similar a GTA 5" y rechazó el video de Blender con Quaternius. D-065 decide:
**el mundo 3D realista va en Unreal Engine 5**; la **estación de tierra** sigue siendo web (`estacion/`, la que irá en la
Jetson). La simulación y el entrenamiento siguen en Python/NumPy: Unreal **solo dibuja** lo que dice `foto()`.

## 1. Lo que hay que saber antes (con fuentes)

| Dato | Valor | Fuente |
|---|---|---|
| Versión a instalar | **Unreal Engine 5.8** (salió el 17-jun-2026, con su arreglo 5.8.1). Epic dice que es la última versión grande de UE5; después viene UE6 | [Foro de Epic: UE 5.8 Released](https://forums.unrealengine.com/t/unreal-engine-5-8-released/2729274), [State of Unreal 2026](https://www.unrealengine.com/news/state-of-unreal-2026-top-news-from-the-show) |
| Requisitos de Unreal (recomendado por Epic) | 4 núcleos a 2.5 GHz o más, **32 GB de RAM**, tarjeta DirectX 11/12 con **8 GB o más** | [Especificaciones de Unreal (Epic, español)](https://dev.epicgames.com/documentation/unreal-engine/hardware-and-software-specifications-for-unreal-engine?lang=es-ES) |
| Requisitos para crear MetaHumans dentro del editor | 16 núcleos, **32 GB de RAM**, RTX 3070 o mejor con **8 GB** | [Requisitos de MetaHuman (Epic)](https://dev.epicgames.com/documentation/metahuman/metahuman-hardware-requirements-in-unreal-engine) |
| MetaHuman Creator | Desde la 5.7 funciona dentro del editor, como complemento | misma fuente |
| Tamaño de la instalación | **Sin cifra oficial**; informes de usuarios: ~25-55 GB solo el motor (más los proyectos). El lanzador muestra el número real antes de instalar | [PC Gamer](https://www.pcgamer.com/au/ue5-unreal-engine-5-game-sizes), [foro Planetside](https://planetside.co.uk/forums/index.php/topic,30270.0.html) |
| Conexión por red sin programar en C++ | Complemento **Remote Control API**: servidor WebSocket dentro de Unreal en `ws://127.0.0.1:30020` que acepta mensajes JSON para cambiar propiedades y llamar funciones | [Remote Control API · WebSocket (Epic)](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-api-websocket-reference-for-unreal-engine) |

**Este portátil** (medido, `mediciones/MEDICION_FPS_V16.md`): i5-12450HX (8 núcleos), **16 GB de RAM**, **RTX 3050 de 6 GB**
(45 W), 283 GB libres. **Queda por debajo de lo que Epic recomienda** (32 GB y 8 GB). Unreal sí abre y funciona, pero:

- crear MetaHumans dentro del editor va a ir lento (se hace una vez por personaje y se guarda);
- en el visor del editor, con Lumen y MetaHumans, hay que esperar **pocos cuadros por segundo** con calidad media (sin
  medir: se mide al instalar);
- por eso el camino principal es el **video de cine** (cada cuadro puede tardar lo que haga falta), y "en vivo" queda
  como segunda fase, con calidad recortada.

## 2. Pasos exactos para Brahian (instalación: lo hace él)

Necesita una cuenta de Epic y permiso de administrador; Claude no crea cuentas ni instala con permisos de administrador.

1. **Espacio:** dejar libres al menos **120 GB** en C: (motor + proyecto + MetaHumans + caché). Hoy hay 283 GB.
2. **Cuenta de Epic:** crearla en https://www.epicgames.com (gratis). Si ya la tiene, iniciar sesión.
3. **Lanzador:** bajar el **Epic Games Launcher** desde https://store.epicgames.com/download, instalarlo e iniciar sesión.
4. **Motor:** en el lanzador, pestaña **Unreal Engine → Biblioteca → (+) junto a "Versiones del motor"** y elegir **5.8.x**
   (la más nueva de la 5.8). En **Opciones**, antes de instalar:
   - **dejar marcado:** el núcleo del motor y "Contenido de inicio" (Starter Content);
   - **desmarcar:** plataformas de destino que no se usan (Android, iOS, Linux, TVOS), "Símbolos de depuración del editor"
     (pesan decenas de GB).
   - Anotar el tamaño que muestra el lanzador y avisarle a Claude (para corregir este plan).
5. **Proyecto:** abrir Unreal → **Juegos → En blanco**, tipo **Blueprint** (no C++), calidad **Máxima**, **sin** contenido de
   inicio, **sin** trazado de rayos. Nombre: `DronIA_Cancha`. Ubicación: `Documentos\Unreal Projects\` (**fuera del
   repositorio**: un proyecto de Unreal pesa decenas de GB y el repositorio es público).
6. **Complementos** (Editar → Complementos, buscar cada uno, marcar y reiniciar el editor):

   | Complemento | Para qué |
   |---|---|
   | **Python Editor Script Plugin** | Correr los scripts de Claude dentro de Unreal (importar repeticiones) |
   | **Editor Scripting Utilities** y **Sequencer Scripting** | Que esos scripts creen actores y secuencias |
   | **Movie Render Queue** (y **Movie Render Graph**) | Renderizar el video de cine |
   | **MetaHuman** (MetaHuman Creator) | Crear el ladrón y los civiles dentro del editor |
   | **Remote Control API** y **Remote Control Web Interface** | Fase 2: recibir la simulación en vivo por WebSocket (puerto 30020) |
   | **Pixel Streaming 2** (opcional) | Fase 3: ver la imagen de Unreal dentro de la estación web |

7. **Contenido gratis de Fab** (el mercado de Epic, dentro del editor: Ventana → Fab; con la misma cuenta):
   - **Game Animation Sample** de Epic: cientos de animaciones para el esqueleto de UE5 (el mismo de los MetaHumans):
     caminar, correr, agacharse, saltar. **Licencia: revisar en la ficha** antes de usar.
   - Árboles, pasto y cancha: elegir paquetes **gratuitos** de Fab de vegetación realista, y **anotar su licencia** en
     `04_VISOR_Y_MOTOR_GRAFICO/unreal/LICENCIAS.md`. Nada de Fab se sube al repositorio público.
8. **MetaHumans:** en el editor, crear 2 personas (ladrón y civil) con ropa de calle, como colombianos de la estatura del
   modelo (1.72 m ± 0.07, `entorno.py`), y guardarlas en el proyecto. Usar el nivel de detalle **LOD 1-3** (el 0 es
   demasiado para 6 GB).
9. **Cielo y luz:** en el nivel, usar el "Mezclador de luz ambiental" (Window → Env. Light Mixer): Sky Atmosphere,
   Sky Light, Directional Light (sol) y Volumetric Clouds. **Lumen en calidad media**.
10. Avisarle a Claude (por el Supervisor o directo): "Unreal instalado, proyecto en ...". Desde ahí sigue Claude.

## 3. Cómo se conecta con la simulación y con la estación web

```
03_SIMULACION_RL (Python/NumPy)          04_VISOR_Y_MOTOR_GRAFICO
  entorno.py ── foto() ──► en_vivo.py ──SSE:8767──► estacion/ (web, la de la Jetson)
                     │                     └──► puente_unreal.py ──WebSocket:30020──► Unreal (Remote Control API)   [fase 2]
                     └──► repetición .json ──► unreal/importar_repeticion.py (Python dentro de Unreal) ──► Sequencer ──► video   [fase 1]
  Unreal ──Pixel Streaming──► panel "Mundo realista" dentro de la estación web   [fase 3, opcional]
```

- **Fase 1 · video de cine (lo principal, sin depender de la velocidad del portátil).** `unreal/importar_repeticion.py`
  (lo escribe Claude) corre dentro de Unreal (Herramientas → Ejecutar script de Python), lee una repetición `foto()`
  (`dt` = 0.1 s) y crea una **Level Sequence**: trayectoria del dron, de cada persona y de la cámara; por cada persona, una
  pista de animación que cambia según `pos` (de pie, agachado, recostado, gateando), la velocidad, `salto` y `civ`. Se
  renderiza con **Movie Render Queue** a 1080p (un cuadro puede tardar segundos; un minuto de video, unas horas).
  Las paredes en V salen de `paneles`, con su alto real.
- **Fase 2 · en vivo.** `puente_unreal.py` (lo escribe Claude) se conecta a `en_vivo.py` y, por cada cuadro, manda a
  Unreal un mensaje JSON a `ws://127.0.0.1:30020` que llama a una función de un Blueprint `BP_Mundo` ("AplicarFoto", con
  el cuadro como texto). Ese Blueprint mueve el dron y las personas y elige la animación. Calidad recortada para que vaya
  fluido en la RTX 3050. **La estación web no cambia**: sigue leyendo `en_vivo.py` como hoy.
- **Fase 3 · opcional.** Pixel Streaming manda la imagen de Unreal al navegador y la estación la muestra en un panel más
  ("Mundo realista"), con las mismas ventanas movibles.

**Qué NO hace Unreal:** no decide nada, no entrena, no cambia la física. Si Unreal no está abierto, todo lo demás
(simulación, entrenamiento, estación) funciona igual.

## 4. Animaciones (lo que pide `foto()`)

| Lo que pasa en la simulación | Campo | Animación en Unreal |
|---|---|---|
| Quieto, caminar, trotar, correr | velocidad de `pers[k].v` | Game Animation Sample (locomoción) |
| Agacharse y caminar agachado | `pos` 0↔1, `pt` | Game Animation Sample (crouch) |
| Recostado contra el panel, asomarse | `pos` = 2, `mira` | Buscar en Fab; si no hay, pose fija + giro de cabeza |
| Gatear | `pos` = 3 | Buscar en Fab ("crawl"); es la que más cuesta conseguir |
| Saltar para agarrar el dron (brazo extendido) | `salto` (fase y mano) | Salto del Game Animation Sample + IK del brazo hacia `salto.mano` (Control Rig) |
| Civil: mira el dron, graba con el celular, esquiva, se va | `civ`, `graba` | Locomoción + "mirar arriba" (Look At) + celular en la mano |

## 5. Orden de trabajo y tamaño

| Paso | Quién | Tamaño |
|---|---|---|
| Instalar Unreal, crear el proyecto, complementos, 2 MetaHumans | Brahian (pasos 1-10) | 1 tarde (descarga + MetaHumans) |
| `importar_repeticion.py`: cancha, V, dron y personas siguiendo la repetición | Claude | Mediano |
| Animaciones por postura y salto con IK | Claude + Brahian (elegir paquetes en Fab) | Mediano |
| Primer video de cine de la cancha V17 y comparación con el de Blender | Claude | Pequeño |
| Fase 2 en vivo (`puente_unreal.py` + `BP_Mundo`) | Claude | Mediano |
| Fase 3 Pixel Streaming en la estación | Claude | Pequeño, opcional |

## 6. Lo que no se pudo verificar desde aquí

- El tamaño exacto de la instalación y los cuadros por segundo reales en este portátil: se miden al instalar.
- Las licencias de los paquetes de Fab (incluido el Game Animation Sample): se revisan en cada ficha antes de usarlos.
- Si la Remote Control API mueve bien los actores durante el juego en el editor (PIE) o solo en el nivel del editor: se
  prueba en la fase 2; si no sirve, la alternativa es un complemento WebSocket de Fab.
