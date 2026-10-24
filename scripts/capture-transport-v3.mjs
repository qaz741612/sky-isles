import { chromium,devices } from '@playwright/test';
import fs from 'node:fs';
const folder='docs/previews/transport-island-redesign-v3';
const baseURL=process.argv[2]||'http://127.0.0.1:4185';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--enable-unsafe-swiftshader']});
try {
 for(const mobile of [false,true]){
 const context=await browser.newContext(mobile?{...devices['iPhone 15 Pro Max']}:{viewport:{width:1440,height:1000}}),page=await context.newPage();
 await page.goto(baseURL);await page.waitForFunction(()=>window.__skyisles);await page.locator('#title-screen .tap').click();
 if(await page.locator('#touch-help').isVisible())await page.locator('#help-close').click();
 await page.waitForFunction(()=>window.__skyisles.world.player.move.grounded);
 await page.waitForTimeout(1200);
 if(mobile){await page.screenshot({path:`${folder}/mobile-portrait.png`});await page.setViewportSize({width:932,height:430});await page.waitForTimeout(1000);await page.screenshot({path:`${folder}/mobile-landscape.png`});}
 else{
 await page.screenshot({path:`${folder}/spawn-view.png`});
 const shots=[
 ['island-top',[0,28,0],[0,0,0]],
 ['island-oblique',[12,16,20],[0,.5,-1.5]],
 ['station-front',[-.7,3.8,3],[-1.1,1.2,-4.1]],
 ['platform-train',[6,4.2,-2.8],[0,.6,-6.4]],
 ['npc-reservation',[5.2,3.3,2.8],[4.1,1.1,-4.2]]
 ];
 await page.evaluate(()=>{const w=window.__skyisles.world;w.captureStep=w.player.update.bind(w.player);w.player.update=()=>{};});
 for(const [name,pos,target]of shots){
 await page.evaluate(({pos,target,name})=>{const w=window.__skyisles.world;if(name==='npc-reservation'){const p=w.transport.plan.npcReservation.playerStop;w.player.teleport(...p);w.captureStep(1/60,{x:0,z:0,jumpHeld:false,jumpPressed:false},0);w.player.char.group.rotation.y=Math.PI;}w.camera.position.set(...pos);w.camera.up.set(0,1,0);if(name==='island-top')w.camera.up.set(0,0,-1);w.camera.lookAt(...target);w.scene.fog=null;w.renderer.render(w.scene,w.camera);}, {pos,target,name});
 await page.waitForTimeout(300);await page.screenshot({path:`${folder}/${name}.png`});
 }
 await page.locator('#panorama-btn').click();await page.waitForFunction(()=>window.__skyisles.world.panorama.mode==='overview');await page.screenshot({path:`${folder}/yuan-panorama.png`});
 }
 const stats=await page.evaluate(()=>{const w=window.__skyisles.world;let triangles=0,meshes=0;w.transport.group.traverse(o=>{if(o.isMesh){meshes++;triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;}});return{meshes,triangles,calls:w.renderer.info.render.calls,worldTriangles:w.renderer.info.render.triangles};});
 fs.writeFileSync(`${folder}/${mobile?'mobile':'desktop'}-render-stats.json`,JSON.stringify(stats,null,2));
 await context.close();}
}finally{await browser.close();}
