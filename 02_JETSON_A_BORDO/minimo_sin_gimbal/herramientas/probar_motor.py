# -*- coding: utf-8 -*-
"""
Gira UN motor unos segundos a baja potencia (MAV_CMD_DO_MOTOR_TEST) para comprobar cuál es y hacia dónde gira. SIN HÉLICES.
Parar antes el servicio (systemctl --user stop campo). Tener el control encendido y a mano el paro de emergencia (CH8).
Uso:  ~/dron_env/bin/python probar_motor.py NUMERO [porcentaje=7] [segundos=3]      NUMERO 1..4
NUMERO es el ORDEN DE PRUEBA de ArduPilot, no el número de motor: A, B, C, D en sentido horario empezando por el delantero DERECHO.
Con FRAME_TYPE 18 (X_REV, el de este dron con SERVO1..4_FUNCTION = 36, 33, 34, 35) se espera, visto desde atrás del dron:
  prueba 1 = delantero DERECHO gira horario | 2 = trasero DERECHO anti-horario | 3 = trasero IZQUIERDO horario | 4 = delantero IZQUIERDO anti-horario
(Con FRAME_TYPE 1, X normal, serían los mismos lugares pero con el giro contrario.)
Reglas duras de este programa: máximo 12 % y 4 s; se niega si el dron está armado.
"""
import sys
import time

sys.path.insert(0, ".")
import config as C
from pymavlink import mavutil

if len(sys.argv) < 2 or sys.argv[1] not in ("1", "2", "3", "4"):
    raise SystemExit(__doc__)
motor = int(sys.argv[1])
pct = min(float(sys.argv[2]) if len(sys.argv) > 2 else 7.0, 12.0)
seg = min(float(sys.argv[3]) if len(sys.argv) > 3 else 3.0, 4.0)
m = mavutil.mavlink_connection(C.PUERTO_PIXHAWK, baud=C.BAUD_PIXHAWK, source_system=C.SYSID_COMPANION, source_component=C.COMPID_COMPANION)
hb = m.wait_heartbeat(timeout=8)
if not hb:
    raise SystemExit("sin HEARTBEAT: ¿el servicio sigue corriendo?")
if hb.base_mode & 128:
    raise SystemExit("el dron está ARMADO: no se prueba nada")
m.mav.command_long_send(m.target_system, 1, mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0, mavutil.mavlink.MAVLINK_MSG_ID_SERVO_OUTPUT_RAW, 1e5, 0, 0, 0, 0, 0)
print("Motor %d al %.0f %% por %.0f s ..." % (motor, pct, seg), flush=True)
m.mav.command_long_send(m.target_system, 1, mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST, 0, motor, mavutil.mavlink.MOTOR_TEST_THROTTLE_PERCENT, pct, seg, 1, 0, 0)
t_fin = time.time() + seg + 1.5
pico, acks, textos = [0] * 4, [], []
while time.time() < t_fin:
    x = m.recv_match(blocking=True, timeout=0.3)
    if x is None:
        continue
    t = x.get_type()
    if t == "COMMAND_ACK" and x.command == mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST:
        acks.append(x.result)
    elif t == "STATUSTEXT":
        textos.append(x.text)
    elif t == "SERVO_OUTPUT_RAW":
        pico = [max(a, b) for a, b in zip(pico, [x.servo1_raw, x.servo2_raw, x.servo3_raw, x.servo4_raw])]
print("Respuesta de la Pixhawk (0 = aceptado): %s" % (acks or "ninguna"))
print("Salida máxima a los 4 motores (µs): %s   (1000 = apagado; el motor %d debe subir)" % (pico, motor))
for tx in dict.fromkeys(textos):
    print("  Pixhawk dice: " + tx)
