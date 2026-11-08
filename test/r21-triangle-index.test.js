import{test}from'node:test';import assert from'node:assert/strict';import fs from'node:fs';import*as T from'three';
import{worldCameraConstraint}from'../src/sim/camera-clearance.js';import{triangleCameraConstraint}from'../src/sim/r21-triangle-index.js';
function compare(meshes,rays){
 const native=worldCameraConstraint(meshes),indexed=triangleCameraConstraint(meshes);assert.equal(indexed.stats.acceleration,'static-triangle-grid');
 for(const[start,end]of rays){const target=new T.Vector3(...start),saved=target.clone(),a=new T.Vector3(...end),b=a.clone(),old=native(target,a),fast=indexed(target,b);assert.equal(fast,old,JSON.stringify({start,end}));assert.ok(a.distanceTo(b)<1e-6,JSON.stringify({native:a.toArray(),indexed:b.toArray()}));assert.deepEqual(target,saved);}
}
test('local triangle camera matches native rays through transformed, grouped, mirrored and instanced geometry',()=>{
 const materials=[new T.MeshBasicMaterial({side:T.FrontSide}),new T.MeshBasicMaterial({side:T.BackSide}),new T.MeshBasicMaterial({side:T.DoubleSide})],meshes=[];
 for(let i=0;i<3;i++){const m=new T.Mesh(new T.BoxGeometry(2,4,1),i===0?[...materials,...materials]:materials[i]);m.position.set(i*3-3,2,i-1);m.rotation.set(.1*i,.37*i,.08);m.scale.set(i===1?-1.4:1.3,.7+i*.1,1.2);m.updateMatrixWorld(true);meshes.push(m);}
 const instanced=new T.InstancedMesh(new T.BoxGeometry(.8,2,.6),materials[2],2);instanced.setMatrixAt(0,new T.Matrix4().makeTranslation(6,1,-3));instanced.setMatrixAt(1,new T.Matrix4().makeTranslation(-6,1,3));instanced.updateMatrixWorld(true);meshes.push(instanced);
 let seed=731;const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};const rays=[];
 for(let i=0;i<700;i++)rays.push([[random()*20-10,random()*6+.1,random()*20-10],[random()*20-10,random()*6+.1,random()*20-10]]);
 for(const x of[-9,-6,-3,0,3,6,9])for(const z of[-6,-3,0,3,6])rays.push([[x,7,z],[x,-1,z]]);
 compare(meshes,rays);
});
test('local triangle camera matches native rays against the four actual architectural shells and tree crowns',()=>{
 const plan=JSON.parse(fs.readFileSync('src/data/bdeh-plan.json')),canopies=JSON.parse(fs.readFileSync('src/data/bdeh-camera-canopies.json')),meshes=[],material=new T.MeshBasicMaterial({side:T.DoubleSide}),rays=[];
 for(const code of'BDEH'){
  const data=JSON.parse(fs.readFileSync(`src/data/bdeh-${code.toLowerCase()}-collision.json`)),c=plan.islands[code].centre;
  for(const positions of[data.cameraPositions,...canopies.islands[code].canopies.map(p=>p.positions)]){const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(positions,3));const m=new T.Mesh(g,material);m.position.set(...c);m.updateMatrixWorld(true);meshes.push(m);}
  for(let i=0;i<48;i++){const yaw=i*Math.PI*2/48+.137,elevation=.15+(i%5)*.21;for(const h of[.75,1.5])rays.push([[c[0],h,c[2]],[c[0]+Math.sin(yaw)*Math.cos(elevation)*22,h+Math.sin(elevation)*22,c[2]+Math.cos(yaw)*Math.cos(elevation)*22]]);}
 }
 compare(meshes,rays);
});
