# -*- coding: utf-8 -*-
"""Genera 11_ubicacion_componentes_vista_lateral.svg.
A escala (16 px por cm) en la zona medida el 20-oct: placas de 15 cm de largo, bloque entre placas 3.85 cm, caja de la Jetson 4.3 cm,
GPS 11.3 cm sobre la placa, eje del LiDAR a 28 cm y de la cámara a 33.5 cm de la superficie de apoyo, TF03 de 44 x 43 x 32 mm.
La zona inferior (batería, patas) es esquemática. Uso: python generar_11_lateral.py y luego renderizar a PNG con Chrome headless."""
E = 16.0


def Y(h):
    """altura en cm sobre la superficie de apoyo -> coordenada y"""
    return 170 + (41.5 - h) * E


o = []
a = o.append
a('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 800" width="1000" height="800" font-family="Times New Roman, serif">')
a('<rect width="1000" height="800" fill="#fff"/>')
a('<text x="500" y="34" text-anchor="middle" font-size="24" font-weight="700">Disposición de los componentes · vista lateral</text>')
a('<text x="500" y="58" text-anchor="middle" font-size="15" fill="#444">Cotas a escala en la parte medida el 20-oct (placas de 15 cm). Posiciones horizontales aproximadas.</text>')
a('<text x="860" y="98" text-anchor="end" font-size="17" font-weight="700" fill="#b71c1c">FRENTE ►</text>')
a('<text x="140" y="98" font-size="17" font-weight="700" fill="#37474f">◄ PARTE POSTERIOR</text>')
# regla vertical
a('<line x1="108" y1="%.0f" x2="108" y2="%.0f" stroke="#555" stroke-width="1.5"/>' % (Y(42), Y(24)))
for h in range(24, 43, 2):
    a('<line x1="102" y1="%.0f" x2="114" y2="%.0f" stroke="#555"/><text x="96" y="%.0f" text-anchor="end" font-size="12" fill="#555">%d</text>' % (Y(h), Y(h), Y(h) + 4, h))
a('<text x="52" y="%.0f" font-size="11" fill="#555" transform="rotate(-90 52 %.0f)" text-anchor="middle">altura sobre la superficie de apoyo (cm)</text>' % (Y(33), Y(33)))

PX0 = 440               # borde posterior de las placas
PX1 = PX0 + 15 * E      # borde frontal (15 cm)


def rotulo(txt, x, y, xl, color="#333", anchor="end", size=13, sub=None):
    a('<text x="%d" y="%.1f" text-anchor="%s" font-size="%d" fill="%s">%s</text>' % (x, y, anchor, size, color, txt))
    if sub:
        a('<text x="%d" y="%.1f" text-anchor="%s" font-size="11" fill="%s">%s</text>' % (x, y + 14, anchor, color, sub))


# placas (15 cm)
a('<rect x="%d" y="%.1f" width="%d" height="5" fill="#212121"/>' % (PX0, Y(30.2), PX1 - PX0))
a('<rect x="%d" y="%.1f" width="%d" height="5" fill="#212121"/>' % (PX0, Y(26.1), PX1 - PX0))
# bloque entre placas
a('<rect x="%d" y="%.1f" width="%d" height="%.1f" fill="#eceff1" stroke="#90a4ae"/>' % (PX0 + 12, Y(29.9), PX1 - PX0 - 24, 3.8 * E))
# TF03 al frente del bloque (44 mm largo, 32 mm alto), eje a 28 cm
tx0 = PX1 - 4.4 * E
a('<rect x="%.0f" y="%.1f" width="%.0f" height="%.1f" rx="4" fill="#fce4ec" stroke="#c2185b" stroke-width="2.5"/>' % (tx0, Y(28) - 1.6 * E, 4.4 * E, 3.2 * E))
a('<text x="%.0f" y="%.1f" text-anchor="middle" font-size="13" font-weight="700" fill="#880e4f">TF03</text>' % (tx0 + 2.2 * E, Y(28) - 8))
# Jetson en caja (4.3 cm), adelantada
bx0, bx1 = PX0 + 40, PX1 - 4
a('<rect x="%d" y="%.1f" width="%d" height="%.1f" fill="#e3f2fd" fill-opacity="0.85" stroke="#1565c0" stroke-width="2.5"/>' % (bx0, Y(34.5), bx1 - bx0, 4.3 * E))
a('<text x="%.0f" y="%.1f" text-anchor="middle" font-size="13" font-weight="700" fill="#0d47a1">Jetson</text>' % ((bx0 + bx1) / 2, Y(32.3)))
# antenas
a('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#37474f" stroke-width="5" stroke-linecap="round"/>' % (bx0 + 22, Y(34.5), bx0 + 2, Y(34.5) - 62))
a('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#37474f" stroke-width="5" stroke-linecap="round"/>' % (bx0 + 42, Y(34.5), bx0 + 28, Y(34.5) - 72))
# cámara CSI: centro a 33.5 cm, al frente de la caja
a('<rect x="%d" y="%.1f" width="14" height="24" rx="3" fill="#fff3e0" stroke="#e65100" stroke-width="2.5" transform="rotate(5 %d %.1f)"/>' % (bx1, Y(33.5) - 12, bx1 + 7, Y(33.5)))
# GPS sobre mástil (base en la placa superior, cima a 11.3 cm)
mx = PX0 + 24
a('<rect x="%d" y="%.1f" width="7" height="%.1f" fill="#9e9e9e"/>' % (mx - 3, Y(39.2), (39.2 - 30.2) * E))
a('<rect x="%d" y="%.1f" width="62" height="%.1f" rx="8" fill="#c8e6c9" stroke="#2e7d32" stroke-width="2.5"/>' % (mx - 31, Y(41.5), 2.3 * E))
a('<text x="%d" y="%.1f" text-anchor="middle" font-size="13" font-weight="700" fill="#1b5e20">GPS</text>' % (mx, Y(41.5) + 0.35 * E + 13))
# Pixhawk bajo la placa inferior (8.1 x 4.4 x 1.6 cm aprox.)
a('<rect x="%d" y="%.1f" width="130" height="%.1f" rx="4" fill="#fff8e1" stroke="#6d4c41" stroke-width="2.5"/>' % (PX0 + 55, Y(25.8), 1.6 * E))
a('<text x="%d" y="%.1f" text-anchor="middle" font-size="12" font-weight="700" fill="#4e342e">Pixhawk</text>' % (PX0 + 120, Y(25.8) + 17))

# ---- rótulos a la izquierda (líneas guía) ----
def guia(x0, y0, x1, y1, c="#555"):
    a('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="1"/>' % (x0, y0, x1, y1, c))


rotulo("GPS RadioLink SE100", 395, Y(40.2) + 4, 0, "#1b5e20")
guia(399, Y(40.2), mx - 31, Y(40.2), "#1b5e20")
rotulo("Antenas WiFi (2)", 395, Y(36.5) + 4, 0, "#37474f")
guia(399, Y(36.5), bx0 + 4, Y(34.5) - 56, "#37474f")
rotulo("Jetson Orin Nano en caja de acrílico", 395, Y(32.7) + 4, 0, "#0d47a1")
guia(399, Y(32.7), bx0, Y(32.7), "#0d47a1")
rotulo("Placa superior", 395, Y(30.2) + 4, 0, "#212121")
guia(399, Y(30.2) + 2, PX0, Y(30.2) + 2, "#212121")
rotulo("Cableado, placa de distribución", 395, Y(28.6) + 2, 0, "#37474f")
rotulo("y módulo de potencia", 395, Y(28.6) + 16, 0, "#37474f")
guia(399, Y(28.2), PX0 + 12, Y(28.2), "#37474f")
rotulo("Placa inferior", 395, Y(26.1) + 4, 0, "#212121")
guia(399, Y(26.1) + 2, PX0, Y(26.1) + 2, "#212121")
rotulo("Pixhawk, pegada bajo la placa", 395, Y(25.0) + 2, 0, "#4e342e")
rotulo("inferior y en posición invertida", 395, Y(25.0) + 16, 0, "#4e342e")
guia(399, Y(25.0), PX0 + 55, Y(25.0), "#4e342e")
# ---- rótulos a la derecha ----
rotulo("Cámara CSI (IMX219)", PX1 + 60, Y(37.4), 0, "#bf360c", "start", 14)
rotulo("fijada al frente de la caja", PX1 + 60, Y(37.4) + 16, 0, "#bf360c", "start", 11)
guia(PX1 + 56, Y(37.4) - 4, bx1 + 8, Y(33.5) - 12, "#bf360c")
a('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#e65100" stroke-width="1" stroke-dasharray="6 4"/><text x="%d" y="%.1f" font-size="12" fill="#bf360c">eje de la cámara</text>' % (bx1 + 16, Y(33.5), PX1 + 135, Y(33.5), PX1 + 140, Y(33.5) + 4))
a('<line x1="%.0f" y1="%.1f" x2="%d" y2="%.1f" stroke="#c2185b" stroke-width="1" stroke-dasharray="6 4"/><text x="%d" y="%.1f" font-size="12" fill="#880e4f">eje del LiDAR (TF03)</text>' % (tx0 + 2.2 * E, Y(28), PX1 + 135, Y(28), PX1 + 140, Y(28) + 4))


def cota(x, h0, h1, txt, lado, dx):
    y0, y1 = Y(h0), Y(h1)
    a('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#000" stroke-width="1.2"/>' % (x, y0, x, y1))
    a('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#000"/><line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#000"/>' % (x - 5, y0, x + 5, y0, x - 5, y1, x + 5, y1))
    a('<text x="%d" y="%.1f" font-size="13" font-weight="700" %s>%s</text>' % (x + lado * dx, (y0 + y1) / 2 + 4, 'text-anchor="end"' if lado < 0 else "", txt))


cota(PX0 - 2, 41.5, 30.2, "11.3 cm", -1, 8) if False else None
cota(PX0 + 8 * 0 + 150 - 150 + 0, 41.5, 30.2, "", 1, 0) if False else None
# cotas verticales (a la derecha de las placas, escalonadas para no chocar con las etiquetas)
cota(PX1 + 14, 34.5, 30.2, "4.3 cm", 1, 8)          # caja de la Jetson
a('<text x="%d" y="%.1f" font-size="11" fill="#444">(caja)</text>' % (PX1 + 22, Y(32.35) + 18))
cota(PX1 + 14, 29.9, 26.1, "", 1, 8)
a('<text x="%d" y="%.1f" font-size="13" font-weight="700">3.85 cm</text>' % (PX1 + 22, Y(26.9)))
cota(PX1 + 44, 33.5, 28.0, "5.5 cm", 1, 8)          # eje cámara - eje LiDAR
# cota del GPS a la izquierda del mástil, entre el mástil y los rótulos
cota(165, 41.5, 30.2, "11.3 cm", 1, 8)
a('<line x1="165" y1="%.1f" x2="%d" y2="%.1f" stroke="#888" stroke-dasharray="3 3"/><line x1="165" y1="%.1f" x2="%d" y2="%.1f" stroke="#888" stroke-dasharray="3 3"/>' % (Y(41.5), mx - 31, Y(41.5), Y(30.2), PX0, Y(30.2)))
# cota de 15 cm de las placas
a('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#000" stroke-width="1.2"/>' % (PX0, Y(26.1) + 78, PX1, Y(26.1) + 78))
a('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#000"/><line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#000"/>' % (PX0, Y(26.1) + 72, PX0, Y(26.1) + 84, PX1, Y(26.1) + 72, PX1, Y(26.1) + 84))
a('<text x="%.0f" y="%.1f" text-anchor="middle" font-size="13" font-weight="700">15 cm (placas)</text>' % ((PX0 + PX1) / 2, Y(26.1) + 98))
# zona inferior esquemática: placa de batería, batería, correas, patas
by = 520
a('<rect x="%d" y="%d" width="230" height="8" fill="#212121"/>' % (PX0 + 5, by))
a('<line x1="%d" y1="%.1f" x2="%d" y2="%d" stroke="#c9a227" stroke-width="5"/><line x1="%d" y1="%.1f" x2="%d" y2="%d" stroke="#c9a227" stroke-width="5"/>' % (PX0 + 25, Y(25.8), PX0 + 25, by, PX0 + 215, Y(25.8), PX0 + 215, by))
a('<rect x="%d" y="%d" width="210" height="62" rx="6" fill="#455a64" stroke="#263238" stroke-width="2"/>' % (PX0 + 15, by + 8))
a('<text x="%d" y="%d" text-anchor="middle" font-size="15" font-weight="700" fill="#fff">Batería LiPo 4S</text>' % (PX0 + 120, by + 44))
a('<rect x="%d" y="%d" width="13" height="74" fill="#1565c0" opacity="0.9"/><rect x="%d" y="%d" width="13" height="74" fill="#111" opacity="0.9"/>' % (PX0 + 45, by + 2, PX0 + 185, by + 2))
a('<text x="%d" y="%d" text-anchor="middle" font-size="11" fill="#1565c0" font-weight="700">correa azul</text><text x="%d" y="%d" text-anchor="middle" font-size="11" fill="#111" font-weight="700">correa negra</text>' % (PX0 + 51, by + 92, PX0 + 191, by + 92))
rotulo("Placa de la batería", 395, by + 8, 0, "#212121")
guia(399, by + 4, PX0 + 5, by + 4, "#212121")
a('<line x1="%d" y1="%.1f" x2="%d" y2="720" stroke="#37474f" stroke-width="9" stroke-linecap="round"/><line x1="%d" y1="%.1f" x2="%d" y2="720" stroke="#37474f" stroke-width="9" stroke-linecap="round"/>' % (PX0 + 6, Y(26.1) + 3, PX0 - 50, PX1 - 6, Y(26.1) + 3, PX1 + 50))
a('<line x1="110" y1="722" x2="900" y2="722" stroke="#9e9e9e" stroke-width="2.5"/>')
a('<text x="880" y="742" text-anchor="end" font-size="12" fill="#757575">superficie de apoyo (h = 0)</text>')
# cota de 28 cm con corte (fuera de escala)
a('<line x1="960" y1="%.1f" x2="960" y2="560" stroke="#000" stroke-width="1.2"/><path d="M952,566 L968,556 M952,574 L968,564" stroke="#000" stroke-width="1.5"/><line x1="960" y1="574" x2="960" y2="722" stroke="#000" stroke-width="1.2"/>' % Y(28))
a('<line x1="955" y1="%.1f" x2="965" y2="%.1f" stroke="#000"/><line x1="955" y1="722" x2="965" y2="722" stroke="#000"/>' % (Y(28), Y(28)))
a('<text x="950" y="650" text-anchor="end" font-size="13" font-weight="700">28 cm</text>')
a('<text x="950" y="666" text-anchor="end" font-size="11" fill="#555">(eje del LiDAR</text><text x="950" y="680" text-anchor="end" font-size="11" fill="#555">a la superficie;</text><text x="950" y="694" text-anchor="end" font-size="11" fill="#555">fuera de escala)</text>')
# pie
a('<rect x="40" y="756" width="920" height="34" rx="6" fill="#f5f5f5" stroke="#cfd8dc"/>')
a('<text x="500" y="778" text-anchor="middle" font-size="13" fill="#333">TF03: carcasa de 44 × 43 × 32 mm (hoja técnica del fabricante). La zona inferior (batería y patas) es esquemática; sus alturas no se midieron.</text>')
a('</svg>')
open("11_ubicacion_componentes_vista_lateral.svg", "w", encoding="utf-8").write("\n".join(o))
print("ok")
