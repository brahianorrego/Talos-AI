// Modo "Vista del dron" (fase V4, boceto 04_VISOR_Y_MOTOR_GRAFICO/boceto_interfaz.svg): mapa de puntos del LiDAR y
// órdenes que la Jetson manda a la Pixhawk.
// Las repeticiones de la V16 no traen la nube de puntos ni las órdenes: la nube se arma acumulando los impactos del TF03
// (`lh`) y del TF-Luna (`luna`), como haría la estación con el sensor real; las órdenes se aproximan con la telemetría
// (velocidad, rumbo, gimbal, altura pedida). Cuando foto() traiga `cmd` y `arb` (encargo a Simulación V17), se usan esos.
import { $, limitar, angNorm } from "./util.js";

const HIST = 10;               // s de historial de las órdenes
const MAX_PTS = 900;           // puntos del LiDAR que se recuerdan
const pwm = g => Math.round(1500 + g * 500 / 45);           // AUX1 del gimbal (regla dura 1)

export class VistaDron {
  constructor() {
    this.pts = [];             // [x, y, sensor, t]
    this.hist = [];            // [t, vx, vy, vz, yawRate, gimbal]
    this.prev = null;
  }
  reiniciar() { this.pts.length = 0; this.hist.length = 0; this.prev = null; }

  // se llama en cada cuadro, en cualquier modo (para que la nube y el historial estén listos al cambiar de modo)
  acumular(e, t) {
    if (this.prev && t < this.prev.t) this.reiniciar();                       // saltó hacia atrás en la línea de tiempo
    const agregar = (q, s) => { if (q && q.length >= 2 && isFinite(q[0])) { this.pts.push([q[0], q[1], s, t]); } };
    if (!this.prev || this.prev.k !== e.k) { agregar(e.lh, 0); agregar(e.luna, 1); }
    if (this.pts.length > MAX_PTS) this.pts.splice(0, this.pts.length - MAX_PTS);
    const dt = this.prev ? t - this.prev.t : 0;
    const w = dt > 1e-3 ? angNorm(e.psi - this.prev.psi) / dt : (this.hist.length ? this.hist[this.hist.length - 1][4] : 0);
    const vz = dt > 1e-3 ? (e.z - this.prev.z) / dt : 0;
    const cmd = e.cmd;                                                         // [vx, vy, vz, yaw_rate, gimbal, modo, quien]
    this.hist.push(cmd ? [t, cmd[0], cmd[1], cmd[2], cmd[3], cmd[4]] : [t, e.vx, e.vy, vz, w * 180 / Math.PI, e.gmb]);
    while (this.hist.length && this.hist[0][0] < t - HIST) this.hist.shift();
    this.prev = { t, k: e.k, psi: e.psi, z: e.z };
  }

  quienManda(e) {
    if (e.cmd && e.cmd[6]) return [e.cmd[6], "var(--aviso)"];
    if (e.fase === 1) return [e.bloq ? "Piloto · bloqueo LiDAR" : "Piloto (radio)", "var(--info)"];
    if (e.rfx || e.gd) return ["Árbitro · esquive", "var(--peligro)"];
    if (e.amz) return ["IA · árbitro alerta", "var(--aviso)"];
    return [e.modo >= 2 ? "IA (PPO) · siguiendo" : "Reglas · búsqueda", "var(--ok)"];
  }

  actualizar(e) {
    const h = this.hist[this.hist.length - 1];
    if (!h) return;
    const [quien, color] = this.quienManda(e);
    $("o-quien").textContent = quien; $("o-quien").style.color = color;
    $("o-vel").textContent = `${h[1].toFixed(1)}  ${h[2].toFixed(1)}  ${h[3].toFixed(1)} m/s`;
    $("o-yaw").textContent = `${h[4] >= 0 ? "+" : ""}${h[4].toFixed(0)} °/s`;
    $("o-gmb").textContent = `${h[5].toFixed(0)}° → PWM ${pwm(h[5])}`;
    $("o-alt").textContent = e.altObj !== null && e.altObj !== undefined ? `${e.altObj.toFixed(2)} m` : "–";
    $("o-modo").textContent = e.fase === 1 ? "LOITER" : "GUIDED";
    $("o-fuente").textContent = e.cmd ? "órdenes de la repetición (cmd)" : "aproximadas desde la telemetría (la repetición no trae cmd)";
    this.dibujarHistorial();
    this.dibujarLidar(e);
  }

  lienzo(id) {
    const c = $(id), r = c.getBoundingClientRect(), dpr = Math.min(devicePixelRatio, 2);
    if (c.width !== Math.round(r.width * dpr) || c.height !== Math.round(r.height * dpr)) { c.width = Math.round(r.width * dpr); c.height = Math.round(r.height * dpr); }
    const g = c.getContext("2d");
    g.setTransform(1, 0, 0, 1, 0, 0);
    g.fillStyle = "#121519"; g.fillRect(0, 0, c.width, c.height);
    return { g, W: c.width, H: c.height, dpr };
  }

  dibujarHistorial() {
    const { g, W, H, dpr } = this.lienzo("o-graf");
    if (W < 20 || this.hist.length < 2) return;
    const t1 = this.hist[this.hist.length - 1][0], X = t => W - (t1 - t) / HIST * W;
    const canales = [[1, "#6aa9d8", 3, "vx"], [2, "#3cc46e", 3, "vy"], [4, "#f0a623", 90, "yaw"], [5, "#c792ea", 45, "gimbal"]];
    g.strokeStyle = "#20252b"; g.lineWidth = 1; g.beginPath(); g.moveTo(0, H / 2); g.lineTo(W, H / 2); g.stroke();
    canales.forEach(([i, col, esc, nom], n) => {
      g.strokeStyle = col; g.lineWidth = 1.4 * dpr; g.beginPath();
      this.hist.forEach((q, k) => { const y = H / 2 - limitar(q[i] / esc, -1, 1) * (H / 2 - 4 * dpr); k ? g.lineTo(X(q[0]), y) : g.moveTo(X(q[0]), y); });
      g.stroke();
      g.fillStyle = col; g.font = `${10 * dpr}px Consolas, monospace`; g.fillText(nom, 6 * dpr + n * 52 * dpr, 12 * dpr);
    });
    g.fillStyle = "#5b636d"; g.fillText("últimos 10 s", W - 80 * dpr, H - 5 * dpr);
  }

  dibujarLidar(e) {
    const { g, W, H, dpr } = this.lienzo("lidar");
    if (W < 20) return;
    const R = 14, esc = Math.min(W, H) / (2 * R), X = x => W / 2 + (x - e.x) * esc, Y = y => H / 2 - (y - e.y) * esc;
    g.strokeStyle = "#1c2026"; g.lineWidth = 1;                                     // anillos cada 5 m
    [5, 10].forEach(r => { g.beginPath(); g.arc(W / 2, H / 2, r * esc, 0, 2 * Math.PI); g.stroke(); });
    const t = this.prev ? this.prev.t : 0;
    this.pts.forEach(([x, y, s, tp]) => {                                           // los puntos viejos se apagan
      g.globalAlpha = limitar(1 - (t - tp) / 60, 0.25, 1);
      g.fillStyle = s ? "#4fc3f7" : "#f0a623";
      g.fillRect(X(x) - 1.5 * dpr, Y(y) - 1.5 * dpr, 3 * dpr, 3 * dpr);
    });
    g.globalAlpha = 1;
    // rayo actual del TF03 y su alcance
    if (e.lh) { g.strokeStyle = "rgba(240,166,35,.6)"; g.lineWidth = 1.2 * dpr; g.beginPath(); g.moveTo(W / 2, H / 2); g.lineTo(X(e.lh[0]), Y(e.lh[1])); g.stroke(); }
    // el dron, con la dirección de la cámara
    g.save(); g.translate(W / 2, H / 2); g.rotate(-e.psi);
    g.fillStyle = "rgba(106,169,216,.18)"; g.beginPath(); g.moveTo(0, 0); g.arc(0, 0, 6 * esc, -0.34, 0.34); g.fill();
    g.fillStyle = "#e8ecf0"; g.beginPath(); g.moveTo(7 * dpr, 0); g.lineTo(-5 * dpr, 4 * dpr); g.lineTo(-5 * dpr, -4 * dpr); g.fill();
    g.restore();
    g.fillStyle = "#8b949e"; g.font = `${10.5 * dpr}px Segoe UI, sans-serif`;
    g.fillText(`TF03 (naranja) ${e.lid !== undefined ? e.lid.toFixed(1) + " m" : ""} · TF-Luna (azul) · anillos de 5 m`, 8 * dpr, H - 7 * dpr);
  }
}
