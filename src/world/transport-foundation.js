// MIT. The authored V9 footprint is shared by the road union and this floor.
// It remains a valid collider independently of asynchronous GLB loading.
import * as THREE from 'three';
import plan from '../data/yuan-plan.json' with {type:'json'};
export function buildTransportFoundation(){
 const ring=plan.islandFootprintsXZ.F;
 const shape=new THREE.Shape(ring.map(([x,z])=>new THREE.Vector2(x,-z)));
 const geometry=new THREE.ShapeGeometry(shape);geometry.rotateX(-Math.PI/2);
 const floor=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color:0xd8d1bf,roughness:.9,side:THREE.DoubleSide}));
 floor.name='transport-foundation';floor.userData.island='home';floor.receiveShadow=true;
 return floor;
}
