import{test}from'node:test';import assert from'node:assert/strict';import*as T from'three';
import{r21DiscoveryCamera}from'../src/sim/r21-camera.js';
import plan from'../src/data/bdeh-plan.json'with{type:'json'};
import views from'../src/data/bdeh-camera.json'with{type:'json'};
const places=Object.fromEntries(Object.entries(plan.islands).map(([c,config])=>[c,{config}]));
function make(code){
 const orbit={yaw:.12,pitch:.67,dist:22,fov:58},player={move:{vx:0,vz:0,grounded:true}},rig=r21DiscoveryCamera(()=>false,places,()=>orbit,()=>player),c=places[code].config.centre,camera=new T.Vector3(c[0]+2,15,c[2]+17);
 const tick=()=>{rig.setDelta(1/60);rig(new T.Vector3(c[0],1.645,c[2]),camera);};
 return{orbit,player,rig,camera,tick};
}
test('arrival framing changes only local idle yaw, never ordinary zoom, FOV or manual pitch',()=>{
 for(const code of'BDEH'){
  const{orbit,rig,tick,camera}=make(code);for(let i=0;i<300;i++)tick();
  assert.equal(orbit.pitch,.67);assert.equal(orbit.dist,22);assert.equal(orbit.fov,58);assert.ok(camera.toArray().every(Number.isFinite));assert.equal(rig.state().island,code);assert.equal(rig.state().manual,false);assert.ok(rig.discovery.maximumIdleYawStep<=views.maximumIdleYawRate/60+1e-10);
  if(code==='H')assert.ok(Math.abs(orbit.yaw-Math.PI)<.01,'H must face the real learning centre, not the empty forum ground');
 }
});
test('holding the one-hand movement input or being airborne never starts an automatic arrival turn',()=>{
 for(const code of'BDEH'){
  const{orbit,player,tick}=make(code);player.move.vx=5;for(let i=0;i<180;i++)tick();assert.equal(orbit.yaw,.12);player.move.vx=0;player.move.grounded=false;for(let i=0;i<180;i++)tick();assert.equal(orbit.yaw,.12);
 }
});
test('held movement against a solid wall never counts as idle arrival when guards zero velocity',()=>{
 for(const code of'BDEH'){
  const{orbit,rig,tick}=make(code);rig.setInput({x:1,z:0});
  for(let i=0;i<300;i++)tick();assert.equal(orbit.yaw,.12);
  rig.setInput({x:0,z:0});for(let i=0;i<300;i++)tick();assert.notEqual(orbit.yaw,.12);
 }
});
test('one manual orbit or zoom overrides idle discovery for the rest of this island visit',()=>{
 for(const code of'BDEH'){
  const{orbit,rig,tick}=make(code);for(let i=0;i<120;i++)tick();orbit.yaw+=.4;orbit.pitch+=.12;orbit.dist-=2;const saved={...orbit};tick();assert.equal(rig.state().manual,true);for(let i=0;i<300;i++)tick();assert.deepEqual(orbit,saved);
 }
});
test('F/A/C/G keep their original camera constraint and profile outside the four local domains',()=>{
 const orbit={yaw:.12,pitch:.67,dist:22,fov:58};let calls=0;
 const base=(target,position)=>{calls++;position.set(target.x+1,7,target.z+4);return false;};const rig=r21DiscoveryCamera(base,places,()=>orbit,()=>({move:{grounded:true,vx:0,vz:0}}));
 for(const[x,z]of[[0,0],[-22.55,-19.656],[-20.358,38.61],[44.928,45.279]]){
  const target=new T.Vector3(x,1.6,z),saved=target.clone(),position=new T.Vector3();rig(target,position);assert.deepEqual(target,saved);assert.deepEqual(position.toArray(),[x+1,7,z+4]);assert.deepEqual(orbit,{yaw:.12,pitch:.67,dist:22,fov:58});
 }
 assert.equal(calls,4);assert.equal(rig.discovery.localFrames,0);
});
test('local arrival converges to the same view at20,60 and120 simulation Hz',()=>{
 const results=[];
 for(const hz of[20,60,120]){
  const{orbit,rig,camera}=make('H'),c=places.H.config.centre;rig.setDelta(1/hz);
  for(let i=0;i<hz*6;i++)rig(new T.Vector3(c[0],1.645,c[2]),camera);
  results.push({yaw:orbit.yaw,camera:camera.clone()});
 }
 for(const r of results){assert.ok(Math.abs(r.yaw-Math.PI)<.001);assert.ok(r.camera.distanceTo(results[1].camera)<.1);}
});
