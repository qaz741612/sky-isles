import{test}from'node:test';import assert from'node:assert/strict';import fs from'node:fs';import{createHash}from'node:crypto';import*as T from'three';import{GLTFLoader}from'three/addons/loaders/GLTFLoader.js';
import{buildFloodControl}from'../src/world/flood-control.js';import{Player}from'../src/sim/player.js';import{guardIndex}from'../src/sim/walkways.js';import plan from'../src/data/flood-control-plan.json'with{type:'json'};import art from'../src/data/flood-control-art.json'with{type:'json'};import collision from'../src/data/flood-control-collision.json'with{type:'json'};
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
 const gate=[];g.scene.traverse(o=>{if(o.isMesh&&/Triple_Sluice_Mechanics/.test(o.name)){gate.push(o);for(const m of Array.isArray(o.material)?o.material:[o.material])m.side=T.DoubleSide;}});
 for(const x of art.water.laneCentres){ray.set(new T.Vector3(x-.99,-1.72,5.25),new T.Vector3(1,0,0));ray.far=1.98;assert.equal(ray.intersectObjects(gate,false).length,0,'foundation/inner structure blocks actual2m wet throat '+x);}

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
 const props=[];g.scene.traverse(o=>{if(o.isMesh&&/Civic_Props/.test(o.name))props.push(o);});const[sx,sz]=art.zones.overlook.sign;
 for(const y of[.08,.20,.40,.53,.80]){ray.set(new T.Vector3(plan.centre[0]+sx-.4,y,plan.centre[2]+sz),new T.Vector3(1,0,0));ray.far=.8;assert.ok(ray.intersectObjects(props,false).length,'water interpretation frame has no real ground mount at '+y);}
 for(const[x,z]of plan.benchesXZ)for(const dx of[-.6,.6]){ray.set(new T.Vector3(plan.centre[0]+x+dx,.60,plan.centre[2]+z+.7),new T.Vector3(0,0,-1));ray.far=.8;assert.ok(ray.intersectObjects(props,false).length,'timber back lacks physical upright');}

});

test('actual Player falling at nine sluice-water points returns to the dry guide checkpoint without underwater support',async()=>{
 const g=await asset(),scene=new T.Scene(),group=new T.Group();group.position.set(...plan.centre);scene.add(group);const built=buildFloodControl(g.scene,{group,pos:group.position});scene.updateMatrixWorld(true);const p=new Player(scene,new T.PerspectiveCamera(),built.colliders);p.navigation={islands:[],barriers:built.barriers,nearby:guardIndex(built.barriers)};p.ceilingConstraint=built.constrainHead;const stop=plan.npc[0].playerStop;let t=0;const tick=()=>{p.update(1/60,{x:0,z:0,jumpHeld:false,jumpPressed:false},t+=1/60);assert.ok(p.pos.toArray().every(Number.isFinite));};
 for(const x of art.water.laneCentres)for(const dx of[-.9,0,.9]){p.respawnCount=0;p.teleport(stop[0]+plan.centre[0],.2,stop[2]+plan.centre[2]);for(let i=0;i<90;i++)tick();const checkpoint=p.lastGrounded.clone();p.teleport(x+dx+plan.centre[0],-.8,5.25+plan.centre[2]);for(let i=0;i<240;i++)tick();assert.equal(p.respawnCount,1,'stranded under water '+x+' '+dx);assert.ok(p.pos.distanceTo(checkpoint)<.05);assert.ok(p.move.grounded);}
 const a=collision.groundPositions.slice(collision.dryGroundFloats);for(let i=1;i<a.length;i+=3)assert.ok(a[i]>=-.001,'submerged structural support became ground');
});
