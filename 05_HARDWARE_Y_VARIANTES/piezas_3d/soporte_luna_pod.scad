// Soporte del TF-Luna para el pod del gimbal BaseCam (variante C). COMPILADO (OpenSCAD 2021.01), NO IMPRESO.
// Ejes: X = adelante (la lente del Luna mira a +X, igual que la cámara USB), Y = izquierda, Z = arriba.
//
// FOTOS 14-18 (2026-10-18): el pod tiene una placa negra con una ranura larga (riel) y dos tornillos de cabeza cilíndrica en
// los extremos de la ranura; hoy el TF03 cuelga de esa placa y la cámara USB (placa verde redonda) va encima, atornillada al
// riel. En la variante C el TF03 se va y el TF-Luna ocupa su lugar. Esta pieza se atornilla por esa ranura con dos tornillos
// (agujeros alargados separados `riel_sep`, a lo largo de `riel_eje`); las tuercas quedan escondidas en un bolsillo hexagonal
// bajo el Luna (por eso hay un pedestal de `piso_extra` mm).
// PENDIENTES de medir (los valores de abajo son de RELLENO, no de la pieza real): riel_sep, riel_eje, tornillo_d.
//
// Ligera (≈5-8 g sin el Luna): no hace palanca. Aliviadero del cable: puente trasero con ventana y una amarra.
// MEDIR también: el Luna (35 x 18 x 21 mm: hoja de datos de memoria) y la altura libre bajo/sobre el riel.

$fn = 40;
S_L = 35; S_W = 18; S_H = 21;   // TF-Luna — MEDIR
riel_sep = 26;                  // PENDIENTE: distancia entre los dos tornillos del riel (de relleno)
riel_eje = "X";                 // PENDIENTE: la ranura va a lo largo de X (adelante) o de Y (de lado)
tornillo_d = 3.4;               // PENDIENTE: M3 si los tornillos son M3
tol = 0.4;
t = 2.4;                        // espesor de la placa
piso_extra = 3.2;               // pedestal bajo el Luna: aloja las tuercas
pared = 1.6; alto_pared = 7;
amarra_w = 4.2; amarra_t = 1.6;
margen = 6;
L = max(S_L + 2 * margen, riel_sep + 14);
W = S_W + 2 * (pared + tol) + 2 * 8;
z0 = t + piso_extra;            // el Luna se apoya aquí
x0 = (L - S_L) / 2;             // inicio del Luna en X

module agujeros_riel(h) {       // dos agujeros alargados (4 mm de recorrido)
    for (s = [-1, 1]) translate([L/2, 0, 0]) rotate([0, 0, riel_eje == "X" ? 0 : 90]) translate([s * riel_sep/2, 0, 0])
        hull() for (dy = [-2, 2]) translate([0, dy, -1]) cylinder(d = tornillo_d, h = h + 2);
}

difference() {
    union() {
        translate([0, -W/2, 0]) cube([L, W, t]);
        translate([x0 - 0.2, -(S_W/2 + tol) - 0.2, 0]) cube([S_L + 0.4, S_W + 2*tol + 0.4, z0]);   // pedestal (solapa 0.2 con las paredes)
        for (s = [-1, 1]) translate([x0, s * (S_W/2 + tol) + (s > 0 ? 0 : -pared), t - 0.1]) cube([S_L, pared, alto_pared + piso_extra + 0.1]);
        translate([x0 - pared, -(S_W/2 + tol + pared), t - 0.1]) cube([pared + 0.2, S_W + 2*(tol + pared), alto_pared + piso_extra + 0.1]);   // puente trasero
    }
    agujeros_riel(z0);
    // bolsillo hexagonal de tuerca M3 (5.5 mm entre caras, 2.6 de hondo) bajo el Luna: se pierde en el pedestal
    for (s = [-1, 1]) translate([L/2, 0, 0]) rotate([0, 0, riel_eje == "X" ? 0 : 90]) translate([s * riel_sep/2, 0, 0])
        hull() for (dy = [-2, 2]) translate([0, dy, z0 - 2.6]) cylinder(d = 6.4, h = 2.7, $fn = 6);
    // ventana del puente para el cable
    translate([x0 - pared - 1, -3, z0 + 1.5]) cube([pared + 2, 6, 4]);
    // amarras: dos a cada lado del Luna y una para el cable
    for (px = [x0 + S_L*0.3, x0 + S_L*0.7]) for (s = [-1, 1])
        translate([px - amarra_w/2, s * (S_W/2 + tol + pared + 3) - amarra_t/2, -1]) cube([amarra_w, amarra_t, t + 2]);
    translate([x0/2 - amarra_w/2, -9, -1]) cube([amarra_w, amarra_t, t + 2]);
}
