// Continuous, non-swaying sightseeing decks; rendering and guard collisions share one plan.
import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { toonMaterial } from './toon.js';
import { planWalkways, WALKWAY } from '../sim/walkways.js';

export function buildBridges(scene, islands, rng) {
  // Preserve downstream cloud/prop random seeds from the retained version.
  // Only old plank jitter/phase draws are consumed; no unstable geometry remains.
  if (rng) for (const [aName,bName] of [['home','meadow'],['home','tree'],['meadow','windmill'],['temple','windmill'],['tree','lookout']]) {
    const a=islands.find(i=>i.name===aName),b=islands.find(i=>i.name===bName);
    const span=a.pos.distanceTo(b.pos)-(a.r-0.4)-(b.r-0.4);
    const planks=Math.max(8,Math.round(span/0.85));
    for(let i=0;i<planks*2+1;i++) rng.float();
  }
  const defs=islands.map(i=>({name:i.name,x:i.pos.x,y:i.pos.y,z:i.pos.z,r:i.r}));
  const plans=planWalkways(defs),colliders=[],bridges=[],barriers=plans.flatMap(p=>p.barriers);
  const deckMat=toonMaterial(0xc9c2bc,{side:THREE.DoubleSide});
  const woodMat=toonMaterial(0xa385a3), trimMat=toonMaterial(0xffebd2);
  for(const plan of plans) {
    const group=new THREE.Group();group.name=`skywalk-${plan.id}`;
    const positions=[],indices=[];
    for(const e of plan.edges) for(const v of [e.left,e.right]) positions.push(v.x,v.y,v.z);
    for(let i=0;i<plan.edges.length-1;i++){const j=i*2;indices.push(j,j+2,j+1,j+1,j+2,j+3);}
    const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geo.setIndex(indices);geo.computeVertexNormals();
    const deck=new THREE.Mesh(geo,deckMat);deck.userData.walkway=plan.id;deck.name=`deck-${plan.id}`;
    group.add(deck);colliders.push(deck);
    const wood=[],trim=[];
    const beam=(a,b,y,width,height,target) => {
      const start=new THREE.Vector3(a.x,a.y+y,a.z),end=new THREE.Vector3(b.x,b.y+y,b.z);
      const delta=end.clone().sub(start),g=new THREE.BoxGeometry(width,height,delta.length()+0.025);
      const matrix=new THREE.Matrix4().compose(start.clone().lerp(end,0.5),
        new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,0,1),delta.normalize()),new THREE.Vector3(1,1,1));
      g.applyMatrix4(matrix);target.push(g);
    };
    for(const wall of plan.barriers) {
      beam(wall.a,wall.b,-0.14,0.18,0.28,wood);
      for(const y of [0.4,0.8]) beam(wall.a,wall.b,y,0.14,0.15,wood);
      beam(wall.a,wall.b,1.25,0.2,0.14,trim);
      const count=Math.ceil(Math.hypot(wall.b.x-wall.a.x,wall.b.z-wall.a.z)/2);
      for(let i=0;i<=count;i++) {
        const t=i/count,p=new THREE.Vector3().lerpVectors(wall.a,wall.b,t);
        const post=new THREE.BoxGeometry(0.17,1.28,0.17);post.translate(p.x,p.y+0.63,p.z);wood.push(post);
      }
    }
    // Surface seams are visual markings, never separate collision planks.
    for(let i=1;i<plan.points.length;i++) {
      const a=plan.points[i-1],b=plan.points[i],length=Math.hypot(b.x-a.x,b.z-a.z);
      for(let d=1;d<length-0.7;d+=1.1) {
        const t=d/length,l=new THREE.Vector3().lerpVectors(plan.edges[i-1].left,plan.edges[i].left,t);
        const r=new THREE.Vector3().lerpVectors(plan.edges[i-1].right,plan.edges[i].right,t);
        beam(l,r,0.012,0.025,0.015,trim);
      }
    }
    for(const [parts,mat] of [[wood,woodMat],[trim,trimMat]]) {
      group.add(new THREE.Mesh(mergeGeometries(parts),mat));parts.forEach(g=>g.dispose());
    }
    scene.add(group);bridges.push({group,plan});
  }
  scene.updateMatrixWorld(true);
  return {bridges,plans,colliders,barriers,width:WALKWAY.width,update() { /* rigid decks */ }};
}
