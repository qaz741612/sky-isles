import {test,expect} from './helpers/software-qa.js';
import fs from 'node:fs';
test('eight current places: authored public circuits, accessible exterior guards and camera orbit',async({page,isMobile})=>{
 test.setTimeout(420000);await page.goto('/');await page.waitForFunction(()=>window.__skyisles);await page.locator('#title-screen .tap').click();if(await page.locator('#touch-help').isVisible())await page.locator('#help-close').click();
 const result=await page.evaluate(()=>{
 const w=window.__skyisles.world,p=w.player,step=p.update.bind(p);p.update=()=>{};p.orbit.yaw=0;let time=0;const records=[];
 const tick=(x=0,z=0)=>{p.cameraConstraint.setDelta?.(1/60);return step(1/60,{x,z,jumpPressed:false,jumpHeld:false},time+=1/60);};
 const land=(x,z)=>{p.teleport(x,.2,z);for(let i=0;i<60;i++)tick();if(!p.move.grounded)throw Error('cannot land');};
 const walk=(x,z)=>{let remaining=1000;while(Math.hypot(x-p.pos.x,z-p.pos.z)>.18&&remaining-->0){const dx=x-p.pos.x,dz=z-p.pos.z,d=Math.hypot(dx,dz);const yaw=p.orbit.yaw;tick((dx*Math.cos(yaw)-dz*Math.sin(yaw))/d,(dx*Math.sin(yaw)+dz*Math.cos(yaw))/d);if(p.pos.y<-.25)throw Error(`ground loss ${JSON.stringify(p.pos)}`);}if(remaining<=0)throw Error(`blocked target ${x},${z}; actual ${JSON.stringify(p.pos)}`);for(let i=0;i<30;i++)tick();};
 const paths={home:[[0,0],[0,-2.3],[-5,-1.8],[0,-1.8],[5.5,-1.4],[0,0]],tree:[[1.1,1.7],[1.1,3],[1.1,5.9],[-2.5,6],[1.1,5.9],[1.1,3],[1.1,2.2],[-2,2.8]],temple:[[0,0],[-2.6,0],[-2.6,-1.2],[-2.6,-2.4]],koi:[[0,0],[3,0],[4.9,-1.05],[3,0],[0,0],[0,4],[.5,6.95],[.5,8.35]],meadow:[[0,0],[2,0],[2,4],[3.3,4]],windmill:[[0,0],[-3.3,0],[-3.3,-1.5],[-3.3,-2.8],[-3.3,-3.3]],crystal:[[0,0],[6.1,-.7],[7.75,.6],[6.1,-.7],[0,0],[0,3]],lookout:[[0,0],[1.9,0],[1.9,-2.4],[1.9,-3.8]]};
 for(const place of Object.values(w.r21??{}))paths[place.config.name]=place.config.publicCircuit;
 const obstacles=[...w.props.cameraObstacles,...w.transport.cameraObstacles],ray=new p.ray.constructor();
 for(const island of w.islands.islands){land(island.pos.x+paths[island.name][0][0],island.pos.z+paths[island.name][0][1]);for(const[x,z]of paths[island.name])walk(island.pos.x+x,island.pos.z+z);const ending=p.pos.toArray();let edges=0,orbits=0;
  for(const yaw of[0,.8,1.6,2.4,3.2,4,4.8,5.6]){p.orbit.yaw=yaw;const local=Object.values(w.r21??{}).some(v=>v.config.name===island.name);for(let k=0;k<(local?35:1);k++)tick();const target=local?p.pos.clone().add(p.pos.clone().set(0,1.5,0)):p._camTarget.clone(),camera=local?w.camera.position.clone():p._camPos.clone();if(!local)p.cameraConstraint(target,camera);ray.set(target,camera.clone().sub(target).normalize());ray.far=target.distanceTo(camera)-.03;if(ray.intersectObjects(obstacles,false).length)throw Error(`camera inside solid ${island.name}`);orbits++;}p.orbit.yaw=0;
  const excluded=[],allEdges=w.bridges.barriers.filter(wall=>wall.island===island.name);
  // Every shared boundary receives swept-capsule unit coverage. The browser
  // samples 24 evenly distributed tessellation segments per island with the
  // real Player; route tests independently traverse every bridge both ways.
  const sampledEdges=allEdges.filter((_,i)=>Math.floor(i*24/allEdges.length)!==Math.floor((i-1)*24/allEdges.length));
  for(const wall of sampledEdges){
   const x=(wall.a.x+wall.b.x)/2,z=(wall.a.z+wall.b.z)/2,dx=wall.b.x-wall.a.x,dz=wall.b.z-wall.a.z,len=Math.hypot(dx,dz);
   if(len<.4){excluded.push({reason:'short junction tessellation',length:len});continue;}
   let nx=dz/len,nz=-dx/len;if((x-island.pos.x)*nx+(z-island.pos.z)*nz<0){nx=-nx;nz=-nz;}
   const sx=x-nx*.9,sz=z-nz*.9;ray.set(p.pos.clone().set(sx,1,sz),p.pos.clone().set(0,-1,0));ray.far=1.4;
   if(!ray.intersectObjects(p.colliders,false).length){excluded.push({reason:'no dry inward test start',x:sx,z:sz});continue;}
   land(sx,sz);if(Math.hypot(p.pos.x-sx,p.pos.z-sz)>.3){excluded.push({reason:'solid occupies inward test start',x:sx,z:sz});continue;}
   for(let i=0;i<65;i++){const yaw=p.orbit.yaw;tick(nx*Math.cos(yaw)-nz*Math.sin(yaw),nx*Math.sin(yaw)+nz*Math.cos(yaw));if(p.pos.y<-.25||p.respawnCount)throw Error(`edge leak ${island.name}`);}edges++;
  }
  records.push({island:island.name,route:paths[island.name],end:ending,edgeProbes:edges,availableBoundarySegments:allEdges.length,sampledBoundarySegments:sampledEdges.length,excludedEdgeStarts:excluded,orbitProbes:orbits});
 }
 if(p.respawnCount)throw Error('unexpected respawn');return{records,respawns:p.respawnCount,cameraIndex:p.cameraConstraint.stats,description:'Accelerated integration audit using the actual Player, not a normal-operation video.'};
 });
 expect(result.records).toHaveLength(8);expect(result.respawns).toBe(0);const folder=process.env.SKYISLES_QA_OUTPUT_DIR??'docs/previews/transport-station-glb-integration-v1';fs.mkdirSync(folder,{recursive:true});fs.writeFileSync(`${folder}/spaces-${isMobile?'mobile':'desktop'}.json`,JSON.stringify(result,null,2));
});
