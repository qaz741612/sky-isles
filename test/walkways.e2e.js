import { test, expect } from './helpers/software-qa.js';
import { walkTour } from './helpers/walk-tour.js';

async function enter(page) {
  test.setTimeout(360000);
  await page.goto('/');await page.waitForFunction(()=>window.__skyisles&&document.querySelector('#loading').classList.contains('hidden'),null,{timeout:150000});
  // Geometry/input regression only: the full rendered scene is captured and
  // benchmarked separately. Keep real rAF, input, raycasts and physics active.
  await page.evaluate(()=>{window.__skyisles.world.renderer.render=()=>{};});
  await page.locator('#title-screen .tap').click({force:true});
  if(await page.locator('#touch-help').isVisible())await page.locator('#help-close').click();
  await page.evaluate(()=>{
    const w=window.__skyisles.world;
    w.tourStep=w.player.update.bind(w.player);
    w.player.update=()=>{}; // Freeze only background physics; explicit steps use the real controller.
    for(let i=0;i<60;i++)w.tourStep(1/60,{x:0,z:0,jumpPressed:false,jumpHeld:false},i/60);
  });
}

test('walk every island without jumping through keyboard or a single joystick pointer', async ({page,isMobile})=>{
  await enter(page);
  const plans=await page.evaluate(()=>(window.__skyisles.world.bridges.walkPlans??window.__skyisles.world.bridges.plans).map(({id,from,to,points})=>({id,from,to,points})));
  const route=walkTour(plans);
  let session=null;
  if(isMobile) {
    await page.evaluate(()=>document.getElementById('joystick').addEventListener('pointerdown',e=>{window.tourPointerId=e.pointerId;},{once:true}));
    const box=await page.locator('#joystick').boundingBox();
    session=await page.context().newCDPSession(page);
    await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:box.x+box.width/2,y:box.y+box.height/2,id:1}]});
  } else await page.keyboard.down('KeyW');
  // Native initial input establishes capture/focus. Subsequent same-pointer moves
  // are DOM events in one task, driving the real UI and Player at fixed dt.
  // This is an accelerated integration test, not a real-time human traversal.
  const result=await page.evaluate(({route,mobile})=>{
    const w=window.__skyisles.world,p=w.player,stick=document.getElementById('joystick');
    const rect=stick.getBoundingClientRect(),cx=rect.left+rect.width/2,cy=rect.top+rect.height/2;
    const visited=new Set(['F']),yaw=p.orbit.yaw;let ticks=0,forcedFall=false;
    const pointer=(x,z)=>stick.dispatchEvent(new PointerEvent('pointermove',{pointerId:window.tourPointerId,pointerType:'touch',clientX:cx+x*42,clientY:cy+z*42,bubbles:true}));
    const tick=()=>{
      const input=w.ui.poll(p.orbit);
      if(input.jumpHeld||input.jumpPressed)throw new Error('tour must not jump');
      w.tourStep(1/60,input,++ticks/60);
      if(!forcedFall && p.respawnCount)throw new Error('unexpected fall/respawn');
    };
    for(const leg of route) {
      for(const target of leg.points) {
        let remaining=1800;
        while(Math.hypot(target.x-p.pos.x,target.z-p.pos.z)>0.24 && remaining-->0) {
          const dx=target.x-p.pos.x,dz=target.z-p.pos.z,len=Math.hypot(dx,dz);
          if(mobile)pointer((dx*Math.cos(yaw)-dz*Math.sin(yaw))/len,(dx*Math.sin(yaw)+dz*Math.cos(yaw))/len);
          else {p.orbit.yaw=Math.atan2(-dx,-dz);window.dispatchEvent(new KeyboardEvent('keydown',{code:'KeyW',bubbles:true}));}
          tick();
          if(p.pos.y<target.y-4)throw new Error(`fell below ${leg.to}: target=${JSON.stringify(target)} pos=${JSON.stringify(p.pos)} input=${JSON.stringify(w.ui.input)} pointer=${window.tourPointerId}`);
        }
        if(remaining<=0)throw new Error(`stuck at ${leg.to}: ${JSON.stringify(target)} / ${JSON.stringify(p.pos)}`);
        if(mobile)pointer(0,0);else window.dispatchEvent(new KeyboardEvent('keyup',{code:'KeyW',bubbles:true}));
        for(let i=0;i<40;i++)tick();
      }
      visited.add(leg.to);
    }
    const before=p.pos.clone();for(let i=0;i<120;i++)tick();
    const stopped={speed:Math.hypot(p.move.vx,p.move.vz),drift:before.distanceTo(p.pos),respawns:p.respawnCount,checkpoint:p.lastGrounded.toArray()};
    const endpoint=p.pos.toArray();forcedFall=true;p.teleport(100,-50,100);tick();
    return {visited:[...visited],ticks,stopped,endpoint,returned:p.pos.toArray(),yawUnchanged:!mobile||p.orbit.yaw===yaw};
  },{route,mobile:isMobile});
  if(session){await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await session.detach();}
  else await page.keyboard.up('KeyW');
  expect(result.visited).toHaveLength(21);expect(result.stopped.speed).toBe(0);expect(result.stopped.drift).toBeLessThan(0.5);
  expect(result.stopped.respawns).toBe(0);expect(result.yawUnchanged).toBe(true);
  expect(Math.hypot(result.returned[0]-result.stopped.checkpoint[0],result.returned[2]-result.stopped.checkpoint[2])).toBeLessThan(0.1);
  expect(result.ticks).toBeGreaterThan(10000);
  console.log(JSON.stringify({device:isMobile?'single-pointer joystick':'keyboard',...result}));
});

test('guards block sideways movement on the live mesh; stepping on a mushroom never launches a walker',async({page})=>{
  await enter(page);
  const result=await page.evaluate(()=>{
    const w=window.__skyisles.world,p=w.bridges.plans[0];
    // A closed long ramp has two parallel guard walls. The short entry landing
    // intentionally permits walking around its corner back onto the island.
    const i=8;
    const a=p.points[i],b=p.points[i+1],x=(a.x+b.x)/2,z=(a.z+b.z)/2,y=(a.y+b.y)/2;
    w.player.orbit.yaw=0;w.player.teleport(x,y+0.05,z);
    const d=Math.hypot(b.x-a.x,b.z-a.z),nx=-(b.z-a.z)/d,nz=(b.x-a.x)/d;
    for(let j=0;j<180;j++)w.tourStep(1/60,{x:nx,z:nz,jumpHeld:false,jumpPressed:false},j/60);
    const offset=(w.player.pos.x-x)*nx+(w.player.pos.z-z)*nz;
    const grounded=w.player.move.grounded;
    const pad=w.islands.jumpPads[0],pos=w.player.pos.clone();
    pad.group.getWorldPosition(pos);w.player.teleport(pos.x,pos.y+1.5,pos.z);
    let maxUp=0;
    for(let j=0;j<180;j++){w.tourStep(1/60,{x:0,z:0,jumpHeld:false,jumpPressed:false},j/60);maxUp=Math.max(maxUp,w.player.move.vy);}
    const maxOffset=2.4+(w.bridges.landscape?.plan.zones.find(z=>z.routes.includes(p.id))?.shoulder??0);return {offset,grounded,maxUp,maxOffset};
  });
  expect(result.grounded).toBe(true);expect(result.offset).toBeLessThan(result.maxOffset);expect(result.offset).toBeGreaterThan(1.8);
  expect(result.maxUp).toBe(0);
});

test('native single-finger release and cancellation reset the stick and stop without camera turning',async({page,isMobile})=>{
  test.skip(!isMobile,'native touch input');
  await enter(page);
  const box=await page.locator('#joystick').boundingBox(),cx=box.x+box.width/2,cy=box.y+box.height/2;
  const session=await page.context().newCDPSession(page);
  for(const end of ['touchEnd','touchCancel']) {
    await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:cx,y:cy,id:1}]});
    await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:cx,y:cy-38,id:1}]});
    await page.evaluate(()=>{
      const w=window.__skyisles.world;
      for(let i=0;i<60;i++)w.tourStep(1/60,w.ui.poll(w.player.orbit),i/60);
    });
    await session.send('Input.dispatchTouchEvent',{type:end,touchPoints:[]});
    const result=await page.evaluate(()=>{
      const w=window.__skyisles.world,before=w.player.pos.clone(),yaw=w.player.orbit.yaw;
      for(let i=0;i<120;i++)w.tourStep(1/60,w.ui.poll(w.player.orbit),i/60);
      return {drift:before.distanceTo(w.player.pos),speed:Math.hypot(w.player.move.vx,w.player.move.vz),input:[w.ui.input.x,w.ui.input.z],yawStable:w.player.orbit.yaw===yaw};
    });
    expect(result.input).toEqual([0,0]);expect(result.speed).toBe(0);expect(result.drift).toBeLessThan(0.5);expect(result.yawStable).toBe(true);
  }
  await session.detach();
});
