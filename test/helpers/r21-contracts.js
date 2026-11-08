// Explicit successor contract for tests whose old whole-world snapshots predate
// the user's R21 road/island authorization. No approved F/A/C/G asset is exempt.
import fs from'node:fs';import assert from'node:assert/strict';import{createHash}from'node:crypto';
export const R21=fs.existsSync('src/data/bdeh-plan.json');
export const R21_WORLD_DERIVATIVES=new Set(['src/main.js','src/world/islands.js','src/world/bridges.js','src/world/bridge-landscape.js','src/data/yuan-plan.json','src/data/yuan-layout.json','src/data/yuan-surface.json','src/data/bridge-landscape.json']);
export function assertR21Contracts(){
 const read=p=>JSON.parse(fs.readFileSync(p)),D='docs/design/bdeh-r21/',base=read(D+'baseline/yuan-plan.json'),plan=read('src/data/yuan-plan.json'),layout=read('src/data/yuan-layout.json'),candidate=read(D+'source-package/base/BDEH_R18/data/road-candidate-r2.json');
 for(const file of read(D+'PROTECTED-BASELINE.json').files)assert.equal(createHash('sha256').update(fs.readFileSync(file.path)).digest('hex'),file.sha256,'protected approved asset '+file.path);
 assert.equal(plan.width,4.8);assert.equal(plan.compressionXZ,base.compressionXZ);assert.equal(layout.paths.length,22);assert.deepEqual(layout.nodes,plan.nodes);
 for(const c of['F','A','C','G']){assert.deepEqual(plan.nodes.find(n=>n.id===c),base.nodes.find(n=>n.id===c));assert.deepEqual(plan.islandFootprintsXZ[c],base.islandFootprintsXZ[c]);}
 const moved=new Set(['B','E','T4','T6','T7']);
 for(const n of plan.nodes){const old=base.nodes.find(p=>p.id===n.id);if(moved.has(n.id)){assert.equal(n.x,candidate.nodes[n.id][0]);assert.equal(n.z,candidate.nodes[n.id][1]);assert.equal(n.r,old.r);}else assert.deepEqual(n,old);}
 for(const edge of plan.edges){const expected=candidate.allRoutesProposed.find(e=>e.id===edge.id);assert.deepEqual(edge.controlPointsXZ,expected.changed?expected.proposedControlPointsXZ:base.edges.find(e=>e.id===edge.id).controlPointsXZ);}
 const oldLayout=read(D+'baseline/yuan-layout.json');
 for(const id of['S01','S04','S05','S09','S10','S11','S15','S16','S18','S19','S20','S21','S22'])assert.deepEqual(layout.paths.find(p=>p.id===id),oldLayout.paths.find(p=>p.id===id),'untouched path '+id);
 for(const[id,count,tail]of[['S14',.6,true],['S02',.28,false]]){const a=oldLayout.paths.find(p=>p.id===id).points,k=Math.round((a.length-1)*count),b=layout.paths.find(p=>p.id===id).points,part=tail?a.slice(k):a.slice(0,k),next=tail?b.slice(-part.length):b.slice(0,part.length);assert.deepEqual(next.map(p=>[p.x,p.y,p.z]),part.map(p=>[p.x,p.y,p.z]),'protected actual A/C samples '+id);}
 const lamps=read('src/data/bridge-landscape.json').lamps,old=read(D+'baseline/bridge-landscape.json').lamps;assert.deepEqual(lamps.map(l=>l.id).sort(),old.map(l=>l.id).sort());
 for(const lamp of lamps)if(!candidate.allRoutesProposed.find(e=>e.id===lamp.route).changed)assert.deepEqual(lamp,old.find(p=>p.id===lamp.id),'unmoved fixture '+lamp.id);
 const seen=new Set(['F']);for(let i=0;i<22;i++)for(const p of layout.paths)if(seen.has(p.from)||seen.has(p.to)){seen.add(p.from);seen.add(p.to);}assert.equal(seen.size,21);
}
