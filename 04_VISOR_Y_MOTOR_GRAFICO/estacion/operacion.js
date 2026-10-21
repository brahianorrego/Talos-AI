// Estación de tierra · interfaz de operación. Una sola pantalla para volar, enseñar y operar: izquierda la cámara principal (CSI#1) con HUD discreto o el mapa táctico
// (Enseñar); derecha tres casillas fijas: cámara al piso (CSI#2), mapa de los dos LiDAR de 1 haz y telemetría (con actitud y minimapa). Los ajustes van en un menú (Esc).
// Habla con en_vivo.py (puerto 8767): lee los cuadros por Server-Sent Events y manda las órdenes del operador por POST.
"use strict";
const NOMBRE_DRON = "TALOS-AI";          // UNA constante: el nombre exacto del dron se cambia solo aquí (y en el <span id="nombreDron"> si hace falta)
const EN_VIVO = "http://127.0.0.1:8767";
const HFOV = 68.3, VFOV = 54.0, MONTAJE = -2.4;       // CSI medida por Brahian (D-078); el montaje inclina la cámara -2.4° respecto al soporte
const ARENA = 25;                                     // geocerca (m)
const $ = id => document.getElementById(id);
const rad = g => g * Math.PI / 180, deg = r => r * 180 / Math.PI;
const lim = (v, a, b) => Math.max(a, Math.min(b, v));
const post = (r, d) => fetch(EN_VIVO + r, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(d || {}) }).catch(() => {});

const S = { c: null, paneles: [], k: 0, tSim: 0, ultimo: 0, estado: "ia", panel: "dron", asist: false, ruta: false, grabando: false, pausa: false, rep: null, repTimer: null,
  hist: [], eventos: [], tend: { alt: [], bat: [], enl: [] }, imgEdad: 0, latencia: 0, prevC: null, lidar: [], luna: [], cajas: [], wp: [], sel: -1, fps: 0, demo: "", fuente: "vivo", vista: [0, 0, 0, 0] };
window.__S = S;
document.querySelector("#nombreDron").textContent = NOMBRE_DRON;
document.title = NOMBRE_DRON + " · Estación de tierra";

// ------------------------------------------------------------------------------------------------------------------ datos
let es = null;
function conectar() {
  if (es) es.close();
  clearInterval(S.repTimer); S.rep = null; S.fuente = "vivo";
  es = new EventSource(EN_VIVO + "/vivo");
  es.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.tipo === "partida") { S.paneles = m.paneles || []; S.lidar.length = 0; S.luna.length = 0; S.tSim = 0; S.wp.length = 0; S.sel = -1; return; }
    if (m.tipo === "cuadro") recibir(m.c);
  };
}
function recibir(c) {
  registrarEventos(S.prevC, c); S.prevC = c;
  S.c = c; S.ultimo = performance.now(); S.tSim += 0.1; S.hist.push([S.ultimo, c]); if (S.hist.length > 80) S.hist.shift();
  if (c.lh && c.lid !== undefined && c.lid < 29.5) { S.lidar.push([c.lh[0], c.lh[1]]); if (S.lidar.length > 2500) S.lidar.shift(); }
  if (c.luna && (c.luna[0] || c.luna[1])) { S.luna.push([c.luna[0], c.luna[1]]); if (S.luna.length > 2500) S.luna.shift(); }
  if (c.ens) { S.grabando = !!c.ens.graba; if (c.ens.demo && c.ens.demo !== S.demo) { S.demo = c.ens.demo; aviso("Demostración guardada: " + c.ens.demo); } }
}
async function cargarRep(url) {
  if (es) { es.close(); es = null; }
  clearInterval(S.repTimer);
  const d = await (await fetch(url)).json();
  const cuadros = (d.cuadros || d), dt = d.dt || 0.1;
  S.rep = { cuadros, dt }; S.paneles = d.paneles || []; S.lidar.length = 0; S.luna.length = 0; S.k = 0; S.fuente = "rep"; S.tSim = 0;
  S.repTimer = setInterval(() => { if (S.pausa) return; S.k = Math.min(S.k + 1, cuadros.length - 1); const c = cuadros[S.k]; if (!c.pers) c.pers = []; recibir(c); S.tSim = S.k * dt; }, dt * 1000);
}

// ------------------------------------------------------------------------------------------------------------------ utilidades de dibujo
function ajustar(cv) {
  const dpr = Math.min(devicePixelRatio || 1, 2), w = cv.clientWidth, h = cv.clientHeight;
  if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) { cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); }
  const g = cv.getContext("2d"); g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, w, h);
  return [g, w, h];
}
const col = { texto: "#e9eef7", tenue: "#93a6c2", tenue2: "#62768f", linea: "#243653", acento: "#2fa4e7", alerta: "#f5a623", peligro: "#e5484d", ok: "#2ecc71" };
const fuente = (g, tam, peso = 400, mono = false) => { g.font = `${peso} ${tam}px ${mono ? "'IBM Plex Mono','Roboto Mono','Cascadia Mono',Consolas,monospace" : "Inter,'Segoe UI',Roboto,sans-serif"}`; };
function texto(g, t, x, y, al = "left", c = col.texto, tam = 11, peso = 500, mono = true) { fuente(g, tam, peso, mono); g.textAlign = al; g.fillStyle = "rgba(0,0,0,.6)"; g.fillText(t, x + 1, y + 1); g.fillStyle = c; g.fillText(t, x, y); }

// pose de la cámara principal en el mundo de la simulación (x este, y norte, z arriba)
function camara(c) {
  const [x, y, z, psi] = c.d, yaw = psi + rad(c.pan || 0), pit = rad((c.gmb ?? -5) + MONTAJE);
  const f = [Math.cos(yaw) * Math.cos(pit), Math.sin(yaw) * Math.cos(pit), Math.sin(pit)];
  const r = [Math.sin(yaw), -Math.cos(yaw), 0];
  const u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]];
  return { p: [x + 0.12 * Math.cos(psi), y + 0.12 * Math.sin(psi), z - 0.05], f, r, u };
}
function proyectar(cam, P, rect) {                    // punto del mundo -> píxeles dentro del rectángulo de la imagen; null si está detrás
  const d = [P[0] - cam.p[0], P[1] - cam.p[1], P[2] - cam.p[2]], dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const zc = dot(d, cam.f); if (zc < 0.3) return null;
  const nx = dot(d, cam.r) / zc / Math.tan(rad(HFOV / 2)), ny = dot(d, cam.u) / zc / Math.tan(rad(VFOV / 2));
  return [rect.x + rect.w * (0.5 + nx / 2), rect.y + rect.h * (0.5 - ny / 2), zc];
}

// ------------------------------------------------------------------------------------------------------------------ cámaras reales de Unreal
const img0 = $("cam0"), img1 = $("cam1");
S.video = [false, false];
[[img0, "cam0.jpg", 0, "sinvideo"], [img1, "cam1.jpg", 1, "sinvideo2"]].forEach(([img, archivo, k, ph]) => {
  let ocupado = false;
  setInterval(() => {
    if (ocupado || S.fuente !== "vivo") { if (S.fuente !== "vivo") { img.style.display = "none"; S.video[k] = false; $(ph).style.display = "flex"; } return; }
    ocupado = true;
    fetch(`/unreal_cam/${archivo}?t=${Date.now()}`).then(r => { if (k === 0 && r.ok) S.imgEdad = +r.headers.get("X-Edad"); return (r.ok && +r.headers.get("X-Edad") < 2.5) ? r.blob() : Promise.reject(); })
      .then(b => { const u = URL.createObjectURL(b); img.onload = () => { URL.revokeObjectURL(u); img.style.display = "block"; S.video[k] = true; $(ph).style.display = "none"; }; img.src = u; })
      .catch(() => { img.style.display = "none"; S.video[k] = false; $(ph).style.display = "flex"; })
      .finally(() => { ocupado = false; });
  }, 110);
});

// ------------------------------------------------------------------------------------------------------------------ cámara principal con HUD completo (estilo PFD)
function rectImagen(W, H) { const w = Math.min(W, H * 4 / 3), h = w * 3 / 4; return { x: (W - w) / 2, y: (H - h) / 2, w, h }; }
// la imagen de Unreal llega con ~0.2-0.3 s de retraso: el horizonte y las cajas se calculan con el cuadro de la simulación del instante en que se tomó la imagen
function cuadroDeLaImagen() {
  if (!S.video[0] || !S.hist.length) return S.c;
  const objetivo = performance.now() - S.imgEdad * 1000 - 70; let mejor = S.hist[S.hist.length - 1];
  for (const h of S.hist) if (Math.abs(h[0] - objetivo) < Math.abs(mejor[0] - objetivo)) mejor = h;
  return mejor[1];
}
const FIJADOS = ["PERSECUCION", "PERDIDA", "RECONFIRMAR", "FIJADO"];
const ALERTAS = { reflejo_ataque: "REFLEJO · EVASIÓN", evadiendo: "EVASIÓN", amenaza: "AMENAZA CERCANA", punto_ciego: "PUNTO CIEGO", perimetro: "PERÍMETRO" };
function cinta(g, x, y, w, h, valor, paso, px, rotulo, fmt, lado) {          // cinta vertical (altitud o velocidad): ticks que corren, caja con el valor actual
  g.save(); g.beginPath(); g.rect(x, y, w, h); g.clip(); g.fillStyle = "rgba(11,18,32,.62)"; g.fillRect(x, y, w, h);
  const cyy = y + h / 2; g.strokeStyle = "rgba(233,238,247,.8)"; g.lineWidth = 1.4;
  for (let v = Math.floor((valor - h / 2 / px) / paso) * paso; v <= valor + h / 2 / px; v += paso) {
    const yy = cyy - (v - valor) * px, mayor = Math.abs(v % 1) < 1e-6;
    g.beginPath(); g.moveTo(lado === "der" ? x : x + w, yy); g.lineTo(lado === "der" ? x + (mayor ? 14 : 8) : x + w - (mayor ? 14 : 8), yy); g.stroke();
    if (mayor && v >= 0) texto(g, String(Math.round(v)), lado === "der" ? x + 20 : x + w - 20, yy + 5, lado === "der" ? "left" : "right", col.texto, 14, 600);
  }
  g.restore(); g.fillStyle = "#0b1220"; g.fillRect(x - 2, cyy - 15, w + 4, 30); g.strokeStyle = col.acento; g.lineWidth = 1.6; g.strokeRect(x - 2, cyy - 15, w + 4, 30);
  texto(g, fmt(valor), x + w / 2, cyy + 8, "center", "#fff", 20, 700); texto(g, rotulo, x + w / 2, y - 6, "center", col.acento, 13, 700, false);
}
function dibujarHUD() {
  const [g, W, H] = ajustar($("hud")), c = cuadroDeLaImagen(), cv = S.c;
  if (S.panel !== "dron" || !c || !cv) { S.cajas = []; return; }
  const R = rectImagen(W, H), cx = R.x + R.w / 2, cy = R.y + R.h / 2, ppd = R.h / VFOV, u = Math.max(0.85, R.h / 720);
  if (!S.video[0]) { g.fillStyle = "#0a0f1a"; g.fillRect(R.x, R.y, R.w, R.h); }
  g.save(); g.beginPath(); g.rect(R.x, R.y, R.w, R.h - 46); g.clip();
  const cam = camara(c), pit = (c.gmb ?? -5) + MONTAJE, roll = rad(c.cr || 0);
  // horizonte artificial con escala de cabeceo (se mueve con el pitch de la cámara y rota con el alabeo)
  g.save(); g.translate(cx, cy); g.rotate(-roll); const hy = pit * ppd, ancho = Math.min(R.w * 0.22, 200 * u);
  const linea = (x0, y0, x1, y1, an = 1.6) => { g.lineWidth = an + 2; g.strokeStyle = "rgba(0,0,0,.55)"; g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke(); g.lineWidth = an; g.strokeStyle = "rgba(255,255,255,.92)"; g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke(); };
  linea(-R.w * 0.46, hy, -ancho * 0.55, hy, 2); linea(ancho * 0.55, hy, R.w * 0.46, hy, 2);
  for (let p = -30; p <= 30; p += 5) { if (!p) continue; const yy = hy - p * ppd, l = p % 10 === 0 ? ancho * 0.5 : ancho * 0.28; g.setLineDash(p < 0 ? [5, 4] : []);
    linea(-l, yy, -ancho * 0.12, yy); linea(ancho * 0.12, yy, l, yy); g.setLineDash([]); if (p % 10 === 0) { texto(g, String(Math.abs(p)), -l - 6, yy + 5, "right", "#fff", 14, 700); texto(g, String(Math.abs(p)), l + 6, yy + 5, "left", "#fff", 14, 700); } }
  g.restore();
  // retícula central
  linea(cx - 22 * u, cy, cx - 7 * u, cy, 2); linea(cx + 7 * u, cy, cx + 22 * u, cy, 2); linea(cx, cy - 22 * u, cx, cy - 7 * u, 2); linea(cx, cy + 7 * u, cx, cy + 22 * u, 2);
  // cajas de YOLO: las personas que la simulación ve en cámara, proyectadas a la imagen (no inventadas)
  S.cajas = []; const fijado = FIJADOS.includes(c.eb);
  (c.en_camara || []).forEach(o => {
    const q = (c.pers || []).find(pp => pp.id === o.id); if (!q) return;
    const alto = q.alto || q.est || 1.7, a = proyectar(cam, [q.p[0], q.p[1], 0.05], R), b = proyectar(cam, [q.p[0], q.p[1], alto], R); if (!a || !b) return;
    const h = Math.abs(a[1] - b[1]), w = h * 0.4, x0 = b[0] - w / 2, y0 = Math.min(a[1], b[1]), objetivo = fijado && q.rol === "ladron", cc = objetivo ? col.peligro : col.ok;
    S.cajas.push({ j: o.i, id: o.id, x0, y0, x1: x0 + w, y1: y0 + h, rol: q.rol });
    g.strokeStyle = cc; g.lineWidth = 2.4; const e = Math.min(14, w / 3, h / 3);
    [[x0, y0, 1, 1], [x0 + w, y0, -1, 1], [x0, y0 + h, 1, -1], [x0 + w, y0 + h, -1, -1]].forEach(([x, y, sx, sy]) => { g.beginPath(); g.moveTo(x, y + sy * e); g.lineTo(x, y); g.lineTo(x + sx * e, y); g.stroke(); });
    g.lineWidth = 1; g.globalAlpha = .55; g.strokeRect(x0, y0, w, h); g.globalAlpha = 1;
    const et = objetivo ? `OBJETIVO · ID ${o.id} · ${o.d.toFixed(1)} m` : `PERSONA · ID ${o.id} · ${o.d.toFixed(1)} m`; fuente(g, 14, 700, true);
    const tw = g.measureText(et).width + 14, ly = Math.max(R.y + 2, y0 - 23); g.fillStyle = cc; g.fillRect(x0, ly, tw, 21); texto(g, et, x0 + 7, ly + 16, "left", "#06101c", 14, 700);
  });
  g.restore();
  // cinta de rumbo (arriba)
  const hdg = (deg(c.d[3]) + 360) % 360, tw = Math.min(R.w * 0.46, 480), tx = cx - tw / 2, tyy = R.y + 10;
  g.save(); g.beginPath(); g.rect(tx, tyy, tw, 36); g.clip(); g.fillStyle = "rgba(11,18,32,.62)"; g.fillRect(tx, tyy, tw, 36); g.strokeStyle = "rgba(233,238,247,.8)"; g.lineWidth = 1.4;
  const pxg = tw / 90;
  for (let a = Math.floor((hdg - 50) / 5) * 5; a <= hdg + 50; a += 5) { const x = cx + (a - hdg) * pxg, n = ((a % 360) + 360) % 360; g.beginPath(); g.moveTo(x, tyy + 36); g.lineTo(x, tyy + 36 - (n % 15 === 0 ? 11 : 6)); g.stroke();
    if (n % 15 === 0) texto(g, { 0: "E", 90: "N", 180: "O", 270: "S" }[n] ?? String(Math.round(((90 - n) + 360) % 360)).padStart(3, "0"), x, tyy + 16, "center", n % 90 === 0 ? col.acento : col.texto, 14, 700); }
  g.restore(); g.fillStyle = "#0b1220"; g.fillRect(cx - 30, tyy + 38, 60, 24); g.strokeStyle = col.acento; g.lineWidth = 1.6; g.strokeRect(cx - 30, tyy + 38, 60, 24);
  const rumbo = ((90 - hdg) + 360) % 360; texto(g, String(Math.round(rumbo) % 360).padStart(3, "0") + "°", cx, tyy + 56, "center", "#fff", 18, 700);
  // cintas de velocidad (izquierda) y altitud (derecha)
  const mh = Math.max(46, Math.round(44 * u)), cinH = Math.min(R.h * 0.5, 330), cinY = cy - cinH / 2 + 4, v = Math.hypot((c.dv || [0, 0])[0], (c.dv || [0, 0])[1]);
  cinta(g, R.x + 14, cinY, 70, cinH, v, 0.5, 52, "VEL m/s", x => x.toFixed(1), "izq"); cinta(g, R.x + R.w - 84, cinY, 70, cinH, c.d[2], 0.5, 40, "ALT m", x => x.toFixed(1), "der");
  // indicador de alabeo (arco bajo) y de pan / tilt
  g.save(); g.translate(cx, R.y + R.h - mh - 52); g.strokeStyle = "rgba(233,238,247,.8)"; g.lineWidth = 1.6; g.beginPath(); g.arc(0, 0, 40 * u, rad(-150), rad(-30)); g.stroke();
  [-45, -30, -20, -10, 0, 10, 20, 30, 45].forEach(r => { const an = rad(r - 90); g.beginPath(); g.moveTo(Math.cos(an) * 40 * u, Math.sin(an) * 40 * u); g.lineTo(Math.cos(an) * (r % 30 === 0 ? 31 : 35) * u, Math.sin(an) * (r % 30 === 0 ? 31 : 35) * u); g.stroke(); });
  g.rotate(roll); g.fillStyle = col.acento; g.beginPath(); g.moveTo(0, -37 * u); g.lineTo(-6, -27 * u); g.lineTo(6, -27 * u); g.closePath(); g.fill(); g.restore();
  const pan = c.pan || 0, tilt = c.gmb ?? -5, gx = R.x + 16, gy = R.y + R.h - mh - 70;
  g.fillStyle = "rgba(11,18,32,.7)"; g.fillRect(gx, gy, 178, 60); g.strokeStyle = "rgba(233,238,247,.35)"; g.lineWidth = 1; g.strokeRect(gx, gy, 178, 60);
  texto(g, "PAN", gx + 8, gy + 17, "left", col.tenue, 13, 700, false); g.strokeStyle = "rgba(233,238,247,.6)"; g.beginPath(); g.moveTo(gx + 44, gy + 12); g.lineTo(gx + 166, gy + 12); g.stroke(); g.fillStyle = col.acento; g.fillRect(gx + 105 + pan / 90 * 61 - 3, gy + 6, 6, 12);
  texto(g, "TILT", gx + 8, gy + 41, "left", col.tenue, 13, 700, false); g.beginPath(); g.moveTo(gx + 44, gy + 36); g.lineTo(gx + 166, gy + 36); g.stroke(); g.fillStyle = col.acento; g.fillRect(gx + 44 + (tilt + 45) / 60 * 122 - 3, gy + 30, 6, 12);
  texto(g, `${pan >= 0 ? "+" : ""}${pan.toFixed(0)}°`, gx + 168, gy + 55, "right", col.texto, 13, 700); texto(g, `${tilt.toFixed(0)}°`, gx + 98, gy + 55, "right", col.texto, 13, 700);
  // alerta y barra de misión
  const alerta = ALERTAS[c.arb], my = R.y + R.h - mh;
  if (alerta) { fuente(g, 16, 700); const tw2 = g.measureText(alerta).width + 34; g.fillStyle = "rgba(61,40,6,.94)"; g.fillRect(cx - tw2 / 2, my - 40, tw2, 30); g.strokeStyle = col.alerta; g.lineWidth = 2; g.strokeRect(cx - tw2 / 2, my - 40, tw2, 30); texto(g, alerta, cx, my - 19, "center", col.alerta, 16, 700); }
  g.fillStyle = "rgba(11,18,32,.88)"; g.fillRect(R.x, my, R.w, mh); g.fillStyle = col.linea; g.fillRect(R.x, my, R.w, 1);
  const hay = (cv.en_camara || []).length > 0, obj = fijado ? "FIJADO" : hay ? "POSIBLE OBJETIVO" : "NINGUNO", segs = [["MODO", cv.eb ?? "–", col.acento], ["OBJETIVO", obj, fijado ? col.peligro : hay ? col.alerta : col.tenue], ["A LA VISTA", (cv.tf ?? 0).toFixed(1) + " s", col.texto], ["AMENAZA", alerta ? alerta : "NINGUNA", alerta ? col.alerta : col.ok], ["HFOV", HFOV + "° · −2.4°", col.tenue]];
  const sw = R.w / segs.length; segs.forEach(([k, val, cc], i) => { texto(g, k, R.x + i * sw + 12, my + 17, "left", col.tenue2, 12, 700, false); texto(g, val, R.x + i * sw + 12, my + mh - 9, "left", cc, Math.round(16 * Math.min(1.2, Math.max(u, .9))), 700); });
  S.vista = [R.x, R.y, R.w, R.h];
}

// ------------------------------------------------------------------------------------------------------------------ CSI#2 (rótulo)
function dibujarCsi2() {
  const [g, W, H] = ajustar($("hud1")); if (!S.c) return;
  texto(g, `HFOV ${HFOV}° · −90°`, W - 8, H - 9, "right", "#fff", 13, 600);
}

// ------------------------------------------------------------------------------------------------------------------ mapa de los dos LiDAR
function dibujarLidar() {
  const [g, W, H] = ajustar($("lidar")), c = S.c; if (!c || W < 60 || H < 60) return;
  const cx = W / 2, cy = H / 2 + 6, alc = 14, k = Math.min(W / 2 - 10, cy - 18, H - cy - 22) / alc, [x, y, , psi] = c.d;
  const P = (wx, wy) => [cx + (wx - x) * k, cy - (wy - y) * k];
  g.strokeStyle = "#243653"; g.lineWidth = 1; [5, 10].forEach(r => { g.beginPath(); g.arc(cx, cy, r * k, 0, 7); g.stroke(); texto(g, r + " m", cx + r * k * 0.71 + 3, cy - r * k * 0.71 - 2, "left", col.tenue2, 12); });
  g.beginPath(); g.moveTo(cx, cy - alc * k); g.lineTo(cx, cy + alc * k); g.moveTo(cx - alc * k, cy); g.lineTo(cx + alc * k, cy); g.stroke(); texto(g, "N", cx, cy - alc * k - 3, "center", col.tenue, 13, 700);
  (S.paneles || []).forEach(p => { const a = P(p[0], p[1]), b = P(p[2], p[3]); g.strokeStyle = "#8fa3bf"; g.lineWidth = 2.5; g.beginPath(); g.moveTo(...a); g.lineTo(...b); g.stroke(); });
  g.fillStyle = col.acento; S.lidar.forEach(q => { const [px, py] = P(q[0], q[1]); if (Math.abs(px - cx) < W && Math.abs(py - cy) < H) g.fillRect(px - 1.2, py - 1.2, 2.4, 2.4); });
  g.fillStyle = "#9fc5e8"; S.luna.forEach(q => { const [px, py] = P(q[0], q[1]); if (Math.abs(px - cx) < W && Math.abs(py - cy) < H) g.fillRect(px - 1.2, py - 1.2, 2.4, 2.4); });
  const tf = Math.min(c.lid ?? 30, 30); g.strokeStyle = col.acento; g.lineWidth = 1.6; g.beginPath(); g.moveTo(cx, cy); g.lineTo(cx + Math.cos(psi) * tf * k, cy - Math.sin(psi) * tf * k); g.stroke();
  if (c.luna && (c.luna[0] || c.luna[1])) { const [lx, ly] = P(c.luna[0], c.luna[1]); g.strokeStyle = "#9fc5e8"; g.setLineDash([4, 3]); g.beginPath(); g.moveTo(cx, cy); g.lineTo(lx, ly); g.stroke(); g.setLineDash([]); }
  g.save(); g.translate(cx, cy); g.rotate(-psi); g.fillStyle = "#fff"; g.beginPath(); g.moveTo(11, 0); g.lineTo(-7, 6.5); g.lineTo(-3, 0); g.lineTo(-7, -6.5); g.closePath(); g.fill(); g.restore();
  texto(g, "● TF03 fijo", 10, H - 8, "left", col.acento, 12, 600, false); texto(g, "● TF-Luna en el pan-tilt", W - 10, H - 8, "right", "#9fc5e8", 12, 600, false);
}

// ------------------------------------------------------------------------------------------------------------------ telemetría en tarjetas, actitud y minimapa
function bateria() { const pct = lim(100 - S.tSim / 9, 0, 100); return { pct, v: 14.0 + 2.8 * pct / 100 }; }
const MODO_VUELO = { ia: "GUIADO (IA)", manual: "MANUAL", puntos: "PUNTOS DE PASO" };
function spark(id, datos, color = col.acento, lo, hi) {
  const cv = $(id); if (!cv) return; const [g, W, H] = ajustar(cv); if (datos.length < 2) return;
  const mn = lo ?? Math.min(...datos), mx = hi ?? Math.max(...datos), rg = Math.max(mx - mn, 1e-6);
  g.strokeStyle = "#243653"; g.lineWidth = 1; g.beginPath(); g.moveTo(0, H - 0.5); g.lineTo(W, H - 0.5); g.stroke();
  g.strokeStyle = color; g.lineWidth = 1.8; g.beginPath(); datos.forEach((d, i) => { const x = i / 59 * W, y = H - 3 - (d - mn) / rg * (H - 6); i ? g.lineTo(x, y) : g.moveTo(x, y); }); g.stroke();
}
function barrasSenal(id, n) { document.querySelectorAll(`#${id} u`).forEach((u, i) => u.classList.toggle("on", i < n)); }
const set = (id, t) => { const e = $(id); if (e && e.textContent !== String(t)) e.textContent = t; };
const ancho = (id, pct, color) => { const e = $(id); if (e) { e.style.width = lim(pct, 0, 100) + "%"; if (color) e.style.background = color; } };
const ptos = (az) => ["E", "NE", "N", "NO", "O", "SO", "S", "SE"][Math.round((((az % 360) + 360) % 360) / 45) % 8];
setInterval(() => {                                                         // cuadros de datos: 5 veces por segundo (las gráficas de tendencia, una vez por segundo)
  const c = S.c; if (!c) return;
  const [x, y, z, psi] = c.d, vel = Math.hypot((c.dv || [0, 0])[0], (c.dv || [0, 0])[1]), b = bateria(), edad = performance.now() - S.ultimo, enl = S.fuente === "rep" ? 0 : Math.round(edad);
  const sinEnlace = S.fuente !== "rep" && edad > 1500, margen = ARENA - Math.max(Math.abs(x), Math.abs(y)), corr = 9 + 3 * vel, resta = Math.max(0, Math.round(b.pct / 100 * 5.2 / corr * 60));
  const h0 = S.hist.length > 12 ? S.hist[S.hist.length - 11] : null, vs = h0 ? (z - h0[1].d[2]) / Math.max(0.1, (S.hist[S.hist.length - 1][0] - h0[0]) / 1000) : 0;
  const rumbo = ((90 - deg(psi)) % 360 + 360) % 360, lunaD = c.luna && (c.luna[0] || c.luna[1]) ? Math.hypot(c.luna[0] - x, c.luna[1] - y, (c.luna[2] ?? 0) - z) : null, tf = c.lid ?? 30;
  const bars = sinEnlace ? 0 : enl < 120 ? 4 : enl < 300 ? 3 : enl < 700 ? 2 : 1;
  // barra superior
  set("bModo", c.eb ?? "–"); set("bControl", MODO_VUELO[S.estado]); set("bEnlace", sinEnlace ? "SIN ENLACE" : S.fuente === "rep" ? "REPETICIÓN" : enl + " ms"); $("bEnlace").className = sinEnlace ? "peligro" : "";
  barrasSenal("bBarrasEnlace", bars); set("bGps", "14 sat"); set("bBat", `${b.pct.toFixed(0)} % · ${b.v.toFixed(1)} V`); $("bBat").className = b.pct < 20 ? "peligro" : b.pct < 35 ? "alerta" : "ok";
  set("bGeoChip", "OK · " + margen.toFixed(0) + " m"); $("bGeoChip").className = margen < 3 ? "peligro" : margen < 8 ? "alerta" : "ok";
  set("bSens", "TF03 · LUNA · 2 CSI"); $("bSens").className = "ok"; const hayP = (c.en_camara || []).length > 0; set("bObj", FIJADOS.includes(c.eb) ? "FIJADO" : hayP ? "POSIBLE" : "NINGUNO"); $("bObj").className = FIJADOS.includes(c.eb) ? "peligro" : hayP ? "alerta" : "";
  set("bHora", new Date().toLocaleTimeString("es-CO", { hour12: false })); set("bT", "T+" + Math.floor(S.tSim / 60) + ":" + String(Math.floor(S.tSim % 60)).padStart(2, "0"));
  $("bModo").className = FIJADOS.includes(c.eb) ? "acento" : ALERTAS[c.arb] ? "alerta" : "";
  // tarjetas
  set("vAlt", z.toFixed(1)); set("sAlt", `VS ${vs >= 0 ? "+" : ""}${vs.toFixed(1)} m/s`); set("vVel", vel.toFixed(1)); ancho("bVel", vel / 5 * 100); set("sVel", "sobre el suelo");
  set("vRum", String(Math.round(rumbo)).padStart(3, "0")); set("sRum", "hacia el " + ptos(deg(psi)) + (c.ens && c.ens.f360 ? " · 360° activo" : ""));
  set("vBat", b.pct.toFixed(0)); ancho("bBatBarra", b.pct, b.pct < 20 ? col.peligro : b.pct < 35 ? col.alerta : col.ok); set("sBat", `${b.v.toFixed(1)}V · ${corr.toFixed(1)}A · ${resta}m`);
  set("vGps", "14"); set("sGps", "HDOP 0.8 · 3D fijo"); document.querySelectorAll("#gBarras u").forEach(u => u.classList.add("on"));
  set("vEnl", sinEnlace ? "—" : enl); set("sEnl", sinEnlace ? "SIN ENLACE" : S.fuente === "rep" ? "repetición" : "RSSI −52 dBm (sim.)"); $("vEnl").className = sinEnlace ? "peligro" : "";
  set("eModo", MODO_VUELO[S.estado]); set("sModo", c.eb ?? "–"); set("dTf", tf < 29.5 ? tf.toFixed(1) + " m" : "> 30 m"); ancho("bTf", tf / 30 * 100); set("dLu", lunaD === null ? "sin eco" : lunaD.toFixed(1) + " m"); ancho("bLu", lunaD === null ? 0 : lunaD / 8 * 100);
  set("vGeo", margen.toFixed(1)); ancho("bGeo", margen / ARENA * 100, margen < 3 ? col.peligro : margen < 8 ? col.alerta : col.acento); $("vGeo").className = margen < 3 ? "peligro" : margen < 8 ? "alerta" : "";
  const nivel = sinEnlace || margen < 3 ? "peligro" : margen < 8 || b.pct < 20 ? "alerta" : "ok", est = $("estTel"); est.className = "est " + nivel; est.textContent = nivel === "ok" ? "NOMINAL" : nivel === "alerta" ? "PRECAUCIÓN" : "ALERTA";
  set("estLidar", `TF03 ${tf < 29.5 ? tf.toFixed(1) : "> 30"} m`); const e2 = $("estCsi2"); e2.textContent = S.video[1] ? "VIDEO" : "SIN SEÑAL"; e2.className = "est " + (S.video[1] ? "ok" : "");
  set("pieEstado", `● ${S.fuente === "rep" ? "REPETICIÓN" : "SIMULACIÓN EN VIVO"} · DATOS SIMULADOS · ${S.fps.toFixed(0)} fps · enlace ${enl} ms · TALOS-AI estación v1.0`);
  $("bGrabar").className = S.grabando ? "rec" : ""; $("bGrabar").textContent = S.grabando ? "Grabando" : "Grabar"; $("bRuta").className = S.ruta ? "act" : ""; $("bPausa").className = S.pausa ? "act" : "";
  if (sinEnlace && !S.sinEnlaceAvisado) { S.sinEnlaceAvisado = true; evento("Sin enlace con la simulación", "peligro"); } else if (!sinEnlace) S.sinEnlaceAvisado = false;
  if (margen < 3 && !S.geoAvisada) { S.geoAvisada = true; evento("Cerca de la geocerca: " + margen.toFixed(1) + " m", "alerta"); } else if (margen > 5) S.geoAvisada = false;
  spark("spAlt", S.tend.alt, col.acento); spark("spEnl", S.tend.enl, col.ok, 0, 200);
}, 200);
setInterval(() => { const c = S.c; if (!c) return; const t = S.tend; t.alt.push(c.d[2]); t.bat.push(bateria().pct); t.enl.push(S.fuente === "rep" ? 0 : Math.min(200, Math.round(performance.now() - S.ultimo))); for (const k of Object.keys(t)) if (t[k].length > 60) t[k].shift(); }, 1000);
function dibujarTel() {
  const c = S.c; if (!c) return;
  // actitud: horizonte artificial con escala y el dron visto desde atrás que se inclina con el alabeo
  const [g, W, H] = ajustar($("actitud")), roll = rad(c.cr || 0), pit = c.cp || 0, mx = W / 2, my = H / 2 + 6, esc = (H - 26) / 70;
  g.save(); g.beginPath(); g.rect(0, 0, W, H); g.clip(); g.translate(mx, my); g.rotate(-roll); const oy = pit * esc * 1.4;
  g.fillStyle = "#1b6aa5"; g.fillRect(-W * 2, -H * 2 + oy, W * 4, H * 2); g.fillStyle = "#7a5530"; g.fillRect(-W * 2, oy, W * 4, H * 2);
  g.strokeStyle = "#fff"; g.lineWidth = 2; g.beginPath(); g.moveTo(-W, oy); g.lineTo(W, oy); g.stroke();
  for (let p = -20; p <= 20; p += 5) { if (!p) continue; const yy = oy - p * esc * 1.4, l = p % 10 === 0 ? 38 : 20; g.lineWidth = 1.5; g.beginPath(); g.moveTo(-l, yy); g.lineTo(l, yy); g.stroke(); if (p % 10 === 0) { texto(g, String(Math.abs(p)), l + 6, yy + 5, "left", "#fff", 13, 700); texto(g, String(Math.abs(p)), -l - 6, yy + 5, "right", "#fff", 13, 700); } }
  g.restore();
  g.save(); g.translate(mx, 26 + 4); g.strokeStyle = "#fff"; g.lineWidth = 1.6; g.beginPath(); g.arc(0, 56, 56, rad(-140), rad(-40)); g.stroke(); g.rotate(-roll); g.fillStyle = "#fff"; g.beginPath(); g.moveTo(0, 6); g.lineTo(-7, -4); g.lineTo(7, -4); g.closePath(); g.fill(); g.restore();
  g.save(); g.translate(mx, my); g.strokeStyle = "#fff"; g.fillStyle = "#0b1220"; g.lineWidth = 2.6; const r = Math.min(W, H) * 0.3;                                   // el dron visto desde atrás
  g.rotate(-roll); g.beginPath(); g.moveTo(-r, 0); g.lineTo(r, 0); g.stroke(); g.fillRect(-r * 0.2, -r * 0.14, r * 0.4, r * 0.28); g.strokeRect(-r * 0.2, -r * 0.14, r * 0.4, r * 0.28); [-1, 1].forEach(s => { g.beginPath(); g.arc(r * s, -r * 0.08, r * 0.17, 0, 7); g.stroke(); g.beginPath(); g.moveTo(r * s, -r * 0.1); g.lineTo(r * s, 0); g.stroke(); }); g.restore();
  texto(g, `ALABEO ${(c.cr || 0) >= 0 ? "+" : ""}${(c.cr || 0).toFixed(1)}°`, 10, H - 28, "left", "#fff", 13, 700); texto(g, `CABECEO ${pit >= 0 ? "+" : ""}${pit.toFixed(1)}°`, 10, H - 10, "left", "#fff", 13, 700);
  // minimapa: la cancha, la geocerca, los paneles, las personas y el dron con su rumbo
  const [m, MW, MH] = ajustar($("minimapa")), ext = 29, kk = Math.min(MW, MH) / (2 * ext), ox = MW / 2, oy2 = MH / 2 + 4, Q = (wx, wy) => [ox + wx * kk, oy2 - wy * kk], [x, y, , psi] = c.d;
  m.fillStyle = "#17382a"; m.fillRect(0, 0, MW, MH);
  for (let i = -ext; i < ext; i += 5) { if ((Math.round(i / 5)) % 2 === 0) { m.fillStyle = "rgba(255,255,255,.045)"; const a = Q(i, ext), bb = Q(i + 5, -ext); m.fillRect(a[0], a[1], bb[0] - a[0], bb[1] - a[1]); } }
  m.strokeStyle = "rgba(255,255,255,.18)"; m.lineWidth = 1; for (let i = -20; i <= 20; i += 10) { let a = Q(i, -ext), bb = Q(i, ext); m.beginPath(); m.moveTo(...a); m.lineTo(...bb); m.stroke(); a = Q(-ext, i); bb = Q(ext, i); m.beginPath(); m.moveTo(...a); m.lineTo(...bb); m.stroke(); }
  m.setLineDash([6, 4]); m.strokeStyle = col.alerta; m.lineWidth = 1.6; const g1 = Q(-ARENA, ARENA), g2 = Q(ARENA, -ARENA); m.strokeRect(g1[0], g1[1], g2[0] - g1[0], g2[1] - g1[1]); m.setLineDash([]);
  texto(m, "GEOCERCA 25 m", g1[0] + 6, g1[1] + 16, "left", col.alerta, 12, 700, false);
  (S.paneles || []).forEach(p => { const a = Q(p[0], p[1]), bb = Q(p[2], p[3]); m.strokeStyle = "#f2f4f8"; m.lineWidth = 3; m.beginPath(); m.moveTo(...a); m.lineTo(...bb); m.stroke(); });
  if (S.ruta && c.ruta) { m.fillStyle = col.acento; c.ruta.forEach(q => { const [rx, ry] = Q(q[0], q[1]); m.beginPath(); m.arc(rx, ry, 2.5, 0, 7); m.fill(); }); }
  (c.pers || []).forEach(q => { const [px, py] = Q(q.p[0], q.p[1]); m.fillStyle = q.rol === "ladron" ? col.peligro : "#d5dce8"; m.beginPath(); m.arc(px, py, 4.5, 0, 7); m.fill(); m.strokeStyle = "#0b1220"; m.lineWidth = 1; m.stroke(); });
  const [dx, dy] = Q(x, y); m.fillStyle = "rgba(47,164,231,.2)"; m.beginPath(); m.moveTo(dx, dy); m.arc(dx, dy, 46, -(psi + rad(c.pan || 0)) - 0.6, -(psi + rad(c.pan || 0)) + 0.6); m.closePath(); m.fill();
  m.save(); m.translate(dx, dy); m.rotate(-psi); m.fillStyle = col.acento; m.strokeStyle = "#fff"; m.lineWidth = 1.5; m.beginPath(); m.moveTo(11, 0); m.lineTo(-8, 7); m.lineTo(-4, 0); m.lineTo(-8, -7); m.closePath(); m.fill(); m.stroke(); m.restore();
  texto(m, "N ↑", MW - 8, 18, "right", "#fff", 14, 700, false); texto(m, `RUMBO ${String(Math.round(((90 - deg(psi)) % 360 + 360) % 360)).padStart(3, "0")}°`, 8, MH - 10, "left", "#fff", 13, 700);
}

// ------------------------------------------------------------------------------------------------------------------ mapa táctico (Enseñar por puntos de paso)
let M = 28;
function dibujarMapa() {
  const cv = $("mapa"), [g, W, H] = ajustar(cv), c = S.c; if (S.panel !== "mapa") return;
  const k = Math.min(W, H) / (2 * M), P = (x, y) => [W / 2 + x * k, H / 2 - y * k]; S.escala = k;
  g.fillStyle = "#10141a"; g.fillRect(0, 0, W, H); g.strokeStyle = "rgba(125,155,189,.10)"; g.lineWidth = 1; g.font = "10px monospace"; g.fillStyle = "rgba(138,148,162,.6)"; g.textAlign = "left";
  for (let m = -25; m <= 25; m += 5) { let a = P(m, -M), b = P(m, M); g.beginPath(); g.moveTo(...a); g.lineTo(...b); g.stroke(); a = P(-M, m); b = P(M, m); g.beginPath(); g.moveTo(...a); g.lineTo(...b); g.stroke(); if (m) { g.fillText(m, P(m, 0)[0] + 2, P(m, 0)[1] + 11); g.fillText(m, P(0, m)[0] + 3, P(0, m)[1] - 2); } }
  g.setLineDash([6, 5]); g.strokeStyle = "rgba(217,164,65,.6)"; const a1 = P(-ARENA, ARENA); g.strokeRect(a1[0], a1[1], 2 * ARENA * k, 2 * ARENA * k); g.setLineDash([]);
  S.lidar.forEach(q => { const [px, py] = P(q[0], q[1]); g.fillStyle = "rgba(125,155,189,.5)"; g.fillRect(px - 1, py - 1, 2, 2); });
  (S.paneles || []).forEach(p => { g.strokeStyle = "#d8d4c8"; g.lineWidth = Math.max(3, 0.05 * k * 3); g.beginPath(); g.moveTo(...P(p[0], p[1])); g.lineTo(...P(p[2], p[3])); g.stroke(); });
  if (S.ruta && c && c.ruta) { g.fillStyle = "rgba(125,155,189,.8)"; c.ruta.forEach(q => { const [rx, ry] = P(q[0], q[1]); g.beginPath(); g.arc(rx, ry, 3, 0, 7); g.fill(); }); }
  if (!c) return;
  candidatos().forEach(o => { const [px, py] = P(o.q.p[0], o.q.p[1]); g.strokeStyle = col.alerta; g.lineWidth = 2; g.beginPath(); g.arc(px, py, 14, 0, 7); g.stroke(); texto(g, "posible objetivo", px + 18, py - 8, "left", col.alerta, 10, 600, false); });
  (c.pers || []).forEach(q => { const [px, py] = P(q.p[0], q.p[1]); g.beginPath(); g.arc(px, py, 7, 0, 7); g.fillStyle = q.rol === "ladron" ? col.peligro : "#9aa3ae"; g.fill(); texto(g, q.rol === "ladron" ? "ladrón" : "civil", px + 10, py + 4, "left", col.texto, 10, 500, false); });
  if (S.wp.length) { g.strokeStyle = "rgba(125,155,189,.7)"; g.setLineDash([5, 4]); g.beginPath(); g.moveTo(...P(c.d[0], c.d[1])); S.wp.forEach(p => g.lineTo(...P(p.x, p.y))); g.stroke(); g.setLineDash([]); }
  const ens = c.ens || {};
  S.wp.forEach((p, i) => {
    const [x, y] = P(p.x, p.y), hecho = i < (ens.i || 0), activo = ens.ir && i === ens.i, cc = hecho ? col.ok || "#8fb3a0" : activo ? col.alerta : col.acento, a = rad(p.yaw);
    g.strokeStyle = cc; g.lineWidth = i === S.sel ? 2.5 : 1.5; g.beginPath(); g.arc(x, y, 24, 0, 7); g.stroke(); g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * 24, y - Math.sin(a) * 24); g.stroke();
    g.fillStyle = cc; g.beginPath(); g.arc(x + Math.cos(a) * 24, y - Math.sin(a) * 24, 5, 0, 7); g.fill(); g.beginPath(); g.arc(x, y, 6, 0, 7); g.fill(); texto(g, String(i + 1), x - 3, y + 3.5, "left", "#0d1014", 9, 700, false);
    if (p.pan || p.tilt !== -5) texto(g, `pan ${p.pan | 0}° · tilt ${p.tilt | 0}°`, x + 30, y + 4, "left", cc, 10);
  });
  const [x, y] = P(c.d[0], c.d[1]), pan = rad(c.pan || 0);
  g.fillStyle = "rgba(125,155,189,.14)"; g.beginPath(); g.moveTo(x, y); g.arc(x, y, 90, -(c.d[3] + pan) - 0.6, -(c.d[3] + pan) + 0.6); g.closePath(); g.fill();
  g.save(); g.translate(x, y); g.rotate(-c.d[3]); g.fillStyle = col.acento; g.strokeStyle = "#fff"; g.lineWidth = 1.4; g.beginPath(); g.moveTo(15, 0); g.lineTo(-10, 9); g.lineTo(-5, 0); g.lineTo(-10, -9); g.closePath(); g.fill(); g.stroke(); g.restore();
}

// ------------------------------------------------------------------------------------------------------------------ barra superior, avisos y bucle
let avisoT = 0;
function aviso(t, alerta = false) { evento(t, alerta ? "alerta" : ""); const a = $("aviso"); a.textContent = t; a.className = alerta ? "alerta" : ""; a.style.display = "block"; clearTimeout(avisoT); avisoT = setTimeout(() => (a.style.display = "none"), 3200); }
const hora = () => new Date().toLocaleTimeString("es-CO", { hour12: false });
function evento(txt, nivel = "") {
  const u = S.eventos[0]; if (u && u.txt === txt && performance.now() - u.t < 1500) return;
  S.eventos.unshift({ txt, nivel, h: hora(), t: performance.now() }); if (S.eventos.length > 40) S.eventos.pop();
  const lista = $("logLista"); lista.innerHTML = S.eventos.slice(0, 6).map(e => `<div class="ev ${e.nivel}"><time>${e.h}</time><i></i><span>${e.txt}</span></div>`).join(""); set("logEst", S.eventos.length + " eventos");
}
function registrarEventos(a, c) {
  if (!a) return; const fa = FIJADOS.includes(a.eb), fc = FIJADOS.includes(c.eb);
  if (a.eb !== c.eb) evento("Modo: " + c.eb, fc && !fa ? "ok" : ""); if (fc && !fa) evento("Objetivo fijado", "ok"); if (fa && !fc) evento("Objetivo perdido: búsqueda", "alerta");
  if (c.arb && c.arb !== a.arb) evento("Árbitro: " + (ALERTAS[c.arb] || c.arb).toLowerCase(), c.arb === "punto_ciego" || c.arb === "perimetro" ? "alerta" : "peligro");
  if ((c.en_camara || []).length && !(a.en_camara || []).length) evento("Persona detectada · ID " + c.en_camara[0].id, "");
  if (c.ens && a.ens && c.ens.f360 && !a.ens.f360) evento("Giro de 360° en curso", "");
}
let _n = 0, _t = performance.now();
function lazo() {
  const ahora = performance.now(); _n++; if (ahora - _t > 1000) { S.fps = _n * 1000 / (ahora - _t); _n = 0; _t = ahora; }
  requestAnimationFrame(lazo);                                           // primero el siguiente cuadro: un error al dibujar no debe detener la pantalla
  for (const f of [dibujarHUD, dibujarCsi2, dibujarLidar, dibujarTel, dibujarMapa]) { try { f(); } catch (e) { if (!S.errDib) { S.errDib = true; console.warn("dibujo:", f.name, e); } } }
}

// ------------------------------------------------------------------------------------------------------------------ vistas
function ponerPanel(p) {
  S.panel = p; $("cam0").style.visibility = p === "dron" ? "visible" : "hidden"; $("sinvideo").style.visibility = p === "dron" ? "visible" : "hidden";
  $("mapa").style.display = p === "mapa" ? "block" : "none"; $("barramapa").style.display = p === "mapa" ? "flex" : "none"; $("hud").style.display = p === "dron" ? "block" : "none";
  if (p === "mapa" && S.estado === "ia") tomarControl("puntos");
}
function tomarControl(e = "manual") { S.estado = e; post("/modo", { modo: "ensenar", sub: e === "puntos" ? "mapa" : "manual" }); }
function devolverIA() { S.estado = "ia"; post("/modo", { modo: "auto" }); aviso("La IA guía el dron"); }

// ------------------------------------------------------------------------------------------------------------------ mando: teclado y mouse (ORDENES §G.1)
const teclas = new Set(); let panAng = 0, tiltAng = -5, ultimoCam = "";
const VUELO = new Set(["KeyW", "KeyS", "KeyA", "KeyD", "KeyQ", "KeyE", "Space", "KeyC", "KeyF"]);
const PROPIAS = new Set([...VUELO, "ShiftLeft", "ShiftRight", "ControlLeft", "ControlRight", "KeyV", "KeyM", "KeyG", "KeyB", "KeyP", "KeyR", "Tab", "Digit1", "Digit4", "Escape", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"]);
const eje = (a, b) => (teclas.has(a) ? 1 : 0) - (teclas.has(b) ? 1 : 0);
const usarCamara = () => post("/camara", { modo: S.asist ? "asistida" : "manual", pan: panAng, tilt: tiltAng });
function accion(code) {
  if (code === "Escape") return alternarMenu();
  if (code === "Tab") return ponerPanel(S.panel === "dron" ? "mapa" : "dron");
  if (code === "Digit1") return ponerPanel("mapa");
  if (code === "Digit4") return ponerPanel("dron");
  if (code === "KeyP") return alternarPausa();
  if (code === "KeyR") { S.ruta = !S.ruta; return; }
  if (code === "KeyB") return post("/grabar", { on: !S.grabando });
  if (code === "KeyV") { S.asist = !S.asist; usarCamara(); return aviso(S.asist ? "Cámara asistida: el pan-tilt sigue al objetivo" : "Cámara manual"); }
  if (code === "KeyG") return S.estado === "ia" ? tomarControl("manual") : devolverIA();
  if (code === "KeyM") { if (S.estado === "puntos") tomarControl("manual"); else tomarControl("puntos"); return aviso(S.estado === "puntos" ? "Modo puntos de paso" : "Modo manual"); }
}
function alternarPausa() { S.pausa = !S.pausa; }
addEventListener("keydown", ev => {
  if (/SELECT|INPUT|TEXTAREA/.test(ev.target.tagName) || !PROPIAS.has(ev.code)) return;
  ev.preventDefault();
  if (!ev.repeat && !teclas.has(ev.code)) { if (VUELO.has(ev.code) && S.estado !== "manual" && !menuAbierto()) tomarControl("manual"); accion(ev.code); }
  teclas.add(ev.code);
}, true);
addEventListener("keyup", ev => teclas.delete(ev.code), true);
addEventListener("blur", () => teclas.clear());
let arrastraCam = false;
addEventListener("mousedown", ev => {
  if (menuAbierto() || ev.target.closest("button, select, input, #menu")) return;
  if (ev.button === 1) { arrastraCam = true; ev.preventDefault(); return; }
  if (S.estado === "ia" && S.panel === "dron") return;
  if (S.panel === "mapa" && S.estado === "puntos") return;                          // los clics del mapa son de los puntos de paso (abajo)
  if (ev.button === 0) fijarObjetivo(ev); else if (ev.button === 2) { post("/soltar"); aviso("Objetivo soltado"); }
});
addEventListener("mouseup", ev => { if (ev.button === 1) arrastraCam = false; });
addEventListener("mousemove", ev => { if (!arrastraCam || S.asist) return; panAng = Math.round(lim(panAng - ev.movementX * 0.3, -90, 90)); tiltAng = Math.round(lim(tiltAng - ev.movementY * 0.3, -45, 15)); });
addEventListener("contextmenu", ev => { if (!menuAbierto() && S.estado !== "ia") ev.preventDefault(); });
addEventListener("wheel", ev => { if (S.panel === "mapa" && ev.target === $("mapa")) { M = lim(M * (ev.deltaY > 0 ? 1.1 : 0.9), 10, 40); ev.preventDefault(); } }, { passive: false });
function candidatos() { const c = S.c; if (!c || !c.en_camara) return []; return c.en_camara.map(o => ({ q: (c.pers || []).find(p => p.id === o.id), j: o.i })).filter(o => o.q); }
function fijarObjetivo(ev) {
  const lista = candidatos(); if (!lista.length) return aviso("No hay un posible objetivo a la vista: mantenga F para el giro de 360°", true);
  let mejor = lista[0], d0 = 1e9; const c = S.c;
  if (S.panel === "mapa") { const r = $("mapa").getBoundingClientRect(), k = S.escala, mx = (ev.clientX - r.left - r.width / 2) / k, my = (r.height / 2 - (ev.clientY - r.top)) / k; lista.forEach(o => { const d = Math.hypot(o.q.p[0] - mx, o.q.p[1] - my); if (d < d0) { d0 = d; mejor = o; } }); }
  else { const r = $("hud").getBoundingClientRect(), px = ev.clientX - r.left, py = ev.clientY - r.top; S.cajas.forEach(b => { const d = Math.hypot((b.x0 + b.x1) / 2 - px, (b.y0 + b.y1) / 2 - py); if (d < d0) { d0 = d; const o = lista.find(l => l.j === b.j); if (o) mejor = o; } }); }
  post("/fijar", { j: mejor.j }); teclas.delete("KeyF"); aviso(mejor.q.rol === "ladron" ? "Objetivo fijado: el sospechoso" : "Persona descartada: no es el sospechoso");
}
setInterval(() => {
  if (S.estado !== "manual") return;
  const f = teclas.has("ControlLeft") || teclas.has("ControlRight") ? 0.25 : (teclas.has("ShiftLeft") || teclas.has("ShiftRight") ? 1.0 : 0.6);
  if (teclas.has("ArrowLeft") || teclas.has("ArrowRight")) panAng = lim(panAng + 9 * eje("ArrowLeft", "ArrowRight"), -90, 90);
  if (teclas.has("ArrowUp") || teclas.has("ArrowDown")) tiltAng = lim(tiltAng + 6 * eje("ArrowUp", "ArrowDown"), -45, 15);
  post("/manual", { vx: f * eje("KeyW", "KeyS"), vy: f * eje("KeyA", "KeyD"), wz: f * eje("KeyQ", "KeyE"), pan: 0, tilt: 0, vz: f * eje("Space", "KeyC"), f360: teclas.has("KeyF") ? 1 : 0 });
  const cc = `${S.asist}|${panAng}|${tiltAng}`; if (cc !== ultimoCam) { ultimoCam = cc; usarCamara(); }
}, 100);

// ------------------------------------------------------------------------------------------------------------------ puntos de paso (mapa táctico)
const mp = ev => { const r = $("mapa").getBoundingClientRect(); return [ev.clientX - r.left, ev.clientY - r.top, r]; };
const aMundo = (px, py, r) => [(px - r.width / 2) / S.escala, (r.height / 2 - py) / S.escala];
const aPix = (x, y, r) => [r.width / 2 + x * S.escala, r.height / 2 - y * S.escala];
let arrastre = null;
const reenviar = () => post("/waypoint", { borrar: "todos" }).then(() => S.wp.forEach(p => post("/waypoint", { x: p.x, y: p.y, yaw: p.yaw, pan: p.pan, tilt: p.tilt })));
function cercano(px, py, r) { for (let i = S.wp.length - 1; i >= 0; i--) { const [x, y] = aPix(S.wp[i].x, S.wp[i].y, r), a = rad(S.wp[i].yaw), d = Math.hypot(px - x, py - y); if (Math.hypot(px - (x + Math.cos(a) * 24), py - (y - Math.sin(a) * 24)) < 11 || (d > 18 && d < 32)) return { i, tipo: "girar" }; if (d < 12) return { i, tipo: "mover" }; } return null; }
$("mapa").addEventListener("mousedown", ev => {
  if (S.estado !== "puntos" || ev.button) return; const [px, py, r] = mp(ev), h = cercano(px, py, r);
  if (h) { S.sel = h.i; arrastre = h; return; }
  const [x, y] = aMundo(px, py, r); if (Math.abs(x) > 24 || Math.abs(y) > 24) return;
  const ant = S.wp.length ? S.wp[S.wp.length - 1] : { x: S.c.d[0], y: S.c.d[1] };
  S.wp.push({ x, y, yaw: Math.round(deg(Math.atan2(y - ant.y, x - ant.x))), pan: 0, tilt: -5 }); S.sel = S.wp.length - 1; arrastre = { i: S.sel, tipo: "girar" };
});
addEventListener("mousemove", ev => {
  if (!arrastre) return; const [px, py, r] = mp(ev), p = S.wp[arrastre.i], [x, y] = aPix(p.x, p.y, r);
  if (arrastre.tipo === "girar") { if (Math.hypot(px - x, py - y) > 6) p.yaw = Math.round(deg(Math.atan2(-(py - y), px - x))); } else { const [mx, my] = aMundo(px, py, r); p.x = lim(mx, -24, 24); p.y = lim(my, -24, 24); }
});
addEventListener("mouseup", () => { if (arrastre) { arrastre = null; reenviar(); } });
$("mIr").onclick = () => { tomarControl("puntos"); reenviar().then(() => setTimeout(() => post("/waypoint", { ir: true }), 150)); };
$("mParar").onclick = () => post("/waypoint", { ir: false });
$("mUltimo").onclick = () => { S.wp.pop(); S.sel = S.wp.length - 1; post("/waypoint", { borrar: "ultimo" }); };
$("mTodos").onclick = () => { S.wp.length = 0; S.sel = -1; post("/waypoint", { borrar: "todos" }); };

// ------------------------------------------------------------------------------------------------------------------ menú de ajustes y ayuda (Esc)
const menuAbierto = () => $("menu").classList.contains("ver");
function alternarMenu() { $("menu").classList.toggle("ver"); if (menuAbierto()) pintarMenu(); }
function pintarMenu() {
  const reps = [["rendicion", "El ladrón se rinde"], ["reencuentro_alto", "Reencuentro desde arriba"], ["salto", "El ladrón salta al dron"], ["civil_curioso", "El civil mira o graba"], ["cambio_de_v", "El ladrón cambia de V"]];
  $("menuCaja").innerHTML = `<h3><span>Ajustes · ${NOMBRE_DRON}</span><button id="mxCerrar">Cerrar (Esc)</button></h3>
    <h5>Vistas</h5><div class="fila"><button data-p="dron" class="${S.panel === "dron" ? "act" : ""}">Cámara del dron (4)</button><button data-p="mapa" class="${S.panel === "mapa" ? "act" : ""}">Mapa táctico · enseñar (1)</button><span style="color:var(--tenue)">Tab alterna las dos. El mundo en 3D (centinela) es la ventana de Unreal.</span></div>
    <h5>Control del dron</h5><div class="fila"><button id="mxIA" class="${S.estado === "ia" ? "act" : ""}">La IA guía (G)</button><button id="mxMan" class="${S.estado === "manual" ? "act" : ""}">Tomar el mando · manual</button><button id="mxPts" class="${S.estado === "puntos" ? "act" : ""}">Puntos de paso (M)</button><button id="mxAsi" class="${S.asist ? "act" : ""}">Cámara asistida (V)</button></div>
    <h5>Misión</h5><div class="fila"><select id="mxMision"><option value="vivo">Simulación en vivo</option>${reps.map(([k, t]) => `<option value="repeticiones_v17_h/${k}.json" ${S.fuente === "rep" && S.rep.url === k ? "selected" : ""}>Repetición · ${t}</option>`).join("")}<option value="mision_completa.json">Misión completa · despegue, tránsito y zona</option></select><button id="mxRuta" class="${S.ruta ? "act" : ""}">Ruta de búsqueda (R)</button><button id="mxGrab" class="${S.grabando ? "rec" : ""}">${S.grabando ? "Parar y guardar" : "Grabar mi demostración (B)"}</button><button id="mxOtra">Otra partida</button></div>
    <h5>Escena</h5><div class="fila"><span style="color:var(--tenue)">Día (activa). La noche se elige al armar el nivel de Unreal (DRONIA_NOCHE=1); ver el manual.</span></div>
    <h5>Teclas</h5><table>
      <tr><td>W S · A D</td><td>adelante·atrás · lado</td><td>Q E</td><td>girar</td></tr><tr><td>Espacio · C</td><td>subir · bajar</td><td>Shift · Ctrl</td><td>rápido · lento</td></tr>
      <tr><td>F (mantener)</td><td>giro de 360° buscando</td><td>Botón central</td><td>arrastrar = pan y tilt</td></tr><tr><td>Clic izquierdo</td><td>fijar al posible objetivo</td><td>Clic derecho</td><td>soltar objetivo</td></tr>
      <tr><td>V · flechas</td><td>cámara asistida · pan/tilt</td><td>G · M</td><td>IA guía · puntos de paso</td></tr><tr><td>Tab · 1 · 4</td><td>alterna vista · mapa · cámara</td><td>R · B · P</td><td>ruta · grabar · pausa</td></tr>
      <tr><td>Rueda</td><td>zoom del mapa</td><td>Esc</td><td>este menú</td></tr></table>`;
  $("mxCerrar").onclick = alternarMenu;
  document.querySelectorAll("#menuCaja [data-p]").forEach(b => (b.onclick = () => { ponerPanel(b.dataset.p); alternarMenu(); }));
  $("mxIA").onclick = () => { devolverIA(); alternarMenu(); }; $("mxMan").onclick = () => { tomarControl("manual"); alternarMenu(); }; $("mxPts").onclick = () => { tomarControl("puntos"); ponerPanel("mapa"); alternarMenu(); };
  $("mxAsi").onclick = () => { accion("KeyV"); pintarMenu(); }; $("mxRuta").onclick = () => { S.ruta = !S.ruta; pintarMenu(); }; $("mxGrab").onclick = () => { accion("KeyB"); alternarMenu(); }; $("mxOtra").onclick = () => { post("/reset"); alternarMenu(); };
  $("mxMision").onchange = ev => { const v = ev.target.value; if (v === "vivo") conectar(); else { cargarRep(v).then(() => { S.rep.url = v.split("/").pop().replace(".json", ""); }); } alternarMenu(); };
}
$("menu").addEventListener("mousedown", ev => { if (ev.target === $("menu")) alternarMenu(); });
$("bMenu").onclick = alternarMenu; $("bPausa").onclick = alternarPausa; $("bRuta").onclick = () => accion("KeyR"); $("bGrabar").onclick = () => accion("KeyB");

// ------------------------------------------------------------------------------------------------------------------ arranque
const q = new URLSearchParams(location.search);
ponerPanel(q.get("vista") === "mapa" ? "mapa" : "dron");
if (q.get("modo") === "manual") tomarControl("manual");
conectar();
requestAnimationFrame(lazo);
