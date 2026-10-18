// Soporte del TF03 al chasis, versión "colgante" para el TF03 REAL de las fotos 14-18. COMPILADO (OpenSCAD 2021.01), NO IMPRESO.
// Ejes: X = adelante, Y = izquierda, Z = arriba. El TF03 cuelga DEBAJO de esta placa, atornillado por su propia placa con
// ranura (riel) o por sus agujeros de arriba, como hoy en el pod. La placa de arriba se sujeta al chasis con 4 ranuras M3.
// `cabeceo_deg` = inclinación del TF03 respecto al plano del chasis (D-064: −3°, nariz hacia abajo; el signo está por probar).
//
// TODO LO MARCADO PENDIENTE son valores de RELLENO, no medidas: se miden con calibrador (ver ESTADO_IMPRESION.md).
$fn = 40;
tf03_largo = 77;        // PENDIENTE (largo del TF03 a lo largo de la mirada; hoja de datos de memoria)
tf03_ancho = 40;        // PENDIENTE
riel_sep = 30;          // PENDIENTE: distancia entre los dos tornillos del riel del TF03
riel_eje = "X";         // PENDIENTE: la ranura del TF03 va a lo largo de X o de Y
tornillo_d = 3.4;       // PENDIENTE: M3
cabeceo_deg = -3;
t = 3;
L = max(tf03_largo * 0.6, riel_sep + 16) ;
W = max(tf03_ancho * 0.8, 36);
cuna_h = 8;             // altura de la cuña bajo el borde del frente (se calcula con el cabeceo)

module ranuras(sep, h, eje) {
    for (s = [-1, 1]) rotate([0, 0, eje == "X" ? 0 : 90]) translate([s * sep/2, 0, 0])
        hull() for (dy = [-2, 2]) translate([0, dy, -1]) cylinder(d = tornillo_d, h = h + 2);
}
union() {
    // placa al chasis
    difference() {
        translate([-L/2 - 12, -W/2 - 6, 0]) cube([L + 24, W + 12, t]);
        for (sx = [-1, 1]) for (sy = [-1, 1]) hull() for (dx = [-3, 3])
            translate([sx * (L/2 + 6) + dx, sy * (W/2 + 2.5), -1]) cylinder(d = 3.4, h = t + 2);
    }
    // placa inclinada que lleva el TF03 (colgado debajo), unida por una cuña
    translate([0, 0, 0]) rotate([0, -cabeceo_deg, 0]) translate([0, 0, -t - 1]) difference() {
        translate([-L/2, -W/2, 0]) cube([L, W, t]);
        translate([0, 0, 0]) ranuras(riel_sep, t, riel_eje);
    }
    // columnas de unión (a las esquinas de las dos placas)
    for (sx = [-1, 1]) for (sy = [-1, 1]) hull() {
        translate([sx * (L/2 - 3), sy * (W/2 - 3), 0]) cylinder(d = 5, h = 0.5);
        rotate([0, -cabeceo_deg, 0]) translate([sx * (L/2 - 3), sy * (W/2 - 3), -1.5]) cylinder(d = 5, h = 0.5);
    }
}
