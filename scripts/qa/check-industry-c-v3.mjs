import {chromium} from 'playwright';
import fs from 'node:fs';
const full=process.argv.includes('--full'),port=process.env.C_QA_PORT??'4220',dir=process.env.C_QA_DIR??'docs/previews/industry-youth-island-c-v3';fs.mkdirSync(dir,{recursive:true});
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--enable-unsafe-swiftshader']});
let failed=false;
for(const mobile of (process.argv.includes('--desktop-only')?[false]:[false,true])){
 const context=await browser.newContext({viewport:mobile?{width:430,height:932}:{width:1200,height:800},deviceScaleFactor:1,isMobile:mobile,hasTouch:mobile}),page=await context.newPage(),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(()=>{const raf=requestAnimationFrame.bind(window);window.requestAnimationFrame=fn=>(fn.name==='frame'||fn.toString().includes('.render('))?(window.__qaFrame=fn,0):raf(fn);});
 try{
  await page.goto(`http://127.0.0.1:${port}/`);await page.waitForFunction(()=>window.__skyisles&&document.querySelector('#loading').classList.contains('hidden'),null,{timeout:180000});
  const result=await page.evaluate(({full})=>{
   const w=window.__skyisles.world,p=w.player,tick=p.update.bind(p);window.__skyisles.start();let t=0;
   const step=(x=0,z=0)=>tick(1/60,{x,z,jumpPressed:false,jumpHeld:false},++t/60);
   function walk(target,label){let n=0;while(Math.hypot(p.pos.x-target.x,p.pos.z-target.z)>.16&&n++<1600){const dx=target.x-p.pos.x,dz=target.z-p.pos.z,d=Math.hypot(dx,dz),a=p.orbit.yaw;step((dx*Math.cos(a)-dz*Math.sin(a))/d,(dx*Math.sin(a)+dz*Math.cos(a))/d);if(p.pos.y<-.25||p.respawnCount)throw Error('ground gap '+label+' '+p.pos.toArray());}if(n>=1600)throw Error('obstruction '+label+' '+p.pos.toArray());}
   const routes=[];for(const path of w.bridges.walkPlans.filter(r=>full||['S14','S15','S16'].includes(r.id))){p.teleport(path.points[0].x,.1,path.points[0].z);for(let i=0;i<45;i++)step();for(const pt of [...path.points,...path.points.toReversed()])walk(pt,path.id);routes.push({id:path.id,bidirectional:true,noJump:true});}
   const c=w.industry.config.centre,world=([x,z])=>({x:x+c[0],z:z+c[2]});p.teleport(c[0],.2,c[2]);for(let i=0;i<45;i++)step();
   const loop=[[0,0],[3,0],[4.1,-1.05],[4.9,-1.05],[3,-1],[0,0],[0,4],[.5,6.95],[.5,8.35],[.5,9.6],[2.4,9.8],[4.5,9.85],[6,9.8],[4.5,9.85],[2.4,9.8],[.5,9.6],[0,4],[-3,0],[-4.6,-.55],[-5.3,-.55],[-4.6,-.55],[-3,0],[0,0]];
   for(const pt of loop)walk(world(pt),'campus '+pt);
   const camera=[];for(const pt of [[0,0],[4.9,-1.05],[6,9.8],[-5.3,-.55],[.5,6.95]]){p.teleport(c[0]+pt[0],.2,c[2]+pt[1]);for(let i=0;i<45;i++)step();for(let j=0;j<8;j++){p.orbit.yaw=j*Math.PI/4;for(let k=0;k<15;k++)step();if(!Number.isFinite(w.camera.position.x)||w.camera.position.distanceTo(p.pos)<2.7)throw Error('camera trapped '+pt);camera.push(w.camera.position.toArray());}}
   const before={position:p.pos.toArray(),checkpoint:p.lastGrounded.toArray(),orbit:{...p.orbit}};w.panorama.enter();w.panorama.update(1.2);w.panorama.leave();w.panorama.update(1.2);const after={position:p.pos.toArray(),checkpoint:p.lastGrounded.toArray(),orbit:{...p.orbit}};
   if(JSON.stringify(before)!==JSON.stringify(after))throw Error('panorama state changed');const checkpoint=p.lastGrounded.clone();p.teleport(200,-50,200);step();if(p.pos.distanceTo(checkpoint)>.6)throw Error('unsafe recovery');
   return{routes,campusLoop:loop,cameraSamples:camera.length,forcedRecovery:true,panoramaRestores:true,stats:w.industry.stats,meshes:w.industry.meshes.length,npc:w.industry.config.npc,ticks:t,mode:'fixed-60Hz engineering traversal; native physics and camera; no hardware FPS claim'};
  },{full});
  fs.writeFileSync(`${dir}/routes-${mobile?'mobile':'desktop'}${full?'':'-checkpoint-a'}.json`,JSON.stringify({passed:errors.length===0,errors,...result},null,2));
  console.log((mobile?'mobile':'desktop')+': '+result.routes.length+' routes, campus and camera passed');
 }catch(e){failed=true;fs.writeFileSync(`${dir}/failure-${mobile?'mobile':'desktop'}.json`,JSON.stringify({error:e.message,errors},null,2));console.log((mobile?'mobile':'desktop')+': FAILED (details in file)');}
 await context.close();
}
await browser.close();if(failed)process.exitCode=1;
