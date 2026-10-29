import {test} from 'node:test';import assert from 'node:assert/strict';import * as THREE from 'three';import polygon from 'polygon-clipping';
import plan from '../src/data/bridge-landscape.json' with {type:'json'};
import layout from '../src/data/yuan-layout.json' with {type:'json'};
import {buildBridgeLandscape} from '../src/world/bridge-landscape.js';
import {nearestOnSegment,moveWithGuards} from '../src/sim/walkways.js';
const area=r=>Math.abs(r.reduce((s,a,i)=>{const b=r[(i+1)%r.length];return s+a[0]*b[1]-b[0]*a[1];},0))/2;
test('landscape beds stay outside the original shared road/island domain and lights respect the budget',()=>{
 assert.equal(plan.safeWidth,4.8);assert.ok(plan.lamps.length<=42);assert.equal(plan.routes.length,22);
 for(const z of plan.zones)for(const bed of z.beds)assert.ok(polygon.intersection([bed],plan.coreDomain).reduce((n,p)=>n+area(p[0]),0)<.0001);
 for(const id of['S12','S17'])assert.equal(plan.routes.find(p=>p.id===id).mode,'island-walk');
 for(const l of plan.lamps.filter(l=>l.route==='S09'))assert.equal(l.type,'low-linear');
});
test('real landscape geometry is instanced, bounded, has no live lights, and leaves the full player corridor clear',()=>{
 const s=buildBridgeLandscape(new THREE.Group());assert.ok(s.stats.newRealtimeLights===0);assert.ok(s.stats.triangles<180000,JSON.stringify(s.stats));
 s.group.traverse(o=>{assert.ok(!o.isLight);if(o.isMesh)assert.ok(o.geometry.attributes.position.array.every(Number.isFinite));});
 for(const path of layout.paths)for(const p of path.points)for(const wall of s.barriers){if(wall.a.y>1.6)continue;const q=nearestOnSegment(p,wall.a,wall.b);assert.ok(Math.hypot(p.x-q.x,p.z-q.z)>2.4,`${path.id} blocked by ${wall.source}`);}
 for(const wall of s.barriers){const dx=wall.b.x-wall.a.x,dz=wall.b.z-wall.a.z,d=Math.hypot(dx,dz);if(d<.001)continue;const p={x:(wall.a.x+wall.b.x)/2-dz/d,y:wall.a.y,z:(wall.a.z+wall.b.z)/2+dx/d};assert.equal(moveWithGuards(p,2*dz/d,-2*dx/d,[wall]),true);}
});
