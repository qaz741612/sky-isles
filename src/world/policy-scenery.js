// Policy facilities are illustrative scenery, not approved construction projects.
// Native geometry, shared palette, per-island material batches. No new textures/NPCs.
import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { toonMaterial } from './toon.js';
import layout from '../data/yuan-layout.json' with { type:'json' };
import { nearestOnSegment } from '../sim/walkways.js';

const C={cream:0xffedcf,teal:0x527f80,dark:0x38555e,coral:0xd98670,stone:0xc7bbad,leaf:0x719e83,mint:0x9ab78f,blue:0x83bed0,white:0xfff7df,gold:0xe8bd76};
export const THEMES={tree:['family-house','playground','stroller'],temple:['care-home','gazebo','rest-garden'],koi:['startup-studio','market','workbench'],meadow:['park-trees','pet-agility','picnic'],windmill:['civic-office','digital-kiosk','service-plaza'],crystal:['sluice-channel','drainage','warning-beacon'],lookout:['school-library','open-book','playfield']};
const segments=layout.paths.flatMap(p=>p.points.slice(1).map((v,i)=>[p.points[i],v]));

// Conservative circular footprints stay within the island and outside the entire
// 4.8-wide bridge gates, tapering to >=2.2-wide island walking lanes + foot clearance.
const planCache=new Map();
export function planScenery(island,occupied=[]) {
 const key=JSON.stringify([island,occupied]);
 if(planCache.has(key))return planCache.get(key).map(p=>({...p}));
 // Roads beyond this envelope cannot be the closest road to any point in
 // the island; pruning them preserves placements while reducing startup work.
 const nearSegments=segments.filter(([a,b])=>{const q=nearestOnSegment(island,a,b);return Math.hypot(q.x-island.x,q.z-island.z)<=2*island.r+5;});
 const placed=[],radii=island.r<=5?[1.3,.75,.65,.5,.45]:[1.8,1.05,.85,.7,.6,.5,.45];
 for(const radius of radii){let best=null;
 for(let x=-island.r;x<=island.r;x+=.25)for(let z=-island.r;z<=island.r;z+=.25){
  if(Math.hypot(x,z)+radius>island.r-.22)continue;
  const p={x:x+island.x,z:z+island.z};let clearance=Infinity;
  for(const [a,b] of nearSegments){const q=nearestOnSegment(p,a,b);const gate=Math.hypot(q.x-island.x,q.z-island.z);
  const half=1.1+1.3*Math.max(0,Math.min(1,(gate-(island.r-3))/1.5));
  clearance=Math.min(clearance,Math.hypot(p.x-q.x,p.z-q.z)-half);}
  if(clearance<radius+.42)continue;
  if([...placed,...occupied].some(v=>Math.hypot(x-v.x,z-v.z)<radius+v.radius+.22))continue;
  const score=Math.min(clearance-radius,.8)-.1*Math.hypot(x,z);
  if(!best||score>best.score)best={x,z,radius,clearance,score};
 }
 if(best)placed.push(best);
 }
 if(placed.length<3)throw new Error(`Insufficient safe scenery plots on ${island.name}: ${placed.length}`);
 planCache.set(key,placed);
 return placed.map(p=>({...p}));
}

export function buildPolicyScenery(islands,occupied={}) {
 const groups=[],barriers=[],plots=[],colliders=[];
 for(const isle of islands){if(isle.name==='home')continue;
 const group=new THREE.Group();group.name=`policy-scenery-${isle.name}`;group.userData.theme=THEMES[isle.name];
 const slots=planScenery({name:isle.name,x:isle.pos.x,z:isle.pos.z,r:isle.r},occupied[isle.name]);
 const batches=new Map();
 const add=(g,color)=>{if(!batches.has(color))batches.set(color,[]);batches.get(color).push(g);};
 // A low, walkable central plaza, with the original grass/rock silhouette intact.
 const plaza=new THREE.CircleGeometry(isle.r*.28,28);plaza.rotateX(-Math.PI/2);plaza.translate(0,.006,0);add(plaza,C.stone);
 for(const [a,b] of segments){const x=(a.x+b.x)/2-isle.pos.x,z=(a.z+b.z)/2-isle.pos.z;if(Math.hypot(x,z)>isle.r-1.1)continue;const g=new THREE.PlaneGeometry(1.8,Math.hypot(b.x-a.x,b.z-a.z)+.04);g.rotateX(-Math.PI/2);g.rotateY(Math.atan2(b.x-a.x,b.z-a.z));g.translate(x,.008,z);add(g,C.stone);}
 slots.forEach((p,index)=>{
  const s=p.radius,kind=THEMES[isle.name][Math.min(index,2)];plots.push({...p,island:isle.name,kind});
  const box=(color,w,h,d,x=0,y=h/2,z=0,rz=0)=>{const g=new THREE.BoxGeometry(w*s,h*s,d*s);g.rotateZ(rz);g.translate(p.x+x*s,y*s,p.z+z*s);add(g,C[color]);};
  const ball=(color,r,x,y,z)=>{const g=new THREE.SphereGeometry(r*s,8,5);g.translate(p.x+x*s,y*s,p.z+z*s);add(g,C[color]);};
  const ring=(color,r,t,x,y,z,flat=false)=>{const g=new THREE.TorusGeometry(r*s,t*s,5,12);if(flat)g.rotateX(-Math.PI/2);g.translate(p.x+x*s,y*s,p.z+z*s);add(g,C[color]);};
  const bench=(x=0,z=0)=>{box('coral',1.1,.12,.4,x,.48,z);box('teal',1.1,.45,.1,x,.72,z+.22);for(const dx of [-.4,.4])box('dark',.1,.45,.3,x+dx,.23,z);};
  const building=(roof='teal')=>{
   box('cream',1.35,1.55,1.1);box(roof,1.5,.18,1.3,0,1.63);box('dark',.3,.85,.04,0,.43,.57);
   for(const x of [-.43,.43])box('blue',.32,.4,.04,x,1.02,.57);
   box('stone',1.5,.08,1.3,0,.04);box('white',.1,1.5,.1,-.61,.8,.56);box('white',.1,1.5,.1,.61,.8,.56);
  };
  if(index===0){
   if(isle.name==='tree'){
    building('coral');box('coral',.8,.16,1.3,-.38,1.83,0,.3);box('coral',.8,.16,1.3,.38,1.83,0,-.3);
    for(const x of [-.23,.23])ball('gold',.16,x,1.48,.61);
   }else if(isle.name==='temple'){
    building();box('leaf',.12,.55,.05,0,1.45,.66);box('leaf',.45,.12,.05,0,1.45,.66);box('coral',1.3,.1,.3,0,1.15,.6);
   }else if(isle.name==='koi'){
    building();box('teal',.75,.9,.9,.25,1.95,-.1);box('blue',1.05,.05,.65,-.15,1.8,-.1);for(const x of [-.5,-.15,.2])box('white',.025,.025,.65,x,1.84,-.1);
   }else if(isle.name==='meadow'){
    for(const [x,z] of [[-.4,-.2],[.4,.25]]){box('coral',.18,1.05,.18,x,.55,z);ball('leaf',.48,x,1.3,z);ball('mint',.36,x+.12,1.66,z);}
   }else if(isle.name==='windmill'){
    building();box('teal',1.4,.2,.3,0,1.35,.6);box('blue',.7,.45,.05,0,1.65,.68);for(const x of [-.55,.55])box('white',.09,1.3,.09,x,.65,.7);box('gold',.3,.12,.04,0,2,.01);
   }else if(isle.name==='crystal'){
    box('blue',1.2,.07,1.2,0,.065);for(const x of [-.65,.65])box('stone',.18,.35,1.35,x,.18);for(const x of [-.55,.55])box('teal',.12,1.25,.14,x,.64,0);
    box('teal',1.3,.12,.18,0,1.3);box('stone',1,.65,.12,0,.4,0);ring('coral',.25,.04,0,1.55,0);
   }else if(isle.name==='lookout'){
    building('coral');box('teal',.1,.8,.1,.4,2.1,0);box('gold',.45,.3,.04,.62,2.25,0);box('white',.55,.28,.05,0,1.5,.65);
   }
  }else if(index===1){
   if(isle.name==='tree'){
    for(const x of [-.55,.55])box('teal',.1,1.1,.1,x,.55,-.3);box('teal',1.4,.12,.16,0,1.1,-.3);for(const x of [-.3,.3])box('gold',.04,.6,.04,x,.72,-.3);box('coral',.8,.12,.4,0,.42,-.3);box('blue',.6,.12,1.3,.5,.4,.25,.5);
   }else if(isle.name==='temple'){
    for(const x of [-.6,.6])for(const z of [-.5,.5])box('cream',.1,1.25,.1,x,.63,z);box('teal',1.55,.2,1.45,0,1.35);bench();
   }else if(isle.name==='koi'){
    box('cream',1.2,.85,.8);box('teal',1.4,.15,1.1,0,1);for(const x of [-.45,0,.45])box('coral',.22,.1,.6,x,.9,.62);box('gold',1,.12,.25,0,.6,.55);
   }else if(isle.name==='meadow'){
    ring('coral',.55,.12,0,.65,0);for(const x of [-.6,.6])box('teal',.12,.65,.35,x,.33);for(const x of [-.2,.2])ball('gold',.15,x,.04,.7);
   }else if(isle.name==='windmill'){
    box('teal',.6,1.3,.45,0,.65);box('blue',.48,.65,.05,0,.9,.26);for(const x of [-.12,.12])for(const y of [.75,1])box('white',.12,.12,.02,x,y,.3);box('gold',.4,.08,.3,0,.47,.32);
   }else if(isle.name==='crystal'){
    box('blue',1.4,.06,.55,0,.05);for(const z of [-.4,.4])box('stone',1.5,.2,.2,0,.12,z);for(const x of [-.4,0,.4])box('teal',.12,.05,.8,x,.27);
   }else if(isle.name==='lookout'){
    box('coral',1.45,.12,.95,0,.25);box('white',.7,.13,.85,-.36,.38,0,-.2);box('white',.7,.13,.85,.36,.38,0,.2);box('teal',.06,.6,.12,0,.35);for(const z of [-.22,0,.22])box('gold',.6,.02,.025,-.38,.48,z);
   }
  }else{
   if(index>2){box('cream',1,.22,.9);ball('leaf',.45,0,.5,0);ball('coral',.15,.2,.84,.1);}
   else if(isle.name==='tree'){box('coral',.7,.6,.7,0,.6);box('cream',.8,.16,.8,0,1);for(const x of [-.4,.4])for(const z of [-.32,.32])ball('dark',.14,x,.2,z);}
   else if(isle.name==='crystal'){box('teal',.18,1.4,.18);box('gold',.5,.4,.5,0,1.5);box('coral',.38,.1,.38,0,1.77);}
   else if(isle.name==='lookout'){ring('coral',.65,.12,0,.04,0,true);box('mint',.65,.03,.6,0,.03);}
   else if(isle.name==='koi'){box('teal',1.3,.12,.85,0,.75);for(const x of [-.5,.5])box('cream',.12,.7,.7,x,.35);box('gold',.4,.4,.35,0,1);}
   else bench();
  }
  // Obstacles use a conservative square within the reserved circular plot.
  const half=s*.72,points=[[-half,-half],[half,-half],[half,half],[-half,half]];
  for(let i=0;i<4;i++){const a=points[i],b=points[(i+1)%4];barriers.push({a:{x:isle.pos.x+p.x+a[0],y:0,z:isle.pos.z+p.z+a[1]},b:{x:isle.pos.x+p.x+b[0],y:0,z:isle.pos.z+p.z+b[1]},height:(index===0?(isle.name==='crystal'?.4:1.55):1.1)*s,scenery:isle.name});}
 });
 for(const [color,parts] of batches){const mesh=new THREE.Mesh(mergeGeometries(parts),toonMaterial(color));mesh.userData.island=isle.name;group.add(mesh);colliders.push(mesh);parts.forEach(g=>g.dispose());}
 isle.group.add(group);groups.push(group);
 }
 return {groups,barriers,plots,colliders,update(){}};
}
