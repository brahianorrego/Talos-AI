# Código del mínimo en la Jetson (sin gimbal), octubre de 2026

Es el código que corre hoy en la Jetson Orin Nano (JetPack 6.2.1) del dron: cámara CSI IMX219 y LiDAR TF03 fijos al chasis, sin gimbal y sin cámara USB.
La carpeta de al lado (`02_JETSON_A_BORDO/`) conserva el de la época del gimbal. Procedimiento completo para repetirlo: [`docs/PROCEDIMIENTO_REPLICABLE.md`](../../docs/PROCEDIMIENTO_REPLICABLE.md).

| Archivo | Qué hace |
|---|---|
| `registro_minimo.py` | Bucle principal: cámara + YOLO + LiDAR + Pixhawk, una fila por cuadro en `datos.csv`, video, panel (`--panel 8080`) y tomas (`--tomas`) |
| `panel_campo.py` | Servidor web de campo: `/` panel, `/persona`, `/calibrar`, `/alinear`, `/video?res=normal\|alta\|maxima`, `/datos`, `/toma/*` |
| `percepcion.py` | Cámara CSI por una tubería de `gst-launch` (`CamaraTuberiaGst`: cuadro grande para mostrar y cuadro de 640×480 para YOLO) |
| `geometria_lidar.py` | Dónde cae el rayo del LiDAR en la imagen según su distancia (paralaje entre LiDAR y cámara) |
| `calibrar.html` | Calibración del montaje: campo de visión, inclinación de la cámara y del LiDAR respecto al chasis (con el cabeceo de la Pixhawk), pasos 5 (persona) y 6 (suelo) |
| `lidar_tf.py`, `intervencion_banco.py` | Lectura del TF03; prueba de intervención por MAVLink en banco |
| `campo.service` | Servicio de usuario `systemd` que arranca todo al encender (borra el archivo de control de tomas) |
| `config.py` | Puertos, umbrales y ángulos del montaje. **Los seriales y puertos reales se ponen en la Jetson**: aquí van como `<NUMERO_DE_SERIE>` |
| `herramientas/` | Análisis de las tomas (`analizar_campo.py`, `geometria_desde_campo.py`, `resumir_tomas.py`), horas de trabajo, configuración y prueba de la Pixhawk y los motores |

Los ángulos de `config.py` (`CAMARA_PITCH_DEG`, `LIDAR_PITCH_DEG`) son **respecto al chasis** y provisionales (D-082); se recalibran con `/calibrar`.
