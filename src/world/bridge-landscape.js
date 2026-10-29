// MIT. Continuous cantilever landscape, shared materials, static region batches.
import * as THREE from 'three';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import plan from '../data/bridge-landscape.json' with {type:'json'};
const colors={stone:0xc7c4b3,rim:0xe0d7bf,soil:0x6a7954,wood:0xba9269,metal:0x355e63,green:0x769b62,flower:0xf2ddaf,finish:0xc8c6b7,rock:0x909d95,transit:0xa9b8b5,pink:0xe5c0b1};
function shape(rings){const s=new THREE.Shape(rings[0].slice(0,-1).map(([x,z])=>new THREE.Vector2(x,-z)));for(const r of rings.slice(1))s.holes.push(new THREE.Path(r.slice(0,-1).map(([x,z])=>new THREE.Vector2(x,-z))));return s;}
const flat=(rings,y)=>{const g=new THREE.ShapeGeometry(shape(rings));g.rotateX(-Math.PI/2);g.translate(0,y,0);return g;};
const extrude=(rings,base,height)=>{const g=new THREE.ExtrudeGeometry(shape(rings),{depth:height,bevelEnabled:false});g.rotateX(-Math.PI/2);g.translate(0,base,0);return g;};
function sevenGeometry(){const p=new THREE.CurvePath();p.add(new THREE.LineCurve3(new THREE.Vector3(),new THREE.Vector3(0,2.91,0)));p.add(new THREE.CubicBezierCurve3(new THREE.Vector3(0,2.91,0),new THREE.Vector3(0,3.015,0),new THREE.Vector3(.085,3.1,0),new THREE.Vector3(.19,3.1,0)));p.add(new THREE.LineCurve3(new THREE.Vector3(.19,3.1,0),new THREE.Vector3(.75,3.1,0)));return new THREE.TubeGeometry(p,24,.052,6,false);}
export function buildBridgeLandscape(parent){
 const start=performance.now(),group=new THREE.Group();group.name='bridge-landscape';parent.add(group);
 const batches=new Map(),materials=new Map(),barriers=[],colliders=[],meshes=[],instanced=[];let geometries=0;
 const material=key=>{if(!materials.has(key))materials.set(key,new THREE.MeshStandardMaterial({color:colors[key],roughness:key==='metal'?.45:.9,metalness:key==='metal'?.45:0,flatShading:key==='green'}));return materials.get(key);};
 const add=(g,key,zone)=>{const a=g.index?g.toNonIndexed():g;if(a!==g)g.dispose();a.deleteAttribute('uv');a.computeBoundingBox();const c=a.boundingBox.getCenter(new THREE.Vector3()),id=`${zone}:${Math.floor(c.x/64)},${Math.floor(c.z/64)}:${key}`;if(!batches.has(id))batches.set(id,{key,zone,parts:[]});batches.get(id).parts.push(a);};
 const box=(size,pos,key,zone,yaw=0)=>{const g=new THREE.BoxGeometry(...size);g.rotateY(yaw);g.translate(...pos);add(g,key,zone);};
 const beam=(a,b,width,height,key,zone)=>{const from=new THREE.Vector3(...a),to=new THREE.Vector3(...b),d=to.clone().sub(from);if(d.length()<.002)return;const g=new THREE.BoxGeometry(width,height,d.length());g.applyMatrix4(new THREE.Matrix4().compose(from.lerp(to,.5),new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,0,1),d.normalize()),new THREE.Vector3(1,1,1)));add(g,key,zone);};
 const boundary=(ring,height,source,base=0,thickness=.035)=>{for(let i=1;i<ring.length;i++){const a=ring[i-1],b=ring[i];if(Math.hypot(a[0]-b[0],a[1]-b[1])<.001)continue;barriers.push({a:{x:a[0],y:base,z:a[1]},b:{x:b[0],y:base,z:b[1]},height,thickness,capsuleHeight:1.6,kind:'landscape-solid',source});}};
 const support=(g,name)=>{const m=new THREE.Mesh(g,new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));m.visible=false;m.name=name;m.userData.noCheckpoint=true;group.add(m);colliders.push(m);};
 for(const z of plan.zones){if(!plan.activeZones.includes(z.id))continue;
  for(const r of z.shoulders){const g=extrude(r,-.48,.46);if(z.id===2||z.id===5){const a=g.attributes.position;for(let i=0;i<a.count;i++)if(a.getY(i)<-.3)a.setY(i,a.getY(i)-.10-Math.sin(a.getX(i)*.8+a.getZ(i)*.7)*.045);g.computeVertexNormals();}add(g,z.id===2||z.id===5?'rock':'stone',z.id);}
  for(const r of z.finishes)add(flat(r,.008),z.id===3?'transit':'finish',z.id);
  for(const r of z.islandFinishes??[])add(flat(r,.026),z.id===4?'wood':'finish',z.id);
  for(const r of z.beds){
   add(extrude(r,0,.245),z.id===4?'wood':'stone',z.id);add(flat(r,.247),'soil',z.id);support(flat(r,.247),'continuous-planter-top');
   for(const ring of r){boundary(ring,.27,'continuous-curved-planter');for(let i=1;i<ring.length;i++)beam([ring[i-1][0],.245,ring[i-1][1]],[ring[i][0],.245,ring[i][1]],.035,.045,z.id===4?'wood':z.id===3?'metal':'rim',z.id);}
  }
 }
 // Shared foliage ellipsoids overlap along the bed, making continuous low masses,
 // never a procession of separate pots. Instance groups retain 64-unit culling.
 function instances(items,geometry,mat,transform,tag){
  const chunks=new Map();for(const item of items){const p=item.position,key=`${Math.floor(p[0]/64)},${Math.floor(p[2]/64)}`;if(!chunks.has(key))chunks.set(key,[]);chunks.get(key).push(item);}
  const dummy=new THREE.Object3D();for(const list of chunks.values()){const m=new THREE.InstancedMesh(geometry,mat,list.length);m.name=tag;list.forEach((item,i)=>{dummy.position.set(...item.position);dummy.rotation.set(0,item.yaw??0,0);dummy.scale.set(1,1,1);transform(dummy,item,i);dummy.updateMatrix();m.setMatrixAt(i,dummy.matrix);if(tag==='integrated-low-foliage')m.setColorAt(i,new THREE.Color().setHex(i%3===0?0x8aa76b:0x72945b));});m.computeBoundingBox();m.computeBoundingSphere();group.add(m);meshes.push(m);instanced.push(m);}
 }
 for(const z of plan.zones){if(!plan.activeZones.includes(z.id))continue;
  const foliage=new THREE.IcosahedronGeometry(1,1);geometries++;
  instances(z.foliage,foliage,material('green'),(o,_item,i)=>{o.scale.set(.20,.19+(i%3)*.025,1.05);},'integrated-low-foliage');
  const blooms=z.id===2||z.id===3?[]:z.foliage.filter(f=>f.flower),petals=[];for(let i=0;i<5;i++){const g=new THREE.CircleGeometry(.047,5);g.rotateX(-Math.PI/2);g.translate(Math.cos(i/5*Math.PI*2)*.045,0,Math.sin(i/5*Math.PI*2)*.045);petals.push(g);}const flower=mergeGeometries(petals);petals.forEach(g=>g.dispose());geometries++;
  instances(blooms,flower,material(z.id===4||z.id===5?'pink':'flower'),o=>{o.position.y=.59;o.scale.set(1,.7,1);},'low-floral-ribbon');
 }
 for(const guide of plan.guides??[]){const[x,z]=guide.position,[tx,tz]=guide.tangent,nx=-tz,nz=tx;const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute([x+tx*.32,.012,z+tz*.32,x-tx*.25+nx*.23,.012,z-tz*.25+nz*.23,x-tx*.10,.012,z-tz*.10,x+tx*.32,.012,z+tz*.32,x-tx*.10,.012,z-tz*.10,x-tx*.25-nx*.23,.012,z-tz*.25-nz*.23],3));g.computeVertexNormals();add(g,'rim',3);}
 const seven=plan.lamps.filter(l=>l.type==='seven'),low=plan.lamps.filter(l=>l.type!=='seven'),metal=material('metal');
 instances(seven,sevenGeometry(),metal,()=>{},'rounded-seven-post');
 const light=new THREE.MeshStandardMaterial({color:0xffedcf,emissive:0xffdfaa,emissiveIntensity:1.2,roughness:.5,toneMapped:false});
 const bar=new THREE.BoxGeometry(.54,.035,.07);bar.translate(.46,3.035,0);instances(seven,bar,light,()=>{},'warm-downward-linear-luminaire');
 const housing=new THREE.BoxGeometry(.60,.07,.12);housing.translate(.46,3.085,0);instances(seven,housing,metal,()=>{},'linear-lamp-housing');
 const lowPost=new THREE.BoxGeometry(.10,.43,.10);lowPost.translate(0,.215,0);instances(low,lowPost,metal,()=>{},'S09-low-light-post');
 const lowBar=new THREE.BoxGeometry(.52,.035,.1);lowBar.translate(0,.43,0);instances(low,lowBar,light,()=>{},'S09-low-light-line');
 for(const l of plan.lamps){const[x,,z]=l.position,r=.065;boundary([[x-r,z-r],[x+r,z-r],[x+r,z+r],[x-r,z+r],[x-r,z-r]],l.type==='seven'?3.1:.45,'lamp:'+l.id,0,.01);box([.19,.075,.19],[x,.0375,z],'metal',l.zone);}
 // Rounded observation bays have the SAME exterior rail as the shared union.
 // Curved timber benches and cantilever support stay beyond the 4.8 clear band.
 for(const p of plan.platforms){
  const[x,,z]=p.position,[tx,tz]=p.tangent,[nx,nz]=p.normal;
  const world=(along,out,y)=>[x+tx*along+nx*out,y,z+tz*along+nz*out];
  add(extrude(p.domain,-.55,.53),'stone',p.zone);
  for(let slat=0;slat<4;slat++)for(let i=0;i<12;i++){const a=-1.05+i*2.1/12,b=-1.05+(i+1)*2.1/12;beam(world(a,.12*a*a+.12*slat,.48),world(b,.12*b*b+.12*slat,.48),.10,.085,'wood',p.zone);}
  for(const a of[-.85,0,.85])beam(world(a,.12*a*a+.15,.02),world(a,.12*a*a+.15,.44),.095,.095,'metal',p.zone);
  const ring=[[-1.12,-.1],[1.12,-.1],[1.12,.64],[-1.12,.64],[-1.12,-.1]].map(([a,o])=>{const q=world(a,o,0);return[q[0],q[2]];});boundary(ring,.55,'curved-viewing-seat');
  const seat=new THREE.Shape(ring.map(([x,z])=>new THREE.Vector2(x,-z))),sg=new THREE.ShapeGeometry(seat);sg.rotateX(-Math.PI/2);sg.translate(0,.52,0);support(sg,'observation-seat-support');
  // A pair of diagonal corbels connects the bay to the original bridge soffit.
  for(const a of[-1.6,1.6])beam(world(a,-1.65,-.35),world(a,.5,-.42),.18,.28,'metal',p.zone);
 }
 for(const {key,zone,parts}of batches.values()){const g=mergeGeometries(parts),m=new THREE.Mesh(g,material(key));m.name=`zone-${zone}-${key}-batch`;m.receiveShadow=false;g.computeBoundingBox();g.computeBoundingSphere();group.add(m);meshes.push(m);parts.forEach(p=>p.dispose());geometries++;}
 group.updateMatrixWorld(true);let triangles=0;for(const m of meshes)triangles+=(m.geometry.index?.count??m.geometry.attributes.position.count)/3*(m.isInstancedMesh?m.count:1);
 const stats={...plan.stats,visibleMeshes:meshes.length,triangles,collisionMeshes:colliders.length,horizontalBarriers:barriers.length,buildMilliseconds:performance.now()-start,newRealtimeLights:0,geometryBatches:geometries,perFrameRebuilds:0,instanceBatches:instanced.length};
 return{group,plan,stats,colliders,barriers,meshes,update(){}};
}
