// Temporal input/physics/camera audit. Real GLBs and trusted touch, no draws.
// This cannot certify appearance or hardware performance; PNGs are separate.
import{chromium}from'playwright';import fs from'node:fs';import{createHash}from'node:crypto';
const port=Number(process.argv[2]??4296);
const out='docs/previews/bdeh-r21/final-qa/regression/manual-temporal-portrait.json',browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--enable-unsafe-swiftshader']});
try{
 const context=await browser.newContext({viewport:{width:430,height:932},deviceScaleFactor:1,isMobile:true,hasTouch:true}),page=await context.newPage();
 await page.addInitScript(()=>{let api;Object.defineProperty(window,'__skyisles',{configurable:true,get:()=>api,set:v=>{api=v;v.world.renderer.render=()=>{};}});const raf=requestAnimationFrame.bind(window);window.requestAnimationFrame=fn=>(fn.name==='frame'||fn.toString().includes('.render('))?(window.__qaFrame=fn,0):raf(fn);});
 await page.goto(`http://127.0.0.1:${port}/`);await page.waitForFunction(()=>window.__skyisles&&document.querySelector('#loading').classList.contains('hidden'),null,{timeout:180000});
 await page.evaluate(()=>{const api=window.__skyisles,w=api.world,p=w.player;api.start();w.originalOrbit={...p.orbit};w.step=p.update.bind(p);p.update=()=>{};w.qt=0;window.__qaFrame();w.scene.updateMatrixWorld(true);document.querySelector('#title-screen').getAnimations().forEach(a=>a.finish());});
 const html=await(await fetch(`http://127.0.0.1:${port}/`)).text(),asset=html.match(/src="([^"]+\.js)"/)[1],bundleSHA256=createHash('sha256').update(Buffer.from(await(await fetch(`http://127.0.0.1:${port}${asset}`)).arrayBuffer())).digest('hex');
 const cdp=await context.newCDPSession(page),rows=[];
 for(const code of'BDEH'){
  await page.evaluate(code=>{const w=window.__skyisles.world,p=w.player,c=w.r21[code].config.centre;Object.assign(p.orbit,w.originalOrbit);p.teleport(c[0],.2,c[2]);p.cameraConstraint.resetVisit();for(let k=0;k<300;k++){p.cameraConstraint.setDelta(1/60);w.step(1/60,w.ui.poll(p.orbit),w.qt+=1/60);}w.manualFrames=[];w.manualLast=null;w.manualMaxAngle=0;w.manualMaxStep=0;w.manualBlocked=0;},code);
  for(const[start,delta]of[[320,-120],[100,240]]){
   await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:start,y:560,id:1}]});
   for(let segment=1;segment<=24;segment++){
    await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:start+delta*segment/24,y:560,id:1}]});
    await page.evaluate(()=>{const w=window.__skyisles.world,p=w.player,ray=new p.ray.constructor(),obstacles=p.cameraConstraint.opaqueObstacles??Object.values(w.r21).flatMap(v=>v.cameraObstacles);for(let k=0;k<6;k++){p.cameraConstraint.setDelta(1/60);w.step(1/60,w.ui.poll(p.orbit),w.qt+=1/60);const now={position:w.camera.position.toArray(),quaternion:w.camera.quaternion.toArray(),orbit:{...p.orbit}};if(w.manualLast){w.manualMaxAngle=Math.max(w.manualMaxAngle,w.camera.quaternion.angleTo(p.camera.quaternion.clone().fromArray(w.manualLast.quaternion)));w.manualMaxStep=Math.max(w.manualMaxStep,w.camera.position.distanceTo(p.pos.clone().fromArray(w.manualLast.position)));}const head=p.pos.clone().add(p.pos.clone().set(0,1.5,0)),body=head.clone().add(p.pos.clone().set(0,-.75,0)),feet=head.clone().add(p.pos.clone().set(0,-1.3,0)),side=p.pos.clone().set(w.camera.position.z-head.z,0,head.x-w.camera.position.x).normalize().multiplyScalar(.32);for(const focus of[head,body,body.clone().add(side),body.clone().sub(side),feet.clone().addScaledVector(side,.78),feet.clone().addScaledVector(side,-.78)]){ray.set(focus,w.camera.position.clone().sub(focus).normalize());ray.far=focus.distanceTo(w.camera.position)-.03;if(ray.intersectObjects(obstacles,false).length)w.manualBlocked++;}w.manualFrames.push(now);w.manualLast=now;}});
   }
   await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  }
  const row=await page.evaluate(()=>{const w=window.__skyisles.world;return{frames:w.manualFrames,maxRadiansPer60HzTick:w.manualMaxAngle,maxWorldUnitsPer60HzTick:w.manualMaxStep,blockedSilhouetteProbes:w.manualBlocked,manualHandoff:w.player.cameraConstraint.state().manual};});const c=JSON.parse(fs.readFileSync('src/data/bdeh-plan.json')).islands[code].centre;let last=null,angles=[];for(const f of row.frames){const raw=Math.atan2(f.position[0]-c[0],f.position[2]-c[2]),a=last===null?raw:last+Math.atan2(Math.sin(raw-last),Math.cos(raw-last));angles.push(a);last=a;}row.actualAzimuthSpan=Math.max(...angles)-Math.min(...angles);rows.push({code,...row});fs.writeFileSync(out,JSON.stringify({port,bundle:asset,bundleSHA256,method:'Renderless engineering audit: actual loaded GLBs/colliders and production Player/UI at60Hz; one trusted CDP pointer,24 segments each120px left/240px right,6 ticks each; six body probes every tick. No pixels, human comfort, live cadence or hardware FPS claim.',rows})+'\n');console.log(code,JSON.stringify({step:row.maxWorldUnitsPer60HzTick,angle:row.maxRadiansPer60HzTick,blocked:row.blockedSilhouetteProbes}));
  if(row.actualAzimuthSpan<.55||!row.manualHandoff||row.maxRadiansPer60HzTick>.05||row.maxWorldUnitsPer60HzTick>.65||row.blockedSilhouetteProbes)throw Error('Manual temporal audit failed '+code);
 }
 await context.close();
}finally{await browser.close();}
