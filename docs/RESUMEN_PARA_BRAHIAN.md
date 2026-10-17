# Resumen para Brahian (noche del 16 al 17 de octubre)

Lo escribe el **Supervisor nocturno**. No aprueba nada: las sesiones solo siguen con lo que tú aprobaste
(D-049 a D-056). Lo más nuevo va arriba. Nada se ha subido a GitHub (sin `git push`).

---

## Revisión de las 2:42 a. m.

### Qué hizo cada sesión

- **Arquitecto:** entregó el plan V17 (commit `95f033d`). Midió que la IA de la V15 no aporta: custodia ≥ 60 s de
  11.3 % con la IA, 10.2 % con "siempre MANTENER" y 7.8 % al azar, en 256 partidas
  (`03_SIMULACION_RL/informes/diagnostico_v17_ia_aporta.md`). Anotó tus aprobaciones D-049 a D-056 (commits `db4063d` y
  `b5affbb`) y dejó abiertas D-057 y D-058 para ti (commit `8ba0aca`).
- **Simulación V17:** está en el paso E1, traer el código de la V16 a `03_SIMULACION_RL/`. Ya cambió `entorno.py`,
  `control.py`, `entrenar_master.py` y las pruebas, y guardó copias `_v15` en `_archivo_versiones/codigo/`. Todavía no
  ha hecho commit ni ha informado si pasan las 118 pruebas.
- **Visor y motor gráfico:** entregó su plan (commit `e2b69a3`). El visor V16 da 144 cuadros/s con la tarjeta RTX y
  24 con la Intel (`04_VISOR_Y_MOTOR_GRAFICO/mediciones/MEDICION_FPS_V16.md`). Recomienda seguir con three.js y usar
  Blender para el video. Revisó las licencias de `v16/`: no hay fotos de personas, los cielos son CC0 (Poly Haven),
  three.js es MIT y las texturas son propias (commit `5e8cde3`). **Lo pausé** porque había 3 sesiones trabajando a la vez
  y lo que le falta depende de tus decisiones.
- **Hardware y variantes:** entregó la matriz de variantes A-F (commits `ebc3b9f` y `a9d4c39`). El chequeo
  `validar_variantes.py` pasa en las 6. Está quieta: lo que le falta depende de ti o de la parte física.

### Espera a Brahian

1. **D-057 · Motor gráfico.** Opciones: (a) seguir con three.js (el visor V16) para la estación de tierra y usar
   Blender para el video realista; (b) Unreal 5; (c) Godot o Unity. **Recomendación del Visor: (a).** Unreal no va
   cómodo con 16 GB de RAM y 6 GB de video, y obligaría a empezar de cero (`04_VISOR_Y_MOTOR_GRAFICO/PLAN_MOTOR_GRAFICO.md`).
2. **D-058 · ¿El visor V16 (9.9 MB) entra a `main`?** El Visor **ya hizo el commit** (`3c38f66`) antes de que tú
   decidieras, pero no lo subió a GitHub. Opciones: (a) dejarlo; (b) deshacerlo con un commit que lo revierta.
   **Recomendación del Arquitecto: (a), sí entra,** después de revisar licencias y fotos. Esa revisión ya está hecha y
   salió limpia (`04_VISOR_Y_MOTOR_GRAFICO/_LEEME.md`). Si dices que sí, falta además traer `generar_texturas.py`.
3. **Hardware · ¿comprar o imprimir la variante D (pan-tilt) desde ya, como plan B?** Cuesta poco. La sesión no dejó
   recomendación (`05_HARDWARE_Y_VARIANTES/VARIANTES.md`, §8).
4. **Pedidos a la parte física, para cuando termine el mínimo:** pesar la BaseCam, el TF03 y la cámara USB; medir si
   el pod baja a −45° sin el TF03; anotar el color real de los paneles (afecta el alcance del TF-Luna). Están en
   `docs/PEDIDOS_A_LA_PARTE_FISICA.md`.

### Problemas

- **Cortes por el límite de uso:** las sesiones ya están activas otra vez, después del reinicio de las 2:20.
  A las 2:42 iba en 41 % del límite de 5 horas (se reinicia a las 7:20) y en 37 % del semanal.
- **3 sesiones trabajando a la vez** (el máximo es 2): pausé al Visor. Siguen Simulación V17 y el Arquitecto.
- **Commit del visor V16 antes de la decisión D-058:** queda como está hasta que decidas (punto 2 de arriba).
- Las piezas 3D (`.scad`) no se han compilado porque en el PC no está instalado OpenSCAD.
