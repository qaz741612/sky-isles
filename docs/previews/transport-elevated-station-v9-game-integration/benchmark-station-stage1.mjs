import {chromium} from 'playwright';import fs from 'node:fs';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader']});const results=[];
for(const mobile of[false,true]){
 const context=await browser.newContext({viewport:mobile?{width:430,height:932}:{width:1200,height:800},isMobile:mobile,hasTouch:mobile,deviceScaleFactor:1});const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:4196/');await page.waitForFunction(()=>window.__skyisles&&document.querySelector('#loading').classList.contains('hidden'),null,{timeout:150000});
 const result=await page.evaluate(async()=>{
  const w=window.__skyisles.world;window.__skyisles.start();const render=w.renderer.render.bind(w.renderer);let warm=0;const times=[];
  await new Promise(resolve=>{w.renderer.render=(scene,camera)=>{render(scene,camera);if(warm++<3)return;times.push(performance.now());if(times.length===13){w.renderer.render=()=>{};resolve();}};});
  const intervals=times.slice(1).map((t,i)=>t-times[i]);const textures=new Set(),missing=[];
  for(const mesh of w.transport.station.meshes)for(const m of Array.isArray(mesh.material)?mesh.material:[mesh.material])for(const[key,v]of Object.entries(m))if(v?.isTexture){textures.add(v);if(!v.image?.width&&!v.image?.[0]?.width)missing.push(`${m.name}:${key}`);}
  const gl=w.renderer.getContext(),ext=gl.getExtension('WEBGL_debug_renderer_info');
  return{intervalsMilliseconds:intervals,frames:intervals.length,observedFPS:1000/(intervals.reduce((s,n)=>s+n,0)/intervals.length),renderer:{...w.renderer.info.render},memory:{...w.renderer.info.memory},source:w.transport.stats,stationBounds:{min:w.transport.station.bounds.min.toArray(),max:w.transport.station.bounds.max.toArray()},boundTextureCount:textures.size,missingTextureImages:missing,cameraCPUQueries:w.player.cameraConstraint.stats,gpu:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER)};
 });
 results.push({device:mobile?'mobile viewport':'desktop viewport',viewport:page.viewportSize(),deviceScaleFactor:1,notes:'SwiftShader software GPU, local server, brief stationary spawn sample. Not real phone/hardware FPS or WAN loading benchmark.',errors,...result});await context.close();
}
fs.writeFileSync('docs/previews/transport-elevated-station-v9-game-integration/software-render-diagnostic.json',JSON.stringify(results,null,2)+'\n');await browser.close();console.log(JSON.stringify(results.map(r=>({device:r.device,FPS:r.observedFPS,textureFailures:r.missingTextureImages,errors:r.errors}))));
