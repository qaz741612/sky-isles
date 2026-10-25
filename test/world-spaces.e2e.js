import {test,expect} from '@playwright/test';
import fs from 'node:fs';
test('eight real places: accessible porches, water crossing, every exposed island edge and camera orbit',async({page,isMobile})=>{
 test.setTimeout(300000);await page.goto('/');await page.waitForFunction(()=>window.__skyisles);await page.locator('#title-screen .tap').click();if(await page.locator('#touch-help').isVisible())await page.locator('#help-close').click();
 const result=await page.evaluate(()=>{
 const w=window.__skyisles.world,p=w.player,step=p.update.bind(p);p.update=()=>{};p.orbit.yaw=0;let time=0;const records=[];
 const tick=(x=0,z=0)=>step(1/60,{x,z,jumpPressed:false,jumpHeld:false},time+=1/60);
 const land=(x,z)=>{p.teleport(x,.2,z);for(let i=0;i<60;i++)tick();if(!p.move.grounded)throw Error('cannot land');};
 const walk=(x,z)=>{let remaining=1000;while(Math.hypot(x-p.pos.x,z-p.pos.z)>.18&&remaining-->0){const dx=x-p.pos.x,dz=z-p.pos.z,d=Math.hypot(dx,dz);tick(dx/d,dz/d);if(!p.move.grounded)throw Error(`ground loss ${JSON.stringify(p.pos)}`);}if(remaining<=0)throw Error(`blocked target ${x},${z}; actual ${JSON.stringify(p.pos)}`);for(let i=0;i<30;i++)tick();};
 const paths={home:[[0,0],[-1.8,-2.5],[-1.8,-4.1],[-1.8,-2.5],[5,-2.5],[5,-5.7],[3.5,-5.7]],tree:[[0,0],[4,0],[4,-2.6],[4,-3.5]],temple:[[0,0],[-2.6,0],[-2.6,-1.2],[-2.6,-2.4]],koi:[[0,0],[2,1.5],[3.1,2.4],[4.9,3.2],[4.9,2]],meadow:[[0,0],[2,0],[2,4],[3.3,4]],windmill:[[0,0],[-3.3,0],[-3.3,-1.5],[-3.3,-2.8],[-3.3,-3.3]],crystal:[[0,0],[2,0],[2,1],[4.5,1],[6.6,1],[4.5,1]],lookout:[[0,0],[1.9,0],[1.9,-2.4],[1.9,-3.8]]};
 const obstacles=[...w.props.cameraObstacles,...w.transport.cameraObstacles],ray=new p.ray.constructor();
 for(const island of w.islands.islands){land(island.pos.x,island.pos.z+3.5);for(const[x,z]of paths[island.name])walk(island.pos.x+x,island.pos.z+z);const ending=p.pos.toArray();let edges=0,orbits=0;
  for(const yaw of[0,.8,1.6,2.4,3.2,4,4.8,5.6]){p.orbit.yaw=yaw;tick();const target=p._camTarget.clone(),camera=p._camPos.clone();p.cameraConstraint(target,camera);ray.set(target,camera.clone().sub(target).normalize());ray.far=target.distanceTo(camera)-.03;if(ray.intersectObjects(obstacles,false).length)throw Error(`camera inside solid ${island.name}`);orbits++;}p.orbit.yaw=0;
  for(const wall of w.bridges.barriers.filter(wall=>wall.island===island.name)){const mx=(wall.a.x+wall.b.x)/2-island.pos.x,mz=(wall.a.z+wall.b.z)/2-island.pos.z,len=Math.hypot(mx,mz);land(island.pos.x+mx*(len-.9)/len,island.pos.z+mz*(len-.9)/len);for(let i=0;i<65;i++){tick(mx/len,mz/len);if(!p.move.grounded)throw Error(`edge leak ${island.name}`);}edges++;}
  records.push({island:island.name,route:paths[island.name],end:ending,edgeProbes:edges,orbitProbes:orbits});
 }
 if(p.respawnCount)throw Error('unexpected respawn');return{records,respawns:p.respawnCount,cameraIndex:p.cameraConstraint.stats,description:'Accelerated integration audit using the actual Player, not a normal-operation video.'};
 });
 expect(result.records).toHaveLength(8);expect(result.respawns).toBe(0);const folder='docs/previews/eight-islands-world-redesign-v1';fs.mkdirSync(folder,{recursive:true});fs.writeFileSync(`${folder}/spaces-${isMobile?'mobile':'desktop'}.json`,JSON.stringify(result,null,2));
});
