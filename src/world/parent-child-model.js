// Approved PR11 asset. Only diorama bridge arms/rail interfaces are replaced. MIT.
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {components,stationHeadroom} from './station-model.js';
import config from '../data/parent-child-model.json' with {type:'json'};
import collision from '../data/parent-child-collision.json' with {type:'json'};
export const PARENT_CHILD_MODEL=config;
export async function loadParentChildModel(onProgress){
 const start=performance.now();const scene=(await new GLTFLoader().loadAsync(config.url,onProgress)).scene;
 scene.userData.loadMilliseconds=performance.now()-start;return scene;
}
function meshFromPositions(positions,name){
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));g.computeVertexNormals();g.computeBoundingBox();g.computeBoundingSphere();
 const mesh=new THREE.Mesh(g,new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));mesh.name=name;mesh.visible=false;mesh.userData.island='tree';return mesh;
}
function triangleChunks(positions,name,parent,size=4){
 const buckets=new Map();for(let i=0;i<positions.length;i+=9){const x=(positions[i]+positions[i+3]+positions[i+6])/3,z=(positions[i+2]+positions[i+5]+positions[i+8])/3,key=`${Math.floor(x/size)},${Math.floor(z/size)}`;if(!buckets.has(key))buckets.set(key,[]);buckets.get(key).push(...positions.slice(i,i+9));}
 return [...buckets.values()].map((p,i)=>{const m=meshFromPositions(p,`${name}-${i}`);parent.add(m);return m;});
}
function prismPositions(s){
 const shape=new THREE.Shape(s.polygon.map(([x,z])=>new THREE.Vector2(x,-z))),g=new THREE.ExtrudeGeometry(shape,{depth:s.top-s.base,bevelEnabled:false});g.rotateX(-Math.PI/2);g.translate(0,s.base,0);const out=Array.from(g.attributes.position.array);g.dispose();return out;
}
export function buildParentChildModel(source,island){
 if(!source)throw Error('Approved parent-child GLB is required');
 const started=performance.now();source.updateMatrixWorld(true);const group=new THREE.Group();group.name='policy-place-tree';group.userData.approvedParentChild=true;group.userData.layout=config;island.group.add(group);
 const bins=new Map(),meshes=[],excluded=[],retained=[],roleFor=node=>{let p=node;while(p.parent&&p.parent!==source.children[0]&&p.parent!==source)p=p.parent;return p.name;};
 let sourceTriangles=0,selectedTriangles=0,sourceMeshes=0;
 source.traverse(node=>{
  if(!node.isMesh)return;sourceMeshes++;sourceTriangles+=(node.geometry.index?.count??node.geometry.attributes.position.count)/3;
  const role=roleFor(node),site=role.startsWith('SiteAndBridgeStubs');
  if(site&&node.material.name==='rail'){excluded.push({name:node.name,reason:'Display-only perimeter/bridge rails replaced by actual shared-domain safety boundary'});return;}
  const transformed=node.geometry.clone().applyMatrix4(node.matrixWorld);
  let parts=[transformed];
  if(site){parts=components(transformed);transformed.dispose();parts=parts.filter(g=>{const p=g.attributes.position;let r=0;for(let i=0;i<p.count;i++)r=Math.max(r,Math.hypot(p.getX(i),p.getZ(i)));if(r<=config.radius+.026)return true;excluded.push({name:node.name,reason:'Display bridge arm; actual game bridges stay in place'});g.dispose();return false;});}
  if(!parts.length)return;
  const material=node.material;retained.push(node.name);
  for(const geometry of parts){selectedTriangles+=(geometry.index?.count??geometry.attributes.position.count)/3;
   // Opaque batching is lossless. Glass retains original assembly sorting.
   const key=`${role}:${material.uuid}:${material.transmission>0?node.uuid:''}`;
   if(!bins.has(key))bins.set(key,{role,material,geometries:[]});bins.get(key).geometries.push(geometry);
  }
 });
 for(const {role,material,geometries}of bins.values()){
  const normalized=geometries.map(g=>{if(!g.index)g.setIndex(Array.from({length:g.attributes.position.count},(_,i)=>i));return g;}),geometry=mergeGeometries(normalized);for(const g of new Set([...geometries,...normalized]))g.dispose();geometry.computeBoundingBox();geometry.computeBoundingSphere();
  const mesh=new THREE.Mesh(geometry,material);mesh.name=`parent-child-${role}-${material.name}`;mesh.userData.island='tree';mesh.userData.approvedParentChild=true;mesh.userData.role=role;mesh.castShadow=!(material.transmission>0);mesh.receiveShadow=true;group.add(mesh);meshes.push(mesh);
 }
 const proxyGroup=new THREE.Group();proxyGroup.name='parent-child-invisible-physics';group.add(proxyGroup);
 const colliders=triangleChunks(collision.groundPositions,'family-ground',proxyGroup),ceilings=triangleChunks(collision.ceilingPositions,'family-headroom',proxyGroup);
 // Paver top / continuous interface under the actual geometry. No model floors are moved.
 const floor=new THREE.Mesh(new THREE.CircleGeometry(config.radius,128),new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));floor.rotation.x=-Math.PI/2;floor.position.y=.03;floor.visible=false;floor.userData.island='tree';proxyGroup.add(floor);colliders.push(floor);
 const barriers=[];for(const solid of collision.solids)for(let i=0;i<solid.polygon.length;i++){
  const a=solid.polygon[i],b=solid.polygon[(i+1)%solid.polygon.length];if(Math.hypot(a[0]-b[0],a[1]-b[1])<.002)continue;
  barriers.push({a:{x:a[0]+island.pos.x,y:solid.base+.1,z:a[1]+island.pos.z},b:{x:b[0]+island.pos.x,y:solid.base+.1,z:b[1]+island.pos.z},height:solid.top-solid.base-.1,thickness:0,kind:'parent-child-solid',island:'tree',source:solid.name,actualBase:solid.base,actualTop:solid.top});
 }
 const cameraPositions=collision.cameraSolids.flatMap(prismPositions),cameraObstacles=triangleChunks(cameraPositions,'family-camera-structure',proxyGroup);
 group.updateWorldMatrix(true,true);const bounds=new THREE.Box3();for(const mesh of meshes)bounds.union(new THREE.Box3().setFromObject(mesh,true));
 const elapsed=performance.now()-started;
 return{group,meshes,colliders,barriers,cameraObstacles,pickMeshes:meshes,bounds,ceilings,constrainHead:stationHeadroom(ceilings,bounds,config.capsuleHeight),config,stats:{sourceTriangles,selectedTriangles,runtimeVertices:meshes.reduce((n,m)=>n+m.geometry.attributes.position.count,0),runtimeMeshes:meshes.length,sourceMeshes,selectedSourceMeshes:retained.length,excluded,sourceLoadMilliseconds:source.userData.loadMilliseconds,buildMilliseconds:elapsed},adaptPaths(paths){
  return paths.map(path=>{const local=config.access[path.id];if(!local)return path;
   const outward=local.map(([x,z])=>({x:x+island.pos.x,y:.03,z:z+island.pos.z})),incoming=path.to==='A',original=incoming?path.points.toReversed():path.points;
   const outside=original.filter(p=>Math.hypot(p.x-island.pos.x,p.z-island.pos.z)>11.6),points=[...outward.toReversed(),...outside];
   const walkPoints=incoming?points.toReversed():points;let walkLength=0;for(let i=1;i<walkPoints.length;i++)walkLength+=Math.hypot(walkPoints[i].x-walkPoints[i-1].x,walkPoints[i].z-walkPoints[i-1].z);
   return{...path,points:walkPoints,centrelineLength:path.length,walkLength,localDetour:'Approved building preserved; outdoor veranda/forecourt access within island only'};
  });
 }};
}

// Covered verandas are genuine walkable spaces. When an overhead eave would
// force the camera against the character, try a low sight line and small orbit
// offsets. The user's stored orbit/zoom and all other islands remain unchanged.
export function parentChildCameraConstraint(constrain,island){
 let lastOffset=0;
 const wrapped=(target,position)=>{
  const desired=position.clone(),blocked=constrain(target,position);
  if(!blocked||Math.hypot(target.x-island.pos.x,target.z-island.pos.z)>config.radius+1||position.distanceTo(target)>2.8)return blocked;
  const dx=desired.x-target.x,dz=desired.z-target.z,r=Math.max(6,Math.hypot(dx,dz)),yaw=Math.atan2(dx,dz);let best=position.clone(),offset=lastOffset;
  for(const a of new Set([lastOffset,0,.35,-.35,.7,-.7,1.05,-1.05])){
   const candidate=new THREE.Vector3(target.x+Math.sin(yaw+a)*r,target.y+.3,target.z+Math.cos(yaw+a)*r);constrain(target,candidate);
   if(candidate.distanceTo(target)>best.distanceTo(target)+.15){best=candidate;offset=a;}
   if(best.distanceTo(target)>3)break;
  }
  lastOffset=offset;position.copy(best);return blocked;
 };wrapped.stats=constrain.stats;return wrapped;
}
