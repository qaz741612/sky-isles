// Shared, renderer-independent walkway plan and swept horizontal guard collisions.
import layout from '../data/yuan-layout.json' with { type: 'json' };
export const WALKWAY = { width: layout.width, maxGrade: .10, railHeight: 1.3, railThickness: .16, playerRadius: .33 };
export const WALKWAY_LINKS = layout.paths.map(p=>[p.from,p.to]);
export function planWalkways() { return layout.paths; }

// Query only nearby outer boundary segments; collision and checkpoint use the same rails.
export function guardIndex(barriers) {
 const cells=new Map(),size=8;
 for(const wall of barriers)for(let x=Math.floor(Math.min(wall.a.x,wall.b.x)/size);x<=Math.floor(Math.max(wall.a.x,wall.b.x)/size);x++)for(let z=Math.floor(Math.min(wall.a.z,wall.b.z)/size);z<=Math.floor(Math.max(wall.a.z,wall.b.z)/size);z++){
 const key=`${x},${z}`;if(!cells.has(key))cells.set(key,[]);cells.get(key).push(wall);
 }
 return p=>{const result=new Set();for(let x=Math.floor((p.x-2)/size);x<=Math.floor((p.x+2)/size);x++)for(let z=Math.floor((p.z-2)/size);z<=Math.floor((p.z+2)/size);z++)for(const wall of cells.get(`${x},${z}`)||[])result.add(wall);return [...result];};
}

export function nearestOnSegment(p, a, b) {
  const dx=b.x-a.x,dz=b.z-a.z;
  const t=Math.max(0,Math.min(1,((p.x-a.x)*dx+(p.z-a.z)*dz)/(dx*dx+dz*dz)));
  return {x:a.x+dx*t,z:a.z+dz*t,y:a.y+(b.y-a.y)*t,t};
}

export function moveWithGuards(position, dx, dz, barriers, radius=WALKWAY.playerRadius) {
  // Substeps prevent tunnelling even at the game's maximum dt and glide speed.
  const steps=Math.max(1,Math.ceil(Math.hypot(dx,dz)/0.1));

  let blocked=false;
  for(let step=0;step<steps;step++) {
    const previous={x:position.x,z:position.z};
    position.x+=dx/steps; position.z+=dz/steps;
    for(let iteration=0;iteration<4;iteration++) for(const wall of barriers) {
      const clearance=radius+(wall.thickness??WALKWAY.railThickness)/2;
      const p=nearestOnSegment(position,wall.a,wall.b);
      if(position.y>p.y+wall.height || position.y+(wall.capsuleHeight??1.5)<p.y-(wall.capsuleHeight?0:.2)) continue;
      const ox=position.x-p.x,oz=position.z-p.z,d=Math.hypot(ox,oz);
      if(d>=clearance) continue;
      let nx=ox/(d||1),nz=oz/(d||1);
      const wx=wall.b.x-wall.a.x,wz=wall.b.z-wall.a.z,len=Math.hypot(wx,wz);
      // Choose the side occupied before the substep when very close to the wall.
      if(d<1e-7) {nx=-wz/len;nz=wx/len;if((previous.x-p.x)*nx+(previous.z-p.z)*nz<0){nx=-nx;nz=-nz;}}
      position.x=p.x+nx*(clearance+1e-5);position.z=p.z+nz*(clearance+1e-5);blocked=true;
    }
  }
  return blocked;
}

export function isSafeCheckpoint(position, hit, islands, barriers) {
  if(hit.userData.noCheckpoint)return false;
  if(hit.userData.island) {
    const island=islands.find(i=>i.name===hit.userData.island);
    return island && Math.hypot(position.x-island.x,position.z-island.z)<island.r-0.8;
  }
  if(!hit.userData.walkway) return false;
  return barriers.every(w=> {
    const p=nearestOnSegment(position,w.a,w.b);
    return Math.abs(position.y-p.y)>2 || Math.hypot(position.x-p.x,position.z-p.z)>0.7;
  });
}
