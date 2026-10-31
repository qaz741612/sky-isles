import {test,expect} from './helpers/software-qa.js';
import fs from 'node:fs';
test('C real model picking, original spring, NPC approach and live boundary guards',async({page,isMobile})=>{
 test.setTimeout(240000);const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(()=>{const raf=requestAnimationFrame.bind(window);window.requestAnimationFrame=fn=>(fn.name==='frame'||fn.toString().includes('.render('))?(window.__qaFrame=fn,0):raf(fn);});
 await page.goto('/');await page.waitForFunction(()=>window.__skyisles&&document.querySelector('#loading').classList.contains('hidden'),null,{timeout:180000});
 const result=await page.evaluate(()=>{
  const w=window.__skyisles.world,p=w.player,c=w.industry.config.centre,step=p.update.bind(p);window.__skyisles.start();let t=0;const tick=(input={x:0,z:0,jumpPressed:false,jumpHeld:false})=>step(1/60,input,++t/60);
  const cap=w.islands.jumpPads.find(p=>{const v=p.cap.getWorldPosition(w.player.pos.clone());return Math.hypot(v.x-c[0],v.z-c[2])<6;});if(!cap)throw Error('C original spring missing');
  const pos=cap.cap.getWorldPosition(p.pos.clone());p.teleport(pos.x,pos.y+1,pos.z);for(let i=0;i<70;i++)tick();const walkingVy=p.move.vy;if(Math.abs(walkingVy)>.1)throw Error('walker auto-launched');
  let springVy=0;for(let i=0;i<10;i++){tick({x:0,z:0,jumpPressed:false,jumpHeld:true});springVy=Math.max(springVy,p.move.vy);}if(springVy<10)throw Error('spring jump lost');
  const walls=w.bridges.barriers.filter(b=>b.island==='koi'&&Math.hypot(b.b.x-b.a.x,b.b.z-b.a.z)>.2),checked=[];
  for(const b of walls.filter((_,i)=>i%Math.max(1,Math.floor(walls.length/8))===0)){
   const x=(b.a.x+b.b.x)/2,z=(b.a.z+b.b.z)/2,dx=b.b.x-b.a.x,dz=b.b.z-b.a.z,d=Math.hypot(dx,dz);let ux=dz/d,uz=-dx/d;if((x-c[0])*ux+(z-c[2])*uz<0){ux=-ux;uz=-uz;}p.teleport(x-ux*.9,.3,z-uz*.9);for(let i=0;i<50;i++)tick();const before=p.pos.clone();for(let i=0;i<110;i++){const a=p.orbit.yaw;tick({x:ux*Math.cos(a)-uz*Math.sin(a),z:ux*Math.sin(a)+uz*Math.cos(a),jumpPressed:false,jumpHeld:false});}if(p.respawnCount||p.pos.y<-.25)throw Error('ordinary edge fall');if((p.pos.x-x)*ux+(p.pos.z-z)*uz>.1)throw Error('walked through C rail '+JSON.stringify({wall:b,player:p.pos.toArray()}));checked.push({a:b.a,b:b.b,moved:p.pos.distanceTo(before)});
  }
  p.teleport(c[0],.2,c[2]);for(let i=0;i<40;i++)tick();
  w.camera.position.set(c[0]-2,4,c[2]+4);w.camera.lookAt(c[0]+5.1,1.8,c[2]+.25);w.camera.updateMatrixWorld();w.scene.updateMatrixWorld(true);
  return{walkingVy,springVy,outerEdges:checked,npc:w.industry.config.npc,model:w.industry.stats,originalPadPosition:pos.toArray()};
 });
 await page.mouse.click((await page.viewportSize()).width/2,(await page.viewportSize()).height/2);await expect(page.locator('#policy-dialog')).toBeVisible();await expect(page.locator('#policy-title')).toHaveText('產業青年');await page.locator('#policy-close').click();await expect(page.locator('#policy-dialog')).not.toBeVisible();expect(errors).toEqual([]);
 fs.mkdirSync(process.env.C_QA_DIR??'docs/previews/industry-youth-island-c-v1',{recursive:true});fs.writeFileSync(`${process.env.C_QA_DIR??'docs/previews/industry-youth-island-c-v1'}/interactions-${isMobile?'mobile':'desktop'}.json`,JSON.stringify({...result,modelPicking:true,errors},null,2)+'\n');
});
