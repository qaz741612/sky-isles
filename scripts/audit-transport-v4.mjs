import fs from 'node:fs';
import * as THREE from 'three';
import {buildTransport} from '../src/world/transport.js';
import {nearestOnSegment} from '../src/sim/walkways.js';
import layout from '../src/data/yuan-layout.json' with {type:'json'};
const root='docs/previews/transport-island-polish-v4';
const s=buildTransport({name:'home',group:new THREE.Group()},()=>new THREE.Group());s.group.updateMatrixWorld(true);
const old=JSON.parse(fs.readFileSync('docs/previews/transport-island-redesign-v3/layout-audit.json','utf8'));
const originalEdges=old.boundaries.filter(b=>b.kind==='island-edge');
if(JSON.stringify(originalEdges)!==JSON.stringify(s.edgeBarriers))throw Error('V3 safety domain changed');
const segments=layout.paths.filter(p=>p.from==='F'||p.to==='F').flatMap(p=>p.points.slice(1).map((b,i)=>[p.points[i],b]));
const solids=s.plan.stationSolids.map(p=>{const [x0,z0,x1,z1]=p.collisionBounds||p.bounds;return{...p,roadEdgeClearance:Math.min(...[{x:x0,z:z0},{x:x0,z:z1},{x:x1,z:z0},{x:x1,z:z1}].flatMap(v=>segments.map(([a,b])=>{const q=nearestOnSegment(v,a,b);return Math.hypot(q.x-v.x,q.z-v.z)-2.4;})))};});
const audit={sourceBase:'70091a429bdbecafa053c3b8964dd34863ba5641',plan:s.plan,stationSolids:solids,edgeSegments:s.edgeBarriers.length,edgeGeometryExactV3:true,barrierCount:s.barriers.length,barriers:s.barriers,
 footprint:{before:old.plan.station.size[0]*old.plan.station.size[1],after:s.plan.station.size[0]*s.plan.station.size[1]},
 unchanged:{worldCenter:[0,0,0],radius:9,width:4.8,spawn:[0,.5,3.5],chime:[4.6,0,3.6],mushroom:old.unchangedHomeMushroom},
 trainSweep:{x:[s.plan.rail.center[0]-s.plan.rail.travel-1.25,s.plan.rail.center[0]+s.plan.rail.travel+1.25],z:[-7.4,-6.6],exclusion:s.plan.rail.exclusion},
 limitations:['No real-world approval/budget/schedule facts inferred.','Local camera constraint contracts to before the obstruction without changing orbit settings; extreme close views still require manual assessment.','No NPC, rideable train or complete interior.']};
fs.writeFileSync(`${root}/layout-audit.json`,JSON.stringify(audit,null,2));
if(fs.existsSync(`${root}/after/render-stats.json`)){
 const before=JSON.parse(fs.readFileSync(`${root}/before/render-stats.json`)),after=JSON.parse(fs.readFileSync(`${root}/after/render-stats.json`));
 const views={};
 for(const [name,a]of Object.entries(before.views)){const b=after.views[name];if(!b)throw Error(`missing ${name}`);
  const lensError=Math.max(...a.camera.map((v,i)=>Math.abs(v-b.camera[i])),...a.quaternion.map((v,i)=>Math.abs(v-b.quaternion[i])));
  if(lensError>1e-5||JSON.stringify(a.viewport)!==JSON.stringify(b.viewport))throw Error(`unmatched camera ${name}: ${lensError}`);
  const texels=v=>v.transportTextures.reduce((sum,[w,h])=>sum+w*h,0);
  views[name]={viewport:a.viewport,cameraPoseError:lensError,calls:[a.calls,b.calls],triangles:[a.triangles,b.triangles],transportMeshes:[a.transportMeshes,b.transportMeshes],transportTriangles:[a.transportTriangles,b.transportTriangles],transportTextureCount:[a.transportTextures.length,b.transportTextures.length],transportTextureTexels:[texels(a),texels(b)],worldTextureCount:[a.worldTextures,b.worldTextures]};
 }
 fs.writeFileSync(`${root}/performance-comparison.json`,JSON.stringify(views,null,2));
 console.log(JSON.stringify({views,footprint:audit.footprint,edges:s.edgeBarriers.length,barriers:s.barriers.length}));
}
