// Actual game frames. Freeze only automated rendering; native Player/orbit and
// geometry are unchanged. QA lenses are explicitly separate from native poses.
import {chromium}from'playwright';import fs from'node:fs';import{createHash}from'node:crypto';
const dir=process.argv[2]??'docs/previews/bdeh-r21/final-game',port=process.argv[3]??4274,assetRoot=process.argv[4]??'public/models/bdeh-r21';
const bundleRoot=assetRoot.replace(/\/models\/bdeh-r21\/?$/,'');const bundles=Object.fromEntries(fs.readdirSync(`${bundleRoot}/assets`).filter(n=>/^index-.*\.js$/.test(n)).map(n=>[`/assets/${n}`,fs.readFileSync(`${bundleRoot}/assets/${n}`)]));
fs.mkdirSync(dir,{recursive:true});const hash=b=>createHash('sha256').update(b).digest('hex'),assets=Object.fromEntries([...'BDEH'].map(c=>[c,hash(fs.readFileSync(`${assetRoot}/${c}.glb`))])),records=[],bundleHashes=Object.fromEntries(Object.entries(bundles).map(([n,b])=>[n,hash(b)]));
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--enable-unsafe-swiftshader']});
try{for(const mobile of[false,true]){
 const context=await browser.newContext({viewport:mobile?{width:430,height:932}:{width:1200,height:800},deviceScaleFactor:1,isMobile:mobile,hasTouch:mobile}),page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(()=>{const get=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(kind,attrs){return get.call(this,kind,/^webgl/.test(kind)?{...attrs,preserveDrawingBuffer:true}:attrs);};const raf=requestAnimationFrame.bind(window);window.requestAnimationFrame=fn=>(fn.name==='frame'||fn.toString().includes('.render('))?(window.__qaFrame=fn,0):raf(fn);});
 const bundleResponses=Object.entries(bundleHashes).map(([path,sha])=>page.waitForResponse(r=>r.url().endsWith(path),{timeout:180000}).then(async r=>{if(hash(await r.body())!==sha)throw Error('Stale compiled game bundle');}));
 const responses=[...'BDEH'].map(code=>page.waitForResponse(r=>r.url().endsWith(`/models/bdeh-r21/${code}.glb`),{timeout:180000}).then(async r=>{if(hash(await r.body())!==assets[code])throw Error(`Stale ${code} asset`);}));
 await page.goto(`http://127.0.0.1:${port}/`);await Promise.all([...responses,...bundleResponses]);await page.waitForFunction(()=>window.__skyisles&&document.querySelector('#loading').classList.contains('hidden'),null,{timeout:180000});
 await page.evaluate(()=>{const api=window.__skyisles,w=api.world;api.start();w.nativeOrbit={...w.player.orbit};w.draw=w.renderer.render.bind(w.renderer);w.renderer.render=()=>{};w.step=w.player.update.bind(w.player);w.player.update=()=>{};window.__qaFrame();const e=document.querySelector('#title-screen');getComputedStyle(e).opacity;e.getAnimations().forEach(a=>a.finish());});
 async function shot(code,name,kind){
  const data=await page.evaluate(({code,kind})=>{const w=window.__skyisles.world,p=w.player,c=w.r21[code].config.centre;Object.assign(p.orbit,w.nativeOrbit);if(w.panorama.mode!=='explore'){w.panorama.leave();w.panorama.update(2);}
   if(kind.startsWith('native')){p.teleport(c[0],.2,c[2]);if(kind==='native-facing')p.orbit.yaw=Math.PI+.16;if(kind==='native-npc'){const npc=w.r21[code].config.npc[0];p.teleport(c[0]+npc.playerStop[0],.2,c[2]+npc.playerStop[2]);p.orbit.yaw=npc.facing;}for(let i=0;i<120;i++)w.step(1/60,{x:0,z:0,jumpPressed:false,jumpHeld:false},i/60);if(!p.move.grounded||p.pos.y<-.01)throw Error(`${code} native not grounded`);}
   else if(kind==='panorama'){w.panorama.enter();w.panorama.update(2);}else{w.camera.position.set(c[0]+(kind==='top'?.001:36),kind==='top'?58:30,c[2]+(kind==='top'?.001:-42));w.camera.lookAt(c[0],kind==='top'?0:1.4,c[2]);w.camera.updateMatrixWorld();}
   window.__qaFrame();w.scene.updateMatrixWorld(true);w.draw(w.scene,w.panorama.camera);const gl=w.renderer.getContext(),ext=gl.getExtension('WEBGL_debug_renderer_info');return{kind,centre:c,camera:w.panorama.camera.position.toArray(),player:p.pos.toArray(),orbit:{...p.orbit},grounded:p.move.grounded,stats:w.r21[code].stats,render:{...w.renderer.info.render},memory:{...w.renderer.info.memory},gpu:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):'unknown'};
  },{code,kind});await page.screenshot({path:`${dir}/${name}.png`,animations:'disabled',timeout:180000});records.push({name,code,mobile,size:page.viewportSize(),errors:[...errors],...data});fs.writeFileSync(`${dir}/capture-record.json`,JSON.stringify({assets,bundleHashes,method:'Actual loaded eight-island Three.js world; native uses original profile and real Player, facing simulates normal orbit rotation; hero/top are QA lenses. SwiftShader, not hardware FPS.',records},null,2)+'\n');console.log('saved',name);
 }
 for(const code of'BDEH'){
  if(!mobile){await shot(code,`${code}-hero`,'hero');await shot(code,`${code}-top`,'top');}
  await shot(code,`${code}-${mobile?'mobile':'desktop'}-native`,'native');await shot(code,`${code}-${mobile?'mobile':'desktop'}-facing`,'native-facing');await shot(code,`${code}-${mobile?'mobile':'desktop'}-npc-reservation`,'native-npc');
  if(mobile&&!process.argv.includes('--stage1')){await page.setViewportSize({width:932,height:430});await shot(code,`${code}-mobile-landscape`,'native-facing');await page.setViewportSize({width:430,height:932});}
 }
 await shot('H',mobile?'yuan-mobile-panorama':'yuan-desktop-panorama','panorama');await context.close();
}}finally{await browser.close();}
console.log('R21 actual game captures',records.length);
