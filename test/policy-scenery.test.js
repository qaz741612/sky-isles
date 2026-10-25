import {test} from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import {buildPolicyScenery,THEMES,PLACE_PLAN} from '../src/world/policy-scenery.js';
import {ISLANDS} from '../src/world/islands.js';
import {buildTransport} from './helpers/station-fixture.js';
import layout from '../src/data/yuan-layout.json' with {type:'json'};
import surface from '../src/data/yuan-surface.json' with {type:'json'};
import {moveWithGuards,nearestOnSegment} from '../src/sim/walkways.js';
const fixture=()=>{const islands=ISLANDS.map(i=>({...i,pos:new THREE.Vector3(i.x,i.y,i.z),group:new THREE.Group()}));return{islands,s:buildPolicyScenery(islands),h:buildTransport(islands[0],()=>new THREE.Group())};};
test('seven distinct authored places use bounded material batches, explicit solids and no decoration ground colliders',()=>{
 const{islands,s}=fixture();assert.equal(s.groups.length,7);assert.equal(islands[0].group.children.length,1); // transport fixture only
 assert.equal(new Set(s.layouts.map(l=>l.kind)).size,7);assert.ok(s.colliders.length>10);assert.ok(s.colliders.every(m=>['roof','solid','walkable-platform'].includes(m.userData.support)),'only explicit structural support/crossing, no decorative batches as ground');
 for(const group of s.groups){assert.deepEqual(group.userData.theme,THEMES[group.name.replace('policy-place-','')]);const visible=group.children.filter(c=>c.visible);assert.ok(visible.length<=15);group.traverse(o=>{assert.ok(!o.isLight);if(o.isMesh){assert.ok(!o.material.map||o.name==='shared-procedural-contact-shade');assert.ok(o.geometry.attributes.position.array.every(Number.isFinite));}});}
 for(const mesh of s.cameraObstacles)assert.equal(mesh.visible,false);
 for(const w of s.barriers){const dx=w.b.x-w.a.x,dz=w.b.z-w.a.z,d=Math.hypot(dx,dz);if(d<1e-6)continue;const p={x:(w.a.x+w.b.x)/2-dz/d,y:0,z:(w.a.z+w.b.z)/2+dx/d};moveWithGuards(p,dz/d*2,-dx/d*2,[w]);assert.ok((p.x-w.a.x)*(-dz/d)+(p.z-w.a.z)*dx/d>=.4099);}
});
test('all scenery preserves the 3.9-wide player-centre corridor along every fixed B route',()=>{
 const{s,h}=fixture(),walls=[...s.barriers,...h.barriers];let probes=0;
 for(const path of layout.paths)for(let i=1;i<path.points.length;i++){const a=path.points[i-1],b=path.points[i],len=Math.hypot(b.x-a.x,b.z-a.z);for(const offset of[-1.95,0,1.95])for(const t of[0,.5,1]){const p={x:a.x+(b.x-a.x)*t-(b.z-a.z)/len*offset,z:a.z+(b.z-a.z)*t+(b.x-a.x)/len*offset};for(const w of walls){const q=nearestOnSegment(p,w.a,w.b);assert.ok(Math.hypot(p.x-q.x,p.z-q.z)>.41,`${path.id} blocked by ${w.island} ${w.kind}`);}probes++;}}
 assert.ok(probes>6000);
});
test('every island has independent exposed union edges and an accessible future NPC reservation',()=>{
 const{s,h}=fixture(),walls=[...s.barriers,...h.barriers];
 for(const i of ISLANDS){const p=PLACE_PLAN[i.name],edges=surface.barriers.filter(b=>b.island===i.name);assert.ok(edges.length>=10,i.name);assert.equal(p.npc.implemented,false);
  for(const v of[p.npc.position,p.npc.playerStop]){assert.ok(Math.hypot(v[0],v[2])<8.3);for(const w of walls){const q=nearestOnSegment({x:i.x+v[0],z:i.z+v[2]},w.a,w.b);assert.ok(Math.hypot(q.x-i.x-v[0],q.z-i.z-v[2])>.45,`${i.name} reservation blocked by ${w.kind}`);}}
 }
});
test('retained chime highlight uses a small geometric ring, not an opaque sprite square',async()=>{
 const{buildChimes}=await import('../src/world/chimes.js');const islands=ISLANDS.map(i=>({name:i.name,group:new THREE.Group()}));for(const c of buildChimes(islands).chimes){assert.equal(c.halo.geometry.type,'RingGeometry');assert.equal(c.halo.material.map,null);}
});
