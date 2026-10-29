import {test} from 'node:test';import assert from 'node:assert/strict';import * as THREE from 'three';import {buildBridgeLandscape} from '../src/world/bridge-landscape.js';
test('real 7-arm underside stops a rising head; ordinary road jump outside the arm is unchanged',()=>{
 const w=buildBridgeLandscape(new THREE.Group()),lamp=w.plan.lamps.find(l=>l.type==='seven'),[x,,z]=lamp.position,c=Math.cos(lamp.yaw),s=Math.sin(lamp.yaw),p=new THREE.Vector3(x+c*.5,1.5,z-s*.5),m={vy:7};
 assert.equal(w.constrainHead(p,1.35,m),true);const edge=new THREE.Vector3(x+c*.80,1.5,z-s*.80),em={vy:7};assert.equal(w.constrainHead(edge,1.35,em),true,'off-centre cap must catch the narrow strip between roof rays');assert.ok(edge.y+1.6<3.025);assert.equal(m.vy,0);assert.ok(p.y+1.6<3.025);
 const clear=new THREE.Vector3(x-c*2,1.5,z+s*2),normal={vy:7};assert.equal(w.constrainHead(clear,1.35,normal),false);assert.equal(normal.vy,7);
});
test('all installed seven lamps keep their real visible emitter aligned with the head collision',()=>{
 const w=buildBridgeLandscape(new THREE.Group()),up=new THREE.Vector3(0,1,0);let count=0;
 for(const l of w.plan.lamps.filter(l=>l.type==='seven')){const[x,,z]=l.position,c=Math.cos(l.yaw),s=Math.sin(l.yaw),origin=new THREE.Vector3(x+c*.5,1,z-s*.5),ray=new THREE.Raycaster(origin,up,0,3),hit=ray.intersectObjects(w.ceilings,false).find(h=>h.face.normal.y<-.2);assert.ok(hit,l.id);assert.ok(Math.abs(hit.point.y-3.0175)<.001,l.id);const edge=new THREE.Vector3(x+c*.8,1.5,z-s*.8),move={vy:7};assert.equal(w.constrainHead(edge,1.35,move),true,l.id);assert.ok(edge.y+1.6<3.025,l.id);count++;}
 assert.equal(count,34);
});
