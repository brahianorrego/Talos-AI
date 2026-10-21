// Foto de la estación (página completa, aunque otra ventana la tape) por el protocolo de depuración de Edge/Chrome.
// Uso: msedge --app=URL --remote-debugging-port=9222 --user-data-dir=<carpeta> ; node capturar_estacion_cdp.mjs salida.png [puerto]
import fs from "node:fs";
const [salida = "estacion.png", puerto = "9222", ancho = "0", alto = "0"] = process.argv.slice(2);   // ancho y alto fuerzan el tamaño de la página (p. ej. 1920 1080)
const paginas = await (await fetch(`http://127.0.0.1:${puerto}/json`)).json();
const pag = paginas.find(p => p.type === "page");
const ws = new WebSocket(pag.webSocketDebuggerUrl);
await new Promise(r => (ws.onopen = r));
let id = 0; const esperan = {};
ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && esperan[m.id]) esperan[m.id](m); };
const llamar = (metodo, params = {}) => new Promise(r => { const i = ++id; esperan[i] = r; ws.send(JSON.stringify({ id: i, method: metodo, params })); });
await llamar("Page.bringToFront");
if (+ancho) { await llamar("Emulation.setDeviceMetricsOverride", { width: +ancho, height: +alto, deviceScaleFactor: 1, mobile: false }); await new Promise(r => setTimeout(r, 2500)); }
const r = await llamar("Page.captureScreenshot", { format: "png" });
fs.writeFileSync(salida, Buffer.from(r.result.data, "base64"));
ws.close(); console.log("guardado", salida);
