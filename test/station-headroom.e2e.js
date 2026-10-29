import{test,expect}from'@playwright/test';
test('imported station lintel and canopy stop real Player double jumps; open-air jump stays unchanged',async({page})=>{
 test.setTimeout(240000);await page.goto('/');await page.waitForFunction(()=>window.__skyisles&&document.querySelector('#loading').classList.contains('hidden'),null,{timeout:150000});await page.evaluate(()=>{window.__skyisles.world.renderer.render=()=>{};});await page.locator('#title-screen .tap').click();if(await page.locator('#touch-help').isVisible())await page.locator('#help-close').click();
 const result=await page.evaluate(()=>{
  const w=window.__skyisles.world,p=w.player,step=p.update.bind(p);p.update=()=>{};p.orbit.yaw=0;let time=0;
  const tick=(jumpPressed=false)=>step(1/60,{x:0,z:0,jumpHeld:jumpPressed,jumpPressed},time+=1/60),records=[];
  for(const[name,x,z]of[['front-eave',0,-2.6],['rear-deck',0,-6.5],['open-air',0,3.5]]){
   p.teleport(x,.3,z);for(let i=0;i<80;i++)tick();if(!p.move.grounded)throw Error('not grounded');const floor=p.pos.y;
   const ray=new p.ray.constructor(p.pos.clone().add(p.pos.clone().set(0,1.6,0)),p.pos.clone().set(0,1,0),0,4),ceiling=ray.intersectObjects(w.transport.station.ceilings,false).find(h=>h.face.normal.y<-.2)?.point.y;
   let maxFoot=floor;for(let i=0;i<150;i++){tick(i===0||i===2);maxFoot=Math.max(maxFoot,p.pos.y);if(ceiling!==undefined&&p.pos.y+1.6>ceiling+.001)throw Error(`${name} head through actual model: ${p.pos.y+1.6}>${ceiling}`);}
   records.push({name,floor,ceiling,maxFoot});
  }
  // Compare identical open-air inputs with the optional constraint disabled;
  // do not assume a jump height different from the existing game's physics.
  const constraint=p.ceilingConstraint;p.ceilingConstraint=null;p.teleport(0,.3,3.5);for(let i=0;i<80;i++)tick();let baseline=p.pos.y;for(let i=0;i<150;i++){tick(i===0||i===2);baseline=Math.max(baseline,p.pos.y);}p.ceilingConstraint=constraint;
  return{records,baseline,respawns:p.respawnCount};
 });
 expect(result.respawns).toBe(0);for(const r of result.records.slice(0,2)){expect(r.ceiling).toBeGreaterThan(1.8);expect(r.maxFoot).toBeGreaterThanOrEqual(r.floor);expect(r.maxFoot+1.6).toBeLessThan(r.ceiling+.001);}expect(result.records[2].maxFoot).toBeGreaterThan(1);expect(result.records[2].maxFoot).toBeCloseTo(result.baseline,8);console.log(JSON.stringify(result));
});
