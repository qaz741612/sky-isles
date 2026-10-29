import {test} from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import {buildTransportFoundation} from '../src/world/transport-foundation.js';
import layout from '../src/data/yuan-layout.json' with {type:'json'};
import surface from '../src/data/yuan-surface.json' with {type:'json'};
test('transport foundation and four mouths have continuous level support across their walkable width',()=>{
 const floor=buildTransportFoundation();floor.updateMatrixWorld(true);
 const ray=new THREE.Raycaster(new THREE.Vector3(0,1,3.5),new THREE.Vector3(0,-1,0));
 assert.ok(Math.abs(ray.intersectObject(floor)[0].point.y)<1e-6);
 const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(surface.positions,3));geo.setIndex(surface.indices);
 const deck=new THREE.Mesh(geo,new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));deck.updateMatrixWorld();let checks=0;
 for(const path of layout.paths.filter(p=>['S09','S10','S15','S18'].includes(p.id)))for(let i=0;i<path.points.length;i++){
  const q=path.points[i];if(Math.hypot(q.x,q.z)>14)continue;
  const a=path.points[Math.max(0,i-1)],b=path.points[Math.min(path.points.length-1,i+1)],l=Math.hypot(b.x-a.x,b.z-a.z);
  for(const d of[-1.8,0,1.8]){ray.ray.origin.set(q.x-(b.z-a.z)/l*d,1,q.z+(b.x-a.x)/l*d);assert.ok(ray.intersectObjects([floor,deck]).some(h=>Math.abs(h.point.y)<1e-6),path.id+JSON.stringify(q));checks++;}
 }
 assert.equal(layout.width,4.8);assert.ok(checks>100);
});
