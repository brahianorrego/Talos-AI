// Árboles y pasto de verdad (fase V3 del plan del visor): "Stylized Nature MegaKit" de Quaternius (CC0),
// en recursos/naturaleza/. Se dibujan con instancias (una sola llamada a la tarjeta por cada parte de cada modelo).
// Los árboles hechos con código (escena.js y previa.js) se cambian por estos en las mismas posiciones; si los modelos no
// cargan, se quedan los de antes.
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { azar } from "./util.js";

const RUTA = "recursos/naturaleza/";
const ARBOLES = ["CommonTree_1", "CommonTree_3", "CommonTree_5", "Pine_2"];
const ESC_ARBOL = 0.9;          // los árboles del paquete miden ~7-9 m; los de código, ~6-8 m
let partes = null;               // nombre -> [{ geometria, material, matriz }]

export async function cargarNaturaleza() {
  if (partes) return true;
  try {
    const cargador = new GLTFLoader();
    const nombres = [...ARBOLES, "Grass_Common_Short"];
    const escenas = await Promise.all(nombres.map(n => cargador.loadAsync(RUTA + n + ".gltf")));
    partes = {};
    escenas.forEach((g, i) => {
      g.scene.updateMatrixWorld(true);
      const lista = [];
      g.scene.traverse(o => {
        if (!o.isMesh) return;
        const m = o.material;
        if (m.alphaTest === 0 && m.map && /Leaves|Leaf/.test(m.name)) m.alphaTest = 0.5;
        if (/Leaves|Leaf|Grass/.test(m.name)) m.side = THREE.DoubleSide;
        lista.push({ geometria: o.geometry, material: m, matriz: o.matrixWorld.clone() });
      });
      partes[nombres[i]] = lista;
    });
    return true;
  } catch (e) {
    console.warn("Naturaleza de Quaternius no disponible; se usan los árboles de código:", e);
    return false;
  }
}

// copias de un modelo con las matrices dadas (en el mundo three); devuelve un grupo con un InstancedMesh por parte
export function instancias(nombre, matrices, { sombras = true, nombreGrupo = nombre } = {}) {
  const g = new THREE.Group(); g.name = nombreGrupo;
  partes[nombre].forEach(({ geometria, material, matriz }) => {
    const im = new THREE.InstancedMesh(geometria, material, matrices.length);
    const m = new THREE.Matrix4();
    matrices.forEach((M, k) => im.setMatrixAt(k, m.multiplyMatrices(M, matriz)));
    im.castShadow = sombras; im.receiveShadow = true;
    im.raycast = () => {};       // shortcut: los árboles no tapan a las personas en la prueba de visibilidad de la vista previa; si hace falta, usar cilindros simples
    im.computeBoundingSphere();
    g.add(im);
  });
  return g;
}

// cambia los árboles de código (InstancedMesh con colores por vértice) de un grupo por árboles del paquete
export function reemplazarArboles(grupo, semilla = 3) {
  if (!partes) return;
  const r = azar(semilla), viejos = grupo.children.filter(o => o.isInstancedMesh && o.material.vertexColors);
  const porModelo = Object.fromEntries(ARBOLES.map(n => [n, []]));
  const m = new THREE.Matrix4(), s = new THREE.Matrix4().makeScale(ESC_ARBOL, ESC_ARBOL, ESC_ARBOL);
  viejos.forEach(im => {
    for (let k = 0; k < im.count; k++) {
      im.getMatrixAt(k, m);
      porModelo[ARBOLES[Math.floor(r() * ARBOLES.length)]].push(m.clone().multiply(s));
    }
    grupo.remove(im);
  });
  Object.entries(porModelo).forEach(([n, lista]) => { if (lista.length) { const g = instancias(n, lista); g.userData.arbol = true; grupo.add(g); } });
}

// matas de pasto en un cuadrado de lado `lado` (m) centrado en el origen
export function sembrar(grupo, { lado = 60, matas = 22000, semilla = 11 } = {}) {
  if (!partes) return;
  const r = azar(semilla), q = new THREE.Quaternion(), y = new THREE.Vector3(0, 1, 0), p = new THREE.Vector3(), e = new THREE.Vector3();
  const mats = [];
  for (let k = 0; k < matas; k++) {
    const sc = 0.14 + r() * 0.14;
    mats.push(new THREE.Matrix4().compose(p.set((r() - 0.5) * lado, 0, (r() - 0.5) * lado), q.setFromAxisAngle(y, r() * 6.28), e.set(sc, sc * (0.7 + r() * 0.6), sc)));
  }
  const pasto = instancias("Grass_Common_Short", mats, { sombras: false, nombreGrupo: "pasto" });
  pasto.userData.pasto = true;
  grupo.add(pasto);
}
