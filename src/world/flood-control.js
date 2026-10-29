// MIT. G-only Blender asset. Visible art, dry ground, walls and camera shells are separate.
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {stationHeadroom} from './station-model.js';
import plan from '../data/flood-control-plan.json' with {type:'json'};
import collision from '../data/flood-control-collision.json' with {type:'json'};
export async function loadFloodControl(){
 const begin=performance.now(),url='/models/flood-control-g/flood-control-g.glb',r=await fetch(url);if(!r.ok)throw Error(`G asset download failed ${r.status}`);
 const bytes=await r.arrayBuffer(),download=performance.now(),gltf=await new GLTFLoader().parseAsync(bytes,url.slice(0,url.lastIndexOf('/')+1));
 gltf.scene.userData.loadStats={bytes:bytes.byteLength,downloadMilliseconds:download-begin,decodeMilliseconds:performance.now()-download,totalMilliseconds:performance.now()-begin};return gltf.scene;
}
export function buildFloodControl(source,island){
 if(!source)throw Error('G Blender park required');const begin=performance.now(),group=new THREE.Group();group.name='policy-place-crystal';group.userData.blenderFloodControl=true;group.add(source);island.group.add(group);
 const material=new THREE.MeshBasicMaterial({side:THREE.DoubleSide}),colliders=[],ceilings=[],cameraObstacles=[];
 function chunks(values,list,name){const cells=new Map();for(let i=0;i<values.length;i+=9){const key=`${Math.floor(values[i]/6)},${Math.floor(values[i+2]/6)}`;if(!cells.has(key))cells.set(key,[]);cells.get(key).push(...values.slice(i,i+9));}for(const v of cells.values()){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(v,3));g.computeVertexNormals();g.computeBoundingBox();g.computeBoundingSphere();const m=new THREE.Mesh(g,material);m.visible=false;m.name=name;m.userData.island='crystal';group.add(m);list.push(m);}}
 chunks(collision.groundPositions,colliders,'G-dry-ground-only');chunks(collision.ceilingPositions,ceilings,'G-roof-soffit');chunks(collision.cameraPositions,cameraObstacles,'G-structural-camera');
 const barriers=[];for(const s of collision.solids){const pairs=s.segment?[s.segment]:s.polygon.map((p,i)=>[p,s.polygon[(i+1)%s.polygon.length]]);for(const[a,b]of pairs)barriers.push({a:{x:a[0]+island.pos.x,y:s.base,z:a[1]+island.pos.z},b:{x:b[0]+island.pos.x,y:s.base,z:b[1]+island.pos.z},height:s.top-s.base,thickness:s.thickness??.025,capsuleHeight:1.6,kind:'flood-control-solid',island:'crystal',source:s.name});}
 const meshes=[],materials=new Set();let triangles=0;source.traverse(o=>{if(!o.isMesh)return;o.userData.island='crystal';meshes.push(o);triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;const ms=Array.isArray(o.material)?o.material:[o.material];ms.forEach(m=>materials.add(m));o.receiveShadow=true;o.castShadow=!ms.some(m=>m.transparent||/water|glass|blossom/i.test(m.name));});
 group.updateWorldMatrix(true,true);const bounds=new THREE.Box3().setFromObject(source,true),head=stationHeadroom(ceilings,bounds,1.6);
 return{group,source,meshes,pickMeshes:meshes,colliders,ceilings,barriers,cameraObstacles,bounds,config:{...plan,kind:'blender-flood-park',npc:plan.npc},constrainHead:head,stats:{...source.userData.loadStats,triangles,runtimeMeshes:meshes.length,materials:materials.size,buildMilliseconds:performance.now()-begin,waterCollision:false,newLights:0}};
}
