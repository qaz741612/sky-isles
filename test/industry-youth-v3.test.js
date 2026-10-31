import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {buildIndustryYouth} from '../src/world/industry-youth.js';
import {Player} from '../src/sim/player.js';
import {ISLANDS} from '../src/world/islands.js';
import {guardIndex} from '../src/sim/walkways.js';
import locks from '../docs/design/industry-youth-island-c-v3/locked-runtime-baseline.json' with {type:'json'};
test('V3 preserves original land, 22 roads, NPC, other approved assets and player code',()=>{
 for(const f of locks.files)assert.equal(crypto.createHash('sha256').update(fs.readFileSync(f.path)).digest('hex'),f.sha256,f.path);
});
test('falling Player rests on actual visible workshop/PV, youth roofs and greenhouse arch',async()=>{
 const b=fs.readFileSync('public/models/industry-youth-c/industry-youth-c.glb'),g=await new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'');
 const scene=new THREE.Scene(),group=new THREE.Group();group.position.set(-20.358,0,38.610);scene.add(group);const built=buildIndustryYouth(g.scene,{group,pos:group.position}),p=new Player(scene,new THREE.PerspectiveCamera(),built.colliders);
 p.navigation={islands:ISLANDS,barriers:built.barriers,nearby:guardIndex(built.barriers)};p.ceilingConstraint=built.constrainHead;scene.updateMatrixWorld(true);
 for(const[x,z]of[[6.8,.6],[-9.5,-.5],[-9.8,2.7],[6,7]]){
  const ray=new THREE.Raycaster(new THREE.Vector3(x-20.358,12,z+38.610),new THREE.Vector3(0,-1,0)),visible=ray.intersectObjects(built.meshes,false)[0];assert.ok(visible,'visible roof absent');
  p.teleport(x-20.358,visible.point.y+1,z+38.610);for(let i=0;i<180;i++)p.update(1/60,{x:0,z:0,jumpPressed:false,jumpHeld:false},i/60);
  assert.ok(p.move.grounded);assert.ok(Math.abs(p.pos.y-visible.point.y)<.04,`visible roof at ${x},${z}: ${visible.point.y} vs ${p.pos.y}`);assert.equal(p.respawnCount,0);
 }
});
test('actual V3 GLB has two substantial closed architectural silhouettes and a distinct arch greenhouse',async()=>{
 const b=fs.readFileSync('public/models/industry-youth-c/industry-youth-c.glb'),g=await new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'');g.scene.updateMatrixWorld(true);
 const terrainPoints=new Set();g.scene.traverse(o=>{if(!o.isMesh||!o.name.startsWith('00_TerrainAndPlaza'))return;const p=o.geometry.attributes.position;for(let i=0;i<p.count;i++){const v=new THREE.Vector3().fromBufferAttribute(p,i).applyMatrix4(o.matrixWorld);terrainPoints.add(v.toArray().map(x=>Math.round(x*1e5)||0).join(','));}});
 assert.equal(crypto.createHash('sha256').update([...terrainPoints].sort().join(';')).digest('hex'),locks.terrainVertexSignature.base.sha256,'original PR17 terrain/plaza visible geometry changed');
 function group(prefix){const box=new THREE.Box3();let count=0;g.scene.traverse(o=>{if(o.isMesh&&o.name.startsWith(prefix)){box.union(new THREE.Box3().setFromObject(o,true));count++;}});assert.ok(count>3,prefix);return box.getSize(new THREE.Vector3());}
 const w=group('01_Workshop'),y=group('03_Exhibition'),h=group('02_Greenhouse');assert.ok(w.y>6.5&&w.x>8);assert.ok(y.y>5.5&&y.x>7);assert.ok(h.y>3.8&&h.x>5.9);
 const roofs=[];g.scene.traverse(o=>{if(o.isMesh&&o.name.startsWith('03_Exhibition')&&o.name.includes('roof')){const p=o.geometry.attributes.position;for(let i=0;i<p.count;i++)roofs.push(p.getY(i));}});
 assert.ok(roofs.some(y=>y>5.6)&&roofs.some(y=>y<5.1),'youth roofs must show a real height step');
});

test('C V3 covered approaches retain a clear camera ray through full user orbit',async()=>{
 const {worldCameraConstraint}=await import('../src/sim/camera-clearance.js');
 const {industryCameraConstraint}=await import('../src/world/industry-youth.js');
 const bytes=fs.readFileSync('public/models/industry-youth-c/industry-youth-c.glb');
 const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
 const group=new THREE.Group();group.position.set(-20.358,0,38.610);const built=buildIndustryYouth(gltf.scene,{group,pos:group.position});group.updateMatrixWorld(true,true);
 const orbit={yaw:0,pitch:.67,dist:22},constrain=industryCameraConstraint(worldCameraConstraint(built.cameraObstacles),{pos:group.position},()=>orbit),ray=new THREE.Raycaster();
 for(const [x,z] of [[4.9,-1.05],[-5.3,-.55],[6,9.8],[.5,6.95]]){
  const target=new THREE.Vector3(x-20.358,1.4,z+38.610),camera=target.clone().add(new THREE.Vector3(0,10,16));
  for(let j=0;j<8;j++){orbit.yaw=j*Math.PI/4;const saved={...orbit},desired=target.clone().add(new THREE.Vector3(Math.sin(orbit.yaw)*Math.cos(orbit.pitch)*22,Math.sin(orbit.pitch)*22,Math.cos(orbit.yaw)*Math.cos(orbit.pitch)*22));
   for(let k=0;k<90;k++){camera.lerp(desired,8/60);constrain(target,camera);}
   assert.ok(camera.distanceTo(target)>2.7,`camera trapped ${x},${z}, yaw ${orbit.yaw}`);
   ray.set(target,camera.clone().sub(target).normalize());ray.far=target.distanceTo(camera)-.03;assert.equal(ray.intersectObjects(built.cameraObstacles,false).length,0,'camera ray crosses structure');assert.deepEqual(orbit,saved);
  }
 }
});
