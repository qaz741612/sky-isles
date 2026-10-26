import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {URL} from 'node:url';
const read=p=>JSON.parse(fs.readFileSync(new URL(p,import.meta.url)));
test('expanded islands retain the approved B centres, exact curves and 4.8 width without repeated scaling',()=>{
 const plan=read('../src/data/yuan-plan.json'),b=read('../docs/design/yuan-size-comparison-v1/b/yuan-plan.json'),layout=read('../src/data/yuan-layout.json');
 assert.equal(plan.width,4.8);assert.equal(plan.compressionXZ,b.compressionXZ);assert.deepEqual(plan.edges,b.edges);
 assert.deepEqual(plan.nodes.map(n=>{const p={...n};delete p.r;return p;}),b.nodes.map(n=>{const p={...n};delete p.r;return p;}));
 assert.ok(plan.nodes.filter(n=>n.island).every(n=>n.r===(n.island==='tree'?10.2:9)));assert.deepEqual(layout.nodes,plan.nodes);
 for(const path of layout.paths){const old=read('../docs/design/yuan-size-comparison-v1/b/yuan-layout.json').paths.find(p=>p.id===path.id);assert.deepEqual(path.points,old.points);assert.equal(path.length,old.length);}
});
