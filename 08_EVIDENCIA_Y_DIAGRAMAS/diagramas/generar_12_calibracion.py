# -*- coding: utf-8 -*-
"""Genera 12_calibracion_disposicion.svg: dónde poner el dron y las marcas para medir ángulos (/calibrar).
Opción elegida: dron sobre el escritorio de la habitación (75.5 cm), mirando una pared lisa a D = 2 m."""
import math

SC = 200.0                      # px por metro (vista lateral)
Y0 = 560                        # y del piso en la vista lateral
T = 0.755                       # escritorio (m)
HL, HC = T + 0.28, T + 0.335    # ejes del LiDAR y la cámara
D = 2.0                         # distancia ejemplo a la pared (m)
XD = 150                        # x del dron
XW = XD + D * SC                # x de la pared
H = 2.5
o = []
a = o.append
a('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1250" width="1000" height="1250" font-family="Times New Roman, serif">')
a('<rect width="1000" height="1250" fill="#fff"/>')
a('<text x="500" y="34" text-anchor="middle" font-size="24" font-weight="700">Medición de ángulos: disposición de la prueba</text>')
a('<text x="500" y="58" text-anchor="middle" font-size="15" fill="#444">Dron sobre el escritorio de la habitación (75.5 cm), mirando una pared lisa a unos 2 m. Cotas en cm desde el piso.</text>')


def y(h):
    return Y0 - h * SC


# ---------- vista lateral
a('<text x="40" y="96" font-size="18" font-weight="700">A · Vista lateral</text>')
a('<line x1="40" y1="%d" x2="960" y2="%d" stroke="#555" stroke-width="2"/><text x="960" y="%d" text-anchor="end" font-size="12" fill="#555">piso</text>' % (Y0, Y0, Y0 + 16))
a('<rect x="70" y="%.0f" width="190" height="%.0f" fill="#d7ccc8" stroke="#6d4c41" stroke-width="2"/>' % (y(T), T * SC))
a('<text x="165" y="%.0f" text-anchor="middle" font-size="14" fill="#4e342e">Escritorio</text><text x="165" y="%.0f" text-anchor="middle" font-size="14" font-weight="700" fill="#4e342e">75.5 cm</text>' % (y(T) + 60, y(T) + 78))
a('<rect x="%d" y="%.0f" width="%.0f" height="%.0f" fill="#fafafa" stroke="#555" stroke-width="2"/>' % (XW, y(H), 10, H * SC))
a('<text x="%.0f" y="%.0f" font-size="13" fill="#555">pared lisa</text>' % (XW + 16, y(H) + 12))
# dron
a('<rect x="%d" y="%.0f" width="30" height="%.0f" fill="#e3f2fd" stroke="#1565c0" stroke-width="2"/>' % (XD - 30, y(HC + 0.05), 0.12 * SC))
a('<rect x="%d" y="%.0f" width="14" height="%.0f" fill="#fce4ec" stroke="#c2185b" stroke-width="2"/>' % (XD - 14, y(HL + 0.02), 0.04 * SC))
a('<text x="%d" y="%.0f" text-anchor="middle" font-size="13" font-weight="700" fill="#0d47a1">dron</text>' % (XD - 15, y(HC + 0.05) - 8))
# ejes (inclinación nominal -5°)
p = math.radians(5)
for hh, col, lab in ((HC, "#e65100", "eje de la cámara"), (HL, "#c2185b", "eje del LiDAR")):
    a('<line x1="%d" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="1.5" stroke-dasharray="7 4"/>' % (XD, y(hh), XW, y(hh) + D * SC * math.tan(p), col))
a('<text x="%d" y="%.0f" font-size="12" fill="#bf360c">eje de la cámara: 109 cm (inclinación nominal −5°)</text>' % (XD + 20, y(HC) - 30))
a('<text x="%d" y="%.0f" font-size="12" fill="#880e4f">eje del LiDAR: 103.5 cm</text>' % (XD + 20, y(HL) + 36))
# campo de visión vertical nominal 48.8° alrededor de -5°
for ang in (24.4 - 5, -24.4 - 5):
    t = math.tan(math.radians(ang))
    x_end = XW
    y_end = y(HC) - t * D * SC
    if y_end > Y0:
        x_end = XD + (Y0 - y(HC)) / (-t)
        y_end = Y0
    a('<line x1="%d" y1="%.0f" x2="%.0f" y2="%.0f" stroke="#e65100" stroke-width="1" opacity="0.55"/>' % (XD, y(HC), x_end, y_end))
a('<text x="%d" y="%.0f" font-size="12" fill="#bf360c" opacity="0.9">campo vertical (nominal 48.8°)</text>' % (XD + 170, y(HC) - 120))
# marcas en la pared
for hh, nom in ((0.40, "B"), (1.50, "T"), (0.90, "L y R")):
    a('<rect x="%d" y="%.0f" width="16" height="16" fill="#ff9800" stroke="#e65100" stroke-width="2"/>' % (XW - 12, y(hh) - 8))
    a('<text x="%.0f" y="%.0f" font-size="13" font-weight="700" fill="#e65100">%s · %d cm</text>' % (XW + 22, y(hh) + 5, nom, hh * 100))
# distancia D
a('<line x1="%d" y1="%d" x2="%.0f" y2="%d" stroke="#000" stroke-width="1.5"/><line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#000"/><line x1="%.0f" y1="%d" x2="%.0f" y2="%d" stroke="#000"/>' % (XD, Y0 + 34, XW, Y0 + 34, XD, Y0 + 28, XD, Y0 + 40, XW, Y0 + 28, XW, Y0 + 40))
a('<text x="%.0f" y="%d" text-anchor="middle" font-size="14" font-weight="700">D ≈ 2 m (la lee el LiDAR; verifícala con el metro)</text>' % ((XD + XW) / 2, Y0 + 56))
# dedo
for d, nom in ((1.0, "dedo a 1 m"), (1.5, "dedo a 1.5 m")):
    xx = XD + d * SC
    yy = y(HL) + d * SC * math.tan(p)
    a('<circle cx="%.0f" cy="%.0f" r="7" fill="#ff80ab" stroke="#c2185b" stroke-width="2"/>' % (xx, yy))
    a('<text x="%.0f" y="%.0f" text-anchor="middle" font-size="12" fill="#880e4f">%s</text>' % (xx, yy + 24, nom))
# cotas verticales
a('<line x1="40" y1="%.0f" x2="40" y2="%d" stroke="#000"/><text x="34" y="%.0f" text-anchor="end" font-size="12">75.5</text>' % (y(T), Y0, (y(T) + Y0) / 2))

# ---------- vista de frente de la pared
a('<text x="40" y="720" font-size="18" font-weight="700">B · La pared vista de frente (como la ve la cámara)</text>')
S2 = 160.0
YB = 1130
XC = 500
a('<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" fill="#fafafa" stroke="#555" stroke-width="2"/>' % (XC - 1.0 * S2, YB - 2.4 * S2, 2.0 * S2, 2.4 * S2))
a('<line x1="%d" y1="%.0f" x2="%d" y2="%d" stroke="#777" stroke-dasharray="6 5"/>' % (XC, YB - 2.4 * S2, XC, YB))
a('<text x="%d" y="%.0f" text-anchor="middle" font-size="12" fill="#555">línea central (el dron mira aquí)</text>' % (XC, YB - 2.4 * S2 - 8))
marks = [("L", -0.6, 0.9), ("R", 0.6, 0.9), ("B", 0.0, 0.4), ("T", 0.0, 1.5)]
for nom, x, h in marks:
    px, py = XC + x * S2, YB - h * S2
    a('<rect x="%.0f" y="%.0f" width="16" height="16" fill="#ff9800" stroke="#e65100" stroke-width="2"/>' % (px - 8, py - 8))
    a('<text x="%.0f" y="%.0f" font-size="14" font-weight="700" fill="#e65100">%s · %d cm</text>' % (px + 14, py + 5, nom, h * 100))
# cota horizontal L-R (arriba de las marcas)
yl = YB - 0.9 * S2 - 38
a('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="#000" stroke-width="1.5"/>' % (XC - 0.6 * S2, yl, XC + 0.6 * S2, yl))
a('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="#000"/><line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="#000"/>' % (XC - 0.6 * S2, yl - 6, XC - 0.6 * S2, yl + 6, XC + 0.6 * S2, yl - 6, XC + 0.6 * S2, yl + 6))
a('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="#999" stroke-dasharray="3 3"/><line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="#999" stroke-dasharray="3 3"/>' % (XC - 0.6 * S2, yl, XC - 0.6 * S2, YB - 0.9 * S2 - 8, XC + 0.6 * S2, yl, XC + 0.6 * S2, YB - 0.9 * S2 - 8))
a('<text x="%d" y="%.0f" text-anchor="middle" font-size="14" font-weight="700">120 cm entre L y R</text>' % (XC, yl - 8))
# cota vertical B-T (a la izquierda de la línea central)
xv = XC - 1.0 * S2 - 40
a('<line x1="%d" y1="%.0f" x2="%d" y2="%.0f" stroke="#000" stroke-width="1.5"/>' % (xv, YB - 0.4 * S2, xv, YB - 1.5 * S2))
a('<line x1="%d" y1="%.0f" x2="%d" y2="%.0f" stroke="#000"/><line x1="%d" y1="%.0f" x2="%d" y2="%.0f" stroke="#000"/>' % (xv - 6, YB - 0.4 * S2, xv + 6, YB - 0.4 * S2, xv - 6, YB - 1.5 * S2, xv + 6, YB - 1.5 * S2))
a('<text x="%d" y="%.0f" text-anchor="end" font-size="14" font-weight="700">110 cm entre B y T</text>' % (xv - 8, YB - 0.95 * S2 - 8))
a('<text x="%d" y="%.0f" text-anchor="end" font-size="12" fill="#555">(alturas medidas desde el piso)</text>' % (xv - 8, YB - 0.95 * S2 + 8))
a('<line x1="%.0f" y1="%d" x2="%.0f" y2="%d" stroke="#9e9e9e" stroke-width="3"/><text x="%.0f" y="%d" text-anchor="end" font-size="12" fill="#757575">piso</text>' % (XC - 1.2 * S2, YB, XC + 1.2 * S2, YB, XC + 1.2 * S2, YB + 16))
# notas
notas = ["Marcas: cuadrados de papel de color de unos 10 × 10 cm (o cinta). Se hace clic en el centro de cada uno.",
         "Todas las alturas se miden con el metro desde el piso, no desde el escritorio. Si se pega a otra altura, se escribe esa en la página.",
         "El dron debe quedar mirando de frente a la pared: la distancia de su lado izquierdo y de su lado derecho a la pared debe ser igual."]
a('<rect x="40" y="1160" width="920" height="80" rx="8" fill="#f5f5f5" stroke="#cfd8dc"/>')
for i, t in enumerate(notas):
    a('<text x="56" y="%d" font-size="13" fill="#333">• %s</text>' % (1182 + i * 20, t))
a('</svg>')
open("12_calibracion_disposicion.svg", "w", encoding="utf-8").write("\n".join(o))
print("ok")
