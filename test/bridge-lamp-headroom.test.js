import {test} from 'node:test';import assert from 'node:assert/strict';import * as THREE from 'three';import {buildBridgeLandscape} from '../src/world/bridge-landscape.js';
test('real 7-arm underside stops a rising head; ordinary road jump outside the arm is unchanged',()=>{
 const w=buildBridgeLandscape(new THREE.Group()),lamp=w.plan.lamps.find(l=>l.type==='seven'),[x,,z]=lamp.position,c=Math.cos(lamp.yaw),s=Math.sin(lamp.yaw),p=new THREE.Vector3(x+c*.5,1.5,z-s*.5),m={vy:7};
 assert.equal(w.constrainHead(p,1.35,m),true);assert.equal(m.vy,0);assert.ok(p.y+1.6<3.025);
 const clear=new THREE.Vector3(x-c*2,1.5,z+s*2),normal={vy:7};assert.equal(w.constrainHead(clear,1.35,normal),false);assert.equal(normal.vy,7);
});
