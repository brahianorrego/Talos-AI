// Paneles como ventanas (D-065): cada panel del visor se mueve arrastrando su título, cambia de tamaño con la esquina de
// abajo a la derecha, se minimiza (–), se maximiza (□) y se cierra (×); se vuelve a abrir desde "Paneles ▾". La
// distribución se guarda en el navegador. Vistas: "Solo 3D", "Solo lo que ve el dron" y "Todo" (teclas 1, 2 y 3).
// Las cámaras se dibujan donde esté su recuadro en cada cuadro, así que siguen a la ventana sin más cambios.
"use strict";
(() => {
  const CLAVE = "estacion-ventanas-v1";
  const VENTANAS = [            // [id, título para el menú y para las que no traen cabecera]
    ["p-tel", "Telemetría del vehículo"], ["p-fsm", "Búsqueda · estados"], ["p-slam", "Mapa SLAM · LiDAR"], ["p-obj", "Objetivo · tracker"],
    ["p-dec", "Lógica de decisión"], ["p-arb", "Árbitro de seguridad"], ["fpv", "Cámara del dron · YOLO"], ["rc", "Entrada de control"],
    ["monitor", "Telemetría de entrenamiento"], ["duelo", "Dominio táctico"], ["estado-linea", "Estado"], ["log", "Bitácora"],
    ["reproductor", "Reproductor"],
  ];
  const $ = id => document.getElementById(id);
  let guardado = {};
  try { guardado = JSON.parse(localStorage.getItem(CLAVE) || "{}"); } catch (e) {}
  const guardar = () => { try { localStorage.setItem(CLAVE, JSON.stringify(guardado)); } catch (e) {} };
  let zTope = 10;
  const avisarTamano = () => dispatchEvent(new Event("resize"));      // osciloscopios y lienzos se ajustan al nuevo tamaño

  function limitarAPantalla(el) {
    const r = el.getBoundingClientRect();
    el.style.left = Math.max(0, Math.min(r.left, innerWidth - 80)) + "px";
    el.style.top = Math.max(44, Math.min(r.top, innerHeight - 30)) + "px";
  }

  function hacerVentana(id, titulo, r, inicial) {
    let el = $(id);
    if (!el) return;
    const g = guardado[id] || inicial;
    let cab = el.querySelector(":scope > .cab");
    if (!cab) {                       // sin cabecera (bitácora, estado, duelo, reproductor): se envuelve en una ventana nueva
      const w = document.createElement("section");
      cab = document.createElement("div"); cab.className = "cab-v"; cab.innerHTML = `<span class="t">${titulo}</span>`;
      el.classList.remove("panel", "ui"); el.classList.add("cuerpo-v");
      el.before(w); w.append(cab, el);
      el = w;
    }
    el.dataset.v = id;
    document.body.appendChild(el);                                       // sale de su columna: se posiciona sola
    el.classList.add("ventana", "panel");
    el.style.left = (g.x ?? r.left) + "px";
    el.style.top = (g.y ?? r.top) + "px";
    el.style.width = (g.w ?? r.width) + "px";
    el.style.right = el.style.bottom = "auto";
    if (g.h) { el.style.height = g.h + "px"; el.classList.add("con-alto"); }
    el.classList.toggle("plegado", !!g.min);
    el.classList.toggle("max", !!g.max);
    el.classList.toggle("cerrada", !!g.cerrada);
    const ctl = document.createElement("div");
    ctl.className = "ctl-v";
    ctl.innerHTML = '<button class="min" title="Minimizar">–</button><button class="maxi" title="Maximizar">□</button><button class="cerrar" title="Cerrar (se vuelve a abrir en Paneles ▾)">×</button>';
    cab.appendChild(ctl);
    const agarre = document.createElement("div"); agarre.className = "agarre"; agarre.title = "Cambiar de tamaño"; el.appendChild(agarre);
    const anotar = () => {
      const q = el.getBoundingClientRect();
      guardado[id] = { ...guardado[id], x: Math.round(q.left), y: Math.round(q.top), w: Math.round(q.width),
                       h: el.classList.contains("con-alto") ? Math.round(q.height) : undefined };
      guardar();
    };
    ctl.querySelector(".min").onclick = ev => { ev.stopPropagation(); el.classList.toggle("plegado"); guardado[id] = { ...guardado[id], min: el.classList.contains("plegado") }; guardar(); avisarTamano(); };
    ctl.querySelector(".maxi").onclick = ev => { ev.stopPropagation(); el.classList.toggle("max"); guardado[id] = { ...guardado[id], max: el.classList.contains("max") }; guardar(); avisarTamano(); };
    ctl.querySelector(".cerrar").onclick = ev => { ev.stopPropagation(); ponerAbierta(id, false); };
    el.addEventListener("pointerdown", () => { el.style.zIndex = ++zTope; document.querySelectorAll(".ventana.enfocada").forEach(v => v.classList.remove("enfocada")); el.classList.add("enfocada"); });
    // mover: arrastrando la cabecera (no sus botones ni listas)
    cab.addEventListener("pointerdown", ev => {
      if (ev.target.closest("button, select, input, a") || el.classList.contains("max")) return;
      const x0 = ev.clientX - el.offsetLeft, y0 = ev.clientY - el.offsetTop;
      cab.setPointerCapture(ev.pointerId);
      const mover = e => { el.style.left = (e.clientX - x0) + "px"; el.style.top = Math.max(44, e.clientY - y0) + "px"; };
      const soltar = () => { cab.removeEventListener("pointermove", mover); limitarAPantalla(el); anotar(); };
      cab.addEventListener("pointermove", mover);
      cab.addEventListener("pointerup", soltar, { once: true });
    });
    // cambiar de tamaño: la esquina de abajo a la derecha
    agarre.addEventListener("pointerdown", ev => {
      ev.stopPropagation();
      const w0 = el.offsetWidth, h0 = el.offsetHeight, x0 = ev.clientX, y0 = ev.clientY;
      agarre.setPointerCapture(ev.pointerId);
      el.classList.add("con-alto");
      const cambiar = e => { el.style.width = Math.max(180, w0 + e.clientX - x0) + "px"; el.style.height = Math.max(60, h0 + e.clientY - y0) + "px"; };
      const soltar = () => { agarre.removeEventListener("pointermove", cambiar); anotar(); avisarTamano(); };
      agarre.addEventListener("pointermove", cambiar);
      agarre.addEventListener("pointerup", soltar, { once: true });
    });
    if (!g.x && g.x !== 0) limitarAPantalla(el);
  }

  function ponerAbierta(id, abierta) {
    const el = document.querySelector(`[data-v="${id}"]`);
    if (!el) return;
    el.classList.toggle("cerrada", !abierta);
    guardado[id] = { ...guardado[id], cerrada: !abierta };
    guardar();
    llenarMenu();
    avisarTamano();
  }

  function llenarMenu() {
    const lista = $("lista-paneles");
    const v = id => document.querySelector(`[data-v="${id}"]`);
    lista.innerHTML = VENTANAS.filter(([id]) => v(id)).map(([id, t]) =>
      `<label><input type="checkbox" data-id="${id}" ${v(id).classList.contains("cerrada") ? "" : "checked"}> ${t}</label>`).join("")
      + '<hr><button class="btn" id="b-restablecer" title="Vuelve a la distribución inicial de la estación">Restablecer distribución</button>';
    lista.querySelectorAll("input").forEach(c => c.onchange = () => ponerAbierta(c.dataset.id, c.checked));
    $("b-restablecer").onclick = () => { try { localStorage.removeItem(CLAVE); localStorage.removeItem(CLAVE + "-vista"); } catch (e) {} location.reload(); };
  }

  function ponerVista(v) {
    document.body.classList.toggle("vista-3d", v === "3d");
    document.body.classList.toggle("vista-dron", v === "dron");
    document.querySelectorAll("[data-vista]").forEach(b => b.classList.toggle("activo", b.dataset.vista === v));
    try { localStorage.setItem(CLAVE + "-vista", v); } catch (e) {}
    avisarTamano();
  }

  // distribución inicial: la del visor clásico; en cada columna, los paneles que no caben en la pantalla arrancan minimizados
  function distribucionInicial(rects) {
    const ini = {};
    const xDer = rects.rc ? Math.round(rects.rc.left) : innerWidth - 374;
    [["p-tel", "p-fsm", "p-obj", "p-arb", "p-dec"], ["fpv", "rc", "p-slam"]].forEach(col => {
      let y = 52;
      col.forEach(id => {
        const r = rects[id]; if (!r) return;
        const h = id === "fpv" ? Math.round(r.width * 3 / 4 + 46) : r.height;    // la cámara necesita alto fijo (4:3 + título)
        const cabe = y + h <= innerHeight - 60;
        ini[id] = { x: col[0] === "fpv" ? xDer : Math.round(r.left), y, w: Math.round(r.width), min: !cabe, h: id === "fpv" ? h : undefined };
        y += (cabe ? h : 34) + 8;
      });
    });
    if (rects.monitor) ini.monitor = { x: xDer, w: Math.round(rects.monitor.width), min: true };   // como en el clásico: plegado
    return ini;
  }

  function iniciar() {
    const rects = Object.fromEntries(VENTANAS.map(([id]) => [id, $(id) && $(id).getBoundingClientRect()]));   // todo se mide antes de mover
    const ini = distribucionInicial(rects);
    const primeraVez = !Object.keys(guardado).length;
    VENTANAS.forEach(([id, t]) => hacerVentana(id, t, rects[id], ini[id] || {}));
    if (primeraVez) {                 // la franja de abajo (estado, bitácora, reproductor) se apila desde abajo con su tamaño real
      let y = innerHeight - 10;
      ["reproductor", "log", "estado-linea"].forEach(id => {
        const v = document.querySelector(`[data-v="${id}"]`); if (!v) return;
        y -= v.offsetHeight; v.style.top = y + "px"; y -= 6;
      });
      const mon = document.querySelector('[data-v="monitor"]');
      if (mon) mon.style.top = (innerHeight - 10 - mon.offsetHeight) + "px";
    }
    llenarMenu();
    $("b-paneles").onclick = ev => { ev.stopPropagation(); $("lista-paneles").classList.toggle("ver"); };
    addEventListener("pointerdown", ev => { if (!ev.target.closest(".menu-paneles")) $("lista-paneles").classList.remove("ver"); });
    document.querySelectorAll("[data-vista]").forEach(b => b.onclick = () => ponerVista(b.dataset.vista));
    addEventListener("keydown", ev => {
      if (/SELECT|INPUT|TEXTAREA/.test(ev.target.tagName)) return;
      const v = { Digit1: "3d", Digit2: "dron", Digit3: "todo" }[ev.code];
      if (v) ponerVista(v);
    });
    let v = "todo";
    try { v = localStorage.getItem(CLAVE + "-vista") || "todo"; } catch (e) {}
    ponerVista(v);
  }
  // los paneles entran con una animación de 0.45 s: se toma su posición cuando ya están quietos
  addEventListener("load", () => setTimeout(iniciar, 700));
})();
