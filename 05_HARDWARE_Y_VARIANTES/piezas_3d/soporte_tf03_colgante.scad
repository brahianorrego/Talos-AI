// Soporte del TF03 al chasis para el TF03 REAL, con las roscas M3 del propio sensor. COMPILADO (OpenSCAD 2021.01), NO IMPRESO.
// Medidas de la ficha técnica oficial (08_EVIDENCIA_Y_DIAGRAMAS/fichas_tecnicas/TF03_dimensiones.png): cuerpo 44 de ancho,
// 42.9 de largo (el eje óptico va a lo largo de este lado: la ventana grande en un extremo y el cable en el opuesto) y 31.8 de
// fondo; 6 roscas M3 de 3.5 mm de hondo en una cara de 44 x 42.9, en dos columnas a 38 mm de un borde (o sea a 6 mm del otro:
// 32 mm entre columnas) y tres filas a 10 mm. LO QUE ES DE DIBUJO APROXIMADO: la distancia de la primera fila al extremo de la
// ventana (`fila0`, ≈7 mm contada con los píxeles del dibujo). Hay que comprobarlo en el sensor real.
//
// Ejes: X = adelante (la ventana del TF03 mira a +X), Y = izquierda, Z = arriba. El TF03 cuelga BAJO la placa, pegado por su
// cara roscada a una pared vertical; tornillos M3 x 6 desde el otro lado de la pared (3 mm de pared + 3 mm de rosca).
// `cabeceo_deg` inclina pared y sensor respecto a la placa (D-064: −3°, nariz hacia abajo; el signo está por probar).
$fn = 40;
W = 44; Lt = 42.9; D = 31.8;     // TF03: ancho (vertical en la pared), largo (a lo largo de la mirada), fondo
col_sep = 32;                    // entre columnas de roscas
fila_sep = 10; filas = 3;
fila0 = 7;                       // DE DIBUJO, APROXIMADO: de la ventana a la primera fila (pendiente comprobar)
tornillo_d = 3.4;
t = 3;                           // espesor de la placa y de la pared
cabeceo_deg = -3;
Lp = Lt + 10;                    // largo de la placa y de la pared (en X)
Wp = D + t + 12;                 // ancho de la placa (en Y): cubre el sensor y deja orejas de tornillo
x_f = Lp/2 - 5;                  // extremo de la ventana del TF03 (x)

module pared() {                 // pared vertical en y ∈ [0, t], colgando de z = 0 hacia abajo
    difference() {
        translate([-Lp/2, 0, -(W + 8)]) cube([Lp, t, W + 8 + 1]);
        for (c = [-1, 1]) for (f = [0 : filas - 1])
            translate([x_f - fila0 - f * fila_sep, -1, -(4 + 6) - (c > 0 ? 0 : col_sep)]) rotate([-90, 0, 0]) cylinder(d = tornillo_d, h = t + 2);
    }
}
union() {
    difference() {
        translate([-Lp/2, 0, 0]) cube([Lp, Wp, t]);                    // placa al chasis
        for (sx = [-1, 1]) for (y = [4, Wp - 4]) hull() for (dx = [-2.5, 2.5])
            translate([sx * (Lp/2 - 7) + dx, y, -1]) cylinder(d = 3.4, h = t + 2);
    }
    rotate([0, -cabeceo_deg, 0]) translate([0, 0, 0]) pared();
}
