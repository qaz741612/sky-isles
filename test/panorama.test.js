import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { Panorama } from '../src/sim/panorama.js';
import layout from '../src/data/yuan-layout.json' with { type:'json' };
globalThis.innerWidth=1440;globalThis.innerHeight=900;
test('orthographic panorama fits every actual footprint corner in landscape and portrait',()=>{
 const p=new Panorama(new THREE.PerspectiveCamera(55,1.6,.1,900),layout.bounds,()=>{});
 for(const [w,h] of [[1440,900],[430,932],[320,568],[844,390]]){
 p.fit(w,h);const b=layout.bounds;
 for(const x of [b.minX,b.maxX])for(const z of [b.minZ,b.maxZ]){const v=new THREE.Vector3(x,0,z).project(p.ortho);assert.ok(Math.abs(v.x)<.86&&Math.abs(v.y)<.86);}
 }
});
test('transition is finite, pauses at the true ortho lens and returns to the saved camera pose',()=>{
 const camera=new THREE.PerspectiveCamera(55,1.6,.1,900);camera.position.set(3,8,16);camera.lookAt(0,1,3);const pos=camera.position.clone(),q=camera.quaternion.clone(),events=[];
 const p=new Panorama(camera,layout.bounds,v=>events.push(v));p.enter();
 for(let i=0;i<80;i++){p.update(1/60);assert.ok(p.camera.projectionMatrix.elements.every(Number.isFinite));}
 assert.equal(p.mode,'overview');assert.equal(p.camera.isOrthographicCamera,true);p.leave();for(let i=0;i<80;i++)p.update(1/60);
 assert.equal(p.mode,'explore');assert.deepEqual(events,[true,false]);assert.ok(camera.position.equals(pos));assert.ok(camera.quaternion.equals(q));
});

test('resizing during overview restores the current aspect without a final lens jump',()=>{
 const camera=new THREE.PerspectiveCamera(58,430/739,.1,900),p=new Panorama(camera,layout.bounds,()=>{});
 p.enter();p.update(1.2);camera.aspect=844/390;camera.fov=55;camera.updateProjectionMatrix();p.fit(844,390);
 p.leave();p.update(1.19999);
 for(let i=0;i<16;i++)assert.ok(Math.abs(p.camera.projectionMatrix.elements[i]-camera.projectionMatrix.elements[i])<1e-5);
 p.update(.01);assert.equal(p.camera,camera);assert.equal(p.mode,'explore');
});
