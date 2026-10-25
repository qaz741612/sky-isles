import {test,expect} from '@playwright/test';
async function enter(page){await page.goto('/');await page.waitForFunction(()=>window.__skyisles);await page.locator('#title-screen .tap').click();if(await page.locator('#touch-help').isVisible())await page.locator('#help-close').click();await page.waitForFunction(()=>window.__skyisles.world.player.move.grounded);}
async function settle(page,x,z){await page.evaluate(({x,z})=>{const w=window.__skyisles.world;w.player.teleport(x,.2,z);Object.assign(w.player.orbit,{yaw:0,pitch:.5,dist:7});},{x,z});await page.waitForFunction(()=>window.__skyisles.world.player.move.grounded);await page.evaluate(()=>{const w=window.__skyisles.world;w.camera.position.copy(w.player._camPos);w.camera.lookAt(w.player._camTarget);w.camera.updateMatrixWorld();});}

test('native scene information and five clues use the readable existing modal; close resumes exploration',async({page,isMobile})=>{
 test.setTimeout(240000);await enter(page);
 for(const size of isMobile?[{width:430,height:739},{width:932,height:430}]:[page.viewportSize()]){
 await page.setViewportSize(size);
 for(const kind of ['vision','mural']){
 const target=await page.evaluate(kind=>{const w=window.__skyisles.world;return kind==='vision'?{x:w.transport.plan.visionDisplay.position[0],z:-2.5}:{x:-5.5,z:2.5};},kind);
 await settle(page,target.x,target.z);
 if(kind==='mural'){await page.evaluate(()=>{const w=window.__skyisles.world;w.player.orbit.yaw=Math.PI;w.player.camera.position.set(-5.5,4,-4);});await page.waitForFunction(()=>{const w=window.__skyisles.world;return w.camera.position.distanceTo(w.player._camPos)<.03;});}
 const xy=await page.evaluate(kind=>{const w=window.__skyisles.world,h=w.transport.interactives.find(h=>h.userData.transportInfo===kind),p=h.position.clone().project(w.camera);return{x:(p.x+1)*innerWidth/2,y:(1-p.y)*innerHeight/2};},kind);
 if(isMobile)await page.touchscreen.tap(xy.x,xy.y);else await page.mouse.click(xy.x,xy.y);
 await expect(page.getByRole('dialog')).toBeVisible();
 await expect(page.locator('#policy-title')).toHaveText(kind==='vision'?'交通政策願景':'風鈴文化牆');
 const lines=page.locator('#policy-content li');await expect(lines).toHaveCount(kind==='vision'?4:5);
 if(kind==='vision')await expect(page.locator('#policy-content')).toContainText('非實際工程核定或完工資訊');else expect(await lines.allTextContents()).toEqual(['日','葉','月','浪','星']);
 await lines.last().scrollIntoViewIfNeeded();await expect(lines.last()).toBeVisible();
 const sizes=await lines.evaluateAll(nodes=>nodes.map(n=>parseFloat(window.getComputedStyle(n).fontSize)));expect(Math.min(...sizes)).toBeGreaterThanOrEqual(16);
 await page.locator('#policy-close').click();await expect(page.getByRole('dialog')).not.toBeVisible();
 }
 }
 if(isMobile){
 const r=await page.locator('#joystick').boundingBox(),x=r.x+r.width/2,y=r.y+r.height/2,session=await page.context().newCDPSession(page);
 await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y,id:1}]});await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:x+35,y,id:1}]});
 await expect.poll(()=>page.evaluate(()=>Math.abs(window.__skyisles.world.player.move.vx))).toBeGreaterThan(1);await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await session.detach();
 await expect.poll(()=>page.evaluate(()=>Math.hypot(window.__skyisles.world.player.move.vx,window.__skyisles.world.player.move.vz))).toBe(0);
 }else{await page.keyboard.down('ArrowRight');await expect.poll(()=>page.evaluate(()=>Math.abs(window.__skyisles.world.player.move.vx))).toBeGreaterThan(1);await page.keyboard.up('ArrowRight');}
});

test('default arrival sees actual train surfaces throughout motion; orbit checks record real occlusion',async({page,isMobile})=>{
 test.setTimeout(240000);await enter(page);
 const result=await page.evaluate(()=>{
  const w=window.__skyisles.world,p=w.player,step=p.update.bind(p);p.update=()=>{};
  for(let i=0;i<50;i++)step(1/60,{x:0,z:0,jumpHeld:false,jumpPressed:false},0);
  w.camera.position.copy(p._camPos);w.camera.lookAt(p._camTarget);w.camera.updateMatrixWorld();
  const objects=[...w.transport.pickMeshes,...w.islands.murals,...w.transport.train.children],trainSet=new Set(w.transport.train.children),ray=new w.player.ray.constructor(),point=w.player.pos.clone(),phases=[];
  for(let i=0;i<=24;i++){w.transport.update(i*Math.PI*2/(24*w.transport.plan.rail.speed));w.scene.updateMatrixWorld(true);let visible=0;
   for(const dx of [-1,-.64,-.3,.3,.64,1]){point.set(w.transport.train.position.x+dx,.9,-6.63);ray.set(w.camera.position,point.clone().sub(w.camera.position).normalize());const screen=point.clone().project(w.camera);if(Math.abs(screen.x)<.95&&Math.abs(screen.y)<.95&&trainSet.has(ray.intersectObjects(objects,false)[0]?.object))visible++;}
   phases.push(visible);
  }
  const rotations=[];
  for(const [x,z]of [[0,3.5],[-1.8,-2.5],[5,-5.8]]){
   p.teleport(x,.2,z);for(let i=0;i<50;i++)step(1/60,{x:0,z:0,jumpHeld:false,jumpPressed:false},0);
   for(const yaw of [0,.8,1.6,2.4,3.2,4,4.8,5.6]){p.orbit.yaw=yaw;step(1/60,{x:0,z:0,jumpHeld:false,jumpPressed:false},0);const target=p._camTarget.clone(),origin=p._camPos.clone();p.cameraConstraint?.(p._camTarget,origin);ray.set(origin,target.clone().sub(origin).normalize());ray.far=origin.distanceTo(target)-.15;rotations.push({x,z,yaw,blocked:ray.intersectObjects(w.transport.cameraObstacles,false).length>0});}
  }
  return{phases,rotations};
 });
 expect(Math.min(...result.phases)).toBeGreaterThan(0);
 expect(result.rotations.filter(r=>r.blocked)).toEqual([]);
 // Record obstructions honestly; covered recess / close zoom still need human review.
 console.log(JSON.stringify({device:isMobile?'mobile':'desktop',...result}));
});
