// Vista del dron (D-072, 20-oct: el dron ya no tiene gimbal ni cámara USB) con sus cámaras y el LiDAR de 360°, como paneles que se activan y
// se apagan con los botones de arriba (teclas P, G y L):
//   · CSI principal FIJA al chasis, inclinada 5° hacia abajo, HFOV 62.2° (IMX219; el dato es nominal, sin medir), con la telemetría y las cajas
//     de YOLO que calcula la simulación (la simulación aún modela una cámara con gimbal: las cajas siguen su campo de visión)
//   · CSI al piso, fija al chasis, -90°, HFOV 62.2° (la segunda cámara; en el dron real la batería taparía parte de su imagen)
//   · LiDAR 360°: mapa de puntos alrededor del dron, vista desde arriba con el frente hacia arriba; se calcula en el navegador con la
//     geometría de la escena (paneles, personas, árboles y edificios) con el haz inclinado (−10° por omisión): solo choca con lo que mide más que la altura del haz a esa distancia. El TF03 real es de un solo haz hacia
//     adelante: este mapa es lo que armaría un LiDAR que girara (el giro de 360° del dron lo hace con el yaw); es una vista simulada.
// Las cajas de las cámaras CSI son SIMULADAS: persona dentro del campo de la cámara, a menos de 30 m y sin un panel en medio, con una
// confianza que baja con la distancia (no es la salida de YOLO real). Lo dibuja el mismo renderer que la cámara principal.
"use strict";
(() => {
  const CLAVE = "estacion-camaras-v1";
  const $ = id => document.getElementById(id);
  const CAMS = [
    { id: "usb", panel: "fpv", nombre: "CSI principal (fija)", corto: "CSI fija" },
    { id: "csi0", panel: "cam-csi0", nombre: "CSI CAM0 · piso", corto: "CSI piso", hfov: 62.2, vfov: 48.3, pitch: -90 },
  ];
  let activas = { usb: true, csi0: true, lid: true };
  try { Object.assign(activas, JSON.parse(localStorage.getItem(CLAVE) || "{}")); } catch (e) {}
  let entorno = null;
  fetch("entorno_u.json").then(r => r.json()).then(j => { entorno = j; }).catch(() => {});

  // ---------------------------------------------------------------------------------------------------------- paneles en el DOM
  function panelCamara(c) {
    const s = document.createElement("section");
    s.className = "panel"; s.id = c.panel;
    s.innerHTML = `<div class="cab"><h3>${c.nombre} · YOLO</h3><span class="tag" id="${c.id}-tag" style="color:var(--tenue)">–</span></div>
      <div class="cuerpo"><div class="vista-cam" id="${c.id}-vista"><div class="filtro"></div><canvas id="${c.id}-hud"></canvas></div></div>`;
    document.body.appendChild(s);
  }
  CAMS.filter(c => c.hfov).forEach(panelCamara);
  const lid = document.createElement("section");
  lid.className = "panel"; lid.id = "p-lid360";
  lid.innerHTML = `<div class="cab"><h3>LiDAR 360° · mapa de puntos</h3><select id="lid360-incl" title="Inclinación del haz del LiDAR que gira"><option value="0">0°</option><option value="-5">−5°</option><option value="-10" selected>−10°</option><option value="-20">−20°</option></select><span class="tag" id="lid360-tag" style="color:var(--tenue)">–</span></div>
    <div class="cuerpo"><canvas id="lid360-lienzo"></canvas><div class="slam-ley"><span><i style="background:#ff4d4f"></i>cerca</span><span><i style="background:#f5c542"></i>medio</span><span><i style="background:#2db7ff"></i>lejos</span><span>anillos 5 · 10 · 20 · 30 m · frente arriba</span></div></div>`;
  document.body.appendChild(lid);
  const barra = document.createElement("div");
  barra.id = "camaras-ui";
  barra.innerHTML = `<span>Mostrar:</span>` + [["usb", "CSI principal (fija)"], ["csi0", "CSI piso"], ["lid", "LiDAR 360°"]]
    .map(([id, t]) => `<button data-vista="${id}" title="Activar o apagar este panel">${t}</button>`).join("");
  document.body.appendChild(barra);

  // ---------------------------------------------------------------------------------------------------------- cámaras de three.js
  const camCsi = {}, filas = {};
  CAMS.filter(c => c.hfov).forEach(c => {
    camCsi[c.id] = new THREE.PerspectiveCamera(c.vfov, Math.tan(c.hfov / 2 * Math.PI / 180) / Math.tan(c.vfov / 2 * Math.PI / 180), 0.1, 700);
    filas[c.id] = { hud: $(c.id + "-hud"), vista: $(c.id + "-vista") };
  });

  function colocar(cam, c, e) {
    cam.up.set(0, 1, 0);
    const adel = new THREE.Vector3(Math.cos(e.psi), 0, -Math.sin(e.psi));
    const p = mundo(e.x + 0.12 * Math.cos(e.psi), e.y + 0.12 * Math.sin(e.psi), e.z - 0.08);
    cam.position.copy(p);
    const th = c.pitch * Math.PI / 180;
    const dir = adel.clone().multiplyScalar(Math.cos(th)).add(new THREE.Vector3(0, Math.sin(th), 0));
    if (c.pitch <= -85) cam.up.copy(adel);              // a plomo: el frente del dron queda hacia arriba de la imagen
    cam.lookAt(p.clone().add(dir));
    cam.updateMatrixWorld();
  }

  // ¿hay un panel entre el dron y la persona? (en planta; los paneles miden 2.1-2.4 m y el dron vuela casi siempre más alto que la persona,
  // pero el panel tapa lo que está detrás desde cualquier altura de la cámara frontal)
  function tapado(e, pp, paneles) {
    const x1 = e.x, y1 = e.y, x2 = pp.p[0], y2 = pp.p[1];
    for (const [ax, ay, bx, by, h] of paneles || []) {
      if (e.z > h + 0.3) continue;                       // por encima del panel se ve por encima
      const d = (x2 - x1) * (by - ay) - (y2 - y1) * (bx - ax);
      if (Math.abs(d) < 1e-9) continue;
      const t = ((ax - x1) * (by - ay) - (ay - y1) * (bx - ax)) / d, u = ((ax - x1) * (y2 - y1) - (ay - y1) * (x2 - x1)) / d;
      if (t > 0 && t < 1 && u >= 0 && u <= 1) return true;
    }
    return false;
  }

  function cajas(cam, W, H, e, hfov) {
    const out = [], adel = new THREE.Vector3();
    cam.getWorldDirection(adel);
    e.pers.forEach(pp => {
      const d = Math.hypot(pp.p[0] - e.x, pp.p[1] - e.y);
      if (d > 30 || tapado(e, pp, partida.paneles)) return;
      const base = mundo(pp.p[0], pp.p[1], 0);
      if (base.clone().sub(cam.position).dot(adel) <= 0.3) return;
      const alto = pp.alto || pp.est || 1.72;
      let x0 = 1, x1 = -1, y0 = 1, y1 = -1, dentro = false;
      [[-0.25, -0.25], [0.25, -0.25], [-0.25, 0.25], [0.25, 0.25]].forEach(([ox, oz]) => [0.0, alto].forEach(hy => {
        const q = new THREE.Vector3(base.x + ox, hy, base.z + oz).project(cam);
        if (Math.abs(q.x) <= 1 && Math.abs(q.y) <= 1 && q.z < 1) dentro = true;
        x0 = Math.min(x0, q.x); x1 = Math.max(x1, q.x); y0 = Math.min(y0, q.y); y1 = Math.max(y1, q.y);
      }));
      if (!dentro) return;
      x0 = Math.max(x0, -1); x1 = Math.min(x1, 1); y0 = Math.max(y0, -1); y1 = Math.min(y1, 1);
      if (x1 <= x0 || y1 <= y0) return;
      const conf = Math.max(0.35, Math.min(0.96, 0.95 - 0.014 * d - (pp.pos === 3 ? 0.2 : pp.pos === 1 ? 0.07 : 0)));
      out.push({ x0: (x0 + 1) / 2 * W, x1: (x1 + 1) / 2 * W, y0: (1 - y1) / 2 * H, y1: (1 - y0) / 2 * H, id: pp.id ?? 61, d, conf, rol: pp.rol });
    });
    return out;
  }

  function dibujarCsi(c, e) {
    const f = filas[c.id], W = f.vista.clientWidth, H = f.vista.clientHeight;
    if (W < 8) return;
    const dpr = Math.min(devicePixelRatio, 2);
    if (f.hud.width !== Math.round(W * dpr)) { f.hud.width = Math.round(W * dpr); f.hud.height = Math.round(H * dpr); }
    const g = f.hud.getContext("2d");
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    g.clearRect(0, 0, W, H);
    const cj = cajas(camCsi[c.id], W, H, e, c.hfov);
    g.font = "500 10px 'Roboto Mono', monospace";
    cj.forEach(b => {
      const col = "rgba(70,235,160,0.95)";
      g.lineWidth = 1.6; g.strokeStyle = col;
      g.strokeRect(b.x0, b.y0, b.x1 - b.x0, b.y1 - b.y0);
      const t = `persona ${b.conf.toFixed(2)} · ${b.d.toFixed(0)} m`;
      g.fillStyle = "rgba(6,14,10,.78)"; g.fillRect(b.x0, Math.max(0, b.y0 - 14), g.measureText(t).width + 8, 14);
      g.fillStyle = col; g.textAlign = "left"; g.fillText(t, b.x0 + 4, Math.max(10, b.y0 - 3));
    });
    g.strokeStyle = "rgba(150,235,255,.55)"; g.lineWidth = 1;                         // mira central
    g.beginPath(); g.moveTo(W / 2 - 10, H / 2); g.lineTo(W / 2 + 10, H / 2); g.moveTo(W / 2, H / 2 - 10); g.lineTo(W / 2, H / 2 + 10); g.stroke();
    g.fillStyle = "rgba(150,235,255,.9)"; g.textAlign = "right";
    g.fillText(`${c.corto.toUpperCase()} · ${c.pitch}° · HFOV ${c.hfov}° · ${cj.length} det.`, W - 8, H - 8);
    g.textAlign = "left"; g.fillText("SIMULADO", 8, 14);
    $(c.id + "-tag").textContent = cj.length ? `${cj.length} persona${cj.length > 1 ? "s" : ""}` : "sin detecciones";
    $(c.id + "-tag").style.color = cj.length ? "var(--ok, #33d17a)" : "var(--tenue)";
  }

  // ---------------------------------------------------------------------------------------------------------- LiDAR 360°
  function circulo(x, y, psi, c, r) {                  // distancia a lo largo del rayo hasta un círculo
    const dx = Math.cos(psi), dy = Math.sin(psi), rx = c[0] - x, ry = c[1] - y, t = rx * dx + ry * dy;
    if (t <= 0) return null;
    const h = Math.abs(rx * dy - ry * dx);
    return h < r ? t - Math.sqrt(r * r - h * h) : null;
  }
  function segmento(x, y, psi, a, b) {
    const dx = Math.cos(psi), dy = Math.sin(psi), ex = b[0] - a[0], ey = b[1] - a[1], den = dx * ey - dy * ex;
    if (Math.abs(den) < 1e-9) return null;
    const t = ((a[0] - x) * ey - (a[1] - y) * ex) / den, u = ((a[0] - x) * dy - (a[1] - y) * dx) / den;
    return t > 0 && u >= 0 && u <= 1 ? t : null;
  }
  function escanear(e) {
    const N = 240, R = 40, pts = [], tg = Math.tan(-Number($("lid360-incl").value) * Math.PI / 180);
    const choca = (m, alto) => { const h = e.z - m * tg; return h >= 0 && h <= alto; };      // el haz inclinado a esa distancia está a la altura h
    const P = (partida && partida.paneles) || [], A = (partida && partida.arboles) || [], B = entorno ? entorno.edificios : [];
    const arbolesCampus = entorno ? entorno.arboles : [];
    for (let i = 0; i < N; i++) {
      const ang = e.psi + (i / N) * 2 * Math.PI;
      let m = R;
      for (const p of P) { const t = segmento(e.x, e.y, ang, [p[0], p[1]], [p[2], p[3]]); if (t !== null && t < m && choca(t, p[4])) m = t; }
      for (const a of A) { const t = circulo(e.x, e.y, ang, a.p, a.r); if (t !== null && t < m && choca(t, a.alto)) m = t; }
      for (const q of e.pers) { const t = circulo(e.x, e.y, ang, q.p, 0.3); if (t !== null && t < m && choca(t, q.alto || q.est || 1.72)) m = t; }
      for (const a of arbolesCampus) if (Math.abs(a.p[0] - e.x) < R && Math.abs(a.p[1] - e.y) < R) { const t = circulo(e.x, e.y, ang, a.p, 0.3); if (t !== null && t < m && choca(t, a.alto)) m = t; }
      for (const b of B) {
        if (Math.abs(b.centro[0] - e.x) > R + b.tam[0] || Math.abs(b.centro[1] - e.y) > R + b.tam[1]) continue;
        const x0 = b.centro[0] - b.tam[0] / 2, x1 = b.centro[0] + b.tam[0] / 2, y0 = b.centro[1] - b.tam[1] / 2, y1 = b.centro[1] + b.tam[1] / 2;
        for (const [a1, a2] of [[[x0, y0], [x1, y0]], [[x1, y0], [x1, y1]], [[x1, y1], [x0, y1]], [[x0, y1], [x0, y0]]]) { const t = segmento(e.x, e.y, ang, a1, a2); if (t !== null && t < m && choca(t, b.alto)) m = t; }
      }
      if (m < R) pts.push([i / N * 2 * Math.PI, m]);
    }
    return pts;
  }
  const lienzo = $("lid360-lienzo");
  let t0 = performance.now();
  function dibujarLidar(e) {
    const r = lienzo.getBoundingClientRect(), dpr = Math.min(devicePixelRatio, 2);
    if (r.width < 8) return;
    if (lienzo.width !== Math.round(r.width * dpr)) { lienzo.width = Math.round(r.width * dpr); lienzo.height = Math.round(r.height * dpr); }
    const g = lienzo.getContext("2d"), W = r.width, H = r.height, cx = W / 2, cy = H / 2, esc = Math.min(W, H) / 2 / 33;
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    g.fillStyle = "#070b10"; g.fillRect(0, 0, W, H);
    g.strokeStyle = "#1f2c3b"; g.lineWidth = 1; g.fillStyle = "#56667a"; g.font = "9px 'Roboto Mono', monospace";
    [5, 10, 20, 30].forEach(m => { g.beginPath(); g.arc(cx, cy, m * esc, 0, 2 * Math.PI); g.stroke(); g.fillText(m + " m", cx + 3, cy - m * esc + 10); });
    g.beginPath(); g.moveTo(cx, cy - 33 * esc); g.lineTo(cx, cy + 33 * esc); g.moveTo(cx - 33 * esc, cy); g.lineTo(cx + 33 * esc, cy); g.stroke();
    const pts = escanear(e), barrido = ((performance.now() - t0) / 1500) % 1 * 2 * Math.PI;
    pts.forEach(([a, m]) => {
      const X = cx + Math.sin(a) * m * esc, Y = cy - Math.cos(a) * m * esc;            // a = ángulo desde el frente, antihorario en la simulación
      const sx = cx - Math.sin(a) * m * esc;
      const col = m < 5 ? "#ff4d4f" : m < 12 ? "#f5c542" : "#2db7ff";
      const da = ((barrido - a) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI);
      g.globalAlpha = da < 1.2 ? 1 : 0.55;
      g.fillStyle = col; g.beginPath(); g.arc(sx, Y, da < 1.2 ? 2.4 : 1.8, 0, 2 * Math.PI); g.fill();
    });
    g.globalAlpha = 1;
    g.strokeStyle = "rgba(51,209,122,.5)";                                              // línea del barrido
    g.beginPath(); g.moveTo(cx, cy); g.lineTo(cx - Math.sin(barrido) * 33 * esc, cy - Math.cos(barrido) * 33 * esc); g.stroke();
    g.fillStyle = "#33d17a"; g.beginPath(); g.moveTo(cx, cy - 7); g.lineTo(cx - 5, cy + 5); g.lineTo(cx + 5, cy + 5); g.closePath(); g.fill();   // el dron, nariz arriba
    const cerca = pts.length ? Math.min(...pts.map(q => q[1])) : null;
    $("lid360-tag").textContent = `${pts.length} pts` + (cerca !== null ? ` · mín ${cerca.toFixed(1)} m` : "");
    $("lid360-tag").style.color = cerca !== null && cerca < 5 ? "#ff4d4f" : "var(--suave)";
  }

  // ---------------------------------------------------------------------------------------------------------- encendido y apagado
  function aplicar() {
    document.body.classList.toggle("cam-off-usb", !activas.usb);
    document.body.classList.toggle("cam-off-csi0", !activas.csi0);
    document.body.classList.toggle("cam-off-lid", !activas.lid);
    barra.querySelectorAll("button").forEach(b => b.classList.toggle("activo", !!activas[b.dataset.vista]));
    const vis = CAMS.filter(c => activas[c.id]);
    const centro = $("centro");
    if (centro) {                                      // rejilla: 1 cámara sola, 2 en columnas, 3 = la principal grande y las otras dos apiladas
      const n = vis.length;
      centro.style.display = n > 1 ? "grid" : "flex";
      centro.style.gridTemplateColumns = n === 2 ? "minmax(0, 1.7fr) minmax(0, 1fr)" : "";
      centro.style.gridTemplateRows = "minmax(0, 1fr)";
      centro.style.gap = "8px";
    }
    try { localStorage.setItem(CLAVE, JSON.stringify(activas)); } catch (e) {}
  }
  barra.addEventListener("click", ev => {
    const b = ev.target.closest("button[data-vista]");
    if (!b) return;
    activas[b.dataset.vista] = !activas[b.dataset.vista];
    aplicar();
  });
  window.CAMARAS_APLICAR = aplicar;
  addEventListener("keydown", ev => {
    if (/SELECT|INPUT|TEXTAREA/.test(ev.target.tagName) || ev.ctrlKey || ev.altKey) return;
    const m = { KeyP: "usb", KeyG: "csi0", KeyL: "lid" }[ev.code];
    if (m) { activas[m] = !activas[m]; aplicar(); }
  });


  // ---------------------------------------------------------------------------------------------------------- ruta de búsqueda de Brahian
  // Se calcula en el servidor (entorno/ruta_busqueda.py) sobre los paneles de la partida y el punto donde empieza la IA, y se dibuja como una
  // línea y puntos de paso a 3.30 m: entrada (giro de 360°), detrás de cada V, el cuadrado, y de frente a la boca con el vaivén de ±30°.
  // Cada punto se pinta de verde cuando el dron pasa a menos de 1.5 m, para verla ejecutarse en las repeticiones.
  const grupoRuta = new THREE.Group();
  grupoRuta.visible = activas.ruta !== false;
  escena.add(grupoRuta);
  window.RUTA_GRUPO = grupoRuta;
  let puntosRuta = [], visitados = [], ultimoK = 0;
  const unos = ["#ffffff", "#7fe3ff"];
  function etiqueta(txt, x, y, z) {
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex(textoPlano(txt, "#bfefff", 512, 96, 54)), transparent: true, depthTest: false }));
    sp.scale.set(5.2, 0.98, 1); sp.position.set(x, z + 0.55, -y); sp.renderOrder = 10;
    return sp;
  }
  function limpiarRuta() { while (grupoRuta.children.length) { const o = grupoRuta.children[0]; grupoRuta.remove(o); } puntosRuta = []; visitados = []; }
  async function cargarRuta() {
    limpiarRuta();
    if (!partida || partida.vivo || !partida.paneles || !partida.paneles.length) return;
    const C = partida.cuadros, c0 = C.find(c => c.fase === 2) || C[0];
    let r;
    try {
      const q = `ruta.json?paneles=${encodeURIComponent(JSON.stringify(partida.paneles))}&inicio=${encodeURIComponent(JSON.stringify(c0.d.slice(0, 3)))}`;
      const resp = await fetch(q, { cache: "no-store" });
      if (!resp.ok) return;
      r = await resp.json();
    } catch (e) { return; }
    const mat = new THREE.LineBasicMaterial({ color: 0x57d6ff, transparent: true, opacity: 0.9, depthTest: false });
    const linea = new THREE.Line(new THREE.BufferGeometry().setFromPoints(r.polilinea.map(p => new THREE.Vector3(p[0], p[2], -p[1]))), mat);
    linea.renderOrder = 9;
    grupoRuta.add(linea);
    const anillo = new THREE.Mesh(new THREE.RingGeometry(1.4, 1.5, 48), new THREE.MeshBasicMaterial({ color: 0xf5c542, side: THREE.DoubleSide, depthTest: false }));
    anillo.rotation.x = -Math.PI / 2; anillo.position.set(r.entrada[0], r.entrada[2], -r.entrada[1]); anillo.renderOrder = 9;
    grupoRuta.add(anillo, etiqueta("ENTRADA · giro de 360°", r.entrada[0], r.entrada[1], r.entrada[2] + 0.3));
    const geo = new THREE.SphereGeometry(0.2, 12, 8);
    r.v.forEach(v => {
      v.puntos.forEach((p, i) => {
        const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: 0xffffff, depthTest: false }));
        m.position.set(p[0], p[2], -p[1]); m.renderOrder = 10;
        grupoRuta.add(m);
        puntosRuta.push({ x: p[0], y: p[1], m });
        if (i === 0 || i === v.puntos.length - 1) grupoRuta.add(etiqueta(p[4].replace(" · esquina 1", " · cuadrado"), p[0], p[1], p[2]));
      });
      const vv = v.vaiven, a0 = vv.psi * Math.PI / 180;
      [-1, 1].forEach(sg => {                           // el abanico del vaivén (±30°) frente a la boca
        const a = a0 + sg * vv.amplitud * Math.PI / 180;
        const g = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(vv.desde[0], 3.3, -vv.desde[1]),
          new THREE.Vector3(vv.desde[0] + Math.cos(a) * vv.largo, 3.3, -(vv.desde[1] + Math.sin(a) * vv.largo))]);
        const l = new THREE.Line(g, new THREE.LineBasicMaterial({ color: 0xf5c542, depthTest: false })); l.renderOrder = 9;
        grupoRuta.add(l);
      });
    });
    visitados = puntosRuta.map(() => false);
  }
  window.RUTA_CARGAR = cargarRuta;
  function pasoRuta(e) {
    if (e.k < ultimoK - 5) { visitados = puntosRuta.map(() => false); puntosRuta.forEach(p => p.m.material.color.set(0xffffff)); }
    ultimoK = e.k;
    puntosRuta.forEach((p, i) => { if (!visitados[i] && Math.hypot(e.x - p.x, e.y - p.y) < 1.5 && e.z > 2.5) { visitados[i] = true; p.m.material.color.set(0x33d17a); } });
  }
  const bRuta = document.createElement("button");
  bRuta.id = "b-ruta"; bRuta.className = "btn"; bRuta.title = "Mostrar u ocultar la ruta de búsqueda de Brahian (tecla R)";
  const ref = $("b-vuelo");
  if (ref && ref.parentNode) ref.parentNode.insertBefore(bRuta, ref.nextSibling);
  const textoRuta = () => { bRuta.textContent = (grupoRuta.visible ? "✓ " : "") + "Ruta (R)"; bRuta.classList.toggle("activo", grupoRuta.visible); };
  const alternarRuta = () => { grupoRuta.visible = !grupoRuta.visible; activas.ruta = grupoRuta.visible; textoRuta(); try { localStorage.setItem(CLAVE, JSON.stringify(activas)); } catch (e) {} };
  bRuta.onclick = alternarRuta;
  textoRuta();
  addEventListener("keydown", ev => { if (ev.code === "KeyR" && !/SELECT|INPUT|TEXTAREA/.test(ev.target.tagName) && !ev.ctrlKey) alternarRuta(); });

  window.CAMARAS_PASO = () => {
    const e = window.ESTADO_VISTA;
    if (!e || !partida) return;
    if (grupoRuta.visible) pasoRuta(e);
    CAMS.filter(c => c.hfov && activas[c.id]).forEach(c => {
      const cam = camCsi[c.id], el = filas[c.id].vista;
      colocar(cam, c, e);
      const r = el.getBoundingClientRect();
      if (r.width > 8) { const asp = r.width / r.height; if (Math.abs(cam.aspect - asp) > 1e-3) { cam.aspect = asp; cam.fov = 2 * Math.atan(Math.tan(c.hfov / 2 * Math.PI / 180) / asp) * 180 / Math.PI; cam.updateProjectionMatrix(); } }
      renderizarEnCaja(cam, el);
      dibujarCsi(c, e);
    });
    if (activas.lid && lienzo.offsetParent) dibujarLidar(e);
  };
})();
