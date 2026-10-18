// Soporte del TF-Luna para el pod del gimbal BaseCam (variante C). COMPILADO (OpenSCAD 2021.01), NO IMPRESO.
// Medidas de la ficha técnica oficial (08_EVIDENCIA_Y_DIAGRAMAS/fichas_tecnicas/TFLuna_dimensiones.png): cuerpo 35 de ancho
// con orejas (26.5 sin ellas), 21.25 de alto, 13.5 de fondo con las lentes (12 el cuerpo); dos agujeros Φ2.2 en las orejas,
// 30.5 mm entre ellos y 9 mm por debajo del borde de arriba; orejas de 2 mm de espesor en la cara de ATRÁS; lentes Φ10.5 a
// 10.5 mm entre centros; conector de 10.5 x 6.8 mm. Los agujeros de las orejas son paralelos a la mirada: el Luna se atornilla
// por DELANTE a una placa que queda DETRÁS de él (2 tornillos M2 x 8, autorroscantes).
//
// Ejes: X = adelante (lentes hacia +X, igual que la cámara USB), Y = izquierda, Z = arriba.
// Forma: una L. Placa vertical trasera (para los 2 tornillos del Luna) + suelo con ventana para el conector y el cable +
// aleta trasera con dos agujeros alargados para atornillar al RIEL del pod (tornillos M3 con tuerca en bolsillo hexagonal).
//
// PENDIENTES (fotos de Brahian, no de la ficha): riel_sep, riel_eje, tornillo_d. Los valores de abajo son de RELLENO.
$fn = 40;
// ---- TF-Luna (ficha oficial) ----
L_ancho = 35; L_alto = 21.25; L_fondo = 13.5; oreja_sep = 30.5; oreja_z = 9; oreja_t = 2; oreja_d = 2.2;
// ---- riel del pod: PENDIENTE (relleno) ----
riel_sep = 26;                  // distancia entre los dos tornillos del riel
riel_eje = "X";                 // la ranura va a lo largo de X o de Y
tornillo_d = 3.4;               // M3
// ---- pieza ----
t = 3;                          // espesor de placa y suelo
hueco_abajo = 1.5;              // el Luna no toca el suelo (conector y cable)
aleta = riel_eje == "X" ? riel_sep + 14 : 20;   // largo de la aleta trasera (hacia atrás, en -X)
W = L_ancho + 10;

module agujeros_riel() {
    for (s = [-1, 1]) translate([-aleta/2 - t, 0, 0]) rotate([0, 0, riel_eje == "X" ? 0 : 90]) translate([s * riel_sep/2, 0, 0])
        hull() for (d = [-2, 2]) translate([0, d, -1]) cylinder(d = tornillo_d, h = t + 2);
}
module bolsillos_tuerca() {      // tuerca M3 (5.5 entre caras) hundida 2.6 mm en la cara de arriba de la aleta
    for (s = [-1, 1]) translate([-aleta/2 - t, 0, 0]) rotate([0, 0, riel_eje == "X" ? 0 : 90]) translate([s * riel_sep/2, 0, 0])
        hull() for (d = [-2, 2]) translate([0, d, t - 2.6]) cylinder(d = 6.4, h = 2.7, $fn = 6);
}
difference() {
    union() {
        translate([-aleta - t, -W/2, 0]) cube([aleta + t + L_fondo + 2, W, t]);                  // aleta + suelo
        translate([-t, -W/2, 0]) cube([t, W, t + hueco_abajo + L_alto + 4]);                      // placa vertical trasera
    }
    agujeros_riel();
    bolsillos_tuerca();
    // ventana del suelo bajo el Luna (conector y cable)
    translate([1, -7, -1]) cube([L_fondo - 3, 14, t + 2]);
    // los 2 agujeros del Luna (autorroscantes para M2) en la placa vertical, 9 mm bajo el borde de arriba del Luna
    for (s = [-1, 1]) translate([-t - 1, s * oreja_sep/2, t + hueco_abajo + L_alto - oreja_z]) rotate([0, 90, 0]) cylinder(d = 1.8, h = t + 2);
}
