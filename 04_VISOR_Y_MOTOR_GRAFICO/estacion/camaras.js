// Vista del dron (D-072, 20-oct: el dron ya no tiene gimbal ni cámara USB) con sus cámaras y el mapa de los dos LiDAR de 1 haz, como paneles que se activan y
// se apagan con los botones de arriba (teclas P, G y L):
//   · CSI principal FIJA al chasis, inclinada 5° hacia abajo, HFOV 62.2° (IMX219; el dato es nominal, sin medir), con la telemetría y las cajas
//     de YOLO que calcula la simulación (la simulación aún modela una cámara con gimbal: las cajas siguen su campo de visión)
//   · CSI al piso, fija al chasis, -90°, HFOV 62.2° (solo en el dron plus, variante H; el mínimo no la tiene)
// El botón "Dron" cambia entre el mínimo (G: CSI fija) y el plus (H: CSI y TF-Luna en un pan-tilt de 2 servos, más la CSI al piso).
//   · LiDAR 1D: los DOS haces del dron (TF03 fijo al frente y TF-Luna en el pan-tilt), con los puntos acumulados; no existe LiDAR de 360°
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
  lid.innerHTML = `<div class="cab"><h3>LiDAR · TF03 y TF-Luna (1 haz)</h3><select id="lid360-incl" title="Alcance del mapa"><option value="12" selected>12 m</option><option value="20">20 m</option><option value="35">35 m</option></select><span class="tag" id="lid360-tag" style="color:var(--tenue)">–</span></div>
    <div class="cuerpo"><canvas id="lid360-lienzo"></canvas><div class="slam-ley"><span><i style="background:#2db7ff"></i>TF03 (fijo, al frente)</span><span><i style="background:#ffb020"></i>TF-Luna (en el pan-tilt)</span><span>norte arriba</span></div></div>`;
  document.body.appendChild(lid);
  const barra = document.createElement("div");
  barra.id = "camaras-ui";
  barra.innerHTML = `<span>Mostrar:</span>` + [["usb", "CSI principal (fija)"], ["csi0", "CSI piso"], ["lid", "LiDAR 1D"]]
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

  // ---------------------------------------------------------------------------------------------------------- los DOS LiDAR de 1 haz
  // No hay LiDAR de 360°: el dron lleva el TF03, fijo al chasis y apuntando al frente (−5°, hasta 30 m), y el TF-Luna, en el pan-tilt junto a la CSI
  // (apunta donde la cámara: pan y tilt de la partida; hasta ~8 m). Aquí se dibuja SOLO lo que miden esos dos haces: cada medida es un punto, y los
  // puntos se acumulan a medida que el dron gira y el pan-tilt se mueve. La distancia se calcula con la geometría de la escena (paneles, personas, árboles,
  // edificios): choca si el haz, inclinado, está a esa distancia a una altura menor que la del objeto y mayor que el suelo.
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
  function medir(e, ang, pitchRad, R) {                // distancia (m) del haz, o null si no toca nada
    const tg = Math.tan(pitchRad);
    const choca = (m, alto) => { const h = e.z + m * tg; return h >= 0 && h <= alto; };
    const P = (partida && partida.paneles) || [], A = (partida && partida.arboles) || [], B = entorno ? entorno.edificios : [];
    const arbolesCampus = entorno ? entorno.arboles : [];
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
    return m < R ? m : null;
  }
  const lienzo = $("lid360-lienzo");
  const nube = [];                                     // puntos acumulados: [x, y, k, haz]  (haz 0 = TF03, 1 = TF-Luna)
  let ultimoKL = 0;
  const TF03 = { alcance: 30, pitch: -5 }, LUNA = { alcance: 8 };
  function dibujarLidar(e) {
    const r = lienzo.getBoundingClientRect(), dpr = Math.min(devicePixelRatio, 2);
    if (r.width < 8) return;
    if (e.k < ultimoKL - 5) nube.length = 0;           // la repetición volvió atrás: se vacía el mapa
    ultimoKL = e.k;
    const plus = typeof MODO_DRON !== "undefined" && MODO_DRON === "plus";
    const rad = Math.PI / 180, pan = plus && typeof panDeg !== "undefined" ? panDeg * rad : 0;
    const tilt = plus && window.PANTILT ? window.PANTILT.tilt.rotation.z : TF03.pitch * rad;
    const mA = medir(e, e.psi, TF03.pitch * rad, TF03.alcance);
    const mB = plus ? medir(e, e.psi + pan, tilt, LUNA.alcance) : null;
    if (mA !== null) nube.push([e.x + Math.cos(e.psi) * mA, e.y + Math.sin(e.psi) * mA, e.k, 0]);
    if (mB !== null) nube.push([e.x + Math.cos(e.psi + pan) * mB, e.y + Math.sin(e.psi + pan) * mB, e.k, 1]);
    if (nube.length > 3000) nube.splice(0, nube.length - 3000);
    if (lienzo.width !== Math.round(r.width * dpr)) { lienzo.width = Math.round(r.width * dpr); lienzo.height = Math.round(r.height * dpr); }
    const g = lienzo.getContext("2d"), W = r.width, H = r.height, cx = W / 2, cy = H / 2, R = Number($("lid360-incl").value), esc = Math.min(W, H) / 2 / R;
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    g.fillStyle = "#070b10"; g.fillRect(0, 0, W, H);
    g.strokeStyle = "#1f2c3b"; g.lineWidth = 1; g.fillStyle = "#56667a"; g.font = "9px 'Roboto Mono', monospace";
    [5, 10, 20, 30].filter(m => m < R * 1.4).forEach(m => { g.beginPath(); g.arc(cx, cy, m * esc, 0, 2 * Math.PI); g.stroke(); g.fillText(m + " m", cx + 3, cy - m * esc + 10); });
    g.beginPath(); g.moveTo(cx, 0); g.lineTo(cx, H); g.moveTo(0, cy); g.lineTo(W, cy); g.stroke();
    g.fillStyle = "#56667a"; g.fillText("N", cx + 4, 11);
    const X = x => cx + (x - e.x) * esc, Y = y => cy - (y - e.y) * esc;                 // norte arriba, centrado en el dron
    const COL = ["#2db7ff", "#ffb020"];
    nube.forEach(([x, y, k, h]) => { g.globalAlpha = Math.max(0.15, 1 - (e.k - k) / 600); g.fillStyle = COL[h]; g.beginPath(); g.arc(X(x), Y(y), 1.8, 0, 2 * Math.PI); g.fill(); });
    g.globalAlpha = 1;
    const haz = (ang, m, alc, col) => { const L = m === null ? alc : m; g.strokeStyle = col; g.globalAlpha = 0.55; g.beginPath(); g.moveTo(cx, cy); g.lineTo(cx + Math.cos(ang) * L * esc, cy - Math.sin(ang) * L * esc); g.stroke(); g.globalAlpha = 1; };
    haz(e.psi, mA, TF03.alcance, COL[0]);
    if (plus) haz(e.psi + pan, mB, LUNA.alcance, COL[1]);
    g.save(); g.translate(cx, cy); g.rotate(-(e.psi - Math.PI / 2)); g.fillStyle = "#33d17a";                           // el dron, con la nariz hacia donde apunta
    g.beginPath(); g.moveTo(0, -7); g.lineTo(-5, 5); g.lineTo(5, 5); g.closePath(); g.fill(); g.restore();
    const fmt = m => m === null ? "—" : m.toFixed(1) + " m";
    $("lid360-tag").textContent = `TF03 ${fmt(mA)}` + (plus ? ` · Luna ${fmt(mB)}` : "");
    $("lid360-tag").style.color = (mA !== null && mA < 5) || (mB !== null && mB < 3) ? "#ff4d4f" : "var(--suave)";
  }

  // ---------------------------------------------------------------------------------------------------------- encendido y apagado
  // la CSI al piso solo existe en el dron "plus" (variante H); el "mínimo" (G) solo tiene la CSI fija
  const hayPiso = () => typeof MODO_DRON !== "undefined" && MODO_DRON === "plus";
  const ef = id => id === "csi0" ? activas.csi0 && hayPiso() : !!activas[id];
  function aplicar() {
    document.body.classList.toggle("cam-off-usb", !ef("usb"));
    document.body.classList.toggle("cam-off-csi0", !ef("csi0"));
    document.body.classList.toggle("cam-off-lid", !ef("lid"));
    barra.querySelectorAll("button[data-vista]").forEach(b => b.classList.toggle("activo", ef(b.dataset.vista)));
    const bp = barra.querySelector('[data-vista="csi0"]'), bu = barra.querySelector('[data-vista="usb"]');
    if (bp) bp.style.display = hayPiso() ? "" : "none";
    if (bu) bu.textContent = hayPiso() ? "CSI en pan-tilt" : "CSI fija";
    const vis = CAMS.filter(c => ef(c.id));
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
  // botón "Dron": mínimo (G) o plus (H)
  const bDron = document.createElement("button");
  bDron.id = "b-dron"; bDron.className = "btn"; bDron.title = "Qué dron mostrar: el del PLUS (pan-tilt de 2 servos y CSI al piso, variante H; en el tránsito su pan-tilt queda parqueado en 0°/−5°) o el del MÍNIMO (CSI fija, variante G)";
  const refR = $("b-ruta") || $("b-vuelo");
  if (refR && refR.parentNode) refR.parentNode.insertBefore(bDron, refR.nextSibling);
  const NOM = { minimo: "Mínimo", plus: "Plus", gimbal: "Antes" };
  window.BOTON_DRON = () => { bDron.textContent = "Dron: " + (NOM[MODO_DRON] || MODO_DRON); };
  bDron.onclick = () => { if (window.DRON_CAMBIAR) DRON_CAMBIAR(MODO_DRON === "plus" ? "minimo" : "plus"); };
  BOTON_DRON();
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
    CAMS.filter(c => c.hfov && ef(c.id)).forEach(c => {
      const cam = camCsi[c.id], el = filas[c.id].vista;
      colocar(cam, c, e);
      const r = el.getBoundingClientRect();
      if (r.width > 8) { const asp = r.width / r.height; if (Math.abs(cam.aspect - asp) > 1e-3) { cam.aspect = asp; cam.fov = 2 * Math.atan(Math.tan(c.hfov / 2 * Math.PI / 180) / asp) * 180 / Math.PI; cam.updateProjectionMatrix(); } }
      renderizarEnCaja(cam, el);
      dibujarCsi(c, e);
    });
    if (ef("lid") && lienzo.offsetParent) dibujarLidar(e);
  };
})();
