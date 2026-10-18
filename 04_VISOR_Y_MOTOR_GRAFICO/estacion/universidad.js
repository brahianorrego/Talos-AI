// El campus de la universidad en la estación de tierra (pedido de Brahian, 18-oct): la cancha de fútbol con la zona de IA, las
// canchas cerradas (tenis y múltiple), el coliseo, el parqueadero, edificios de ladrillo, torres, árboles y los cerros, todo desde
// entorno/entorno_u.json (la misma especificación que construye Unreal). Tecla T: la cámara vuela entre las dos canchas.
// Se carga después de index.html y usa sus variables (escena, camara, controles, sol, ponerCamara, aviso, dtReal...).
// Marco de la simulación: x este, y norte, z arriba  ->  three.js: X = x, Y = z, Z = -y (igual que mundo()).
// Con ?entorno=arena se ve la arena blanca de antes.
"use strict";
(async () => {
  if (new URLSearchParams(location.search).get("entorno") === "arena") return;
  let E;
  try { E = await (await fetch("entorno_u.json", { cache: "no-store" })).json(); } catch (e) { console.warn("Entorno de la universidad no disponible; queda la arena:", e); return; }
  const T3 = (x, y, z = 0) => new THREE.Vector3(x, z, -y);
  const grupo = new THREE.Group();
  grupo.name = "universidad";
  escena.add(grupo);

  // ---------------------------------------------------------------------------------------------- la arena blanca se oculta
  escena.children.forEach(o => { if (o.userData.vieja) o.visible = false; });
  escena.fog.color.set(0xb7c3cf); escena.fog.near = 140; escena.fog.far = 2600;
  camara.far = 6000; camara.updateProjectionMatrix();
  escena.traverse(o => {                                                        // cielo nublado de Bogotá
    if (o.material && o.material.uniforms && o.material.uniforms.arriba) { o.material.uniforms.arriba.value.set(0x7a93ad); o.material.uniforms.horizonte.value.set(0xc9d2da); }
  });
  sol.color.set(0xfff6ea); sol.intensity = 1.0;
  controles.maxDistance = 900;

  // ---------------------------------------------------------------------------------------------- utilidades
  const ruido = (g, w, h, n, a) => { for (let i = 0; i < n; i++) { g.fillStyle = `rgba(${Math.random() < .5 ? "0,0,0" : "255,255,255"},${Math.random() * a})`; g.fillRect(Math.random() * w, Math.random() * h, 1 + Math.random() * 2, 1 + Math.random() * 2); } };
  const plano = (cx, cy, sx, sy, material, y = 0.0, rot = 0) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(sx, sy), material);
    m.rotation.x = -Math.PI / 2; m.rotation.z = rot; m.position.set(cx, y, -cy); m.receiveShadow = true; grupo.add(m); return m;
  };
  const caja3 = (cx, cy, sx, sy, alto, mat, y0 = 0, rot = 0) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(sx, alto, sy), mat);
    m.position.set(cx, y0 + alto / 2, -cy); m.rotation.y = rot; m.castShadow = m.receiveShadow = true; grupo.add(m); return m;
  };
  const mat = (c, o = {}) => new THREE.MeshStandardMaterial(Object.assign({ color: new THREE.Color(c).convertSRGBToLinear(), roughness: 0.85 }, o));

  // ---------------------------------------------------------------------------------------------- terreno y cerros
  {
    const [c, g] = lienzo(256, 256);
    g.fillStyle = "#58733a"; g.fillRect(0, 0, 256, 256); ruido(g, 256, 256, 2500, 0.18);
    const t = tex(c, 700);
    plano(0, 0, 8000, 8000, new THREE.MeshStandardMaterial({ map: t, roughness: 1 }), -0.06);
    E.cerros.forEach(h => {
      const geo = new THREE.SphereGeometry(1, 40, 20);
      const p = geo.attributes.position, col = new Float32Array(p.count * 3);
      for (let i = 0; i < p.count; i++) {
        const y = Math.max(p.getY(i), 0), n = 0.5 + 0.5 * Math.sin(p.getX(i) * 9 + p.getZ(i) * 7) * Math.sin(p.getZ(i) * 5 - p.getX(i) * 3);
        const v = 0.55 + 0.45 * y;                                                  // más claro y seco arriba
        col[3 * i] = (0.13 + 0.10 * v + 0.05 * n); col[3 * i + 1] = (0.22 + 0.10 * v + 0.04 * n); col[3 * i + 2] = (0.11 + 0.05 * v);
      }
      geo.setAttribute("color", new THREE.BufferAttribute(col, 3));
      const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 1 }));
      m.scale.set(h.radio[0], h.alto, h.radio[1]); m.position.copy(T3(h.centro[0], h.centro[1], -h.alto * 0.12));
      grupo.add(m);
    });
  }

  // ---------------------------------------------------------------------------------------------- cancha de fútbol (césped con franjas y líneas)
  {
    const PPM = 18, W = Math.round(E.campo.tam[0] * PPM), H = Math.round(E.campo.tam[1] * PPM), [c, g] = lienzo(W, H);
    const fx = x => W / 2 + x * PPM, fy = y => H / 2 - (y - E.campo.centro[1]) * PPM;       // metros de la simulación -> píxeles del lienzo
    for (let k = 0; k * 5 * PPM < H; k++) { g.fillStyle = k % 2 ? "#4f7a2f" : "#5b8736"; g.fillRect(0, k * 5 * PPM, W, 5 * PPM + 1); }   // franjas de corte de 5 m
    ruido(g, W, H, 60000, 0.12);
    for (let i = 0; i < 90; i++) { const x = Math.random() * W, y = Math.random() * H, r = 10 + Math.random() * 40; const gr = g.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, "rgba(110,110,60,.22)"); gr.addColorStop(1, "rgba(110,110,60,0)"); g.fillStyle = gr; g.fillRect(x - r, y - r, 2 * r, 2 * r); }
    g.strokeStyle = "rgba(240,240,235,.92)"; g.lineWidth = 3; g.fillStyle = "rgba(240,240,235,.92)";
    const J = E.campo.juego, cy = E.campo.centro[1];
    g.strokeRect(fx(-J.x), fy(J.y1), 2 * J.x * PPM, (J.y1 - J.y0) * PPM);
    g.beginPath(); g.moveTo(fx(-J.x), fy(cy)); g.lineTo(fx(J.x), fy(cy)); g.stroke();
    g.beginPath(); g.arc(fx(0), fy(cy), 9.15 * PPM, 0, 2 * Math.PI); g.stroke();
    g.beginPath(); g.arc(fx(0), fy(cy), 0.3 * PPM, 0, 2 * Math.PI); g.fill();
    [[J.y1, -1], [J.y0, 1]].forEach(([yl, dentro]) => {                              // áreas y punto penal; "dentro" = hacia el centro de la cancha
      const franja = (ancho, hondo) => g.strokeRect(fx(-ancho / 2), fy(Math.max(yl, yl + dentro * hondo)), ancho * PPM, hondo * PPM);
      franja(40.3, 16.5); franja(18.32, 5.5);
      g.beginPath(); g.arc(fx(0), fy(yl + dentro * 11), 0.3 * PPM, 0, 2 * Math.PI); g.fill();
      g.beginPath(); g.arc(fx(0), fy(yl + dentro * 11), 9.15 * PPM, dentro < 0 ? Math.PI * 0.31 : Math.PI * 1.31, dentro < 0 ? Math.PI * 0.69 : Math.PI * 1.69); g.stroke();
    });
    [[-J.x, J.y1, 0.5], [J.x, J.y1, 1], [-J.x, J.y0, 0], [J.x, J.y0, 1.5]].forEach(([x, y, q]) => { g.beginPath(); g.arc(fx(x), fy(y), 1 * PPM, q * Math.PI, (q + 0.5) * Math.PI); g.stroke(); });
    const t = tex(c); t.anisotropy = 8;
    plano(E.campo.centro[0], E.campo.centro[1], E.campo.tam[0], E.campo.tam[1], new THREE.MeshStandardMaterial({ map: t, roughness: 0.95 }), 0.0);
    // arcos de fútbol (7.32 x 2.44 m)
    const blanco = mat(0xf2f2ee, { roughness: 0.4 });
    [J.y0, J.y1].forEach(yl => {
      [-3.66, 3.66].forEach(x => { const p = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 2.44, 8), blanco); p.position.copy(T3(x, yl, 1.22)); p.castShadow = true; grupo.add(p); });
      const tr = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 7.44, 8), blanco); tr.rotation.z = Math.PI / 2; tr.position.copy(T3(0, yl, 2.44)); tr.castShadow = true; grupo.add(tr);
      const red = new THREE.Mesh(new THREE.PlaneGeometry(7.32, 2.44), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.18, side: THREE.DoubleSide, depthWrite: false }));
      red.position.copy(T3(0, yl + (yl > cy ? 1.2 : -1.2), 1.22)); grupo.add(red);
    });
    // la zona de IA, discreta en el piso (30 x 30 m)
    const z = E.campo.zona_ia, zl = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints([T3(-z / 2, -z / 2, 0.04), T3(z / 2, -z / 2, 0.04), T3(z / 2, z / 2, 0.04), T3(-z / 2, z / 2, 0.04)]), new THREE.LineDashedMaterial({ color: 0xffb347, dashSize: 1.2, gapSize: 0.8, transparent: true, opacity: 0.6 }));
    zl.computeLineDistances(); grupo.add(zl);
  }

  // ---------------------------------------------------------------------------------------------- canchas cerradas (tenis y múltiple)
  E.canchas.forEach(cn => {
    const PPM = 22, W = Math.round(cn.tam[0] * PPM), H = Math.round(cn.tam[1] * PPM), [c, g] = lienzo(W, H);
    g.fillStyle = "#8a2f2a"; g.fillRect(0, 0, W, H); ruido(g, W, H, 20000, 0.1);
    g.strokeStyle = "rgba(245,245,240,.95)"; g.lineWidth = 3;
    if (cn.tipo === "tenis") {
      const cw = 10.97 * PPM, ch = 23.77 * PPM, x0 = (W - cw) / 2, y0 = (H - ch) / 2;
      g.fillStyle = "#4d6b5c"; g.fillRect(x0 - 3 * PPM, y0 - 4 * PPM, cw + 6 * PPM, ch + 8 * PPM);
      g.strokeRect(x0, y0, cw, ch); g.strokeRect(x0 + 1.37 * PPM, y0, cw - 2.74 * PPM, ch);
      g.beginPath(); g.moveTo(x0 + 1.37 * PPM, y0 + 6.4 * PPM); g.lineTo(x0 + cw - 1.37 * PPM, y0 + 6.4 * PPM); g.moveTo(x0 + 1.37 * PPM, y0 + ch - 6.4 * PPM); g.lineTo(x0 + cw - 1.37 * PPM, y0 + ch - 6.4 * PPM);
      g.moveTo(W / 2, y0 + 6.4 * PPM); g.lineTo(W / 2, y0 + ch - 6.4 * PPM); g.stroke();
    } else {                                                                     // múltiple: futsal verde con baloncesto
      g.fillStyle = "#3f6b4a"; g.fillRect(1 * PPM, 1.5 * PPM, W - 2 * PPM, H - 3 * PPM);
      g.strokeRect(1 * PPM, 1.5 * PPM, W - 2 * PPM, H - 3 * PPM);
      g.beginPath(); g.moveTo(1 * PPM, H / 2); g.lineTo(W - 1 * PPM, H / 2); g.stroke();
      g.beginPath(); g.arc(W / 2, H / 2, 3 * PPM, 0, 2 * Math.PI); g.stroke();
      [1.5 * PPM, H - 1.5 * PPM].forEach((yy, i) => { g.strokeRect(W / 2 - 3 * PPM, i ? yy - 5.8 * PPM : yy, 6 * PPM, 5.8 * PPM); g.beginPath(); g.arc(W / 2, i ? yy - 5.8 * PPM : yy + 5.8 * PPM, 1.8 * PPM, 0, 2 * Math.PI); g.stroke(); });
    }
    plano(cn.centro[0], cn.centro[1], cn.tam[0], cn.tam[1], new THREE.MeshStandardMaterial({ map: tex(c), roughness: 0.8 }), 0.03);
    if (cn.tipo === "tenis") {                                                      // red
      const red = new THREE.Mesh(new THREE.PlaneGeometry(12.8, 0.9), new THREE.MeshBasicMaterial({ color: 0xe8e8e0, transparent: true, opacity: 0.55, side: THREE.DoubleSide }));
      red.position.copy(T3(cn.centro[0], cn.centro[1], 0.55)); grupo.add(red);
    } else {                                                                        // aros de baloncesto en los dos extremos
      [-1, 1].forEach(s => {
        const poste = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 3.0, 8), mat(0x555a60)); poste.position.copy(T3(cn.centro[0], cn.centro[1] + s * (cn.tam[1] / 2 - 0.4), 1.5)); poste.castShadow = true;
        const tablero = new THREE.Mesh(new THREE.BoxGeometry(1.8, 1.05, 0.05), mat(0xe9edf0)); tablero.position.copy(T3(cn.centro[0], cn.centro[1] + s * (cn.tam[1] / 2 - 1.0), 3.0)); tablero.castShadow = true;
        grupo.add(poste, tablero);
      });
    }
  });

  // ---------------------------------------------------------------------------------------------- suelos (parqueadero, caminos, vías)
  E.suelos.forEach(s => {
    const PPM = 8, W = Math.max(8, Math.round(s.tam[0] * PPM)), H = Math.max(8, Math.round(s.tam[1] * PPM)), [c, g] = lienzo(Math.min(W, 2048), Math.min(H, 2048));
    const sx = c.width / s.tam[0], sy = c.height / s.tam[1];
    if (s.tipo === "adoquin") { g.fillStyle = "#a79e92"; g.fillRect(0, 0, c.width, c.height); g.strokeStyle = "rgba(60,55,50,.35)"; g.lineWidth = 1; for (let x = 0; x < c.width; x += 0.22 * sx) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, c.height); g.stroke(); } for (let y = 0; y < c.height; y += 0.11 * sy) { g.beginPath(); g.moveTo(0, y); g.lineTo(c.width, y); g.stroke(); } }
    else { g.fillStyle = "#454a4f"; g.fillRect(0, 0, c.width, c.height); ruido(g, c.width, c.height, 4000, 0.15); }
    if (s.nombre === "parqueadero") {                                              // líneas amarillas de los puestos
      g.strokeStyle = "#d8b02a"; g.lineWidth = 2;
      for (let f = 0; f < 4; f++) for (let k = 0; k <= 14; k++) { const x = (s.tam[0] / 2 - 24.5 + k * 3.6) * sx, y = (s.tam[1] / 2 - 11.3 + f * 5.6) * sy; g.beginPath(); g.moveTo(x, y); g.lineTo(x, y + 4.8 * sy); g.stroke(); }
    }
    if (s.tipo === "via") { g.strokeStyle = "#d8b02a"; g.lineWidth = 2; g.setLineDash([sx * 3, sx * 3]); g.beginPath(); if (s.tam[0] > s.tam[1]) { g.moveTo(0, c.height / 2); g.lineTo(c.width, c.height / 2); } else { g.moveTo(c.width / 2, 0); g.lineTo(c.width / 2, c.height); } g.stroke(); }
    plano(s.centro[0], s.centro[1], s.tam[0], s.tam[1], new THREE.MeshStandardMaterial({ map: tex(c), roughness: 0.9 }), s.tipo === "adoquin" ? 0.04 : 0.02);
  });

  // ---------------------------------------------------------------------------------------------- edificios con fachadas dibujadas
  const fachada = (tipo, ancho, alto) => {
    const PPM = 14, W = Math.round(ancho * PPM), H = Math.round(alto * PPM), [c, g] = lienzo(W, H);
    const ladrillo = (col, a, b) => { g.fillStyle = col; g.fillRect(a, b[0], W - a, b[1]); for (let i = 0; i < 900 * (ancho / 20); i++) { g.fillStyle = `rgba(${Math.random() < .5 ? "70,25,15" : "230,150,110"},${Math.random() * 0.16})`; g.fillRect(Math.random() * W, b[0] + Math.random() * b[1], 3 + Math.random() * 6, 2); } };
    if (tipo === "laboratorio") { g.fillStyle = "#c9c9c4"; g.fillRect(0, 0, W, H); ruido(g, W, H, 1500, .08); }
    else ladrillo(tipo === "torre" ? "#b0613f" : tipo === "caseta" ? "#a9563a" : "#b5563a", 0, [0, H]);
    const ventanas = (paso, ancV, altV, y0, col, marco) => {
      for (let y = y0; y + altV < H - 0.4 * PPM; y += paso * PPM) for (let x = 1.4 * PPM; x + ancV * PPM < W - 0.5 * PPM; x += (ancV + 1.3) * PPM) {
        g.fillStyle = marco; g.fillRect(x - 3, y - 3, ancV * PPM + 6, altV * PPM + 6); g.fillStyle = col; g.fillRect(x, y, ancV * PPM, altV * PPM);
        g.fillStyle = "rgba(255,255,255,.18)"; g.fillRect(x, y, ancV * PPM * 0.4, altV * PPM);
      }
    };
    if (tipo === "apartamentos") { ventanas(3.0, 1.5, 1.4, 1.0 * PPM, "#2a3a4a", "#d9d3c7"); for (let y = 3 * PPM; y < H; y += 3 * PPM) { g.fillStyle = "rgba(210,205,195,.9)"; g.fillRect(0, y - 0.35 * PPM, W, 0.35 * PPM); } }
    else if (tipo === "torre") { ventanas(2.9, 1.3, 1.3, 1.2 * PPM, "#27374a", "#cfc8bb"); for (let y = 2.9 * PPM; y < H; y += 2.9 * PPM) { g.fillStyle = "rgba(205,200,190,.85)"; g.fillRect(0, y - 0.3 * PPM, W, 0.3 * PPM); } for (let x = 0; x < W; x += 5 * PPM) { g.fillStyle = "rgba(190,100,70,.9)"; g.fillRect(x, 0, 0.9 * PPM, H); } }
    else if (tipo === "laboratorio") { ventanas(3.2, 2.2, 1.8, 1.4 * PPM, "#3a5f86", "#8a8f94"); }
    else if (tipo === "ladrillo") { ventanas(3.0, 2.0, 1.2, 1.4 * PPM, "#27374a", "#7a4a35"); }
    else if (tipo === "caseta") { g.fillStyle = "#3d2a1d"; g.fillRect(W * 0.55, H * 0.22, W * 0.2, H * 0.78); g.fillStyle = "#31404a"; g.fillRect(W * 0.1, H * 0.35, W * 0.35, H * 0.3); }
    else if (tipo === "coliseo") {                                                // ladrillo abajo, franja larga de ventanas arriba
      g.fillStyle = "#26323d"; g.fillRect(0, H * 0.18, W, H * 0.3); g.strokeStyle = "#c0523a"; g.lineWidth = 5; for (let x = 0; x < W; x += 3.2 * PPM) { g.beginPath(); g.moveTo(x, H * 0.18); g.lineTo(x, H * 0.48); g.stroke(); }
    }
    return tex(c);
  };
  E.edificios.forEach(b => {
    const [sx, sy] = b.tam, h = b.alto;
    const cuerpoH = b.tipo === "coliseo" ? h - 3 : h;
    const mA = new THREE.MeshStandardMaterial({ map: fachada(b.tipo === "coliseo" ? "ladrillo" : b.tipo, sy, cuerpoH), roughness: 0.9 });
    const mB = new THREE.MeshStandardMaterial({ map: fachada(b.tipo === "coliseo" ? "coliseo" : b.tipo, sx, cuerpoH), roughness: 0.9 });
    const techo = mat(b.tipo === "laboratorio" ? 0xe4e6e8 : 0x6b6f73);
    const cuerpo = new THREE.Mesh(new THREE.BoxGeometry(sx, cuerpoH, sy), [mA, mA, techo, techo, mB, mB]);
    cuerpo.position.set(b.centro[0], cuerpoH / 2, -b.centro[1]); cuerpo.castShadow = cuerpo.receiveShadow = true; grupo.add(cuerpo);
    if (b.tipo === "coliseo") caja3(b.centro[0], b.centro[1], sx + 1.6, sy + 1.6, 3.0, mat(0x3d4044, { roughness: 0.6 }), cuerpoH);       // la cubierta oscura, más ancha
    if (b.tipo === "caseta") caja3(b.centro[0], b.centro[1], sx + 1.2, sy + 1.2, 0.25, mat(0x9b9a95), h);
  });

  // ---------------------------------------------------------------------------------------------- vallas y cercos
  {
    const [c, g] = lienzo(256, 256);
    g.strokeStyle = "rgba(25,28,30,.9)"; g.lineWidth = 3;
    for (let i = -256; i < 512; i += 24) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i + 256, 256); g.moveTo(i + 256, 0); g.lineTo(i, 256); g.stroke(); }
    const malla = tex(c); malla.wrapS = malla.wrapT = THREE.RepeatWrapping;
    const poste = mat(0x2e3236, { roughness: 0.5 });
    E.vallas.forEach(v => {
      const pts = v.p.slice(); if (v.cerrado) pts.push(pts[0]);
      for (let i = 0; i < pts.length - 1; i++) {
        const [ax, ay] = pts[i], [bx, by] = pts[i + 1], L = Math.hypot(bx - ax, by - ay), ang = Math.atan2(by - ay, bx - ax);
        if (v.tipo === "malla") {
          const m = malla.clone(); m.needsUpdate = true; m.repeat.set(L / 2.4, v.alto / 2.4);
          const pl = new THREE.Mesh(new THREE.PlaneGeometry(L, v.alto), new THREE.MeshBasicMaterial({ map: m, transparent: true, side: THREE.DoubleSide, depthWrite: false, alphaTest: 0.05 }));
          pl.position.copy(T3((ax + bx) / 2, (ay + by) / 2, v.alto / 2)); pl.rotation.y = ang; grupo.add(pl);
          for (let d = 0; d <= L; d += 3.5) { const p = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, v.alto, 6), poste); p.position.copy(T3(ax + Math.cos(ang) * d, ay + Math.sin(ang) * d, v.alto / 2)); p.castShadow = true; grupo.add(p); }
        } else caja3((ax + bx) / 2, (ay + by) / 2, L, 0.35, v.alto, mat(0x4a3a35), 0, -ang);
      }
    });
  }

  // ---------------------------------------------------------------------------------------------- árboles y autos (instancias)
  {
    const fr = E.arboles.filter(a => a.tipo === "frondoso"), ci = E.arboles.filter(a => a.tipo === "cipres");
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), col = new THREE.Color();
    const troncos = new THREE.InstancedMesh(new THREE.CylinderGeometry(0.22, 0.34, 1, 7), mat(0x4a3a2c, { roughness: 1 }), E.arboles.length);
    E.arboles.forEach((a, i) => { const hT = a.alto * (a.tipo === "cipres" ? 0.25 : 0.45); m4.compose(T3(a.p[0], a.p[1], hT / 2), q, new THREE.Vector3(1, hT, 1)); troncos.setMatrixAt(i, m4); });
    const copasA = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1, 1), mat(0xffffff, { roughness: 1 }), fr.length);
    const copasB = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1, 1), mat(0xffffff, { roughness: 1 }), fr.length);
    fr.forEach((a, i) => {
      const y0 = a.alto * 0.45, r = a.copa, v = a.semilla;
      m4.compose(T3(a.p[0], a.p[1], y0 + r * 0.8), q, new THREE.Vector3(r, r * 0.85, r)); copasA.setMatrixAt(i, m4); copasA.setColorAt(i, col.setRGB(0.10 + 0.10 * v, 0.24 + 0.12 * v, 0.07 + 0.06 * v).convertSRGBToLinear());
      m4.compose(T3(a.p[0] + (v - 0.5) * r, a.p[1] + (0.5 - v) * r * 0.8, y0 + r * 1.55), q, new THREE.Vector3(r * 0.72, r * 0.62, r * 0.72)); copasB.setMatrixAt(i, m4); copasB.setColorAt(i, col.setRGB(0.12 + 0.09 * v, 0.28 + 0.1 * v, 0.08 + 0.05 * v).convertSRGBToLinear());
    });
    const conos = new THREE.InstancedMesh(new THREE.ConeGeometry(1, 1, 8), mat(0xffffff, { roughness: 1 }), ci.length);
    ci.forEach((a, i) => { const hC = a.alto * 0.8; m4.compose(T3(a.p[0], a.p[1], a.alto * 0.25 + hC / 2), q, new THREE.Vector3(a.copa, hC, a.copa)); conos.setMatrixAt(i, m4); conos.setColorAt(i, col.setRGB(0.05, 0.14 + 0.06 * a.semilla, 0.07).convertSRGBToLinear()); });
    [troncos, copasA, copasB, conos].forEach(m => { m.castShadow = true; m.receiveShadow = true; if (m.instanceColor) m.instanceColor.needsUpdate = true; grupo.add(m); });
    // autos: carrocería y cabina
    const n = E.carros.length, cuerpo = new THREE.InstancedMesh(new THREE.BoxGeometry(4.3, 0.75, 1.75), mat(0xffffff, { roughness: 0.35, metalness: 0.3 }), n), cabina = new THREE.InstancedMesh(new THREE.BoxGeometry(2.2, 0.62, 1.55), mat(0x1b2530, { roughness: 0.15, metalness: 0.5 }), n);
    E.carros.forEach((c2, i) => {
      const qy = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), -c2.rot * Math.PI / 180);
      m4.compose(T3(c2.p[0], c2.p[1], 0.62), qy, new THREE.Vector3(1, 1, 1)); cuerpo.setMatrixAt(i, m4); cuerpo.setColorAt(i, col.setRGB(...c2.color));
      m4.compose(T3(c2.p[0], c2.p[1], 1.3).add(new THREE.Vector3(-0.2, 0, 0).applyQuaternion(qy)), qy, new THREE.Vector3(1, 1, 1)); cabina.setMatrixAt(i, m4);
    });
    [cuerpo, cabina].forEach(m => { m.castShadow = true; m.receiveShadow = true; if (m.instanceColor) m.instanceColor.needsUpdate = true; grupo.add(m); });
  }

  // ---------------------------------------------------------------------------------------------- el motor de avión de la exhibición (foto 4)
  E.extras.forEach(x => {
    const g = new THREE.Group(); g.position.copy(T3(x.p[0], x.p[1], 0)); g.rotation.y = -x.rot * Math.PI / 180;
    const losa = new THREE.Mesh(new THREE.BoxGeometry(5.5, 0.12, 3.2), mat(0x8d8f8c)), carcasa = new THREE.Mesh(new THREE.CylinderGeometry(0.62, 0.62, 3.2, 20), mat(0x15191d, { roughness: 0.4, metalness: 0.5 }));
    carcasa.rotation.z = Math.PI / 2; carcasa.position.set(0, 1.1, 0);
    const turbina = new THREE.Mesh(new THREE.CylinderGeometry(0.66, 0.66, 0.5, 24), mat(0xb02323, { roughness: 0.4 })); turbina.rotation.z = Math.PI / 2; turbina.position.set(-1.75, 1.1, 0);
    const base = new THREE.Mesh(new THREE.BoxGeometry(3.4, 0.14, 1.3), mat(0xd9a920)); base.position.set(0, 0.45, 0);
    [losa, carcasa, turbina, base].forEach(m => { m.castShadow = m.receiveShadow = true; g.add(m); }); losa.position.y = 0.06; grupo.add(g);
  });

  // ---------------------------------------------------------------------------------------------- vuelo entre las dos canchas (tecla T)
  const P = E.poses, vuelo = { activo: false, t: 0, de: null, a: null, destino: "cancha_cerrada", en: "campo" };
  const pose = n => ({ pos: T3(P[n].pos[0], P[n].pos[1], P[n].pos[2]), mira: T3(P[n].mira[0], P[n].mira[1], P[n].mira[2]) });
  const suave = t => t * t * (3 - 2 * t);
  window.volarEntreCanchas = () => {
    if (vuelo.activo) return;
    vuelo.destino = vuelo.en === "campo" ? "cancha_cerrada" : "campo";
    const d = pose(vuelo.destino);
    vuelo.de = { pos: camara.position.clone(), mira: controles.target.clone() }; vuelo.a = d; vuelo.t = 0; vuelo.activo = true;
    controles.enabled = false;
    aviso("VUELO · " + P[vuelo.destino].nombre, COL.nominal || "#2db7ff", P.segundos);
  };
  window.VUELO_PASO = dt => {
    if (!vuelo.activo) return;
    vuelo.t = Math.min(1, vuelo.t + dt / P.segundos);
    const u = suave(vuelo.t), alto = P.altura_de_vuelo, a = vuelo.de.pos, b = vuelo.a.pos;
    const c1 = new THREE.Vector3(a.x, Math.max(a.y, alto), a.z), c2 = new THREE.Vector3(b.x, Math.max(b.y, alto), b.z);       // sube, cruza y baja (curva de Bézier)
    const w = 1 - u;
    camara.position.set(...["x", "y", "z"].map(k => w * w * w * a[k] + 3 * w * w * u * c1[k] + 3 * w * u * u * c2[k] + u * u * u * b[k]));
    controles.target.lerpVectors(vuelo.de.mira, vuelo.a.mira, suave(Math.min(1, vuelo.t * 1.15)));
    if (vuelo.t >= 1) {
      vuelo.activo = false; vuelo.en = vuelo.destino; controles.enabled = true;
      modoCam = "orbita"; document.querySelectorAll("[data-cam]").forEach(x => x.classList.toggle("activo", x.dataset.cam === "orbita"));
    }
  };
  addEventListener("keydown", ev => { if (ev.code === "KeyT" && !/SELECT|INPUT|TEXTAREA/.test(ev.target.tagName)) window.volarEntreCanchas(); });
  const boton = document.getElementById("b-vuelo");
  if (boton) boton.onclick = window.volarEntreCanchas;
  // arranque: la cámara mira la zona de IA desde el borde de la cancha
  const p0 = pose("campo"); camara.position.copy(p0.pos); controles.target.copy(p0.mira);
  document.body.dataset.entorno = "universidad";
})();
