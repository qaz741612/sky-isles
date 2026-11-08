// MIT. Static camera shells only. World-space triangle grid for the four R21
// domains; no visible meshes, physics changes, dependencies or global cameras.
import * as THREE from 'three';
import {worldCameraConstraint} from './camera-clearance.js';
export function triangleCameraConstraint(meshes,size=3){
 // Keep native behavior for unsupported dynamic/custom geometry.
 if(meshes.some(m=>!m.isMesh||m.isSkinnedMesh||m.isBatchedMesh||m.geometry.morphAttributes.position?.length||(!m.isInstancedMesh&&m.raycast!==THREE.Mesh.prototype.raycast))){const original=worldCameraConstraint(meshes);original.stats.acceleration='native-mesh-fallback';return original;}
 const vertices=[],bounds=[],sides=[],cells=new Map(),eps=1e-7;
 const a=new THREE.Vector3(),b=new THREE.Vector3(),c=new THREE.Vector3(),instance=new THREE.Matrix4();
 function addMesh(mesh,matrix){
  const g=mesh.geometry,p=g.attributes.position,index=g.index,count=index?.count??p.count,draw=g.drawRange,mirrored=matrix.determinant()<0;
  const ranges=Array.isArray(mesh.material)?g.groups.map(v=>({...v,material:mesh.material[v.materialIndex]})):[{start:0,count,material:mesh.material}];
  for(const range of ranges){
   if(!range.material)continue;
   const start=Math.max(0,range.start,draw.start),end=Math.min(count,range.start+range.count,draw.start+draw.count),side=range.material.side;
   for(let i=start;i+2<end;i+=3){
    a.fromBufferAttribute(p,index?index.getX(i):i).applyMatrix4(matrix);b.fromBufferAttribute(p,index?index.getX(i+1):i+1).applyMatrix4(matrix);c.fromBufferAttribute(p,index?index.getX(i+2):i+2).applyMatrix4(matrix);
    // Negative transforms invert world winding; native Mesh.raycast tests the
    // local winding. BackSide then inverts that test once more.
    const flip=mirrored!==(side===THREE.BackSide),q=flip?c:b,r=flip?b:c,id=sides.length;
    vertices.push(a.x,a.y,a.z,q.x,q.y,q.z,r.x,r.y,r.z);sides.push(side!==THREE.DoubleSide?1:0);
    const x0=Math.min(a.x,b.x,c.x),x1=Math.max(a.x,b.x,c.x),y0=Math.min(a.y,b.y,c.y),y1=Math.max(a.y,b.y,c.y),z0=Math.min(a.z,b.z,c.z),z1=Math.max(a.z,b.z,c.z);bounds.push(x0-eps,y0-eps,z0-eps,x1+eps,y1+eps,z1+eps);
    for(let x=Math.floor((x0-eps)/size);x<=Math.floor((x1+eps)/size);x++)for(let z=Math.floor((z0-eps)/size);z<=Math.floor((z1+eps)/size);z++){const key=`${x},${z}`;if(!cells.has(key))cells.set(key,[]);cells.get(key).push(id);}
   }
  }
 }
 for(const mesh of meshes){
  mesh.updateWorldMatrix(true,false);if(!(mesh.layers.mask&1))continue;
  if(mesh.isInstancedMesh){for(let i=0;i<mesh.count;i++){mesh.getMatrixAt(i,instance);addMesh(mesh,mesh.matrixWorld.clone().multiply(instance));}}
  else addMesh(mesh,mesh.matrixWorld);
 }
 let references=0;for(const[key,ids]of cells){cells.set(key,new Uint32Array(ids));references+=ids.length;}
 const data=new Float64Array(vertices),boxes=new Float64Array(bounds),cull=new Uint8Array(sides),seen=new Uint32Array(sides.length),candidates=[],direction=new THREE.Vector3(),ray=new THREE.Ray(),point=new THREE.Vector3(),box=new THREE.Box3();let stamp=0;
 const stats={acceleration:'static-triangle-grid',queries:0,candidates:0,maxCandidates:0,indexTriangles:sides.length,indexCells:cells.size,indexReferences:references,bufferBytes:data.byteLength+boxes.byteLength+cull.byteLength+seen.byteLength+references*4};
 vertices.length=0;bounds.length=0;sides.length=0;
 const visit=(x,z,y0,y1)=>{const low=Math.min(y0,y1)-eps,high=Math.max(y0,y1)+eps;for(const id of cells.get(`${x},${z}`)??[]){if(seen[id]===stamp||boxes[id*6+4]<low||boxes[id*6+1]>high)continue;seen[id]=stamp;candidates.push(id);}};
 const clamp=(target,position)=>{
  direction.subVectors(position,target);const length=direction.length();if(length<.3)return false;
  stats.queries++;candidates.length=0;if(stamp===0xffffffff){seen.fill(0);stamp=1;}else stamp++;
  const dx=direction.x,dy=direction.y,dz=direction.z,sx=Math.sign(dx),sz=Math.sign(dz);let x=Math.floor(target.x/size),z=Math.floor(target.z/size);const ex=Math.floor(position.x/size),ez=Math.floor(position.z/size);
  let tx=sx?(((sx>0?x+1:x)*size-target.x)/dx):Infinity,tz=sz?(((sz>0?z+1:z)*size-target.z)/dz):Infinity;const dtx=sx?size/Math.abs(dx):Infinity,dtz=sz?size/Math.abs(dz):Infinity,limit=Math.abs(ex-x)+Math.abs(ez-z)+4;
  // Supercover traversal includes both side cells at a corner. Height is
  // conservatively filtered over the ray interval inside each XZ cell, so a
  // low view does not scan thousands of facade/roof faces high above it.
  let entered=0;
  for(let i=0;i<limit;i++){
   const last=x===ex&&z===ez,exit=last?1:Math.min(1,tx,tz);visit(x,z,target.y+dy*entered,target.y+dy*exit);if(last)break;
   const crossing=Math.min(tx,tz);
   if(Math.abs(tx-tz)<1e-12){const y=target.y+dy*crossing;visit(x+sx,z,y,y);visit(x,z+sz,y,y);x+=sx;z+=sz;tx+=dtx;tz+=dtz;}else if(tx<tz){x+=sx;tx+=dtx;}else{z+=sz;tz+=dtz;}
   entered=crossing;
  }
  stats.candidates+=candidates.length;stats.maxCandidates=Math.max(stats.maxCandidates,candidates.length);ray.set(target,direction.normalize());let closest=length,hit=false;
  for(const id of candidates){
   const k=id*6;box.min.fromArray(boxes,k);box.max.fromArray(boxes,k+3);if(!ray.intersectsBox(box))continue;
   const j=id*9;a.fromArray(data,j);b.fromArray(data,j+3);c.fromArray(data,j+6);if(!ray.intersectTriangle(a,b,c,Boolean(cull[id]),point))continue;
   const distance=target.distanceTo(point);if(distance<=closest){closest=distance;hit=true;}
  }
  if(hit)position.copy(target).addScaledVector(direction,Math.max(.15,closest-.22));return hit;
 };clamp.stats=stats;return clamp;
}
