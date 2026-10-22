# -*- coding: utf-8 -*-
"""
"Foto" de la actitud de la Pixhawk: promedia 2 s de roll/pitch/yaw con el dron sostenido en una posición. Parar antes el servicio (systemctl --user stop campo).
Uso:  ~/dron_env/bin/python foto_actitud.py [nombre_de_la_foto]      (acumula en /tmp/fotos_actitud.txt)
"""
import math
import sys
import time

sys.path.insert(0, ".")
import config as C
from pymavlink import mavutil

m = mavutil.mavlink_connection(C.PUERTO_PIXHAWK, baud=C.BAUD_PIXHAWK, source_system=C.SYSID_COMPANION, source_component=C.COMPID_COMPANION)
hb = m.wait_heartbeat(timeout=8)
if not hb or hb.base_mode & 128:
    raise SystemExit("sin latido o el dron está ARMADO")
m.mav.command_long_send(m.target_system, 1, mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0, mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 1e5, 0, 0, 0, 0, 0)
r, p, sy, cy, n = 0.0, 0.0, 0.0, 0.0, 0
t_fin = time.time() + 2.0
while time.time() < t_fin:
    a = m.recv_match(type="ATTITUDE", blocking=True, timeout=1.0)
    if a is not None:
        r, p, n = r + math.degrees(a.roll), p + math.degrees(a.pitch), n + 1
        sy, cy = sy + math.sin(a.yaw), cy + math.cos(a.yaw)
if n == 0:
    raise SystemExit("sin datos de actitud")
linea = "%s: roll %+.1f  pitch %+.1f  yaw %.1f   (%d muestras)" % (sys.argv[1] if len(sys.argv) > 1 else "foto", r / n, p / n, math.degrees(math.atan2(sy, cy)) % 360, n)
print(linea)
open("/tmp/fotos_actitud.txt", "a").write(linea + "\n")
