import {test,expect} from '@playwright/test';
import fs from 'node:fs';
const output=process.env.SKYISLES_QA_OUTPUT_DIR||'docs/previews/transport-elevated-station-v9-game-integration';
test('V9 live game: spawn, four mouths, new solids, closed access, original gameplay and information',async({page,isMobile})=>{
 test.setTimeout(600000);const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('/');await page.waitForFunction(()=>window.__skyisles&&document.querySelector('#loading').classList.contains('hidden'),null,{timeout:180000});
 await page.evaluate(()=>window.__skyisles.start());
 // The actual renderer produced the loading frame. Accelerate controller checks
 // using the same Player, all collision meshes and navigation; no mock geometry.
 await page.evaluate(()=>{const w=window.__skyisles.world;w.savedRender=w.renderer.render.bind(w.renderer);w.renderer.render=()=>{};});
 const results=await page.evaluate(()=>{
  const w=window.__skyisles.world,p=w.player,step=p.update.bind(p);p.update=()=>{};let time=0;const savedOrbit={...p.orbit},records={gates:[],solids:[],camera:[]};
  const tick=(x=0,z=0,jumpPressed=false,jumpHeld=false)=>step(1/60,{x,z,jumpPressed,jumpHeld},time+=1/60);
  const land=(x,z,y=.1)=>{p.teleport(x,y,z);for(let i=0;i<60;i++)tick();if(!p.move.grounded)throw Error('no support '+JSON.stringify(p.pos));};
  const drive=(x,z)=>{let i=0;while(Math.hypot(x-p.pos.x,z-p.pos.z)>.18&&i++<1500){const dx=x-p.pos.x,dz=z-p.pos.z,d=Math.hypot(dx,dz),yaw=p.orbit.yaw;tick((dx*Math.cos(yaw)-dz*Math.sin(yaw))/d,(dx*Math.sin(yaw)+dz*Math.cos(yaw))/d);if(!p.move.grounded||p.respawnCount)throw Error('fall '+JSON.stringify(p.pos));}if(i>=1500)throw Error('blocked '+JSON.stringify({target:[x,z],pos:p.pos.toArray()}));for(let j=0;j<25;j++)tick();};
  records.spawn={position:p.pos.toArray(),grounded:p.move.grounded,respawns:p.respawnCount};
  for(const path of w.bridges.plans.filter(p=>['S09','S10','S15','S18'].includes(p.id))){const points=path.from==='F'?path.points:[...path.points].reverse();land(0,0);for(const pt of points)drive(pt.x,pt.z);for(const pt of [...points].reverse())drive(pt.x,pt.z);records.gates.push({id:path.id,bidirectional:true,noJump:true});}
  land(0,3.5);drive(0,0);drive(0,-2.3);drive(-5,-1.8);drive(0,-1.8);drive(5.5,-1.4);drive(0,0);
  // Drive into the closed glass entrance; solid walls must stop the real Player.
  land(0,-2.2);p.orbit.yaw=0;for(let i=0;i<100;i++)tick(0,-1);records.solids.push({kind:'closed-glass-entrance',pos:p.pos.toArray()});
  land(-8.6,-2);for(let i=0;i<100;i++)tick(0,-1);records.solids.push({kind:'closed-stairs',pos:p.pos.toArray()});
  land(7.7,-2.1);for(let i=0;i<100;i++)tick(0,-1);records.solids.push({kind:'closed-lift',pos:p.pos.toArray()});
  land(0,-6.63);for(let i=0;i<100;i++)tick(1,0);records.solids.push({kind:'viaduct-pier',pos:p.pos.toArray()});
  land(0,3.5);let openJump=0,glide=false;for(let i=0;i<180;i++){tick(0,0,i===0||i===2,true);openJump=Math.max(openJump,p.pos.y);glide ||= p.move.gliding;}
  records.jump={openJump,glide};
  // Beneath the real front eave: use actual downward-facing shell triangles.
  land(0,-2.6);const floor=p.pos.y;let maxHead=floor+1.6;
  const up=p.pos.clone().set(0,1,0),ray=new p.ray.constructor(p.pos.clone().add({x:0,y:1.6,z:0}),up,0,8),ceiling=ray.intersectObjects(w.transport.station.ceilings,false).find(h=>h.face.normal.y<-.2)?.point.y;
  for(let i=0;i<150;i++){tick(0,0,i===0||i===2,i<40);maxHead=Math.max(maxHead,p.pos.y+1.6);}records.headroom={floor,ceiling,maxHead};
  const pad=w.islands.jumpPads[0],v=p.pos.clone();pad.group.getWorldPosition(v);land(v.x,v.z,2);let passive=0;for(let i=0;i<100;i++){tick();passive=Math.max(passive,p.move.vy);}let bounce=0;for(let i=0;i<45;i++){tick(0,0,false,true);bounce=Math.max(bounce,p.move.vy);}records.mushroom={passive,bounce};
  for(const[x,z]of[[0,3.5],[0,-2.3],[-5,-1.8],[5.5,-1.4],[-8.6,-2]]){land(x,z);for(const yaw of[0,Math.PI/2,Math.PI,Math.PI*1.5])for(const pitch of[.25,.6,.9]){Object.assign(p.orbit,{yaw,pitch,dist:savedOrbit.dist});for(let i=0;i<50;i++)tick();w.camera.updateMatrixWorld();const ndc=p.pos.clone().add({x:0,y:.8,z:0}).project(w.camera);records.camera.push({x,z,yaw,pitch,ndc:ndc.toArray(),distance:w.camera.position.distanceTo(p._camTarget)});}}
  records.chimes=w.chimes.chimes.map(c=>c.worldPos.toArray());records.murals=w.islands.murals.map(m=>m.userData.chimeIndex);for(const i of window.__skyisles.getState().muralOrder)window.__skyisles.playChime(i);records.puzzle=w.puzzle.unlocked;
  land(0,3.5);const checkpoint=p.lastGrounded.toArray();p.teleport(100,-50,100);tick();records.fall={checkpoint,returned:p.pos.toArray(),respawns:p.respawnCount};
  land(0,3.5);Object.assign(p.orbit,savedOrbit);for(let i=0;i<70;i++)tick();p.update=step;
  records.stats=w.transport.stats;records.firstWorldRender=w.renderer.info.render.calls;return records;
 });
 fs.writeFileSync(`${output}/${isMobile?'mobile':'desktop'}-controller.json`,JSON.stringify(results,null,2)+'\n');
 expect(results.spawn.grounded).toBe(true);expect(results.spawn.position[1]).toBeCloseTo(0,5);expect(results.gates).toHaveLength(4);
 expect(results.solids[0].pos[2]).toBeGreaterThan(-2.65);expect(results.solids[1].pos[2]).toBeGreaterThan(-2.8);expect(results.solids[2].pos[2]).toBeGreaterThan(-3.2);expect(results.solids[3].pos[0]).toBeLessThan(2.0);
 expect(results.jump.openJump).toBeGreaterThan(1);expect(results.jump.glide).toBe(true);expect(results.headroom.ceiling).toBeGreaterThan(2);expect(results.headroom.maxHead).toBeLessThanOrEqual(results.headroom.ceiling+.01);
 expect(results.mushroom.passive).toBe(0);expect(results.mushroom.bounce).toBeGreaterThan(12);expect(results.chimes).toHaveLength(5);expect(results.chimes[0]).toEqual([4.6,1.6,3.6]);expect(results.murals).toEqual([2,4,0,3,1]);expect(results.puzzle).toBe(5);expect(results.fall.respawns).toBe(1);
 expect(Math.hypot(results.fall.returned[0]-results.fall.checkpoint[0],results.fall.returned[2]-results.fall.checkpoint[2])).toBeLessThan(.02);
 for(const r of results.camera){expect(Math.abs(r.ndc[0]),JSON.stringify(r)).toBeLessThan(1);expect(Math.abs(r.ndc[1]),JSON.stringify(r)).toBeLessThan(1);expect(r.distance,JSON.stringify(r)).toBeGreaterThan(.4);}
 for(const name of['交通大升級','安心生養']){await page.locator('#policy-menu summary').click();await page.locator('#policy-list').getByRole('button',{name,exact:true}).click();await expect(page.locator('#policy-title')).toHaveText(name);await page.locator('#policy-close').click();}
 // Native click/touch ray against the actual relocated mural and V9 stele.
 for(const kind of['mural','vision']){
  const xy=await page.evaluate(kind=>{const w=window.__skyisles.world,p=w.player,step=p.update.bind(p);p.update=()=>{};const x=kind==='mural'?-5:5.5,z=-1.2;p.teleport(x,.1,z);p.orbit.yaw=0;p.orbit.pitch=.5;p.orbit.dist=7;for(let i=0;i<100;i++)step(1/60,{x:0,z:0,jumpPressed:false,jumpHeld:false},i/60);w.camera.updateMatrixWorld();const target=w.transport.interactives.find(m=>m.userData.transportInfo===kind).position.clone().project(w.camera);p.update=step;return{x:(target.x+1)*innerWidth/2,y:(1-target.y)*innerHeight/2};},kind);
  if(isMobile)await page.touchscreen.tap(xy.x,xy.y);else await page.mouse.click(xy.x,xy.y);
  await expect(page.locator('#policy-title')).toHaveText(kind==='mural'?'風鈴文化牆':'交通政策願景');await expect(page.locator('#policy-content li')).toHaveCount(kind==='mural'?5:4);await page.locator('#policy-content li').last().scrollIntoViewIfNeeded();await page.locator('#policy-close').click();
 }
 await page.evaluate(()=>{const w=window.__skyisles.world;w.player.teleport(0,.1,3.5);Object.assign(w.player.orbit,{yaw:.16,pitch:.6,dist:16});});await page.waitForFunction(()=>window.__skyisles.world.player.move.grounded);
 const before=await page.evaluate(()=>{const p=window.__skyisles.world.player;return{pos:p.pos.toArray(),orbit:{...p.orbit},checkpoint:p.lastGrounded.toArray()};});
 await page.locator('#panorama-btn').click();await page.waitForFunction(()=>window.__skyisles.world.panorama.mode==='overview');await page.locator('#panorama-btn').click();await page.waitForFunction(()=>window.__skyisles.world.panorama.mode==='explore');
 const after=await page.evaluate(()=>{const p=window.__skyisles.world.player;return{pos:p.pos.toArray(),orbit:{...p.orbit},checkpoint:p.lastGrounded.toArray()};});expect(after.orbit).toEqual(before.orbit);for(const key of['pos','checkpoint'])for(let i=0;i<3;i++)expect(after[key][i]).toBeCloseTo(before[key][i],8);expect(errors).toEqual([]);
});
