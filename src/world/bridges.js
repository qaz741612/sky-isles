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
 const deck=new THREE.Mesh(geo,toonMaterial(0xc9c2bc,{side:THREE.DoubleSide}));deck.name='shared-deck';deck.userData.walkway='shared-yuan-domain';group.add(deck);
 const wood=toonMaterial(0xa385a3),trim=toonMaterial(0xffebd2),chunks=new Map();
 function beam(a,b,y,width,height,parts){
 const start=new THREE.Vector3(a.x,a.y+y,a.z),end=new THREE.Vector3(b.x,b.y+y,b.z),d=end.clone().sub(start);
 if(d.length()<.0001)return;
 const g=new THREE.BoxGeometry(width,height,d.length()+.006);
 g.applyMatrix4(new THREE.Matrix4().compose(start.lerp(end,.5),new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,0,1),d.normalize()),new THREE.Vector3(1,1,1)));parts.push(g);
 }
 for(const wall of surface.barriers){
 const key=`${Math.floor((wall.a.x+wall.b.x)/64)},${Math.floor((wall.a.z+wall.b.z)/64)}`;
 if(!chunks.has(key))chunks.set(key,[[],[]]);const [body,top]=chunks.get(key);
 beam(wall.a,wall.b,-.14,.18,.28,body);
 for(const y of [.4,.8])beam(wall.a,wall.b,y,.14,.15,body);
 beam(wall.a,wall.b,1.25,.2,.14,top);
 const p=wall.a,g=new THREE.BoxGeometry(.17,1.28,.17);g.translate(p.x,p.y+.63,p.z);body.push(g);
 }
 for(const parts of chunks.values())for(let i=0;i<2;i++)if(parts[i].length){const mesh=new THREE.Mesh(mergeGeometries(parts[i]),i?trim:wood);group.add(mesh);parts[i].forEach(g=>g.dispose());}
 scene.add(group);scene.updateMatrixWorld(true);
 return {group,bridges:[{group}],plans:layout.paths,nodes:layout.nodes,colliders:[deck],barriers:surface.barriers,nearby:guardIndex(surface.barriers),width:layout.width,bounds:layout.bounds,domain:surface.domain,update(){}};
}
