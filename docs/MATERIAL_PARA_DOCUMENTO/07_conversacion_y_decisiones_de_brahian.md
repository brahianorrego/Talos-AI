# 07 · Lo que pidió y corrigió Brahian (línea de tiempo)

Fuente: la conversación de la sesión del Coordinador (`...\.claude\projects\C--Users-Brahi-Desktop-Claude\6f0a00e4-...jsonl`, 42 mensajes suyos con texto) y `docs/DECISIONES.md`.
Las horas del registro están en UTC; la hora de Colombia es UTC−5. Solo hechos con fecha. Se omiten datos de red, correos, claves y direcciones. Las citas son cortas y textuales.
Lo que no consta en esa conversación se dice así.

## Lo que pidió

| Fecha (UTC) | Qué pidió o dijo | Fuente |
|---|---|---|
| 17-oct 02:37 | Ejecutar la guía de migración a la carpeta definitiva `Dron-IA-Proyecto`, que "ya existe y está a medias": verificarla | conversación |
| 17-oct 04:03 | Autoriza un GitHub "impecable, super llamativo, bien visual, que la gente quiera entrar y ayudarme"; el pesaje de 2 371 g y lo físico se hacen "mañana sábado" | conversación |
| 17-oct 04:19 | Queja: sigue viendo "un montón de carpetas y de cosas que no entiendo", nombres que no se ven bien y documentos en `.md` en vez de PDF o Word; pide una guía visual como la de GitHub y que se mencione la nueva interfaz con motor gráfico | conversación |
| 17-oct 04:34 | Reparte el trabajo: la parte física y el mínimo siguen en la cuenta de Tania; en esta, la simulación y el plus | conversación; `docs/EQUIPO_Y_SESIONES.md` |
| 18-oct 17:15 | Se acerca al límite de uso diario ("todo se pausa"); cierra la sesión y pide un prompt para que la cuenta de Tania revise cómo se organiza lo que lleva la Jetson, solo para el mínimo | conversación |
| 19-oct 06:18 | "Me costó más de un día y no llegué a la prueba física": se quedó reiniciando la Jetson desde cero. Pide seguir "con todos los agentes" toda la noche | conversación; `docs/HISTORIAL_PRUEBAS_FISICAS.md` |
| 19-oct 15:57 | Pregunta si el equipo trabajó o "se quedó toda la noche quieto" | conversación |
| 19-oct 16:39 | **Ruta de búsqueda como consejos, no reglas duras:** 360° para ubicar los paneles y hacer un mapa de puntos, luego buscar detrás del panel | conversación; `docs/RUTA_BUSQUEDA_BRAHIAN.md` |
| 20-oct 06:26 | "De ahora en adelante las simulaciones las vas a hacer con el TF03 fijo, y en el pan-tilt solo la CSI y el TF-Luna" | conversación; D-075 |
| 20-oct 06:27 | Se va a dormir y pide estar pendiente "para que no se pierda el tiempo" | conversación |
| 20-oct 14:44 | Pide el avance de todos, el porcentaje, cómo va la lógica de la simulación y verlo todo en tiempo real | conversación |
| 20-oct 16:24 | Pide una aplicación para manejar el dron desde un mapa visto desde arriba, con un círculo para rotarlo y una flecha de frente, y ver cámaras y sensores | conversación; modo Enseñar (`81d71b2`) |
| 20-oct 23:18 | Pide enseñar por ruta en el mapa y poder volar el dron con el teclado, "como un juego" en el motor gráfico | conversación; `docs/ORDENES_BRAHIAN_20OCT.md` §G |
| 20-oct 23:40 | "La prioridad es dejar listo el motor gráfico con todo"; pide un mapa de teclas y un pantallazo, que no había visto | conversación |
| 21-oct 03:33 | Se abrió Epic Games y no sabía qué descargar de Unreal | conversación |
| 21-oct 03:40 | Pide confirmar qué correcciones hizo la cuenta de Tania | conversación |
| 21-oct 03:50 | **Altura del mínimo: 2 metros**, la altura donde el LiDAR alcanza a medir a una persona de 1.70 a 1.72 m | conversación; D-081 |
| 21-oct 03:53 | La simulación debe ser **de día**; las fotos de la universidad (de noche) son solo referencia de la distribución | conversación; D-081 |
| 21-oct 04:00 | Autoriza trabajar toda la noche, dar los permisos y descargar lo necesario para no parar "por un mensaje o por una descarga" | conversación |

## Lo que corrigió

| Fecha | Corrección | Fuente |
|---|---|---|
| 19-oct | Que la búsqueda sea guía y no regla dura: la red puede mejorarla | conversación; `docs/ORDENES_BRAHIAN_20OCT.md` §C |
| 20-oct | **G es el mínimo y H es el plus** (no "el dron de hoy" y "el de la meta"); en el plus, TF03 fijo y TF-Luna con la CSI en el pan-tilt | D-074, D-075 |
| 20-oct | **A 2 m el LiDAR pasa sobre la cabeza**: de ahí la altura base de 2.0 m y la subida a 3.30 m solo si hay alguien a ~4 m o menos | D-080, D-081; `docs/ORDENES_BRAHIAN_20OCT.md` §D |
| 20-oct | Paneles: 2.30 × 1.50 × 0.05 m, con las V abiertas hasta 175° y giratorias | D-076; `docs/ORDENES_BRAHIAN_20OCT.md` §B |
| 20-oct | Quitar el vuelo entre canchas, un solo escenario, árboles realistas, quitar el botón Dron Mínimo/Plus | `docs/ORDENES_BRAHIAN_20OCT.md` §F |
| 20-oct | **Mezcla B0/B5':** los archivos `d_r3_b0` y `d_r5_b0` eran en realidad B5'; el Arquitecto corrigió su mensaje | `docs/PROGRESO_V17.md`; ver `02_errores_y_lecciones.md` |

## Lo que frenó o enredó el trabajo (con fecha)

- **Uso diario agotado:** 18-oct 17:15 ("todo se pausa") y varias sesiones cortadas por el límite el 19 y el 20-oct (avisos en esta conversación). Brahian pidió que no se parara por pedir permisos.
- **Una noche sin avance** (19-oct 15:57): Brahian preguntó si el equipo se había quedado quieto. Los registros de ese turno no explican por qué; no hay más fuente.
- **Permisos y descargas** (21-oct 04:00): Brahian autorizó aceptar permisos y bajar herramientas. Epic Games/Unreal lo confundió (21-oct 03:33).
- **Commits cruzados entre sesiones:** el 20-oct el Arquitecto arrastró por error en un commit archivos de otras sesiones y lo rehizo (commit `7b55e8f` reemplaza al anterior). Fuente: `git log` y el aviso al Coordinador.
- **Cifras de cuadros por segundo:** el panel interno de la app con la ventana oculta da ~1 cps y no sirve para medir; las cifras válidas son las de Chrome visible (`04_VISOR_Y_MOTOR_GRAFICO/mediciones/MEDICION_FPS_V16.md`). La medición de Unreal en vivo no existe todavía.
- **Documentación excesiva:** Brahian pidió "menos documentos" (20-oct, según el Coordinador). No consta en los mensajes que extraje; viene de las instrucciones del Coordinador.
