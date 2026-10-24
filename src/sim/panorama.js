import * as THREE from 'three';

// The same scene is rendered through a fitted orthographic lens. No world scaling.
export class Panorama {
 constructor(camera,bounds,onMode){this.explore=camera;this.camera=camera;this.bounds=bounds;this.onMode=onMode;this.mode='explore';this.elapsed=0;this.duration=1.2;this.ortho=new THREE.OrthographicCamera(-1,1,1,-1,.1,900);this.transition=new THREE.Camera();this.transition.near=.1;this.transition.far=900;this.fit(innerWidth,innerHeight);}
 get active(){return this.mode!=='explore';}
 fit(width,height){
  // Resize/orientation updates the return lens without changing the saved pose.
  if(this.saved)this.saved.projection.copy(this.explore.projectionMatrix);
  const b=this.bounds,aspect=width/height,w=(b.maxX-b.minX)*1.18,h=(b.maxZ-b.minZ)*1.18,span=Math.max(h,w/aspect);
  Object.assign(this.ortho,{left:-span*aspect/2,right:span*aspect/2,top:span/2,bottom:-span/2});this.ortho.updateProjectionMatrix();
  this.ortho.position.set((b.minX+b.maxX)/2,240,(b.minZ+b.maxZ)/2);this.ortho.up.set(0,0,-1);this.ortho.lookAt(this.ortho.position.x,0,this.ortho.position.z);this.ortho.updateMatrixWorld();
 }
 enter(){if(this.active)return;this.saved={position:this.explore.position.clone(),quaternion:this.explore.quaternion.clone(),projection:this.explore.projectionMatrix.clone()};this.mode='entering';this.elapsed=0;this.camera=this.transition;this.onMode(true);this.update(0);}
 leave(){if(this.mode!=='overview')return;this.mode='leaving';this.elapsed=0;this.camera=this.transition;}
 update(dt){
  if(this.mode==='explore'||this.mode==='overview')return;
  this.elapsed=Math.min(this.duration,this.elapsed+dt);let t=this.elapsed/this.duration;t=t*t*(3-2*t);if(this.mode==='leaving')t=1-t;
  this.transition.position.lerpVectors(this.saved.position,this.ortho.position,t);this.transition.quaternion.slerpQuaternions(this.saved.quaternion,this.ortho.quaternion,t);
  // Blend homogeneous lens matrices as well as pose: continuous perspective-to-ortho.
  const a=this.saved.projection.elements,b=this.ortho.projectionMatrix.elements,c=this.transition.projectionMatrix.elements;
  for(let i=0;i<16;i++)c[i]=a[i]*(1-t)+b[i]*t;
  this.transition.projectionMatrixInverse.copy(this.transition.projectionMatrix).invert();this.transition.updateMatrixWorld();
  if(this.elapsed===this.duration){if(this.mode==='entering'){this.mode='overview';this.camera=this.ortho;}else{this.explore.position.copy(this.saved.position);this.explore.quaternion.copy(this.saved.quaternion);this.camera=this.explore;this.mode='explore';this.onMode(false);}}
 }
}
