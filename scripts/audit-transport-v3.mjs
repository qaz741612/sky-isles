import fs from 'node:fs';
import * as THREE from 'three';
import {buildTransport} from '../src/world/transport.js';
import {nearestOnSegment} from '../src/sim/walkways.js';
import layout from '../src/data/yuan-layout.json' with {type:'json'};
const scene=buildTransport({name:'home',group:new THREE.Group()},()=>new THREE.Group());
const roads=layout.paths.filter(p=>p.from==='F'||p.to==='F');
const segments=roads.flatMap(p=>p.points.slice(1).map((b,i)=>[p.points[i],b]));
const clearance=points=>Math.min(...points.flatMap(p=>segments.map(([a,b])=>{const q=nearestOnSegment(p,a,b);return Math.hypot(p.x-q.x,p.z-q.z)-2.4;})));
const solids=scene.plan.stationSolids.map(s=>{const [x0,z0,x1,z1]=s.bounds;return {...s,minDistanceFromRoadEdge:clearance([{x:x0,z:z0},{x:x1,z:z0},{x:x0,z:z1},{x:x1,z:z1}])};});
const npc=scene.plan.npcReservation;
const eye=new THREE.Vector3(...npc.cameraFrom),target=new THREE.Vector3(...npc.position).add(new THREE.Vector3(0,1.1,0));scene.group.updateMatrixWorld(true);
const ray=new THREE.Raycaster(eye,target.clone().sub(eye).normalize(),0,eye.distanceTo(target)-.1);
const report={
 source:'B coordinates and exact existing yuan-surface union; no transforms',home:{center:[0,0,0],radius:9,routeWidth:4.8,entryRoutes:roads.map(p=>p.id)},
 plan:scene.plan,stationSolids:solids,edgeSegments:scene.edgeBarriers.length,barrierSegments:scene.barriers.length,
 npc:{...npc,nearestBarrierDistance:Math.min(...scene.barriers.map(w=>{const p={x:npc.position[0],z:npc.position[2]},q=nearestOnSegment(p,w.a,w.b);return Math.hypot(p.x-q.x,p.z-q.z);})),cameraToHeadBlocked:ray.intersectObjects(scene.colliders,false).length>0},
 unchangedHomeChime:[4.6,0,3.6],unchangedHomeMushroom:[Math.cos(Math.atan2(22,18))*6.2,0,Math.sin(Math.atan2(22,18))*6.2],
 trainEnvelope:{x:[-2.9,2.9],z:[-7.4,-6.6],exclusion:scene.plan.rail.exclusion},
 boundaries:scene.barriers,
 limitations:['Camera ray checks the reserved NPC angle, not every possible user orbit.','No NPC model or dialogue added.','Display railway separated by physical railing; deliberate jumping can still leave safe ground.','Station is an exterior with a shallow real recess, not an indoor simulation.']
};
fs.writeFileSync('docs/previews/transport-island-redesign-v3/layout-audit.json',JSON.stringify(report,null,2));
console.log(JSON.stringify({solids,npc:report.npc,edges:report.edgeSegments,barriers:report.barrierSegments}));
