// Pan-tilt de 2 servos (MG90D) para el plus: variantes D, E y F de 05_HARDWARE_Y_VARIANTES/VARIANTES.md
// OpenSCAD 2021.01 o más nuevo. COMPILADA (2021.01), NO IMPRESA: ver "Qué no se puede verificar" en VARIANTES.md.
//
// Ejes (como el dron): X = adelante, Y = izquierda, Z = arriba. Cabeceo POSITIVO = la cámara mira hacia ARRIBA.
// Tres piezas para imprimir (cambia `parte`, F5 para ver, F6 y exportar STL):
//   "base"        placa al chasis + soporte del servo de PAN (eje vertical)
//   "plataforma"  mesa que gira con el PAN + dos mejillas que sostienen el servo de TILT
//   "cuna"        cuna que gira con el TILT: lleva la cámara y el TF-Luna, y el PIN del tope mecánico
//   "vista"       las tres armadas, con los servos en gris (para mirar; usa `angulo_vista` para ver el tope)
// Material sugerido: PETG o PLA+, 0.2 mm de capa, 3 perímetros, 30-40 % de relleno. Tornillos: M2 autorroscantes
// (servo, cuerno), M3 con tuerca (placa al chasis).
//
// TODAS las medidas marcadas "MEDIR" salen de la hoja de datos del MG90D o de memoria: mide con calibrador
// los servos y el cuerno que te lleguen y cambia solo estos números.

parte = "vista";
angulo_vista = 0;        // grados de cabeceo para la vista armada (prueba -45 y 15: el pin debe tocar el final de la ranura)
$fn = 48;

// ---- servo MG90D (cuerpo sin cuerno) — MEDIR ----
sv_L = 22.8;             // largo del cuerpo
sv_W = 12.2;             // ancho
sv_H = 22.5;             // alto, de la cara de abajo a la cara de arriba del cuerpo
sv_eje = 5.9;            // del eje al extremo corto del cuerpo
sv_oreja_tot = 32.5;     // largo total con orejas
sv_oreja_t = 2.5;        // espesor de la oreja
sv_oreja_z = 4.5;        // de la cara de arriba del cuerpo a la cara de arriba de la oreja
sv_oreja_sep = 27.5;     // separación de los tornillos de las orejas
sv_tol = 0.3;            // holgura del hueco (impresora)
cuerno_h = 3.5;          // alto del cuerno sobre la cara de arriba del cuerpo — MEDIR
cuerno_r = 7.0;          // radio de los 4 agujeros del cuerno en cruz — MEDIR

// ---- tope mecánico (regla dura 1: pitch entre -45° y +15°) ----
tilt_min = -45;
tilt_max = 15;
margen_interior_deg = 1.0;  // los topes quedan 1° DENTRO del rango, para que la tolerancia de impresión nunca lo amplíe
R_tope = 16;                // radio del pin respecto al eje del tilt
pin_d = 4;

// ---- geometría ----
cuna_w = 56;             // ancho exterior de la cuna: cabe el TF-Luna (18) + una cámara CSI (25) lado a lado
pared_cuna = 2.5;
pared_A = 4;             // pared de la cuna donde se atornilla el cuerno (más gruesa)
gap_cuerno = cuerno_h + 0.5;   // entre la mejilla del servo y la pared A
gap_B = 0.6;
mejilla_B = 3;
z_eje_rel = 38;          // altura del eje del tilt sobre la plataforma (con 45° de bajada la cuna no toca la plataforma)
deck_x0 = 8;
deck_x1 = 45;            // la carga llega hasta aquí
deck_t = 3;
paso_agujeros = 10;      // cuadrícula M2 de la cubierta: x = 15, 25, 35 e y = -20..20 de 10 en 10 (los soportes de cámara y LiDAR usan este paso)
base_x = 64; base_y = 56; placa_t = 3;
plataforma_t = 3;

// ---- derivados (marco del servo de PAN: eje en el origen, cara de arriba del cuerpo en z = 0) ----
z_placa_sup = -sv_H - 1;
zp0 = cuerno_h + 0.5;                    // fondo de la plataforma
z_eje = zp0 + plataforma_t + z_eje_rel;  // eje del tilt
yA = -(cuna_w/2 + gap_cuerno);           // cara interior de la mejilla A (servo de tilt)
yB = cuna_w/2 + gap_B;                   // cara interior de la mejilla B (ranura del tope)
delta = asin(pin_d/2 / R_tope);          // ángulo que el pin ocupa a cada lado de su centro
a_min = tilt_min + margen_interior_deg;
a_max = tilt_max - margen_interior_deg;

// ---- ayudas de forma (diseño): placas de esquinas redondas con el canto de arriba biselado ----
module rrect2d(x0, x1, y0, y1, r) { hull() for (x = [x0 + r, x1 - r]) for (y = [y0 + r, y1 - r]) translate([x, y]) circle(r); }
module placa_r(x0, x1, y0, y1, z0, h, r, ch = 0.8) {
    hull() {
        translate([0, 0, z0]) linear_extrude(h - ch) rrect2d(x0, x1, y0, y1, r);
        translate([0, 0, z0]) linear_extrude(h) rrect2d(x0 + ch, x1 - ch, y0 + ch, y1 - ch, max(r - ch, 0.5));
    }
}
module ventana2d(x1, x2, z, r) { hull() for (x = [x1, x2]) translate([x, z]) circle(r); }   // ventana "estadio"
// mejilla: perfil alado en el plano XZ, de espesor t que empieza en y0 y va hacia +Y
module mejilla(y0, t) {
    translate([0, y0 + t, 0]) rotate([90, 0, 0]) linear_extrude(t) difference() {
        polygon([[-26, zp0], [20, zp0], [26, zp0 + 12], [26, z_eje + 16], [14, z_eje + 26], [-10, z_eje + 26], [-26, z_eje + 10]]);
        ventana2d(-17, 3, zp0 + 13, 4);
        ventana2d(-17, -9, zp0 + 24, 2.2);
    }
}

// ---- servo ----
module servo_fantasma() {
    color("gray", 0.5) {
        translate([-sv_eje, -sv_W/2, -sv_H]) cube([sv_L, sv_W, sv_H]);
        translate([sv_L/2 - sv_eje - sv_oreja_tot/2, -sv_W/2, -sv_oreja_z - sv_oreja_t])
            cube([sv_oreja_tot, sv_W, sv_oreja_t]);
        cylinder(d = 4.8, h = cuerno_h);
    }
}
// hueco del cuerpo entre z1 (abajo) y z2 (arriba) + agujeros autorroscantes de las orejas entre z3 y z4
module servo_hueco(z1, z2, z3, z4) {
    translate([-sv_eje - sv_tol, -sv_W/2 - sv_tol, z1]) cube([sv_L + 2*sv_tol, sv_W + 2*sv_tol, z2 - z1]);
    for (s = [-1, 1])
        translate([sv_L/2 - sv_eje + s*sv_oreja_sep/2, 0, z3]) cylinder(d = 1.8, h = z4 - z3);
}
// Transformación del servo de TILT: eje del servo a lo largo de +Y, cuerpo hacia atrás (-X)
module en_tilt() {
    translate([0, yA, z_eje]) rotate([0, 180, 0]) rotate([-90, 0, 0]) children();
}

// ---- piezas ----
module base_srv() {
    // placa con 4 ranuras M3 (largas en X: ajustan la separación al chasis) + bloque del servo de PAN
    difference() {
        union() {
            placa_r(-base_x/2, base_x/2, -base_y/2, base_y/2, z_placa_sup - placa_t, placa_t, 6);
            placa_r(-sv_eje - 6, sv_L - sv_eje + 6, -sv_W/2 - 3, sv_W/2 + 3, z_placa_sup, -sv_oreja_z - z_placa_sup, 3, 1.0);  // ancho para las orejas
        }
        servo_hueco(z_placa_sup + 1, -sv_oreja_z + 1, -sv_oreja_z - 9, -sv_oreja_z + 0.01);
        for (sx = [-1, 1]) for (sy = [-1, 1])
            hull() for (dx = [-4, 4])
                translate([sx*(base_x/2 - 9) + dx, sy*(base_y/2 - 6), z_placa_sup - placa_t - 1]) cylinder(d = 3.4, h = placa_t + 2);
        // ventanas "estadio" de aligeramiento a los lados del bloque (diseño)
        for (sy = [-1, 1]) hull() for (dx = [-8, 8]) translate([5.5 + dx, sy * 22, z_placa_sup - placa_t - 1]) cylinder(d = 5, h = placa_t + 2);
        // paso del cable del servo
        translate([sv_L - sv_eje - 2, -3, z_placa_sup]) cube([8, 6, 5]);
    }
}
module plataforma_srv() {
    difference() {
        union() {
            placa_r(-26, 26, yA - sv_oreja_z, yB + mejilla_B, zp0, plataforma_t, 6);
            // mejilla A (servo de tilt, espesor = sv_oreja_z) y mejilla B (ranura del tope), con perfil alado y ventanas
            mejilla(yA - sv_oreja_z, sv_oreja_z);
            mejilla(yB, mejilla_B);
        }
        // 4 agujeros del cuerno del servo de PAN
        for (a = [0, 90, 180, 270]) translate([cuerno_r*cos(a), cuerno_r*sin(a), zp0 - 1]) cylinder(d = 2.2, h = plataforma_t + 2);
        // hueco del servo de tilt en la mejilla A
        en_tilt() servo_hueco(-sv_oreja_z - 0.1, 1, -sv_oreja_z - 0.1, -1);
        // pivote M2 en la mejilla B
        translate([0, yB - 1, z_eje]) rotate([-90, 0, 0]) cylinder(d = 2.4, h = mejilla_B + 2);
        // ranura de arco del tope: de a_min-delta a a_max+delta, ancho radial = pin + holgura
        translate([0, yB + mejilla_B + 1, 0]) rotate([90, 0, 0]) linear_extrude(mejilla_B + 2)
            translate([0, z_eje]) polygon(arco(R_tope - pin_d/2 - 0.2, R_tope + pin_d/2 + 0.2, a_min - delta, a_max + delta));
    }
}
function arco(r1, r2, a1, a2, n = 24) = concat(
    [for (i = [0:n]) [r2*cos(a1 + (a2 - a1)*i/n), r2*sin(a1 + (a2 - a1)*i/n)]],
    [for (i = [n:-1:0]) [r1*cos(a1 + (a2 - a1)*i/n), r1*sin(a1 + (a2 - a1)*i/n)]]);

module cuna_tilt() {
    // marco del tilt: eje en el origen, cabeceo 0 = mira a +X
    difference() {
        union() {
            // pared A (cuerno) y pared B (pivote + pin)
            translate([0, -cuna_w/2, 0]) rotate([90, 0, 0]) mirror([0, 0, 1]) linear_extrude(pared_A) pared_2d();
            translate([0, cuna_w/2 - pared_cuna, 0]) rotate([90, 0, 0]) mirror([0, 0, 1]) linear_extrude(pared_cuna) pared_2d();
            // cubierta
            placa_r(deck_x0, deck_x1, -cuna_w/2, cuna_w/2, -deck_t, deck_t, 4, 0.8);
            // pin del tope: sale de la pared B hacia la mejilla B
            translate([R_tope, cuna_w/2, 0]) rotate([-90, 0, 0]) cylinder(d = pin_d, h = gap_B + mejilla_B - 0.5);
        }
        // pivote M2 y agujeros del cuerno
        translate([0, -cuna_w/2 - 1, 0]) rotate([-90, 0, 0]) cylinder(d = 1.8, h = pared_A + 2);
        for (a = [0, 90, 180, 270]) translate([cuerno_r*cos(a), -cuna_w/2 - 1, cuerno_r*sin(a)]) rotate([-90, 0, 0]) cylinder(d = 1.8, h = pared_A + 2);
        translate([0, cuna_w/2 - pared_cuna - 1, 0]) rotate([-90, 0, 0]) cylinder(d = 2.4, h = pared_cuna + gap_B + 4);
        // cuadrícula M2 de la cubierta
        for (x = [15, 25, 35]) for (y = [-20, -10, 0, 10, 20])
            translate([x, y, -deck_t - 1]) cylinder(d = 2.2, h = deck_t + 2);
    }
}
module pared_2d() {
    difference() {
        offset(r = 2) offset(delta = -2) hull() { circle(r = 14); translate([deck_x1 - 4, -deck_t]) square([4, 15]); }
        ventana2d(22, 36, 6.5, 2.4);   // ventana "estadio" de aligeramiento (diseño)
    }
}

// ---- salida ----
if (parte == "base") translate([0, 0, sv_H + 1 + placa_t]) base_srv();
if (parte == "plataforma") translate([0, 0, -zp0]) plataforma_srv();
if (parte == "cuna") translate([0, 0, cuna_w/2]) rotate([90, 0, 0]) cuna_tilt();   // apoyada sobre la pared A para imprimir
if (parte == "asm_base") base_srv();
if (parte == "asm_plataforma") plataforma_srv();
if (parte == "asm_cuna") cuna_tilt();   // marco de la cuna: el eje del tilt en el origen
if (parte == "vista") {
    base_srv();
    servo_fantasma();
    plataforma_srv();
    en_tilt() servo_fantasma();
    color("orange") translate([0, 0, z_eje]) rotate([0, -angulo_vista, 0]) cuna_tilt();
}
