# Pedidos a la parte física (nube de Tania, vía Brahian)

Lo que la simulación y el plus necesitan medir en el dron real. **Nada de esto se hace antes de terminar los pasos 4-7
del mínimo indispensable**, salvo lo marcado "se puede ya" (no toca el montaje).

| # | Pedido | De quién | Para qué | Cuándo |
|---|---|---|---|---|
| 1 | Medir con cinta los paneles de exposición que se van a pedir prestados: alto, ancho de cada panel y cómo se unen | Arquitecto (D-051, D-066) | Cerrar `ALTO_PANEL_V17` (hoy 2.25 m según Brahian) y `ANCHO_PANEL_V17` (hoy 1.5 m) | Se puede ya, el día que se pidan |
| 2 | Pesar por separado la BaseCam, el TF03 con su cable y la cámara USB | Hardware y variantes (D-055) | Peso y centro de gravedad de las variantes C y D | Se puede ya (con el dron en el banco, sin desmontar si no hace falta) |
| 3 | Comprobar si el pod de la BaseCam baja a −45° **sin** el cable del TF03 | Hardware y variantes (D-055) | Decide entre la variante C y la D | Después del mínimo |
| 4 | Confirmar si la Jetson tiene el overlay para **dos** IMX219 (CAM0 y CAM1) y qué puerto serie de la Pixhawk está libre (¿TELEM1?) | Hardware y variantes | Cámara al piso y un posible TF-Luna como altímetro | Se puede ya (solo leer configuración) |
| 5 | Para el tránsito: elegir un árbol con la copa por encima de ~4.5 m, o que ante un árbol el mínimo solo frene | Arquitecto (plan V17, 3.3) | Subir a 3.30 m bajo una copa baja mete el dron entre las ramas | Antes de la prueba de la misión completa |
| 6 | Interruptor de la radio para activar la IA (propuesta: CH7; CH8 sigue siendo la parada de emergencia) | Arquitecto (D-053) | Fase 3 de la misión V17 | Cuando se programe el plus en la Jetson |
