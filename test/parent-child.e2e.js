import {test,expect} from './helpers/software-qa.js';
test('approved family island: four gates, destinations, headroom, orbit visibility, policies and panorama',async({page})=>{
 test.setTimeout(600000);const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('/');await page.waitForFunction(()=>window.__skyisles&&document.querySelector('#loading').classList.contains('hidden'),{},{timeout:150000});await page.evaluate(()=>{window.__skyisles.world.renderer.render=()=>{};});await page.locator('#title-screen .tap').click({force:true,timeout:120000});if(await page.locator('#touch-help').isVisible())await page.locator('#help-close').click();
 const result=await page.evaluate(()=>{
  const w=window.__skyisles.world,p=w.player,f=w.family,isle=w.islands.islands.find(i=>i.name==='tree'),step=p.update.bind(p);p.update=()=>{};let time=0;const results=[],camera=[];const originalOrbit={...p.orbit};
  const tick=(x=0,z=0,jump=false)=>step(1/60,{x,z,jumpPressed:jump,jumpHeld:jump},time+=1/60);
  const drive=([x,z])=>{const tx=x+isle.pos.x,tz=z+isle.pos.z;let frames=0;while(Math.hypot(tx-p.pos.x,tz-p.pos.z)>.16&&frames++<1500){const dx=tx-p.pos.x,dz=tz-p.pos.z,d=Math.hypot(dx,dz),yaw=p.orbit.yaw;tick((dx*Math.cos(yaw)-dz*Math.sin(yaw))/d,(dx*Math.sin(yaw)+dz*Math.cos(yaw))/d);}for(let i=0;i<35;i++)tick();if(Math.hypot(tx-p.pos.x,tz-p.pos.z)>.45||!p.move.grounded||p.respawnCount)throw Error('Family path failed '+JSON.stringify({x,z,pos:p.pos.toArray(),frames,grounded:p.move.grounded}));};
  for(const[id,route]of Object.entries(f.config.access)){p.teleport(isle.pos.x+route[0][0],.15,isle.pos.z+route[0][1]);for(let i=0;i<40;i++)tick();for(const pt of route.slice(1))drive(pt);for(const pt of route.toReversed().slice(1))drive(pt);results.push({gate:id,bidirectional:true});}
  p.teleport(isle.pos.x+1.1,.2,isle.pos.z+1.7);for(let i=0;i<40;i++)tick();for(const pt of[[1.1,3],[1.1,5.9],[-2.5,6],[-2.5,2.2],[-2,2.8]])drive(pt);
  const head=[];for(const[x,z]of[[1.1,.4],[7.5,-3]]){p.teleport(isle.pos.x+x,.2,isle.pos.z+z);for(let i=0;i<80;i++)tick();const floor=p.pos.y,ray=new p.ray.constructor(p.pos.clone().add({x:0,y:1.6,z:0}),p.pos.clone().set(0,1,0),0,4),ceiling=ray.intersectObjects(f.ceilings,false).find(h=>h.face.normal.y<-.2)?.point.y;let max=floor;for(let i=0;i<140;i++){tick(0,0,i===0||i===2);max=Math.max(max,p.pos.y);}head.push({x,z,floor,ceiling,maxHead:max+1.6});}
  for(const[x,z]of[[1.1,.4],[7.5,-3],[7.5,-2.825],[-2.5,6],[1.1,3]]){p.teleport(isle.pos.x+x,.2,isle.pos.z+z);for(let i=0;i<60;i++)tick();for(const yaw of[0,Math.PI/2,Math.PI,3*Math.PI/2])for(const pitch of[.25,.6,.9]){p.orbit.yaw=yaw;p.orbit.pitch=pitch;p.orbit.dist=16;for(let i=0;i<45;i++)tick();w.camera.updateMatrixWorld();const centre=p.pos.clone().add({x:0,y:.8,z:0}).project(w.camera);camera.push({x,z,yaw,pitch,centre:centre.toArray(),distance:w.camera.position.distanceTo(p.pos.clone().add({x:0,y:1.5,z:0}))});}}
  Object.assign(p.orbit,originalOrbit);p.teleport(isle.pos.x+1.1,.2,isle.pos.z+4.5);for(let i=0;i<100;i++)tick();
  const checkpoint=p.lastGrounded.toArray();p.teleport(100,-50,100);tick();const returned=p.pos.toArray();
  // Stand safely on the family forecourt for normal UI checks after the deliberate fall.
  p.teleport(isle.pos.x+1.1,.2,isle.pos.z+4.5);for(let i=0;i<80;i++)tick();p.update=step;
  return{gates:results,head,camera,checkpoint,returned,respawns:p.respawnCount,npc:f.config.npc,stats:f.stats,groups:w.props.groups.length};
 });
 // Geometry/controller/camera assertions above use the live model. UI state
 // checks below need no repeated GPU raster; actual screenshots/FPS are separate.
 await page.evaluate(()=>{window.__skyisles.world.renderer.render=()=>{};});
 expect(result.gates).toHaveLength(4);expect(result.groups).toBe(7);expect(result.npc.implemented).toBe(false);expect(result.respawns).toBe(1);expect(Math.hypot(result.returned[0]-result.checkpoint[0],result.returned[2]-result.checkpoint[2])).toBeLessThan(.05);
 for(const r of result.head){expect(r.ceiling).toBeGreaterThan(2);expect(r.maxHead).toBeLessThanOrEqual(r.ceiling+.012);}
 for(const r of result.camera){expect(Math.abs(r.centre[0]),JSON.stringify(r)).toBeLessThan(1);expect(Math.abs(r.centre[1]),JSON.stringify(r)).toBeLessThan(1);expect(r.distance,JSON.stringify(r)).toBeGreaterThan(.4);}
 await page.locator('.island-label[data-island="tree"]').click();await expect(page.getByRole('dialog')).toBeVisible();await expect(page.locator('#policy-title')).toHaveText('安心生養');await page.locator('#policy-close').click();
 const before=await page.evaluate(()=>({pos:window.__skyisles.world.player.pos.toArray(),checkpoint:window.__skyisles.world.player.lastGrounded.toArray(),orbit:{...window.__skyisles.world.player.orbit}}));await page.locator('#panorama-btn').click();await page.waitForFunction(()=>window.__skyisles.world.panorama.mode==='overview');await page.locator('#panorama-btn').click();await page.waitForFunction(()=>window.__skyisles.world.panorama.mode==='explore');const after=await page.evaluate(()=>({pos:window.__skyisles.world.player.pos.toArray(),checkpoint:window.__skyisles.world.player.lastGrounded.toArray(),orbit:{...window.__skyisles.world.player.orbit}}));expect(after.orbit).toEqual(before.orbit);for(const key of['pos','checkpoint'])for(let i=0;i<3;i++)expect(after[key][i]).toBeCloseTo(before[key][i],8);expect(errors).toEqual([]);
 console.log(JSON.stringify({gateCount:result.gates.length,cameraCases:result.camera.length,minimumCameraDistance:Math.min(...result.camera.map(r=>r.distance)),head:result.head,sourceTriangles:result.stats.sourceTriangles,selectedTriangles:result.stats.selectedTriangles,runtimeMeshes:result.stats.runtimeMeshes,npc:'reservation only; no NPC body/dialogue to test',errors}));
 // Assertions are complete; release the software GPU before Playwright fixture teardown.
 await page.evaluate(()=>{window.__skyisles.world.renderer.dispose();window.__skyisles.world.renderer.forceContextLoss();});
});
