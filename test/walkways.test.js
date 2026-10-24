import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { ISLANDS } from '../src/world/islands.js';
import { buildBridges } from '../src/world/bridges.js';
import { Player } from '../src/sim/player.js';
import { WALKWAY, planWalkways, moveWithGuards, nearestOnSegment } from '../src/sim/walkways.js';
import { createMoveState, stepHorizontal } from '../src/sim/movement.js';

function fixture() {
  const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera();
  const colliders=[],islands=ISLANDS.map(d=> {
    const grass=new THREE.Mesh(new THREE.CylinderGeometry(d.r,d.r*0.9,1.1,28),new THREE.MeshBasicMaterial());
    grass.position.set(d.x,d.y-0.55,d.z);grass.userData.island=d.name;scene.add(grass);colliders.push(grass);
    return { name:d.name,r:d.r,pos:new THREE.Vector3(d.x,d.y,d.z) };
  });
  const bridges=buildBridges(scene,islands);
  const player=new Player(scene,camera,[...colliders,...bridges.colliders]);
  player.orbit.yaw=0;player.navigation={islands:ISLANDS,barriers:bridges.barriers};
  scene.updateMatrixWorld(true);
  return {scene,player,bridges};
}

export function tour(plans) {
  const result=[],visited=new Set(['home']);
  const dfs=(name) => {
    for(const p of plans) {
      const next=p.from===name?p.to:p.to===name?p.from:null;
      if(!next || visited.has(next)) continue;
      visited.add(next);
      const points=p.from===name?p.points:[...p.points].reverse();
      result.push({to:next,points});dfs(next);
      result.push({to:name,points:[...points].reverse()});
    }
  };
  dfs('home');return result;
}

test('eight islands share a seven-edge, wide, low-gradient network with overlapped entrances', () => {
  const plans=planWalkways(ISLANDS),seen=new Set(['home']);
  assert.equal(plans.length,7);assert.ok(WALKWAY.width>=3);
  for(let repeat=0;repeat<8;repeat++) for(const p of plans) if(seen.has(p.from)||seen.has(p.to)){seen.add(p.from);seen.add(p.to);}
  assert.equal(seen.size,8);
  for(const plan of plans) {
    for(let i=1;i<plan.points.length;i++) {
      const a=plan.points[i-1],b=plan.points[i];
      const grade=Math.abs(b.y-a.y)/Math.hypot(b.x-a.x,b.z-a.z);
      assert.ok(grade<=WALKWAY.maxGrade+1e-9,`${plan.id}: ${grade}`);
    }
    assert.equal(plan.barriers.length,(plan.points.length-1)*2);
    for(const [name,p] of [[plan.from,plan.points[0]],[plan.to,plan.points.at(-1)]]) {
      const d=ISLANDS.find(i=>i.name===name);
      assert.ok(Math.hypot(p.x-d.x,p.z-d.z)<d.r-1.5);
      assert.equal(p.y,d.y);
    }
  }
});

for(const dt of [1/60,0.05]) test(`actual Player and mesh colliders walk all islands and return without jumping at dt=${dt}`, () => {
  const {player,bridges}=fixture(),seen=new Set(['home']);let time=0;
  const advance=(x,z)=> {time+=dt;player.update(dt,{x,z,jumpPressed:false,jumpHeld:false},time);};
  for(let i=0;i<40;i++)advance(0,0);
  for(const leg of tour(bridges.plans)) {
    for(const target of leg.points) {
      let remaining=2000;
      while(Math.hypot(target.x-player.pos.x,target.z-player.pos.z)>0.22 && remaining-->0) {
        const dx=target.x-player.pos.x,dz=target.z-player.pos.z,len=Math.hypot(dx,dz);
        advance(dx/len,dz/len);
        assert.ok(player.move.grounded,`airborne on ${leg.to} at ${JSON.stringify(player.pos)}`);
      }
      assert.ok(remaining>0,`stuck reaching ${leg.to}: ${JSON.stringify(target)} from ${JSON.stringify(player.pos)}`);
      for(let i=0;i<30;i++)advance(0,0);
      assert.ok(Math.abs(player.pos.y-target.y)<0.15,`unexpected surface on ${leg.to}`);
    }
    seen.add(leg.to);
  }
  assert.equal(seen.size,8);
});

test('guards prevent high-speed horizontal crossing from either side, including endpoints', () => {
  const wall={a:{x:0,y:0,z:-5},b:{x:0,y:2,z:5},height:1.3};
  for(const sign of [-1,1]) {
    const p={x:sign*2,y:1,z:0};
    moveWithGuards(p,-sign*6,0,[wall]);
    assert.ok(p.x*sign>=WALKWAY.playerRadius+WALKWAY.railThickness/2-1e-4);
  }
  const {player,bridges}=fixture();
  const plan=bridges.plans[0],target=plan.points[2];
  player.teleport(target.x,target.y+0.1,target.z);
  for(let i=0;i<60;i++)player.update(1/60,{x:0,z:0,jumpPressed:false,jumpHeld:false},i/60);
  const checkpoint=player.lastGrounded.clone();
  assert.ok(checkpoint.distanceTo(new THREE.Vector3(target.x,target.y,target.z))<0.2);
  player.teleport(100,-50,100);
  player.update(1/60,{x:0,z:0,jumpPressed:false,jumpHeld:false},2);
  assert.ok(player.pos.distanceTo(checkpoint)<0.6);
  assert.ok(player.pos.distanceTo(new THREE.Vector3(0,0,3.5))>5);
  assert.ok(bridges.barriers.every(w=>Number.isFinite(nearestOnSegment(checkpoint,w.a,w.b).y)));
});

test('released stick decelerates to rest quickly, with a bounded stopping distance', () => {
  const m=createMoveState();m.vx=6.2;let distance=0;
  for(let i=0;i<60;i++){stepHorizontal(m,0,0,1/60);distance+=Math.hypot(m.vx,m.vz)/60;}
  assert.equal(m.vx,0);assert.equal(m.vz,0);assert.ok(distance<0.5);
});

test('mesh ground stays continuous while pushing both guards and right-angle landings', () => {
  const {player,bridges}=fixture();let time=0;
  for(const plan of bridges.plans) for(let i=1;i<plan.points.length-1;i++) for(const edge of ['left','right']) {
    const c=plan.points[i],e=plan.edges[i][edge];
    player.teleport(c.x,c.y+0.05,c.z);
    for(let j=0;j<30;j++){time+=1/60;player.update(1/60,{x:0,z:0,jumpHeld:false,jumpPressed:false},time);}
    const dx=e.x-c.x,dz=e.z-c.z,len=Math.hypot(dx,dz);
    for(let j=0;j<100;j++) {
      time+=1/60;player.update(1/60,{x:dx/len,z:dz/len,jumpHeld:false,jumpPressed:false},time);
      assert.ok(player.move.grounded,`guard/corner dropped player: ${plan.id}/${i}/${edge}`);
      for(const wall of bridges.barriers) {
        const q=nearestOnSegment(player.pos,wall.a,wall.b);
        if(player.pos.y>q.y+wall.height || player.pos.y+1.5<q.y-0.2)continue;
        assert.ok(Math.hypot(player.pos.x-q.x,player.pos.z-q.z)>=WALKWAY.playerRadius+WALKWAY.railThickness/2-1e-4,`guard penetration ${plan.id}/${i}/${edge}`);
      }
    }
  }
});

test('every rendered deck triangle is at most 16 percent grade, including all corner shoulders',()=>{
  const {bridges}=fixture();
  for(const mesh of bridges.colliders) {
    const p=mesh.geometry.attributes.position,index=mesh.geometry.index;
    for(let i=0;i<index.count;i+=3) {
      const a=new THREE.Vector3().fromBufferAttribute(p,index.getX(i));
      const b=new THREE.Vector3().fromBufferAttribute(p,index.getX(i+1));
      const c=new THREE.Vector3().fromBufferAttribute(p,index.getX(i+2));
      const n=b.sub(a).cross(c.sub(a));
      assert.ok(Math.abs(n.y)>1e-6,`${mesh.name} has a degenerate surface`);
      assert.ok(Math.hypot(n.x,n.z)/Math.abs(n.y)<=WALKWAY.maxGrade+1e-5,`${mesh.name} has a steep triangle`);
    }
  }
});
