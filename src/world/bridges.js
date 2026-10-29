// One shared Boolean-unioned domain: no internal fences at any road junction.
import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { toonMaterial } from './toon.js';
import layout from '../data/yuan-layout.json' with { type: 'json' };
import surface from '../data/yuan-surface.json' with { type: 'json' };
import { guardIndex } from '../sim/walkways.js';

export function buildBridges(scene, islands, rng) {
 // Consume the ORIGINAL seed stream, independent of the new island positions.
 const old={home:[0,0,0,9],meadow:[-14,3,18,6],tree:[26,5,-14,7],windmill:[-30,8,4,6],temple:[-24,10,-20,8],lookout:[2,14,-30,5]};
 if(rng)for(const [a,b] of [['home','meadow'],['home','tree'],['meadow','windmill'],['temple','windmill'],['tree','lookout']]){
 const p=old[a],q=old[b],span=Math.hypot(p[0]-q[0],p[1]-q[1],p[2]-q[2])-(p[3]-.4)-(q[3]-.4);
 for(let i=0;i<Math.max(8,Math.round(span/.85))*2+1;i++)rng.float();
 }
 const group=new THREE.Group();group.name='yuan-shared-walkways';
 const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(surface.positions,3));geo.setIndex(surface.indices);geo.computeVertexNormals();
 const deck=new THREE.Mesh(geo,toonMaterial(0xbeb8a7,{side:THREE.DoubleSide}));deck.name='shared-deck';deck.userData.walkway='shared-yuan-domain';group.add(deck);
 // Island transit paving is clipped from these same fixed centreline ribbons.
 // It joins the bridge deck exactly and stays separate from landscaped courts.
 for(const patch of surface.islandPaving){if(patch.island==='tree'||patch.island==='home')continue;const isle=islands.find(i=>i.name===patch.island);if(!isle)continue;const pieces=[];
 for(const rings of patch.domain){const shape=new THREE.Shape(rings[0].slice(0,-1).map(p=>new THREE.Vector2(p[0],-p[1])));for(const hole of rings.slice(1))shape.holes.push(new THREE.Path(hole.slice(0,-1).map(p=>new THREE.Vector2(p[0],-p[1]))));const g=new THREE.ShapeGeometry(shape);g.rotateX(-Math.PI/2);g.translate(-isle.pos.x,.015,-isle.pos.z);pieces.push(g);}
 if(pieces.length){const mesh=new THREE.Mesh(mergeGeometries(pieces),toonMaterial(0xbeb8a7));mesh.name='island-transit-paving';mesh.userData.island=patch.island;isle.group.add(mesh);pieces.forEach(p=>p.dispose());}
 }
 const wood=toonMaterial(0x66807e),trim=toonMaterial(0xd4c8ad),chunks=new Map();
 function beam(a,b,y,width,height,parts){
 const start=new THREE.Vector3(a.x,a.y+y,a.z),end=new THREE.Vector3(b.x,b.y+y,b.z),d=end.clone().sub(start);
 if(d.length()<.0001)return;
 const g=new THREE.BoxGeometry(width,height,d.length()+.006);
 g.applyMatrix4(new THREE.Matrix4().compose(start.lerp(end,.5),new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,0,1),d.normalize()),new THREE.Vector3(1,1,1)));parts.push(g);
 }
 let postDistance=0;
 for(const wall of surface.barriers){
 if(wall.island==='home')continue; // V9 authored boundary owns this plinth only.
 const key=`${Math.floor((wall.a.x+wall.b.x)/64)},${Math.floor((wall.a.z+wall.b.z)/64)}`;
 if(!chunks.has(key))chunks.set(key,[[],[]]);const [body,top]=chunks.get(key);
 const islandEdge=wall.kind==='island-edge';
 beam(wall.a,wall.b,islandEdge?.23:-.1,islandEdge?.18:.16,islandEdge?.46:.2,top);
 beam(wall.a,wall.b,1.22,.055,.065,body);
 if(!islandEdge)beam(wall.a,wall.b,.64,.035,.045,body);
 const distance=Math.hypot(wall.a.x-wall.b.x,wall.a.z-wall.b.z);
 // Sampling points are geometry tessellation, not a reason to repeat heavy posts.
 if(postDistance>=2.1||distance>1.9){const p=wall.a,g=new THREE.BoxGeometry(.055,1.26,.055);g.translate(p.x,p.y+.63,p.z);body.push(g);postDistance=0;}
 postDistance+=distance;
 }
 for(const parts of chunks.values())for(let i=0;i<2;i++)if(parts[i].length){const mesh=new THREE.Mesh(mergeGeometries(parts[i]),i?trim:wood);group.add(mesh);parts[i].forEach(g=>g.dispose());}
 scene.add(group);scene.updateMatrixWorld(true);
 return {group,bridges:[{group}],plans:layout.paths,nodes:layout.nodes,colliders:[deck],barriers:surface.barriers.filter(w=>w.island!=='home'),nearby:guardIndex(surface.barriers.filter(w=>w.island!=='home')),width:layout.width,bounds:layout.bounds,domain:surface.domain,update(){}};
}
