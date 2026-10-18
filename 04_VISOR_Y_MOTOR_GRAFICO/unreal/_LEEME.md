# Unreal Engine 5.8 · la cancha realista (fase 1 de PLAN_UNREAL.md)

El proyecto **DronIA_Cancha** vive en `Documentos\Unreal Projects\DronIA_Cancha\` (fuera del repositorio: pesa mucho).
Aquí están sus scripts de Python y una copia de su `.uproject` (`proyecto/`). **Guía para Brahian: `../GUIA_BRAHIAN_UNREAL.md`.**

| Archivo | Qué hace |
|---|---|
| `dronia_ue.py` | Funciones comunes: de la simulación (m, y al norte) a Unreal (cm, y a la derecha), materiales, cancha, V de paneles (1.5 × 2.25 m, D-066), dron, cielo y luz |
| `crear_cancha.py` | Arma el nivel `/Game/DronIA/Mapas/Cancha_V17`. Si ya existe, no lo toca (ahí van los árboles y MetaHumans de Brahian) |
| `importar_repeticion.py` | Convierte una repetición `foto()` (JSON) en una Level Sequence: dron, personas, paneles de esa partida y cámara de cine |
| `renderizar.py` | Renderiza una secuencia a PNG de 1080p con Movie Render Queue |
| `ejecutar_en_unreal.bat` | Abre el editor con el proyecto, corre un script y espera a que termine (`.bat` porque Windows tiene desactivados los `.ps1`) |
| `init_unreal.py` | Lo corre Unreal al arrancar; si hay una orden en `DRONIA_ORDEN`, la ejecuta ya con el editor cargado |

**Configuración del proyecto que no está en el repositorio** (en `Config\DefaultEngine.ini` de DronIA_Cancha): mapa por defecto
`/Game/DronIA/Mapas/Cancha_V17` y, en `[/Script/PythonScriptPlugin.PythonScriptPluginSettings]`, `+AdditionalPaths` con la ruta
de esta carpeta `unreal/` (así Unreal encuentra `init_unreal.py` y los módulos). Si se mueve el repositorio, se cambia esa ruta.

## Lo aprendido al probarlo (para no repetirlo)

- `-ExecutePythonScript` **cierra el editor al terminar el script** y corta el render ("PIE Ended while Movie Pipeline was still
  active"). Por eso se usa `init_unreal.py` + `DRONIA_ORDEN`.
- La variable del ejecutor de renderizado tiene que ser **global**; si no, Python la borra y se corta.
- Sequencer escribe escala 1 en lo que mueve: si la pieza raíz de un actor con hijos tiene otra escala, los hijos salen
  deformados (el dron salía gigante). La raíz del dron no tiene forma ni escala.
- El callback de "render terminado" recibe exactamente 2 argumentos.
- Desde Git Bash los argumentos que empiezan con `/Game/...` se convierten en rutas de Windows (`MSYS_NO_PATHCONV=1`).

## Medido (Unreal 5.8.3, RTX 3050 de 6 GB)

Abrir el editor y renderizar: ≈ 35-70 s por corrida (arranque incluido). Un cuadro de 1920 × 1080 con 4 muestras temporales:
unos 3-4 s. Secuencia de 30 s (721 cuadros a 24 cps): ≈ 40-50 min **estimados** (no se renderizó completa). El primer arranque
del proyecto compila shaders (varios minutos).

## Estado

Listo: cancha, V, dron provisional, personas **provisionales (cilindros)**, secuencia desde cualquier repetición V17, render y
MP4 (probado con 24 cuadros). Falta: MetaHumans con sus animaciones (guía, pasos 3-4), árboles y pasto de Fab, modelo del dron
real, la fase 2 en vivo (`puente_unreal.py`) y la fase 3 (Pixel Streaming).
