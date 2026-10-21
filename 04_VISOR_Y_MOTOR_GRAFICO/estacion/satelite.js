// Mapa satelital de la estación (TALOS-AI). Leaflet con teselas de Esri World Imagery que sirve estacion/servidor.py desde su caché local (/tiles/z/x/y.jpg),
// así funciona sin internet una vez precargado el campus (mapa/precargar_teselas.py). Sobre la imagen: posición y rumbo del dron, trayectoria, geocerca,
// cancha, zona de IA, paneles, personas, objetivo y ruta de búsqueda. La arena de la simulación está georreferenciada con entorno_u.json -> "georef".
//
// GPS REAL: cuando el dron vuele de verdad, la estación solo tiene que llamar  SAT.gps({ lat, lon, rumbo, alt })  con lo que llegue por MAVLink
// (GLOBAL_POSITION_INT y VFR_HUD): el marcador, la trayectoria y el centrado pasan a usar esa posición en lugar de la de la simulación.
// Atribución obligatoria (Esri, Maxar, Earthstar Geographics) en la esquina del mapa.
const SAT = (() => {
  const S = { mapa: null, listo: false, georef: null, capas: {}, tray: [], seguir: true, gps: null, visible: false, ultimaTray: 0 };
  const M_LAT = 111320;
  const deg = r => r * 180 / Math.PI;
  const a = (x, y) => {                                                  // metros del mundo (x este, y norte) -> [lat, lon]
    const g = S.georef, lat0 = g.centro_campo_latlon[0] + g.origen_desde_centro_campo_m[1] / M_LAT, lon0 = g.centro_campo_latlon[1] + g.origen_desde_centro_campo_m[0] / (M_LAT * Math.cos(g.centro_campo_latlon[0] * Math.PI / 180));
    return [lat0 + y / M_LAT, lon0 + x / (M_LAT * Math.cos(lat0 * Math.PI / 180))];
  };
  const icono = () => L.divIcon({ className: "sat-dron", iconSize: [44, 44], iconAnchor: [22, 22],
    html: '<svg viewBox="0 0 44 44"><g class="g"><path d="M22 3 33 36 22 29 11 36Z" fill="#2fa4e7" stroke="#fff" stroke-width="2.2" stroke-linejoin="round"/></g></svg>' });

  async function iniciar() {
    if (S.listo || typeof L === "undefined") return;
    try { S.georef = (await (await fetch("entorno_u.json", { cache: "no-store" })).json()).georef; } catch (e) { S.georef = null; }
    if (!S.georef) { console.warn("sin georreferencia"); return; }
    const c0 = a(0, 0);
    const m = L.map("sat", { center: c0, zoom: 19, maxZoom: 21, zoomSnap: 0.5, attributionControl: true, zoomControl: true });
    m.attributionControl.setPrefix(false);
    L.tileLayer("/tiles/{z}/{x}/{y}.jpg", { maxNativeZoom: 19, maxZoom: 21, attribution: "Imágenes © Esri, Maxar, Earthstar Geographics", errorTileUrl: "" }).addTo(m);
    L.control.scale({ metric: true, imperial: false, position: "bottomleft" }).addTo(m);
    S.mapa = m;
    const C = S.capas;
    const [cx, cy] = S.georef ? [0, -25.5] : [0, 0], T = [67, 102];
    C.cancha = L.polygon([[-T[0] / 2, cy - T[1] / 2], [T[0] / 2, cy - T[1] / 2], [T[0] / 2, cy + T[1] / 2], [-T[0] / 2, cy + T[1] / 2]].map(p => a(p[0], p[1])), { color: "#ffffff", weight: 1.5, opacity: .7, fill: false, dashArray: "2 6" }).addTo(m);
    C.zona = L.polygon([[-15, -15], [15, -15], [15, 15], [-15, 15]].map(p => a(p[0], p[1])), { color: "#ff8a1f", weight: 2, fill: true, fillOpacity: .06, dashArray: "6 5" }).addTo(m);
    C.geocerca = L.polygon([[-25, -25], [25, -25], [25, 25], [-25, 25]].map(p => a(p[0], p[1])), { color: "#f5a623", weight: 2.5, fill: false, dashArray: "10 6" }).addTo(m);
    C.geocerca.bindTooltip("Geocerca 25 m", { permanent: true, direction: "top", className: "sat-etq", offset: [0, -2] });
    C.tray = L.polyline([], { color: "#2fa4e7", weight: 3, opacity: .95 }).addTo(m);
    C.ruta = L.polyline([], { color: "#ffffff", weight: 2, opacity: .8, dashArray: "3 6" }).addTo(m);
    C.fov = L.polygon([], { color: "#2fa4e7", weight: 1, fillColor: "#2fa4e7", fillOpacity: .18 }).addTo(m);
    C.paneles = L.layerGroup().addTo(m);
    C.pers = L.layerGroup().addTo(m);
    C.dron = L.marker(c0, { icon: icono(), zIndexOffset: 1000, interactive: false }).addTo(m);
    // controles propios: seguir al dron, centrar, borrar la trayectoria
    const Ctl = L.Control.extend({ options: { position: "topright" }, onAdd() {
      const d = L.DomUtil.create("div", "sat-ctl");
      d.innerHTML = '<button id="satSeguir" class="act" title="La vista sigue al dron">Seguir</button><button id="satCentrar" title="Centrar en el dron">Centrar</button><button id="satBorrar" title="Borrar la trayectoria">Borrar ruta</button>';
      L.DomEvent.disableClickPropagation(d); return d; } });
    m.addControl(new Ctl());
    const $ = id => document.getElementById(id);
    $("satSeguir").onclick = () => { S.seguir = !S.seguir; $("satSeguir").classList.toggle("act", S.seguir); };
    $("satCentrar").onclick = () => { if (S.ult) m.setView(S.ult, Math.max(m.getZoom(), 19)); };
    $("satBorrar").onclick = () => { S.tray.length = 0; C.tray.setLatLngs([]); };
    m.on("dragstart", () => { S.seguir = false; $("satSeguir").classList.remove("act"); });
    const info = L.control({ position: "bottomright" }); info.onAdd = () => { const d = L.DomUtil.create("div", "sat-info"); d.id = "satInfo"; return d; }; info.addTo(m);
    S.listo = true;
  }

  // se llama ~5 veces por segundo con el último cuadro de la simulación (c) y el estado de la estación (est)
  function actualizar(c, est) {
    if (!S.listo || !c) return;
    const C = S.capas, [x, y, z, psi] = c.d;
    const g = S.gps, pos = g ? [g.lat, g.lon] : a(x, y), rumbo = g ? g.rumbo : ((90 - deg(psi)) % 360 + 360) % 360;
    S.ult = pos;
    const ahora = performance.now();
    if (ahora - S.ultimaTray > 400) {
      S.ultimaTray = ahora; S.tray.push(pos); if (S.tray.length > 900) S.tray.shift();
      C.tray.setLatLngs(S.tray);
    }
    if (!S.visible) return;
    C.dron.setLatLng(pos); const gsvg = C.dron.getElement(); if (gsvg) gsvg.querySelector(".g").setAttribute("transform", `rotate(${rumbo.toFixed(1)} 22 22)`);
    if (S.seguir) S.mapa.panTo(pos, { animate: false });
    // cono de la cámara principal: pan + campo de vista horizontal de 68.3°
    const yawC = psi + (c.pan || 0) * Math.PI / 180, R = 28, pts = [pos];
    for (let k = -4; k <= 4; k++) { const an = yawC + k * (34.15 / 4) * Math.PI / 180; pts.push(g ? pos : a(x + R * Math.cos(an), y + R * Math.sin(an))); }
    C.fov.setLatLngs(g ? [] : pts);
    // paneles, personas y ruta de búsqueda
    C.paneles.clearLayers(); (est.paneles || []).forEach(p => L.polyline([a(p[0], p[1]), a(p[2], p[3])], { color: "#ffffff", weight: 5, opacity: .95, lineCap: "butt" }).addTo(C.paneles));
    C.pers.clearLayers(); const fijado = ["PERSECUCION", "PERDIDA", "RECONFIRMAR", "FIJADO"].includes(c.eb);
    (c.pers || []).forEach(q => { const lad = q.rol === "ladron"; const ll = a(q.p[0], q.p[1]);
      L.circleMarker(ll, { radius: lad ? 7 : 5, color: "#07090b", weight: 1.5, fillColor: lad ? "#e5484d" : "#d5dce8", fillOpacity: 1 }).addTo(C.pers);
      if (lad && fijado) L.circleMarker(ll, { radius: 14, color: "#e5484d", weight: 2, fill: false }).addTo(C.pers); });
    C.ruta.setLatLngs(est.ruta && c.ruta ? c.ruta.map(q => a(q[0], q[1])) : []);
    const el = document.getElementById("satInfo");
    if (el) el.innerHTML = `<b>${pos[0].toFixed(6)}, ${pos[1].toFixed(6)}</b><br>rumbo ${String(Math.round(rumbo)).padStart(3, "0")}° · alt ${z.toFixed(1)} m${g ? " · GPS real" : " · posición simulada"}`;
  }

  async function mostrar(v) {
    S.visible = v; const d = document.getElementById("sat"); if (d) d.style.visibility = v ? "visible" : "hidden";
    if (v) { await iniciar(); if (S.mapa) { S.mapa.invalidateSize(); if (S.ult) S.mapa.setView(S.ult, S.mapa.getZoom()); } }
  }
  return { mostrar, actualizar, iniciar, gps: g => { S.gps = g || null; } };
})();
