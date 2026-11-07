// Shared actual-Player arrival audit. Renderless diagnostics and GPU tests use the same route, input and assertions.
export function auditR21Arrival(){
  const api=window.__skyisles,w=api.world,p=w.player;api.start();w.renderer.render=()=>{};const step=p.update.bind(p);p.update=()=>{};const profile={...p.orbit},rows=[];let time=0,recording=false,trace=[],last=null,maxAngle=0,maxStep=0,maxAngleFrame=null,maxStepFrame=null;
  const ray=new p.ray.constructor(),obstacles=p.cameraConstraint.opaqueObstacles??Object.values(w.r21).flatMap(v=>v.cameraObstacles);
  const tick=(x=0,z=0)=>{
   const yaw=p.orbit.yaw;p.cameraConstraint.setDelta(1/60);step(1/60,{x,z,jumpPressed:false,jumpHeld:false},time+=1/60);
   if(![...p.pos.toArray(),...w.camera.position.toArray()].every(Number.isFinite))throw Error('nonfinite camera/player');
   if(Math.hypot(x,z)>.1&&Math.abs(p.orbit.yaw-yaw)>.00001)throw Error('idle discovery turned the moving player');
   if(recording){const now={player:p.pos.toArray(),camera:w.camera.position.toArray(),quaternion:w.camera.quaternion.toArray(),yaw:p.orbit.yaw,moving:Math.hypot(x,z)>.1,local:p.cameraConstraint.state().island};if(last){const angle=w.camera.quaternion.angleTo(p.camera.quaternion.clone().fromArray(last.quaternion)),distance=p.camera.position.distanceTo(p.pos.clone().fromArray(last.camera));if(angle>maxAngle){maxAngle=angle;maxAngleFrame={index:trace.length,now,previous:last,state:p.cameraConstraint.state()};}if(distance>maxStep){maxStep=distance;maxStepFrame={index:trace.length,now,previous:last,state:p.cameraConstraint.state()};}}if(trace.length%8===0){const head=p.pos.clone().add(p.pos.clone().set(0,1.5,0));ray.set(head,w.camera.position.clone().sub(head).normalize());ray.far=head.distanceTo(w.camera.position)-.03;if(ray.intersectObjects(obstacles,false).length)throw Error('actual moving camera hides player');}trace.push(now);last=now;}
  };
  const idle=n=>{for(let i=0;i<n;i++)tick();};
  const walk=target=>{let n=0;while(Math.hypot(target.x-p.pos.x,target.z-p.pos.z)>.18&&n++<1500){const dx=target.x-p.pos.x,dz=target.z-p.pos.z,d=Math.hypot(dx,dz),a=p.orbit.yaw;tick((dx*Math.cos(a)-dz*Math.sin(a))/d,(dx*Math.sin(a)+dz*Math.cos(a))/d);if(!p.move.grounded||p.respawnCount)throw Error('final route lost dry ground');}if(n>=1500)throw Error('final route blocked '+JSON.stringify({target,player:p.pos.toArray()}));};
  // Real guard-clamped movement, not a mocked zero-velocity state. The intent
  // remains held for5s at the actual D facade; the camera must not turn it.
  const dc=w.r21.D.config.centre;Object.assign(p.orbit,profile,{yaw:0});p.cameraConstraint.resetVisit();p.teleport(dc[0]-2.0,.2,dc[2]-6);for(let k=0;k<300;k++)tick(-1,0);
  if(Math.hypot(p.move.vx,p.move.vz)>.08||Math.hypot(p.pos.x-(dc[0]-2.0),p.pos.z-(dc[2]-6))>1)throw Error('wall-intent probe did not meet the actual D wall '+JSON.stringify({position:p.pos.toArray(),velocity:[p.move.vx,p.move.vz]}));
  if(!p.cameraConstraint.state().movingIntent)throw Error('actual held input did not reach the camera');
  const blockedInput={player:p.pos.toArray(),velocity:[p.move.vx,p.move.vz],movingIntent:p.cameraConstraint.state().movingIntent,yaw:p.orbit.yaw,seconds:5};
  const landmarks={B:[[-7.8,2.8,-3.9]],D:[[-2.65,2.8,-6.5]],E:[[2.25,3.4,5]],H:[[0,4.3,4.1]]};
  for(const[code,place]of Object.entries(w.r21)){
   const c=place.config.centre,local=([x,z])=>({x:c[0]+x,z:c[2]+z});Object.assign(p.orbit,profile);p.cameraConstraint.resetVisit();p.teleport(c[0],.2,c[2]);idle(300);w.camera.updateMatrixWorld();
   const points=[...landmarks[code]];if(code==='E'){const garden=place.config.finalQA.rainGarden;points.push([garden.centre[0],garden.waterTop,garden.centre[1]]);}
   const projection=points.map(([x,y,z])=>p.pos.clone().set(c[0]+x,y,c[2]+z).project(w.camera).toArray());if(projection.some(v=>Math.abs(v[0])>1||Math.abs(v[1])>1||v[2]<-1||v[2]>1))throw Error('native landmark off screen '+code+' '+JSON.stringify(projection));
   // Check actual visible opaque model triangles as well as the simplified
   // structural shells: a tree crown must not hide the small visual avatar.
   const opaque=place.meshes.filter(mesh=>(Array.isArray(mesh.material)?mesh.material:[mesh.material]).every(m=>!m.transparent&&m.opacity>.95));
   for(const height of[.7,1.1]){const focus=p.pos.clone().add(p.pos.clone().set(0,height,0));ray.set(focus,w.camera.position.clone().sub(focus).normalize());ray.far=focus.distanceTo(w.camera.position)-.03;const hits=ray.intersectObjects(opaque,false);if(hits.length)throw Error('actual opaque model hides native avatar '+code+' '+JSON.stringify({mesh:hits[0].object.name,point:hits[0].point.toArray(),height}));}
   const path=w.bridges.walkPlans.find(r=>r.id===place.config.finalQA.entryRoad);let pointsOnRoad=path.points.slice();if(Math.hypot(pointsOnRoad[0].x-c[0],pointsOnRoad[0].z-c[2])<Math.hypot(pointsOnRoad.at(-1).x-c[0],pointsOnRoad.at(-1).z-c[2]))pointsOnRoad.reverse();
   let start=pointsOnRoad.length-1;while(start>0&&Math.hypot(pointsOnRoad[start].x-c[0],pointsOnRoad[start].z-c[2])<Math.max(...place.config.maxDimensions)/2+2.1)start--;
   Object.assign(p.orbit,profile);p.cameraConstraint.resetVisit();p.teleport(pointsOnRoad[start].x,.15,pointsOnRoad[start].z);idle(90);trace=[];last=null;maxAngle=0;maxStep=0;recording=true;let gatePaused=false;
   for(const t of pointsOnRoad.slice(start)){walk(t);if(!gatePaused&&Math.hypot(p.pos.x-c[0],p.pos.z-c[2])<Math.min(...place.config.maxDimensions)/2-.5){idle(300);gatePaused=true;}}
   const guides={B:[[7.2,-6.6],[7.2,-7.15]],D:[[6.2,1.6],[8.8,1],[9.1,-3.55],[11.3,-3.55],[11.9,-4.9],[11.9,-6.35]],E:[[4.7,2.8],[-1,2.4],[-6,4],[-10.55,6.5]],H:[[0,-8.1],[0,-8.55]]};for(const pt of guides[code])walk(local(pt));idle(300);recording=false;
   if(maxAngle>.15||maxStep>3)throw Error('abrupt gate-to-guide camera '+code+' '+JSON.stringify({maxAngle,maxStep,maxAngleFrame,maxStepFrame}));
   if(p.lastGrounded.distanceTo(p.pos)>.05)throw Error('guide dry checkpoint not updated');const safe=p.lastGrounded.clone(),before={pos:p.pos.toArray(),safe:safe.toArray(),orbit:{...p.orbit},camera:w.camera.position.toArray(),quaternion:w.camera.quaternion.toArray(),progress:w.puzzle.unlocked};w.panorama.enter();w.panorama.update(2);w.panorama.leave();w.panorama.update(2);const after={pos:p.pos.toArray(),safe:p.lastGrounded.toArray(),orbit:{...p.orbit},camera:w.camera.position.toArray(),quaternion:w.camera.quaternion.toArray(),progress:w.puzzle.unlocked};if(JSON.stringify(before)!==JSON.stringify(after))throw Error('panorama state changed');
   const saved=p.orbit.yaw;p.orbit.yaw+=.6;idle(60);const manualYaw=p.orbit.yaw;if(!p.cameraConstraint.state().manual||Math.abs(manualYaw-saved-.6)>.000001)throw Error('manual camera handoff failed');idle(100);if(p.orbit.yaw!==manualYaw)throw Error('arrival rig fought manual orbit');
   p.teleport(250,-50,250);idle(100);if(p.respawnCount!==1||!p.move.grounded||p.pos.distanceTo(safe)>.05)throw Error('expanded dry checkpoint recovery failed');p.respawnCount=0;
   rows.push({code,profile,landmarkNDC:projection,entryRoad:path.id,oneStartTeleportOnly:true,gatePauseSeconds:5,NPCStop:place.config.npc[0].playerStop,frames:trace,maximumCameraRotationRadiansPer60HzFrame:maxAngle,maximumCameraTranslationPer60HzFrame:maxStep,manualOverride:true,panoramaRestored:true,fallRecovered:true});
  }
  return{method:'Actual loaded GLBs, real Player and production local camera at fixed60Hz; accelerated engineering input along a continuous gate-to-NPC path. Route starts are teleported; not a human operation or real-device FPS measurement.',blockedInput,rows};

}
