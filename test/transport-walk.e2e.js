import {test,expect} from './helpers/software-qa.js';

async function enter(page){
 await page.goto('/');await page.waitForFunction(()=>window.__skyisles&&document.querySelector('#loading').classList.contains('hidden'),null,{timeout:150000});await page.evaluate(()=>{window.__skyisles.world.renderer.render=()=>{};});await page.locator('#title-screen .tap').click();
 if(await page.locator('#touch-help').isVisible())await page.locator('#help-close').click();
 await page.waitForFunction(()=>window.__skyisles.world.player.move.grounded);
}
test('transport portrait and landscape keep policy, panorama and existing input available',async({page,isMobile})=>{
 test.setTimeout(240000);await enter(page);
 for(const size of isMobile?[{width:430,height:932},{width:932,height:430}]:[{width:1440,height:900}]){
 await page.setViewportSize(size);await page.locator('.home-policy').click();await expect(page.getByRole('dialog')).toBeVisible();await expect(page.locator('#policy-title')).toHaveText('交通大升級');await page.locator('#policy-close').click();
 const before=await page.evaluate(()=>{const p=window.__skyisles.world.player;return{pos:p.pos.toArray(),orbit:{...p.orbit},checkpoint:p.lastGrounded.toArray()};});
 await page.locator('#panorama-btn').click();await page.waitForFunction(()=>window.__skyisles.world.panorama.mode==='overview');
 const corners=await page.evaluate(()=>{const w=window.__skyisles.world,b=w.bridges.bounds;return[[b.minX,b.minZ],[b.maxX,b.maxZ]].map(([x,z])=>w.player.pos.clone().set(x,0,z).project(w.panorama.camera).toArray());});
 for(const c of corners){expect(Math.abs(c[0])).toBeLessThan(1);expect(Math.abs(c[1])).toBeLessThan(1);}
 await page.locator('#panorama-btn').click();await page.waitForFunction(()=>window.__skyisles.world.panorama.mode==='explore');
 const after=await page.evaluate(()=>{const p=window.__skyisles.world.player;return{pos:p.pos.toArray(),orbit:{...p.orbit},checkpoint:p.lastGrounded.toArray()};});expect(after.orbit).toEqual(before.orbit);for(const key of['pos','checkpoint'])for(let i=0;i<3;i++)expect(after[key][i]).toBeCloseTo(before[key][i],8);
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
