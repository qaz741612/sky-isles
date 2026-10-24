import {test,expect} from '@playwright/test';

async function enter(page){
 await page.goto('/');await page.waitForFunction(()=>window.__skyisles);await page.locator('#title-screen .tap').click();
 if(await page.locator('#touch-help').isVisible())await page.locator('#help-close').click();
 await page.waitForFunction(()=>window.__skyisles.world.player.move.grounded);
}
test('V3 actual Player: station recess, platform, NPC space, safe edge, original mushroom and mural puzzle',async({page})=>{
 test.setTimeout(240000);await enter(page);
 const result=await page.evaluate(()=>{
  const w=window.__skyisles.world,p=w.player,step=p.update.bind(p);p.update=()=>{};p.orbit.yaw=0;let t=0;
  const tick=(x=0,z=0,jumpHeld=false,jumpPressed=false)=>step(1/60,{x,z,jumpHeld,jumpPressed},t+=1/60);
  const land=(x,z)=>{p.teleport(x,.22,z);for(let i=0;i<80;i++)tick();if(!p.move.grounded)throw Error(`cannot land ${x},${z}`);};
  const walk=(x,z)=>{let n=1000;while(Math.hypot(x-p.pos.x,z-p.pos.z)>.16&&n-->0){const dx=x-p.pos.x,dz=z-p.pos.z,d=Math.hypot(dx,dz);tick(dx/d,dz/d);if(!p.move.grounded)throw Error(`ground gap ${JSON.stringify(p.pos)}`);}if(n<=0)throw Error(`blocked ${x},${z}: ${JSON.stringify(p.pos)}`);for(let i=0;i<40;i++)tick();};
  land(0,3.5);walk(.1,-2.6);walk(.1,-4.3);walk(.1,-2.6); // actual recessed entrance
  walk(2.4,-2.7);walk(2.4,-5.84);walk(2.4,-5.94);
  const platformY=p.pos.y;walk(2.4,-4.4);walk(4.1,-4.2);walk(4.1,-2.9); // future NPC approach
  // Walk directly into the west wing: explicit side collision must stop us.
  land(-2,-2.7);for(let i=0;i<90;i++)tick(0,-1);const buildingStop=p.pos.z;
  // Rail fences isolate the entire swept animated train volume from walking.
  land(2.5,-5.85);for(let i=0;i<90;i++)tick(0,-1);const railStop=p.pos.z;
  let edges=0;
  for(const wall of w.transport.edgeBarriers){const mx=(wall.a.x+wall.b.x)/2,mz=(wall.a.z+wall.b.z)/2,len=Math.hypot(mx,mz);land(mx*(len-.9)/len,mz*(len-.9)/len);
    for(let i=0;i<80;i++){tick(mx/len,mz/len);if(!p.move.grounded)throw Error(`edge ground loss ${JSON.stringify(p.pos)}`);}
    if(p.respawnCount)throw Error(`edge leak ${JSON.stringify(p.pos)}`);edges++;
  }
  const pad=w.islands.jumpPads[0],v=p.pos.clone();pad.group.getWorldPosition(v);p.teleport(v.x,2,v.z);let passive=0;
  for(let i=0;i<160;i++){tick();passive=Math.max(passive,p.move.vy);}
  let bounce=0;for(let i=0;i<50;i++){tick(0,0,true);bounce=Math.max(bounce,p.move.vy);}
  const murals=w.islands.murals.map(m=>({order:m.userData.muralOrderIndex,chime:m.userData.chimeIndex,position:m.position.toArray()}));
  const order=window.__skyisles.getState().muralOrder;for(const index of order)window.__skyisles.playChime(index);
  // Do not change current checkpoint when forced to fall in the void.
  land(4.1,-2.9);const checkpoint=p.lastGrounded.toArray();p.teleport(100,-50,100);tick();
  return{platformY,buildingStop,railStop,edges,passive,bounce,murals,chimes:w.chimes.chimes.length,order,progress:w.puzzle.unlocked,checkpoint,returned:p.pos.toArray(),respawns:p.respawnCount};
 });
 expect(result.platformY).toBeCloseTo(.12,2);expect(result.buildingStop).toBeGreaterThan(-3.15);expect(result.railStop).toBeGreaterThan(-5.95);
 expect(result.edges).toBeGreaterThan(14);expect(result.passive).toBe(0);expect(result.bounce).toBeGreaterThan(12);
 expect(result.chimes).toBe(5);expect(result.murals.map(m=>m.chime)).toEqual(result.order);expect(result.progress).toBe(5);
 expect(result.respawns).toBe(1);expect(Math.hypot(result.returned[0]-result.checkpoint[0],result.returned[2]-result.checkpoint[2])).toBeLessThan(.01);
 console.log(JSON.stringify(result));
});

test('V3 portrait and landscape keep policy, panorama and existing input available',async({page,isMobile})=>{
 test.setTimeout(240000);await enter(page);
 for(const size of isMobile?[{width:430,height:932},{width:932,height:430}]:[{width:1440,height:900}]){
 await page.setViewportSize(size);await page.locator('.home-policy').click();await expect(page.getByRole('dialog')).toBeVisible();await expect(page.locator('#policy-title')).toHaveText('交通大升級');await page.locator('#policy-close').click();
 const before=await page.evaluate(()=>{const p=window.__skyisles.world.player;return{pos:p.pos.toArray(),orbit:{...p.orbit},checkpoint:p.lastGrounded.toArray()};});
 await page.locator('#panorama-btn').click();await page.waitForFunction(()=>window.__skyisles.world.panorama.mode==='overview');
 const corners=await page.evaluate(()=>{const w=window.__skyisles.world,b=w.bridges.bounds;return[[b.minX,b.minZ],[b.maxX,b.maxZ]].map(([x,z])=>w.player.pos.clone().set(x,0,z).project(w.panorama.camera).toArray());});
 for(const c of corners){expect(Math.abs(c[0])).toBeLessThan(1);expect(Math.abs(c[1])).toBeLessThan(1);}
 await page.locator('#panorama-btn').click();await page.waitForFunction(()=>window.__skyisles.world.panorama.mode==='explore');
 const after=await page.evaluate(()=>{const p=window.__skyisles.world.player;return{pos:p.pos.toArray(),orbit:{...p.orbit},checkpoint:p.lastGrounded.toArray()};});expect(after).toEqual(before);
 if(isMobile){await expect(page.locator('#joystick')).toBeVisible();await expect(page.locator('#jump-btn')).toBeVisible();}
 }
});

test('original home chime responds to native keyboard or touchscreen interaction',async({page,isMobile})=>{
 test.setTimeout(180000);await enter(page);
 await page.evaluate(()=>{const w=window.__skyisles.world;w.player.teleport(4.6,.2,2.5);Object.assign(w.player.orbit,{yaw:0,pitch:.5,dist:7});});
 await page.waitForFunction(()=>window.__skyisles.world.player.move.grounded);await page.waitForTimeout(800);
 if(isMobile){
 const xy=await page.evaluate(()=>{const w=window.__skyisles.world;w.camera.position.copy(w.player._camPos);w.camera.lookAt(w.player._camTarget);w.camera.updateMatrixWorld();const p=w.chimes.chimes[0].worldPos.clone().project(w.camera);return{x:(p.x+1)*innerWidth/2,y:(1-p.y)*innerHeight/2};});
 await page.touchscreen.tap(xy.x,xy.y);
 }else await page.keyboard.press('KeyE');
 await expect.poll(()=>page.evaluate(()=>window.__skyisles.world.puzzle.lastResult?.index)).toBe(0);
 await expect.poll(()=>page.evaluate(()=>window.__skyisles.world.puzzle.lastResult?.type)).toBe('wrong'); // Original order starts with sun, not moon.
 expect(await page.evaluate(()=>window.__skyisles.world.chimes.chimes[0].worldPos.toArray())).toEqual([4.6,1.6,3.6]);
});
