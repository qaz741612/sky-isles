// Shared, renderer-independent walkway plan and swept horizontal guard collisions.
export const WALKWAY = { width: 3.6, maxGrade: 0.16, railHeight: 1.3, railThickness: 0.16, playerRadius: 0.33 };
export const WALKWAY_LINKS = [
  ['home', 'meadow', 1], ['meadow', 'windmill', -1],
  ['windmill', 'temple', 1], ['temple', 'lookout', -1],
  ['home', 'tree', -1], ['tree', 'koi', -1], ['koi', 'crystal', 1]
];
const point = (x, y, z) => ({ x, y, z });
const dist = (a, b) => Math.hypot(b.x-a.x, b.z-a.z);
const shift = (p, x, z, amount, y = p.y) => point(p.x+x*amount,y,p.z+z*amount);

export function planWalkways(islands) {
  const byName = new Map(islands.map(i => [i.name,i]));
  return WALKWAY_LINKS.map(([from,to,side]) => {
    const a=byName.get(from), b=byName.get(to);
    if (!a || !b) throw new Error(`Missing walkway endpoint: ${from}/${to}`);
    const length=dist(a,b), ux=(b.x-a.x)/length, uz=(b.z-a.z)/length;
    const start=shift(a,ux,uz,a.r-1.8), end=shift(b,-ux,-uz,b.r-1.8);
    const p=shift(start,ux,uz,2), q=shift(end,-ux,-uz,2);
    const span=dist(p,q), rise=Math.abs(b.y-a.y);
    let points;
    if (rise/span <= WALKWAY.maxGrade) points=[start,p,q,end];
    else {
      // Two 90-degree turns, level landings and a level upper promenade.
      // Only the two lateral legs climb; their length includes landing allowance.
      const landing=2.4, h=rise/(2*WALKWAY.maxGrade)+2*landing;
      const nx=-uz*side, nz=ux*side, middle=(a.y+b.y)/2;
      const c=shift(p,nx,nz,h,middle), d=shift(q,nx,nz,h,middle);
      points=[start,p,shift(p,nx,nz,landing),shift(c,-nx,-nz,landing),c,shift(c,ux,uz,landing),
        shift(d,-ux,-uz,landing),d,shift(d,-nx,-nz,landing),shift(q,nx,nz,landing),q,end];
    }
    const half=WALKWAY.width/2;
    const edges=points.map((p,i) => {
      const before=points[Math.max(0,i-1)], after=points[Math.min(points.length-1,i+1)];
      const da=i ? dist(before,p) : dist(p,after), db=i===points.length-1 ? da : dist(p,after);
      const na=i ? {x:-(p.z-before.z)/da,z:(p.x-before.x)/da} : {x:-(after.z-p.z)/db,z:(after.x-p.x)/db};
      const nb=i===points.length-1 ? na : {x:-(after.z-p.z)/db,z:(after.x-p.x)/db};
      const sumX=na.x+nb.x, sumZ=na.z+nb.z, dot=sumX*nb.x+sumZ*nb.z;
      const dx=half*sumX/dot, dz=half*sumZ/dot;
      return {left:point(p.x+dx,p.y,p.z+dz),right:point(p.x-dx,p.y,p.z-dz)};
    });
    const barriers=[];
    for(let i=1;i<edges.length;i++) for(const edge of ['left','right']) {
      barriers.push({ a:edges[i-1][edge], b:edges[i][edge], height:WALKWAY.railHeight });
    }
    return { id:`${from}-${to}`,from,to,points,edges,barriers,width:WALKWAY.width,
      length:points.slice(1).reduce((sum,p,i)=>sum+dist(points[i],p),0) };
  });
}

export function nearestOnSegment(p, a, b) {
  const dx=b.x-a.x,dz=b.z-a.z;
  const t=Math.max(0,Math.min(1,((p.x-a.x)*dx+(p.z-a.z)*dz)/(dx*dx+dz*dz)));
  return {x:a.x+dx*t,z:a.z+dz*t,y:a.y+(b.y-a.y)*t,t};
}

export function moveWithGuards(position, dx, dz, barriers, radius=WALKWAY.playerRadius) {
  // Substeps prevent tunnelling even at the game's maximum dt and glide speed.
  const steps=Math.max(1,Math.ceil(Math.hypot(dx,dz)/0.1));
  const clearance=radius+WALKWAY.railThickness/2;
  let blocked=false;
  for(let step=0;step<steps;step++) {
    const previous={x:position.x,z:position.z};
    position.x+=dx/steps; position.z+=dz/steps;
    for(let iteration=0;iteration<4;iteration++) for(const wall of barriers) {
      const p=nearestOnSegment(position,wall.a,wall.b);
      if(position.y>p.y+wall.height || position.y+1.5<p.y-0.2) continue;
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
