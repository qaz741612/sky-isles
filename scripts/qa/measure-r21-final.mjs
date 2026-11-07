// PR19 final polish: identical F-spawn and world panorama, both all-eight-island scenes.
// Software GPU observations, never a real-device FPS certification.
import{chromium}from'playwright';import fs from'node:fs';import{createHash}from'node:crypto';
const output='docs/previews/bdeh-r21/final-qa/performance.json',hash=b=>createHash('sha256').update(b).digest('hex'),results=[];
const cases=[['before',4275,'work/bdeh-final-83-dist'],['after',4280,'work/r21-final-candidate5-dist']];
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--enable-unsafe-swiftshader']});
try{for(const[stage,port,dist]of cases)for(const mobile of[false,true]){
 const page=await browser.newPage({viewport:mobile?{width:430,height:932}:{width:1200,height:800},deviceScaleFactor:1,isMobile:mobile,hasTouch:mobile});
 await page.addInitScript(()=>{const raf=requestAnimationFrame.bind(window);window.requestAnimationFrame=fn=>(fn.name==='frame'||fn.toString().includes('.render('))?(window.__qaFrame=fn,0):raf(fn);});
 const bundles=fs.readdirSync(`${dist}/assets`).filter(n=>/^index-.*\.js$/.test(n)),verified=[];
 const requests=bundles.map(n=>page.waitForResponse(r=>r.url().endsWith(`/assets/${n}`),{timeout:180000}).then(async r=>{const actual=hash(await r.body());if(actual!==hash(fs.readFileSync(`${dist}/assets/${n}`)))throw Error('stale benchmark bundle');verified.push({path:`assets/${n}`,sha256:actual});}));
 await page.goto(`http://127.0.0.1:${port}/`);await Promise.all(requests);await page.waitForFunction(()=>window.__skyisles&&document.querySelector('#loading').classList.contains('hidden'),null,{timeout:180000});
 const report=await page.evaluate(()=>{
  const w=window.__skyisles.world,p=w.player;window.__skyisles.start();const draw=w.renderer.render.bind(w.renderer),step=p.update.bind(p);w.renderer.render=()=>{};p.update=()=>{};window.__qaFrame();
  const ready=performance.now(),gl=w.renderer.getContext(),ext=gl.getExtension('WEBGL_debug_renderer_info'),views=[];
  const originalOrbit={...p.orbit};
  for(const name of['F-native','D-native','E-native','H-native','panorama']){
   if(name==='panorama'){w.panorama.enter();w.panorama.update(2);}else{Object.assign(p.orbit,originalOrbit);p.cameraConstraint.resetVisit?.();const c=name==='F-native'?[0,.5,3.5]:w.r21[name[0]].config.centre;p.teleport(c[0],.5,c[2]);for(let i=0;i<300;i++){p.cameraConstraint.setDelta?.(1/60);step(1/60,{x:0,z:0,jumpPressed:false,jumpHeld:false},i/60);}}
   const camera=w.panorama.camera;w.scene.updateMatrixWorld(true);for(let i=0;i<2;i++){draw(w.scene,camera);gl.finish();}
   const times=[];for(let i=0;i<6;i++){const t=performance.now();draw(w.scene,camera);gl.finish();times.push(performance.now()-t);}times.sort((a,b)=>a-b);
   const cpu=[];if(name!=='panorama')for(let i=0;i<5;i++){const t=performance.now();for(let k=0;k<100;k++)step(1/60,{x:0,z:0,jumpPressed:false,jumpHeld:false},10+i+k/60);cpu.push((performance.now()-t)/100);}cpu.sort((a,b)=>a-b);
   views.push({name,camera:camera.position.toArray(),player:p.pos.toArray(),orbit:{...p.orbit},drawCalls:w.renderer.info.render.calls,triangles:w.renderer.info.render.triangles,memory:{...w.renderer.info.memory},synchronizedSoftwareFrameMs:{samples:times,median:(times[2]+times[3])/2,max:times.at(-1)},controllerCPUms:cpu[2]??null});
  }
  return{allEightLoaded:w.islands.islands.length,navigationReadyAtMs:ready,GLBLoads:Object.fromEntries(Object.entries(w.r21??{}).map(([c,v])=>[c,v.stats])),views,webGL:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):'unknown',webGLError:gl.getError()};
 });results.push({stage,base:stage==='before'?'PR19 39f4194 frozen baseline':'PR19 final QA candidate5 verified production build',mobile,viewport:page.viewportSize(),dpr:1,verifiedBundles:verified,...report});
 fs.writeFileSync(output,JSON.stringify({method:'All eight islands loaded, same F player spawn and native original profile, complete orthographic panorama. Six gl.finish frames after two warmups, five batches of100 idle real Player ticks. Local HTTP. Loading-screen readiness is not a hardware first-interactive-frame measure.',limits:'Chromium ANGLE SwiftShader, shared cloud two-core CPU. This is diagnostic software timing, not hardware FPS, real mobile heat, bandwidth or long-touch acceptance.',results},null,2)+'\n');console.log(stage,mobile?'portrait':'desktop','measured');await page.close();
}}finally{await browser.close();}
