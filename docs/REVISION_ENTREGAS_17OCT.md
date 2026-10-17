# Revisión de entregas · 17 de octubre

Arquitecto, a pedido del Supervisor. Revisé los commits del Visor (fd6b302, 931d90f, 59a10b7, f8300e1, 86b336d y 8a0e296)
y el de Hardware (096f304), buscando en el código y en la lista de archivos. **No abrí el video ni el visor en el
navegador.**

## Lo que está bien

1. **Regla dura 1 en el visor:** el gimbal se recorta a −45°..+15° antes de dibujarlo (`visor/util.js` y `dron.js:115`,
   con un comentario de la regla). En la vista del dron, el PWM usa la fórmula exacta `1500 + θ·500/45`
   (`vista_dron.js:10`).
2. **Repositorio público:** no hay rutas `C:\Users`, IPs ni claves en 04 ni en 05. Las capturas `.jpg` muestran personas
   3D del paquete, no fotos reales. El video quedó fuera del repositorio (`Videos\dron_ia\`).
3. **Licencias:** three.js MIT; cielos de Poly Haven y modelos de Quaternius, todos CC0, cada uno con su fuente en
   `recursos/LICENCIAS.md` y en el `_LEEME.md`. Los recursos pesan ~14 MB en total: razonable para Git.
4. **Simulación en vivo:** `en_vivo.py` solo escucha en `127.0.0.1`, no queda abierto a la red.
5. **Pestaña Dron:** usa `cmd` y `arb` de `foto()`, como se acordó con Simulación V17.
6. **Guía de Hardware:** está clara para Brahian. Explica las palabras raras (BEC, pitch), dice por qué y qué se
   descartó, y respeta el orden: nada se toca en el dron antes de los pasos 4-7 del mínimo. Dice que con el TF03 en
   otro lugar **hay que re-simular el mínimo**. Las piezas de la variante D tienen topes de plástico en −44° y +14°,
   1° por dentro de la regla dura. Los 7 STL están.
7. **Advertencia honesta en la guía:** las medidas del servo y la tolerancia de la impresora no están verificadas, y
   recomienda imprimir primero solo la plataforma y probar el servo. Correcto.

## Lo que hay que corregir o comprobar

8. **Mapeo del servo (variante D):** la guía no dice cómo se calibra el PWM del servo del pitch. La regla dura exige
   `pwm = 1500 + θ·500/45` sin ampliarlo. Un MG90D típico da ~11 µs por grado, que coincide, pero hay que **medirlo en
   banco** y escribirlo como paso 3 de la sección de pruebas: con PWM 1000 debe llegar a −45° y con 1667 a +15°. Si no
   coincide, se ajustan los parámetros del servo en la Pixhawk, no la fórmula. **Encargo para Hardware.**
9. **Humano en el lazo en la estación de tierra:** en la simulación en vivo, el "clic" lo hace el operador simulado
   del entorno. Eso está bien para simular, pero en la interfaz debe verse que **la confirmación es del operador** (un
   botón o un aviso "esperando confirmación") y no parecer automática. **Encargo para Visor, sin prisa.**
10. **Medición de cuadros por segundo:** el 134 cps con naturaleza se midió con la RTX. Que la guía de uso le recuerde a
    Brahian poner Chrome en "Alto rendimiento" (con la Intel da ~24). Ya está en `PLAN_MOTOR_GRAFICO.md`: basta con
    copiarlo a `ABRIR_EN_VIVO.bat` o al `_LEEME.md`.
