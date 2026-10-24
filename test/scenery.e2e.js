import { test,expect } from '@playwright/test';
import fs from 'node:fs';
const folder='docs/previews/eight-policy-islands-scenery-v1';
test('each policy theme renders, leaves routes open and supports policy entry',async({page,isMobile})=>{
 test.setTimeout(360000);const errors=[];page.on('pageerror',e=>errors.push(String(e)));fs.mkdirSync(folder,{recursive:true});
 await page.goto('/');await page.waitForFunction(()=>window.__skyisles);
 await page.locator('#title-screen .tap').click();if(await page.locator('#touch-help').isVisible())await page.locator('#help-close').click();
 await page.waitForFunction(()=>window.__skyisles.world.player.move.grounded);
 await page.waitForTimeout(1000);await page.screenshot({path:`${folder}/${isMobile?'mobile':'desktop'}-explore.png`});
 const state=await page.evaluate(()=>{const w=window.__skyisles.world;return{groups:w.props.groups.map(g=>({name:g.name,themes:g.userData.theme})),plots:w.props.plots,scale:w.islands.group.scale.toArray(),islands:w.islands.islands.map(i=>i.name)};});
 expect(state.groups).toHaveLength(7);expect(state.scale).toEqual([1,1,1]);for(const p of state.plots)expect(p.clearance-p.radius).toBeGreaterThanOrEqual(.4199);
 if(!isMobile)for(const name of state.islands){
  await page.evaluate(name=>{const w=window.__skyisles.world,i=w.islands.islands.find(i=>i.name===name);w.player.teleport(i.pos.x,i.pos.y+.3,i.pos.z);Object.assign(w.player.orbit,{yaw:.25,pitch:.92,dist:i.r*2.6});},name);
  await page.waitForFunction(()=>window.__skyisles.world.player.move.grounded);await page.evaluate(()=>{const w=window.__skyisles.world;w.camera.position.copy(w.player._camPos);w.camera.lookAt(w.player._camTarget);});await page.waitForTimeout(250);
  await page.screenshot({path:`${folder}/island-${name}.png`});
 }
 if(isMobile){await page.evaluate(()=>{const w=window.__skyisles.world,i=w.islands.islands.find(i=>i.name==='lookout');w.player.teleport(i.pos.x,i.pos.y+.3,i.pos.z);Object.assign(w.player.orbit,{yaw:.25,pitch:.92,dist:13});});await page.waitForFunction(()=>window.__skyisles.world.player.move.grounded);await page.evaluate(()=>{const w=window.__skyisles.world;w.camera.position.copy(w.player._camPos);w.camera.lookAt(w.player._camTarget);});await page.waitForTimeout(250);}
 const target=await page.evaluate(()=>{const w=window.__skyisles.world,i=w.islands.islands.find(i=>i.name==='lookout'),p=w.props.plots.find(p=>p.island==='lookout');const v=i.pos.clone().set(i.pos.x+p.x,i.pos.y+p.radius*1.6,i.pos.z+p.z).project(w.camera);return{x:(v.x+1)*innerWidth/2,y:(1-v.y)*innerHeight/2};});
 if(isMobile)await page.touchscreen.tap(target.x,target.y);else await page.mouse.click(target.x,target.y);
 await expect(page.getByRole('dialog')).toBeVisible();await expect(page.locator('#policy-title')).toHaveText('教育發展');
 if(isMobile)await page.touchscreen.tap(5,5);else await page.mouse.click(5,5);
 await expect(page.getByRole('dialog')).not.toBeVisible();
 await page.locator('#panorama-btn').click();await page.waitForFunction(()=>window.__skyisles.world.panorama.mode==='overview');
 await page.screenshot({path:`${folder}/${isMobile?'mobile-panorama':'panorama-pure'}.png`});
 if(!isMobile){await page.evaluate(()=>window.__skyisles.world.panorama.labelled=true);await expect(page.locator('.island-label:visible')).toHaveCount(8);await page.screenshot({path:`${folder}/panorama-labelled.png`});}
 await page.locator('#panorama-btn').click();await page.waitForFunction(()=>window.__skyisles.world.panorama.mode==='explore');
 await page.locator('#policy-menu summary').click();await page.locator('#policy-list button').first().click();await expect(page.locator('#policy-title')).toHaveText('交通大升級');await expect(page.getByRole('dialog')).toBeVisible();expect(errors).toEqual([]);
});
