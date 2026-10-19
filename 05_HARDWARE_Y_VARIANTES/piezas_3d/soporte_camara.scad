// Soporte de cámara (IMX219 CSI o cámara USB) — COMPILADO (OpenSCAD 2021.01), NO IMPRESO (ver VARIANTES.md).
// Ejes: X = adelante, Y = izquierda, Z = arriba.
//
// mira = "frente": placa base con la cuadrícula M2 de 10 mm de la cuna del pan-tilt (x = 15, 25, 35; y = -20..20)
//                  + placa vertical con la cámara mirando a +X (cámara frontal ancha o cámara del pan-tilt).
// mira = "abajo" : una sola placa que se atornilla bajo el chasis (ranuras M3), cámara mirando a -Z (cámara al piso).
// El lente queda del lado de afuera de la placa, así que no hay ventana: solo separadores de la placa a la tarjeta.
//
// FUENTE de las medidas del IMX219 (Raspberry Pi Camera Module 2 / V2.1): dibujo mecánico OFICIAL de Raspberry Pi,
//   https://pip-assets.raspberrypi.com/categories/1205-design-files/documents/RP-008149-DS-1-camera-module-2-mechanical-drawing.pdf
//   Placa de 23.862 x 25 mm, esquinas de radio 2; 4 agujeros de Φ2.2 a 2 mm de los bordes (12.5 x 21 mm entre centros); el lente
//   queda sobre la columna de agujeros de 14.5 mm y a 12.5 mm del borde de 25 (mitad de la placa). Altura total ≈ 9 mm (página
//   oficial: "Around 25 × 24 × 9 mm", https://www.raspberrypi.com/documentation/accessories/camera.html).
// PENDIENTE: los clones de IMX219 para Jetson (Arducam, Waveshare...) pueden tener otras medidas: comprobar el módulo que llegue.
// SUPUESTO: el lado largo del sensor (62.2°) va a lo largo de los 25 mm de la placa (no está en el dibujo).

modelo = "imx219";        // "imx219" | "usb_generica"
mira = "frente";          // "frente" | "abajo" | "doble" (piso + frontal ancha, variante F)
eje_largo_longitudinal = true;   // solo "abajo": el lado largo (62.2° de campo) va a lo largo del vuelo -> empalme con la cámara principal
$fn = 40;

// tarjeta: ancho, alto, espesor, agujeros [x, y] desde el centro de la tarjeta, diámetro, lente [x, y]
imx = [25.0, 23.862, 1.0, [[-10.5, -9.931], [10.5, -9.931], [-10.5, 2.569], [10.5, 2.569]], 2.2, [0, 2.569]];   // oficial; espesor de la placa 1.0 supuesto
usb = [32.0, 32.0, 1.6, [[-13, 13], [13, 13], [-13, -13], [13, -13]], 2.2, [0, 0]];   // PLACEHOLDER: medir la tuya
tj = (modelo == "imx219") ? imx : usb;
pw = tj[0]; ph = tj[1]; pt = tj[2]; hs = tj[3]; hd = tj[4];
sep = 3.5;                // altura de los separadores (deja sitio al conector plano de atrás)
pared = 3;

module separadores() {    // sobre la cara z=0 hacia +z, centrados en el origen de la tarjeta
    for (h = hs) translate([h[0], h[1], 0]) difference() {
        cylinder(d = 4.8, h = sep);
        translate([0, 0, 1]) cylinder(d = hd - 0.4, h = sep);   // agujero autorroscante
    }
}
module ranuras_m3(w, d) {   // 4 ranuras M3 para el chasis, largas en X (ajustan la separación)
    for (sx = [-1, 1]) for (sy = [-1, 1]) hull() for (dx = [-3, 3])
        translate([sx*(w/2 - 8) + dx, sy*(d/2 - 4), -1]) cylinder(d = 3.4, h = pared + 2);
}

if (mira == "frente") {
    bx = 44; by = 52;      // la base cubre las 3 x 5 posiciones de la cuadrícula (x = 15..35 -> desde 5 hasta 45)
    difference() {
        union() {
            translate([5, -by/2, 0]) cube([bx, by, pared]);                      // base: x de 5 a 49
            translate([5 + bx - pared, -(pw + 8)/2, 0]) cube([pared, pw + 8, ph + 8]);   // placa vertical al frente
        }
        for (x = [15, 25, 35]) for (y = [-20, -10, 0, 10, 20]) translate([x, y, -1]) cylinder(d = 2.2, h = pared + 2);
    }
    // separadores en la cara de adelante (+X) de la placa vertical: rotamos el sistema de la tarjeta
    translate([5 + bx, 0, 4 + ph/2]) rotate([90, 0, 90]) translate([-tj[5][0], -tj[5][1], 0]) separadores();   // x de la tarjeta -> Y, y -> Z, z -> X
} else if (mira == "doble") {
    // placa bajo el chasis con la cámara al piso colgando debajo y la frontal ancha en una pared que cuelga del borde delantero
    L = pw + 24 + 14; A = max(ph, pw) + 24;
    difference() {
        union() {
            translate([-L/2, -A/2, 0]) cube([L, A, pared]);
            translate([L/2 - pared, -(pw + 8)/2, -(ph + 8)]) cube([pared, pw + 8, ph + 8 + pared]);
        }
        ranuras_m3(L, A);
    }
    translate([-6, 0, 0]) mirror([0, 0, 1]) translate([-tj[5][0], -tj[5][1], 0]) separadores();             // al piso, lente centrado
    translate([L/2, 0, -(ph + 8)/2 + pared/2]) rotate([90, 0, 90]) translate([-tj[5][0], -tj[5][1], 0]) separadores();   // al frente
} else {
    // placa que va bajo el chasis; la tarjeta cuelga debajo (-Z)
    d_l = eje_largo_longitudinal ? pw : ph;     // largo de la tarjeta a lo largo de X
    L = d_l + 24; A = (eje_largo_longitudinal ? ph : pw) + 20;
    difference() {
        translate([-L/2, -A/2, 0]) cube([L, A, pared]);
        ranuras_m3(L, A);
    }
    mirror([0, 0, 1]) rotate([0, 0, eje_largo_longitudinal ? 0 : 90]) translate([-tj[5][0], -tj[5][1], 0]) separadores();   // el lente queda en el centro de la placa
}
