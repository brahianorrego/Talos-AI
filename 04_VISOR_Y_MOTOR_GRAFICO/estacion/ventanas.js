// Paneles como ventanas (D-065 y pedido de Brahian del 17-oct): cada panel se mueve arrastrando su título, cambia de
// tamaño con la esquina de abajo a la derecha, se minimiza (– o doble clic en el título), se maximiza (□) y se cierra (×);
// se vuelve a abrir desde "Paneles ▾". La distribución se guarda en el navegador.
// Vista principal: ocupa el centro de la pantalla y se intercambia con el botón ⇱ de la cámara del dron, del mapa SLAM o
// de la vista 3D (por defecto, lo que ve el dron). index.html lee window.PRINCIPAL para saber dónde dibujar el 3D.
// Vistas: "Solo 3D", "Solo lo que ve el dron" y "Todo" (teclas 1, 2 y 3).
"use strict";
(() => {
  const CLAVE = "estacion-ventanas-v2";
  const VENTANAS = [            // [id, título para el menú y para las que no traen cabecera]
    ["p-3d", "Vista 3D · simulación"], ["fpv", "Cámara del dron · YOLO"], ["rc", "Entrada de control"], ["p-slam", "Mapa SLAM · LiDAR"],
    ["p-cus", "Custodia del ladrón"], ["p-tel", "Telemetría del vehículo"], ["p-fsm", "Búsqueda · estados"], ["p-obj", "Objetivo · tracker"],
    ["p-arb", "Árbitro de seguridad"], ["p-dec", "Lógica de decisión"], ["monitor", "Telemetría de entrenamiento"],
    ["estado-linea", "Estado"], ["log", "Bitácora"], ["reproductor", "Reproductor"],
  ];
  const INTERCAMBIABLES = { fpv: "dron", "p-slam": "mapa", "p-3d": "3d" };      // ventana -> nombre de la vista principal
  const VENTANA_DE = { dron: "fpv", mapa: "p-slam", "3d": "p-3d" };
  const $ = id => document.getElementById(id);
  const ventana = id => document.querySelector(`[data-v="${id}"]`);
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

  function hacerVentana(id, titulo, ini) {
    let el = $(id);
    if (!el) return;
    const g = guardado[id] || ini;
    let cab = el.querySelector(":scope > .cab");
    if (!cab) {                       // sin cabecera (bitácora, estado, reproductor): se envuelve en una ventana nueva
      const w = document.createElement("section");
      cab = document.createElement("div"); cab.className = "cab-v"; cab.innerHTML = `<span class="t">${titulo}</span>`;
      el.classList.remove("panel", "ui"); el.classList.add("cuerpo-v");
      el.before(w); w.append(cab, el);
      el = w;
    }
    el.dataset.v = id;
    document.body.appendChild(el);                                       // sale de su columna: se posiciona sola
    el.classList.add("ventana", "panel");
    el.style.right = el.style.bottom = "auto";
    if (g.x !== undefined) { el.style.left = g.x + "px"; el.style.top = g.y + "px"; }
    if (g.w) el.style.width = g.w + "px";
    if (g.h) { el.style.height = g.h + "px"; el.classList.add("con-alto"); }
    el.classList.toggle("plegado", !!g.min);
    el.classList.toggle("max", !!g.max);
    el.classList.toggle("cerrada", !!g.cerrada);
    const ctl = document.createElement("div");
    ctl.className = "ctl-v";
    ctl.innerHTML = (INTERCAMBIABLES[id] ? '<button class="poner" title="Poner en la pantalla principal (intercambia)">⇱</button>' : "")
      + '<button class="min" title="Minimizar (o doble clic en el título)">–</button><button class="maxi" title="Maximizar">□</button>'
      + '<button class="cerrar" title="Cerrar (se vuelve a abrir en Paneles ▾)">×</button>';
    cab.appendChild(ctl);
    const agarre = document.createElement("div"); agarre.className = "agarre"; agarre.title = "Cambiar de tamaño"; el.appendChild(agarre);
    const anotar = () => {
      if (el.classList.contains("principal")) return;                   // la principal no cambia su lugar guardado
      const q = el.getBoundingClientRect();
      guardado[id] = { ...guardado[id], x: Math.round(q.left), y: Math.round(q.top), w: Math.round(q.width),
                       h: el.classList.contains("con-alto") ? Math.round(q.height) : undefined };
      guardar();
    };
    const minimizar = () => { el.classList.toggle("plegado"); guardado[id] = { ...guardado[id], min: el.classList.contains("plegado") }; guardar(); avisarTamano(); };
    ctl.querySelector(".min").onclick = ev => { ev.stopPropagation(); minimizar(); };
    cab.addEventListener("dblclick", ev => { if (!ev.target.closest("button, select") && !el.classList.contains("principal")) minimizar(); });
    ctl.querySelector(".maxi").onclick = ev => { ev.stopPropagation(); el.classList.toggle("max"); guardado[id] = { ...guardado[id], max: el.classList.contains("max") }; guardar(); avisarTamano(); };
    ctl.querySelector(".cerrar").onclick = ev => { ev.stopPropagation(); ponerAbierta(id, false); };
    const poner = ctl.querySelector(".poner");
    if (poner) poner.onclick = ev => { ev.stopPropagation(); ponerPrincipal(INTERCAMBIABLES[id]); };
    el.addEventListener("pointerdown", () => {
      if (el.classList.contains("principal")) return;
      el.style.zIndex = ++zTope; document.querySelectorAll(".ventana.enfocada").forEach(v => v.classList.remove("enfocada")); el.classList.add("enfocada");
    });
    // mover: arrastrando la cabecera (no sus botones ni listas)
    cab.addEventListener("pointerdown", ev => {
      if (ev.target.closest("button, select, input, a") || el.classList.contains("max") || el.classList.contains("principal")) return;
      const x0 = ev.clientX - el.offsetLeft, y0 = ev.clientY - el.offsetTop;
      cab.setPointerCapture(ev.pointerId);
      const mover = e => { el.style.left = (e.clientX - x0) + "px"; el.style.top = Math.max(44, e.clientY - y0) + "px"; };
      const soltar = () => { cab.removeEventListener("pointermove", mover); limitarAPantalla(el); anotar(); ajustarPrincipal(); };
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
      const soltar = () => { agarre.removeEventListener("pointermove", cambiar); anotar(); ajustarPrincipal(); avisarTamano(); };
      agarre.addEventListener("pointermove", cambiar);
      agarre.addEventListener("pointerup", soltar, { once: true });
    });
  }

  // ------------------------------------------------------------------------------------------------ vista principal
  // la zona del centro: entre las columnas y por encima de la franja de abajo (o casi toda la pantalla en "Solo ...")
  function zonaPrincipal(propia) {
    const solo = document.body.classList.contains("vista-3d") || document.body.classList.contains("vista-dron");
    const rep = ventana("reproductor");
    if (solo) return { x: 10, y: 52, w: innerWidth - 20, h: (rep ? rep.getBoundingClientRect().top : innerHeight) - 60 };
    const abierta = v => v && v !== propia && !v.classList.contains("cerrada") && !v.classList.contains("principal");
    const izq = ["p-3d", "rc"].map(ventana).filter(abierta).map(v => v.getBoundingClientRect()).filter(r => r.left < innerWidth / 2);
    const der = ["p-cus", "p-tel", "p-fsm", "p-obj", "p-arb", "p-dec", "monitor"].map(ventana).filter(abierta).map(v => v.getBoundingClientRect()).filter(r => r.left > innerWidth / 2);
    const x0 = izq.length ? Math.max(...izq.map(r => r.right)) + 10 : 10;
    const x1 = der.length ? Math.min(...der.map(r => r.left)) - 10 : innerWidth - 10;
    const abajo = ["estado-linea", "log", "reproductor"].map(ventana).filter(abierta).map(v => v.getBoundingClientRect().top);
    const y1 = (abajo.length ? Math.min(...abajo) : innerHeight) - 8;
    return { x: x0, y: 52, w: Math.max(200, x1 - x0), h: Math.max(150, y1 - 52) };
  }
  function ajustarPrincipal() {
    const id = VENTANA_DE[window.PRINCIPAL];
    document.querySelectorAll(".ventana.principal").forEach(v => { if (v.dataset.v !== id) v.classList.remove("principal"); });
    const el = ventana(id);
    if (!el || window.PRINCIPAL === "3d") return;                      // el 3D principal no necesita marco: va de fondo
    const z = zonaPrincipal(el);
    el.classList.add("principal");
    Object.assign(el.style, { left: z.x + "px", top: z.y + "px", width: z.w + "px", height: z.h + "px" });
  }
  // intercambio: la que deja la pantalla principal ocupa el recuadro de la que entra
  function ponerPrincipal(nombre) {
    const anterior = ventana(VENTANA_DE[window.PRINCIPAL]), nueva = ventana(VENTANA_DE[nombre]);
    if (anterior && window.PRINCIPAL !== nombre) {
      anterior.classList.remove("principal");
      const g = guardado[nueva.dataset.v] || guardado[anterior.dataset.v] || {};
      Object.assign(anterior.style, { left: g.x + "px", top: g.y + "px", width: g.w + "px", height: g.h ? g.h + "px" : "" });
      anterior.classList.toggle("con-alto", !!g.h);
      anterior.classList.remove("plegado", "cerrada");
      guardado[anterior.dataset.v] = { ...guardado[anterior.dataset.v], x: g.x, y: g.y, w: g.w, h: g.h, min: false, cerrada: false };
      guardar();
    }
    window.PRINCIPAL = nombre;
    document.body.dataset.principal = nombre;
    try { localStorage.setItem(CLAVE + "-principal", nombre); } catch (e) {}
    ajustarPrincipal();
    avisarTamano();
  }

  function ponerAbierta(id, abierta) {
    const el = ventana(id);
    if (!el) return;
    el.classList.toggle("cerrada", !abierta);
    guardado[id] = { ...guardado[id], cerrada: !abierta };
    guardar();
    llenarMenu();
    ajustarPrincipal();
    avisarTamano();
  }

  function llenarMenu() {
    const lista = $("lista-paneles");
    lista.innerHTML = VENTANAS.filter(([id]) => ventana(id)).map(([id, t]) =>
      `<label><input type="checkbox" data-id="${id}" ${ventana(id).classList.contains("cerrada") ? "" : "checked"}> ${t}</label>`).join("")
      + '<hr><button class="btn" id="b-restablecer" title="Vuelve a la distribución inicial de la estación">Restablecer distribución</button>';
    lista.querySelectorAll("input").forEach(c => c.onchange = () => ponerAbierta(c.dataset.id, c.checked));
    $("b-restablecer").onclick = () => { try { [CLAVE, CLAVE + "-vista", CLAVE + "-principal"].forEach(k => localStorage.removeItem(k)); } catch (e) {} location.reload(); };
  }

  function ponerVista(v) {
    document.body.classList.toggle("vista-3d", v === "3d");
    document.body.classList.toggle("vista-dron", v === "dron");
    document.querySelectorAll("[data-vista]").forEach(b => b.classList.toggle("activo", b.dataset.vista === v));
    try { localStorage.setItem(CLAVE + "-vista", v); } catch (e) {}
    if (v === "3d") ponerPrincipal("3d");
    else if (v === "dron") ponerPrincipal("dron");
    else ajustarPrincipal();
    avisarTamano();
  }

  // ------------------------------------------------------------------------------------------------ distribución inicial
  // izquierda: vista 3D, control y mapa SLAM (la cámara del dron va en el centro); derecha: custodia, telemetría, estados,
  // objetivo, árbitro y decisión; abajo: estado, bitácora y reproductor. Lo que no cabe arranca minimizado.
  function distribucionInicial(alturas) {
    const ini = {}, wI = 364, wD = 300, xD = innerWidth - wD - 10;
    const columna = (ids, x, w) => {
      let y = 52;
      ids.forEach(id => {
        const h = id === "p-3d" ? Math.round(w * 9 / 16 + 48) : alturas[id] || 120;
        const cabe = y + h <= innerHeight - 12;
        ini[id] = { x, y, w, min: !cabe, h: id === "p-3d" ? h : undefined };
        y += (cabe ? h : 34) + 8;
      });
    };
    columna(["p-3d", "rc"], 10, wI);
    columna(["p-cus", "p-tel", "p-fsm", "p-obj", "p-arb", "p-dec"], xD, wD);
    ini.monitor = { x: xD, w: wD, min: true };
    ini.fpv = { x: 10 + wI + 10, y: 52, w: 480, h: 406 };                // su lugar cuando no es la principal
    const xA = 10 + wI + 10, wA = xD - 10 - xA;
    ["estado-linea", "log", "reproductor"].forEach(id => { ini[id] = { x: xA, w: wA }; });
    return ini;
  }

  function iniciar() {
    const alturas = Object.fromEntries(VENTANAS.map(([id]) => [id, $(id) ? $(id).getBoundingClientRect().height : 0]));
    const primeraVez = !Object.keys(guardado).length;
    const ini = distribucionInicial(alturas);
    VENTANAS.forEach(([id, t]) => hacerVentana(id, t, ini[id] || {}));
    if (primeraVez) {                 // la franja de abajo se apila desde abajo con su tamaño real; el monitor, abajo a la derecha
      let y = innerHeight - 10;
      ["reproductor", "log", "estado-linea"].forEach(id => {
        const v = ventana(id); if (!v) return;
        y -= v.offsetHeight; v.style.top = y + "px"; y -= 6;
        const q = v.getBoundingClientRect(); ini[id] = { ...ini[id], x: Math.round(q.left), y: Math.round(q.top), w: Math.round(q.width) };
      });
      const est = ventana("estado-linea"), slam = ventana("p-slam");
      if (est && slam) {              // el mapa SLAM, como recuadro sobre la vista del dron (abajo a la izquierda)
        ini["p-slam"] = { x: 10 + 364 + 22, y: Math.round(est.getBoundingClientRect().top - 8 - 330 - 12), w: 300, h: 330 };
        Object.assign(slam.style, { left: ini["p-slam"].x + "px", top: ini["p-slam"].y + "px", width: "300px", height: "330px" });
        slam.classList.add("con-alto");
      }
      const mon = ventana("monitor");
      if (mon) { mon.style.top = (innerHeight - 10 - mon.offsetHeight) + "px"; ini.monitor = { ...ini.monitor, y: innerHeight - 10 - mon.offsetHeight }; }
      VENTANAS.forEach(([id]) => { guardado[id] = ini[id] || {}; });
      guardar();
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
    addEventListener("resize", () => requestAnimationFrame(ajustarPrincipal));
    let p = "dron", v = "todo";
    try { p = localStorage.getItem(CLAVE + "-principal") || "dron"; v = localStorage.getItem(CLAVE + "-vista") || "todo"; } catch (e) {}
    window.PRINCIPAL = p; document.body.dataset.principal = p;
    ponerVista(v);
    ajustarPrincipal();
  }
  window.PRINCIPAL = "dron";
  // los paneles entran con una animación de 0.45 s: se toma su tamaño cuando ya están quietos
  addEventListener("load", () => setTimeout(iniciar, 700));
})();
