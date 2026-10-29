import {test} from 'node:test';import assert from 'node:assert/strict';import polygon from 'polygon-clipping';
import layout from '../src/data/yuan-layout.json' with {type:'json'};
import config from '../src/data/future-island-reservations.json' with {type:'json'};
const area=r=>Math.abs(r.reduce((s,v,i)=>{const q=r[(i+1)%r.length];return s+v[0]*q[1]-q[0]*v[1];},0))/2;
const roads=layout.paths.map(p=>{const e=p.points.map((q,i)=>{const a=p.points[Math.max(0,i-1)],b=p.points[Math.min(p.points.length-1,i+1)],d=Math.hypot(b.x-a.x,b.z-a.z);return{l:[q.x-(b.z-a.z)/d*2.4,q.z+(b.x-a.x)/d*2.4],r:[q.x+(b.z-a.z)/d*2.4,q.z-(b.x-a.x)/d*2.4]};});const ring=[...e.map(e=>e.l),...e.toReversed().map(e=>e.r)];return[[...ring,ring[0]]];});
test('six future building envelopes remain inside their islands and outside every 4.8 route, without runtime construction',()=>{
 assert.equal(config.reservations.length,6);
 for(const v of config.reservations){const n=layout.nodes.find(n=>n.island===v.island);assert.ok(v.localFootprintXZ.every(p=>Math.hypot(...p)<n.r));const ring=v.localFootprintXZ.map(([x,z])=>[x+n.x,z+n.z]);for(const road of roads)assert.ok(polygon.intersection([ring],road).reduce((s,p)=>s+area(p[0]),0)<.001,v.island);assert.equal(v.runtimeObjectsCreated,0);assert.equal(v.npc.implemented,false);assert.ok(v.gates.length);}
});
