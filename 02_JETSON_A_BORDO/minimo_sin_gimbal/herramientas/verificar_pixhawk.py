# -*- coding: utf-8 -*-
"""
Revisión de banco de la Pixhawk por TELEM2 (solo lectura, no manda ninguna orden salvo pedir parámetros y frecuencias de mensajes).
Hay que parar antes el servicio (systemctl --user stop campo): el puerto serie no se comparte.
Uso:  ~/dron_env/bin/python verificar_pixhawk.py [segundos=12]
Muestra: latido, AHRS_ORIENTATION y otros parámetros, actitud (roll/pitch/yaw), vibración, GPS, receptor (canales), salidas a los motores y los STATUSTEXT.
"""
import sys
import time

sys.path.insert(0, ".")
import config as C
from pymavlink import mavutil

DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 12.0
PARAMS = ["AHRS_ORIENTATION", "SERVO1_FUNCTION", "SERVO2_FUNCTION", "SERVO3_FUNCTION", "SERVO4_FUNCTION", "COMPASS_ORIENT", "COMPASS_USE", "COMPASS_USE2", "COMPASS_USE3", "FRAME_CLASS", "FRAME_TYPE", "ARMING_CHECK",
          "BATT_MONITOR", "BATT_ARM_VOLT", "BATT_FS_LOW_ACT", "FS_THR_ENABLE", "SERIAL2_PROTOCOL", "SERIAL2_BAUD"]

m = mavutil.mavlink_connection(C.PUERTO_PIXHAWK, baud=C.BAUD_PIXHAWK, source_system=C.SYSID_COMPANION, source_component=C.COMPID_COMPANION)
if not m.wait_heartbeat(timeout=8):
    raise SystemExit("sin HEARTBEAT en %s (¿el servicio sigue corriendo?)" % C.PUERTO_PIXHAWK)
print("HEARTBEAT ok: sistema %d, tipo %d, firmware ArduPilot" % (m.target_system, m.target_component))
for msg, hz in ((mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 10), (mavutil.mavlink.MAVLINK_MSG_ID_SYS_STATUS, 2), (mavutil.mavlink.MAVLINK_MSG_ID_VIBRATION, 2),
                (mavutil.mavlink.MAVLINK_MSG_ID_GPS_RAW_INT, 2), (mavutil.mavlink.MAVLINK_MSG_ID_RC_CHANNELS, 4),
                (mavutil.mavlink.MAVLINK_MSG_ID_SERVO_OUTPUT_RAW, 2), (mavutil.mavlink.MAVLINK_MSG_ID_SCALED_PRESSURE, 2)):
    m.mav.command_long_send(m.target_system, 1, mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0, msg, 1e6 / hz, 0, 0, 0, 0, 0)
valores = {}
for p in PARAMS:
    m.mav.param_request_read_send(m.target_system, 1, p.encode(), -1)
t_fin = time.time() + DUR
ultimo = {}
textos = []
while time.time() < t_fin:
    x = m.recv_match(blocking=True, timeout=0.5)
    if x is None or x.get_srcSystem() != m.target_system:
        continue
    t = x.get_type()
    if t == "PARAM_VALUE":
        valores[x.param_id if isinstance(x.param_id, str) else x.param_id.decode()] = x.param_value
    elif t == "STATUSTEXT":
        textos.append(x.text)
    elif t in ("ATTITUDE", "VIBRATION", "GPS_RAW_INT", "RC_CHANNELS", "SERVO_OUTPUT_RAW", "SYS_STATUS", "SCALED_PRESSURE"):
        ultimo[t] = x

print("\n== Parámetros ==")
for p in PARAMS:
    print("  %-18s %s" % (p, valores.get(p, "(sin respuesta)")))
a = ultimo.get("ATTITUDE")
if a:
    print("\n== Actitud (dron quieto, apoyado en su base) ==\n  roll %.1f°  pitch %.1f°  yaw %.1f°   (en reposo, nivelado: roll y pitch cerca de 0)"
          % (a.roll * 57.2958, a.pitch * 57.2958, a.yaw * 57.2958))
v = ultimo.get("VIBRATION")
if v:
    print("\n== Vibración ==\n  X %.1f  Y %.1f  Z %.1f m/s²   clipping %d/%d/%d   (bueno < 30; malo > 60)" % (v.vibration_x, v.vibration_y, v.vibration_z, v.clipping_0, v.clipping_1, v.clipping_2))
g = ultimo.get("GPS_RAW_INT")
if g:
    print("\n== GPS ==\n  fix tipo %d (3 = 3D)  satélites %d  HDOP %.1f" % (g.fix_type, g.satellites_visible, g.eph / 100.0))
s = ultimo.get("SYS_STATUS")
if s:
    print("\n== Batería / sensores ==\n  %.2f V  %.1f A   sensores presentes %s  sanos %s" % (s.voltage_battery / 1000.0, max(s.current_battery, 0) / 100.0,
          hex(s.onboard_control_sensors_present), hex(s.onboard_control_sensors_health)))
    falta = s.onboard_control_sensors_present & ~s.onboard_control_sensors_health
    nombres = {mavutil.mavlink.MAV_SYS_STATUS_SENSOR_3D_GYRO: "giroscopio", mavutil.mavlink.MAV_SYS_STATUS_SENSOR_3D_ACCEL: "acelerómetro",
               mavutil.mavlink.MAV_SYS_STATUS_SENSOR_3D_MAG: "brújula", mavutil.mavlink.MAV_SYS_STATUS_SENSOR_ABSOLUTE_PRESSURE: "barómetro",
               mavutil.mavlink.MAV_SYS_STATUS_SENSOR_GPS: "GPS", mavutil.mavlink.MAV_SYS_STATUS_AHRS: "AHRS", mavutil.mavlink.MAV_SYS_STATUS_SENSOR_RC_RECEIVER: "receptor RC"}
    mal = [n for b, n in nombres.items() if falta & b]
    print("  con problema: %s" % (", ".join(mal) if mal else "ninguno"))
r = ultimo.get("RC_CHANNELS")
if r:
    print("\n== Receptor (canales 1-8, µs) ==\n  %s   RSSI %s" % ([r.chan1_raw, r.chan2_raw, r.chan3_raw, r.chan4_raw, r.chan5_raw, r.chan6_raw, r.chan7_raw, r.chan8_raw], r.rssi))
o = ultimo.get("SERVO_OUTPUT_RAW")
if o:
    print("\n== Salidas a motores (µs) ==\n  %s" % [o.servo1_raw, o.servo2_raw, o.servo3_raw, o.servo4_raw])
p = ultimo.get("SCALED_PRESSURE")
if p:
    print("\n== Barómetro ==\n  %.1f hPa  %.1f °C" % (p.press_abs, p.temperature / 100.0))
print("\n== Mensajes de la Pixhawk ==")
for tx in dict.fromkeys(textos):
    print("  " + tx)
if not textos:
    print("  (ninguno en estos %d s)" % DUR)
