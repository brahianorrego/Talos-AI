# -*- coding: utf-8 -*-
"""
Prueba de orientación de la Pixhawk con el dron DESARMADO y sin hélices, en la mano o sobre una mesa. Parar antes el servicio (systemctl --user stop campo).
Graba la actitud 40 s y dice, por separado, cuánto subió/bajó el cabeceo, cuánto se inclinó a cada lado y cuánto giró el rumbo.
Movimientos (cada uno ~6 s y volver a nivelar): 1) nariz ARRIBA ~30°  2) lado DERECHO abajo ~30°  3) girar el dron ~90° hacia la DERECHA (visto desde arriba).
Esperado con la orientación bien puesta: nariz arriba -> pitch POSITIVO; lado derecho abajo -> roll POSITIVO; giro a la derecha -> yaw AUMENTA.
Uso:  ~/dron_env/bin/python probar_orientacion.py [segundos=40]
"""
import math
import sys
import time

sys.path.insert(0, ".")
import config as C
from pymavlink import mavutil

DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 40.0
m = mavutil.mavlink_connection(C.PUERTO_PIXHAWK, baud=C.BAUD_PIXHAWK, source_system=C.SYSID_COMPANION, source_component=C.COMPID_COMPANION)
hb = m.wait_heartbeat(timeout=8)
if not hb:
    raise SystemExit("sin HEARTBEAT: ¿el servicio sigue corriendo?")
if hb.base_mode & 128:
    raise SystemExit("el dron está ARMADO")
m.mav.command_long_send(m.target_system, 1, mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0, mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 1e5, 0, 0, 0, 0, 0)
print("GRABANDO %.0f s ... mueve el dron" % DUR, flush=True)
t_fin = time.time() + DUR
serie = []
while time.time() < t_fin:
    a = m.recv_match(type="ATTITUDE", blocking=True, timeout=1.0)
    if a is not None:
        serie.append((time.time(), math.degrees(a.roll), math.degrees(a.pitch), math.degrees(a.yaw)))
if len(serie) < 20:
    raise SystemExit("muy pocos datos de actitud (%d)" % len(serie))
r0, p0, y0 = serie[0][1:]
pitch = [s[2] - p0 for s in serie]
roll = [s[1] - r0 for s in serie]
yaw, acum = [], 0.0
for (_, _, _, ya), (_, _, _, yb) in zip(serie, serie[1:]):
    acum += (yb - ya + 180.0) % 360.0 - 180.0
    yaw.append(acum)
print("Muestras: %d (%.1f por segundo)" % (len(serie), len(serie) / DUR))
print("\nLínea de tiempo (cada 2 s, respecto a la posición inicial):  seg | pitch | roll | yaw acumulado")
for k in range(0, len(serie), 20):
    print("  %3.0f | %+6.1f | %+6.1f | %+7.1f" % (serie[k][0] - serie[0][0], pitch[k], roll[k], yaw[min(k, len(yaw) - 1)]))
print()
print("Pitch  (nariz arriba debe dar +):  máximo %+.1f°   mínimo %+.1f°" % (max(pitch), min(pitch)))
print("Roll   (lado derecho abajo debe dar +):  máximo %+.1f°   mínimo %+.1f°" % (max(roll), min(roll)))
print("Yaw    (giro a la derecha debe SUBIR):  mayor giro a la derecha %+.1f°   mayor giro a la izquierda %+.1f°" % (max(yaw), min(yaw)))
ok = max(pitch) > 15 and max(roll) > 15 and max(yaw) > 45
print("\nVEREDICTO: " + ("los tres movimientos salieron con el signo esperado" if ok else
      "revisar: algún eje salió con el signo contrario o no se movió lo pedido (mira los números de arriba)"))
