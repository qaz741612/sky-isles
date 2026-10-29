import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {URL} from 'node:url';
const adjustment=JSON.parse(fs.readFileSync(new URL('../src/data/yuan-map-adjustment.json',import.meta.url)));
const read=p=>JSON.parse(fs.readFileSync(new URL(p,import.meta.url)));
test('expanded islands retain the approved B centres, exact curves and 4.8 width without repeated scaling',()=>{
 const plan=read('../src/data/yuan-plan.json'),b=read('../docs/design/yuan-size-comparison-v1/b/yuan-plan.json'),layout=read('../src/data/yuan-layout.json');
 assert.equal(plan.width,4.8);assert.equal(plan.compressionXZ,b.compressionXZ);const expected=JSON.parse(JSON.stringify(b));for(const n of expected.nodes)n.x+=adjustment.nodeXOffsets[n.id]??0;for(const e of expected.edges)if(adjustment.edgeControlXOffsets[e.id])e.controlPointsXZ.forEach((p,i)=>p[0]+=adjustment.edgeControlXOffsets[e.id][i]);assert.deepEqual(plan.edges,expected.edges);
 assert.deepEqual(plan.nodes.map(n=>{const p={...n};delete p.r;return p;}),expected.nodes.map(n=>{const p={...n};delete p.r;return p;}));
 assert.ok(plan.nodes.filter(n=>n.island).every(n=>n.r===(n.island==='tree'?10.2:9)));assert.deepEqual(layout.nodes,plan.nodes);
 for(const path of layout.paths){const old=read('../docs/design/yuan-size-comparison-v1/b/yuan-layout.json').paths.find(p=>p.id===path.id);if(!adjustment.edgeControlXOffsets[path.id]){assert.deepEqual(path.points,old.points);assert.equal(path.length,old.length);}else{assert.equal(path.points[0].x,path.from==='A'?plan.nodes.find(n=>n.id==='A').x:path.from==='T3'?plan.nodes.find(n=>n.id==='T3').x:old.points[0].x);}}
});
