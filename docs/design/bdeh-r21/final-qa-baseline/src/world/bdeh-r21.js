// MIT. User R21 architecture: visible Blender assets, public floors, structural
// solids and camera shells are separate. No research terrain/rail placeholders.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { stationHeadroom } from './station-model.js';
import { floodCameraConstraint } from './flood-control.js';
import plan from '../data/bdeh-plan.json' with {type:'json'};
import B from '../data/bdeh-b-collision.json' with {type:'json'};
import D from '../data/bdeh-d-collision.json' with {type:'json'};
import E from '../data/bdeh-e-collision.json' with {type:'json'};
import H from '../data/bdeh-h-collision.json' with {type:'json'};
const collisions={B,D,E,H};
export async function loadR21Models(){
 return Object.fromEntries(await Promise.all(Object.keys(plan.islands).map(async code=>{
  const begin=performance.now(),url=`/models/bdeh-r21/${code}.glb`,response=await fetch(url);if(!response.ok)throw Error(`R21 ${code} model HTTP ${response.status}`);
  const bytes=await response.arrayBuffer(),download=performance.now(),gltf=await new GLTFLoader().parseAsync(bytes,'/models/bdeh-r21/');
  gltf.scene.userData.loadStats={bytes:bytes.byteLength,downloadMilliseconds:download-begin,decodeMilliseconds:performance.now()-download,totalMilliseconds:performance.now()-begin};return[code,gltf.scene];
 })));
}
export function buildR21Places(sources,islands){
 return Object.fromEntries(Object.entries(plan.islands).map(([code,config])=>{
  const begin=performance.now(),island=islands.find(i=>i.name===config.name),source=sources[code],data=collisions[code];if(!island||!source)throw Error(`Missing R21 ${code}`);
  const group=new THREE.Group();group.name=`policy-place-${config.name}`;group.userData.blenderR21=code;group.add(source);island.group.add(group);
  const colliders=[],ceilings=[],cameraObstacles=[],hidden=new THREE.MeshBasicMaterial({side:THREE.DoubleSide});
  function chunks(values,list,name,publicFloor=false){
   const cells=new Map();for(let i=0;i<values.length;i+=9){const key=`${Math.floor(values[i]/6)},${Math.floor(values[i+2]/6)}`;if(!cells.has(key))cells.set(key,[]);cells.get(key).push(...values.slice(i,i+9));}
   for(const v of cells.values()){
    const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(v,3));g.computeVertexNormals();g.computeBoundingBox();g.computeBoundingSphere();const mesh=new THREE.Mesh(g,hidden);mesh.visible=false;mesh.name=`R21-${code}-${name}`;mesh.userData={noCheckpoint:!publicFloor,ownerIsland:config.name};
    if(publicFloor)mesh.userData.walkway=`R21-${code}-authored-public-land`;
    if(name==='roof-support'){mesh.userData.support='roof';mesh.userData.island=config.name;}
    group.add(mesh);list.push(mesh);
   }
  }
  chunks(data.groundPositions,colliders,'public-ground',true);chunks(data.supportPositions,colliders,'physical-top-support');chunks(data.roofPositions??[],colliders,'roof-support');chunks(data.ceilingPositions,ceilings,'real-soffit');chunks(data.cameraPositions,cameraObstacles,'structural-camera');
  const barriers=[];
  for(const solid of data.solids)for(const ring of[solid.polygon,...solid.holes])for(let i=0;i<ring.length;i++){
   const a=ring[i],b=ring[(i+1)%ring.length];if(Math.hypot(a[0]-b[0],a[1]-b[1])<1e-6)continue;
   barriers.push({a:{x:a[0]+island.pos.x,y:solid.base,z:a[1]+island.pos.z},b:{x:b[0]+island.pos.x,y:solid.base,z:b[1]+island.pos.z},height:solid.top-solid.base,thickness:.012,capsuleHeight:1.6,kind:'r21-real-solid',island:config.name,source:solid.name});
  }
  const meshes=[],materials=new Set();let triangles=0;
  source.traverse(o=>{if(!o.isMesh)return;meshes.push(o);o.userData.island=config.name;triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;const ms=Array.isArray(o.material)?o.material:[o.material];ms.forEach(m=>{materials.add(m);if(m.transparent){m.depthWrite=false;m.side=THREE.DoubleSide;}});o.receiveShadow=true;o.castShadow=!ms.some(m=>m.transparent);});
  group.updateWorldMatrix(true,true);const bounds=new THREE.Box3().setFromObject(source,true);
  return[code,{group,source,meshes,pickMeshes:meshes,colliders,ceilings,cameraObstacles,barriers,bounds,config,constrainHead:stationHeadroom(ceilings,bounds,1.6),stats:{...source.userData.loadStats,triangles,runtimeMeshes:meshes.length,materials:materials.size,buildMilliseconds:performance.now()-begin,scale:1,newLights:0}}];
 }));
}
export function r21CameraConstraint(constrain,places,getOrbit){
 // Reuse the existing six-probe algorithm without changing G's module or its
 // current wrapper. Each new island keeps its own stable local offset state.
 const wrappers=Object.values(places).map(place=>({centre:place.config.centre,apply:floodCameraConstraint(constrain,{pos:place.group.parent.position},getOrbit)}));
 const wrapped=(target,position)=>{
  const entry=wrappers.find(w=>Math.hypot(target.x-w.centre[0],target.z-w.centre[2])<24);
  return entry?entry.apply(target,position):constrain(target,position);
 };wrapped.stats=constrain.stats;return wrapped;
}
