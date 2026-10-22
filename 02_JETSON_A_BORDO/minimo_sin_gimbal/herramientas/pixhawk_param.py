# -*- coding: utf-8 -*-
"""
Cambia UN parámetro de la Pixhawk por TELEM2, lo lee de vuelta y (opcional) reinicia la placa. Parar antes el servicio: systemctl --user stop campo
Uso:  ~/dron_env/bin/python pixhawk_param.py NOMBRE VALOR [--reiniciar]
Ejemplo (Pixhawk boca abajo, flecha al frente):  pixhawk_param.py AHRS_ORIENTATION 8 --reiniciar
Solo con el dron DESARMADO y sin hélices; no toca ningún otro parámetro.
"""
import sys
import time

sys.path.insert(0, ".")
import config as C
from pymavlink import mavutil

if len(sys.argv) < 3:
    raise SystemExit(__doc__)
nombre, valor, reiniciar = sys.argv[1].upper(), float(sys.argv[2]), "--reiniciar" in sys.argv
m = mavutil.mavlink_connection(C.PUERTO_PIXHAWK, baud=C.BAUD_PIXHAWK, source_system=C.SYSID_COMPANION, source_component=C.COMPID_COMPANION)
hb = m.wait_heartbeat(timeout=8)
if not hb:
    raise SystemExit("sin HEARTBEAT: ¿el servicio sigue corriendo?")
if hb.base_mode & 128:
    raise SystemExit("el dron está ARMADO: no se cambia nada")


def leer():
    m.mav.param_request_read_send(m.target_system, 1, nombre.encode(), -1)
    x = m.recv_match(type="PARAM_VALUE", blocking=True, timeout=3)
    return x.param_value if x is not None else None


antes = leer()
print("%s antes: %s" % (nombre, antes))
m.mav.param_set_send(m.target_system, 1, nombre.encode(), valor, mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
time.sleep(1.0)
despues = leer()
print("%s después: %s" % (nombre, despues))
if despues is None or abs(despues - valor) > 1e-6:
    raise SystemExit("la Pixhawk no aceptó el valor")
if reiniciar:
    m.mav.command_long_send(m.target_system, 1, mavutil.mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN, 0, 1, 0, 0, 0, 0, 0, 0)
    print("reinicio pedido: la Pixhawk tarda ~10 s en volver")
