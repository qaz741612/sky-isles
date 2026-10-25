import * as THREE from 'three';

// Optional local camera constraint. Keep configured orbit/zoom unchanged; the
// existing follow lerp restores distance when the obstruction clears.
export function homeCameraConstraint(meshes, radius=9) {
 const ray=new THREE.Raycaster(),direction=new THREE.Vector3();
 return (target,position)=>{
  if(Math.hypot(target.x,target.z)>radius)return false;
  direction.subVectors(position,target);const length=direction.length();
  if(length<.3)return false;
  ray.set(target,direction.normalize());ray.far=length;
  const hit=ray.intersectObjects(meshes,false)[0];
  if(!hit)return false;
  position.copy(target).addScaledVector(direction,Math.max(.15,hit.distance-.22));
  return true;
 };
}
