// Identical cameras, viewport sizes and frozen train phase for both versions.
import {chromium,devices} from '@playwright/test';
import fs from 'node:fs';
const url=process.argv[2]||'http://127.0.0.1:4185';
const stage=process.argv[3]||'after';
const root='docs/previews/transport-island-polish-v4',folder=`${root}/${stage}`;
const include=new Set((process.argv[4]||'').split(',').filter(Boolean));
fs.mkdirSync(folder,{recursive:true});
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--enable-unsafe-swiftshader']});
const stats=include.size&&fs.existsSync(`${folder}/render-stats.json`)?JSON.parse(fs.readFileSync(`${folder}/render-stats.json`)).views:{},errors=[];
try{
for(const mobile of [false,true]){
 if(mobile&&include.size&&![...include].some(n=>n.startsWith('mobile-')))continue;
 const context=await browser.newContext(mobile?{...devices['iPhone 15 Pro Max']}:{viewport:{width:1440,height:1000}}),page=await context.newPage();page.on('pageerror',e=>errors.push(String(e)));
 const setup=async()=>{
 await page.goto(url);await page.waitForFunction(()=>window.__skyisles);await page.locator('#title-screen .tap').click();if(await page.locator('#touch-help').isVisible())await page.locator('#help-close').click();
 await page.waitForFunction(()=>window.__skyisles.world.player.move.grounded);await page.waitForTimeout(700);
 await page.evaluate(()=>{const w=window.__skyisles.world;w.captureStep=w.player.update.bind(w.player);w.player.update=()=>{};w.transport.update=()=>{};w.transport.train.position.x=.9;w.camera.position.copy(w.player._camPos);w.camera.position.y-=w.player.pos.y;w.camera.lookAt(w.player._camTarget.clone().setY(1.5));});
 };await setup();
 const shot=async name=>{
  if(include.size&&!include.has(name))return;
  stats[name]=await page.evaluate(()=>{const w=window.__skyisles.world,c=w.panorama.active?w.panorama.camera:w.camera;w.renderer.render(w.scene,c);let meshes=0,triangles=0;const textures=new Set();w.transport.group.traverse(o=>{if(o.isMesh){meshes++;triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;for(const m of [].concat(o.material))if(m.map)textures.add(m.map);}});return{viewport:[innerWidth,innerHeight],camera:c.position.toArray(),quaternion:c.quaternion.toArray(),calls:w.renderer.info.render.calls,triangles:w.renderer.info.render.triangles,transportMeshes:meshes,transportTriangles:triangles,transportTextures:[...textures].map(t=>[t.image.width,t.image.height]),worldTextures:w.renderer.info.memory.textures};});
  await page.screenshot({path:`${folder}/${name}.png`});
 };
 if(mobile){await shot('mobile-portrait');await page.setViewportSize({width:932,height:430});await setup();await shot('mobile-landscape');}
 else{
  await shot('spawn-view');
  const shots=[['station-front',[-.7,3.8,3],[-1.1,1.2,-4.1]],['platform-train',[6,4.2,-2.8],[0,.6,-6.4]],['station-rear',[-5.7,4.2,-9],[-2.7,1.2,-4.3]],['island-oblique',[12,16,20],[0,.5,-1.5]],['island-top',[0,28,0],[0,0,0]]];
  for(const [name,pos,target]of shots){await page.evaluate(({pos,target,name})=>{const w=window.__skyisles.world;w.camera.position.set(...pos);w.camera.up.set(0,1,0);if(name==='island-top')w.camera.up.set(0,0,-1);w.camera.lookAt(...target);}, {pos,target,name});await shot(name);}
  if(!include.size||include.has('yuan-panorama')){await page.locator('#panorama-btn').click();await page.waitForFunction(()=>window.__skyisles.world.panorama.mode==='overview',null,{timeout:90000});await shot('yuan-panorama');}
 }
 // Walk V3/V4's same four approaches and inspect the default follow camera.
 if(!mobile&&!include.size){await page.evaluate(()=>{const w=window.__skyisles.world;if(w.panorama.mode==='overview'){w.panorama.leave();w.panorama.update(2);}});
 const visit=await page.evaluate(stage=>{const w=window.__skyisles.world,p=w.player;const records=[];p.orbit.yaw=0;
 for(const id of ['S09','S10','S15','S18']){const route=w.bridges.plans.find(p=>p.id===id);const pts=(route.from==='F'?route.points:[...route.points].reverse()).filter(v=>Math.hypot(v.x,v.z)<=10).reverse();const a=pts[0];p.teleport(a.x,.1,a.z);for(let i=0;i<30;i++)w.captureStep(1/60,{x:0,z:0,jumpHeld:false,jumpPressed:false},0);
 let ok=true;for(const q of pts){let limit=500;while(Math.hypot(p.pos.x-q.x,p.pos.z-q.z)>.24&&limit-->0){const dx=q.x-p.pos.x,dz=q.z-p.pos.z,d=Math.hypot(dx,dz);w.captureStep(1/60,{x:dx/d,z:dz/d,jumpHeld:false,jumpPressed:false},0);if(!p.move.grounded)ok=false;}if(limit<=0)ok=false;}
 records.push({entry:id,grounded:ok,respawns:p.respawnCount,end:p.pos.toArray()});}
 const rear=stage==='before'?[[-4.6,-2.7],[-4.6,-5.87],[2.8,-5.87],[4.9,-5.87]]:[[-1.8,-2.5],[5,-2.5],[5,-5.7],[-4.9,-5.7],[3.5,-5.7]];
 const first=rear[0];p.teleport(first[0],.2,first[1]);for(let i=0;i<40;i++)w.captureStep(1/60,{x:0,z:0,jumpHeld:false,jumpPressed:false},0);let airborne=0,blocked=false;
 for(const [x,z]of rear){let remaining=600;while(Math.hypot(p.pos.x-x,p.pos.z-z)>.24&&remaining-->0){const dx=x-p.pos.x,dz=z-p.pos.z,len=Math.hypot(dx,dz);w.captureStep(1/60,{x:dx/len,z:dz/len,jumpHeld:false,jumpPressed:false},0);if(!p.move.grounded)airborne++;}if(remaining<=0){blocked=true;break;}}
 records.push({stationSideRear:{path:rear,airborneTicks:airborne,blocked,respawns:p.respawnCount}});
 return records;},stage);fs.writeFileSync(`${folder}/four-entry-walk.json`,JSON.stringify(visit,null,2));
 }
 await context.close();
}
fs.writeFileSync(`${folder}/render-stats.json`,JSON.stringify({views:stats,errors},null,2));if(errors.length)throw Error(errors.join('\n'));
}finally{await browser.close();}
