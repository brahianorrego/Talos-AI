# Plan del repositorio nuevo en GitHub (Fase E)

> **Resuelto (22-oct-2026):** el repositorio se publicó como `Dron-IA-Vigilancia` y Brahian lo renombró a **`Talos-AI`** (`github.com/brahianorrego/Talos-AI`). El resto de este plan es el original del 16-oct.

Preparado el 2026-10-16. **No se crea ni se sube nada sin que Brahian lo confirme en el chat.** El repo es público.

## 1. Nombre (decide Brahian)

| Opción | Por qué |
|---|---|
| **`Dron-IA-Vigilancia`** (recomendado) | Dice qué hace el plus sin sonar a "tesis" |
| `Dron-IA-Deteccion-Evasion` | Calca el objetivo del comité (el mínimo) |
| `Cuadricoptero-IA-USB` | Neutro e institucional |

## 2. Cómo se arma (recomendación)

**Repositorio nuevo con historia limpia** (un primer commit con la carpeta organizada) y el viejo `Tesis-IA-Drone`
**se conserva tal cual** como archivo histórico, enlazado desde el README nuevo. Motivos: la estructura 01-08 no
existe en el historial viejo, el historial viejo pesa por los cambios de `entorno.py` y así no se arrastra nada privado
que se haya colado antes. La etiqueta `v10-master-759M` y su Release (12 MB de modelos) **se quedan en el repo viejo**
y se enlazan.

Alternativa (si Brahian quiere un solo repo): seguir en `Tesis-IA-Drone` con una rama `organizacion` que mueva todo a
01-08. Más trabajo y el nombre sigue diciendo "Tesis".

## 3. Qué sube y qué no

| Sube | No sube (`.gitignore`) |
|---|---|
| `README.md`, `CLAUDE.md`, guías, `INDICE_NOMBRES.md`, `docs/` | `07_DOCUMENTO_PROYECTO_DE_GRADO/` (Word, PDFs del comité) |
| `01_MINIMO_INDISPENSABLE/` (código, informes, `decision.json`/`.pkl`, huellas) | `01_MINIMO_INDISPENSABLE/registros_campo/` y cualquier `datos_campo/` (fotos y video de personas) |
| `02_JETSON_A_BORDO/` (ya viene con `<NUMERO_DE_SERIE>` e `<IP-de-la-Jetson>`) | `.venv/`, `__pycache__/`, `*.log` |
| `03_SIMULACION_RL/` código, `tests/`, `informes/`, `herramientas/`, `index.html`, `minimo_tesis/replay/` (17 MB) | `modelos_master/`, `modelos_v*/`, `salida*/` (≈3.4 GB), `*.zip`, `*.pt` |
| `modelos/dron_politica.json` (864 KB, como hasta ahora) | `minimo_tesis/datos/*.npz` (57 MB: se regeneran con `entrenar_decisor`) |
| `05_`, `06_`, `08_` (diagramas, capturas, fotos **sin personas**) | `_memoria_claude/`, `.claude/settings.local.json`, `_copia_log.txt` |
| `.claude/agents/`, `.claude/skills/cierre-sesion/` | `_archivo_versiones/modelos_y_salidas/` (1.6 GB) |
| `_archivo_versiones/codigo/` (versiones viejas del código, 4.3 MB; sin los `.log`) | |

Limpiar antes del primer commit las rutas con la carpeta de usuario de Windows en `CLAUDE.md` y
`DEMOSTRACION_PARA_EL_INGENIERO.md` (hecho el 2026-10-16: ahora usan `$HOME\Desktop\...`). Luego repetir la búsqueda de secretos
(IPs, `password`, seriales, rutas de usuario, nombres de hotspots, nombres de redes WiFi) sobre lo que `git add` vaya a incluir.

## 4. Portada (`README.md`) · índice y de dónde sale cada imagen

| Sección | Imagen | ¿La tenemos? |
|---|---|---|
| Banner: el dron | Foto del dron armado (de lado, con gimbal y LiDAR) | **Falta: pedir a Brahian** |
| Qué problema resuelve | Captura del visor 3D con el ladrón detrás del muro | Se genera con el visor |
| La misión en dos fases | Diagrama tránsito → zona de IA; foto de los paneles de la U | `08/paneles_de_exposicion_universidad.png` ✔ |
| Arquitectura Percepción → Decisión → Control | `08/diagramas/01_arquitectura.png`, `08_funcional.png` | ✔ (traídos de la rama del documento) |
| Conexiones del hardware | `08/diagramas/09_conexiones.png` | ✔ |
| Mínimo indispensable | `02_estados.png`, `03_experimento.png`, tabla del protocolo, `minimo_tesis_decisor_curvas.png` | ✔ |
| Por qué IA y no solo reglas | `04_porque_ia.png`, `06_caja_negra.png`, `07_caja_transparente.png` | ✔ |
| Las redes | `08/redes/*.png` (de `ver_redes.py`) | ✔ |
| Paso a paso físico (pasos 0-7) | Fotos: Jetson en el dron, cableado TELEM2, gimbal + TF03, Mission Planner, prueba en banco, carrito del paso 4 | **Faltan: pedir a Brahian** |
| Cámara real | Captura de `visor_web.py` con la caja de YOLO (sin cara reconocible o con permiso) | **Falta** |
| Plus: IA de refuerzo | Capturas del visor por nivel, gráfica de aprendizaje desde `salida/metricas.json` | Se generan |
| Historial V1 → V17 | Tabla (de `BITACORA.md` y `DECISIONES.md`) | Texto ✔ |
| Variantes de hardware | `08/pan_tilt_servos.png` y renders de las piezas | Parcial |
| Cómo reproducirlo | Comandos de `CLAUDE.md` | ✔ |
| Créditos | Brahian (autor), Tania (documento), Universidad de San Buenaventura | ✔ |

## 5. Ramas, etiquetas y modelos

- `main` limpia con lo de arriba. Una rama por trabajo nuevo (`v17-refuerzo`, `visor-v16`, `variantes-hardware`) y
  Pull Request.
- V16 (`origin/v16-simulacion`, 7 commits; `origin/v16-visor`, 6 commits: visor modular en `simulacion/visor/`,
  texturas CC0, `test_v16.py`): **se trae solo si Brahian aprueba**, después de revisarla en local.
- Modelos: Release `v17-...` con `ultimo.zip` y algunos checkpoints (decenas de MB); la copia completa en Google Drive.
- `docs/PARA_TANIA_ESTADO.md`: versión pública del estado; la skill `/cierre-sesion` lo actualiza al cerrar.

## 6. Pasos (cada uno con confirmación de Brahian donde dice ✋)

1. Brahian elige nombre y forma (sección 1 y 2) ✋.
2. Escribir `.gitignore`, limpiar rutas, `git init` **local** y primer commit local. Mostrar `git status` y la lista de
   archivos que entrarían, con tamaños.
3. Brahian pasa las fotos que faltan (sección 4) a `08_EVIDENCIA_Y_DIAGRAMAS/fotos/`; se revisan una por una
   (nada de caras sin permiso, placas, pantallas con IPs o redes WiFi).
4. README completo con las imágenes; revisarlo en local ✋.
5. `gh repo create` público y `git push` ✋ (dos confirmaciones separadas).
6. Release de modelos ✋.

## 7. Lo que Brahian debe aprobar antes del primer push (19-oct)

El README ya trae la sección del plus con los resultados de la V17, las capturas y la ruta de búsqueda, **solo en local**
(commit sin push). Antes de subir, Brahian decide:

1. ✋ **Nombre y forma del repositorio** (secciones 1 y 2): sigue pendiente.
2. ✋ **Las 7 imágenes nuevas** de `08_EVIDENCIA_Y_DIAGRAMAS/capturas/` (`unreal_partida_3000`, `unreal_maniquies_ladron_corriendo`,
   `unreal_vuelo_cruce`, `estacion_modo_dron`, `estacion_modo_3d`, `dron_real_lado`, `v17_cancha_arriba`): las revisé una por
   una en miniatura y son de la simulación o del modelo 3D, sin personas reales, caras, IPs ni redes. Dos detalles para ti:
   `unreal_vuelo_cruce` muestra el **campus de la universidad** dibujado desde medidas de Google Earth (decide si quieres
   mostrar el lugar real); y el README solo usa 5 de las 7 (`unreal_vuelo_cruce` y `v17_cancha_arriba` quedan sin enlazar).
3. ✋ **Las cifras del plus.** Son honestas e incluyen las malas: la política V17.2 supera a "solo reglas" y empata con "siempre
   subir" en la cancha de prueba, y en la cancha real queda por debajo de "siempre subir". Las filas "afinado" y "ruta de Brahian"
   siguen **pendientes** hasta que termine la simulación de la noche: no subir hasta llenarlas o quitarlas.
4. ✋ **D-069** (que la red decida tras perder al ladrón) toca la regla dura 3: confirmar por escrito antes de describirla como
   política del plus.
5. ✋ **Los paneles** (~1.5 × 2.2-2.3 m) son medidas dichas por Brahian, no medidas con cinta: el README lo dice así; actualizarlo
   cuando se midan.
6. ✋ **Videos y modelos de Unreal:** no suben (pesan; viven en `Videos\dron_ia\`). Si quieres un video corto en la portada, se
   comprime a ≤ 10 MB y se revisa cuadro por cuadro.
7. Repetir antes del push la búsqueda de secretos y rutas de usuario sobre lo que `git add` incluya; en este commit ya revisé el
   README y los documentos nuevos.
