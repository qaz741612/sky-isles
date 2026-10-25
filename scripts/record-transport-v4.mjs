// Native keyboard/mouse input in the real running game; no teleports or sim stepping.
import {chromium} from '@playwright/test';
import fs from 'node:fs';
const folder='docs/previews/transport-island-polish-v4';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--enable-unsafe-swiftshader']});
const context=await browser.newContext({viewport:{width:1280,height:800},recordVideo:{dir:`${folder}/video-tmp`,size:{width:1280,height:800}}});
const page=await context.newPage(),log=[];const held=new Set();
async function keys(next){for(const k of held)if(!next.includes(k)){await page.keyboard.up(k);held.delete(k);}for(const k of next)if(!held.has(k)){await page.keyboard.down(k);held.add(k);}}
async function walk(x,z){await page.bringToFront();await keys([]);const deadline=Date.now()+60000;let state;
 while(Date.now()<deadline){state=await page.evaluate(()=>{const p=window.__skyisles.world.player;return{x:p.pos.x,z:p.pos.z,y:p.pos.y,yaw:p.orbit.yaw,respawns:p.respawnCount,focus:document.activeElement?.id,keys:[...window.__skyisles.world.ui._keys],modal:document.getElementById('policy-dialog').open};});const dx=x-state.x,dz=z-state.z,d=Math.hypot(dx,dz);if(d<.36)break;
 if([...held].some(k=>!state.keys.includes(k)))await keys([]);
 const cx=(dx*Math.cos(state.yaw)-dz*Math.sin(state.yaw))/d,cz=(dx*Math.sin(state.yaw)+dz*Math.cos(state.yaw))/d,next=[];
 if(cx>.32)next.push('KeyD');else if(cx<-.32)next.push('KeyA');if(cz>.32)next.push('KeyS');else if(cz<-.32)next.push('KeyW');await keys(next);await page.waitForTimeout(120);}
 await keys([]);await page.waitForTimeout(200);if(Math.hypot(x-state.x,z-state.z)>.5)throw Error(`native walk stuck: ${JSON.stringify({x,z,state})}`);log.push({target:[x,z],state});
}
try{
 await page.goto(process.argv[2]||'http://127.0.0.1:4185');await page.waitForFunction(()=>window.__skyisles);await page.locator('#title-screen .tap').click();await page.waitForFunction(()=>window.__skyisles.world.player.move.grounded);
 await walk(-1.8,-2.5);await walk(-1.8,-4.1);await walk(-1.8,-2.5);await walk(-5.8,-2.5);
 const xy=await page.evaluate(()=>{const w=window.__skyisles.world,h=w.transport.interactives.find(h=>h.userData.transportInfo==='vision'),p=h.position.clone().project(w.camera);return{x:(p.x+1)*innerWidth/2,y:(1-p.y)*innerHeight/2};});await page.mouse.click(xy.x,xy.y);await page.waitForTimeout(1200);log.push({modal:await page.locator('#policy-title').textContent(),visible:await page.getByRole('dialog').isVisible()});await page.locator('#policy-close').click();await page.waitForFunction(()=>!document.getElementById('policy-dialog').open);await page.waitForTimeout(250);
 await walk(2.25,-2.6);await walk(5,-2.5);await walk(5,-5.85);await walk(3.5,-5.85);
 await page.mouse.move(650,400);await page.mouse.down();await page.mouse.move(745,410,{steps:8});await page.mouse.up();await page.waitForTimeout(700);
 await page.locator('#panorama-btn').click();await page.waitForFunction(()=>window.__skyisles.world.panorama.mode==='overview');await page.waitForTimeout(1000);await page.locator('#panorama-btn').click();await page.waitForFunction(()=>window.__skyisles.world.panorama.mode==='explore');
 log.push({final:await page.evaluate(()=>window.__skyisles.getState()),sourceAsset:await page.evaluate(()=>document.querySelector('script[type=module]').getAttribute('src')),description:'Native keyboard/mouse automated operation; silent browser recording, not human handheld footage.'});
}finally{
 const video=page.video();await context.close();const source=await video.path();fs.renameSync(source,`${folder}/exploration.webm`);fs.rmSync(`${folder}/video-tmp`,{recursive:true,force:true});fs.writeFileSync(`${folder}/operation-log.json`,JSON.stringify(log,null,2));await browser.close();
}
