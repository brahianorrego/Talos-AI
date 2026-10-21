# -*- coding: utf-8 -*-
"""Registro de demostraciones de Brahian (Modo Enseñar): por cada paso guarda lo que veía el dron (obs_dron, 195 números) y
lo que pidió el operador (mando de velocidad, guiñada y gimbal que salieron a la Pixhawk). Sirve para imitar o para medir
cuánto se parece una política a Brahian. Se guarda en demos_brahian/ (fuera de Git: puede traer a personas).

  g = Grabador(env, 0)            # partida 0 del entorno
  ... en cada paso, después de env.step(...):  g.paso()
  g.guardar()                     # -> demos_brahian/demo_<fecha>.npz  (devuelve la ruta; None si hay < 5 pasos)
Leerla:  d = np.load(ruta);  d["obs"] (T, 195), d["cmd"] (T, 5: vx, vy, vz, yaw °/s, gimbal °), d["operador"] (T,) bool
"""
import datetime
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.dirname(AQUI)
DEMOS = os.path.join(SIM, "demos_brahian")


class Grabador(object):
    def __init__(self, env, i=0):
        self.env, self.i = env, i
        self.obs, self.cmd, self.op, self.pose = [], [], [], []

    def paso(self):
        e, i = self.env, self.i
        self.obs.append(e.obs_dron()[i].astype(np.float32))
        self.cmd.append(np.asarray(e.cmd_reg[i], np.float32))
        self.op.append(bool(e.man_t[i] > 0 or e.obj_on[i]))
        self.pose.append([e.dx[i], e.dy[i], e.dz[i], e.psi[i], e.pan[i], e.gimbal[i]])

    def guardar(self, carpeta=DEMOS):
        if len(self.obs) < 5:
            return None
        os.makedirs(carpeta, exist_ok=True)
        ruta = os.path.join(carpeta, "demo_%s.npz" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        np.savez_compressed(ruta, obs=np.array(self.obs), cmd=np.array(self.cmd), operador=np.array(self.op),
                            pose=np.array(self.pose, np.float32))
        self.obs, self.cmd, self.op, self.pose = [], [], [], []
        return ruta
