// Apariencia del dron REAL en el visor: lee recursos/dron_real.json (lo genera 04_VISOR_Y_MOTOR_GRAFICO/modelo_dron/dron_real.py
// a partir de las fotos de 08_EVIDENCIA_Y_DIAGRAMAS) y reemplaza la geometría decorativa de dron.js. Se queda lo que importa: las
// cámaras, el gimbal (límites de la regla dura 1) y la lógica de actualizar().
// Marco del JSON: x adelante, y izquierda, z arriba. En three.js (como mundo() de util.js): X = x, Y = z, Z = -y.
// Con ?dron=v16 se ve el dron de antes. El TF03 va en el gimbal con la cámara USB, como en las fotos (variante A).
import * as THREE from "three";

const PIEZAS_DEL_GIMBAL = new Set(["gimbal_plataforma", "tf03", "camara_usb_placa", "camara_usb_lente", "gimbal_motor_pitch"]);
const PIVOTE = [0.150, 0.0, -0.200];            // eje del motor de pitch, en el marco del JSON

const tres = (x, y, z) => new THREE.Vector3(x, z, -y);

export async function aplicarModeloReal(dron, ruta = "recursos/dron_real.json") {
  const modelo = await (await fetch(ruta)).json();
  const c = dron.chasis;
  // 1) la geometría decorativa de antes se oculta (las cámaras y el gimbal no son mallas, siguen funcionando)
  c.traverse(o => { if (o.isMesh) o.visible = false; });
  const real = new THREE.Group();
  c.add(real);
  dron.gimbal.position.copy(tres(...PIVOTE));
  dron.camara.position.set(0.056, 0.004, 0);      // el lente de la cámara USB, respecto al eje de pitch
  dron.estrobo = { visible: false };              // el estrobo de antes ya no existe
  const mats = {};
  const material = p => {
    const k = p.color + (p.translucido ? "_t" : "");
    if (!mats[k]) {
      const col = modelo.colores[p.color];
      mats[k] = new THREE.MeshStandardMaterial({ color: new THREE.Color(col[0], col[1], col[2]), roughness: ["carbono", "rojo", "espuma"].includes(p.color) ? 0.3 : 0.55,
        metalness: p.color === "dorado" ? 0.9 : 0.05, transparent: !!p.translucido, opacity: p.translucido ? 0.22 : 1, depthWrite: !p.translucido });
    }
    return mats[k];
  };
  const rotores = {};
  const piezas = new URLSearchParams(location.search).get("dron") === "gimbal" ? modelo.piezas_gimbal : modelo.piezas;     // ?dron=gimbal: el dron de antes
  piezas.forEach(p => {
    const [x, y, z] = p.centro;
    let geo, eje = p.eje || "z";
    if (p.forma === "caja") geo = new THREE.BoxGeometry(p.tam[0], p.tam[2], p.tam[1]);
    else geo = new THREE.CylinderGeometry(p.tam[0] / 2, p.tam[0] / 2, p.tam[1], 20);
    const m = new THREE.Mesh(geo, material(p));
    m.castShadow = true;
    const yaw = (p.yaw || 0) * Math.PI / 180, incl = (p.inclinacion || 0) * Math.PI / 180;
    m.rotation.order = "YXZ";
    m.rotation.y = yaw;
    if (p.forma === "cilindro") {
      if (eje === "x") m.rotation.z = -Math.PI / 2;
      else if (eje === "y") m.rotation.x = Math.PI / 2;
      else m.rotation.x = incl;
    }
    const posicion = tres(x, y, z);
    // las hélices y su cono giran juntos, alrededor del eje de su motor
    const k = /^(helice|cono)(\d)$/.exec(p.nombre);
    if (k) {
      const n = k[2];
      if (!rotores[n]) {
        const mo = piezas.find(q => q.nombre === "motor" + n);
        const g = new THREE.Group();
        g.position.copy(tres(mo.centro[0], mo.centro[1], 0));
        real.add(g);
        rotores[n] = { rotor: g, sentido: Number(n) % 2 ? 1 : -1 };
      }
      m.position.set(0, posicion.y, 0);
      rotores[n].rotor.add(m);
      return;
    }
    if (PIEZAS_DEL_GIMBAL.has(p.nombre)) {          // cuelgan del gimbal: se inclinan con su pitch
      m.position.copy(posicion).sub(dron.gimbal.position);
      dron.gimbal.add(m);
      return;
    }
    m.position.copy(posicion);
    if (p.nombre === "bateria" || p.nombre === "velcro_azul") m.userData.tapaPiso = true;
    real.add(m);
  });
  dron.rotores = Object.values(rotores);
  dron.modeloReal = true;
}
