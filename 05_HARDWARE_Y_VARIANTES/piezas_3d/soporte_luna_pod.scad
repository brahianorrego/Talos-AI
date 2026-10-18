// Soporte del TF-Luna para el pod del gimbal BaseCam (variante C). COMPILADO (OpenSCAD 2021.01), NO IMPRESO.
// Ejes: X = adelante (la lente del Luna mira a +X, igual que la cámara USB), Y = izquierda, Z = arriba.
//
// Una sola placa liviana que se atornilla (o se amarra) a la parte de arriba del pod, lo más cerca posible del eje del
// pitch, con el Luna mirando donde mira la cámara. Pesa del orden de 4-6 g sin contar el Luna (≈5 g): no hace palanca.
//   - Dos ranuras de tornillo (M2) en los extremos, largas en Y: se centra el Luna sobre la lente de la cámara.
//   - Dos ranuras de amarra plástica por lado para sujetar el Luna (no dependen de sus agujeros).
//   - Aliviadero del cable: un puente trasero por donde pasa el cable fino del Luna con holgura, y una amarra que lo
//     sujeta a la placa, para que el tirón del cable no se transmita al sensor ni al pitch (deja un lazo flojo).
//
// MEDIR: el pod real (altura libre, tornillos, cámara USB), el Luna (35 x 18 x 21 mm: hoja de datos de memoria) y la
// distancia lente-cámara a lente-Luna (`separacion_z`, solo informativa aquí: la fija dónde atornillas la placa).

$fn = 40;
S_L = 35; S_W = 18; S_H = 21;   // TF-Luna — MEDIR
tol = 0.4;
t = 2.4;                        // espesor de la placa
pared = 1.6; alto_pared = 7;
amarra_w = 4.2; amarra_t = 1.6;
margen = 6;                     // placa más larga que el Luna para las ranuras de tornillo
L = S_L + 2 * margen;           // 47
W = S_W + 2 * (pared + tol) + 2 * 8;   // 8 mm a cada lado para las amarras

module ranura(x, largo_y, d) { hull() for (dy = [-largo_y/2, largo_y/2]) translate([x, dy, -1]) cylinder(d = d, h = t + 2); }

difference() {
    union() {
        translate([0, -W/2, 0]) cube([L, W, t]);
        // paredes laterales cortas
        for (s = [-1, 1]) translate([margen, s * (S_W/2 + tol) + (s > 0 ? 0 : -pared), t]) cube([S_L, pared, alto_pared]);
        // tope trasero con aliviadero: puente por el que pasa el cable
        translate([margen - pared - 0.2, -(S_W/2 + tol + pared), t]) cube([pared, S_W + 2*(tol + pared), alto_pared]);
    }
    // ventana del puente para el cable (4 x 6 mm) a la altura del conector
    translate([margen - pared - 1, -3, t + 1.5]) cube([pared + 2, 6, 4]);
    // ranuras de tornillo M2 en los extremos (largas en Y)
    ranura(margen/2, 8, 2.4);
    ranura(L - margen/2, 8, 2.4);
    // ranuras de amarra a cada lado, dos posiciones a lo largo del Luna
    for (px = [margen + S_L*0.3, margen + S_L*0.7]) for (s = [-1, 1])
        translate([px - amarra_w/2, s * (S_W/2 + tol + pared + 3) - amarra_t/2, -1]) cube([amarra_w, amarra_t, t + 2]);
    // ranura de amarra del cable, detrás del puente
    translate([margen/2 - amarra_w/2, -9, -1]) cube([amarra_w, amarra_t, t + 2]);
}
