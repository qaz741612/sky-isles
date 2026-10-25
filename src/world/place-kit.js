// Original native low-poly architecture kit (MIT). Hand composed per island.
// Static batches stay per island; physics and camera shells are explicit subsets.
import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { toonMaterial } from './toon.js';
export const PALETTE={cream:0xf0e5cc,stone:0xbab7a5,edge:0xd6cfba,teal:0x45686b,glass:0x8ebfc4,dark:0x344e51,wood:0xad8058,woodLight:0xd6b480,coral:0xc77e62,leaf:0x638f70,leafLight:0x95af77,leafDark:0x3e725c,lawn:0x83a87a,water:0x59a7ad,waterLight:0x91d1ce,shade:0x657b65};
const materials=new Map();
let contactMaterial;
function softContact(){
 if(contactMaterial)return contactMaterial;
 const data=new Uint8Array(64*64*4);for(let y=0;y<64;y++)for(let x=0;x<64;x++){const i=(y*64+x)*4,r=Math.hypot((x-31.5)/31.5,(y-31.5)/31.5);data[i]=42;data[i+1]=58;data[i+2]=49;data[i+3]=Math.round(Math.max(0,1-r)**1.4*60);}
 const texture=new THREE.DataTexture(data,64,64);texture.needsUpdate=true;texture.magFilter=THREE.LinearFilter;texture.minFilter=THREE.LinearFilter;
 contactMaterial=new THREE.MeshBasicMaterial({map:texture,transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-1});return contactMaterial;
}
export function placeMaterial(color){if(!materials.has(color))materials.set(color,toonMaterial(color));return materials.get(color);}
export function placeKit(island,parent){
 const shadows=[],batches=new Map(),barriers=[],colliders=[],cameraObstacles=[],solids=[];
 const pos=island.pos||new THREE.Vector3();
 const guard=(a,b,height,kind,base=0)=>barriers.push({a:{x:a[0]+pos.x,y:base+pos.y,z:a[1]+pos.z},b:{x:b[0]+pos.x,y:base+pos.y,z:b[1]+pos.z},height,kind,island:island.name});
 const add=(color,g)=>{if(g.index){const old=g;g=g.toNonIndexed();old.dispose();}g.deleteAttribute('uv');if(!batches.has(color))batches.set(color,[]);batches.get(color).push(g);};
 const box=(color,size,p,rz=0,ry=0)=>{const g=new THREE.BoxGeometry(...size);g.rotateZ(rz);g.rotateY(ry);g.translate(...p);add(color,g);};
 const beam=(color,a,b,w=.07,h=w)=>{const v=new THREE.Vector3(...a),end=new THREE.Vector3(...b),d=end.clone().sub(v);if(d.length()<1e-6)return;const g=new THREE.BoxGeometry(w,h,d.length());g.applyMatrix4(new THREE.Matrix4().compose(v.lerp(end,.5),new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,0,1),d.normalize()),new THREE.Vector3(1,1,1)));add(color,g);};
 function shadow(x,z,w,d){const g=new THREE.PlaneGeometry(w,d);g.rotateX(-Math.PI/2);g.translate(x,.045,z);shadows.push(g);}
 function boundary(bounds,height,kind='wall',base=0){const[x,z,xx,zz]=bounds;for(const[a,b,c,d]of[[x,z,xx,z],[xx,z,xx,zz],[xx,zz,x,zz],[x,zz,x,z]])barriers.push({a:{x:a+pos.x,y:base+pos.y,z:b+pos.z},b:{x:c+pos.x,y:base+pos.y,z:d+pos.z},height,kind,island:island.name});}
 function solid(color,size,p,kind='wall'){
  box(color,size,p);const bounds=[p[0]-size[0]/2,p[2]-size[2]/2,p[0]+size[0]/2,p[2]+size[2]/2];boundary(bounds,size[1],kind,p[1]-size[1]/2);solids.push({bounds,height:size[1],kind});
  const mesh=new THREE.Mesh(new THREE.BoxGeometry(...size),placeMaterial(color));mesh.position.set(...p);mesh.visible=false;mesh.userData.island=island.name;parent.add(mesh);cameraObstacles.push(mesh);mesh.userData.support='solid';colliders.push(mesh);return mesh;
 }
 function walkable(size,p,color=PALETTE.wood){const mesh=new THREE.Mesh(new THREE.BoxGeometry(...size),placeMaterial(color));mesh.position.set(...p);mesh.userData.island=island.name;mesh.userData.support='walkable-platform';parent.add(mesh);colliders.push(mesh);return mesh;}
 function roof(profile,z,depth,color=PALETTE.teal){for(let i=1;i<profile.length;i++){const[x,y]=profile[i-1],[xx,yy]=profile[i],g=new THREE.BoxGeometry(Math.hypot(xx-x,yy-y)+.08,.16,depth);g.rotateZ(Math.atan2(yy-y,xx-x));g.translate((x+xx)/2,(y+yy)/2,z);const cam=new THREE.Mesh(g.clone(),placeMaterial(color));cam.visible=false;cam.userData.island=island.name;cam.userData.support='roof';parent.add(cam);cameraObstacles.push(cam);colliders.push(cam);add(color,g);for(const zz of[z-depth/2+.07,z+depth/2-.07])beam(PALETTE.wood,[x,y-.15,zz],[xx,yy-.15,zz],.09,.1);}}
 function paving(points,color=PALETTE.edge){const shape=new THREE.Shape();points.forEach(([x,z],i)=>i?shape.lineTo(x,-z):shape.moveTo(x,-z));shape.closePath();const g=new THREE.ShapeGeometry(shape);g.rotateX(-Math.PI/2);g.translate(0,.025,0);add(color,g);for(let i=0;i<points.length;i++){const a=points[i],b=points[(i+1)%points.length];beam(PALETTE.stone,[a[0],.035,a[1]],[b[0],.035,b[1]],.095,.065);}}
 function pad(x,z,w,d,color=PALETTE.edge){paving([[x-w/2,z-d/2],[x+w/2,z-d/2],[x+w/2,z+d/2],[x-w/2,z+d/2]],color);}
 function column(x,z,h=2.4){solid(PALETTE.wood,[.12,h,.12],[x,h/2,z],'column');box(PALETTE.stone,[.21,.12,.21],[x,.06,z]);}
 function glazing(x,z,w,h,y=1.3,side=false,normal=1){box(PALETTE.dark,side?[.06,h+.16,w+.16]:[w+.16,h+.16,.06],[x,y,z]);box(PALETTE.glass,side?[.075,h,w]:[w,h,.075],[x,y,z+(side?0:.03*normal)]);for(let i=0;i<=Math.ceil(w/.7);i++){const t=-w/2+i*w/Math.ceil(w/.7);box(PALETTE.wood,side?[.09,h+.12,.055]:[.055,h+.12,.09],[x+(side?0:t),y,z+(side?t:.055*normal)]);} }
 function bench(x,z,yaw=0,w=1.5){const part=(c,s,p)=>{const xx=p[0]*Math.cos(yaw)+p[2]*Math.sin(yaw),zz=-p[0]*Math.sin(yaw)+p[2]*Math.cos(yaw);box(c,s,[x+xx,p[1],z+zz],0,yaw);};part(PALETTE.wood,[w,.13,.46],[0,.48,0]);part(PALETTE.wood,[w,.35,.08],[0,.74,-.21]);for(const xx of[-w*.35,w*.35])part(PALETTE.teal,[.08,.42,.42],[xx,.21,0]);const rw=Math.abs(Math.cos(yaw))*w/2+Math.abs(Math.sin(yaw))*.24,rd=Math.abs(Math.sin(yaw))*w/2+Math.abs(Math.cos(yaw))*.24;boundary([x-rw,z-rd,x+rw,z+rd],.92,'bench');}
 function tree(x,z,r=1.4,form=0){
  solid(PALETTE.wood,[.22,2.3,.22],[x,1.15,z],'tree-trunk');
  for(const[dx,dy,dz,rr,color]of[[0,0,0,r,PALETTE.leaf],[-r*.5,-.25,.1,r*.62,PALETTE.leafDark],[r*.45,.16,.25,r*.68,PALETTE.leafLight]]){const g=form?new THREE.CylinderGeometry(rr*.7,rr,.75,7):new THREE.IcosahedronGeometry(rr,0);g.rotateY(dx*1.37+dz*.8);g.rotateZ(.17*(dx<0?-1:1));g.scale(1,form?1:.62,1);g.translate(x+dx,2.7+dy,z+dz);add(color,g);}
  shadow(x+.2,z+.2,r*2.6,r*2.2);
 }
 function planter(x,z,w,d){solid(PALETTE.stone,[w,.24,d],[x,.12,z],'planter');box(PALETTE.leafDark,[w-.12,.25,d-.12],[x,.32,z]);box(PALETTE.leafLight,[w*.7,.14,d*.7],[x,.48,z]);}
 function table(x,z,w=1.2,d=.7){solid(PALETTE.wood,[w,.12,d],[x,.86,z],'table');for(const xx of[-w*.35,w*.35])box(PALETTE.teal,[.08,.82,d*.65],[x+xx,.41,z]);}
 function finish(){if(shadows.length){const mesh=new THREE.Mesh(mergeGeometries(shadows),softContact());mesh.name='shared-procedural-contact-shade';mesh.raycast=()=>{};parent.add(mesh);shadows.forEach(g=>g.dispose());}for(const[color,parts]of batches){const mesh=new THREE.Mesh(mergeGeometries(parts),placeMaterial(color));mesh.userData.island=island.name;parent.add(mesh);parts.forEach(p=>p.dispose());}return{barriers,colliders,cameraObstacles,solids};}
 return{add,box,beam,walkable,shadow,boundary,guard,solid,roof,paving,pad,column,glazing,bench,tree,planter,table,finish};
}
