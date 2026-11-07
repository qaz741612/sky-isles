// MIT. Four local discovery views; no world, avatar, FOV or zoom scaling.
// Idle arrival turns the real orbit (and hence movement basis), never an
// invisible camera-only 180-degree offset. A deliberate orbit/zoom cancels it
// for this visit. Movement and airborne states never initiate a yaw turn.
import * as THREE from 'three';
import views from '../data/bdeh-camera.json' with {type:'json'};
import {floodCameraConstraint} from '../world/flood-control.js';
import {worldCameraConstraint} from './camera-clearance.js';
const angle=a=>Math.atan2(Math.sin(a),Math.cos(a));
export function r21DiscoveryCamera(constrain,places,getOrbit,getPlayer){
 let dt=1/60,active=null,idle=0,manual=false,expected=null,previous=null,previousHead=null,detouring=false,movingIntent=false;
 const metrics={arrivals:0,idleTurns:0,manualOverrides:0,localFrames:0,maximumIdleYawStep:0};
 const entries=Object.entries(places).map(([code,p])=>({code,p,centre:p.config.centre,radius:Math.max(...p.config.maxDimensions)/2+2.0}));
 const foliage=worldCameraConstraint(Object.values(places).flatMap(p=>p.cameraVegetation??[]));
 const localConstrain=(target,position)=>{const wall=constrain(target,position),leaf=foliage(target,position);return wall||leaf;};
 let effectiveOrbit;
 const safe=new Map(entries.map(e=>[e.code,floodCameraConstraint(localConstrain,{pos:new THREE.Vector3(...e.centre)},()=>effectiveOrbit)]));
 const reset=()=>{active=null;idle=0;manual=false;expected=null;previous=null;previousHead=null;detouring=false;};
 const apply=(target,position)=>{
  const entry=entries.find(e=>Math.hypot(target.x-e.centre[0],target.z-e.centre[2])<e.radius);
  if(!entry){reset();return constrain(target,position);}
  const o=getOrbit(),player=getPlayer?.(),preset=views[entry.code];
  const newVisit=active!==entry.code;
  if(newVisit){active=entry.code;idle=0;manual=false;expected={...o};previous=position.clone();previousHead=target.clone();detouring=false;metrics.arrivals++;}
  if(expected&&(Math.abs(angle(o.yaw-expected.yaw))>.001||Math.abs(o.pitch-expected.pitch)>.001||Math.abs(o.dist-expected.dist)>.01)){
   if(!manual)metrics.manualOverrides++;
   manual=true;
  }
  // Swept guards zero actual velocity at a wall. Held movement intent must
  // still suppress arrival turning, or the joystick basis rotates under a
  // player who is deliberately pushing against the wall.
  const moving=player?(Math.hypot(player.move.vx,player.move.vz)>.08||movingIntent):true;
  const grounded=player?.move.grounded??false;
  idle=(!moving&&grounded)?idle+dt:0;
  if(!manual&&idle>views.idleDelay&&player){
   const anchor=preset.arrivalFocus??[preset.focus[0],preset.focus[2]];
   const dx=target.x-entry.centre[0]-anchor[0],dz=target.z-entry.centre[2]-anchor[1];
   const desired=Math.hypot(dx,dz)>3?Math.atan2(dx,dz):preset.fallbackYaw;
   const step=THREE.MathUtils.clamp(angle(desired-o.yaw),-views.maximumIdleYawRate*dt,views.maximumIdleYawRate*dt);
   o.yaw+=step;metrics.idleTurns++;metrics.maximumIdleYawStep=Math.max(metrics.maximumIdleYawStep,Math.abs(step));
  }
  expected={...o};
  const distance=Math.hypot(target.x-entry.centre[0],target.z-entry.centre[2]);
  const blend=THREE.MathUtils.smoothstep(entry.radius-distance,0,3);
  const portrait=o.fov===58,basePitch=portrait?.67:.60;
  // Preserve manual pitch deltas and zoom, lower the ordinary arrival view so
  // the near roof edge frames facades instead of filling the portrait canvas.
  const pitch=THREE.MathUtils.clamp(o.pitch+blend*(preset.pitch-basePitch),.12,1.2);
  const focus=new THREE.Vector3(entry.centre[0]+preset.focus[0],preset.focus[1],entry.centre[2]+preset.focus[2]);
  const head=target.clone(),look=target.clone().lerp(focus,.16*blend);
  const body=head.clone().add(new THREE.Vector3(0,-.75,0)),feet=head.clone().add(new THREE.Vector3(0,-1.30,0));
  const probes=point=>{const r=new THREE.Vector3(point.z-head.z,0,head.x-point.x).normalize().multiplyScalar(.32);return[head,body,body.clone().add(r),body.clone().sub(r),feet.clone().addScaledVector(r,.78),feet.clone().addScaledVector(r,-.78)];};
  const visible=point=>probes(point).every(focus=>!localConstrain(focus,point.clone()));
  // Keep focus near the player: this is an ordinary third-person view, not a
  // distant QA lens. No field-of-view, model scale or orbit-distance change.
  const delta=look.clone().sub(target);if(delta.length()>1.8)delta.setLength(1.8);look.copy(target).add(delta);
  const desired=head.clone().add(new THREE.Vector3(Math.sin(o.yaw)*Math.cos(pitch)*o.dist,Math.sin(pitch)*o.dist,Math.cos(o.yaw)*Math.cos(pitch)*o.dist));
  effectiveOrbit={...o,pitch};
  if(manual){
   // User orbit takes priority over the automatic distant composition. Seek
   // a clear lower/closer lens at the requested azimuth before choosing a side.
   let best=null,score=-Infinity;
   for(const elevation of new Set([pitch,Math.min(pitch,.25),Math.min(pitch,.12),.02,Math.max(pitch,.75),Math.max(pitch,1.15)])){
    if(o.dist-5*Math.abs(elevation-pitch)<=score)continue;
    const candidate=head.clone().add(new THREE.Vector3(Math.sin(o.yaw)*Math.cos(elevation)*o.dist,Math.sin(elevation)*o.dist,Math.cos(o.yaw)*Math.cos(elevation)*o.dist));
    for(let pass=0;pass<3&&!visible(candidate);pass++)for(const focus of probes(candidate))localConstrain(focus,candidate);
    const distance=candidate.distanceTo(head),value=distance-5*Math.abs(elevation-pitch);
    if(distance>=2.6&&visible(candidate)&&value>score){best=candidate;score=value;if(distance>=o.dist-.01&&Math.abs(elevation-pitch)<.001)break;}
   }
   if(best)desired.copy(best);else safe.get(entry.code)(head,desired);
  }else safe.get(entry.code)(head,desired);
  // The older body-visibility clamp can settle at nine units under an eave.
  // Prefer a nearby unobstructed ordinary orbit over a sudden apparent zoom.
  if(!manual&&desired.distanceTo(head)<o.dist*.78){
   for(const shift of[.12,-.12,.24,-.24,.36,-.36,.48,-.48,.64,-.64]){
    const candidate=head.clone().add(new THREE.Vector3(Math.sin(o.yaw+shift)*Math.cos(pitch)*o.dist,Math.sin(pitch)*o.dist,Math.cos(o.yaw+shift)*Math.cos(pitch)*o.dist));
    for(const focus of probes(candidate))localConstrain(focus,candidate);
    if(candidate.distanceTo(head)<o.dist*.80)continue;
    if(!visible(candidate))continue;
    desired.copy(candidate);break;
   }
  }
  if(previous&&!newVisit&&previous.distanceTo(desired)<35){
   const old=previous.clone().add(head.clone().sub(previousHead??head));
   if(!visible(old)&&visible(previous))old.copy(previous);
   // Follow the orbit arc rather than a chord through a roof. Crucially,
   // only primitive visibility clamps run after interpolation: the stateful
   // endpoint selector would overwrite the smoothed pose every pointer packet.
   const from=old.clone().sub(head),to=desired.clone().sub(head),a=1-Math.exp(-8*dt);
   const azimuth=Math.atan2(from.x,from.z)+THREE.MathUtils.clamp(angle(Math.atan2(to.x,to.z)-Math.atan2(from.x,from.z))*a,-1.5*dt,1.5*dt);
   const fromElevation=Math.atan2(from.y,Math.hypot(from.x,from.z)),toElevation=Math.atan2(to.y,Math.hypot(to.x,to.z));
   if(Math.abs(angle(Math.atan2(to.x,to.z)-Math.atan2(from.x,from.z)))<.025&&Math.abs(toElevation-fromElevation)<.025)detouring=false;
   const elevation=fromElevation+THREE.MathUtils.clamp((toElevation-fromElevation)*a,-1.5*dt,1.5*dt),radius=THREE.MathUtils.lerp(from.length(),detouring?Math.min(from.length(),to.length()):to.length(),a);
   position.copy(head).add(new THREE.Vector3(Math.sin(azimuth)*Math.cos(elevation)*radius,Math.sin(elevation)*radius,Math.cos(azimuth)*Math.cos(elevation)*radius));
   const travel=position.clone().sub(old);const limit=Math.min(27*dt,1.5*dt*from.length());if(travel.length()>limit)position.copy(old).addScaledVector(travel,limit/travel.length());
   if(!visible(position)){
    // Backtrack along a short safe segment instead of instantly pulling the
    // camera14m under the eave. For a stationary avatar the previous pose is
    // still valid, so normal orbit never jumps or crosses a solid boundary.
    detouring=true;const attempted=position.clone();let accepted=false;
    // Contract gradually along the already visible cone, turn inside the
    // obstruction, then expand. Holding the far pose would freeze user orbit.
    const retreat=old.clone().lerp(body,Math.min(21*dt/old.distanceTo(body),Math.max(0,1-2.6/old.distanceTo(body))));
    if(old.distanceTo(body)>2.7&&visible(retreat)){position.copy(retreat);accepted=true;}
    if(!accepted)for(const fraction of[.5,.25,.125,.0625]){const candidate=old.clone().lerp(attempted,fraction);if(visible(candidate)){position.copy(candidate);accepted=true;break;}}
    if(!accepted){
     if(visible(old))position.copy(old);
     else{
      // A moving avatar can invalidate the old view behind a pillar. Safety
      // still takes priority over smoothing in this genuinely occluded case.
      for(let pass=0;pass<3&&!visible(position);pass++)for(const focus of probes(position))localConstrain(focus,position);
      if(!visible(position))position.copy(desired);
     }
    }
   }
  }else position.copy(desired);
  look.copy(head).lerp(look,Math.min(1,(position.distanceTo(head)/10)**2));
  target.copy(look);previous=position.clone();previousHead=head.clone();metrics.localFrames++;
  return true;
 };
 apply.stats=constrain.stats;apply.discovery=metrics;
 apply.setDelta=value=>{dt=THREE.MathUtils.clamp(value,1/240,.05);};
 apply.setInput=input=>{movingIntent=Math.hypot(input.x,input.z)>.08;};
 apply.resetVisit=reset;
 apply.state=()=>({island:active,idle,manual,movingIntent,orbit:expected?{...expected}:null});
 return apply;
}
