import{test}from'node:test';import assert from'node:assert/strict';import fs from'node:fs';import{createHash}from'node:crypto';import*as T from'three';import{GLTFLoader}from'three/addons/loaders/GLTFLoader.js';
import{buildFloodControl}from'../src/world/flood-control.js';import plan from'../src/data/flood-control-plan.json'with{type:'json'};import art from'../src/data/flood-control-art.json'with{type:'json'};import collision from'../src/data/flood-control-collision.json'with{type:'json'};
const D='docs/design/flood-control-island-g-v5-1/',hash=b=>createHash('sha256').update(b).digest('hex');
async function asset(){const b=fs.readFileSync('public/models/flood-control-g/flood-control-g.glb');return new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'');}
test('V5.1 art preserves all214 V5 protected world, F/A/C and historical delivery bytes',()=>{
 const base=JSON.parse(fs.readFileSync(D+'protected-baseline.json'));assert.equal(base.commit,'8849b89e99163c179973a31571498115c6c80e7c');assert.ok(base.files.length>=214);for(const f of base.files)assert.equal(hash(fs.readFileSync(f.path)),f.sha256,f.path);
 const old=JSON.parse(fs.readFileSync(D+'baseline/flood-control-collision.json'));assert.equal(collision.dryGroundFloats,old.dryGroundFloats);assert.deepEqual(collision.groundPositions.slice(0,collision.dryGroundFloats),old.groundPositions.slice(0,old.dryGroundFloats));assert.equal(collision.waterIsCollider,false);
});
test('exported real V5.1 water has measurable crest-to-outfall descent on all three sluice lanes',async()=>{
 const g=await asset(),water=[];g.scene.traverse(o=>{if(o.isMesh&&/Hydraulic_Water/.test(o.name))water.push(o);});assert.ok(water.length>1);g.scene.updateMatrixWorld(true);const ray=new T.Raycaster(),heights=[];
 for(const x of art.water.laneCentres){const samples=[];for(const z of[6.35,5.4,4.3]){ray.set(new T.Vector3(x,1,z),new T.Vector3(0,-1,0));ray.far=4;const hit=ray.intersectObjects(water,false)[0];assert.ok(hit,'missing true flow surface '+x+' '+z);samples.push(hit.point.y);}assert.ok(samples[0]-samples[1]>.6,'no visible crest drop');assert.ok(samples[1]>samples[2],'runout should descend');assert.ok(samples[2]>=plan.waterHeights.downstream-.03);heights.push(samples);}
 assert.equal(heights.length,3);
});
test('V5.1 surface details stay opaque and within bounded mobile asset cost; no texture or live water dependency',async()=>{
 const b=fs.readFileSync('public/models/flood-control-g/flood-control-g.glb'),n=b.readUInt32LE(12),j=JSON.parse(b.subarray(20,20+n));let tri=0;for(const m of j.meshes)for(const p of m.primitives)tri+=j.accessors[p.indices].count/3;
 assert.ok(tri<100000);assert.ok(b.length<6*1024*1024);assert.ok(j.meshes.length<=64);assert.ok(j.materials.length<=26);assert.equal(j.textures?.length??0,0);for(const m of j.materials.filter(m=>/water|foam|ripple/.test(m.name)))assert.notEqual(m.alphaMode,'BLEND','transparent water cost '+m.name);assert.ok(j.materials.some(m=>/water/.test(m.name)));
 const report=JSON.parse(fs.readFileSync(D+'model-report.json'));assert.ok(report.unchangedEditableObjectsRetained>2000);assert.equal(report.baseBlendSHA256,hash(fs.readFileSync(D+'baseline/flood-control-g-v5.blend')));
});
test('V5.1 additional real banks/backrests remain clear of the exact guide reservation and public walking corridor',async()=>{
 const g=await asset(),scene=new T.Scene(),group=new T.Group();group.position.set(...plan.centre);scene.add(group);const built=buildFloodControl(g.scene,{group,pos:group.position});scene.updateMatrixWorld(true);const npc=plan.npc[0];assert.equal(plan.npc.length,1);assert.equal(npc.implemented,false);
 // Actual player-height ray sweeps across the entire3x3 box, not a mirrored coordinate assertion.
 const ray=new T.Raycaster();for(let i=0;i<=6;i++){const z=plan.centre[2]+npc.position[2]-1.49+i*.496;ray.set(new T.Vector3(plan.centre[0]+npc.position[0]-1.49,.8,z),new T.Vector3(1,0,0));ray.far=2.98;assert.equal(ray.intersectObjects(built.cameraObstacles,false).length,0,'guide volume obstructed by actual architecture');}
 for(const s of collision.solids.filter(v=>v.name==='V51 arrival planted bank'||v.name==='V51 command rain-garden bank'))assert.ok(s.polygon.length>=4);
 assert.equal(collision.solids.filter(v=>v.name==='V51 arrival planted bank').length,2);
});
