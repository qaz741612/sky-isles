// Eight places share components, not a repeated house. Layouts are hand authored
// in island-places.json; routing/occupied-point audits validate, never place them.
import * as THREE from 'three';
import places from '../data/island-places.json' with {type:'json'};
import {placeKit,PALETTE as C} from './place-kit.js';
export const PLACE_PLAN=places;
export const THEMES={tree:['family-hall','shaded-court','caregiver'],temple:['community-veranda','garden-walk','rest'],koi:['open-workshop','exhibit-shed','work-yard'],meadow:['canopy-garden','pergola','park'],windmill:['public-hall','service-porch','waiting-court'],crystal:['rain-garden','continuous-water','observatory'],lookout:['reading-hall','book-veranda','learning-court']};
// Closed rooms are clearly glazed shells; their usable entrance is a real open
// porch. Workshops, verandas and pavilions instead have individual wall/post guards.
function hall(k,s,{roof='fold',accent=C.wood,porch=1,posts}={}){
 const[x,z,w,d,h]=s;
 k.solid(C.cream,[w,h,d],[x,h/2,z],'hall-shell');k.shadow(x,z+d/2,w+1,d+1.8);
 k.box(C.stone,[w+.12,.18,d+.12],[x,.09,z]);
 k.glazing(x,z+d/2+.035,w*.78,h*.45,h*.56);
 k.glazing(x,z-d/2-.05,w*.76,h*.34,h*.58,false,-1);
 for(const xx of[x-w/2-.04,x+w/2+.04])k.glazing(xx,z,d*.63,h*.36,h*.58,true);
 k.box(accent,[w,.12,.12],[x,h*.25,z+d/2+.08]);
 const profile=roof==='butterfly'?[[x-w/2-.25,h+.5],[x,h+.18],[x+w/2+.25,h+.65]]:roof==='flat'?[[x-w/2-.25,h+.22],[x+w/2+.25,h+.22]]:[[x-w/2-.25,h+.18],[x-w*.05,h+.8],[x+w/2+.25,h+.35]];
 k.roof(profile,z,d+.5);
 if(porch){const front=z+d/2+porch;k.pad(x,z+d/2+porch/2,w+.45,porch+.2);k.roof([[x-w/2-.22,h-.08],[x+w/2+.22,h+.04]],front-porch/2,porch+.35,C.woodLight);for(const xx of posts||[x-w/2+.12,x+w/2-.12])k.column(xx,front-.1,h-.12);}
}
function pergola(k,[x,z,w,d,h],solidRoof=false){
 k.pad(x,z,w+.35,d+.35,C.woodLight);
 for(const xx of[x-w/2+.12,x+w/2-.12])for(const zz of[z-d/2+.12,z+d/2-.12])k.column(xx,zz,h);
 for(const zz of[z-d/2,z+d/2])k.beam(C.wood,[x-w/2-.15,h,zz],[x+w/2+.15,h,zz],.13,.17);
 if(solidRoof)k.roof([[x-w/2-.2,h+.17],[x+w/2+.2,h+.32]],z,d+.4);
 else for(let i=0;i<=7;i++)k.box(C.woodLight,[.13,.1,d+.35],[x-w/2+i*w/7,h+.14,z]);
}
function family(k,p){
 hall(k,p.building,{roof:'butterfly',accent:C.coral,porch:.55});hall(k,p.wing,{roof:'flat',accent:C.coral,porch:0});
 // Paired fabric-like low-poly shade above the caregiver/play garden, away from the four gates.
 k.pad(4.65,3.7,3.5,2.6);k.roof([[3,2.25],[4.7,2.65],[6.4,2.2]],3.8,2.8,C.woodLight);for(const x of[4.5,6.1])k.column(x,4.9,2.2);
 k.solid(C.coral,[1.25,.35,.9],[4.4,.175,4.1],'play-low-step');
 for(const x of[4,4.5,5])k.box(C.cream,[.18,.04,.65],[x,.38,4.1]);
 // Complete small play bridge: low deck, hand holds and adjacent caregiver seats.
 for(const z of[3.65,4.55])k.beam(C.teal,[3.8,.92,z],[5,.92,z],.05);
 k.planter(-5.9,4.2,1,.75);
}
function community(k,p){
 hall(k,p.building,{roof:'flat',porch:1.05,posts:[-5.8,-2.1]});
 // Long veranda rhythm, not a temple: horizontal clerestory, paired window bays.
 const[x,z,w,d,h]=p.building;
 for(const xx of[-4.8,-3.3,-1.8])k.column(xx,z+d/2+.88,h-.1);
 k.box(C.glass,[w*.68,.3,.07],[x,h-.18,z+d/2+.06]);
 k.pad(-3.5,-.65,4.3,1.1);k.planter(-6.7,-3.7,.5,2.7);k.planter(.65,-5.55,1.4,.6);
 // A continuous garden promenade has open centre and deliberate resting edges.
 k.paving([[-7.1,-.8],[-5.3,-.8],[-5.3,1.2],[-6.8,2.2],[-7.7,.4]],C.woodLight);
 k.bench(-6.3,.4,Math.PI/2,1.3);
 k.paving([[2.5,2.7],[5.7,2.8],[6.9,4.9],[4.7,6.8],[2.6,5.7],[1.7,4.2]],C.edge);
 k.planter(5.9,5.2,.6,1.4);k.bench(4.2,5.7,Math.PI,1.7);
}
function workshop(k,p){
 const[x,z,w,d,h]=p.building;
 k.pad(x-.3,z,w+1,d+.5);
 // Working hall opens west into the shared yard; no proxy box across its mouth.
 k.solid(C.cream,[w,h,.18],[x,h/2,z-d/2+.09],'workshop-rear');
 for(const xx of[x-w/2+.09,x+w/2-.09]){k.solid(C.cream,[.18,h,d-.18],[xx,h/2,z+.05],'workshop-side');k.column(xx,z+d/2,h-.1);k.glazing(xx+(xx<x?-.11:.11),z,d*.6,.85,1.65,true);}
 k.roof([[x-w/2-.3,h+.18],[x+.35,h+.8],[x+w/2+.3,h+.25]],z,d+.6);
 k.glazing(x,z-d/2-.025,w*.6,.8,1.6,false,-1);
 k.shadow(x,z+.8,w+1,d+1.5);
 k.table(x,z,1.1,.7);for(const xx of[x-.3,x+.05,x+.3])k.box(C.woodLight,[.18,.24,.35],[xx,1.04,z]);
 const[sx,sz,sw,sd,sh]=p.shed;
 pergola(k,[sx,sz,sw,sd,sh],true);k.solid(C.cream,[sw,.95,.16],[sx,.475,sz-sd/2],'exhibit-back');
 k.table(sx,sz,.95,.65);k.box(C.coral,[.32,.3,.32],[sx,.98,sz]);
 // Open side display shelving is architectural infill with real side collision.
 for(const yy of[.45,.95,1.45])k.box(C.woodLight,[.35,.08,1.2],[5.4,yy,.4]);
}
function garden(k,p){
 pergola(k,p.pergola);k.planter(6,4.4,.55,1.6);k.planter(-3.9,-5.8,1.4,.65);
 // A garden terrace, lawn and raised herb bed; paths surround, never bisect, tree trunks.
 k.pad(3.7,5.4,2.2,1,C.woodLight);k.planter(3.7,5.9,1.8,.45);
 k.paving([[-6.8,-4.5],[-4.5,-5.8],[-2.6,-5.4],[-3,-3.1],[-5.1,-2.6]],C.lawn);
 // Modest pet-friendly play arch, off the travel spine; no giant pet monument.
 for(const x of[3.1,4.4])k.column(x,3.15,.75);
 k.beam(C.coral,[3.1,.75,3.15],[4.4,.75,3.15],.09);
}
function services(k,p){
 const[x,z,w,d,h]=p.building;
 k.pad(x,z+.6,w+.6,d+1.8);k.shadow(x,z+1,w+1,d+2);
 k.solid(C.cream,[w,h,.18],[x,h/2,z-d/2+.09],'service-back');
 for(const xx of[x-w/2+.09,x+w/2-.09]){k.solid(C.cream,[.18,h,d],[xx,h/2,z],'service-side');k.glazing(xx+(xx<x?-.11:.11),z,d*.7,1.05,1.4,true);}
 k.glazing(x,z-d/2-.035,w*.75,.85,1.45,false,-1);
 // Separate glazed bays frame a genuine open covered entry to a public counter.
 for(const xx of[x-1.5,x+1.5]){k.solid(C.cream,[1.05,2.05,.2],[xx,1.025,z+d/2],'service-bay');k.glazing(xx,z+d/2+.03,.95,1.1,1.3);}
 k.roof([[x-w/2-.4,h+.15],[x+w/2+.7,h+.15]],z+.45,d+1.7);
 for(const xx of[-5.58,-2.2])k.column(xx,-2.1,h);
 k.box(C.cream,[w*.64,.55,1.5],[x-.35,h+.42,z-.25]);k.glazing(x-.35,z+.52,w*.54,.27,h+.45);k.glazing(x-.35,z-1.035,w*.54,.27,h+.45,false,-1);
 k.solid(C.stone,[1.55,.85,.42],[x,.425,z-.15],'service-counter');k.box(C.woodLight,[1.7,.08,.55],[x,.89,z-.15]);
 k.planter(-5.8,-.8,1.2,.5);k.planter(.1,-5.1,.6,1.3);
}
function waterGarden(k,p){
 pergola(k,p.pergola,true);
 k.solid(C.cream,[1.7,.8,.18],[4.6,.4,.2],'observation-display');
 // A connected watercourse reads from a headbox in the east to a southern rain garden.
 for(let i=1;i<p.water.length;i++){
  const a=p.water[i-1],b=p.water[i],retention=i===p.water.length-1,waterWidth=retention?p.retentionWidth:p.waterWidth,bank=waterWidth/2+.17;k.beam(C.stone,[a[0],.08,a[1]],[b[0],.08,b[1]],waterWidth+.28,.14);k.beam(C.water,[a[0],.16,a[1]],[b[0],.16,b[1]],waterWidth,.035);
  // Low curbs visibly mark the same horizontal safety boundary.
  const dx=b[0]-a[0],dz=b[1]-a[1],len=Math.hypot(dx,dz),nx=-dz/len*bank,nz=dx/len*bank;
  for(const sign of[-1,1])for(const [t0,t1]of(i===1?[[0,.45],[.8,1]]:[[0,1]])){const aa=[a[0]+dx*t0+nx*sign,a[1]+dz*t0+nz*sign],bb=[a[0]+dx*t1+nx*sign,a[1]+dz*t1+nz*sign];k.beam(C.cream,[aa[0],.23,aa[1]],[bb[0],.23,bb[1]],.11,.3);k.guard(aa,bb,.38,'water-edge');}
  if(retention){const endA=[b[0]+nx,b[1]+nz],endB=[b[0]-nx,b[1]-nz];k.beam(C.cream,[endA[0],.23,endA[1]],[endB[0],.23,endB[1]],.11,.3);k.guard(endA,endB,.38,'retention-bank');}
 }
 k.planter(-3.6,5.55,1.3,.6);
 // A real supported crossing opens both water curbs and returns to dry land.
 k.walkable([1.7,.16,1.2],[6,.16,1],C.woodLight);
 for(const x of[5.35,5.65,5.95,6.25,6.55])k.box(C.wood,[.035,.007,1.18],[x,.244,1]);
 for(const z of[.4,1.6]){k.guard([5.15,z],[6.85,z],1.3,'water-crossing-rail');k.beam(C.teal,[5.15,1.2,z],[6.85,1.2,z],.045);for(const x of[5.15,6.85])k.column(x,z,1.2);}
 const[hx,hz]=p.water[0];k.solid(C.teal,[.62,.65,.7],[hx,.325,hz],'water-headbox');k.box(C.stone,[.22,.12,.55],[hx,.35,hz+.38]);k.box(C.waterLight,[.14,.23,.05],[hx,.2,hz+.65]);
}
function reading(k,p){
 hall(k,p.building,{roof:'fold',accent:C.wood,porch:.85});
 const[x,z,w,d,h]=p.wing;
 // Book veranda is usable half-outdoor architecture, with a rear book wall.
 k.pad(x,z,w+.3,d+.4);for(const yy of[.25,1,1.8])k.box(C.wood,[w,.05,.07],[x,yy,z-d/2-.025]);k.solid(C.cream,[w,h,.18],[x,h/2,z-d/2+.09],'book-wall');
 k.roof([[x-w/2-.2,h+.2],[x+w/2+.2,h+.4]],z,d+.5);
 for(const xx of[x-w/2+.12,x+w/2-.12])k.column(xx,z+d/2-.1,h+.1);
 for(const yy of[.55,1.1,1.65]){k.box(C.wood,[w-.35,.09,.35],[x,yy,z-d/2+.3]);for(let i=0;i<9;i++)k.box(i%3?C.woodLight:C.coral,[.17,.3,.18],[x-w*.4+i*w*.1,yy+.2,z-d/2+.3]);}
 k.table(.8,-3.7,1,.5);
 // Open outdoor reading table in the southern shade, clear of the retained chime.
 k.pad(3.6,3,2.3,2);k.table(3.6,3.1,1.5,.8);k.bench(3.6,4.1,0);
}
const BUILD={tree:family,temple:community,koi:workshop,meadow:garden,windmill:services,crystal:waterGarden,lookout:reading};
export function buildPolicyScenery(islands){
 const groups=[],barriers=[],colliders=[],cameraObstacles=[],pickMeshes=[],plots=[],layouts=[];
 for(const island of islands){if(island.name==='home')continue;const p=places[island.name],group=new THREE.Group();group.name=`policy-place-${island.name}`;group.userData.theme=THEMES[island.name];group.userData.layout=p;island.group.add(group);
  const k=placeKit(island,group);for(const path of p.paths)k.paving(path);BUILD[island.name](k,p);
  for(const[x,z,r]of p.trees)k.tree(x,z,r,island.name==='meadow'?0:1);
  for(const[x,z,yaw]of p.benches)k.bench(x,z,yaw);
  const built=k.finish();pickMeshes.push(...group.children.filter(m=>m.isMesh&&m.visible));groups.push(group);barriers.push(...built.barriers);colliders.push(...built.colliders);cameraObstacles.push(...built.cameraObstacles);layouts.push({island:island.name,...p,solids:built.solids});
  // Compatibility metadata for picking/QA: descriptive authored landmark, not a slot solver.
  const anchor=p.building||p.pergola;plots.push({island:island.name,x:anchor[0],z:anchor[1],radius:1,authored:true});
 }
 return{groups,barriers,colliders,cameraObstacles,pickMeshes,plots,layouts,update(){}};
}
