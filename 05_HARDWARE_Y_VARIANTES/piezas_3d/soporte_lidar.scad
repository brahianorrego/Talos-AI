// Soporte de LiDAR (TF-Luna o TF03) — NO COMPILADO NI IMPRESO (ver VARIANTES.md).
// Ejes: X = adelante (el frente del sensor mira a +X), Y = izquierda, Z = arriba. Cabeceo + = frente hacia arriba.
//
// Cuna abierta por arriba y por el frente (las lentes quedan libres), pared trasera baja con muesca para el cable,
// y ranuras para amarras plásticas que sujetan el sensor sin depender de sus agujeros de montaje.
// fijacion = "cuadricula": base con agujeros M2 de 10 mm para la cuna del pan-tilt (x = 15, 25, 35; y = -20..20).
// fijacion = "chasis"    : base con 4 ranuras M3 para el chasis; `cabeceo_deg` inclina el sensor (cuña) para dejarlo a +1°.
//
// MEDIR: las medidas del sensor son de hoja de datos recordada (TF-Luna 35 x 18 x 21 mm) o PROVISIONALES (TF03).
// Pesa tu unidad y mídela con calibrador antes de imprimir; solo cambian 3 números.

modelo = "luna";                 // "luna" | "tf03"
fijacion = "cuadricula";         // "cuadricula" | "chasis"
cabeceo_deg = 0;                 // solo "chasis": inclinación del sensor (+1 en la variante C/D/E/F del TF03)
$fn = 40;

dims = (modelo == "luna") ? [35, 18, 21] : [77, 40, 40];   // largo (X), ancho (Y), alto (Z) — TF03 PROVISIONAL
S_L = dims[0]; S_W = dims[1]; S_H = dims[2];
tol = 0.4;
pared = 2.5;
base_t = 3;
alto_pared = 0.6 * S_H;
amarra_w = 4.2; amarra_t = 1.6;  // ranura para amarra plástica de 3.6 mm de ancho

BL = S_L + 2*pared + (fijacion == "chasis" ? 20 : 0);
BW = S_W + 2*pared + 2*(amarra_t + 4) + 8;

module cuna() {
    difference() {
        union() {
            translate([0, -BW/2, 0]) cube([BL, BW, base_t]);
            // paredes laterales y pared trasera baja
            for (s = [-1, 1]) translate([pared, s*(S_W/2 + tol) + (s > 0 ? 0 : -pared), base_t]) cube([S_L, pared, alto_pared]);
            translate([0, -(S_W/2 + tol + pared), base_t]) cube([pared, S_W + 2*(tol + pared), alto_pared * 0.5]);
        }
        // muesca del cable en la pared trasera
        translate([-1, -4, base_t + 2]) cube([pared + 2, 8, alto_pared]);
        // ranuras de amarra: 2 posiciones a lo largo del sensor, a cada lado
        for (px = [pared + S_L*0.25, pared + S_L*0.75]) for (s = [-1, 1])
            translate([px - amarra_w/2, s*(S_W/2 + tol + pared + 3) - amarra_t/2, -1]) cube([amarra_w, amarra_t, base_t + 2]);
        if (fijacion == "cuadricula") {
            for (x = [15, 25, 35]) for (y = [-10, 0, 10]) translate([x, y, -1]) cylinder(d = 2.2, h = base_t + 2);   // y = ±20 no cabe en la base del Luna
        }
    }
}

if (fijacion == "cuadricula") {
    cuna();
} else {
    // placa plana con ranuras M3 + cuña que lleva la cuna inclinada `cabeceo_deg` alrededor de su borde trasero
    difference() {
        union() {
            translate([0, -BW/2, 0]) cube([BL, BW, base_t]);
            translate([0, 0, base_t]) hull() {
                translate([0, -BW/2, 0]) cube([BL, BW, 0.01]);
                rotate([0, -cabeceo_deg, 0]) translate([0, -BW/2, base_t]) cube([BL, BW, 0.01]);
            }
            translate([0, 0, base_t]) rotate([0, -cabeceo_deg, 0]) cuna();
        }
        for (sx = [-1, 1]) for (sy = [-1, 1]) hull() for (dx = [-3, 3])
            translate([BL/2 + sx*(BL/2 - 6) + dx, sy*(BW/2 - 3.5), -1]) cylinder(d = 3.4, h = base_t + 2);
    }
}
