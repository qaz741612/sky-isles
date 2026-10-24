import fs from 'node:fs';
import polygon from 'polygon-clipping';
const out='docs/design/yuan-size-comparison-v1';
const read=p=>JSON.parse(fs.readFileSync(p));
const area=multi=>multi.reduce((sum,poly)=>sum+poly.reduce((s,ring,i)=>{let a=0;for(let j=1;j<ring.length;j++)a+=ring[j-1][0]*ring[j][1]-ring[j][0]*ring[j-1][1];return s+(i?-1:1)*Math.abs(a/2);},0),0);
const disk=n=>[Array.from({length:29},(_,i)=>[n.x+Math.sin(i/28*Math.PI*2)*n.r,n.z+Math.cos(i/28*Math.PI*2)*n.r])];
function strip(p){const half=p.width/2;const edges=p.points.map((v,i)=>{const a=p.points[Math.max(0,i-1)],b=p.points[Math.min(p.points.length-1,i+1)],d=Math.hypot(b.x-a.x,b.z-a.z);return [[v.x-(b.z-a.z)/d*half,v.z+(b.x-a.x)/d*half],[v.x+(b.z-a.z)/d*half,v.z-(b.x-a.x)/d*half]];});const ring=[...edges.map(e=>e[0]),...edges.toReversed().map(e=>e[1])];ring.push(ring[0]);return [ring];}
function near(p,a,b){const dx=b.x-a.x,dz=b.z-a.z,t=Math.max(0,Math.min(1,((p.x-a.x)*dx+(p.z-a.z)*dz)/(dx*dx+dz*dz)));return Math.hypot(p.x-a.x-t*dx,p.z-a.z-t*dz);}
function stats(layout,surface){
 const nodes=layout.nodes.filter(n=>n.island),pairs=[];
 for(let i=0;i<nodes.length;i++)for(const b of nodes.slice(i+1)){const a=nodes[i],distance=Math.hypot(a.x-b.x,a.z-b.z);pairs.push({from:a.island,to:b.island,centerDistance:distance,edgeGap:distance-a.r-b.r});}
 const shortest={};for(const a of nodes){const d=Object.fromEntries(layout.nodes.map(n=>[n.id,Infinity]));d[a.id]=0;for(let i=0;i<layout.nodes.length;i++)for(const e of layout.paths){d[e.to]=Math.min(d[e.to],d[e.from]+e.length);d[e.from]=Math.min(d[e.from],d[e.to]+e.length);}shortest[a.island]=Object.fromEntries(nodes.map(n=>[n.island,d[n.id]]));}
 const overlaps=[],foreign=[],intersections=[];let roadIslandGap=Infinity,nonSharedGap=Infinity;
 const shapes=layout.paths.map(strip);
 for(let i=0;i<layout.paths.length;i++){
 const a=layout.paths[i];
 for(let j=i+1;j<layout.paths.length;j++){
  const b=layout.paths[j],shared=[a.from,a.to].filter(v=>v===b.from||v===b.to),overlap=area(polygon.intersection(shapes[i],shapes[j]));
  if(shared.length){if(overlap>1e-6)intersections.push({edges:[a.id,b.id],sharedNodes:shared,overlapArea:overlap});}
  else {
   if(overlap>1e-6)overlaps.push({edges:[a.id,b.id],overlapArea:overlap});
   for(let ai=1;ai<a.points.length;ai++)for(let bi=1;bi<b.points.length;bi++){
    const p=a.points[ai-1],q=a.points[ai],r=b.points[bi-1],s=b.points[bi];
    nonSharedGap=Math.min(nonSharedGap,near(p,r,s)-layout.width,near(q,r,s)-layout.width,near(r,p,q)-layout.width,near(s,p,q)-layout.width);
   }
  }
 }
 for(const n of nodes){if([a.from,a.to].includes(n.id))continue;
  const overlap=area(polygon.intersection(shapes[i],disk(n)));if(overlap>1e-6)foreign.push({edge:a.id,island:n.island,area:overlap});
  for(let j=1;j<a.points.length;j++)roadIslandGap=Math.min(roadIslandGap,near(n,a.points[j-1],a.points[j])-n.r-layout.width/2);
 }
 }
 const xs=surface.domain.flat(2).map(p=>p[0]),zs=surface.domain.flat(2).map(p=>p[1]);
 return {totalLength:layout.paths.reduce((s,p)=>s+p.length,0),shortest,islandPairs:pairs,minIslandEdgeGap:Math.min(...pairs.map(p=>p.edgeGap)),width:Math.max(...xs)-Math.min(...xs),height:Math.max(...zs)-Math.min(...zs),walkwayWidth:layout.width,unionComponents:surface.domain.length,holes:surface.domain.reduce((s,p)=>s+p.length-1,0),walkableArea:area(surface.domain),guardSegments:surface.barriers.length,collisionTriangles:surface.indices.length/3,nonSharedRoadOverlaps:overlaps,foreignIslandOverlaps:foreign,minNonEndpointRoadToIslandGap:roadIslandGap,minNonSharedRoadBoundaryGap:nonSharedGap,junctionOverlaps:intersections};
}
const report={referenceCommit:'860cf7a57a6d65771bbb445ea04493c219047a56',notes:'All distances use the PR #4 compiled centerline network as baseline; new XZ factors applied once to current plan coordinates, not to models.',baseline:stats(read('src/data/yuan-layout.json'),read('src/data/yuan-surface.json'))};
for(const id of ['a','b'])report[id]={relativeScale:id==='a'?.85:.75,...stats(read(`${out}/${id}/yuan-layout.json`),read(`${out}/${id}/yuan-surface.json`))};
fs.writeFileSync(`${out}/comparison.json`,JSON.stringify(report,null,2));
for(const id of ['baseline','a','b']){const {totalLength,minIslandEdgeGap,width,height,holes,nonSharedRoadOverlaps,foreignIslandOverlaps,minNonEndpointRoadToIslandGap}=report[id];console.log(id,{totalLength,minIslandEdgeGap,width,height,holes,nonSharedRoadOverlaps,foreignIslandOverlaps,minNonEndpointRoadToIslandGap});}
