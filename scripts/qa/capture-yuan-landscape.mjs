// Actual game capture, no Blender renders. Run from repo root against a fixed build.
import {chromium} from 'playwright';import fs from 'node:fs';
const port=process.argv[2]??'4200',folder=process.argv[3]??'docs/previews/yuan-bridges-landscape-v1/map-checkpoint',final=process.argv.includes('--landscape');fs.mkdirSync(folder,{recursive:true});
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--enable-unsafe-swiftshader']});const records=[];
for(const mobile of[false,true]){
 const context=await browser.newContext({viewport:mobile?{width:430,height:932}:{width:1200,height:800},deviceScaleFactor:1,isMobile:mobile,hasTouch:mobile});const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(`http://127.0.0.1:${port}/`);await page.waitForFunction(()=>window.__skyisles&&document.querySelector('#loading').classList.contains('hidden'),null,{timeout:180000});
 await page.evaluate(()=>{const w=window.__skyisles.world;window.__skyisles.start();w.draw=w.renderer.render.bind(w.renderer);w.renderer.render=()=>{};w.step=w.player.update.bind(w.player);w.player.update=()=>{};for(let i=0;i<80;i++)w.step(1/60,{x:0,z:0,jumpPressed:false,jumpHeld:false},i/60);});
 await page.evaluate(()=>{const el=document.querySelector('#title-screen');window.getComputedStyle(el).opacity;el.getAnimations().forEach(a=>a.finish());});
await page.waitForTimeout(100);
 async function shot(name,kind,fn,args){if(fn)await page.evaluate(fn,args);const result=await page.evaluate(()=>{const w=window.__skyisles.world;w.scene.updateMatrixWorld(true);w.draw(w.scene,w.panorama.camera);const gl=w.renderer.getContext(),ext=gl.getExtension('WEBGL_debug_renderer_info');return{position:w.player.pos.toArray(),orbit:w.player.orbit,camera:w.panorama.camera.position.toArray(),render:{...w.renderer.info.render},memory:{...w.renderer.info.memory},landscape:w.bridges.landscape?.stats,gpu:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER)};});await page.screenshot({path:`${folder}/${name}.png`,timeout:120000,animations:'disabled'});records.push({name,kind,viewport:page.viewportSize(),errors:[...errors],...result});}
 await shot(mobile?'mobile-player':'desktop-player','unchanged default player camera and original spawn');
 if(!mobile){
  await shot('family-separation','QA position at transport west mouth, normal player orbit',()=>{const w=window.__skyisles.world,p=w.player,i=w.islands.islands.find(i=>i.name==='tree');p.teleport(-8,.1,0);p.orbit.yaw=Math.atan2(p.pos.x-i.pos.x,p.pos.z-i.pos.z);for(let i=0;i<80;i++)w.step(1/60,{x:0,z:0,jumpPressed:false,jumpHeld:false},i/60);});
  if(final){
   for(const[id,name]of[['S02','zone-1'],['S07','zone-2'],['S11','zone-3'],['S16','zone-4'],['S19','zone-5']])await shot(name,`custom QA bridge camera ${id}`,({id})=>{const w=window.__skyisles.world,p=w.bridges.plans.find(p=>p.id===id),pt=p.points[Math.floor(p.points.length*.5)];w.camera.position.set(pt.x+9,10,pt.z+12);w.camera.lookAt(pt.x,0,pt.z);w.camera.updateMatrixWorld();},{id});
   await shot('seven-lamp-close','custom QA camera; real shared 7-shaped lamp',()=>{const w=window.__skyisles.world,l=w.bridges.landscape.plan.lamps.find(l=>l.type==='seven'),p=l.position;w.camera.position.set(p[0]+3.8,3.6,p[2]+4);w.camera.lookAt(p[0],1.8,p[2]);w.camera.updateMatrixWorld();});
  }
  await page.evaluate(()=>{const w=window.__skyisles.world;w.panorama.enter();w.panorama.update(1.2);});await page.waitForTimeout(100);await shot('yuan-panorama','actual fitted orthographic panorama, labels hidden');
 }else if(final){await page.setViewportSize({width:932,height:430});await shot('mobile-landscape','mobile orientation change, same user orbit');await page.setViewportSize({width:430,height:932});await page.evaluate(()=>{const w=window.__skyisles.world;w.panorama.enter();w.panorama.update(1.2);});await page.waitForTimeout(100);await shot('mobile-panorama','actual portrait orthographic panorama');}
 await context.close();
}
fs.writeFileSync(`${folder}/capture-record.json`,JSON.stringify(records,null,2)+'\n');await browser.close();console.log('Captured '+records.length+' actual game views.');
