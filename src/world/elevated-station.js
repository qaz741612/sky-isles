// MIT. Integrates the locked ca94f48 asset; visual art and physics are separate.
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {stationHeadroom} from './station-model.js';
import config from '../data/elevated-station-model.json' with {type:'json'};
import data from '../data/elevated-station-collision.json' with {type:'json'};
export const ELEVATED_STATION=config;
export async function loadElevatedStation(){
 const start=performance.now(),response=await fetch(config.url);
 if(!response.ok)throw new Error(`Station download failed: ${response.status}`);
 const bytes=await response.arrayBuffer(),downloaded=performance.now();
 let sha256=null;
 if(globalThis.crypto?.subtle){sha256=Array.from(new Uint8Array(await globalThis.crypto.subtle.digest('SHA-256',bytes)),n=>n.toString(16).padStart(2,'0')).join('');if(sha256!==config.sha256)throw new Error('Locked station SHA256 mismatch');}
 const gltf=await new GLTFLoader().parseAsync(bytes,config.url.slice(0,config.url.lastIndexOf('/')+1));
 gltf.scene.userData.loadStats={bytes:bytes.byteLength,sha256,downloadMilliseconds:downloaded-start,decodeMilliseconds:performance.now()-downloaded,totalMilliseconds:performance.now()-start};
 return gltf.scene;
}
const proxyMaterial=new THREE.MeshBasicMaterial({side:THREE.DoubleSide});
function triangleChunks(positions,parent,name){
 const chunks=new Map();
 for(let i=0;i<positions.length;i+=9){const key=`${Math.floor((positions[i]+positions[i+3]+positions[i+6])/12)},${Math.floor((positions[i+2]+positions[i+5]+positions[i+8])/12)}`;if(!chunks.has(key))chunks.set(key,[]);chunks.get(key).push(...positions.slice(i,i+9));}
 return [...chunks.values()].map(values=>{const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(values,3));g.computeVertexNormals();g.computeBoundingBox();g.computeBoundingSphere();const mesh=new THREE.Mesh(g,proxyMaterial);mesh.name=name;mesh.visible=false;mesh.userData={island:'home',noCheckpoint:true};parent.add(mesh);return mesh;});
}
function prism(s){
 const shape=new THREE.Shape(s.polygon.map(([x,z])=>new THREE.Vector2(x,-z)));
 const g=new THREE.ExtrudeGeometry(shape,{depth:s.top-s.base,bevelEnabled:false});g.rotateX(-Math.PI/2);g.translate(0,s.base,0);
 const mesh=new THREE.Mesh(g,proxyMaterial);mesh.name=`camera:${s.name}`;mesh.visible=false;return mesh;
}
function solidBarriers(s){return s.polygon.slice(1).map((b,i)=>({a:{x:s.polygon[i][0],y:s.base,z:s.polygon[i][1]},b:{x:b[0],y:s.base,z:b[1]},height:s.top-s.base,thickness:0,capsuleHeight:1.6,kind:s.kind,source:s.name}));}
export function buildElevatedStation(source){
 if(!source)throw new Error('Locked elevated station must load before world construction');
 const begin=performance.now(),group=new THREE.Group();group.name='elevated-station-v9';
 source.position.set(...config.position);source.rotation.y=config.yaw;source.scale.setScalar(config.scale);group.add(source);
 const meshes=[],materials=new Set();let triangles=0;
 source.traverse(o=>{if(!o.isMesh)return;o.userData.island='home';meshes.push(o);triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;for(const m of Array.isArray(o.material)?o.material:[o.material])materials.add(m);o.receiveShadow=true;o.castShadow=!(Array.isArray(o.material)?o.material:[o.material]).some(m=>m.transparent||/Leaf|Petal/i.test(m.name));});
 group.updateMatrixWorld(true);const bounds=new THREE.Box3().setFromObject(source,true);
 // The always-present foundation owns the public flat floor. Upper surfaces are
 // real support for deliberate jumps, but never become respawn checkpoints.
 const colliders=triangleChunks(data.groundPositions.slice(data.siteGroundFloats),group,'station-upper-support');
 const ceilings=triangleChunks(data.ceilingPositions,group,'station-headroom');
 const barriers=data.solids.flatMap(solidBarriers);
 for(const w of data.slopingGuards)barriers.push({a:{x:w.a[0],y:w.a[1],z:w.a[2]},b:{x:w.b[0],y:w.b[1],z:w.b[2]},height:w.height,thickness:w.thickness,capsuleHeight:1.6,kind:'stair-side',source:w.source});
 const cameraObstacles=data.cameraSolids.map(prism);cameraObstacles.forEach(m=>group.add(m));cameraObstacles.push(...ceilings);
 // Visible, matching safety additions only; no changes to the approved GLB.
 const parts=[];
 const box=(size,pos)=>{const g=new THREE.BoxGeometry(...size);g.translate(...pos);parts.push(g);};
 function rail(a,b,base,height,kind){
  const dx=b[0]-a[0],dz=b[1]-a[1],length=Math.hypot(dx,dz);
  for(const y of[base+.45,base+height]){const g=new THREE.BoxGeometry(.034,.034,length);g.rotateY(Math.atan2(dx,dz));g.translate((a[0]+b[0])/2,y,(a[1]+b[1])/2);parts.push(g);}
  const count=Math.ceil(length/1.4);for(let i=0;i<=count;i++)box([.045,height,.045],[a[0]+dx*i/count,base+height/2,a[1]+dz*i/count]);
  barriers.push({a:{x:a[0],y:base,z:a[1]},b:{x:b[0],y:base,z:b[1]},height:height+.017,thickness:.045,capsuleHeight:1.6,kind,source:'visible-safety-rail'});
 }
 rail([-9.3,-7.16],[9.3,-7.16],3.675,.98,'platform-track-safety');
 rail([-9.13,-3.08],[-8.07,-3.08],0,1.2,'closed-stair-access');
 rail([6.93,-3.4],[8.48,-3.4],0,1.0,'closed-lift-access');
 const safety=new THREE.Mesh(mergeGeometries(parts),new THREE.MeshStandardMaterial({color:0x3b7180,roughness:.36,metalness:.58}));safety.name='visible-closed-access-and-track-guards';safety.userData.island='home';group.add(safety);parts.forEach(g=>g.dispose());
 // Retained chime posts have visible, physical bodies at their original positions.
 for(const x of[3.9,5.3])barriers.push(...solidBarriers({name:'retained-home-chime-post',kind:'chime-post',base:0,top:2.3,polygon:[[x-.09,3.51],[x+.09,3.51],[x+.09,3.69],[x-.09,3.69],[x-.09,3.51]]}));
 group.updateMatrixWorld(true);
 const stats={...source.userData.loadStats,triangles,materials:materials.size,runtimeMeshes:meshes.length+1,groundTriangles:colliders.reduce((n,m)=>n+m.geometry.attributes.position.count/3,0),ceilingTriangles:data.ceilingPositions.length/9,buildMilliseconds:performance.now()-begin,scale:config.scale,position:config.position,upperAccess:'closed display; not a usable stair or elevator',train:'locked static display; not boardable'};
 return {group,source,meshes,colliders,ceilings,barriers,cameraObstacles,pickMeshes:[...meshes,safety],bounds,config,stats,triangles,included:meshes.map(m=>m.name),constrainHead:stationHeadroom(ceilings,bounds,1.6)};
}
// Use only nearby structural proxies; preserve the user's requested orbit/zoom.
// A low orbit trapped under an eave can escape sideways without changing controls.
export function elevatedCameraConstraint(constrain,bounds){
 let lastOffset=0;
 const wrapped=(target,position)=>{
  const desired=position.clone(),blocked=constrain(target,position);
  if(!blocked||position.distanceTo(target)>3||target.x<bounds.min.x-1||target.x>bounds.max.x+1||target.z<bounds.min.z-1||target.z>bounds.max.z+1)return blocked;
  const radius=Math.max(5,Math.min(7,desired.distanceTo(target))),yaw=Math.atan2(desired.x-target.x,desired.z-target.z);let best=position.clone(),bestDistance=best.distanceTo(target);
  for(const offset of new Set([lastOffset,0,.35,-.35,.7,-.7,1.05,-1.05,1.57,-1.57])){
   const candidate=new THREE.Vector3(target.x+Math.sin(yaw+offset)*radius,target.y+.3,target.z+Math.cos(yaw+offset)*radius);constrain(target,candidate);const distance=candidate.distanceTo(target);
   if(distance>bestDistance+.4){best=candidate;bestDistance=distance;lastOffset=offset;}if(bestDistance>4)break;
  }
  position.copy(best);return blocked;
 };wrapped.stats=constrain.stats;return wrapped;
}
