// Estación de tierra · MÍNIMO. La interfaz de operación (operacion.css) conectada a la Jetson real: video MJPEG, /datos y el control de tomas del panel de campo.
// Todo pasa por el servidor de la estación (/jetson/...), que reenvía al panel de la Jetson (servidor.py, constante JETSON). Sin gimbal: el mínimo lleva cámara y LiDAR fijos al chasis.
"use strict";
const J = "/jetson";
const $ = id => document.getElementById(id);
const lim = (v, a, b) => Math.max(a, Math.min(b, v));
const rad = g => g * Math.PI / 180, deg = r => r * 180 / Math.PI;
const col = { texto: "#e8ecef", tenue: "#98a2ab", tenue2: "#6a747d", linea: "#2a3036", acento: "#2fa4e7", alerta: "#f5a623", peligro: "#e5484d", ok: "#2ecc71" };
const S = { d: null, ultimo: 0, lat: 0, video: false };
let JETSON_DIRECTO = "talos-jetson.local:8080";   // dirección real de la Jetson (la pregunta al servidor de la estación): sirve para abrir /alinear y /calibrar en otra pestaña
const set = (id, t) => { const e = $(id); if (e && e.textContent !== String(t)) e.textContent = t; };
const clase = (id, c) => { const e = $(id); if (e && e.className !== c) e.className = c; };
const ancho = (id, pct, color) => { const e = $(id); if (e) { e.style.width = lim(pct, 0, 100) + "%"; if (color) e.style.background = color; } };
const num = (v, d = 1, u = "") => v == null || Number.isNaN(v) ? "–" : v.toFixed(d) + u;
const guardar = (k, v) => { try { localStorage.setItem(k, v); } catch (e) { /* sin almacenamiento: se queda en la sesión */ } };
const leerGuardado = k => { try { return localStorage.getItem(k); } catch (e) { return null; } };
const ALTURA_PERSONA = 1.72;          // la misma que usa la Jetson para estimar la distancia por el alto de la caja

// ----------------------------------------------------------------------------------------------- datos
async function sondear() {
  const t0 = performance.now();
  try {
    const r = await fetch(J + "/datos", { cache: "no-store" });
    if (!r.ok) throw new Error(r.status);
    S.d = await r.json(); S.lat = performance.now() - t0; S.ultimo = performance.now();
  } catch (e) { /* queda el último dato; la barra marca SIN ENLACE si pasa de 1.5 s */ }
  setTimeout(sondear, 150);
}
const img = $("cam0");
let resActual = leerGuardado("minimo_res") || "alta";
function conectarVideo() {
  img.onload = () => { S.video = true; img.style.display = "block"; $("sinvideo").style.display = "none"; };
  img.onerror = () => { if (S.pausa) return; S.video = false; img.style.display = "none"; $("sinvideo").style.display = "flex"; setTimeout(() => { img.src = `${J}/video?res=${resActual}&t=${Date.now()}`; }, 1500); };
  img.src = `${J}/video?res=${resActual}&t=${Date.now()}`;
}
$("selRes").value = resActual;
$("selRes").onchange = () => { resActual = $("selRes").value; guardar("minimo_res", resActual); S.video = false; img.src = `${J}/video?res=${resActual}&t=${Date.now()}`; };

// ----------------------------------------------------------------------------------------------- dibujo
function ajustar(cv) {
  const dpr = Math.min(devicePixelRatio || 1, 1.25), w = cv.clientWidth, h = cv.clientHeight;
  if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) { cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); }
  const g = cv.getContext("2d"); g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, w, h);
  return [g, w, h];
}
const fuente = (g, tam, peso = 400, mono = false) => { g.font = `${peso} ${tam}px ${mono ? "'IBM Plex Mono','Roboto Mono','Cascadia Mono',Consolas,monospace" : "Inter,'Segoe UI',Roboto,sans-serif"}`; };
function texto(g, t, x, y, al = "left", c = col.texto, tam = 11, peso = 500, mono = true) { fuente(g, tam, peso, mono); g.textAlign = al; g.fillStyle = "rgba(0,0,0,.6)"; g.fillText(t, x + 1, y + 1); g.fillStyle = c; g.fillText(t, x, y); }
function rectImagen(W, H) { const w = Math.min(W, H * 4 / 3), h = w * 3 / 4; return { x: (W - w) / 2, y: (H - h) / 2, w, h }; }

function dibujarHUD() {
  const [g, W, H] = ajustar($("hud")), d = S.d; if (!d) return;
  const R = rectImagen(W, H), cx = R.x + R.w / 2, cy = R.y + R.h / 2, u = Math.max(0.85, R.h / 720), my = R.y + R.h - Math.max(46, Math.round(44 * u));
  const geo = d.geo || {}, p = d.pix || {}, L = d.lidar || {}, v = d.vision || {}, tm = d.tomas || {};
  const linea = (x0, y0, x1, y1, an = 2) => { g.lineWidth = an + 2; g.strokeStyle = "rgba(0,0,0,.55)"; g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke(); g.lineWidth = an; g.strokeStyle = "rgba(255,255,255,.92)"; g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke(); };
  // horizonte: con la Pixhawk conectada se mueve con el cabeceo y gira con el alabeo (la cámara mira −2.4° respecto al chasis)
  if (p.ok && p.pitch != null) {
    const ppd = R.h / (geo.vfov || 54), elev = (geo.cam_pitch ?? -2.4) + p.pitch, hy = cy + elev * ppd, roll = rad(p.roll || 0), ln = R.w * 0.34;
    g.save(); g.beginPath(); g.rect(R.x, R.y, R.w, my - R.y); g.clip(); g.translate(cx, hy); g.rotate(-roll);
    g.setLineDash([10, 7]); g.lineWidth = 3; g.strokeStyle = "rgba(0,0,0,.5)"; g.beginPath(); g.moveTo(-ln, 0); g.lineTo(ln, 0); g.stroke();
    g.lineWidth = 1.6; g.strokeStyle = "rgba(255,176,0,.95)"; g.beginPath(); g.moveTo(-ln, 0); g.lineTo(ln, 0); g.stroke(); g.setLineDash([]);
    texto(g, "HORIZONTE", ln + 6, 5, "left", "#ffb000", 12, 700, false); g.restore();
  }
  linea(cx - 22 * u, cy, cx - 7 * u, cy); linea(cx + 7 * u, cy, cx + 22 * u, cy); linea(cx, cy - 22 * u, cx, cy - 7 * u); linea(cx, cy + 7 * u, cx, cy + 22 * u);
  const cerca = L.valido && L.m < 3;
  const alerta = cerca ? `OBSTÁCULO A ${L.m.toFixed(2)} m · MENOS DE 3 m` : v.personas > 0 ? `PERSONA DETECTADA · ID ${v.id ?? "–"} · ${v.conf ? Math.round(v.conf * 100) : "–"} %` : "";
  if (alerta) { fuente(g, 16, 700); const tw = g.measureText(alerta).width + 34, c = cerca ? col.peligro : col.ok; g.fillStyle = cerca ? "rgba(47,18,20,.94)" : "rgba(10,38,22,.94)"; g.fillRect(cx - tw / 2, my - 40, tw, 30); g.strokeStyle = c; g.lineWidth = 2; g.strokeRect(cx - tw / 2, my - 40, tw, 30); texto(g, alerta, cx, my - 19, "center", c, 16, 700); }
  if (tm.activa) { const t = tm.preparando ? `PREPÁRATE · ${tm.resta ?? ""} s` : `${tm.id} · ${tm.texto}`; fuente(g, 18, 700); const tw = g.measureText(t).width + 30; g.fillStyle = "rgba(16,48,63,.92)"; g.fillRect(cx - tw / 2, R.y + 10, tw, 32); g.strokeStyle = col.acento; g.lineWidth = 1.6; g.strokeRect(cx - tw / 2, R.y + 10, tw, 32); texto(g, t, cx, R.y + 32, "center", "#fff", 18, 700); }
  g.fillStyle = "rgba(7,9,11,.88)"; g.fillRect(R.x, my, R.w, R.y + R.h - my); g.fillStyle = col.linea; g.fillRect(R.x, my, R.w, 1);
  const nivelado = p.ok && p.pitch != null && Math.abs(p.pitch) <= 1 && Math.abs(p.roll) <= 1;
  const segs = [["LIDAR", L.valido ? L.m.toFixed(2) + " m" : "sin retorno", cerca ? col.peligro : col.acento], ["PERSONAS", String(v.personas ?? 0), v.personas ? col.ok : col.tenue],
    ["CABECEO · ALABEO", p.ok && p.pitch != null ? `${num(p.pitch, 1)}° · ${num(p.roll, 1)}°` : "sin Pixhawk", p.ok ? (nivelado ? col.ok : col.alerta) : col.tenue2],
    ["CUADROS · YOLO", v.fps ? `${v.fps.toFixed(0)} fps · ${num(v.yolo, 0)} ms` : "–", v.fps >= 24 ? col.ok : v.fps >= 18 ? col.alerta : col.peligro], ["CAMPO", `${geo.hfov ?? 68.3}° × ${geo.vfov ?? 54}°`, col.tenue]];
  const sw = R.w / segs.length; segs.forEach(([k, val, c], i) => { texto(g, k, R.x + i * sw + 12, my + 17, "left", col.tenue2, 12, 700, false); texto(g, val, R.x + i * sw + 12, R.y + R.h - 10, "left", c, Math.round(16 * Math.min(1.2, Math.max(u, .9))), 700); });
}
function dibujarLidar() {
  const [g, W, H] = ajustar($("lidarg")), d = S.d; if (!d || !d.hist || W < 60) return;
  const x0 = 8, x1 = W - 8, y0 = 24, y1 = H - 10, MAX = 20, Y = m => y1 - lim(m, 0, MAX) / MAX * (y1 - y0), n = d.hist.length;
  g.strokeStyle = col.linea; g.lineWidth = 1; [0, 3, 10, 20].forEach(m => { g.beginPath(); g.moveTo(x0, Y(m)); g.lineTo(x1, Y(m)); g.stroke(); texto(g, m + " m", x1, Y(m) - 3, "right", m === 3 ? col.peligro : col.tenue2, 11); });
  g.strokeStyle = "rgba(229,72,77,.5)"; g.setLineDash([5, 4]); g.beginPath(); g.moveTo(x0, Y(3)); g.lineTo(x1, Y(3)); g.stroke(); g.setLineDash([]);
  g.strokeStyle = col.acento; g.lineWidth = 1.8; g.beginPath(); d.hist.forEach((m, i) => { const x = x0 + i / Math.max(1, n - 1) * (x1 - x0), y = Y(m); i ? g.lineTo(x, y) : g.moveTo(x, y); }); g.stroke();
  const suelo = S.suelo; if (suelo && suelo < MAX) { g.strokeStyle = "rgba(255,176,0,.7)"; g.setLineDash([2, 4]); g.beginPath(); g.moveTo(x0, Y(suelo)); g.lineTo(x1, Y(suelo)); g.stroke(); g.setLineDash([]); texto(g, "suelo esperado", x0 + 2, Y(suelo) - 3, "left", "#ffb000", 11); }
}
function dibujarActitud() {                                  // horizonte artificial pequeño: cielo, tierra, línea de nivel y símbolo del dron
  const [g, W, H] = ajustar($("actitud")), d = S.d, p = (d && d.pix) || {};
  g.fillStyle = "#07090b"; g.fillRect(0, 0, W, H); if (W < 60) return;
  const ok = p.ok && p.pitch != null, roll = rad(ok ? p.roll : 0), esc = Math.min(H / 40, 5), mx = W * 0.32, my = H / 2 + 6, oy = (ok ? p.pitch : 0) * esc;
  g.save(); g.beginPath(); g.rect(0, 0, W, H); g.clip(); g.translate(mx, my); g.rotate(-roll);
  g.fillStyle = ok ? "#3a5a70" : "#2a3036"; g.fillRect(-W * 2, -H * 3 + oy, W * 4, H * 3); g.fillStyle = ok ? "#5e5446" : "#22262a"; g.fillRect(-W * 2, oy, W * 4, H * 3);
  g.strokeStyle = "#f3f5f7"; g.lineWidth = 1.6; g.beginPath(); g.moveTo(-W * 2, oy); g.lineTo(W * 2, oy); g.stroke();
  for (let q = -15; q <= 15; q += 5) { if (!q) continue; const yy = oy - q * esc, l = q % 10 === 0 ? 30 : 15; g.lineWidth = 1.2; g.strokeStyle = "rgba(243,245,247,.9)"; g.beginPath(); g.moveTo(-l, yy); g.lineTo(l, yy); g.stroke(); if (q % 10 === 0) texto(g, String(Math.abs(q)), l + 5, yy + 4, "left", "#f3f5f7", 11, 600, false); }
  g.restore();
  g.save(); g.translate(mx, my); g.strokeStyle = "#ffb000"; g.lineWidth = 3; g.beginPath(); g.moveTo(-50, 0); g.lineTo(-18, 0); g.lineTo(-18, 7); g.moveTo(50, 0); g.lineTo(18, 0); g.lineTo(18, 7); g.stroke(); g.fillStyle = "#ffb000"; g.fillRect(-2.5, -2.5, 5, 5); g.restore();
  if (!ok) texto(g, "SIN PIXHAWK", mx, my + 4, "center", col.alerta, 12, 700, false);
  const niv = ok ? (Math.abs(p.pitch) <= 1 && Math.abs(p.roll) <= 1 ? ["NIVELADO", col.ok] : Math.abs(p.pitch) <= 3 && Math.abs(p.roll) <= 3 ? ["CASI NIVELADO", col.alerta] : ["INCLINADO", col.peligro]) : ["conecta la batería", col.tenue];
  const tx = W - 10;
  texto(g, niv[0], tx, 22, "right", niv[1], 14, 700, false);
  texto(g, `CABECEO ${ok ? (p.pitch >= 0 ? "+" : "") + p.pitch.toFixed(1) + "°" : "–"}`, tx, 46, "right", col.texto, 13, 600);
  texto(g, `ALABEO  ${ok ? (p.roll >= 0 ? "+" : "") + p.roll.toFixed(1) + "°" : "–"}`, tx, 64, "right", col.texto, 13, 600);
  texto(g, "+ = nariz arriba", tx, H - 26, "right", col.tenue2, 11, 500, false); texto(g, "+ alabeo = lado derecho abajo", tx, H - 10, "right", col.tenue2, 11, 500, false);
}

// ----------------------------------------------------------------------------------------------- tablero
const NIVEL = { ok: "ok", warn: "alerta", info: "", bad: "peligro" };
const METAS = { E0: [2, 3], E2: [5, 10], E3: [5, 10], E1: [1, 3], E4: [6, 30], E5: [2, 5], E6: [2, 5] };    // corta / completa (guía de campo del 21-oct)
function rayoYSuelo(d) {                                      // con la altura del LiDAR y la inclinación del dron: dónde debe tocar el piso el rayo
  const geo = d.geo || {}, p = d.pix || {}, h = parseFloat($("hLidar").value);
  const elev = (geo.lidar_pitch ?? -6.7) + (p.ok && p.pitch != null ? p.pitch : 0);
  set("rElev", num(elev, 1, "°") + (p.ok && p.pitch != null ? "" : " (sin Pixhawk)"));
  let suelo = null;
  if (h > 0 && elev < 0) {
    suelo = h / Math.tan(rad(-elev)); set("rSuelo", suelo.toFixed(1) + " m");
    set("rPers", h <= ALTURA_PERSONA ? "cualquier distancia" : ((h - ALTURA_PERSONA) / Math.tan(rad(-elev))).toFixed(1) + " m");
  } else { set("rSuelo", h > 0 ? "no toca el suelo" : "–"); set("rPers", "–"); }
  S.suelo = suelo;
  const L = d.lidar || {}, v = d.vision || {};
  let est = "Escribe la altura del LiDAR (desde el suelo) para calcular el rayo.";
  if (h > 0 && L.valido && !v.personas && elev < 0) { const hh = L.m * Math.tan(rad(-elev)); est = `Con ${L.m.toFixed(2)} m y nadie delante, si el rayo está en el piso la altura sería ≈ ${hh.toFixed(2)} m (escribiste ${h.toFixed(2)} m).`; }
  else if (h > 0 && suelo && L.valido && v.personas) est = L.m > suelo - 1 ? "El LiDAR mide el piso o el fondo, no a la persona (está más lejos que el suelo esperado)." : "El LiDAR mide algo antes del suelo esperado: persona u obstáculo.";
  set("rEst", est);
}
function tablero() {
  const d = S.d, edad = performance.now() - S.ultimo, sinEnlace = !d || edad > 1500;
  set("bHora", new Date().toLocaleTimeString("es-CO", { hour12: false })); set("bFecha", new Date().toLocaleDateString("es-CO"));
  set("bJetson", sinEnlace ? "SIN ENLACE" : Math.round(S.lat) + " ms"); clase("bJetson", sinEnlace ? "peligro" : "");
  if (!d) { set("pieEstado", "● Esperando datos de la Jetson (" + JETSON_DIRECTO + ")…"); return; }
  const L = d.lidar || {}, p = d.pix || {}, b = d.bat || {}, v = d.vision || {}, geo = d.geo || {}, vid = d.video || {}, ex = d.expo || {}, sis = d.sist || {};
  set("bPix", p.ok ? "CONECTADA" : "SIN ENLACE"); clase("bPix", p.ok ? "ok" : "alerta");
  set("bArmado", p.ok ? (p.armado ? "ARMADO" : "DESARMADO") : "–"); clase("bArmado", p.armado ? "peligro" : "");
  set("bBat", b.volt ? b.volt.toFixed(1) + " V" : "–"); clase("bBat", !b.volt ? "" : b.volt < b.corte ? "peligro" : b.volt < b.aviso ? "alerta" : "ok");
  set("bLidar", L.valido ? L.m.toFixed(2) + " m" : L.ok ? "sin retorno" : "SIN DATO"); clase("bLidar", L.valido && L.m < 3 ? "peligro" : L.ok ? "" : "alerta");
  const hayAct = p.ok && p.pitch != null, niv = hayAct && Math.abs(p.pitch) <= 1 && Math.abs(p.roll) <= 1;
  set("bNivel", hayAct ? `${num(p.pitch, 1)}° · ${num(p.roll, 1)}°` : "–"); clase("bNivel", !hayAct ? "" : niv ? "ok" : Math.abs(p.pitch) <= 3 && Math.abs(p.roll) <= 3 ? "alerta" : "peligro");
  set("bVision", v.fps ? v.fps.toFixed(0) + " fps · " + (v.personas ?? 0) + " pers." : "–"); clase("bVision", v.fps >= 24 ? "ok" : v.fps >= 18 ? "alerta" : "peligro");
  const tm = d.tomas || {}; set("bToma", tm.activa ? tm.id : "ninguna"); clase("bToma", tm.activa ? "acento" : "");
  // tarjetas
  set("vLid", L.valido ? L.m.toFixed(2) : "–"); ancho("bLid", (L.valido ? L.m : 0) / 20 * 100, L.valido && L.m < 3 ? col.peligro : col.acento);
  set("sLid", L.ok ? `señal ${L.fuerza ?? "–"}${L.m < 3 && L.valido ? " · BAJO 3 m" : ""}` : "sin dato del TF03");
  set("vBat", b.volt ? b.volt.toFixed(1) : "–"); ancho("bBatBarra", b.pct ?? 0, b.volt && b.volt < b.corte ? col.peligro : b.volt && b.volt < b.aviso ? col.alerta : col.ok);
  set("sBat", b.volt ? `${(b.pct ?? 0).toFixed(0)} % · ${b.celda ? b.celda.toFixed(2) : "–"} V/celda · aviso ${b.aviso} V` : "sin Pixhawk: sin dato de batería");
  set("eModo", p.ok ? (p.modo ?? "–") : "–"); set("eArm", p.ok ? (p.armado ? "ARMADO" : "DESARMADO") : "SIN ENLACE"); clase("eArm", "etq " + (p.armado ? "alerta" : p.ok ? "ok" : ""));
  set("sModo", p.alt != null ? `Altura ${p.alt.toFixed(1)} m · vel ${(p.vel ?? 0).toFixed(1)} m/s` : "Altura –");
  rayoYSuelo(d);
  // velocidades y GPS (Pixhawk)
  set("vSuelo", p.vel_suelo != null ? p.vel_suelo.toFixed(1) + " m/s" : "–");
  set("vAsc", p.ascenso != null ? (p.ascenso > 0.05 ? "▲ +" : p.ascenso < -0.05 ? "▼ " : "= ") + p.ascenso.toFixed(2) + " m/s" : "–"); clase("vAsc", p.ascenso == null ? "" : Math.abs(p.ascenso) > 0.3 ? "alerta" : "");
  set("vAltR", p.alt != null ? p.alt.toFixed(2) + " m" : "–"); set("vRum", p.rumbo != null ? Math.round(p.rumbo) + "° " + ["N", "NE", "E", "SE", "S", "SO", "O", "NO"][Math.round(p.rumbo / 45) % 8] : "–");
  set("sVel", p.ok ? (p.armado ? "ARMADO: con hélices habría empuje" : "desarmado") : "sin Pixhawk");
  const gp = p.gps || {}, fixTxt = { 0: "sin GPS", 1: "sin fijación", 2: "2D", 3: "3D", 4: "3D + DGPS", 5: "RTK flotante", 6: "RTK fijo" };
  set("gFix", gp.fix != null ? (fixTxt[gp.fix] || gp.fix) : "–"); clase("gFix", gp.fix >= 3 ? "ok" : gp.fix >= 2 ? "alerta" : gp.fix != null ? "peligro" : "");
  set("gSats", gp.sats ?? "–"); clase("gSats", gp.sats >= 8 ? "ok" : gp.sats >= 6 ? "alerta" : gp.sats != null ? "peligro" : "");
  set("gHdop", gp.hdop != null ? gp.hdop.toFixed(2) : "–"); clase("gHdop", gp.hdop == null ? "" : gp.hdop <= 1.5 ? "ok" : gp.hdop <= 3 ? "alerta" : "peligro");
  set("gLL", gp.lat != null ? gp.lat.toFixed(5) + " , " + gp.lon.toFixed(5) : "–");
  set("gEst", gp.hdop == null ? "sin dato" : gp.hdop <= 1.5 ? "buena posición" : gp.hdop <= 3 ? "aceptable" : "mala: esperar más satélites o salir al aire libre");
  // persona
  const q = (v.pers || [])[0];
  const htmlP = q ? `<div class="fila"><span>ID · confianza</span><b>${q.id} · ${Math.round(q.conf * 100)} %</b></div>
    <div class="fila"><span>Ángulo desde el centro</span><b>${q.az > 0 ? "+" : ""}${q.az}° ${q.az > 2 ? "(derecha)" : q.az < -2 ? "(izquierda)" : "(centro)"}</b></div>
    <div class="fila"><span>Distancia por la cámara</span><b>${q.trunc ? ">" : "~"}${q.d_cam.toFixed(1)} m</b></div>
    <div class="fila"><span>Distancia del LiDAR</span><b>${L.valido ? L.m.toFixed(2) + " m" : "–"}</b></div>
    <div class="fila"><span>¿El rayo le pega a la persona?</span><b class="${q.en_caja ? "si" : "no"}">${q.en_caja ? "SÍ" : "NO"}</b></div>
    <div class="sub">${q.en_caja && L.valido && !q.trunc ? `cámara − LiDAR = ${(q.d_cam - L.m >= 0 ? "+" : "") + (q.d_cam - L.m).toFixed(2)} m (la cámara es orientativa)` : "la distancia de la cámara solo es confiable con la persona completa"}</div>` : `<div class="sub">ninguna persona en cuadro</div>`;
  if ($("persona").dataset.h !== htmlP) { $("persona").dataset.h = htmlP; $("persona").innerHTML = htmlP; }
  // imagen y enlace
  set("iMedia", ex.media != null ? `${ex.media.toFixed(0)} / 255` : "–"); clase("iMedia", ex.media == null ? "" : ex.media < 50 || ex.media > 200 ? "alerta" : "ok");
  set("iSat", ex.sat != null ? `${ex.sat.toFixed(1)} % / ${ex.osc.toFixed(1)} %` : "–"); clase("iSat", ex.sat != null && (ex.sat > 5 || ex.osc > 30) ? "alerta" : "");
  set("iFps", v.fps ? `${v.fps.toFixed(0)} fps · ${num(v.yolo, 0)} ms` : "–");
  set("iVid", `${vid.origen ? vid.origen[0] + "×" + vid.origen[1] : "–"} · ${vid.kbps != null ? (vid.kbps / 1000).toFixed(1) + " Mbps" : "–"} · ${Math.round(S.lat)} ms`);
  set("iTemp", `Jetson: CPU ${num(sis.cpu, 0, " °C")} · GPU ${num(sis.gpu, 0, " °C")}`);
  // geometría
  set("gFov", `${geo.hfov ?? "–"}° × ${geo.vfov ?? "–"}°`); set("gPit", `${geo.cam_pitch ?? "–"}° / ${geo.lidar_pitch ?? "–"}°`);
  set("gPx", geo.lidar_px ? `${(geo.lidar_px[0] * 100).toFixed(1)} % , ${(geo.lidar_px[1] * 100).toFixed(1)} %` : "sin alinear");
  const nivel = sinEnlace ? "peligro" : (b.volt && b.volt < b.aviso) || (v.fps && v.fps < 18) ? "alerta" : "ok", est = $("estTel");
  est.className = "est " + nivel; est.textContent = nivel === "ok" ? "NOMINAL" : nivel === "alerta" ? "PRECAUCIÓN" : "SIN ENLACE";
  set("pieEstado", `● DATOS REALES · Jetson ${JETSON_DIRECTO} · ${S.video ? "video " + resActual : "sin video"} · enlace ${Math.round(S.lat)} ms · TALOS-AI estación · mínimo`);
  // registro de eventos
  const ev = d.eventos || [];
  const html = ev.slice(0, 10).map(e => `<div class="ev ${NIVEL[e[1]] ?? ""}"><time>${e[0]}</time><i></i><span>${e[2]}</span></div>`).join("");
  if ($("logLista").dataset.h !== html) { $("logLista").dataset.h = html; $("logLista").innerHTML = html; } set("logEst", ev.length);
  // progreso de tomas
  const hechas = {}; (tm.historial || []).forEach(h => { if (h[2] === "ok") { const e = h[1].split("-")[0]; hechas[e] = (hechas[e] || 0) + 1; } });
  const htmlG = Object.keys(METAS).map(e => { const [c, f] = METAS[e], n = hechas[e] || 0; return `<div class="${n >= c ? "listo" : n > 0 ? "medio" : ""}"><b>${e}</b>${n} · ${c}/${f}</div>`; }).join("");
  if ($("progreso").dataset.h !== htmlG) { $("progreso").dataset.h = htmlG; $("progreso").innerHTML = htmlG; }
}

// ----------------------------------------------------------------------------------------------- tomas
let tomasListas = false;
function api(ruta) { return fetch(J + ruta, { cache: "no-store" }).then(r => r.text().then(t => ({ ok: r.ok, t }))).catch(() => ({ ok: false, t: "sin enlace con la Jetson" })); }
function selUrl() { const g = i => encodeURIComponent($(i).value); return `/toma/sel?esc=${g("t_esc")}&rep=${g("t_rep")}&altura=${g("t_alt")}&montaje=${g("t_mon")}&dist=${g("t_dist")}&nota=${encodeURIComponent($("t_nota").value || " ")}`; }   // el panel ignora los valores vacíos de la URL: un espacio deja la nota en blanco
function construirTomas(tm) {
  $("t_esc").innerHTML = Object.entries(tm.escenarios).map(([k, e]) => `<option value="${k}">${k} · ${e.nombre}</option>`).join("");
  $("t_mon").innerHTML = (tm.montajes || []).map(m => `<option>${m}</option>`).join("");
  ["t_esc", "t_rep", "t_alt", "t_mon", "t_dist"].forEach(i => $(i).addEventListener("change", () => api(selUrl())));
  $("t_nota").addEventListener("change", () => api(selUrl()));
  $("bIniciar").onclick = async () => { await api(selUrl()); const r = await api("/toma/iniciar"); set("tMsg", r.ok ? "" : r.t); };
  $("bCancelar").onclick = async () => { const r = await api("/toma/cancelar"); set("tMsg", r.ok ? "" : r.t); };
  $("t_alt").addEventListener("change", () => { const a = parseFloat($("t_alt").value); if (a > 0 && !$("hLidar").value) { $("hLidar").value = Math.max(0, a - 0.05).toFixed(2); guardar("minimo_hlidar", $("hLidar").value); } });   // el lente queda ~5 cm sobre el eje del LiDAR
  tomasListas = true;
}
function tablerotomas() {
  const tm = S.d && S.d.tomas; if (!tm || !tm.disponible) { if (S.d) set("estToma", "NO DISPONIBLE"); return; }
  if (!tomasListas) construirTomas(tm);
  anunciar(tm);
  const sel = tm.sel, e = tm.escenarios[sel.esc], enfoque = document.activeElement && $("tForm").contains(document.activeElement);
  if (!enfoque) { $("t_esc").value = sel.esc; $("t_rep").value = sel.rep; $("t_alt").value = sel.altura; $("t_mon").value = sel.montaje; $("t_dist").value = sel.dist; if (document.activeElement !== $("t_nota")) $("t_nota").value = sel.nota.trim(); }
  const c = e.campos; $("f_dist").style.display = c.includes("dist") ? "" : "none"; $("f_mon").style.display = c.includes("montaje") ? "" : "none"; $("f_nota").style.display = c.includes("nota") ? "" : "none";
  ["t_esc", "t_rep", "t_alt", "t_mon", "t_dist", "t_nota"].forEach(i => $(i).disabled = tm.activa);
  $("bIniciar").disabled = tm.activa; $("bCancelar").disabled = !tm.activa;
  const est = $("estToma"); est.textContent = tm.activa ? (tm.preparando ? "PREPARANDO" : "GRABANDO") : "LISTO"; est.className = "est " + (tm.activa ? "alerta" : "ok");
  const caja = $("tEstado");
  if (tm.activa) {
    caja.className = tm.preparando ? "prep" : "act";
    caja.innerHTML = `<div class="grande">${tm.preparando ? "PREPÁRATE" : tm.id}  ·  ${tm.resta ?? "–"} s</div><div class="peq">${tm.texto}</div>` + (tm.siguiente && !tm.preparando ? `<div class="peq">Paso ${tm.fase + 1} de ${tm.n_fases} · siguiente en ${tm.resta_fase ?? "–"} s: ${tm.siguiente}</div>` : "");
  } else { caja.className = ""; caja.innerHTML = `<div class="peq">Elige el escenario, pon la repetición y la altura real del lente, y pulsa INICIAR; la persona sigue lo que le digas (o lo que diga el portátil si activas Sonido).</div>`; }
  const clave = sel.esc; if ($("tGuia").dataset.e !== clave) { $("tGuia").dataset.e = clave; $("tGuia").innerHTML = `<p><b>${e.nombre}</b> · dura ${e.dur} s</p>` + e.guia.map(x => `<p>• ${x}</p>`).join(""); }
  $("tHist").innerHTML = tm.historial.length ? "Últimas: " + tm.historial.slice(0, 5).map(h => `<span class="${h[2] === "ok" ? "ok" : "mal"}">${h[1]} ${h[2]}</span>`).join(" · ") : "";
}

// ----------------------------------------------------------------------------------------------- mapa GPS (pequeño en la esquina; clic = grande)
let mapa = null, marca = null, rutaMapa = null, seguir = true, ultPos = null;
const puntosRuta = [];
function iniciarMapa() {
  if (typeof L === "undefined") { set("miniInfo", "sin mapa"); return; }
  const guardada = JSON.parse(leerGuardado("minimo_pos") || "null");
  mapa = L.map("miniMapa", { center: guardada || [4.65, -74.1], zoom: guardada ? 19 : 11, maxZoom: 21, zoomSnap: 0.5, zoomControl: false, attributionControl: true });
  mapa.attributionControl.setPrefix(false);
  L.tileLayer("/tiles/{z}/{x}/{y}.jpg", { maxNativeZoom: 19, maxZoom: 21, attribution: "Imágenes © Esri, Maxar, Earthstar Geographics", errorTileUrl: "" }).addTo(mapa);
  const icono = L.divIcon({ className: "dronmapa", iconSize: [40, 40], iconAnchor: [20, 20], html: '<svg viewBox="0 0 40 40"><path d="M20 3 33 34 20 28 7 34z" fill="#2fa4e7" stroke="#fff" stroke-width="2.2" stroke-linejoin="round"/></svg>' });
  marca = L.marker(guardada || [4.65, -74.1], { icon: icono, interactive: false, opacity: guardada ? 0.6 : 0 }).addTo(mapa);
  rutaMapa = L.polyline([], { color: "#ffb000", weight: 3, opacity: 0.9 }).addTo(mapa);
  L.control.scale({ imperial: false, position: "bottomright" }).addTo(mapa);
  mapa.on("dragstart", () => { seguir = false; });
  $("mini").addEventListener("click", ev => { if (!$("mini").classList.contains("grande") && ev.target.id !== "miniBtn") ampliarMapa(true); });
  $("miniBtn").onclick = ev => { ev.stopPropagation(); ampliarMapa(!$("mini").classList.contains("grande")); };
  $("miniCentro").onclick = ev => { ev.stopPropagation(); seguir = true; if (ultPos) mapa.setView(ultPos, Math.max(mapa.getZoom(), 19)); };
}
function ampliarMapa(si) {
  $("mini").classList.toggle("grande", si); $("mini").title = si ? "" : "Clic para ampliar el mapa"; $("miniBtn").textContent = si ? "✕ cerrar" : "⤢";
  setTimeout(() => { mapa.invalidateSize(); if (ultPos) mapa.setView(ultPos, si ? Math.max(mapa.getZoom(), 19) : 19); }, 60);
}
function actualizarMapa() {
  const p = (S.d && S.d.pix) || {}, g = p.gps || {};
  if (!mapa) return;
  if (g.lat == null || g.lon == null || (g.lat === 0 && g.lon === 0)) { set("miniInfo", p.ok ? `sin posición GPS (${g.sats ?? 0} sat)` : "sin Pixhawk"); return; }
  const pos = [g.lat, g.lon], primera = !ultPos;
  ultPos = pos; marca.setLatLng(pos).setOpacity(1);
  const svg = marca.getElement() && marca.getElement().querySelector("svg"); if (svg && p.rumbo != null) svg.style.transform = `rotate(${p.rumbo}deg)`;
  const ult = puntosRuta[puntosRuta.length - 1]; if (!ult || Math.abs(ult[0] - pos[0]) + Math.abs(ult[1] - pos[1]) > 1e-6) { puntosRuta.push(pos); if (puntosRuta.length > 600) puntosRuta.shift(); rutaMapa.setLatLngs(puntosRuta); }
  if (primera) { mapa.setView(pos, 19); guardar("minimo_pos", JSON.stringify(pos)); } else if (seguir) mapa.panTo(pos, { animate: false });
  set("miniInfo", `GPS ${["", "", "2D", "3D", "3D+", "RTK", "RTK"][g.fix] || g.fix} · ${g.sats} sat · HDOP ${g.hdop != null ? g.hdop.toFixed(1) : "–"}`);
}

// ----------------------------------------------------------------------------------------------- sonido del PC (lo mismo que dice el celular de /persona)
let audioOn = false, audioCtx = null, ultN = null;
function pitar(n, largo) { if (!audioOn || !audioCtx) return; let t = audioCtx.currentTime; for (let i = 0; i < Math.max(n, 1); i++) { const o = audioCtx.createOscillator(), g = audioCtx.createGain(); o.frequency.value = largo ? 600 : 1000; o.connect(g); g.connect(audioCtx.destination); g.gain.setValueAtTime(0.3, t); const d = largo ? 0.8 : 0.18; o.start(t); o.stop(t + d); t += d + 0.14; } }
function hablar(x) { if (!audioOn || !window.speechSynthesis) return; try { speechSynthesis.cancel(); const u = new SpeechSynthesisUtterance(x); u.lang = "es-CO"; u.rate = 1.0; speechSynthesis.speak(u); } catch (e) { /* sin voz en este equipo */ } }
function anunciar(T) { if (ultN === null) { ultN = T.n; return; } if (T.n === ultN) return; ultN = T.n; if (T.pitidos === -1) pitar(1, true); else if (T.pitidos > 0) pitar(T.pitidos); hablar(T.texto); }
$("bSonido").onclick = () => { audioOn = !audioOn; if (audioOn) { try { audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)(); audioCtx.resume(); } catch (e) { /* sin audio */ } pitar(1); hablar("Sonido del computador activado"); } $("bSonido").textContent = audioOn ? "🔊 Sonido: activado" : "🔈 Sonido: apagado"; $("bSonido").classList.toggle("act", audioOn); };

// ----------------------------------------------------------------------------------------------- enlace con la Jetson: dirección y búsqueda automática
async function estadoHost(ruta = "/jetson_estado") { try { const r = await (await fetch(ruta, { cache: "no-store" })).json(); JETSON_DIRECTO = r.host; return r; } catch (e) { return null; } }
$("bBuscar").onclick = async () => { set("msgHost", " buscando en la red…"); const r = await estadoHost("/jetson_buscar"); set("msgHost", r && r.ok ? " encontrada: " + r.host : " no la encontré"); };
$("bUsar").onclick = async () => { const h = $("inHost").value.trim(); if (!h) return; const r = await estadoHost("/jetson_host?h=" + encodeURIComponent(h)); set("msgHost", r && r.ok ? " conectada: " + r.host : " esa dirección no responde"); };
setInterval(() => { const sin = !S.d || performance.now() - S.ultimo > 3500; $("enlaceBanner").style.display = sin ? "block" : "none"; }, 1000);
estadoHost();

// ----------------------------------------------------------------------------------------------- arranque
$("hLidar").value = leerGuardado("minimo_hlidar") || ""; $("hLidar").addEventListener("change", () => guardar("minimo_hlidar", $("hLidar").value));
function abrirJetson(ruta, titulo) { S.pausa = true; img.removeAttribute("src"); $("modalTitulo").textContent = titulo; $("modalFrame").src = ruta; $("modalJ").classList.add("ver"); }
function cerrarJetson() { $("modalJ").classList.remove("ver"); $("modalFrame").src = "about:blank"; S.pausa = false; conectarVideo(); }
$("bAlinear").onclick = () => abrirJetson("/alinear", "ALINEAR EL LiDAR CON LA CÁMARA");
$("bCalibrar").onclick = () => abrirJetson("/calibrar", "CALIBRAR EL MONTAJE (cámara y LiDAR)");
$("modalCerrar").onclick = cerrarJetson;
window.addEventListener("message", ev => { if (ev.data === "cerrar-jetson") cerrarJetson(); });
if (location.search.includes("abajo")) setTimeout(() => { $("der").scrollTop = $("der").scrollHeight; }, 4500);   // solo para tomar capturas del final del panel
iniciarMapa(); setInterval(actualizarMapa, 500); sondear(); conectarVideo();
setInterval(() => { tablero(); tablerotomas(); }, 200);
(function bucle() { dibujarHUD(); dibujarLidar(); dibujarActitud(); requestAnimationFrame(bucle); })();
