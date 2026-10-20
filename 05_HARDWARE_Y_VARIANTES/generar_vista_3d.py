"""Genera VISTA_3D.html (visor three.js con los STL incrustados) a partir de piezas_3d/stl/*.stl.

Uso:  python generar_vista_3d.py      (desde cualquier carpeta; solo lee piezas_3d/stl y escribe VISTA_3D.html)
Los servos, la cámara y el TF-Luna del montaje se dibujan en el navegador (formas simples, solo ilustración).
"""
import base64
import json
import os
import re
import struct

AQUI = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(AQUI, "piezas_3d", "stl")

PIEZAS = [
    ("pan_tilt_base", "Pan-tilt H · base"),
    ("pan_tilt_plataforma", "Pan-tilt H · plataforma con mejillas"),
    ("pan_tilt_cuna", "Pan-tilt H · cuna con placa para CSI + TF-Luna"),
    ("soporte_luna_pod", "Variante C · soporte del TF-Luna para el pod"),
    ("soporte_tf03_colgante", "Variante C/D · soporte del TF03 al chasis"),
    ("soporte_lidar_luna_pantilt", "Variante D · soporte del TF-Luna en la cuna"),
    ("soporte_camara_frente", "Soporte de cámara IMX219 al frente"),
    ("soporte_camara_abajo", "Soporte de cámara IMX219 al piso"),
    ("soporte_csi_doble", "Soporte de las dos cámaras CSI (piso + frontal ancha)"),
]
MONTAJE = ["asm_base", "asm_plataforma", "asm_plataforma_ancho", "asm_cuna"]


def binario(nombre):
    """STL ascii de OpenSCAD -> STL binario en base64 (cuatro veces más chico)."""
    t = open(os.path.join(STL, nombre + ".stl"), "rb").read()
    v = [tuple(map(float, m)) for m in re.findall(rb"vertex\s+(\S+)\s+(\S+)\s+(\S+)", t)]
    buf = bytearray(80) + struct.pack("<I", len(v) // 3)
    for i in range(0, len(v), 3):
        buf += struct.pack("<12fH", 0, 0, 0, *v[i], *v[i + 1], *v[i + 2], 0)
    return base64.b64encode(bytes(buf)).decode()


PLANTILLA = r'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vista 3D del pan-tilt</title>
<style>
:root{--bg:#eef0f4;--fg:#1d2330;--card:#fff;--ac:#1565c0}
@media (prefers-color-scheme:dark){:root{--bg:#10131a;--fg:#e8ebf2;--card:#1c2230;--ac:#64b5f6}}
html,body{margin:0}
body{background:var(--bg);color:var(--fg);font:16px/1.45 system-ui,Arial,sans-serif}
main{max-width:1100px;margin:0 auto;padding:16px}
h1{font-size:1.35rem;margin:.2em 0}
.fila{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:10px 0}
button,label.btn{background:var(--card);color:var(--fg);border:1px solid #8886;border-radius:8px;padding:8px 12px;font:inherit;cursor:pointer}
button.on{background:var(--ac);color:#fff;border-color:var(--ac)}
.sw{width:22px;height:22px;border-radius:50%;display:inline-block;vertical-align:middle;margin-right:6px;border:1px solid #8888}
#vista{width:100%;height:68vh;min-height:340px;border-radius:14px;touch-action:none;display:block;background:linear-gradient(#f9fafc,#cfd5df)}
@media (prefers-color-scheme:dark){#vista{background:linear-gradient(#262d3d,#0b0d12)}}
.nota{background:var(--card);border-radius:12px;padding:12px;margin-top:12px;font-size:.93rem}
input[type=range]{width:min(360px,70vw)}
</style></head><body><main>
<h1>El pan-tilt de la variante H, casi real</h1>
<div class="fila" id="modos"></div>
<div class="fila" id="color"></div>
<div class="fila" id="extra"></div>
<canvas id="vista"></canvas>
<div class="nota" id="info"></div>
<div class="nota">Arrastra para girar, rueda para acercar, Mayús + arrastrar para mover. Las piezas impresas están <b>diseñadas por nosotros</b> (no se descargaron de ningún sitio) y <b>aún no se han impreso</b>. Los servos MG90D, la CSI IMX219 (medidas del dibujo oficial de Raspberry Pi) y el TF-Luna (ficha oficial) son <b>ilustraciones</b>: el cable flex dorado es solo una indicación. La base y su montaje en el dron dependen de medidas pendientes (ver <code>piezas_3d/ESTADO_IMPRESION.md</code>). El módulo va <b>colgado bajo el chasis</b> (de cabeza). El deslizador de cabeceo se detiene donde el pin de plástico choca con la ranura: −44° y +14° con la regla dura 1. El botón de rango ancho muestra solo la <b>capacidad mecánica</b> (mirar hasta el suelo, −89°, y +44°): <b>no está aprobado</b> y la fórmula del PWM no lo cubre.</div>
</main>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const PIEZAS=__PIEZAS__, MONTAJE=__MONTAJE__;
const Z_EJE=45, YA=-32, YB=28.6;
const COLORES={Gris:0x70757e,Blanco:0xeceae4,Negro:0x1d1e22};
let colgado=true,ancho=false,mallaPlat,chasis,ren,esc,cam,grupoMontaje,grupoCuna,piezaMalla,modo='montaje',colorSel='Gris',rot={x:-0.55,z:0.75},dist=260,mira=new THREE.Vector3(0,0,15),auto=false,tilt=0,verElec=true;
const cv=document.getElementById('vista'),info=document.getElementById('info');
const matPLA=()=>new THREE.MeshPhysicalMaterial({color:COLORES[colorSel],roughness:.52,metalness:0,clearcoat:.12,clearcoatRoughness:.6});
const piezasPLA=[];
function geom(b64){const bin=atob(b64),u=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);
 const dv=new DataView(u.buffer),n=dv.getUint32(80,true),p=new Float32Array(n*9);
 for(let i=0;i<n;i++)for(let k=0;k<9;k++)p[i*9+k]=dv.getFloat32(84+i*50+12+k*4,true);
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(p,3));g.computeVertexNormals();g.computeBoundingBox();return g}
function pla(g){const m=new THREE.Mesh(g,matPLA());m.castShadow=m.receiveShadow=true;piezasPLA.push(m);return m}
const M=(c,r=.5,m=0,o={})=>new THREE.MeshStandardMaterial(Object.assign({color:c,roughness:r,metalness:m},o));
function caja(x,y,z,mat,px=0,py=0,pz=0){const m=new THREE.Mesh(new THREE.BoxGeometry(x,y,z),mat);m.position.set(px,py,pz);m.castShadow=m.receiveShadow=true;return m}
function cil(rt,rb,h,mat,seg=32){const m=new THREE.Mesh(new THREE.CylinderGeometry(rt,rb,h,seg),mat);m.castShadow=m.receiveShadow=true;return m}
// servo MG90D en su marco: eje +Z, cara de arriba del cuerpo en z=0, cuerpo hacia abajo, largo hacia +X
function servo(){
 const g=new THREE.Group();
 const cuerpo=M(0x3b2a1b,.35,.1,{transparent:true,opacity:.92}),negro=M(0x15161a,.5),metal=M(0xb8bcc4,.35,.9);
 g.add(caja(22.8,12.2,22.5,cuerpo,5.5,0,-11.25));
 g.add(caja(32.5,12.2,2.5,cuerpo,5.5,0,-5.75));
 const eje=cil(2.4,2.4,3.5,metal,24);eje.rotation.x=Math.PI/2;eje.position.set(0,0,1.75);g.add(eje);
 const cubo=cil(4.2,4.2,2,cuerpo,28);cubo.rotation.x=Math.PI/2;cubo.position.set(0,0,1);g.add(cubo);
 const brazo=caja(20,4,1.4,negro,8,0,2.6);g.add(brazo);
 const hub=cil(3.6,3.6,3.2,negro,24);hub.rotation.x=Math.PI/2;hub.position.set(0,0,2.1);g.add(hub);
 const et=new THREE.Mesh(new THREE.PlaneGeometry(11,6.5),new THREE.MeshBasicMaterial({color:0xc2188f}));et.position.set(5.5,6.12,-5);et.rotation.x=Math.PI/2;g.add(et);
 // cables naranja, rojo y marrón saliendo del extremo corto
 [[0xe8761b,-1.2],[0xc62828,0],[0x6d3a1f,1.2]].forEach(([c,dy])=>{
  const curva=new THREE.CatmullRomCurve3([new THREE.Vector3(-5.9,dy,-17),new THREE.Vector3(-12,dy,-19),new THREE.Vector3(-20,dy+3,-14),new THREE.Vector3(-26,dy+4,-20)]);
  const t=new THREE.Mesh(new THREE.TubeGeometry(curva,16,.55,6,false),M(c,.6));t.castShadow=true;g.add(t)});
 return g}
function camara(){ // CSI IMX219 (Raspberry Pi Camera Module 2): placa 25 x 23.862, lente cuadrado de 8.5 mm, mira a +X. Marco: centro de la placa
 const g=new THREE.Group();
 const pcb=caja(1,25,23.862,M(0x1f7a3a,.45),0,0,0);g.add(pcb);
 const aloj=caja(5,8.5,8.5,M(0x15161a,.45),3,0,2.569);g.add(aloj);
 const tubo=cil(3.4,3.4,4,M(0x0b0b0d,.4),28);tubo.rotation.z=Math.PI/2;tubo.position.set(7,0,2.569);g.add(tubo);
 const vidrio=cil(2.2,2.2,.3,M(0x222a44,.1,.2),24);vidrio.rotation.z=Math.PI/2;vidrio.position.set(9.1,0,2.569);g.add(vidrio);
 const conector=caja(2.5,20.8,3,M(0xe8e2cf,.5),-1.5,0,8.5);g.add(conector);
 const flex=caja(.4,16,40,M(0xd89a2b,.5),-2.5,0,28);flex.name='flex';g.add(flex);
 return g}
function luna(){ // TF-Luna: 35 de ancho con orejas (atrás), 26.5 de cuerpo, 21.25 de alto, 12 de fondo; lentes a +X. Marco: el plano de las orejas
 const g=new THREE.Group(),n=M(0x17181c,.5);
 g.add(caja(12,26.5,21.25,n,6,0,-1.6));            // cuerpo (su centro queda 1.6 mm bajo la altura de las orejas)
 g.add(caja(2,35,9,n,1,0,0));                      // orejas
 [-5.25,5.25].forEach(y=>{const l=cil(5.25,5.25,1.5,M(0x0d0e11,.35),32);l.rotation.z=Math.PI/2;l.position.set(12.75,y,0);g.add(l);
  const v=cil(3.6,3.6,.3,M(0x3a1d22,.1,.3),24);v.rotation.z=Math.PI/2;v.position.set(13.6,y,0);g.add(v)});
 return g}
function construir(){
 grupoMontaje=new THREE.Group();grupoMontaje.name='montaje';
 const g0=geom(MONTAJE_B64.asm_base),g1=geom(MONTAJE_B64.asm_plataforma),g2=geom(MONTAJE_B64.asm_cuna);window.gAncho=geom(MONTAJE_B64.asm_plataforma_ancho);window.gRegla=g1;
 mallaPlat=pla(g1);grupoMontaje.add(pla(g0),mallaPlat);
 // servo de pan (eje +Z en el origen)
 const sp=servo();sp.name='elec';grupoMontaje.add(sp);
 // servo de tilt: T(0,YA,Z_EJE) · Ry(180°) · Rx(−90°)
 const env=new THREE.Group();env.position.set(0,YA,Z_EJE);env.rotation.y=Math.PI;const st=servo();st.rotation.x=-Math.PI/2;env.add(st);env.name='elec';grupoMontaje.add(env);
 // cuna que gira con el tilt (marco con el eje en el origen)
 grupoCuna=new THREE.Group();grupoCuna.position.set(0,0,Z_EJE);grupoCuna.add(pla(g2));
 // placa frontal de la carga en x = 24 (cuna csi_luna): la CSI arriba (lente a z = +6) y el TF-Luna abajo (agujeros a z = -12.4)
 const lu=luna();lu.position.set(24,0,-12.4);lu.name='elec';grupoCuna.add(lu);
 const ca=camara();ca.position.set(24+3.5+.5,0,6-2.569);ca.name='elec';grupoCuna.add(ca);
 grupoMontaje.add(grupoCuna);
 grupoMontaje.position.set(0,0,0);esc.add(grupoMontaje);
 // placa del chasis del dron (solo de referencia): la base se atornilla a su cara de abajo
 chasis=caja(150,110,3,M(0x23262b,.35,.4),0,0,0);chasis.name='chasis';esc.add(chasis);
 orientar();
}
function orientar(){ // colgado = de cabeza bajo el chasis: el módulo se gira 180° sobre X y la base queda arriba
 grupoMontaje.rotation.x=colgado?Math.PI:0;
 chasis.visible=colgado&&modo==='montaje';chasis.position.z=colgado?27.9:-27.9-3;
 grupoCuna.rotation.y=(colgado?1:-1)*tilt*Math.PI/180;
}
const MONTAJE_B64={__MONTAJE_B64__};
function iniciar(){
 if(!window.THREE){info.textContent='No se pudo cargar three.js: hace falta internet para abrir esta página.';return}
 ren=new THREE.WebGLRenderer({canvas:cv,antialias:true});ren.shadowMap.enabled=true;ren.shadowMap.type=THREE.PCFSoftShadowMap;
 ren.toneMapping=THREE.ACESFilmicToneMapping;ren.toneMappingExposure=.82;ren.outputEncoding=THREE.sRGBEncoding;
 esc=new THREE.Scene();cam=new THREE.PerspectiveCamera(35,1,1,3000);
 esc.add(new THREE.HemisphereLight(0xffffff,0x8a93a6,.6));
 const k=new THREE.DirectionalLight(0xffffff,1.1);k.position.set(120,-160,260);k.castShadow=true;k.shadow.mapSize.set(2048,2048);
 const c=k.shadow.camera;c.left=-180;c.right=180;c.top=180;c.bottom=-180;c.near=10;c.far=800;esc.add(k);
 const r=new THREE.DirectionalLight(0xbfd4ff,.45);r.position.set(-200,120,90);esc.add(r);
 const suelo=new THREE.Mesh(new THREE.PlaneGeometry(1200,1200),new THREE.ShadowMaterial({opacity:.28}));suelo.position.z=-26.6;suelo.receiveShadow=true;esc.add(suelo);
 construir();
 modos();colores();extras();aplicarModo();ajustar();bucle();
}
function modos(){const d=document.getElementById('modos');d.innerHTML='';
 const mk=(t,f,on)=>{const b=document.createElement('button');b.textContent=t;b.onclick=f;if(on)b.classList.add('on');d.appendChild(b)};
 mk('Montaje completo',()=>{modo='montaje';aplicarModo();modos()},modo==='montaje');
 PIEZAS.forEach((p,i)=>mk(p.titulo,()=>{modo='pieza'+i;aplicarModo();modos()},modo==='pieza'+i))}
function colores(){const d=document.getElementById('color');d.innerHTML='<span>Color del PLA:</span>';
 Object.keys(COLORES).forEach(n=>{const b=document.createElement('button');b.innerHTML='<span class="sw" style="background:#'+COLORES[n].toString(16).padStart(6,'0')+'"></span>'+n;
  if(n===colorSel)b.classList.add('on');b.onclick=()=>{colorSel=n;piezasPLA.forEach(m=>m.material.color.setHex(COLORES[n]));colores()};d.appendChild(b)})}
function extras(){const d=document.getElementById('extra');d.innerHTML='';
 const a=document.createElement('button');a.textContent=auto?'Detener giro':'Girar solo';a.classList.toggle('on',auto);a.onclick=()=>{auto=!auto;extras()};d.appendChild(a);
 if(modo==='montaje'){
  const e=document.createElement('button');e.textContent=verElec?'Ocultar servos y sensores':'Mostrar servos y sensores';e.onclick=()=>{verElec=!verElec;setElec();extras()};d.appendChild(e);
  const c1=document.createElement('button');c1.textContent=colgado?'Módulo colgado (de cabeza) ✓':'Módulo hacia arriba';c1.classList.toggle('on',colgado);
  c1.onclick=()=>{colgado=!colgado;orientar();extras();dibujar()};d.appendChild(c1);
  const c2=document.createElement('button');c2.textContent=ancho?'Rango ancho (NO aprobado) ✓':'Rango de la regla (−45° a +15°)';c2.classList.toggle('on',ancho);
  c2.onclick=()=>{ancho=!ancho;mallaPlat.geometry=ancho?window.gAncho:window.gRegla;if(!ancho)tilt=Math.max(-44,Math.min(14,tilt));orientar();extras();dibujar()};d.appendChild(c2);
  const mn=ancho?-89:-44,mx=ancho?44:14;
  const l=document.createElement('label');l.innerHTML='Cabeceo del mundo (+ = mira arriba): <b id="tv">'+tilt+'</b>° <input type="range" min="'+mn+'" max="'+mx+'" step="1" value="'+tilt+'">';
  l.querySelector('input').oninput=ev=>{tilt=+ev.target.value;document.getElementById('tv').textContent=tilt;orientar();dibujar()};d.appendChild(l)}}
function setElec(){grupoMontaje.traverse(o=>{if(o.name==='elec')o.visible=verElec})}
function aplicarModo(){
 if(piezaMalla){esc.remove(piezaMalla);piezasPLA.splice(piezasPLA.indexOf(piezaMalla),1);piezaMalla.geometry.dispose();piezaMalla=null}
 grupoMontaje.visible=(modo==='montaje');if(chasis)chasis.visible=colgado&&modo==='montaje';extras();
 if(modo==='montaje'){mira.set(0,0,colgado?-18:12);dist=colgado?330:250;rot={x:colgado?-0.25:-0.5,z:0.8};setElec();
  info.innerHTML='<b>Montaje completo</b> (pan-tilt de la variante H): base, plataforma con el servo de giro, mejillas con el servo de subir-bajar y cuna con la CSI IMX219 y el TF-Luna. Eje X hacia adelante.'}
 else{const i=+modo.slice(5),p=PIEZAS[i],g=geom(p.b64),bb=g.boundingBox,c=new THREE.Vector3(),s=new THREE.Vector3();bb.getCenter(c);bb.getSize(s);
  g.translate(-c.x,-c.y,-c.z);piezaMalla=pla(g);piezaMalla.position.z=0;esc.add(piezaMalla);mira.set(0,0,0);dist=Math.max(s.x,s.y,s.z)*2.6;rot={x:-0.6,z:0.7};
  info.innerHTML='<b>'+p.titulo+'</b><br>Tamaño: '+s.x.toFixed(1)+' × '+s.y.toFixed(1)+' × '+s.z.toFixed(1)+' mm.'}
 dibujar()}
function ajustar(){const w=cv.clientWidth,h=cv.clientHeight;ren.setPixelRatio(window.devicePixelRatio||1);ren.setSize(w,h,false);cam.aspect=w/h;cam.updateProjectionMatrix();dibujar()}
function dibujar(){const cx=Math.cos(rot.x),sx=Math.sin(rot.x);
 cam.position.set(mira.x-dist*cx*Math.sin(rot.z),mira.y-dist*cx*Math.cos(rot.z),mira.z-dist*sx);cam.up.set(0,0,1);cam.lookAt(mira);ren.render(esc,cam)}
function bucle(){if(auto&&!ar){rot.z+=0.006;dibujar()}requestAnimationFrame(bucle)}
let ar=null;
cv.addEventListener('pointerdown',e=>{ar={x:e.clientX,y:e.clientY,sh:e.shiftKey};cv.setPointerCapture(e.pointerId)});
cv.addEventListener('pointerup',()=>ar=null);
cv.addEventListener('pointermove',e=>{if(!ar)return;const dx=e.clientX-ar.x,dy=e.clientY-ar.y;ar.x=e.clientX;ar.y=e.clientY;
 if(ar.sh||e.buttons===2){mira.z+=dy*dist*0.002;mira.x-=dx*dist*0.002*Math.cos(rot.z);mira.y+=dx*dist*0.002*Math.sin(rot.z)}else{rot.z-=dx*0.01;rot.x=Math.max(-1.5,Math.min(1.5,rot.x+dy*0.01))}dibujar()});
cv.addEventListener('wheel',e=>{e.preventDefault();dist*=e.deltaY>0?1.1:0.9;dibujar()},{passive:false});
cv.addEventListener('contextmenu',e=>e.preventDefault());
window.addEventListener('resize',()=>ren&&ajustar());
iniciar();
</script></body></html>'''


def main():
    piezas = [{"id": n, "titulo": t, "b64": binario(n)} for n, t in PIEZAS]
    montaje = ",".join(f'"{n}":"{binario(n)}"' for n in MONTAJE)
    html = (PLANTILLA.replace("__PIEZAS__", json.dumps(piezas)).replace("__MONTAJE__", json.dumps(MONTAJE))
            .replace("__MONTAJE_B64__", montaje))
    out = os.path.join(AQUI, "VISTA_3D.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(out, os.path.getsize(out) // 1024, "KB")


if __name__ == "__main__":
    main()
