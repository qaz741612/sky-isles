// Real production game frames: identical player/device/profile/gesture recipe.
// Native and touch gestures never set the camera; QA hero/top are separate.
import{chromium}from'playwright';import fs from'node:fs';import{createHash}from'node:crypto';
const port=Number(process.argv[2]??4278),out=process.argv[3]??'docs/previews/bdeh-r21/final-qa/game',option=(key,fallback)=>process.argv.includes(key)?process.argv[process.argv.indexOf(key)+1]:fallback,modelRoot=option('--models','public/models/bdeh-r21'),study=process.argv.includes('--study');fs.mkdirSync(out,{recursive:true});
const hash=b=>createHash('sha256').update(b).digest('hex'),expected=Object.fromEntries([...'BDEH'].map(c=>[`${c}.glb`,hash(fs.readFileSync(`${modelRoot}/${c}.glb`))])),records=[],browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--enable-unsafe-swiftshader']});
try{for(const profile of(study?(option('--profile',null)?[option('--profile')]:['portrait']):option('--profile',null)?[option('--profile')]:['desktop','portrait','landscape'])){
 const size=profile==='portrait'?{width:430,height:932}:profile==='landscape'?{width:932,height:430}:{width:1200,height:800};
 const context=await browser.newContext({viewport:size,deviceScaleFactor:1,isMobile:profile!=='desktop',hasTouch:profile!=='desktop'}),page=await context.newPage(),errors=[],served={},bundles={};page.on('pageerror',e=>errors.push(e.message));
 page.on('response',async r=>{if(/\/models\/bdeh-r21\/[BDEH]\.glb$/.test(r.url()))served[r.url().split('/').at(-1)]=hash(await r.body());else if(/\/assets\/index-.*\.js$/.test(r.url()))bundles[r.url().split('/').at(-1)]=hash(await r.body());});
 await page.addInitScript(()=>{const get=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(kind,attrs){return get.call(this,kind,/^webgl/.test(kind)?{...attrs,preserveDrawingBuffer:true}:attrs);};const raf=requestAnimationFrame.bind(window);window.requestAnimationFrame=fn=>(fn.name==='frame'||fn.toString().includes('.render('))?(window.__qaFrame=fn,0):raf(fn);});
 await page.goto(`http://127.0.0.1:${port}/`);await page.waitForFunction(()=>window.__skyisles&&document.querySelector('#loading').classList.contains('hidden'),null,{timeout:180000});
 await page.evaluate(()=>{const api=window.__skyisles,w=api.world;api.start();w.nativeOrbit={...w.player.orbit};w.draw=w.renderer.render.bind(w.renderer);w.renderer.render=()=>{};w.step=w.player.update.bind(w.player);w.player.update=()=>{};w.qt=0;w.tick=(wish)=>{const input=w.ui.poll(w.player.orbit);w.player.cameraConstraint.setDelta?.(1/60);w.step(1/60,wish??input,w.qt+=1/60);};window.__qaFrame();document.querySelector('#title-screen').getAnimations().forEach(a=>a.finish());});
 async function save(code,kind,initial){
  await page.waitForFunction(()=>{const w=window.__skyisles.world,c=w.renderer.domElement;return Math.abs(w.camera.aspect-innerWidth/innerHeight)<.0001&&c.width===Math.floor(innerWidth*w.renderer.getPixelRatio())&&c.height===Math.floor(innerHeight*w.renderer.getPixelRatio());});await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  const data=await page.evaluate(()=>{const w=window.__skyisles.world,p=w.player;window.__qaFrame();w.scene.updateMatrixWorld(true);w.draw(w.scene,w.panorama.camera);const gl=w.renderer.getContext();gl.finish();const ext=gl.getExtension('WEBGL_debug_renderer_info');return{player:p.pos.toArray(),camera:w.panorama.camera.position.toArray(),quaternion:w.panorama.camera.quaternion.toArray(),lookTarget:p._camTarget.toArray(),orbit:{...p.orbit},actualCameraFOV:w.camera.fov,aspect:w.camera.aspect,canvas:[w.renderer.domElement.width,w.renderer.domElement.height],grounded:p.move.grounded,discovery:p.cameraConstraint.state?.()??null,render:{...w.renderer.info.render},gpu:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):'unknown'};});
  const name=`${code}-${profile}-${kind}`;await page.screenshot({path:`${out}/${name}.png`,animations:'disabled',timeout:180000});records.push({name,code,profile,size,kind,initial,errors:[...errors],...data});fs.writeFileSync(`${out}/capture-record.json`,JSON.stringify({port,method:'Actual eight-island production game. Each centre/NPC initialization restores the original device orbit and player position, then idles5s. Same input recipe before/after. Left120px then right240px is one touch pointer; UI.poll drives the production camera, no direct native lens positioning. Only explicit QA-hero/top use custom lenses. Fixed60Hz poses, software GPU, not hardware performance.',expectedModels:expected,servedModels:served,bundleSHA256:bundles,records},null,2)+'\n');console.log('saved',name);
 }
 async function pose(code,npc=false){return await page.evaluate(({code,npc})=>{const w=window.__skyisles.world,p=w.player,place=w.r21[code],c=place.config.centre;if(w.panorama.mode!=='explore'){w.panorama.leave();w.panorama.update(2);}Object.assign(p.orbit,w.nativeOrbit);p.cameraConstraint.resetVisit?.();const stop=npc?place.config.npc[0].playerStop:[0,.2,0];p.teleport(c[0]+stop[0],.2,c[2]+stop[2]);const initial={player:[c[0]+stop[0],.2,c[2]+stop[2]],orbit:{...w.nativeOrbit},idleSeconds:5,source:'original initial device cameraProfile; engineering pose initialization'};for(let i=0;i<300;i++)w.tick({x:0,z:0,jumpPressed:false,jumpHeld:false});if(!p.move.grounded||Math.hypot(p.pos.x-initial.player[0],p.pos.z-initial.player[2])>.05)throw Error('native pose moved from intended clear position '+code);return initial;},{code,npc});}
 async function swipe(delta){
  const x=delta>0?Math.max(10,size.width*.23):Math.min(size.width-10,size.width*.72),y=size.height*.62;
  if(profile==='desktop')await page.mouse.move(x,y),await page.mouse.down();
  const cdp=profile==='desktop'?null:await context.newCDPSession(page);
  if(cdp)await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y,id:1}]});
  for(let i=1;i<=8;i++){
   const xx=x+delta*i/8;if(cdp)await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:xx,y,id:1}]});else await page.mouse.move(xx,y);
   await page.evaluate(()=>{const w=window.__skyisles.world;for(let k=0;k<6;k++)w.tick({x:0,z:0,jumpPressed:false,jumpHeld:false});});
  }
  if(cdp){await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await cdp.detach();}else await page.mouse.up();
  await page.evaluate(()=>{const w=window.__skyisles.world;for(let i=0;i<90;i++)w.tick({x:0,z:0,jumpPressed:false,jumpHeld:false});});
 }
 for(const code of option('--codes','BDEH')){
  const initial=await pose(code);await save(code,'native',initial);if(study)continue;
  await swipe(-120);await save(code,'single-finger-left',{...initial,gesture:{dx:-120,pointers:1,steps:8,after:'native'}});
  await swipe(240);await save(code,'single-finger-right',{...initial,gesture:{dx:240,pointers:1,steps:8,after:'left swipe'}});
  const npc=await pose(code,true);await save(code,'NPC-native',npc);
  if(profile==='desktop')for(const kind of['QA-hero','QA-top']){
   await page.evaluate(({code,kind})=>{const w=window.__skyisles.world,c=w.r21[code].config.centre;w.camera.position.set(c[0]+(kind==='QA-top'?.001:36),kind==='QA-top'?58:30,c[2]+(kind==='QA-top'?.001:-42));w.camera.lookAt(c[0],kind==='QA-top'?0:1.4,c[2]);w.camera.updateMatrixWorld();},{code,kind});await save(code,kind,{kind:'explicit QA camera, not a native player view'});
  }
 }
 if(!study&&!process.argv.includes('--no-pano')){await page.evaluate(()=>{const w=window.__skyisles.world;w.panorama.enter();w.panorama.update(2);});await save('world','panorama',{kind:'ordinary panorama button endpoint'});}
 for(const[c,sha]of Object.entries(expected))if(served[c]!==sha)throw Error('served model SHA mismatch '+c);
 if(errors.length)throw Error('Actual page errors: '+errors.join(';'));await context.close();
}}finally{await browser.close();}
