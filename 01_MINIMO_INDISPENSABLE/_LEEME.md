# 01 · Mínimo indispensable — CONGELADO

**Congelado el 2026-10-16.** Esta carpeta es una foto fija del mínimo indispensable. No se edita: si algo debe
cambiar, se cambia en `03_SIMULACION_RL/minimo_tesis/` (o en `02_JETSON_A_BORDO/`), se re-corre el protocolo y se
hace una foto nueva con fecha. `HUELLAS_SHA256.txt` permite comprobar que nada cambió.

## Qué es el mínimo

Lo que aprobó el comité ("Cambio de objetivos", 2026-09-01): el **piloto avanza en línea recta**; el sistema solo
interviene ante un **riesgo definido** (obstáculo por LiDAR o persona por YOLO) con **DETENCIÓN + ASCENSO VERTICAL**
hasta 3.30 m, y el operador puede retomar siempre (CH5 a ALT_HOLD; CH8 corta motores). También un modo estático.
Sin esquives laterales, sin navegación autónoma, sin la IA de refuerzo.

Dos IAs: **YOLO26n** detecta personas y el **decisor MLP** (capas de 32 y 16, `minimo_tesis/decision.json`) decide
CONTINUAR o DETENER_Y_ASCENDER dentro de la envolvente de reglas duras.

Resultado en simulación (`informes/minimo_tesis_protocolo.md`): 1300 vuelos, éxito 100 % [99.7, 100], 0 activaciones
falsas en 300. Decisor IA (`informes/minimo_tesis_decisor_ia.md`): activaciones innecesarias 44 → 30; en los mundos de
prueba, choques 39 → 28.

## Qué hay aquí

| Carpeta / archivo | Qué es |
|---|---|
| `PLAN_MINIMO_FISICO.md` | Plan del arquitecto: pasos 0-8 en el dron real y cómo grabar los datos |
| `minimo_tesis/` | Simulación del mínimo, el decisor (`decision.pkl`, `decision.json`) y sus datos |
| `informes/` | Protocolo del comité, condiciones degradadas y decisor IA (md, csv, png) |
| `pruebas/` | `test_minimo_tesis.py` y `test_decisor_ia.py` (se corren desde `03_SIMULACION_RL`) |
| `jetson_minimo/` | `registro_minimo.py` (pasos 1 y 4), `intervencion_banco.py` (paso 3) y `campo.py` (tomas desde el portátil) |
| `registros_campo/` | **Única carpeta que se escribe**: aquí van los datos del sábado (no van a Git si tienen personas) |

## Qué se hace el sábado (un paso a la vez)

1. **Resolver el WiFi de la Jetson** (el 13 de octubre no se conectó al hotspot del celular). Sin esto no hay SSH.
2. Ver la cámara en el visor web de la Jetson.
3. **Paso 4: tomas E0 a E6** con `campo.py` (dron sin hélices, en carrito o trípode a ~2 m; persona nunca a menos
   de 3 m). Escenarios en la sección 6 del plan.
4. Pendientes del banco: batería nueva (vigilar voltaje: aviso 14.4 V, desconectar a 14.0 V) y motores 3 y 4.
5. Después, en otras jornadas: paso 5 (modo sombra), paso 6 (vuelos, solo con autorización), paso 7 (protocolo).

## Qué NO se toca

- **El TF03 ni el gimbal** hasta terminar los pasos 4-7: el decisor se entrenó con el TF03 alineado a la cámara a −5°.
  Si se mueven, hay que re-simular el mínimo y repetir el protocolo.
- El pitch fijo (−5°, 1444 µs por AUX1), la altura de protección (3.30 m) y la lógica de `minimo_tesis/`.
- Nada de hélices hasta el paso 6.

## Comprobar que no cambió

```
cd 01_MINIMO_INDISPENSABLE
certutil -hashfile minimo_tesis\decision.json SHA256
```
y comparar con la línea de `HUELLAS_SHA256.txt` (o, en Git Bash: `sha256sum -c HUELLAS_SHA256.txt`).

En una copia bajada de GitHub faltan `minimo_tesis/datos/*.npz` (57 MB, no van a Git): esas 3 líneas saldrán como
"no se encontró"; se regeneran con `python -m minimo_tesis.entrenar_decisor` o se bajan de la Release.
