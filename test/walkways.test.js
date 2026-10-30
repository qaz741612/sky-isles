import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { ISLANDS } from '../src/world/islands.js';
import { buildBridges } from '../src/world/bridges.js';
import { buildPolicyScenery } from '../src/world/policy-scenery.js';
import { guardIndex } from '../src/sim/walkways.js';
import { buildTransport } from './helpers/elevated-fixture.js';
import {buildFloodControl} from '../src/world/flood-control.js';
import {buildIndustryYouth} from '../src/world/industry-youth.js';
import { Player } from '../src/sim/player.js';
import { WALKWAY, planWalkways, moveWithGuards, nearestOnSegment } from '../src/sim/walkways.js';
import { walkTour } from './helpers/walk-tour.js';
import { createMoveState, stepHorizontal } from '../src/sim/movement.js';

function fixture() {
  const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera();
  const colliders=[],islands=ISLANDS.map(d=> {
    const grass=new THREE.Mesh(new THREE.CylinderGeometry(d.r,d.r*0.9,1.1,28),new THREE.MeshBasicMaterial());
    grass.position.set(d.x,d.y-0.55,d.z);grass.userData.island=d.name;scene.add(grass);if(d.name!=='crystal'&&d.name!=='koi')colliders.push(grass);
    const group=new THREE.Group();group.position.set(d.x,d.y,d.z);scene.add(group);
    return { name:d.name,r:d.r,pos:new THREE.Vector3(d.x,d.y,d.z),group };
  });
  const bridges=buildBridges(scene,islands);
  const trafficHome={name:'home',group:new THREE.Group()};scene.add(trafficHome.group);
  const transport=buildTransport(trafficHome,()=>new THREE.Group());
  const flood=buildFloodControl(new THREE.Group(),islands.find(i=>i.name==='crystal'));
  const industry=buildIndustryYouth(new THREE.Group(),islands.find(i=>i.name==='koi'));
  const scenery=buildPolicyScenery(islands,{crystal:flood,koi:industry});
  const barriers=[...bridges.barriers,...scenery.barriers,...transport.barriers];
  const player=new Player(scene,camera,[...colliders,...bridges.colliders,...transport.colliders,...scenery.colliders]);
  player.orbit.yaw=0;player.navigation={islands:ISLANDS,barriers,nearby:guardIndex(barriers)};
  scene.updateMatrixWorld(true);
  return {scene,player,bridges};
}

test('approved handwritten graph has 21 connected nodes, 22 real paths and eight distinct islands',()=>{
 const plans=planWalkways(),seen=new Set(['F']);
 for(let i=0;i<21;i++)for(const p of plans)if(seen.has(p.from)||seen.has(p.to)){seen.add(p.from);seen.add(p.to);}
 assert.equal(plans.length,22);assert.equal(seen.size,21);assert.equal(ISLANDS.length,8);assert.equal(WALKWAY.width,4.8);
 for(const plan of plans)assert.ok(plan.points.length>2);
});

for(const dt of [1/60,.05])test(`actual Player walks every route in both directions without jumping dt=${dt}`,()=>{
 const {player,bridges}=fixture();let time=0;const seen=new Set(['F']);
 const step=(x,z)=>player.update(dt,{x,z,jumpPressed:false,jumpHeld:false},time+=dt);
 player.teleport(0,.1,0);for(let i=0;i<30;i++)step(0,0);
 for(const leg of walkTour(bridges.plans)){
  for(const target of leg.points){let limit=600;while(Math.hypot(target.x-player.pos.x,target.z-player.pos.z)>.24&&limit-->0){const dx=target.x-player.pos.x,dz=target.z-player.pos.z,d=Math.hypot(dx,dz);step(dx/d,dz/d);assert.ok(player.move.grounded,`airborne ${leg.to}`);assert.equal(player.respawnCount,0);}
   assert.ok(limit>0,`stuck ${leg.to}`);
  }
  for(let i=0;i<30;i++)step(0,0);seen.add(leg.to);
 }
 assert.equal(seen.size,21);
});

test('guards prevent high-speed horizontal crossing from either side, including endpoints', () => {
  const wall={a:{x:0,y:0,z:-5},b:{x:0,y:2,z:5},height:1.3};
  for(const sign of [-1,1]) {
    const p={x:sign*2,y:1,z:0};
    moveWithGuards(p,-sign*6,0,[wall]);
    assert.ok(p.x*sign>=WALKWAY.playerRadius+WALKWAY.railThickness/2-1e-4);
  }
  const {player,bridges}=fixture();
  const plan=bridges.plans[0],target=plan.points[2];
  player.teleport(target.x,target.y+0.1,target.z);
  for(let i=0;i<60;i++)player.update(1/60,{x:0,z:0,jumpPressed:false,jumpHeld:false},i/60);
  const checkpoint=player.lastGrounded.clone();
  assert.ok(checkpoint.distanceTo(new THREE.Vector3(target.x,target.y,target.z))<0.2);
  player.teleport(100,-50,100);
  player.update(1/60,{x:0,z:0,jumpPressed:false,jumpHeld:false},2);
  assert.ok(player.pos.distanceTo(checkpoint)<0.6);
  assert.ok(player.pos.distanceTo(new THREE.Vector3(0,0,3.5))>5);
  assert.ok(bridges.barriers.every(w=>Number.isFinite(nearestOnSegment(checkpoint,w.a,w.b).y)));
});

test('released stick decelerates to rest quickly, with a bounded stopping distance', () => {
  const m=createMoveState();m.vx=6.2;let distance=0;
  for(let i=0;i<60;i++){stepHorizontal(m,0,0,1/60);distance+=Math.hypot(m.vx,m.vz)/60;}
  assert.equal(m.vx,0);assert.equal(m.vz,0);assert.ok(distance<0.5);
});

test('every actual outer rail blocks crossing and matches rendered guard coordinates',()=>{
 const {bridges}=fixture();
 for(const w of bridges.barriers){const dx=w.b.x-w.a.x,dz=w.b.z-w.a.z,d=Math.hypot(dx,dz);if(d<.05)continue;
  for(const side of [-1,1]){const nx=-dz/d*side,nz=dx/d*side,p={x:(w.a.x+w.b.x)/2+nx,y:0,z:(w.a.z+w.b.z)/2+nz};
   moveWithGuards(p,-nx*2,-nz*2,[w]);const q=nearestOnSegment(p,w.a,w.b);assert.ok(Math.hypot(p.x-q.x,p.z-q.z)>=WALKWAY.playerRadius+(w.thickness??WALKWAY.railThickness)/2-1e-4);}
 }
});

test('all actual collision triangles have finite horizontal surfaces and <=10% grade',()=>{
 const {bridges}=fixture();let count=0;
 for(const mesh of bridges.colliders){const p=mesh.geometry.attributes.position,index=mesh.geometry.index;
  for(let i=0;i<index.count;i+=3){const a=new THREE.Vector3().fromBufferAttribute(p,index.getX(i)),b=new THREE.Vector3().fromBufferAttribute(p,index.getX(i+1)),c=new THREE.Vector3().fromBufferAttribute(p,index.getX(i+2)),n=b.sub(a).cross(c.sub(a));
   assert.ok(Math.abs(n.y)>1e-10);assert.ok(Number.isFinite(n.y));assert.ok(Math.hypot(n.x,n.z)/Math.abs(n.y)<=.1);count++;
  }
 }
 assert.ok(count>1000);
});

test('near-zero X movement never falls through a cylinder cap triangle seam',()=>{
 const {player}=fixture();player.teleport(-3e-16,.1,3.5);
 for(let i=0;i<30;i++)player.update(1/60,{x:0,z:0,jumpHeld:false,jumpPressed:false},i/60);
 for(let i=0;i<80;i++){player.update(1/60,{x:1e-17,z:-.8,jumpHeld:false,jumpPressed:false},i/60);assert.ok(player.move.grounded,`cap seam at ${JSON.stringify(player.pos)}`);}
});


test('every ordered junction turn stays walkable with actual transport decks present',()=>{
 const {player,bridges}=fixture();player.orbit.yaw=0;let time=0,turns=0;
 const zero={x:0,z:0,jumpPressed:false,jumpHeld:false};
 const walk=points=>{for(const t of points){let remaining=500;while(Math.hypot(t.x-player.pos.x,t.z-player.pos.z)>.23&&remaining-->0){const dx=t.x-player.pos.x,dz=t.z-player.pos.z,d=Math.hypot(dx,dz);player.update(1/60,{...zero,x:dx/d,z:dz/d},time+=1/60);assert.ok(player.move.grounded,`junction gap ${JSON.stringify(t)}`);}assert.ok(remaining>0,'blocked junction turn');}for(let i=0;i<30;i++)player.update(1/60,zero,time+=1/60);};
 for(const node of bridges.nodes){const ports=bridges.plans.filter(p=>p.from===node.id||p.to===node.id).map(p=>(p.from===node.id?p.points:[...p.points].reverse()).slice(0,12));
 if(ports.length<2)continue;
 for(const incoming of ports)for(const outgoing of ports)if(incoming!==outgoing){
  const a=incoming.at(-1);player.teleport(a.x,a.y+.1,a.z);for(let i=0;i<30;i++)player.update(1/60,zero,time+=1/60);
  walk([...incoming].reverse());walk(outgoing);assert.equal(player.respawnCount,0);turns++;
 }
 }
 assert.ok(turns>=60,`ordered port turns: ${turns}`);
});

test('all six covered policy places support an actual falling Player; the open park pergola has no fake roof',()=>{
 const {scene,player}=fixture(),roofs=new Map();
 scene.traverse(mesh=>{if(mesh.userData.support==='roof'&&mesh.userData.island!=='home'&&!roofs.has(mesh.userData.island))roofs.set(mesh.userData.island,mesh);});
 assert.deepEqual([...roofs.keys()].sort(),['tree','temple','koi','windmill','crystal','lookout'].sort());
 for(const[name,mesh]of roofs){const box=new THREE.Box3().setFromObject(mesh),centre=box.getCenter(new THREE.Vector3()),ray=new THREE.Raycaster(new THREE.Vector3(centre.x,box.max.y+2,centre.z),new THREE.Vector3(0,-1,0));const expected=ray.intersectObject(mesh,false)[0];assert.ok(expected,name);player.teleport(centre.x,expected.point.y+1,centre.z);
 for(let i=0;i<180;i++)player.update(1/60,{x:0,z:0,jumpHeld:false,jumpPressed:false},i/60);
 assert.ok(player.move.grounded,name);assert.ok(Math.abs(player.pos.y-expected.point.y)<.04,`${name} roof support`);assert.equal(player.respawnCount,0);
 }
});
