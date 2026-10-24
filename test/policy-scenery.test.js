import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { buildPolicyScenery,THEMES } from '../src/world/policy-scenery.js';
import { ISLANDS } from '../src/world/islands.js';
import { moveWithGuards } from '../src/sim/walkways.js';

test('seven thematic scenes reserve 4.8-wide bridge gates and island lanes, keep original terrain, and batch materials',()=>{
 const islands=ISLANDS.map(i=>({...i,pos:new THREE.Vector3(i.x,i.y,i.z),group:new THREE.Group()}));
 const result=buildPolicyScenery(islands);
 assert.equal(result.groups.length,7);assert.ok(islands[0].group.children.length===0,'transport is retained separately');
 for(const island of islands.slice(1)){
  const group=island.group.children[0];assert.deepEqual(group.userData.theme,THEMES[island.name]);
  assert.ok(group.children.length<=10,'bounded material batches');
  for(const p of result.plots.filter(p=>p.island===island.name)){
   assert.ok(Math.hypot(p.x,p.z)+p.radius<=island.r-.21);
   assert.ok(p.clearance>=p.radius+.42);
  }
  group.traverse(o=>{assert.ok(!o.isLight);if(o.isMesh){assert.ok(!o.material.map,'no added textures');assert.ok(o.geometry.attributes.position.array.every(Number.isFinite));}});
 }
 for(const w of result.barriers){
  const dx=w.b.x-w.a.x,dz=w.b.z-w.a.z,d=Math.hypot(dx,dz),p={x:(w.a.x+w.b.x)/2-dz/d,y:0,z:(w.a.z+w.b.z)/2+dx/d};
  moveWithGuards(p,dz/d*2,-dx/d*2,[w]);const side=(p.x-w.a.x)*(-dz/d)+(p.z-w.a.z)*dx/d;assert.ok(side>=.4099);
 }
});

test('retained chime highlight uses a small geometric ring, not an opaque sprite square',async()=>{
 const {buildChimes}=await import('../src/world/chimes.js');
 const islands=ISLANDS.map(i=>({name:i.name,group:new THREE.Group()}));const chimes=buildChimes(islands);
 for(const c of chimes.chimes){assert.equal(c.halo.geometry.type,'RingGeometry');assert.equal(c.halo.material.blending,THREE.NormalBlending);assert.equal(c.halo.material.map,null);}
});
