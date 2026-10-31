// Read-only V3 intake: measure actual PR17 GLB/terrain/colliders, no generation.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import polygon from 'polygon-clipping';
const read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const out='docs/design/industry-youth-island-c-v3/preflight';fs.mkdirSync(out,{recursive:true});
const model='public/models/industry-youth-c/industry-youth-c.glb',buffer=fs.readFileSync(model),gltf=await new GLTFLoader().parseAsync(buffer.buffer.slice(buffer.byteOffset,buffer.byteOffset+buffer.byteLength),'');gltf.scene.updateMatrixWorld(true);
const plan=read('src/data/industry-youth-plan.json'),world=read('src/data/yuan-plan.json'),surface=read('src/data/yuan-surface.json'),collision=read('src/data/industry-youth-collision.json'),landscape=read('src/data/bridge-landscape.json');
const whole=new THREE.Box3().setFromObject(gltf.scene,true),materials=new Set(),areas={};let triangles=0,meshes=0;
gltf.scene.traverse(o=>{if(!o.isMesh)return;meshes++;triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;for(const m of(Array.isArray(o.material)?o.material:[o.material]))materials.add(m);const area=o.name.match(/^0[0-4]_[A-Za-z]+/)?.[0]??'signs';areas[area]??=new THREE.Box3();areas[area].union(new THREE.Box3().setFromObject(o,true));});
const bounds=b=>({min:b.min.toArray(),max:b.max.toArray(),dimensions:b.getSize(new THREE.Vector3()).toArray()});
const footprint=[[[...plan.footprintLocal,plan.footprintLocal[0]]]],c=plan.centre;
const core=surface.islandPaving.find(p=>p.island==='koi').domain.map(rs=>rs.map(r=>r.map(([x,z])=>[x-c[0],z-c[2]])));
const area=mp=>mp.reduce((a,rs)=>a+rs.reduce((n,r,i)=>n+(i===0?1:-1)*Math.abs(r.reduce((v,p,j)=>{const q=r[(j+1)%r.length];return v+p[0]*q[1]-p[1]*q[0];},0)/2),0),0);
const npc=plan.npc[0],x=npc.position[0],z=npc.position[2],reserved=[[[x-1.5,z-1.5],[x+1.5,z-1.5],[x+1.5,z+1.5],[x-1.5,z+1.5],[x-1.5,z-1.5]]];
const collisions=collision.solids.map(s=>{const p=s.polygon,region=[[...p,p[0]]];return{name:s.name,min:[Math.min(...p.map(p=>p[0])),s.base,Math.min(...p.map(p=>p[1]))],max:[Math.max(...p.map(p=>p[0])),s.top,Math.max(...p.map(p=>p[1]))],roadCoreOverlapArea:s.base<1.6&&s.top>.25?area(polygon.intersection(core,region)):0,npcOverlapArea:area(polygon.intersection(reserved,region))};});
const report={basis:'PR17 0c7cab7 measured before V3; V3 package not yet located',worldCentre:c,model:{path:model,sha256:hash(model),bytes:buffer.byteLength,triangles,meshes,materials:materials.size,boundsLocal:bounds(whole),areas:Object.fromEntries(Object.entries(areas).map(([k,b])=>[k,bounds(b)]))},terrain:{source:'src/data/industry-youth-plan.json + yuan-plan.json',footprintArea:area(footprint),coreClippedArea:area(core),localXZBounds:[Math.min(...plan.footprintLocal.map(p=>p[0])),Math.min(...plan.footprintLocal.map(p=>p[1])),Math.max(...plan.footprintLocal.map(p=>p[0])),Math.max(...plan.footprintLocal.map(p=>p[1]))]},lockedEntrances:world.edges.filter(e=>plan.entrances.includes(e.id)),npc:{...npc,full3x3OutsideArea:area(polygon.difference(reserved,footprint))},collision:{sourceSHA256:hash('src/data/industry-youth-collision.json'),solids:collisions,coreConflicts:collisions.filter(s=>s.roadCoreOverlapArea>.0001),npcConflicts:collisions.filter(s=>s.npcOverlapArea>.0001)},retainedLamps:landscape.lamps.filter(l=>['S14','S15','S16'].includes(l.route)),limits:['No V3 GLB/source available; no V3 bounding boxes or fit decision claimed.','Only existing PR17 static data audited; no new gameplay test or model export in this step.']};
assertZero(report.collision.coreConflicts.length,'existing core conflicts');assertZero(report.collision.npcConflicts.length,'existing NPC conflicts');assertZero(report.npc.full3x3OutsideArea,'NPC outside current ground');
fs.writeFileSync(path.join(out,'baseline-runtime-audit.json'),JSON.stringify(report,null,2)+'\n');console.log(`Measured actual PR17 GLB (${meshes} meshes / ${triangles} triangles); baseline core + NPC clear`);
function assertZero(v,label){if(v>.0001)throw Error(label);}
