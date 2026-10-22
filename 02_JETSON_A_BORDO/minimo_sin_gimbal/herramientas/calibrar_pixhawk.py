# -*- coding: utf-8 -*-
"""
Calibración de la Pixhawk por TELEM2 con el dron DESARMADO y SIN hélices. Parar antes el servicio (systemctl --user stop campo).
  calibrar_pixhawk.py accel     6 posiciones. En cada una el script escribe "POSICION n: ..." y espera el archivo /tmp/cal_listo
                                (se crea con `touch /tmp/cal_listo` cuando el dron ya está quieto en esa posición) y recién entonces confirma.
  calibrar_pixhawk.py brujula   calibración de brújulas a bordo (todas): hay que girar el dron en todos los ejes hasta ~100 %; guarda sola.
Escribe todo en la salida estándar (se puede lanzar en segundo plano con nohup > /tmp/cal.log).
"""
import os
import sys
import time

sys.path.insert(0, ".")
import config as C
from pymavlink import mavutil

LISTO = "/tmp/cal_listo"
NOMBRES = {1: "NIVEL: plano sobre su base, como vuela", 2: "LADO IZQUIERDO abajo (apoyado sobre su costado izquierdo)",
           3: "LADO DERECHO abajo (apoyado sobre su costado derecho)", 4: "NARIZ ABAJO (la cámara apuntando al suelo)",
           5: "NARIZ ARRIBA (la cámara apuntando al techo)", 6: "AL REVÉS: boca abajo, con la Jetson hacia la mesa"}
EST_BRUJULA = {4: "BIEN", 5: "FALLÓ", 6: "ORIENTACIÓN MALA", 7: "RADIO MALO"}

if len(sys.argv) < 2 or sys.argv[1] not in ("accel", "brujula"):
    raise SystemExit(__doc__)
m = mavutil.mavlink_connection(C.PUERTO_PIXHAWK, baud=C.BAUD_PIXHAWK, source_system=C.SYSID_COMPANION, source_component=C.COMPID_COMPANION)
hb = m.wait_heartbeat(timeout=8)
if not hb or hb.base_mode & 128:
    raise SystemExit("sin latido o el dron está ARMADO: no se calibra")
if os.path.exists(LISTO):
    os.remove(LISTO)
print("INICIO %s" % sys.argv[1], flush=True)

if sys.argv[1] == "accel":
    m.mav.command_long_send(m.target_system, 1, mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION, 0, 0, 0, 0, 0, 1, 0, 0)   # param5 = 1: acelerómetro, 6 posiciones
    t_fin = time.time() + 15 * 60
    ult_pos, t_conf = 0, 0.0
    while time.time() < t_fin:
        x = m.recv_match(blocking=True, timeout=1.0)
        if x is None:
            continue
        t = x.get_type()
        if t == "STATUSTEXT":
            print("Pixhawk: " + x.text, flush=True)
        elif t == "COMMAND_LONG" and x.command == 42429:                  # MAV_CMD_ACCELCAL_VEHICLE_POS
            pos = int(x.param1)
            if pos == 16777215:
                print("RESULTADO: CALIBRACION OK", flush=True)
                break
            if pos == 16777216:
                print("RESULTADO: CALIBRACION FALLÓ", flush=True)
                break
            if pos == ult_pos and time.time() - t_conf < 12:          # la Pixhawk repite la petición hasta procesar la confirmación: se ignora
                continue
            print("POSICION %d: %s" % (pos, NOMBRES.get(pos, "?")), flush=True)
            while not os.path.exists(LISTO) and time.time() < t_fin:
                time.sleep(0.3)
            if os.path.exists(LISTO):
                os.remove(LISTO)
            m.mav.command_long_send(m.target_system, 1, 42429, 0, pos, 0, 0, 0, 0, 0, 0)
            ult_pos, t_conf = pos, time.time()
            print("CONFIRMADA %d: mantenlo quieto unos segundos" % pos, flush=True)
    else:
        print("RESULTADO: tiempo agotado", flush=True)
else:
    m.mav.command_long_send(m.target_system, 1, 42424, 0, 0, 0, 1, 0, 0, 0, 0)   # DO_START_MAG_CAL: todas, sin reintento, guarda sola, sin autoreinicio
    t_fin = time.time() + 150
    informes, ultimo = {}, 0.0
    while time.time() < t_fin and len(informes) < 3:
        x = m.recv_match(blocking=True, timeout=1.0)
        if x is None:
            continue
        t = x.get_type()
        if t == "MAG_CAL_PROGRESS" and time.time() - ultimo > 3:
            ultimo = time.time()
            print("PROGRESO brújula %d: %d %%" % (x.compass_id, x.completion_pct), flush=True)
        elif t == "MAG_CAL_REPORT":
            informes[x.compass_id] = x
            print("INFORME brújula %d: %s  fitness %.1f  offsets %.0f %.0f %.0f" % (x.compass_id, EST_BRUJULA.get(x.cal_status, x.cal_status), x.fitness,
                  x.ofs_x, x.ofs_y, x.ofs_z), flush=True)
        elif t == "STATUSTEXT":
            print("Pixhawk: " + x.text, flush=True)
    print("RESULTADO: terminado (%d informes)" % len(informes), flush=True)
