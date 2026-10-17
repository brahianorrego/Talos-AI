// Abre el visor V16 en un Chrome visible con perfil aparte y mide cuadros por segundo por calidad (CDP, Node 24).
// Uso: node medir_fps.mjs <etiqueta> <carpeta_salida> [banderas extra de Chrome...]
import { spawn } from "node:child_process";
import { writeFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const [etiqueta, salida, ...extra] = process.argv.slice(2);
const PUERTO = 9333;
const perfil = join(salida, "perfil_" + etiqueta);
mkdirSync(perfil, { recursive: true });
const chrome = spawn("C:/Program Files/Google/Chrome/Application/chrome.exe", [
  `--remote-debugging-port=${PUERTO}`, `--user-data-dir=${perfil}`, "--window-size=1600,900", "--window-position=0,0",
  "--no-first-run", "--no-default-browser-check", "--disable-background-timer-throttling",
  "--disable-renderer-backgrounding", "--disable-backgrounding-occluded-windows", ...extra, "http://127.0.0.1:8766/"], { stdio: "ignore" });

const dormir = ms => new Promise(r => setTimeout(r, ms));
let pag;
for (let i = 0; i < 40 && !pag; i++) {
  await dormir(500);
  try { pag = (await (await fetch(`http://127.0.0.1:${PUERTO}/json`)).json()).find(t => t.type === "page" && t.url.includes("8766")); } catch {}
}
if (!pag) { chrome.kill(); throw new Error("Chrome no abrió el puerto de depuración"); }
const ws = new WebSocket(pag.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener("open", r));
let id = 0; const esperas = new Map();
ws.addEventListener("message", ev => { const m = JSON.parse(ev.data); if (esperas.has(m.id)) { esperas.get(m.id)(m); esperas.delete(m.id); } });
const cdp = (method, params = {}) => new Promise(r => { const k = ++id; esperas.set(k, r); ws.send(JSON.stringify({ id: k, method, params })); });
const evaluar = async expr => {
  const m = await cdp("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true });
  if (!m.result) throw new Error(JSON.stringify(m.error));
  if (m.result.exceptionDetails) throw new Error(JSON.stringify(m.result.exceptionDetails));
  return m.result.result.value;
};

await cdp("Page.bringToFront");
await dormir(3000);
await evaluar(`new Promise(r => { const f = () => (window.__v16 && document.getElementById('cargando').style.display === 'none') ? r() : setTimeout(f, 300); f(); })`);
// la partida corre sin detenerse a esperar el clic del operador, y con el panel de ingeniería abierto
await evaluar(`(() => { window.__v16.irA(0); document.getElementById('b-pausa').click(); document.getElementById('b-ing').click(); })()`);
await dormir(3000);
const info = await evaluar(`(() => { const gl = document.createElement('canvas').getContext('webgl2'); const e = gl.getExtension('WEBGL_debug_renderer_info');
  return { gpu: gl.getParameter(e.UNMASKED_RENDERER_WEBGL), w: innerWidth, h: innerHeight, dpr: devicePixelRatio, vis: document.visibilityState }; })()`);
const res = { etiqueta, extra, ...info, calidades: {} };
if (etiqueta === "capturas") {   // fotos para Brahian: [nombre, código que arma la toma]
  const tomas = [
    ["camara_yolo", "__v16.irA(7.5)"],
    ["externa_salto", "__v16.irA(41.5); __v16.vista('externa'); __v16.modo('seguir')"],
    ["externa_paneles", "__v16.irA(31); __v16.vista('externa'); __v16.modo('cine')"],
    ["previa_hangar", "await __v16.escenario('hangar'); __v16.vista('externa'); __v16.modo('libre')"],
    ["previa_campo", "await __v16.escenario('campo'); __v16.vista('externa'); __v16.modo('libre')"],
  ];
  await evaluar(`document.getElementById('b-ing').click()`);   // cerrar ingeniería para que se vea la escena
  for (const [nombre, js] of tomas) {
    await evaluar(`(async () => { ${js}; })()`);
    await dormir(2500);
    const foto = await cdp("Page.captureScreenshot", { format: "png" });
    writeFileSync(join(salida, `v16_${nombre}.png`), Buffer.from(foto.result.data, "base64"));
  }
  ws.close(); chrome.kill(); process.exit(0);
}
for (const q of ["alta", "media", "baja"]) {
  res.calidades[q] = await evaluar(`(async () => {
    const sel = document.getElementById('calidad'); sel.value = '${q}'; sel.dispatchEvent(new Event('change'));
    await new Promise(r => setTimeout(r, 4000));
    let n = 0, dts = [], tp = performance.now(); const t0 = tp;
    await new Promise(r => { function f(now) { n++; dts.push(now - tp); tp = now; if (now - t0 < 10000) requestAnimationFrame(f); else r(); } requestAnimationFrame(f); });
    dts.sort((a, b) => a - b);
    return { fps: +(n / 10).toFixed(1), ms_mediana: +dts[dts.length >> 1].toFixed(1), ms_p95: +dts[Math.floor(dts.length * 0.95)].toFixed(1),
             panel: document.getElementById('i-fps').textContent, t_partida: window.__v16.tiempo() };
  })()`);
  const foto = await cdp("Page.captureScreenshot", { format: "png" });
  writeFileSync(join(salida, `v16_${etiqueta}_${q}.png`), Buffer.from(foto.result.data, "base64"));
}
console.log(JSON.stringify(res, null, 1));
writeFileSync(join(salida, `fps_${etiqueta}.json`), JSON.stringify(res, null, 1));
ws.close(); chrome.kill();
