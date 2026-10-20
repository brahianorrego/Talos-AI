// Modos de la estación (pedido de Brahian, 17-oct): en vez de ventanas sueltas que se pueden cerrar y desordenar, cinco
// pantallas ya organizadas que se eligen con los botones de arriba (o las teclas 1 a 5). Ningún panel se pierde: cada modo
// pone los que necesita en su lugar y guarda los demás. El modo elegido se recuerda.
//   Vista del dron  · la cámara USB con YOLO, la telemetría y el mapa SLAM encima; más las cámaras CSI (frontal y piso) y el LiDAR 360°,
//                     que se encienden y apagan con los botones de arriba o las teclas P, G y L (camaras.js)
//   Simulación 3D   · el mundo 3D a pantalla completa; "Ocultar paneles" deja solo la simulación
//   Mapa            · el mapa del LiDAR grande (rueda: acercar; arrastrar: mover; doble clic: centrar)
//   Ingeniería      · todo el análisis alrededor del 3D: estados, decisiones, árbitro, tracker, entrenamiento
//   Vuelo real      · la pantalla del operador con el dron de verdad: cámara, conexión, telemetría, mando y árbitro
// index.html lee window.PRINCIPAL ("3d", "dron" o "mapa") para saber si dibuja el 3D de fondo.
"use strict";
(() => {
  const CLAVE = "estacion-modo-v3";
  const MODOS = {
    dron:  { principal: "dron", centro: ["fpv", "cam-csi0"], sobre: { "sobre-tl": ["p-tel"], "sobre-br": ["p-slam"], "sobre-tr": ["p-cus"], "sobre-bl": ["p-lid360"] }, abajo: ["reproductor"] },
    "3d":  { principal: "3d", izq: ["fpv", "rc", "p-slam"], der: ["p-cus", "p-tel", "p-fsm", "p-arb"], abajo: ["estado-linea", "reproductor"], ocultable: true },
    mapa:  { principal: "mapa", centro: "p-slam", der: ["p-cus", "p-tel", "p-fsm", "p-arb"], abajo: ["estado-linea", "reproductor"] },
    ing:   { principal: "3d", izq: ["p-fsm", "p-dec", "p-obj"], der: ["p-cus", "p-tel", "p-arb", "monitor"], abajo: ["estado-linea", "log", "reproductor"] },
    vuelo: { principal: "dron", centro: "fpv", der: ["p-enlace", "p-tel", "rc", "p-arb", "p-slam"], abajo: ["estado-linea", "log"], derAncha: true },
  };
  const PANELES = ["fpv", "cam-csi0", "p-lid360", "rc", "p-slam", "p-cus", "p-tel", "p-fsm", "p-obj", "p-arb", "p-dec", "monitor", "p-enlace", "estado-linea", "log", "reproductor", "p-3d"];
  const $ = id => document.getElementById(id);
  const caja = (id, clase) => { const d = document.createElement("div"); d.id = id; d.className = "caja " + clase; document.body.appendChild(d); return d; };
  let modo = "dron";

  function iniciar() {
    ["col-izq", "col-der", "centro", "abajo", "guardados", "sobre-tl", "sobre-br", "sobre-tr", "sobre-bl"].forEach(id => caja(id, id.startsWith("sobre") ? "sobre" : id));
    PANELES.forEach(id => { const p = $(id); if (p) { p.classList.add("pnl"); $("guardados").appendChild(p); } });
    ["izq", "der", "dock"].forEach(id => { const c = $(id); if (c && !c.children.length) c.remove(); });
    // en la columna los paneles no se pliegan solos (la columna tiene su propio desplazamiento)
    document.querySelectorAll(".pnl.plegado").forEach(p => p.classList.remove("plegado"));
    document.querySelectorAll("[data-modo]").forEach(b => b.onclick = () => poner(b.dataset.modo));
    $("b-ocultar").onclick = () => { document.body.classList.toggle("sin-paneles"); textoOcultar(); acomodar(); };
    addEventListener("keydown", ev => {
      if (/SELECT|INPUT|TEXTAREA/.test(ev.target.tagName)) return;
      const m = { Digit1: "dron", Digit2: "3d", Digit3: "mapa", Digit4: "ing", Digit5: "vuelo" }[ev.code];
      if (m) poner(m);
    });
    addEventListener("resize", acomodar);
    new ResizeObserver(acomodar).observe($("abajo"));
    let m = "dron";
    try { m = localStorage.getItem(CLAVE) || "dron"; } catch (e) {}
    poner(MODOS[m] ? m : "dron");
    setInterval(acomodarSobre, 500);        // los recuadros sobre la cámara siguen a la imagen si cambia su tamaño
  }

  function textoOcultar() { $("b-ocultar").textContent = document.body.classList.contains("sin-paneles") ? "Mostrar paneles" : "Ocultar paneles"; }

  function poner(m) {
    modo = m;
    const M = MODOS[m];
    try { localStorage.setItem(CLAVE, m); } catch (e) {}
    document.querySelectorAll("[data-modo]").forEach(b => b.classList.toggle("activo", b.dataset.modo === m));
    PANELES.forEach(id => { const p = $(id); if (p) $("guardados").appendChild(p); });          // todo a guardar
    const meter = (destino, ids) => (ids || []).forEach(id => { const p = $(id); if (p) $(destino).appendChild(p); });
    meter("col-izq", M.izq); meter("col-der", M.der); meter("abajo", M.abajo);
    if (M.centro) meter("centro", [].concat(M.centro));
    Object.entries(M.sobre || {}).forEach(([d, ids]) => meter(d, ids));
    document.body.dataset.modo = m;
    document.body.classList.toggle("con-izq", !!M.izq);
    document.body.classList.toggle("con-der", !!M.der);
    document.body.classList.toggle("der-ancha", !!M.derAncha);
    document.body.classList.remove("sin-paneles");
    $("b-ocultar").style.display = M.ocultable ? "" : "none";
    textoOcultar();
    window.PRINCIPAL = M.principal;
    document.body.dataset.principal = M.principal;
    if (window.CAMARAS_APLICAR) CAMARAS_APLICAR();
    acomodar();
  }

  // el alto de la franja de abajo define dónde termina el centro y las columnas
  function acomodar() {
    const h = $("abajo").offsetHeight;
    document.body.style.setProperty("--abajo", (h ? h + 18 : 10) + "px");
    acomodarSobre();
  }
  // los recuadros sobre la cámara del dron van en las esquinas de la imagen (no de la ventana, que tiene franjas negras)
  function acomodarSobre() {
    if (modo !== "dron") return;
    const r = $("fpv-vista").getBoundingClientRect();
    const pon = (id, x, y) => Object.assign($(id).style, { left: x + "px", top: y + "px" });
    pon("sobre-tl", r.left + 12, r.top + 34);
    pon("sobre-tr", r.right - 12 - $("sobre-tr").offsetWidth, r.top + 34);
    pon("sobre-br", r.right - 12 - $("sobre-br").offsetWidth, r.bottom - 12 - $("sobre-br").offsetHeight);
    pon("sobre-bl", r.left + 12, r.bottom - 12 - $("sobre-bl").offsetHeight);
  }

  window.PRINCIPAL = "dron";
  addEventListener("load", () => setTimeout(iniciar, 600));     // después de la animación de entrada de los paneles
})();
