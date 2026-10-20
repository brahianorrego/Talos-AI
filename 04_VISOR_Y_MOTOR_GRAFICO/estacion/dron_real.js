// El dron REAL en la estación de tierra: reemplaza el dron decorativo del visor clásico por el modelo hecho con las fotos de
// Brahian (modelo_dron/dron_real.py -> dron_real.json, copia en esta carpeta). Se carga después de index.html y usa sus variables
// (dron, chasis, rotores, leds, ventilador, gimbalPitch, estrobo, etqDron, halo): se quita la geometría vieja (no solo se oculta,
// porque el reproductor vuelve a mostrar leds y estrobo en cada cuadro), pero siguen girando las hélices y el gimbal inclinándose.
// Marco del JSON: x adelante, y izquierda, z arriba  ->  three.js: X = x, Y = z, Z = -y (como mundo()).
// Con ?dron=viejo se ve el dron decorativo de antes; con ?dron=gimbal, el modelo anterior (BaseCam + cámara USB).
"use strict";
(async () => {
  if (new URLSearchParams(location.search).get("dron") === "viejo") return;
  let modelo;
  try { modelo = await (await fetch("dron_real.json", { cache: "no-store" })).json(); } catch (e) { console.warn("Dron real no disponible; queda el decorativo:", e); return; }
  const tres = (x, y, z) => new THREE.Vector3(x, z, -y);
  const PIVOTE = tres(0.150, 0.0, -0.200);                    // eje del motor de pitch del gimbal
  const GIMBAL = new Set(["gimbal_plataforma", "tf03", "camara_usb_placa", "camara_usb_lente", "gimbal_motor_pitch"]);

  chasis.clear();
  rotores.length = 0; leds.length = 0;
  const real = new THREE.Group();
  chasis.add(real);
  // el gimbal: vuelve a colgar de la nariz y su pivote queda en el eje real del pitch
  gimbalPitch.clear();
  gimbalPitch.rotation.set(0, 0, 0);
  gimbalPitch.position.copy(PIVOTE);
  real.add(gimbalPitch);
  // el ventilador y el estrobo viejos ya no existen: se dejan sueltos (el reproductor sigue tocándolos sin efecto)
  ventilador.clear();
  estrobo.visible = false;

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
  const grupos = {};
  const piezas = new URLSearchParams(location.search).get("dron") === "gimbal" ? modelo.piezas_gimbal : modelo.piezas;     // ?dron=gimbal: el dron de antes (con gimbal)
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
    if (GIMBAL.has(p.nombre)) { m.position.copy(pos).sub(PIVOTE); gimbalPitch.add(m); return; }   // se inclinan con el pitch
    m.position.copy(pos);
    real.add(m);
  });
  // la antena, el GPS y el halo del estado quedan a la altura del modelo nuevo
  halo.position.y = 0.0;
  etqDron.position.y = 0.30;
  dron.userData.real = true;
})();
