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
  hist: [], imgEdad: 0, lidar: [], luna: [], cajas: [], wp: [], sel: -1, fps: 0, demo: "", fuente: "vivo", vista: [0, 0, 0, 0] };
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
const col = { texto: "#e7e3d9", tenue: "#8a94a2", linea: "#262e39", acento: "#7d9bbd", alerta: "#d9a441", peligro: "#cf5c57" };
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

// ------------------------------------------------------------------------------------------------------------------ cámara principal con HUD
function rectImagen(W, H) { const w = Math.min(W, H * 4 / 3), h = w * 3 / 4; return { x: (W - w) / 2, y: (H - h) / 2, w, h }; }
// la imagen de Unreal llega con ~0.2-0.3 s de retraso: el horizonte y las cajas se calculan con el cuadro de la simulación del instante en que se tomó la imagen
function cuadroDeLaImagen() {
  if (!S.video[0] || !S.hist.length) return S.c;
  const objetivo = performance.now() - S.imgEdad * 1000 - 70; let mejor = S.hist[S.hist.length - 1];
  for (const h of S.hist) if (Math.abs(h[0] - objetivo) < Math.abs(mejor[0] - objetivo)) mejor = h;
  return mejor[1];
}
function dibujarHUD() {
  const [g, W, H] = ajustar($("hud")), cv = S.c, c = cuadroDeLaImagen();
  if (S.panel !== "dron" || !c) { S.cajas = []; return; }
  const R = rectImagen(W, H), cx = R.x + R.w / 2, cy = R.y + R.h / 2, ppd = R.h / VFOV;
  if (!S.video[0]) { g.fillStyle = "#0a0c0f"; g.fillRect(R.x, R.y, R.w, R.h); }
  g.save(); g.beginPath(); g.rect(R.x, R.y, R.w, R.h); g.clip();
  // horizonte artificial
  const cam = camara(c), pit = (c.gmb ?? -5) + MONTAJE, roll = rad(c.cr || 0);
  g.save(); g.translate(cx, cy); g.rotate(-roll); g.strokeStyle = "rgba(231,227,217,.55)"; g.lineWidth = 1;
  const hy = pit * ppd; g.beginPath(); g.moveTo(-R.w * 0.46, hy); g.lineTo(-40, hy); g.moveTo(40, hy); g.lineTo(R.w * 0.46, hy); g.stroke();
  [-20, -10, 10, 20].forEach(p => { const y = hy - p * ppd; g.setLineDash(p < 0 ? [3, 3] : []); g.beginPath(); g.moveTo(-30, y); g.lineTo(-12, y); g.moveTo(12, y); g.lineTo(30, y); g.stroke(); texto(g, Math.abs(p) + "", 38, y + 3, "left", "rgba(231,227,217,.5)", 9); });
  g.setLineDash([]); g.restore();
  // cinta de rumbo
  const hdg = (deg(c.d[3]) + 360) % 360; g.strokeStyle = "rgba(231,227,217,.55)";
  for (let a = Math.floor(hdg / 5) * 5 - 40; a <= hdg + 40; a += 5) {
    const x = cx + (a - hdg) * 3.2, n = ((a % 360) + 360) % 360; g.beginPath(); g.moveTo(x, R.y + 26); g.lineTo(x, R.y + 26 - (n % 15 === 0 ? 7 : 3)); g.stroke();
    if (n % 30 === 0) texto(g, { 0: "E", 90: "N", 180: "O", 270: "S" }[n] ?? String(n).padStart(3, "0"), x, R.y + 13, "center", "rgba(231,227,217,.6)", 9);
  }
  g.fillStyle = "rgba(13,16,20,.8)"; g.fillRect(cx - 20, R.y + 29, 40, 14); texto(g, String(Math.round(hdg) % 360).padStart(3, "0") + "°", cx, R.y + 40, "center", col.texto, 10, 600);
  // retícula
  g.strokeStyle = "rgba(231,227,217,.7)"; g.lineWidth = 1.1; g.beginPath(); g.moveTo(cx - 12, cy); g.lineTo(cx - 4, cy); g.moveTo(cx + 4, cy); g.lineTo(cx + 12, cy); g.moveTo(cx, cy - 12); g.lineTo(cx, cy - 4); g.moveTo(cx, cy + 4); g.lineTo(cx, cy + 12); g.stroke();
  // cajas de YOLO: las personas que la simulación ve en cámara, proyectadas a la imagen (no inventadas)
  S.cajas = [];
  const fijado = ["PERSECUCION", "PERDIDA", "RECONFIRMAR", "FIJADO"].includes(c.eb);
  (c.en_camara || []).forEach(o => {
    const q = (c.pers || []).find(p => p.id === o.id); if (!q) return;
    const alto = q.alto || q.est || 1.7, a = proyectar(cam, [q.p[0], q.p[1], 0.05], R), b = proyectar(cam, [q.p[0], q.p[1], alto], R); if (!a || !b) return;
    const h = Math.abs(a[1] - b[1]), w = h * 0.38, x0 = b[0] - w / 2, y0 = Math.min(a[1], b[1]), objetivo = fijado && q.rol === "ladron";
    S.cajas.push({ j: o.i, id: o.id, x0, y0, x1: x0 + w, y1: y0 + h, rol: q.rol });
    g.strokeStyle = objetivo ? col.peligro : "rgba(231,227,217,.85)"; g.lineWidth = objetivo ? 1.8 : 1.2; g.strokeRect(x0, y0, w, h);
    const et = objetivo ? `ID ${o.id} · OBJETIVO · ${o.d.toFixed(1)} m` : `ID ${o.id} · PERSONA · ${o.d.toFixed(1)} m`; fuente(g, 10, 600, true);
    const tw = g.measureText(et).width + 8; g.fillStyle = objetivo ? col.peligro : "rgba(40,48,58,.92)"; g.fillRect(x0, Math.max(R.y, y0 - 14), tw, 14); texto(g, et, x0 + 4, Math.max(R.y, y0 - 14) + 10.5, "left", "#fff", 10, 600);
  });
  g.restore();
  // bloque superior izquierdo: modo, objetivo y tiempo a la vista
  const obj = fijado ? "FIJADO" : ((c.en_camara || []).length ? "posible objetivo" : "ninguno");
  g.fillStyle = "rgba(13,16,20,.55)"; g.fillRect(R.x + 8, R.y + 8, 190, 50);
  texto(g, "MODO  " + (c.eb ?? "–"), R.x + 14, R.y + 23, "left", col.texto, 11, 600);
  texto(g, "OBJETIVO  " + obj, R.x + 14, R.y + 37, "left", fijado ? "#e8a19d" : col.tenue, 10);
  texto(g, "A LA VISTA  " + (c.tf ?? 0).toFixed(1) + " s", R.x + 14, R.y + 51, "left", col.tenue, 10);
  // pie de la imagen: pan/tilt y campo de visión
  texto(g, `PAN ${(c.pan || 0) >= 0 ? "+" : ""}${(c.pan || 0).toFixed(0)}°  TILT ${(c.gmb ?? 0).toFixed(0)}°  ·  HFOV ${HFOV}°`, R.x + 10, R.y + R.h - 8, "left", col.tenue, 10);
  if (c.ens && c.ens.f360) texto(g, "BÚSQUEDA 360°", cx, R.y + R.h - 8, "center", col.texto, 11, 600);
  const alerta = { reflejo_ataque: "REFLEJO · EVASIÓN", evadiendo: "EVASIÓN", amenaza: "AMENAZA CERCANA", punto_ciego: "PUNTO CIEGO", perimetro: "PERÍMETRO" }[c.arb];
  if (alerta) { fuente(g, 12, 700); const tw = g.measureText(alerta).width + 24; g.fillStyle = "rgba(60,44,12,.9)"; g.fillRect(cx - tw / 2, R.y + R.h - 60, tw, 24); g.strokeStyle = col.alerta; g.strokeRect(cx - tw / 2, R.y + R.h - 60, tw, 24); texto(g, alerta, cx, R.y + R.h - 43, "center", col.alerta, 12, 700); }
  S.vista = [R.x, R.y, R.w, R.h];
}

// ------------------------------------------------------------------------------------------------------------------ CSI#2 (rótulo)
function dibujarCsi2() {
  const [g, W, H] = ajustar($("hud1")); if (!S.c) return;
  texto(g, `HFOV ${HFOV}° · −90°`, W - 8, H - 8, "right", col.tenue, 10);
}

// ------------------------------------------------------------------------------------------------------------------ mapa de los dos LiDAR
function dibujarLidar() {
  const [g, W, H] = ajustar($("lidar")), c = S.c; if (!c || W < 60 || H < 60) return;
  const cx = W / 2, cy = H * 0.56, alc = 14, k = Math.min(W / 2 - 14, cy - 22, H - cy - 8) / alc, [x, y, , psi] = c.d;
  const P = (wx, wy) => [cx + (wx - x) * k, cy - (wy - y) * k];
  g.strokeStyle = "#232b35"; g.lineWidth = 1; [5, 10].forEach(r => { g.beginPath(); g.arc(cx, cy, r * k, 0, 7); g.stroke(); texto(g, r + " m", cx + r * k * 0.71 + 3, cy - r * k * 0.71, "left", "#4b5560", 9); });
  g.beginPath(); g.moveTo(cx, cy - alc * k); g.lineTo(cx, cy + alc * k); g.moveTo(cx - alc * k, cy); g.lineTo(cx + alc * k, cy); g.stroke(); texto(g, "N", cx, cy - alc * k - 3, "center", col.tenue, 10);
  (S.paneles || []).forEach(p => { const a = P(p[0], p[1]), b = P(p[2], p[3]); g.strokeStyle = "#3b4551"; g.lineWidth = 2; g.beginPath(); g.moveTo(...a); g.lineTo(...b); g.stroke(); });
  g.fillStyle = col.acento; S.lidar.forEach(q => { const [px, py] = P(q[0], q[1]); if (Math.abs(px - cx) < W && Math.abs(py - cy) < H) g.fillRect(px - 1, py - 1, 2, 2); });
  g.fillStyle = "#c9d3de"; S.luna.forEach(q => { const [px, py] = P(q[0], q[1]); if (Math.abs(px - cx) < W && Math.abs(py - cy) < H) g.fillRect(px - 1, py - 1, 2, 2); });
  const tf = Math.min(c.lid ?? 30, 30); g.strokeStyle = col.acento; g.lineWidth = 1.2; g.beginPath(); g.moveTo(cx, cy); g.lineTo(cx + Math.cos(psi) * tf * k, cy - Math.sin(psi) * tf * k); g.stroke();
  if (c.luna && (c.luna[0] || c.luna[1])) { const [lx, ly] = P(c.luna[0], c.luna[1]); g.strokeStyle = "#c9d3de"; g.setLineDash([3, 3]); g.beginPath(); g.moveTo(cx, cy); g.lineTo(lx, ly); g.stroke(); g.setLineDash([]); }
  g.save(); g.translate(cx, cy); g.rotate(-psi); g.fillStyle = col.texto; g.beginPath(); g.moveTo(9, 0); g.lineTo(-6, 5.5); g.lineTo(-3, 0); g.lineTo(-6, -5.5); g.closePath(); g.fill(); g.restore();
  texto(g, "● TF03 (fijo, al frente)", 10, H - 8, "left", col.acento, 9); texto(g, "● TF-Luna (en el pan-tilt)", W - 10, H - 8, "right", "#c9d3de", 9);
}

// ------------------------------------------------------------------------------------------------------------------ telemetría: datos, actitud y minimapa
function bateria() { const pct = lim(100 - S.tSim / 9, 0, 100); return { pct, v: 14.0 + 2.8 * pct / 100 }; }
const MODO_VUELO = { ia: "GUIADO (IA)", manual: "MANUAL", puntos: "PUNTOS DE PASO" };
function dibujarTel() {
  const c = S.c, el = $("telDatos"); if (!c) { el.innerHTML = ""; return; }
  const [x, y, z] = c.d, v = Math.hypot((c.dv || [0, 0])[0], (c.dv || [0, 0])[1]), b = bateria(), edad = performance.now() - S.ultimo;
  const enlace = S.fuente === "rep" ? "REPETICIÓN" : (edad > 1500 ? "SIN ENLACE" : Math.round(edad) + " ms"), margen = ARENA - Math.max(Math.abs(x), Math.abs(y));
  const luna = c.luna && (c.luna[0] || c.luna[1]) ? Math.hypot(c.luna[0] - x, c.luna[1] - y, (c.luna[2] ?? 0) - z).toFixed(1) + " m" : "sin eco";
  const filas = [["ALTURA", z.toFixed(1) + " m", ""], ["VELOCIDAD", v.toFixed(1) + " m/s", ""], ["BATERÍA", `${b.v.toFixed(1)} V · ${b.pct.toFixed(0)} %`, b.pct < 20 ? "peligro" : b.pct < 35 ? "alerta" : ""],
    ["GPS", "14 sat · HDOP 0.8", ""], ["ENLACE", enlace, enlace === "SIN ENLACE" ? "peligro" : ""], ["MODO DE VUELO", MODO_VUELO[S.estado], ""], ["TF03", (c.lid ?? 30) < 29.5 ? c.lid.toFixed(1) + " m" : "> 30 m", ""],
    ["TF-LUNA", luna, ""], ["GEOCERCA", margen.toFixed(1) + " m", margen < 3 ? "peligro" : margen < 8 ? "alerta" : ""]];
  el.innerHTML = filas.map(([k, val, cl]) => `<div class="f"><span>${k}</span><b class="${cl}">${val}</b></div>`).join("");
  // actitud: horizonte artificial con el dron visto desde atrás que se inclina con el alabeo
  const [g, W, H] = ajustar($("actitud")), r = Math.min(W, H) / 2 - 8, mx = W / 2, my = H / 2, roll = rad(c.cr || 0), pit = c.cp || 0;
  g.save(); g.beginPath(); g.arc(mx, my, r, 0, 7); g.clip(); g.translate(mx, my); g.rotate(-roll);
  const oy = pit * r / 35; g.fillStyle = "#2d3b4c"; g.fillRect(-r * 2, -r * 2 + oy, r * 4, r * 2); g.fillStyle = "#3b352d"; g.fillRect(-r * 2, oy, r * 4, r * 2);
  g.strokeStyle = "rgba(231,227,217,.7)"; g.beginPath(); g.moveTo(-r, oy); g.lineTo(r, oy); g.stroke();
  [-20, -10, 10, 20].forEach(p => { const yy = oy - p * r / 35; g.beginPath(); g.moveTo(-r * 0.22, yy); g.lineTo(r * 0.22, yy); g.stroke(); });
  g.restore(); g.strokeStyle = col.linea; g.lineWidth = 1.5; g.beginPath(); g.arc(mx, my, r, 0, 7); g.stroke();
  g.save(); g.translate(mx, my); g.rotate(-roll * 0); g.strokeStyle = col.texto; g.fillStyle = col.texto; g.lineWidth = 2;     // el dron visto desde atrás: brazos y cuerpo
  g.rotate(-roll); g.beginPath(); g.moveTo(-r * 0.55, 0); g.lineTo(r * 0.55, 0); g.stroke(); g.fillRect(-r * 0.12, -r * 0.08, r * 0.24, r * 0.16); [-0.55, 0.55].forEach(s => { g.beginPath(); g.arc(r * s, -r * 0.05, r * 0.09, 0, 7); g.stroke(); }); g.restore();
  texto(g, `ALAB. ${(c.cr || 0) >= 0 ? "+" : ""}${(c.cr || 0).toFixed(1)}°  CAB. ${pit >= 0 ? "+" : ""}${pit.toFixed(1)}°`, mx, H - 4, "center", col.tenue, 9);
  // minimapa: la cancha, la geocerca, los paneles y el dron con su rumbo
  const [m, MW, MH] = ajustar($("minimapa")), ext = 30, kk = Math.min(MW, MH) / (2 * ext), ox = MW / 2, oy2 = MH / 2, Q = (wx, wy) => [ox + wx * kk, oy2 - wy * kk];
  m.fillStyle = "#1c2a22"; m.fillRect(0, 0, MW, MH);
  for (let i = -ext; i < ext; i += 5) { if (((i / 5) | 0) % 2 === 0) { m.fillStyle = "rgba(255,255,255,.035)"; const a = Q(i, ext), bb = Q(i + 5, -ext); m.fillRect(a[0], a[1], bb[0] - a[0], bb[1] - a[1]); } }
  m.setLineDash([4, 3]); m.strokeStyle = "rgba(217,164,65,.7)"; const g1 = Q(-ARENA, ARENA), g2 = Q(ARENA, -ARENA); m.strokeRect(g1[0], g1[1], g2[0] - g1[0], g2[1] - g1[1]); m.setLineDash([]); texto(m, "GEOCERCA", g1[0] + 4, g1[1] + 11, "left", "rgba(217,164,65,.8)", 8, 600, false);
  (S.paneles || []).forEach(p => { const a = Q(p[0], p[1]), bb = Q(p[2], p[3]); m.strokeStyle = "#d8d4c8"; m.lineWidth = 2; m.beginPath(); m.moveTo(...a); m.lineTo(...bb); m.stroke(); });
  (c.pers || []).forEach(q => { const [px, py] = Q(q.p[0], q.p[1]); m.fillStyle = q.rol === "ladron" ? "#cf5c57" : "#b9c0c9"; m.beginPath(); m.arc(px, py, 3, 0, 7); m.fill(); });
  const [dx, dy] = Q(x, y); m.save(); m.translate(dx, dy); m.rotate(-c.d[3]); m.fillStyle = col.acento; m.strokeStyle = "#fff"; m.lineWidth = 1; m.beginPath(); m.moveTo(8, 0); m.lineTo(-6, 5); m.lineTo(-3, 0); m.lineTo(-6, -5); m.closePath(); m.fill(); m.stroke(); m.restore();
  texto(m, "N", MW - 10, 12, "right", col.tenue, 10, 700, false); texto(m, `${Math.round(((deg(c.d[3]) + 360) % 360))}°`, 6, MH - 6, "left", col.texto, 10, 600);
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
function aviso(t, alerta = false) { const a = $("aviso"); a.textContent = t; a.className = alerta ? "alerta" : ""; a.style.display = "block"; clearTimeout(avisoT); avisoT = setTimeout(() => (a.style.display = "none"), 3200); }
function barra() {
  const c = S.c; if (!c) return;
  $("bModo").textContent = c.eb ?? "–"; $("bControl").textContent = MODO_VUELO[S.estado];
  const edad = performance.now() - S.ultimo, e = $("bEnlace"); e.textContent = S.fuente === "rep" ? "REPETICIÓN" : edad > 1500 ? "SIN ENLACE" : "ENLAZADO"; e.className = edad > 1500 && S.fuente !== "rep" ? "peligro" : "";
  $("bHora").textContent = new Date().toLocaleTimeString("es-CO", { hour12: false }) + "  ·  T+" + Math.floor(S.tSim / 60) + ":" + String(Math.floor(S.tSim % 60)).padStart(2, "0");
  $("bGrabar").className = S.grabando ? "rec" : ""; $("bGrabar").textContent = S.grabando ? "Grabando" : "Grabar"; $("bRuta").className = S.ruta ? "act" : ""; $("bPausa").className = S.pausa ? "act" : "";
  $("pieEstado").textContent = (S.fuente === "rep" ? "Repetición" : "Simulación en vivo") + " · datos simulados · " + S.fps.toFixed(0) + " fps";
}
let _n = 0, _t = performance.now();
function lazo() {
  const ahora = performance.now(); _n++; if (ahora - _t > 1000) { S.fps = _n * 1000 / (ahora - _t); _n = 0; _t = ahora; }
  requestAnimationFrame(lazo);                                           // primero el siguiente cuadro: un error al dibujar no debe detener la pantalla
  for (const f of [dibujarHUD, dibujarCsi2, dibujarLidar, dibujarTel, dibujarMapa, barra]) { try { f(); } catch (e) { if (!S.errDib) { S.errDib = true; console.warn("dibujo:", f.name, e); } } }
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
