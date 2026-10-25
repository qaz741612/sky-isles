// Actual Three.js renders. 'explore' uses the unchanged default follow/orbit;
// 'qa' changes only the camera for architectural inspection and is labelled.
import {chromium,devices} from '@playwright/test';
import fs from 'node:fs';
const stage=process.argv[3]||'after',folder=`docs/previews/eight-islands-world-redesign-v1/${stage}`,url=process.argv[2]||'http://127.0.0.1:4185';
const include=new Set((process.argv[4]||'').split(',').filter(Boolean));
fs.mkdirSync(folder,{recursive:true});
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--enable-unsafe-swiftshader']});
const stats={},errors=[];
try{for(const mobile of[false,true]){
 const context=await browser.newContext(mobile?{...devices['iPhone 15 Pro Max']}:{viewport:{width:1440,height:1000}}),page=await context.newPage();page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(url);await page.waitForFunction(()=>window.__skyisles);await page.locator('#title-screen .tap').click();if(await page.locator('#touch-help').isVisible())await page.locator('#help-close').click();await page.waitForFunction(()=>window.__skyisles.world.player.move.grounded);
 await page.addStyleTag({content:'.qa-capture #hud,.qa-capture #hint,.qa-capture #policy-nav,.qa-capture #island-labels,.qa-capture #panorama-btn{visibility:hidden!important}'});
 await page.evaluate(()=>{const w=window.__skyisles.world;w.captureStep=w.player.update.bind(w.player);w.player.update=()=>{};w.transport.update=()=>{};w.transport.train.position.x=.9;});
 const shot=async(name)=>{stats[name]=await page.evaluate(()=>{const w=window.__skyisles.world,c=w.panorama.camera,t=performance.now();for(let i=0;i<120;i++)w.player.cameraConstraint?.(w.player._camTarget,w.camera.position.clone());const cpu=(performance.now()-t)/120;w.renderer.render(w.scene,c);return{qaArchitectureUIHidden:document.body.classList.contains('qa-capture'),sourceAsset:document.querySelector('script[src^="/assets/"]').getAttribute('src'),viewport:[innerWidth,innerHeight],camera:c.position.toArray(),quaternion:c.quaternion.toArray(),calls:w.renderer.info.render.calls,triangles:w.renderer.info.render.triangles,textures:w.renderer.info.memory.textures,cameraQueryCPUms:cpu,cameraIndex:w.player.cameraConstraint?.stats,player:w.player.pos.toArray()};});await page.screenshot({path:`${folder}/${name}.png`});console.log(stage,name,stats[name].calls);};
 const names=await page.evaluate(()=>window.__skyisles.world.islands.islands.map(i=>i.name));
 for(const name of names){if(include.size&&!include.has(name))continue;
 await page.evaluate(({name,mobile})=>{const w=window.__skyisles.world,i=w.islands.islands.find(i=>i.name===name),p=w.player;p.teleport(i.pos.x,.2,i.pos.z+3.5);Object.assign(p.orbit,mobile?{yaw:.12,pitch:.67,dist:22}:{yaw:.16,pitch:.6,dist:16});for(let j=0;j<100;j++)w.captureStep(1/60,{x:0,z:0,jumpHeld:false,jumpPressed:false},j/60);}, {name,mobile});
 await page.waitForTimeout(200);await shot(`${mobile?'mobile':'desktop'}-${name}-explore`);
 if(!mobile&&stage==='after'){await page.evaluate(()=>document.body.classList.add('qa-capture'));
 for(const[side,offset]of[['front',[0,6,13]],['side',[13,6,0]],['back',[0,6,-13]],['top',[0,26,0]]]){await page.evaluate(({name,offset,side})=>{const w=window.__skyisles.world,i=w.islands.islands.find(i=>i.name===name);w.camera.position.set(i.pos.x+offset[0],offset[1],i.pos.z+offset[2]);w.camera.up.set(0,side==='top'?0:1,side==='top'?-1:0);w.camera.lookAt(i.pos.x,.8,i.pos.z);},{name,offset,side});await shot(`qa-${name}-${side}`);}await page.evaluate(()=>{window.__skyisles.world.camera.up.set(0,1,0);document.body.classList.remove('qa-capture');});
 }
 }
 if(!mobile&&!include.size){await page.evaluate(()=>{const w=window.__skyisles.world;w.panorama.enter();w.panorama.update(2);});await shot('panorama-pure');await page.evaluate(()=>window.__skyisles.world.panorama.labelled=true);await page.waitForTimeout(250);await shot('qa-panorama-labelled');}
 if(mobile&&!include.size){await page.setViewportSize({width:932,height:430});await page.evaluate(()=>{const w=window.__skyisles.world;w.player.teleport(0,.2,3.5);Object.assign(w.player.orbit,{yaw:.16,pitch:.6,dist:18});for(let j=0;j<100;j++)w.captureStep(1/60,{x:0,z:0,jumpHeld:false,jumpPressed:false},j/60);});await shot('mobile-landscape-home');await page.evaluate(()=>{const w=window.__skyisles.world;w.panorama.enter();w.panorama.update(2);});await page.setViewportSize({width:430,height:932});await page.waitForTimeout(250);await shot('mobile-panorama');}
 await context.close();}
fs.writeFileSync(`${folder}/render-stats.json`,JSON.stringify({views:stats,errors},null,2));if(errors.length)throw Error(errors.join('\n'));
}finally{await browser.close();}
