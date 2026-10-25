import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { buildTransport } from '../src/world/transport.js';
import { nearestOnSegment, moveWithGuards } from '../src/sim/walkways.js';

const fixture=()=>buildTransport({name:'home',group:new THREE.Group()},()=>new THREE.Group());
test('transport stays home, bounded north train, low material batches and no extra lights',()=>{
 const s=fixture();let meshes=0,triangles=0,lights=0;
 s.group.traverse(o=>{if(o.isMesh){meshes++;triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;}if(o.isLight)lights++;});
 assert.ok(meshes<=25,`meshes ${meshes}`);assert.ok(triangles<16000,`triangles ${triangles}`);assert.equal(lights,0);
 assert.ok(s.colliders.some(c=>c.name==='station-platform'));assert.ok(s.interactives.length === 2);
 for(let time=0;time<150;time+=.1){s.update(time);const [x0,z0,x1,z1]=s.plan.rail.exclusion;assert.ok(s.train.position.x-1.25>x0+.4&&s.train.position.x+1.25<x1-.4);assert.ok(s.train.position.z-.4>z0&&s.train.position.z+.4<z1);}
 assert.throws(()=>buildTransport({name:'tree'}),/only/);
});
test('all visible island safety segments block either direction and southern shared gate has no fence',()=>{
 const s=fixture();assert.ok(s.edgeBarriers.length>=14);
 for(const wall of s.edgeBarriers){const dx=wall.b.x-wall.a.x,dz=wall.b.z-wall.a.z,len=Math.hypot(dx,dz);if(len<.01)continue;
 for(const sign of [-1,1]){const nx=-dz/len*sign,nz=dx/len*sign,p={x:(wall.a.x+wall.b.x)/2+nx,y:0,z:(wall.a.z+wall.b.z)/2+nz};moveWithGuards(p,-2*nx,-2*nz,[wall]);const q=nearestOnSegment(p,wall.a,wall.b);assert.ok(Math.hypot(p.x-q.x,p.z-q.z)>.4099);}}
 for(const p of [{x:0,z:3.5},{x:-1.7,z:8.3},{x:.63,z:8.1},{x:-.5,z:8.4}])for(const w of s.barriers){const q=nearestOnSegment(p,w.a,w.b);assert.ok(Math.hypot(p.x-q.x,p.z-q.z)>.42,`blocked spawn / shared gate ${JSON.stringify(p)}`);}
});
test('NPC reservation, interaction stop and approach stay outside physical solids',()=>{
 const s=fixture(),r=s.plan.npcReservation;
 for(const xyz of [r.position,r.playerStop])for(const w of s.barriers){const p={x:xyz[0],z:xyz[2]},q=nearestOnSegment(p,w.a,w.b);assert.ok(Math.hypot(p.x-q.x,p.z-q.z)>.8);}
 assert.equal(r.implemented,false);assert.equal(r.facingYaw,0);assert.ok(r.interactionRadius>=1.3);

});

test('full 4.8-wide home approaches keep a 3.9-wide player-centre band unobstructed',async()=>{
 const {default:layout}=await import('../src/data/yuan-layout.json',{with:{type:'json'}});const s=fixture();let probes=0;
 for(const path of layout.paths.filter(p=>p.from==='F'||p.to==='F')){
 const points=path.from==='F'?path.points:[...path.points].reverse();
 for(let i=0;i<points.length-1;i++){
 const a=points[i],b=points[i+1],len=Math.hypot(b.x-a.x,b.z-a.z);if(Math.hypot(a.x,a.z)>10)continue;
 for(const offset of [-1.95,0,1.95])for(const t of [0,.5,1]){
 const p={x:a.x+(b.x-a.x)*t-(b.z-a.z)/len*offset,z:a.z+(b.z-a.z)*t+(b.x-a.x)/len*offset};
 for(const w of s.barriers){const q=nearestOnSegment(p,w.a,w.b);assert.ok(Math.hypot(p.x-q.x,p.z-q.z)>.41,`${path.id} blocked by ${w.kind} at ${JSON.stringify(p)}`);}probes++;
 }}}
 assert.ok(probes>100);
});

test('every actual home structure, column, culture base, viewing seat and rail blocks swept crossing',()=>{
 const scene=fixture();let probes=0;
 for(const wall of scene.barriers){const dx=wall.b.x-wall.a.x,dz=wall.b.z-wall.a.z,length=Math.hypot(dx,dz);if(length<.0001)continue;
 for(const side of [-1,1]){const nx=-dz/length*side,nz=dx/length*side,mx=(wall.a.x+wall.b.x)/2,mz=(wall.a.z+wall.b.z)/2,p={x:mx+nx,y:.05,z:mz+nz};
  assert.equal(moveWithGuards(p,-2*nx,-2*nz,[wall]),true);assert.ok((p.x-mx)*nx+(p.z-mz)*nz>=.4099,`${wall.kind}: crossed actual obstacle`);probes++;}}
 assert.ok(probes>100);
});

test('compound facade collision protects the actual front and side woven surfaces, not only the cream wall',()=>{
 const s=fixture();s.group.updateMatrixWorld(true);
 for(const [start,direction]of [[new THREE.Vector3(-3.56,1.3,-2.5),new THREE.Vector3(0,0,-1)],[new THREE.Vector3(-5.8,1.3,-4.35),new THREE.Vector3(1,0,0)]]){
  const hit=new THREE.Raycaster(start,direction).intersectObjects(s.colliders,false)[0];assert.ok(hit,'actual facade visible');
  const p={x:start.x,y:.05,z:start.z};moveWithGuards(p,direction.x*4,direction.z*4,s.barriers);
  const forward=(hit.point.x-p.x)*direction.x+(hit.point.z-p.z)*direction.z;
  assert.ok(forward>=.33,`capsule intersects visible facade: ${forward}`);
 }
});
