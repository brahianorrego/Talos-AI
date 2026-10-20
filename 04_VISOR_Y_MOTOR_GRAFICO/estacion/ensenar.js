// Modo ENSEÑAR (tecla E): Brahian dirige al dron sobre el mapa visto desde arriba y se graba la demostración (en_vivo.py, 03_SIMULACION_RL/demos_brahian/).
//   · Clic en el mapa = punto de paso; el círculo que lo rodea se arrastra para girar la flecha (el rumbo al llegar). Se encadenan varios puntos.
//   · Cada punto lleva pan (±90°) y tilt (−45° a +15°) de la cámara; "Ir" sigue los puntos, "Parar" detiene, "Borrar último" quita uno.
//   · "Manual": W/S adelante y atrás, A/D de lado, Q/E giran, flechas = pan y tilt (o un gamepad); la cámara CSI#1 se ve grande.
//   · "Grabar demostración" guarda la partida tal como la dirigió (puntos, rumbos, pan/tilt y el mundo en cada paso).
"use strict";
(() => {
  const URL = "http://127.0.0.1:8767";
  const $ = id => document.getElementById(id);
  const post = (ruta, datos) => fetch(URL + ruta, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(datos || {}) }).catch(() => {});

  const s = document.createElement("section");
  s.className = "panel"; s.id = "p-ens";
  s.innerHTML = `<div class="cab"><h3>Enseñar · dirija al dron</h3><span class="tag" id="ens-tag" style="color:var(--tenue)">–</span></div>
    <div class="cuerpo" id="ens-cuerpo">
      <div class="ens-barra">
        <button class="btn activo" data-sub="mapa" title="Clic en el mapa: punto de paso">Puntos</button><button class="btn" data-sub="manual" title="W S A D, Q E, flechas">Manual</button>
        <span class="ens-sep"></span>
        <button class="btn" id="ens-ir">Ir</button><button class="btn" id="ens-parar">Parar</button><button class="btn" id="ens-ultimo">Borrar último</button><button class="btn" id="ens-todos">Borrar todos</button>
        <span class="ens-sep"></span>
        <button class="btn" id="ens-grabar">● Grabar demostración</button><button class="btn" id="ens-reset" title="Empieza otra partida">Otra partida</button>
      </div>
      <div class="ens-punto" id="ens-punto">Haga clic en el mapa para poner el primer punto.</div>
      <canvas id="ens-lienzo"></canvas>
      <div class="ens-ayuda" id="ens-ayuda"></div>
    </div>`;
  document.body.appendChild(s);

  const cv = $("ens-lienzo"), g = cv.getContext("2d");
  const L = [];                                   // puntos de paso del lado de la estación (x, y, yaw, pan, tilt)
  let sel = -1, arrastre = null, sub = "mapa", conectado = false, ultimoE = null, cmdManual = { vx: 0, vy: 0, wz: 0, pan: 0, tilt: 0 };
  window.ENSENAR_MANUAL = false;
  const M = 28;                                   // semi-lado del mapa en metros (la arena mide 25)
  const dim = () => { const r = cv.getBoundingClientRect(); return { w: r.width, h: r.height, k: Math.min(r.width, r.height) / (2 * M) }; };
  const aPix = (x, y) => { const d = dim(); return [d.w / 2 + x * d.k, d.h / 2 - y * d.k]; };
  const aMundo = (px, py) => { const d = dim(); return [(px - d.w / 2) / d.k, (d.h / 2 - py) / d.k]; };
  const rad = 24;                                 // radio del círculo de giro, en píxeles

  const modoActivo = () => document.body.dataset.modo === "ens";
  const enviarPunto = p => post("/waypoint", { x: p.x, y: p.y, yaw: p.yaw, pan: p.pan, tilt: p.tilt });
  const reenviar = () => { post("/waypoint", { borrar: "todos" }).then(() => L.forEach(enviarPunto)); };   // tras mover o girar un punto se manda la lista de nuevo

  // ----------------------------------------------------------------------------------------------------------- dibujo
  function dibujar() {
    const r = cv.getBoundingClientRect(), dpr = Math.min(devicePixelRatio || 1, 2);
    if (r.width < 10) return;
    if (cv.width !== Math.round(r.width * dpr)) { cv.width = Math.round(r.width * dpr); cv.height = Math.round(r.height * dpr); }
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    const d = dim();
    g.fillStyle = "#0a1018"; g.fillRect(0, 0, d.w, d.h);
    g.strokeStyle = "rgba(120,150,180,.13)"; g.lineWidth = 1; g.font = "10px 'Roboto Mono', monospace"; g.fillStyle = "rgba(160,180,200,.5)";
    for (let m = -25; m <= 25; m += 5) { const [x0, y0] = aPix(m, -M), [x1, y1] = aPix(m, M); g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke(); const [a0, b0] = aPix(-M, m), [a1, b1] = aPix(M, m); g.beginPath(); g.moveTo(a0, b0); g.lineTo(a1, b1); g.stroke(); if (m) { g.fillText(m, aPix(m, 0)[0] + 2, aPix(m, 0)[1] + 11); g.fillText(m, aPix(0, m)[0] + 3, aPix(0, m)[1] - 2); } }
    const [ax, ay] = aPix(-25, 25); g.strokeStyle = "rgba(245,197,66,.55)"; g.setLineDash([6, 5]); g.strokeRect(ax, ay, 50 * d.k, 50 * d.k); g.setLineDash([]);   // geocerca
    const e = window.ESTADO_VISTA, pt = typeof partida !== "undefined" ? partida : null;
    if (pt && pt.paneles) {                                                  // los paneles (giran de una partida a otra)
      g.strokeStyle = "#cfd9e4"; g.lineWidth = Math.max(3, 0.05 * d.k * 3);
      pt.paneles.forEach(p => { const [x0, y0] = aPix(p[0], p[1]), [x1, y1] = aPix(p[2], p[3]); g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke(); });
    }
    if (e) {
      (e.pers || []).forEach(q => { const [x, y] = aPix(q.p[0], q.p[1]); g.beginPath(); g.arc(x, y, 7, 0, 7); g.fillStyle = q.rol === "ladron" ? "#ff4d4f" : "#8fa3b8"; g.fill(); g.fillStyle = "#e8eef5"; g.font = "11px Inter, sans-serif"; g.fillText(q.rol === "ladron" ? "ladrón" : "civil", x + 10, y + 4); });
    }
    // puntos de paso, unidos por la ruta
    g.lineWidth = 2;
    if (e && L.length) { g.strokeStyle = "rgba(45,183,255,.6)"; g.setLineDash([5, 4]); g.beginPath(); g.moveTo(...aPix(e.x, e.y)); L.forEach(p => g.lineTo(...aPix(p.x, p.y))); g.stroke(); g.setLineDash([]); }
    L.forEach((p, i) => {
      const [x, y] = aPix(p.x, p.y), hecho = ultimoE && i < ultimoE.i, activo = ultimoE && ultimoE.ir && i === ultimoE.i;
      const col = hecho ? "#33d17a" : activo ? "#f5c542" : "#2db7ff";
      g.strokeStyle = col; g.lineWidth = i === sel ? 2.5 : 1.5; g.beginPath(); g.arc(x, y, rad, 0, 7); g.stroke();           // círculo de giro
      const a = p.yaw * Math.PI / 180, tx = x + Math.cos(a) * rad, ty = y - Math.sin(a) * rad;
      g.beginPath(); g.moveTo(x, y); g.lineTo(tx, ty); g.stroke();
      g.fillStyle = col; g.beginPath(); g.arc(tx, ty, 5, 0, 7); g.fill();                                                    // agarradera del giro
      g.beginPath(); g.arc(x, y, 6, 0, 7); g.fill();
      g.fillStyle = "#06090d"; g.font = "bold 9px Inter, sans-serif"; g.fillText(i + 1, x - 2.5, y + 3.2);
      if (p.pan || p.tilt !== -5) { g.fillStyle = col; g.font = "10px 'Roboto Mono', monospace"; g.fillText(`pan ${p.pan | 0}° tilt ${p.tilt | 0}°`, x + rad + 4, y + 4); }
    });
    if (e) {                                                                 // el dron: flecha hacia su frente, y el cono de la cámara con el pan
      const [x, y] = aPix(e.x, e.y), psi = e.psi, pan = ((e.c && e.c.pan) || 0) * Math.PI / 180;
      g.fillStyle = "rgba(45,183,255,.12)"; g.beginPath(); g.moveTo(x, y); g.arc(x, y, 90, -(psi + pan) - 0.6, -(psi + pan) + 0.6); g.closePath(); g.fill();
      g.save(); g.translate(x, y); g.rotate(-psi); g.fillStyle = "#2db7ff"; g.strokeStyle = "#fff"; g.lineWidth = 1.5;
      g.beginPath(); g.moveTo(15, 0); g.lineTo(-10, 9); g.lineTo(-5, 0); g.lineTo(-10, -9); g.closePath(); g.fill(); g.stroke(); g.restore();
    }
  }

  // ----------------------------------------------------------------------------------------------------------- ratón
  function cercano(px, py) {                                                 // ¿el clic cayó sobre la agarradera o el círculo de algún punto?
    for (let i = L.length - 1; i >= 0; i--) {
      const [x, y] = aPix(L[i].x, L[i].y), a = L[i].yaw * Math.PI / 180, d = Math.hypot(px - x, py - y);
      if (Math.hypot(px - (x + Math.cos(a) * rad), py - (y - Math.sin(a) * rad)) < 11 || (d > rad - 6 && d < rad + 8)) return { i, tipo: "girar" };
      if (d < 12) return { i, tipo: "mover" };
    }
    return null;
  }
  const pos = ev => { const r = cv.getBoundingClientRect(); return [ev.clientX - r.left, ev.clientY - r.top]; };
  cv.addEventListener("mousedown", ev => {
    if (sub !== "mapa" || ev.button) return;
    const [px, py] = pos(ev), h = cercano(px, py);
    if (h) { sel = h.i; arrastre = h; mostrarPunto(); return; }
    const [x, y] = aMundo(px, py), e = window.ESTADO_VISTA, lim = 24;
    if (Math.abs(x) > lim || Math.abs(y) > lim) return;                                       // fuera de la geocerca no
    const ant = L.length ? L[L.length - 1] : (e ? { x: e.x, y: e.y } : { x: 0, y: 0 });
    const yaw = Math.round(Math.atan2(y - ant.y, x - ant.x) * 180 / Math.PI);
    L.push({ x, y, yaw, pan: 0, tilt: -5 }); sel = L.length - 1; arrastre = { i: sel, tipo: "girar", nuevo: true }; mostrarPunto();
  });
  addEventListener("mousemove", ev => {
    if (!arrastre) return;
    const [px, py] = pos(ev), p = L[arrastre.i], [x, y] = aPix(p.x, p.y);
    if (arrastre.tipo === "girar") { if (Math.hypot(px - x, py - y) > 6) p.yaw = Math.round(Math.atan2(-(py - y), px - x) * 180 / Math.PI); }
    else { const [mx, my] = aMundo(px, py); p.x = Math.max(-24, Math.min(24, mx)); p.y = Math.max(-24, Math.min(24, my)); }
    mostrarPunto();
  });
  addEventListener("mouseup", () => { if (arrastre) { arrastre = null; reenviar(); } });

  // ----------------------------------------------------------------------------------------------------------- punto escogido: pan y tilt
  function mostrarPunto() {
    const el = $("ens-punto");
    if (sel < 0 || !L[sel]) { el.textContent = L.length ? "Escoja un punto (clic sobre él) para darle pan y tilt." : "Haga clic en el mapa para poner el primer punto."; return; }
    const p = L[sel];
    el.innerHTML = `<b>Punto ${sel + 1}</b> · rumbo ${p.yaw}° · pan <input type="range" id="ens-pan" min="-90" max="90" step="5" value="${p.pan}"> <b id="ens-pan-v">${p.pan}°</b>
      · tilt <input type="range" id="ens-tilt" min="-45" max="15" step="5" value="${p.tilt}"> <b id="ens-tilt-v">${p.tilt}°</b>`;
    $("ens-pan").oninput = ev => { p.pan = +ev.target.value; $("ens-pan-v").textContent = p.pan + "°"; };
    $("ens-tilt").oninput = ev => { p.tilt = +ev.target.value; $("ens-tilt-v").textContent = p.tilt + "°"; };
    $("ens-pan").onchange = $("ens-tilt").onchange = reenviar;
  }

  // ----------------------------------------------------------------------------------------------------------- botones
  const fijarSub = x => {
    sub = x; window.ENSENAR_MANUAL = x === "manual";
    document.querySelectorAll("#p-ens [data-sub]").forEach(b => b.classList.toggle("activo", b.dataset.sub === x));
    document.body.classList.toggle("ens-manual", x === "manual");
    $("ens-ayuda").textContent = x === "manual" ? "W/S adelante y atrás · A/D de lado · Q/E giran · flechas: pan (← →) y tilt (↑ ↓) · también sirve un gamepad" : "Clic: punto de paso · arrastre el círculo para girar la flecha · clic sobre un punto: pan y tilt · \"Ir\" lo ejecuta";
    post("/modo", { modo: "ensenar", sub: x });
  };
  document.querySelectorAll("#p-ens [data-sub]").forEach(b => b.onclick = () => fijarSub(b.dataset.sub));
  $("ens-ir").onclick = () => { reenviar(); setTimeout(() => post("/waypoint", { ir: true }), 150); };
  $("ens-parar").onclick = () => post("/waypoint", { ir: false });
  $("ens-ultimo").onclick = () => { L.pop(); sel = L.length - 1; mostrarPunto(); post("/waypoint", { borrar: "ultimo" }); };
  $("ens-todos").onclick = () => { L.length = 0; sel = -1; mostrarPunto(); post("/waypoint", { borrar: "todos" }); };
  $("ens-grabar").onclick = () => post("/grabar", { on: !(ultimoE && ultimoE.graba) });
  $("ens-reset").onclick = () => { L.length = 0; sel = -1; mostrarPunto(); post("/reset"); };

  // ----------------------------------------------------------------------------------------------------------- manual (teclado y gamepad)
  const teclas = new Set();
  addEventListener("keydown", ev => { if (modoActivo() && sub === "manual" && !/SELECT|INPUT|TEXTAREA/.test(ev.target.tagName)) { teclas.add(ev.code); if (/^(Arrow)/.test(ev.code)) ev.preventDefault(); } });
  addEventListener("keyup", ev => teclas.delete(ev.code));
  const eje = (m, p) => (teclas.has(m) ? 1 : 0) - (teclas.has(p) ? 1 : 0);
  setInterval(() => {
    if (!modoActivo() || sub !== "manual") return;
    const gp = (navigator.getGamepads ? [...navigator.getGamepads()].find(x => x) : null), z = v => (Math.abs(v) < 0.15 ? 0 : v);
    cmdManual = {
      vx: eje("KeyW", "KeyS") || (gp ? -z(gp.axes[1]) : 0), vy: eje("KeyA", "KeyD") || (gp ? -z(gp.axes[0]) : 0), wz: eje("KeyQ", "KeyE") || (gp ? -z(gp.axes[2]) : 0),
      pan: eje("ArrowLeft", "ArrowRight") || (gp ? (gp.buttons[14] && gp.buttons[14].pressed ? 1 : 0) - (gp.buttons[15] && gp.buttons[15].pressed ? 1 : 0) : 0), tilt: eje("ArrowUp", "ArrowDown") || (gp ? -z(gp.axes[3] || 0) : 0),
    };
    post("/manual", cmdManual);
  }, 100);

  // ----------------------------------------------------------------------------------------------------------- vida del panel
  let anterior = false;
  setInterval(() => {
    const act = modoActivo();
    if (act && !anterior) {                                                  // entra al modo: se conecta al en vivo y le pide que el dron sea de Brahian
      const sl = $("selector");
      if (sl && sl.value !== "vivo") { sl.value = "vivo"; sl.dispatchEvent(new Event("change")); }
      fijarSub(sub);
    }
    if (!act && anterior) post("/modo", { modo: "auto" });
    anterior = act;
    if (!act) return;
    const e = window.ESTADO_VISTA;
    ultimoE = e && e.c && e.c.ens ? e.c.ens : ultimoE;
    conectado = !!(e && e.c && e.c.ens);
    const t = $("ens-tag");
    t.textContent = !conectado ? "sin en_vivo.py" : ultimoE.graba ? `● grabando (${ultimoE.n} pasos)` : ultimoE.demo ? "guardada: " + ultimoE.demo : "listo";
    t.style.color = !conectado ? "#ff4d4f" : ultimoE && ultimoE.graba ? "#ff4d4f" : "var(--suave)";
    $("ens-grabar").textContent = ultimoE && ultimoE.graba ? "■ Parar y guardar" : "● Grabar demostración";
    if (ultimoE && L.length === 0 && ultimoE.cola && ultimoE.cola.length === 0) sel = -1;
    if (!conectado) $("ens-punto").textContent = "Falta la simulación en vivo: abra ENSENAR.bat (o corra en_vivo.py).";
  }, 250);
  (function lazo() { if (modoActivo()) dibujar(); requestAnimationFrame(lazo); })();
})();
