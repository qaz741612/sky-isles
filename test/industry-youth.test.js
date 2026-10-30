import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from 'three';
import polygon from 'polygon-clipping';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {buildIndustryYouth,industryCameraConstraint} from '../src/world/industry-youth.js';
import {worldCameraConstraint} from '../src/sim/camera-clearance.js';
import {moveWithGuards} from '../src/sim/walkways.js';
import plan from '../src/data/industry-youth-plan.json' with {type:'json'};
import collision from '../src/data/industry-youth-collision.json' with {type:'json'};
import layout from '../src/data/yuan-layout.json' with {type:'json'};
import surface from '../src/data/yuan-surface.json' with {type:'json'};

const area=mp=>mp.reduce((a,rings)=>a+rings.reduce((n,r,i)=>n+(i===0?1:-1)*Math.abs(r.reduce((s,p,j)=>{const q=r[(j+1)%r.length];return s+p[0]*q[1]-p[1]*q[0];},0)/2),0),0);
const closed=r=>[...r,r[0]];
test('C exact route core, NPC 3x3 and original mushroom stay unobstructed',()=>{
 assert.deepEqual(plan.centre,[-20.358,0,38.610]);assert.deepEqual(plan.entrances,['S14','S15','S16']);
 const core=surface.islandPaving.find(p=>p.island==='koi').domain.map(rings=>rings.map(r=>r.map(([x,z])=>[x-plan.centre[0],z-plan.centre[2]])));
 const npc=plan.npc[0],x=npc.position[0],z=npc.position[2],reserved=[[[x-1.5,z-1.5],[x+1.5,z-1.5],[x+1.5,z+1.5],[x-1.5,z+1.5],[x-1.5,z-1.5]]];
 assert.ok(area(polygon.difference(reserved,[closed(plan.footprintLocal)]))<1e-5);
 for(const s of collision.solids){if(s.base>1.6||s.top<.25)continue;const region=[closed(s.polygon)];assert.ok(area(polygon.intersection(core,region))<.0001,'road blocked by '+s.name);assert.ok(area(polygon.intersection(reserved,region))<.0001,'NPC blocked by '+s.name);}
 assert.equal(npc.implemented,false);assert.equal(layout.paths.length,22);
 assert.ok(Math.hypot(npc.playerStop[0]-x,npc.playerStop[2]-z)<=npc.interactionRadius,'future player stop outside interaction reach');
});
test('C actual GLB is valid, floor is real, walls and visible outer guard have blocking data',async()=>{
 const b=fs.readFileSync('public/models/industry-youth-c/industry-youth-c.glb'),gltf=await new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'');
 const scene=new THREE.Scene(),group=new THREE.Group();group.position.set(...plan.centre);scene.add(group);const built=buildIndustryYouth(gltf.scene,{group,pos:group.position});scene.updateMatrixWorld(true);
 assert.ok(built.stats.triangles>30000&&built.stats.triangles<100000);assert.ok(built.stats.runtimeMeshes<100);assert.ok(built.stats.materials>=20);
 assert.ok(built.meshes.every(m=>m.material&&m.geometry.attributes.position.array.every(Number.isFinite)));
 const ray=new THREE.Raycaster();let floorSamples=0;for(const[x,z]of [[0,0],[3.5,0],[.5,8.35],[-6.5,-6.1],[5.6,-6.9],[-5.1,7.3],[-8.5,2.7],[3.7,7.04]]){
  ray.set(new THREE.Vector3(x+plan.centre[0],1,z+plan.centre[2]),new THREE.Vector3(0,-1,0));ray.far=1.5;const hits=ray.intersectObjects(built.colliders);assert.ok(hits.length,'floor gap '+x+','+z);floorSamples++;
 }
 assert.equal(floorSamples,8);assert.ok(built.colliders.filter(m=>m.name==='C-dry-ground').every(m=>!m.userData.noCheckpoint));assert.ok(built.colliders.filter(m=>m.name==='C-solid-top').every(m=>m.userData.noCheckpoint));
 const orbit={yaw:.12,pitch:.67,dist:22},saved={...orbit},constrain=industryCameraConstraint(worldCameraConstraint(built.cameraObstacles),{pos:group.position},()=>orbit),target=new THREE.Vector3(plan.centre[0]+3.8,1.5,plan.centre[2]);
 for(let frame=0;frame<120;frame++){const pos=new THREE.Vector3(target.x+Math.sin(orbit.yaw)*Math.cos(orbit.pitch)*orbit.dist,target.y+Math.sin(orbit.pitch)*orbit.dist,target.z+Math.cos(orbit.yaw)*Math.cos(orbit.pitch)*orbit.dist);constrain(target,pos);assert.ok(pos.distanceTo(target)>4,'porch camera too close');}
 assert.deepEqual(orbit,saved,'avoidance changed orbit/zoom state');
 for(const wall of [...built.barriers,...surface.barriers.filter(w=>w.island==='koi')]){
  if(wall.a.y>1.5)continue;const dx=wall.b.x-wall.a.x,dz=wall.b.z-wall.a.z,d=Math.hypot(dx,dz);if(d<.015)continue;
  const p={x:(wall.a.x+wall.b.x)/2-dz/d,y:Math.max(0,wall.a.y),z:(wall.a.z+wall.b.z)/2+dx/d};assert.equal(moveWithGuards(p,2*dz/d,-2*dx/d,[wall]),true,'nonblocking '+wall.source);
 }
});
