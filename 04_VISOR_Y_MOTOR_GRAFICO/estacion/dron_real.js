// El dron REAL en la estación de tierra: reemplaza el dron decorativo del visor clásico por el modelo hecho con las fotos de
// Brahian (modelo_dron/dron_real.py -> dron_real.json, copia en esta carpeta). Se carga después de index.html y usa sus variables
// (dron, chasis, rotores, leds, ventilador, gimbalPitch, estrobo, etqDron, halo, MODO_DRON): se quita la geometría vieja (no solo se oculta,
// porque el reproductor vuelve a mostrar leds y estrobo en cada cuadro), pero siguen girando las hélices.
// Tres modelos (D-072/D-073): "minimo" (variante G: CSI y TF03 fijos), "plus" (variante H: pan-tilt de 2 servos con la CSI y el TF-Luna encima, que se
// MUEVEN con el pan y el tilt de la partida: window.PANTILT) y "gimbal" (el de antes: BaseCam con el TF03 y la USB, historia). Se elige con
// MODO_DRON (botón "Dron" de camaras.js o ?dron=minimo|plus|gimbal; por omisión plus) y window.DRON_CAMBIAR(v) lo reconstruye sin recargar.
// Marco del JSON: x adelante, y izquierda, z arriba  ->  three.js: X = x, Y = z, Z = -y (como mundo()).
// Con ?dron=viejo se ve el dron decorativo de antes.
"use strict";
(async () => {
  if (new URLSearchParams(location.search).get("dron") === "viejo") return;
  let modelo;
  try { modelo = await (await fetch("dron_real.json", { cache: "no-store" })).json(); } catch (e) { console.warn("Dron real no disponible; queda el decorativo:", e); return; }
  const tres = (x, y, z) => new THREE.Vector3(x, z, -y);
  const PIVOTE = tres(0.150, 0.0, -0.200);                    // eje del motor de pitch del gimbal viejo
  const GIMBAL = new Set(["gimbal_plataforma", "tf03", "camara_usb_placa", "camara_usb_lente", "gimbal_motor_pitch"]);
  const CLAVE = { minimo: "piezas", plus: "piezas_plus", gimbal: "piezas_gimbal" };
  const mats = {};
  const material = p => {
    const k = p.color + (p.translucido ? "_t" : "");
    if (!mats[k]) {
      const c = modelo.colores[p.color];
      mats[k] = new THREE.MeshStandardMaterial({ color: new THREE.Color(c[0], c[1], c[2]), roughness: ["carbono", "rojo", "espuma"].includes(p.color) ? 0.3 : 0.55,
        metalness: p.color === "dorado" ? 0.9 : 0.05, transparent: !!p.translucido, opacity: p.translucido ? 0.22 : 1, depthWrite: !p.translucido });
    }
    return mats[k];
  };

  function construir(variante) {
    const piezas = modelo[CLAVE[variante] || "piezas"];
    chasis.clear();
    rotores.length = 0; leds.length = 0;
    const real = new THREE.Group();
    chasis.add(real);
    gimbalPitch.clear();
    gimbalPitch.rotation.set(0, 0, 0);
    gimbalPitch.position.copy(PIVOTE);
    if (variante === "gimbal") real.add(gimbalPitch);                // el gimbal viejo: su pivote queda en el eje real del pitch
    window.PANTILT = null;
    let pan = null, tilt = null;
    if (variante === "plus") {                                       // dos grupos anidados: el pan gira todo lo de encima; el tilt, además, la cuna
      const pp = modelo.pivotes_plus;
      pan = new THREE.Group(); pan.position.copy(tres(...pp.pan));
      tilt = new THREE.Group(); tilt.position.copy(tres(...pp.tilt).sub(pan.position));
      pan.add(tilt); real.add(pan);
      window.PANTILT = { pan, tilt, pivotePan: tres(...pp.pan), pivoteTilt: tres(...pp.tilt) };
    }
    ventilador.clear();
    estrobo.visible = false;
    const grupos = {};
    piezas.forEach(p => {
      const [x, y, z] = p.centro, eje = p.eje || "z";
      const geo = p.forma === "caja" ? new THREE.BoxGeometry(p.tam[0], p.tam[2], p.tam[1]) : new THREE.CylinderGeometry(p.tam[0] / 2, p.tam[0] / 2, p.tam[1], 20);
      const m = new THREE.Mesh(geo, material(p));
      m.castShadow = !p.translucido;
      m.rotation.order = "YXZ";
      m.rotation.y = (p.yaw || 0) * Math.PI / 180;
      if (p.forma === "cilindro") {
        if (eje === "x") m.rotation.z = -Math.PI / 2;
        else if (eje === "y") m.rotation.x = Math.PI / 2;
        else m.rotation.x = (p.inclinacion || 0) * Math.PI / 180;
      }
      const pos = tres(x, y, z);
      const k = /^(helice|cono)(\d)$/.exec(p.nombre);
      if (k) {                                                   // hélice y cono giran juntos alrededor de su motor
        const n = k[2];
        if (!grupos[n]) {
          const mo = piezas.find(q => q.nombre === "motor" + n);
          const g = new THREE.Group();
          g.position.copy(tres(mo.centro[0], mo.centro[1], 0));
          real.add(g);
          grupos[n] = g;
          rotores.push({ rotor: g, sentido: Number(n) % 2 ? 1 : -1 });
        }
        m.position.set(0, pos.y, 0);
        grupos[n].add(m);
        return;
      }
      if (variante === "plus" && p.grupo === "tilt") { m.position.copy(pos).sub(window.PANTILT.pivoteTilt); tilt.add(m); return; }
      if (variante === "plus" && p.grupo === "pan") { m.position.copy(pos).sub(window.PANTILT.pivotePan); pan.add(m); return; }
      if (variante === "gimbal" && GIMBAL.has(p.nombre)) { m.position.copy(pos).sub(PIVOTE); gimbalPitch.add(m); return; }   // se inclinan con el pitch
      m.position.copy(pos);
      real.add(m);
    });
    halo.position.y = 0.0;
    etqDron.position.y = 0.30;
    dron.userData.real = true;
    dron.userData.variante = variante;
  }

  // el pan-tilt se mueve en el bucle principal de index.html (window.PANTILT); aquí solo se arma y se cambia
  construir(MODO_DRON);
  window.DRON_CAMBIAR = v => {
    MODO_DRON = v;
    try { localStorage.setItem("estacion-dron", v); } catch (e) {}
    construir(v);
    if (window.aplicarModoDron) aplicarModoDron();
    if (window.CAMARAS_APLICAR) CAMARAS_APLICAR();
  };
})();
