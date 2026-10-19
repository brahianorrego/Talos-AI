# -*- coding: utf-8 -*-
"""
La RUTA DE BÚSQUEDA de Brahian (docs/RUTA_BUSQUEDA_BRAHIAN.md, D-071) calculada sobre los paneles de una partida, para DIBUJARLA en la
estación web y en Unreal y verla ejecutarse cuando Simulación grabe repeticiones con la ruta. Son consejos, no reglas duras: aquí solo se
dibuja el recorrido ideal (los números son valores de partida, sin medir):

  1 Entrada      giro de 360° donde está el dron al empezar
  2 Detrás       ir al lado de la V que la oculta del dron: a 4.5 m de su centro por el lado de la boca, a 3.30 m de altura
  3 Cuadrado     recorrer un cuadrado alrededor de la V (lado = boca de ~2.1 m + 2 m de margen por lado), con la cámara mirando hacia donde vuela
  4 Vaivén       frente a la boca, la cámara a izquierda y derecha (guiñada de ±30°)
  5 La otra V    repetir 2-4 con el otro conjunto de paneles
Siempre en movimiento (nunca se queda quieta) y sin subir de 3.30 m: la altura queda fija.

    ruta(paneles, inicio) -> {"entrada": [x, y, z], "v": [{"apice", "eje", "centro", "puntos": [[x, y, z, psi_grados, nombre]], "cuadrado", "vaiven"}],
                              "polilinea": [[x, y, z]]}
Marco de la simulación: x este, y norte, metros. psi en grados, antihorario desde +x (como la guiñada de la simulación).
"""
import math

Z_RUTA = 3.30
D_DETRAS = 4.5
BOCA = 2.12
MARGEN = 2.0
AMP_VAIVEN = 30.0
LARGO_VAIVEN = 6.0


def _norm(v):
    n = math.hypot(*v)
    return (v[0] / n, v[1] / n)


def uves(paneles, tol=0.05):
    """Agrupa los paneles [x1, y1, x2, y2, alto] de a dos que comparten un extremo (el vértice) y devuelve cada V."""
    usados, lista = set(), []
    for i, p in enumerate(paneles):
        if i in usados:
            continue
        for j in range(i + 1, len(paneles)):
            if j in usados:
                continue
            q = paneles[j]
            for a in ((p[0], p[1]), (p[2], p[3])):
                for b in ((q[0], q[1]), (q[2], q[3])):
                    if math.hypot(a[0] - b[0], a[1] - b[1]) < tol:
                        ap = a
                        ex1 = (p[2], p[3]) if a == (p[0], p[1]) else (p[0], p[1])
                        ex2 = (q[2], q[3]) if b == (q[0], q[1]) else (q[0], q[1])
                        usados.update((i, j))
                        medio = ((ex1[0] + ex2[0]) / 2, (ex1[1] + ex2[1]) / 2)
                        eje = _norm((medio[0] - ap[0], medio[1] - ap[1]))
                        d = math.hypot(medio[0] - ap[0], medio[1] - ap[1])
                        lista.append({"apice": list(ap), "eje": list(eje), "centro": [ap[0] + eje[0] * d / 2, ap[1] + eje[1] * d / 2],
                                      "alas": [list(ex1), list(ex2)]})
                        break
                else:
                    continue
                break
            if i in usados:
                break
    return lista


def ruta(paneles, inicio):
    """inicio = (x, y, z) del dron al empezar la búsqueda. Devuelve la ruta (ver el docstring del módulo)."""
    V = uves(paneles)
    V.sort(key=lambda v: math.hypot(v["centro"][0] - inicio[0], v["centro"][1] - inicio[1]))        # primero la V más cercana
    puntos_total = [[inicio[0], inicio[1], Z_RUTA]]
    pos = (inicio[0], inicio[1])
    salida = {"entrada": [inicio[0], inicio[1], Z_RUTA], "v": [], "polilinea": []}
    for n, v in enumerate(V, 1):
        u = tuple(v["eje"])
        w = (-u[1], u[0])
        c = v["centro"]
        M = (c[0] + u[0] * D_DETRAS, c[1] + u[1] * D_DETRAS)
        psi_M = math.degrees(math.atan2(-u[1], -u[0]))                    # mirando hacia la V
        h = (BOCA + 2 * MARGEN) / 2
        esquinas = [(c[0] + h * (su * u[0] + sw * w[0]), c[1] + h * (su * u[1] + sw * w[1])) for su, sw in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
        # el cuadrado se recorre empezando por la esquina más cercana al punto donde está el dron, hacia el lado que tenga menos giro
        k0 = min(range(4), key=lambda k: math.hypot(esquinas[k][0] - pos[0], esquinas[k][1] - pos[1]))
        orden = [esquinas[(k0 + s) % 4] for s in range(4)] + [esquinas[k0]]
        pts = []
        for i in range(len(orden) - 1):
            a, b = orden[i], orden[i + 1]
            psi = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            pts.append([a[0], a[1], Z_RUTA, psi, f"V{n} · esquina {i + 1}"])
        pts.append([orden[-1][0], orden[-1][1], Z_RUTA, pts[0][3], f"V{n} · cierra el cuadrado"])
        pts.append([M[0], M[1], Z_RUTA, psi_M, f"V{n} · de frente a la boca"])
        salida["v"].append({"apice": v["apice"], "eje": v["eje"], "centro": c, "alas": v["alas"], "puntos": pts, "cuadrado": [[p[0], p[1]] for p in pts[:5]],
                            "vaiven": {"desde": [M[0], M[1]], "psi": psi_M, "amplitud": AMP_VAIVEN, "largo": LARGO_VAIVEN}})
        for p in pts:
            puntos_total.append([p[0], p[1], p[2]])
        pos = M
    salida["polilinea"] = puntos_total
    return salida


if __name__ == "__main__":
    import json
    import sys
    d = json.load(open(sys.argv[1], encoding="utf-8"))
    r = ruta(d["paneles"], d["cuadros"][0]["d"][:3])
    print(json.dumps(r, ensure_ascii=False)[:1200])
