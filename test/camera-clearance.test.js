import {test} from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import {homeCameraConstraint} from '../src/sim/camera-clearance.js';
import {ISLANDS} from '../src/world/islands.js';
import {buildTransport} from '../src/world/transport.js';

test('actual station roof no longer blocks the local target; other seven islands are unaffected',()=>{
 const s=buildTransport({name:'home',group:new THREE.Group()},()=>new THREE.Group());s.group.updateMatrixWorld(true);
 const clamp=homeCameraConstraint(s.colliders),target=new THREE.Vector3(-1.8,1.512,-2.5),position=new THREE.Vector3(-1.8,10,-14);
 assert.equal(clamp(target,position),true);
 const distance=target.distanceTo(position),ray=new THREE.Raycaster(target,position.clone().sub(target).normalize(),0,distance-.01);
 assert.ok(distance>.5);assert.equal(ray.intersectObjects(s.colliders,false).length,0);
 for(const island of ISLANDS.filter(i=>i.name!=='home')){
  const target=new THREE.Vector3(island.x,island.y+1.5,island.z);
  const pos=target.clone().add(new THREE.Vector3(0,10,16)),before=pos.clone();assert.equal(clamp(target,pos),false);assert.deepEqual(pos.toArray(),before.toArray());
 }
});
