import * as THREE from 'three';
// Static wall/roof shells only. Index once after world transforms are ready;
// query cells along the short target-to-camera ray, never the entire world.
export function worldCameraConstraint(meshes){
 const cells=new Map(),size=8,ray=new THREE.Raycaster(),direction=new THREE.Vector3();
 for(const mesh of meshes){mesh.updateWorldMatrix(true,false);const box=new THREE.Box3().setFromObject(mesh);for(let x=Math.floor(box.min.x/size);x<=Math.floor(box.max.x/size);x++)for(let z=Math.floor(box.min.z/size);z<=Math.floor(box.max.z/size);z++){const key=`${x},${z}`;if(!cells.has(key))cells.set(key,[]);cells.get(key).push(mesh);}}
 const stats={queries:0,candidates:0,maxCandidates:0};
 const clamp=(target,position)=>{
  direction.subVectors(position,target);const length=direction.length();if(length<.3)return false;
  const near=new Set();for(let x=Math.floor(Math.min(target.x,position.x)/size);x<=Math.floor(Math.max(target.x,position.x)/size);x++)for(let z=Math.floor(Math.min(target.z,position.z)/size);z<=Math.floor(Math.max(target.z,position.z)/size);z++)for(const mesh of cells.get(`${x},${z}`)||[])near.add(mesh);
  stats.queries++;stats.candidates+=near.size;stats.maxCandidates=Math.max(stats.maxCandidates,near.size);
  ray.set(target,direction.normalize());ray.far=length;const hit=ray.intersectObjects([...near],false)[0];if(!hit)return false;
  position.copy(target).addScaledVector(direction,Math.max(.15,hit.distance-.22));return true;
 };clamp.stats=stats;return clamp;
}
// Retained compatibility for callers that explicitly need a home-only constraint.
export function homeCameraConstraint(meshes,radius=9){const clamp=worldCameraConstraint(meshes);return(target,position)=>Math.hypot(target.x,target.z)<=radius?clamp(target,position):false;}
