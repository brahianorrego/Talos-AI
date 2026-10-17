// Personas vestidas con animaciones de verdad (fase V2 del plan del visor, D-057): modelos "Ultimate Modular Characters"
// y animaciones de la "Universal Animation Library" de Quaternius (CC0), redirigidas en Blender
// (04_VISOR_Y_MOTOR_GRAFICO/blender/redirigir_animaciones.py y exportar_personas_glb.py).
// Misma interfaz que Humano (humano.js): raiz, H (huesos con los nombres que usan las cajas de YOLO), escala,
// actualizar(p, dt, ctx), manoMundo() y liberar(). Si los GLB no cargan, el visor sigue con Humano.
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { clone } from "three/addons/utils/SkeletonUtils.js";
import { mundo, angNorm, limitar } from "./util.js";

const RUTA = "recursos/personas/";
const MODELOS = { ladron: ["Casual_Hoodie"], peaton: ["Worker", "Casual_2", "Suit", "Farmer"] };
// nombre en las cajas de YOLO (camaras.js) -> hueso del modelo
const HUESOS = { cabeza: "Head", mano_L: "WristL", mano_R: "WristR", dedos_L: "Middle4L", dedos_R: "Middle4R", pie_L: "FootL",
                 pie_R: "FootR", cadera: "Hips", brazo_L: "UpperArmL", brazo_R: "UpperArmR", pierna_L: "LowerLegL", pierna_R: "LowerLegR" };
// velocidad (m/s) a la que cada animación de marcha se ve natural: se acelera o frena con la velocidad real
const MARCHA = [["Idle_Loop", 0, 0.25], ["Walk_Loop", 1.3, 1.9], ["Jog_Fwd_Loop", 3.0, 3.6], ["Sprint_Loop", 5.5, 99]];

let base = null;

export async function cargarPersonas() {
  if (base) return true;
  try {
    const cargador = new GLTFLoader();
    const nombres = [...MODELOS.ladron, ...MODELOS.peaton];
    const [anim, ...modelos] = await Promise.all([cargador.loadAsync(RUTA + "animaciones.glb"), ...nombres.map(n => cargador.loadAsync(RUTA + n + ".glb"))]);
    const alto = {};
    modelos.forEach((g, i) => {
      g.scene.traverse(o => { if (o.isMesh) { o.castShadow = o.receiveShadow = true; o.frustumCulled = false; } });
      alto[nombres[i]] = new THREE.Box3().setFromObject(g.scene).getSize(new THREE.Vector3()).y;
    });
    base = { modelos: Object.fromEntries(nombres.map((n, i) => [n, modelos[i].scene])), alto,
             clips: Object.fromEntries(anim.animations.map(c => [c.name, c])) };
    return true;
  } catch (e) {
    console.warn("Personas GLB no disponibles; se usan las de código:", e);
    return false;
  }
}

function hueso(raiz, nombre) {        // GLTFLoader quita los puntos de los nombres ("Wrist.L" -> "WristL")
  let b = null;
  raiz.traverse(o => { if (!b && o.isBone && o.name.replace(/\./g, "") === nombre) b = o; });
  return b;
}

export class FiguraGLTF {
  constructor(p) {
    const lista = MODELOS[p.rol === "ladron" ? "ladron" : "peaton"];
    const nombre = lista[Math.abs(p.id ?? 0) % lista.length];
    this.raiz = new THREE.Group();
    this.modelo = clone(base.modelos[nombre]);
    this.escala = (p.est || 1.72) / base.alto[nombre];
    this.modelo.scale.setScalar(this.escala);
    this.raiz.add(this.modelo);
    this.H = Object.fromEntries(Object.entries(HUESOS).map(([k, n]) => [k, hueso(this.modelo, n)]));
    this.mezclador = new THREE.AnimationMixer(this.modelo);
    this.acciones = {};
    this.actual = null;
    this.yaw = null;
    this.vel = new THREE.Vector3();
    this.celular = new THREE.Mesh(new THREE.BoxGeometry(0.075, 0.15, 0.009), new THREE.MeshStandardMaterial({ color: 0x111317, roughness: 0.3, metalness: 0.5 }));
    this.celular.scale.setScalar(1 / this.escala);
    this.celular.visible = false;
    if (this.H.mano_R) this.H.mano_R.add(this.celular);
  }
  liberar() { this.mezclador.stopAllAction(); }
  manoMundo(v = new THREE.Vector3()) { return this.H.mano_R.getWorldPosition(v); }

  poner(clip, velocidad = 1, fundido = 0.25) {
    if (!base.clips[clip]) return;
    let a = this.acciones[clip];
    if (!a) { a = this.acciones[clip] = this.mezclador.clipAction(base.clips[clip]); }
    a.timeScale = velocidad;
    if (this.actual === a) return;
    const unaVez = /_(Start|Land)$|^(Roll|Interact|LayToIdle)$/.test(clip);
    a.setLoop(unaVez ? THREE.LoopOnce : THREE.LoopRepeat, Infinity);
    a.clampWhenFinished = unaVez;
    a.reset().play();
    if (this.actual) this.actual.crossFadeTo(a, fundido, false);
    this.actual = a;
  }

  actualizar(p, dt, ctx) {
    const dtR = Math.max(dt, ctx.dtReal || 0);
    this.raiz.position.copy(mundo(p.x, p.y, 0));
    // rumbo: hacia donde se mueve, o hacia donde dice la simulación que mira (suave, como en humano.js)
    const vm = new THREE.Vector3(p.vx, 0, -p.vy);
    this.vel.lerp(vm, this.yaw === null ? 1 : 1 - Math.exp(-dt / 0.18));
    const v = this.vel.length();
    let obj = this.yaw ?? 0;
    if (p.mira !== undefined && p.mira !== null) obj = p.mira + Math.PI / 2;
    else if (v > 0.3) obj = Math.atan2(this.vel.x, this.vel.z);
    if (this.yaw === null) this.yaw = obj;
    this.yaw += limitar(angNorm(obj - this.yaw) * (1 - Math.exp(-dtR / 0.12)), -4 * dtR, 4 * dtR);
    this.raiz.rotation.y = this.yaw;
    // animación según la postura, la acción y la velocidad
    const s = p.salto, fs = s ? s[0] : (p.sz > 0.05 ? 2 : 0), pos = p.pos ?? 0, graba = p.graba || p.civ === 4;
    let y = 0;
    if (fs === 1) this.poner("Jump_Start", 1.6, 0.12);
    else if (fs === 2) { this.poner("Jump_Loop", 1, 0.12); y = (p.sz || 0.35) * Math.sin(Math.PI * limitar(s && s[2] !== undefined ? s[2] : 0.5, 0, 1)); }
    else if (fs === 3) this.poner("Jump_Land", 1.4, 0.12);
    else if (pos === 1 || pos === 3) this.poner(v > 0.15 ? "Crouch_Fwd_Loop" : "Crouch_Idle_Loop", v > 0.15 ? limitar(v / 1.0, 0.6, 1.8) : 1);   // shortcut: gatear usa la marcha agachada hasta tener una animación de gateo
    else if (pos === 2) this.poner("Idle_FoldArms_Loop");
    else if (graba && v < 0.3) this.poner("Idle_TalkingPhone_Loop");
    else {
      const [clip, vRef] = MARCHA.find(([, , hasta]) => v < hasta);
      this.poner(clip, vRef ? limitar(v / vRef, 0.6, 1.6) : 1);
    }
    this.celular.visible = !!graba;
    this.raiz.position.y = y;
    this.mezclador.update(dt);
  }
}
