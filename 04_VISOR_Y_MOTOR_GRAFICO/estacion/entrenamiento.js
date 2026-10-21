// Pestaña "Entrenamiento" de la estación: lee los archivos que escribe el entrenamiento (03_SIMULACION_RL/salida_v17_*/estado.json y metricas.json) por el servidor
// de la estación y dibuja las curvas. Solo lee archivos y dibuja en canvas 2D: no usa la GPU, no toca el entrenamiento ni a Unreal.
// "Ver partida de la política" abre en el mapa táctico la repetición que el entrenamiento guarda (replay_v17.json) con la política entrenada jugando.
const ENT = (() => {
  const E = { visible: false, corridas: [], carpeta: null, estado: null, metricas: [], t: 0, ocupado: false };
  const $ = id => document.getElementById(id);
  const SERIES = [
    ["recompensa", "Recompensa media por partida", m => m.adv && m.adv.recompensa, v => v.toFixed(1), "#2fa4e7"],
    ["cumplida", "Misión cumplida (%)", m => m.adv && m.adv.cumplida * 100, v => v.toFixed(0) + " %", "#2ecc71"],
    ["custodia", "Custodia ≥ 60 s en el nivel actual (%)", m => { const c = m.curriculo; const p = c && c.por_nivel && c.por_nivel[c.nivel]; return p && p.custodia_60 * 100; }, v => v.toFixed(0) + " %", "#f5a623"],
    ["vista", "Tiempo con el objetivo a la vista (%)", m => m.adv && m.adv.vista * 100, v => v.toFixed(0) + " %", "#9fc5e8"],
    ["perdidas", "Pérdidas del objetivo por partida", m => m.adv && m.adv.perdidas, v => v.toFixed(1), "#e5484d"],
    ["entropia", "Entropía de la política (cuánto duda)", m => m.dron && m.dron.entropia, v => v.toFixed(2), "#c9a0ff"],
  ];

  function armar() {
    $("ent").innerHTML = `<div class="ent-cab"><select id="entCorrida"></select><span id="entEstado" class="est"></span><span class="ent-sp"></span>
      <button id="entVer" title="Abre en el mapa táctico una partida guardada de la política entrenada">Ver partida de la política</button></div>
      <div class="ent-barra"><div class="ent-prog"><u id="entProg"></u></div><div id="entTexto"></div></div>
      <div id="entRej">${SERIES.map(s => `<div class="ent-g"><label>${s[1]} <b id="ev_${s[0]}"></b></label><canvas id="ec_${s[0]}"></canvas></div>`).join("")}</div>
      <div id="entPie"></div>`;
    $("entCorrida").onchange = ev => { E.carpeta = ev.target.value; E.metricas = []; cargar(true); };
    $("entVer").onclick = async () => {
      if (!E.carpeta) return;
      try { await cargarRep(`${E.carpeta}/replay_v17.json`); S.rep.url = "entrenamiento"; ponerPanel("mapa"); aviso("Partida de la política (" + E.carpeta + ")"); }
      catch (e) { aviso("Esa corrida no guardó partida de ejemplo", true); }
    };
  }

  async function lista() {
    try { E.corridas = await (await fetch("/corridas.json", { cache: "no-store" })).json(); } catch (e) { E.corridas = []; }
    const sel = $("entCorrida"); if (!sel) return;
    if (!E.carpeta && E.corridas.length) E.carpeta = (E.corridas.find(c => c.vivo) || E.corridas[0]).carpeta;
    sel.innerHTML = E.corridas.map(c => `<option value="${c.carpeta}" ${c.carpeta === E.carpeta ? "selected" : ""}>${c.carpeta.replace("salida_", "")} ${c.vivo ? "· entrenando ahora" : ""}</option>`).join("") || '<option>sin corridas</option>';
  }

  async function cargar(forzar) {
    if (!E.carpeta || E.ocupado) return; E.ocupado = true;
    try {
      E.estado = await (await fetch(`${E.carpeta}/estado.json`, { cache: "no-store" })).json();
      const corr = E.corridas.find(c => c.carpeta === E.carpeta);
      if (forzar || !E.metricas.length || (corr && corr.vivo)) E.metricas = await (await fetch(`${E.carpeta}/metricas.json`, { cache: "no-store" })).json();
    } catch (e) { E.estado = null; }
    E.ocupado = false; pintar();
  }

  function suave(v, k = 9) { return v.map((_, i) => { let s = 0, n = 0; for (let j = Math.max(0, i - k); j <= i; j++) if (v[j] != null && isFinite(v[j])) { s += v[j]; n++; } return n ? s / n : null; }); }

  function curva(s) {
    const cv = $("ec_" + s[0]); if (!cv) return; const [g, W, H] = ajustar(cv), xs = [], ys = [];
    E.metricas.forEach(m => { const y = s[2](m); if (y != null && isFinite(y)) { xs.push(m.pasos / 1e6); ys.push(y); } });
    if (ys.length < 2) { texto(g, "sin datos todavía", W / 2, H / 2, "center", "#6a747d", 13, 500, false); return; }
    const ys2 = suave(ys), mn = Math.min(...ys2), mx = Math.max(...ys2), rg = Math.max(mx - mn, 1e-9), x0 = xs[0], x1 = xs[xs.length - 1], px = 34, py = 8, w = W - px - 8, h = H - py - 20;
    g.strokeStyle = "#2a3036"; g.lineWidth = 1; g.fillStyle = "#6a747d"; g.font = "11px 'IBM Plex Mono', monospace"; g.textAlign = "right";
    for (let k = 0; k <= 3; k++) { const y = py + h - h * k / 3; g.beginPath(); g.moveTo(px, y); g.lineTo(px + w, y); g.stroke(); g.fillText(s[3](mn + rg * k / 3).replace(" %", ""), px - 4, y + 4); }
    g.textAlign = "center"; for (let k = 0; k <= 4; k++) { const x = px + w * k / 4; g.fillText((x0 + (x1 - x0) * k / 4).toFixed(1) + " M", x, H - 5); }
    g.strokeStyle = s[4] + "55"; g.lineWidth = 1; g.beginPath(); ys.forEach((v, i) => { const x = px + (xs[i] - x0) / Math.max(x1 - x0, 1e-9) * w, y = py + h - (v - mn) / rg * h; i ? g.lineTo(x, Math.max(py, Math.min(py + h, y))) : g.moveTo(x, y); }); g.stroke();
    g.strokeStyle = s[4]; g.lineWidth = 2.2; g.beginPath(); ys2.forEach((v, i) => { const x = px + (xs[i] - x0) / Math.max(x1 - x0, 1e-9) * w, y = py + h - (v - mn) / rg * h; i ? g.lineTo(x, y) : g.moveTo(x, y); }); g.stroke();
    $("ev_" + s[0]).textContent = s[3](ys2[ys2.length - 1]);
  }

  function pintar() {
    if (!E.visible) return; const e = E.estado;
    if (!e) { $("entTexto").textContent = "Sin datos del entrenamiento (¿está corriendo? ¿carpeta salida_v17_*?)"; return; }
    const corr = E.corridas.find(c => c.carpeta === E.carpeta), vivo = corr && corr.vivo, pct = Math.min(100, e.pasos / (e.objetivo || 1) * 100);
    const resta = e.pasos_s ? Math.max(0, (e.objetivo - e.pasos) / e.pasos_s) : 0, hh = s => `${Math.floor(s / 3600)} h ${String(Math.floor(s % 3600 / 60)).padStart(2, "0")} min`;
    $("entEstado").textContent = vivo ? "ENTRENANDO" : "TERMINADO"; $("entEstado").className = "est " + (vivo ? "ok" : "");
    $("entProg").style.width = pct + "%";
    $("entTexto").innerHTML = `<b>${(e.pasos / 1e6).toFixed(1)} M</b> de ${(e.objetivo / 1e6).toFixed(0)} M pasos · <b>${pct.toFixed(1)} %</b> · ${e.pasos_s || "–"} pasos/s · llevado ${hh(e.seg)}${vivo ? ` · faltan ≈ ${hh(resta)}` : ""} · ${e.version || ""} · nivel ${e.curriculo ? e.curriculo.nivel + " · " + e.curriculo.nombre : ""}`;
    SERIES.forEach(curva);
    const c = e.competencia;
    $("entPie").innerHTML = `Dron gana <b>${c ? (c.dron * 100).toFixed(0) : "–"} %</b> de las partidas decisivas · ladrón <b>${c ? (c.ladron * 100).toFixed(0) : "–"} %</b> · éxito del nivel <b>${e.curriculo && e.curriculo.exito != null ? (e.curriculo.exito * 100).toFixed(0) + " %" : "–"}</b> · la política entrena en el procesador (no usa la tarjeta gráfica); esta pestaña solo lee archivos.`;
  }

  async function mostrar(v) {
    E.visible = v; const d = $("ent"); if (d) d.style.visibility = v ? "visible" : "hidden";
    if (!v) return; if (!$("entCorrida")) armar(); await lista(); await cargar(true);
  }
  setInterval(() => { if (E.visible) { lista().then(() => cargar(false)); } }, 15000);
  addEventListener("resize", () => pintar());
  return { mostrar };
})();
