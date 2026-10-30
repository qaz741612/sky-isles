import { test,expect } from './helpers/software-qa.js';
import fs from 'node:fs';
const folder='work/world-regression-panorama';

test('real 3D panorama fits, locks movement, preserves progress and returns the exploration camera',async({page,isMobile})=>{
 test.setTimeout(300000);
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('/');await page.waitForFunction(()=>window.__skyisles);
 await page.locator('#title-screen .tap').click();
 if(await page.locator('#touch-help').isVisible())await page.locator('#help-close').click();
 await expect.poll(()=>page.evaluate(()=>window.__skyisles.world.player.move.grounded),{timeout:60000}).toBe(true);
 await page.waitForTimeout(800);
 fs.mkdirSync(folder,{recursive:true});
 await page.evaluate(()=>{const w=window.__skyisles.world;w.renderer.qaDraw?.(w.scene,w.panorama.camera);});await page.screenshot({path:`${folder}/${isMobile?'mobile':'desktop'}-explore.png`});
 await page.evaluate(()=>{const w=window.__skyisles.world;window.__skyisles.playChime(window.__skyisles.getState().muralOrder[0]);const island=w.islands.islands.find(i=>i.name==='windmill');w.player.teleport(island.pos.x,island.pos.y+.4,island.pos.z);});
 await expect.poll(()=>page.evaluate(()=>window.__skyisles.world.player.move.grounded),{timeout:60000}).toBe(true);
 await page.waitForTimeout(1200);
 const before=await page.evaluate(()=>{const w=window.__skyisles.world;return{pos:w.player.pos.toArray(),checkpoint:w.player.lastGrounded.toArray(),orbit:{...w.player.orbit},cam:w.camera.position.toArray(),quaternion:w.camera.quaternion.toArray(),progress:w.puzzle.unlocked};});
 expect(before.progress).toBe(1);expect(Math.hypot(before.checkpoint[0],before.checkpoint[2])).toBeGreaterThan(50);
 await page.locator('#panorama-btn').click();
 await expect.poll(()=>page.evaluate(()=>window.__skyisles.getState().panoramaMode),{timeout:30000}).toBe('overview');
 await expect(page.locator('#panorama-btn')).toHaveText('返回探索');
 await expect(page.locator('.island-label:visible')).toHaveCount(0);
 await expect(page.locator('#policy-nav')).toBeHidden();
 const result=await page.evaluate(()=>{
 const w=window.__skyisles.world,b=w.bridges.bounds,c=w.panorama.camera,corners=[];
 for(const x of [b.minX,b.maxX])for(const z of [b.minZ,b.maxZ]){const v=w.player.pos.clone().set(x,0,z).project(c);corners.push(v.toArray());}
 return{corners,orthographic:c.isOrthographicCamera,pos:w.player.pos.toArray(),checkpoint:w.player.lastGrounded.toArray(),progress:w.puzzle.unlocked};
 });
 expect(result.orthographic).toBe(true);for(const p of result.corners){expect(Math.abs(p[0])).toBeLessThan(.86);expect(Math.abs(p[1])).toBeLessThan(.86);}
 for(const key of['pos','checkpoint'])for(let i=0;i<3;i++)expect(result[key][i]).toBeCloseTo(before[key][i],10);
 await page.keyboard.down('KeyW');await page.waitForTimeout(500);await page.keyboard.up('KeyW');
 const locked=await page.evaluate(()=>window.__skyisles.world.player.pos.toArray());for(let i=0;i<3;i++)expect(locked[i]).toBeCloseTo(before.pos[i],10);
 await page.evaluate(()=>{const w=window.__skyisles.world;w.renderer.qaDraw?.(w.scene,w.panorama.camera);});await page.screenshot({path:`${folder}/${isMobile?'mobile-portrait-panorama':'panorama-pure'}.png`});
 if(!isMobile){await page.evaluate(()=>window.__skyisles.world.panorama.labelled=true);await expect(page.locator('.island-label:visible')).toHaveCount(8);await page.evaluate(()=>{const w=window.__skyisles.world;w.renderer.qaDraw?.(w.scene,w.panorama.camera);});await page.screenshot({path:`${folder}/panorama-labelled.png`});await page.evaluate(()=>window.__skyisles.world.panorama.labelled=false);}
 await page.setViewportSize(isMobile?{width:844,height:390}:{width:1280,height:720});
 const fitted=await page.evaluate(()=>{const w=window.__skyisles.world,b=w.bridges.bounds;return [[b.minX,b.minZ],[b.maxX,b.maxZ]].map(([x,z])=>w.player.pos.clone().set(x,0,z).project(w.panorama.camera).toArray());});
 for(const p of fitted){expect(Math.abs(p[0])).toBeLessThan(.86);expect(Math.abs(p[1])).toBeLessThan(.86);}
 await page.locator('#panorama-btn').click();await expect.poll(()=>page.evaluate(()=>window.__skyisles.getState().panoramaMode),{timeout:30000}).toBe('explore');
 const after=await page.evaluate(()=>{const w=window.__skyisles.world;return{pos:w.player.pos.toArray(),checkpoint:w.player.lastGrounded.toArray(),orbit:{...w.player.orbit},progress:w.puzzle.unlocked};});
 for(const key of['pos','checkpoint'])for(let i=0;i<3;i++)expect(after[key][i]).toBeCloseTo(before[key][i],10);expect(after.orbit).toEqual(before.orbit);expect(after.progress).toBe(before.progress);
 await page.locator('#policy-menu summary').click();await page.locator('#policy-list button').first().click();await expect(page.locator('#policy-title')).toHaveText('交通大升級');expect(errors).toEqual([]);
});
