// Integrates the supplied, unmodified Blender GLB. MIT repository model.
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import config from '../data/station-model.json' with {type:'json'};
export const STATION_MODEL=config;
export async function loadStationModel(){return(await new GLTFLoader().loadAsync(config.url)).scene;}

// Source meshes are merged by material, not by purpose. Split touching vertices
// to select entire disconnected source parts (e.g. canopy posts, not sleepers).
export function components(geometry){
 const p=geometry.attributes.position,idx=geometry.index,triCount=(idx?.count??p.count)/3,parent=Array.from({length:triCount},(_,i)=>i),first=new Map();
 const root=i=>{while(parent[i]!==i){parent[i]=parent[parent[i]];i=parent[i];}return i;};
 const vertex=i=>idx?idx.getX(i):i;
 for(let t=0;t<triCount;t++)for(let j=0;j<3;j++){const v=vertex(t*3+j),key=`${Math.round(p.getX(v)*1e5)},${Math.round(p.getY(v)*1e5)},${Math.round(p.getZ(v)*1e5)}`;if(first.has(key))parent[root(t)]=root(first.get(key));else first.set(key,t);}
 const groups=new Map();for(let t=0;t<triCount;t++){const r=root(t);if(!groups.has(r))groups.set(r,[]);groups.get(r).push(...[0,1,2].map(j=>vertex(t*3+j)));}
 return[...groups.values()].map(indices=>{const g=new THREE.BufferGeometry();for(const[name,a]of Object.entries(geometry.attributes)){const out=new Float32Array(indices.length*a.itemSize);indices.forEach((v,i)=>{for(let j=0;j<a.itemSize;j++)out[i*a.itemSize+j]=a.array[v*a.itemSize+j];});g.setAttribute(name,new THREE.BufferAttribute(out,a.itemSize));}g.computeBoundingBox();return g;});
}
function selectedParts(mesh){
 const g=mesh.geometry.clone().applyMatrix4(mesh.matrixWorld),name=mesh.name;
 if(name.startsWith('Architecture__')||name==='Station_interior_floor'||name==='Attached_platform_roof'||name==='Platform__Woven_timber'||name==='Terrain__Woven_timber')return[g];
 if(name==='Platform__Oiled_oak'||name==='Wayfinding__Train_blue_stripe'||name==='Wayfinding__Dark_teal_metal'){
  const all=components(g),keep=[];for(const part of all){const b=part.boundingBox,yes=name==='Platform__Oiled_oak'?b.max.y>1:b.max.z<-.6&&b.min.y>2.5;if(yes)keep.push(part);else part.dispose();}g.dispose();return keep;
 }
 g.dispose();return[];
}
export function buildStationModel(source){
 if(!source)throw new Error('The supplied Blender station GLB must be loaded before building transport');
 source.updateMatrixWorld(true);const group=new THREE.Group();group.name='blender-station';const meshes=[],colliders=[],cameraObstacles=[],barriers=[],seen=new Set(),included=[];
 const transform=new THREE.Matrix4().compose(new THREE.Vector3(...config.position),new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),config.yaw),new THREE.Vector3().setScalar(config.scale));
 source.traverse(node=>{if(!node.isMesh)return;const parts=selectedParts(node);if(!parts.length)return;const normalized=parts.map(g=>g.index?g.toNonIndexed():g),geometry=mergeGeometries(normalized);geometry.applyMatrix4(transform);for(const g of new Set([...parts,...normalized]))g.dispose();const mesh=new THREE.Mesh(geometry,node.material);mesh.name=node.name;mesh.userData.island='home';mesh.userData.stationModel=true;group.add(mesh);meshes.push(mesh);included.push(node.name);
  // No display terrain, static train, text or leaves become ground/camera obstacles.
  if(!node.name.startsWith('Wayfinding')){colliders.push(mesh);if(node.name!=='Terrain__Woven_timber')cameraObstacles.push(mesh);}
  if(!node.name.startsWith('Architecture__')&&!node.name.startsWith('Platform__Woven')&&!node.name.startsWith('Platform__Oiled'))return;
  if(/Roof|Standing_seam|Glazing_reflection|Dark_teal_metal/.test(node.name))return;
  const p=geometry.attributes.position,a=new THREE.Vector3(),b=new THREE.Vector3(),c=new THREE.Vector3(),normal=new THREE.Vector3();
  for(let i=0;i<p.count;i+=3){a.fromBufferAttribute(p,i);b.fromBufferAttribute(p,i+1);c.fromBufferAttribute(p,i+2);normal.crossVectors(b.clone().sub(a),c.clone().sub(a));const n=normal.length();if(n<1e-9||Math.abs(normal.y/n)>.08)continue;const base=Math.min(a.y,b.y,c.y),top=Math.max(a.y,b.y,c.y);if(top<.3||top-base<.28)continue;
   const pairs=[[a,b],[b,c],[c,a]].sort((u,v)=>Math.hypot(v[0].x-v[1].x,v[0].z-v[1].z)-Math.hypot(u[0].x-u[1].x,u[0].z-u[1].z));let[u,v]=pairs[0];if(Math.hypot(u.x-v.x,u.z-v.z)<.025)continue;if(u.x>v.x||(u.x===v.x&&u.z>v.z))[u,v]=[v,u];const key=[u.x,u.z,v.x,v.z,base,top].map(v=>v.toFixed(4)).join(',');if(seen.has(key))continue;seen.add(key);
   // Existing guard solver uses head=1.5 + margin=.2. This local base adapter
   // matches the unchanged character's 1.60 head envelope, leaving real doors open.
   barriers.push({a:{x:u.x,y:base+config.guardBaseBias,z:u.z},b:{x:v.x,y:base+config.guardBaseBias,z:v.z},height:top-base-config.guardBaseBias,kind:'glb-station',source:node.name,actualBase:base});
  }
 });
 group.updateMatrixWorld(true);const bounds=new THREE.Box3().setFromObject(group,true);let triangles=0;for(const m of meshes)triangles+=m.geometry.attributes.position.count/3;
 return{group,meshes,colliders,cameraObstacles,barriers,included,bounds,triangles,config,constrainHead:stationHeadroom(colliders,bounds,config.capsuleHeight)};
}

// Only rising movement near this imported building. Sample the visible head's
// footprint against actual downward-facing model surfaces, not a bounding box.
// Other islands retain the existing movement and ground rules.
export function stationHeadroom(meshes,bounds,height){
 const ray=new THREE.Raycaster(),up=new THREE.Vector3(0,1,0),origin=new THREE.Vector3();
 const offsets=[[0,0],[.22,0],[-.22,0],[0,.22],[0,-.22]];
 return(position,previousY,move)=>{
  if(move.vy<=0||position.y<=previousY||position.x<bounds.min.x-.3||position.x>bounds.max.x+.3||position.z<bounds.min.z-.3||position.z>bounds.max.z+.3)return false;
  let allowed=position.y;ray.far=position.y-previousY+.012;
  for(const[dx,dz]of offsets){origin.set(position.x+dx,previousY+height,position.z+dz);ray.set(origin,up);
   for(const hit of ray.intersectObjects(meshes,false))if(hit.face.normal.y<-.2){allowed=Math.min(allowed,hit.point.y-height-.005);break;}
  }
  if(allowed>=position.y)return false;
  position.y=Math.max(previousY,allowed);move.vy=0;return true;
 };
}
