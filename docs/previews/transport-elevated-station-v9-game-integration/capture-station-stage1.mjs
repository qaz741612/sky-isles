import {chromium} from 'playwright';
import fs from 'node:fs';
const folder='docs/previews/transport-elevated-station-v9-game-integration';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader']});
const captures=[];
for(const mobile of[true,false]){
 const context=await browser.newContext({viewport:mobile?{width:430,height:932}:{width:1200,height:800},isMobile:mobile,hasTouch:mobile,deviceScaleFactor:1});const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:4196/');await page.waitForFunction(()=>window.__skyisles&&document.querySelector('#loading').classList.contains('hidden'),null,{timeout:180000});
 await page.evaluate(()=>{const w=window.__skyisles.world;window.__skyisles.start();w.savedRender=w.renderer.render.bind(w.renderer);w.renderer.render=()=>{};w.savedStep=w.player.update.bind(w.player);w.player.update=()=>{};for(let i=0;i<90;i++)w.savedStep(1/60,{x:0,z:0,jumpPressed:false,jumpHeld:false},i/60);});
 async function shot(name,description,setup){
  if(setup)await page.evaluate(setup);
  const details=await page.evaluate(()=>{const w=window.__skyisles.world;w.scene.updateMatrixWorld(true);w.savedRender(w.scene,w.panorama.camera);const gl=w.renderer.getContext(),ext=gl.getExtension('WEBGL_debug_renderer_info');return{player:w.player.pos.toArray(),camera:w.panorama.camera.position.toArray(),orbit:{...w.player.orbit},render:{...w.renderer.info.render},memory:{...w.renderer.info.memory},load:w.transport.stats,gpu:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER)};});
  await page.screenshot({path:`${folder}/${name}.png`,timeout:120000});captures.push({name,description,viewport:page.viewportSize(),deviceScaleFactor:1,errors:[...errors],...details});
 }
 await shot(mobile?'mobile-default':'desktop-default','Actual game, original spawn and unchanged default camera profile. QA start skips title only.');
 if(mobile){
  await page.setViewportSize({width:932,height:430});await page.evaluate(()=>{const w=window.__skyisles.world;for(let i=0;i<90;i++)w.savedStep(1/60,{x:0,z:0,jumpPressed:false,jumpHeld:false},i/60);});await shot('mobile-landscape','Actual mobile landscape; same portrait-entry orbit retained after orientation change.');
 }else{
  await shot('from-family','Actual exploration camera at approved family south entrance; QA teleport, normal orbit.',()=>{const w=window.__skyisles.world,p=w.player,isle=w.islands.islands.find(i=>i.name==='tree');p.teleport(isle.pos.x+1.1,.1,isle.pos.z+8.2);p.orbit.yaw=Math.atan2(p.pos.x,p.pos.z);for(let i=0;i<90;i++)w.savedStep(1/60,{x:0,z:0,jumpPressed:false,jumpHeld:false},i/60);});
  await shot('toward-family','Actual exploration camera at transport west mouth toward family; QA teleport, normal orbit.',()=>{const w=window.__skyisles.world,p=w.player,isle=w.islands.islands.find(i=>i.name==='tree');p.teleport(-8,.1,0);p.orbit.yaw=Math.atan2(p.pos.x-isle.pos.x,p.pos.z-isle.pos.z);for(let i=0;i<90;i++)w.savedStep(1/60,{x:0,z:0,jumpPressed:false,jumpHeld:false},i/60);});
  await shot('station-45-qa','Actual Three.js scene, custom QA camera; not the default player view.',()=>{const w=window.__skyisles.world;w.camera.position.set(22,18,24);w.camera.lookAt(0,1.8,-2);w.camera.updateMatrixWorld();});
  await page.evaluate(()=>{const w=window.__skyisles.world;w.panorama.enter();w.panorama.update(1.2);});await page.waitForTimeout(150);await shot('yuan-panorama','Actual full-world orthographic panorama; no policy labels.');
 }
 await context.close();
}
fs.writeFileSync(`${folder}/capture-record.json`,JSON.stringify(captures,null,2)+'\n');await browser.close();console.log(JSON.stringify({captures:captures.map(c=>c.name),errors:captures.flatMap(c=>c.errors)}));
