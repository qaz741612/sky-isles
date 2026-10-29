// MIT. Build-time only. Native polygon-clipping dependency; nothing Boolean in the browser.
import polygon from 'polygon-clipping';
export const snap=p=>JSON.parse(JSON.stringify(p,(_k,v)=>typeof v==='number'?Math.round(v*1e5)/1e5:v));
const area=r=>Math.abs(r.reduce((s,a,i)=>{const b=r[(i+1)%r.length];return s+a[0]*b[1]-b[0]*a[1];},0))/2;
const clean=d=>d.filter(p=>area(p[0])>.003);
export function contains(domain,x,z){return domain.some(rings=>{const inRing=r=>{let yes=false;for(let i=0,j=r.length-1;i<r.length;j=i++){const a=r[i],b=r[j];if((a[1]>z)!==(b[1]>z)&&x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0])yes=!yes;}return yes;};return inRing(rings[0])&&!rings.slice(1).some(inRing);});}
const distance=(x,z,a,b)=>{const dx=b[0]-a[0],dz=b[1]-a[1],t=Math.max(0,Math.min(1,((x-a[0])*dx+(z-a[1])*dz)/(dx*dx+dz*dz||1)));return Math.hypot(x-a[0]-dx*t,z-a[1]-dz*t);};
export function compileLandscape({paths,nodes,coreDomain,islePolys,footprint,config}){
 const zoneFor=id=>config.zones.find(z=>z.routes.includes(id)),active=id=>config.activeZones.includes(zoneFor(id).id),islands=nodes.filter(n=>n.island);
 const isleDistance=(x,z)=>Math.min(...islands.map(n=>{if(!footprint(n))return Infinity;const ring=footprint(n)[0];if(contains([[ring]],x,z))return -1;return Math.min(...ring.slice(1).map((p,i)=>distance(x,z,ring[i],p)));}));
 function sample(path,t){const s=path.length*t;let i=path.points.findIndex(p=>p.s>=s);if(i<1)i=1;const a=path.points[i-1],b=path.points[i],f=Math.max(0,Math.min(1,(s-a.s)/(b.s-a.s||1))),d=Math.hypot(b.x-a.x,b.z-a.z);return{x:a.x+(b.x-a.x)*f,z:a.z+(b.z-a.z)*f,tx:(b.x-a.x)/d,tz:(b.z-a.z)/d,nx:-(b.z-a.z)/d,nz:(b.x-a.x)/d};}
 const weight=p=>Math.max(0,Math.min(1,(isleDistance(p.x,p.z)-1)/3));
 function band(path,a,b,points=path.points){const sides=points.map((p,i)=>{const v=sample(path,p.s/path.length),w=weight(p);return[[p.x+v.nx*a(w),p.z+v.nz*a(w)],[p.x+v.nx*b(w),p.z+v.nz*b(w)]];});const ring=[...sides.map(p=>p[0]),...sides.toReversed().map(p=>p[1])];return snap([[...ring,ring[0]]]);}
 const protectedRoads=paths.map(p=>band(p,()=>-2.55,()=>2.55));
 const protectedDomain=polygon.union(coreDomain,...protectedRoads);
 const additions=[],zones=config.zones.map(z=>({...z,beds:[],shoulders:[],finishes:[],islandFinishes:[],platforms:[],foliage:[]})),routes=[];
 const circleDomain=polygon.union(...islePolys);
 for(const path of paths){const z=zoneFor(path.id),out=zones.find(v=>v.id===z.id),inside=path.points.every(p=>contains(circleDomain,p.x,p.z));routes.push({id:path.id,zone:z.id,length:path.length,mode:inside?'island-walk':path.id==='S09'?'junction-connector':'landscaped-bridge',active:active(path.id)});if(!active(path.id))continue;
  // All widening tapers away before the unchanged GLB plinth mouths.
  const wider=band(path,w=>-2.4-z.shoulder*w,w=>2.4+z.shoulder*w);additions.push(wider);
  const shoulder=clean(polygon.difference(wider,coreDomain));out.shoulders.push(...shoulder);
  if(!inside){
   for(const side of[-1,1]){
    let run=[];const flush=()=>{if(run.length>2){const region=clean(polygon.difference(band(path,w=>side*(2.56+.06*w),w=>side*(2.4+(z.shoulder-.12)*w),run),protectedDomain));out.beds.push(...region);}run=[];};
    for(const p of path.points){if(weight(p)>.82)run.push(p);else flush();}flush();
   }
  }
  // A flat, clipped stone inlay marks even internal S12/S17; no fictitious bridge.
  if(inside)out.islandFinishes.push(...clean(polygon.intersection(band(path,()=>-1.5,()=>1.5),circleDomain)));
  const finish=clean(polygon.difference(band(path,()=>-2.30,()=>2.30),circleDomain));out.finishes.push(...finish);
 }
 const terminals=[];
 for(const id of['S20','S22']){if(!active(id))continue;const path=paths.find(p=>p.id===id),q=sample(path,1),zone=zoneFor(id),circle=r=>[Array.from({length:33},(_,i)=>[q.x+Math.cos(i/32*Math.PI*2)*r,q.z+Math.sin(i/32*Math.PI*2)*r])];additions.push(snap(circle(3.3)));
  const outer=[],inner=[];for(let i=0;i<=20;i++){const a=-Math.PI/2+i/20*Math.PI;outer.push([q.x+(q.tx*Math.cos(a)+q.nx*Math.sin(a))*3.15,q.z+(q.tz*Math.cos(a)+q.nz*Math.sin(a))*3.15]);inner.push([q.x+(q.tx*Math.cos(a)+q.nx*Math.sin(a))*2.64,q.z+(q.tz*Math.cos(a)+q.nz*Math.sin(a))*2.64]);}
  const ring=[...outer,...inner.reverse(),outer[0]],out=zones.find(z=>z.id===zone.id);out.beds.push(...clean(polygon.difference(snap([ring]),protectedDomain)));out.shoulders.push(...clean(polygon.difference(snap(circle(3.3)),coreDomain)));terminals.push({route:id,position:[q.x,0,q.z],tangent:[q.tx,q.tz],normal:[q.nx,q.nz]});
 }
 const platforms=[];
 for(const p of config.platforms){if(!active(p.route))continue;const path=paths.find(v=>v.id===p.route),q=sample(path,p.t),z=zoneFor(p.route);if(isleDistance(q.x,q.z)<4)continue;
  const ring=Array.from({length:25},(_,i)=>{const a=i/24*Math.PI*2,along=Math.cos(a)*2.75,out=p.side*(3.65+Math.sin(a)*1.65);return[q.x+q.tx*along+q.nx*out,q.z+q.tz*along+q.nz*out];});
  const domain=snap([ring]);additions.push(domain);const item={...p,zone:z.id,position:[q.x+q.nx*p.side*4.25,0,q.z+q.nz*p.side*4.25],tangent:[q.tx,q.tz],normal:[q.nx*p.side,q.nz*p.side],domain};platforms.push(item);zones.find(v=>v.id===z.id).platforms.push(item);
 }
 // Shared bay entrances replace the bed, never a low wall across the way in.
 for(const z of zones)if(z.beds.length&&platforms.length)z.beds=clean(polygon.difference(z.beds,...platforms.map(p=>p.domain)));
 let domain=coreDomain;for(const add of additions)domain=polygon.union(domain,add);domain=clean(domain);
 let ownedBeds=[];for(const z of zones){if(z.shoulders.length)z.shoulders=clean(polygon.union(...z.shoulders.map(r=>[r])));if(z.beds.length){z.beds=clean(polygon.difference(polygon.union(...z.beds.map(r=>[r])),ownedBeds));ownedBeds=polygon.union(ownedBeds,z.beds);}}
 const safeFromRoad=(x,z,r=.18)=>paths.every(p=>p.points.every((a,i)=>i===0||distance(x,z,[p.points[i-1].x,p.points[i-1].z],[a.x,a.z])>2.4+r));
 const guides=[];for(const p of paths.filter(p=>active(p.id)&&zoneFor(p.id).id===3))for(const t of[.35,.65]){const q=sample(p,t);if(isleDistance(q.x,q.z)>.5)guides.push({route:p.id,position:[q.x,q.z],tangent:[q.tx,q.tz]});}
 const lamps=[],rejected=[];
 for(const l of config.lamps){if(!active(l.route))continue;const p=paths.find(p=>p.id===l.route),q=sample(p,l.t),offset=l.type==='seven'?3.02:2.9,x=q.x+q.nx*offset*l.side,z=q.z+q.nz*offset*l.side;
  if(!contains(domain,x,z)||isleDistance(x,z)<.5||!safeFromRoad(x,z,.12)){rejected.push({...l,reason:'planned anchor fails floor/island/4.8-corridor clearance; omitted, not auto-relocated'});continue;}
  lamps.push({...l,zone:zoneFor(l.route).id,position:[x,0,z],yaw:Math.atan2(-q.nx*l.side,-q.nz*l.side)-Math.PI/2});
 }
 if(lamps.length>config.maxLampCount)throw Error('Lamp budget exceeded');
 for(const p of paths){if(!active(p.id))continue;const out=zones.find(z=>z.id===zoneFor(p.id).id);for(let s=1.8;s<p.length-1.5;s+=1.8){const q=sample(p,s/p.length);for(const side of[-1,1]){const x=q.x+q.nx*2.96*side,z=q.z+q.nz*2.96*side;if(contains(out.beds,x,z)&&safeFromRoad(x,z,.21)&&[-1,1].every(a=>[-1,1].every(b=>safeFromRoad(x+q.tx*a*1.05+q.nx*b*.20,z+q.tz*a*1.05+q.nz*b*.20,.025))))out.foliage.push({position:[x,.39,z],yaw:Math.atan2(q.tx,q.tz),flower:Math.round(s/1.8)%3===0});}}}
 for(const t of terminals){const out=zones.find(z=>z.id===5),[x,,z]=t.position,[tx,tz]=t.tangent,[nx,nz]=t.normal;for(let i=0;i<=10;i++){const a=-Math.PI/2+i/10*Math.PI,px=x+(tx*Math.cos(a)+nx*Math.sin(a))*2.94,pz=z+(tz*Math.cos(a)+nz*Math.sin(a))*2.94;if(contains(out.beds,px,pz))out.foliage.push({position:[px,.39,pz],yaw:Math.atan2(-tx*Math.sin(a)+nx*Math.cos(a),-tz*Math.sin(a)+nz*Math.cos(a)),alongScale:.65,flower:i%2===0});}}
 return{domain,data:{revision:config.revision,activeZones:config.activeZones,safeWidth:4.8,routes,zones,platforms,terminals,guides,lamps,rejectedLamps:rejected,coreDomain,stats:{lampCount:lamps.length,sevenLampCount:lamps.filter(l=>l.type==='seven').length,lowLightCount:lamps.filter(l=>l.type!=='seven').length,platformCount:platforms.length,foliageInstances:zones.reduce((n,z)=>n+z.foliage.length,0)}}};
}
