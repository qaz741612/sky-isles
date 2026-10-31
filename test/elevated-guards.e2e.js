import {test,expect} from './helpers/software-qa.js';
import fs from 'node:fs';
test('new V9 plinth visible north/east/west guards stop ordinary live Player walking',async({page,isMobile})=>{
 test.setTimeout(240000);await page.goto('/');await page.waitForFunction(()=>window.__skyisles&&document.querySelector('#loading').classList.contains('hidden'),null,{timeout:150000});
 const result=await page.evaluate(()=>{
  const w=window.__skyisles.world,p=w.player,step=p.update.bind(p);p.update=()=>{};w.renderer.render=()=>{};p.orbit.yaw=0;let t=0;const results=[];
  const tick=(x=0,z=0)=>step(1/60,{x,z,jumpPressed:false,jumpHeld:false},t+=1/60);
  for(const[name,x,z,dx,dz]of[['north',0,-10.1,0,-1],['east',9.3,-7.8,1,0],['west',-9.3,-8,-1,0]]){
   p.teleport(x,.1,z);for(let i=0;i<60;i++)tick();if(!p.move.grounded)throw Error('bad starting floor '+name);
   for(let i=0;i<180;i++){tick(dx,dz);if(!p.move.grounded||p.respawnCount)throw Error('ordinary edge fall '+name);}
   results.push({edge:name,position:p.pos.toArray(),grounded:p.move.grounded});
  }
  return{results,respawns:p.respawnCount,description:'Normal walk only. Does not prove deliberate jump/glide containment.'};
 });
 expect(result.results[0].position[2]).toBeGreaterThan(-11);expect(result.results[1].position[0]).toBeLessThan(10);expect(result.results[2].position[0]).toBeGreaterThan(-10);expect(result.respawns).toBe(0);
 fs.writeFileSync(`docs/previews/transport-elevated-station-v9-game-integration/${isMobile?'mobile':'desktop'}-plinth-guards.json`,JSON.stringify(result,null,2)+'\n');
});
