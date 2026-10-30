// MIT. User-approved V2.2 C campus: separate visible asset, floor, solids and camera.
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {stationHeadroom} from './station-model.js';
import plan from '../data/industry-youth-plan.json' with {type:'json'};
import collision from '../data/industry-youth-collision.json' with {type:'json'};

export async function loadIndustryYouth(){
 const begin=performance.now(),url='/models/industry-youth-c/industry-youth-c.glb',r=await fetch(url);
 if(!r.ok)throw Error(`C campus download failed ${r.status}`);
 const bytes=await r.arrayBuffer(),download=performance.now(),gltf=await new GLTFLoader().parseAsync(bytes,'/models/industry-youth-c/');
 gltf.scene.userData.loadStats={bytes:bytes.byteLength,downloadMilliseconds:download-begin,decodeMilliseconds:performance.now()-download,totalMilliseconds:performance.now()-begin};return gltf.scene;
}
export function buildIndustryYouth(source,island){
 if(!source)throw Error('C campus GLB required');const group=new THREE.Group();group.name='policy-place-koi';group.add(source);island.group.add(group);
 const material=new THREE.MeshBasicMaterial({side:THREE.DoubleSide}),colliders=[],ceilings=[],cameraObstacles=[];
 function chunks(values,list,name){
  const cells=new Map();for(let i=0;i<values.length;i+=9){const key=`${Math.floor(values[i]/6)},${Math.floor(values[i+2]/6)}`;if(!cells.has(key))cells.set(key,[]);cells.get(key).push(...values.slice(i,i+9));}
  for(const v of cells.values()){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(v,3));g.computeVertexNormals();g.computeBoundingSphere();const m=new THREE.Mesh(g,material);m.visible=false;m.name=name;m.userData={island:'koi',noCheckpoint:name!=='C-dry-ground'};if(name==='C-real-roof-support')m.userData.support='roof';group.add(m);list.push(m);}
 }
 chunks(collision.groundPositions,colliders,'C-dry-ground');chunks(collision.supportPositions,colliders,'C-solid-top');chunks(collision.roofPositions,colliders,'C-real-roof-support');chunks(collision.ceilingPositions,ceilings,'C-real-soffit');chunks(collision.cameraPositions,cameraObstacles,'C-structural-camera');
 const barriers=[];for(const s of collision.solids)for(let i=0;i<s.polygon.length;i++){const a=s.polygon[i],b=s.polygon[(i+1)%s.polygon.length];barriers.push({a:{x:a[0]+island.pos.x,y:s.base,z:a[1]+island.pos.z},b:{x:b[0]+island.pos.x,y:s.base,z:b[1]+island.pos.z},height:s.top-s.base,thickness:.015,capsuleHeight:1.6,kind:'industry-solid',island:'koi',source:s.name});}
 const meshes=[],materials=new Set();let triangles=0;source.traverse(o=>{if(!o.isMesh)return;o.userData.island='koi';meshes.push(o);triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;for(const m of(Array.isArray(o.material)?o.material:[o.material]))materials.add(m);o.receiveShadow=true;o.castShadow=!(Array.isArray(o.material)?o.material:[o.material]).some(m=>m.transparent);});
 group.updateWorldMatrix(true,true);const bounds=new THREE.Box3().setFromObject(source,true);
 return{group,source,meshes,pickMeshes:meshes,colliders,ceilings,barriers,cameraObstacles,bounds,config:plan,constrainHead:stationHeadroom(ceilings,bounds,1.6),stats:{...source.userData.loadStats,triangles,runtimeMeshes:meshes.length,materials:materials.size,newLights:0}};
}

// Covered approaches must not push the camera into the character's head.
// Keep orbit state untouched; use a nearby clear orbit ray, then a low porch
// sight line only if the original high sight line has no room. Remember the
// chosen offset to avoid alternating sides while walking under a beam.
export function industryCameraConstraint(constrain,island,getOrbit){
 let lastOffset=0;
 const wrapped=(target,position)=>{
  const desired=position.clone(),blocked=constrain(target,position);
  if(!blocked||Math.hypot(target.x-island.pos.x,target.z-island.pos.z)>16||position.distanceTo(target)>3.2)return blocked;
  const o=getOrbit?.(),dx=desired.x-target.x,dz=desired.z-target.z,r=o?Math.cos(o.pitch)*o.dist:Math.max(6,Math.hypot(dx,dz)),yaw=o?.yaw??Math.atan2(dx,dz);
  let best=position.clone(),offset=lastOffset;
  outer:for(const height of[o?target.y+Math.sin(o.pitch)*o.dist:desired.y,target.y+.3]){
   for(const a of new Set([lastOffset,0,-.35,.35,-.7,.7,-1.05,1.05])){
    const candidate=new THREE.Vector3(target.x+Math.sin(yaw+a)*r,height,target.z+Math.cos(yaw+a)*r);constrain(target,candidate);
    if(candidate.distanceTo(target)>best.distanceTo(target)+.15){best=candidate;offset=a;}
    if(best.distanceTo(target)>Math.min(6,r*.7))break outer;
   }
  }
  lastOffset=offset;position.copy(best);return blocked;
 };wrapped.stats=constrain.stats;return wrapped;
}
