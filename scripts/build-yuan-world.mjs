// Reproducible build-time polygon union; no Boolean library is sent to browsers.
import fs from 'node:fs';
import polygon from 'polygon-clipping';
import { ShapeUtils, Vector2 } from 'three';
const source=JSON.parse(fs.readFileSync('docs/design/yuan-masterplan-v1/yuan-layout.json'));
const plan=JSON.parse(fs.readFileSync('src/data/yuan-plan.json'));
const scale=plan.compressionXZ, half=plan.width/2;
const nodes=plan.nodes.map(n=>({...n}));
if(nodes.some(n=>n.y!==plan.heightDatum))throw new Error('This prototype uses a shared level datum; non-level roads require a new triangulation/grade review.');
const byId=new Map(nodes.map(n=>[n.id,n]));
const circle=(n,r=n.r,count=28)=>[Array.from({length:count+1},(_,i)=>[n.x+Math.sin(i/count*Math.PI*2)*r,n.z+Math.cos(i/count*Math.PI*2)*r])];
const paths=plan.edges.map(e=>{
 const cp=e.controlPointsXZ,a=byId.get(e.from),b=byId.get(e.to);
 const evaluate=t=> cp.length===2?cp[0].map((v,i)=>v+(cp[1][i]-v)*t):cp[0].map((v,i)=>(1-t)**3*v+3*(1-t)**2*t*cp[1][i]+3*(1-t)*t*t*cp[2][i]+t**3*cp[3][i]);
 const count=Math.ceil(source.edges.find(s=>s.id===e.id).length*scale/.9),points=Array.from({length:count+1},(_,i)=>{const p=evaluate(i/count);return{x:p[0],y:0,z:p[1],s:0};});
 for(let i=1;i<points.length;i++)points[i].s=points[i-1].s+Math.hypot(points[i].x-points[i-1].x,points[i].z-points[i-1].z);
 const length=points.at(-1).s;
 // Keep all overlapping branches level until they have separated. Island radii are NOT scaled.
 const flatA=Math.max(a.r+2,e.flatFrom),flatB=Math.max(b.r+2,e.flatTo);
 for(const p of points){const t=Math.max(0,Math.min(1,(p.s-flatA)/Math.max(.001,length-flatA-flatB)));p.y=a.y+(b.y-a.y)*t*t*(3-2*t);}
 const edges=points.map((p,i)=>{const a=points[Math.max(0,i-1)],b=points[Math.min(points.length-1,i+1)],d=Math.hypot(b.x-a.x,b.z-a.z);return{left:[p.x-(b.z-a.z)/d*half,p.z+(b.x-a.x)/d*half],right:[p.x+(b.z-a.z)/d*half,p.z-(b.x-a.x)/d*half]};});
 return {id:e.id,from:e.from,to:e.to,meaning:e.meaning,width:plan.width,points,length,outline:[...edges.map(e=>e.left),...edges.toReversed().map(e=>e.right)]};
});
const roads=paths.flatMap(p=>[[[...p.outline,p.outline[0]]],circle(p.points[0],half,16),circle(p.points.at(-1),half,16)]);
const footprint=n=>plan.islandFootprintsXZ?.[n.id]?[plan.islandFootprintsXZ[n.id]]:circle(n);
const islePolys=nodes.filter(n=>n.island).map(footprint);
const inFootprint=(x,z,n)=>{const ring=footprint(n)[0];let yes=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>z)!==(b[1]>z)&&x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0])yes=!yes;}return yes;};
const snap=p=>JSON.parse(JSON.stringify(p,(_k,v)=>typeof v==='number'?Math.round(v*1e5)/1e5:v));
const operands=snap([...roads,...nodes.filter(n=>n.r>0).map(footprint)]);
let union=operands[0];for(const operand of operands.slice(1))union=polygon.union(union,operand);
const decks=polygon.difference(union,polygon.union(...snap(islePolys)));
const roadOperands=snap(roads);let roadDomain=roadOperands[0];for(const part of roadOperands.slice(1))roadDomain=polygon.union(roadDomain,part);
const islandPaving=nodes.filter(n=>n.island).map(n=>({island:n.island,domain:polygon.intersection(roadDomain,snap(footprint(n)))}));
function height(){ return plan.heightDatum; }
const positions=[],indices=[];
for(const rings of decks){
 const clean=rings.map(r=>r.slice(0,-1));const contour=clean[0].map(p=>new Vector2(...p)),holes=clean.slice(1).map(r=>r.map(p=>new Vector2(...p))),triangles=ShapeUtils.triangulateShape(contour,holes),offset=positions.length/3;
 for(const [x,z] of clean.flat())positions.push(Math.fround(x),height(x,z),Math.fround(z));
 for(const t of triangles){const [a,b,c]=t.map(i=>i+offset);const ax=positions[b*3]-positions[a*3],az=positions[b*3+2]-positions[a*3+2],bx=positions[c*3]-positions[a*3],bz=positions[c*3+2]-positions[a*3+2];if(Math.abs(az*bx-ax*bz)>1e-8)indices.push(...(az*bx-ax*bz>0?[a,b,c]:[a,c,b]));}
}
function maxGrade(){let max=0;for(let i=0;i<indices.length;i+=3){const [a,b,c]=indices.slice(i,i+3).map(j=>positions.slice(j*3,j*3+3)),u=b.map((v,j)=>v-a[j]),v=c.map((v,j)=>v-a[j]),nx=u[1]*v[2]-u[2]*v[1],ny=u[2]*v[0]-u[0]*v[2],nz=u[0]*v[1]-u[1]*v[0];if(Math.abs(ny)>1e-10)max=Math.max(max,Math.hypot(nx,nz)/Math.abs(ny));}return max;}
const rawGrade=maxGrade(),heightFactor=rawGrade>0?Math.min(1,.08/rawGrade):1;
for(let i=1;i<positions.length;i+=3)positions[i]*=heightFactor;
for(const n of nodes)n.y*=heightFactor;
for(const p of paths)for(const v of p.points)v.y=height(v.x,v.z);
const barriers=[];
for(const rings of union)for(const ring of rings)for(let i=1;i<ring.length;i++){
 const a=ring[i-1],b=ring[i],mx=(a[0]+b[0])/2,mz=(a[1]+b[1])/2;
 // Keep every exposed edge of the shared domain, including enlarged islands.
 // Classify for landscape treatment only; there are never internal gate fences.
 const owner=nodes.find(n=>n.island&&(plan.islandFootprintsXZ?.[n.id]?inFootprint(mx,mz,n)||footprint(n)[0].some((p,i,r)=>{const q=r[(i+1)%r.length],dx=q[0]-p[0],dz=q[1]-p[1],t=Math.max(0,Math.min(1,((mx-p[0])*dx+(mz-p[1])*dz)/(dx*dx+dz*dz||1)));return Math.hypot(mx-p[0]-dx*t,mz-p[1]-dz*t)<.016;}):Math.hypot(mx-n.x,mz-n.z)<n.r+.015));
 barriers.push({a:{x:a[0],y:height(a[0],a[1]),z:a[1]},b:{x:b[0],y:height(b[0],b[1]),z:b[1]},height:1.3,kind:owner?'island-edge':'bridge-edge',island:owner?.island??null});
}
// height() now sees scaled path/node heights, so boundary heights match the scaled deck.
const bounds={minX:Math.min(...union.flat(2).map(p=>p[0]))-1,maxX:Math.max(...union.flat(2).map(p=>p[0]))+1,minZ:Math.min(...union.flat(2).map(p=>p[1]))-1,maxZ:Math.max(...union.flat(2).map(p=>p[1]))+1};
function distances(edges){const out={};for(const a of nodes.filter(n=>n.island)){const d=Object.fromEntries(nodes.map(n=>[n.id,Infinity]));d[a.id]=0;for(let pass=0;pass<nodes.length;pass++)for(const e of edges){d[e.to]=Math.min(d[e.to],d[e.from]+e.length);d[e.from]=Math.min(d[e.from],d[e.to]+e.length);}out[a.island]=Object.fromEntries(nodes.filter(n=>n.island).map(n=>[n.island,+d[n.id].toFixed(3)]));}return out;}
const beforePoints=[];
for(const edge of source.edges){const cp=edge.controlPointsXZ;
 for(let i=0;i<=1000;i++){const t=i/1000,p=cp.length===2?cp[0].map((v,j)=>v+(cp[1][j]-v)*t):cp[0].map((v,j)=>(1-t)**3*v+3*(1-t)**2*t*cp[1][j]+3*(1-t)*t*t*cp[2][j]+t**3*cp[3][j]);beforePoints.push(p);}
}
const baselineBounds={width:Math.max(...beforePoints.map(p=>p[0]))-Math.min(...beforePoints.map(p=>p[0]))+plan.width+2,height:Math.max(...beforePoints.map(p=>p[1]))-Math.min(...beforePoints.map(p=>p[1]))+plan.width+2};
const baselineEdges=source.edges.map(e=>{const cp=e.controlPointsXZ;let length=0,previous=cp[0];for(let i=1;i<=1000;i++){const t=i/1000,p=cp.length===2?cp[0].map((v,j)=>v+(cp[1][j]-v)*t):cp[0].map((v,j)=>(1-t)**3*v+3*(1-t)**2*t*cp[1][j]+3*(1-t)*t*t*cp[2][j]+t**3*cp[3][j]);length+=Math.hypot(p[0]-previous[0],p[1]-previous[1]);previous=p;}return {...e,length};});
const report={comparisonReference:'Original design A reference (not V4); V4-to-current invariants and distances are in layout-audit.json and v4-network-comparison.json',scaleXZ:scale,islandRadii:nodes.filter(n=>n.island).map(n=>({island:n.island,r:n.r})),heightFactor,rawTriangleGrade:rawGrade,levelDatum:plan.heightDatum,baselineHeightRange:[0,2],maxTriangleGrade:maxGrade(),deckTriangles:indices.length/3,boundarySegments:barriers.length,unionComponents:union.length,totalLengthBefore:baselineEdges.reduce((s,e)=>s+e.length,0),totalLengthAfter:paths.reduce((s,e)=>s+e.length,0),shortestBefore:distances(baselineEdges),shortestAfter:distances(paths),boundsBefore:baselineBounds,boundsAfter:{width:bounds.maxX-bounds.minX,height:bounds.maxZ-bounds.minZ},bounds};
const layout={reference:'Manually traced approved plan A; real walkable geometry, no font outlines',width:plan.width,nodes,paths:paths.map(({outline,...p})=>p),bounds};
fs.writeFileSync('src/data/yuan-layout.json',JSON.stringify(layout));
fs.writeFileSync('src/data/yuan-surface.json',JSON.stringify({positions,indices,barriers,domain:union,islandPaving}));
const reportDir=process.argv.includes('--report-dir')?process.argv[process.argv.indexOf('--report-dir')+1]:'docs/previews/eight-islands-world-redesign-v1';
fs.mkdirSync(reportDir,{recursive:true});
fs.writeFileSync(`${reportDir}/network-comparison.json`,JSON.stringify(report,null,2));
console.log(report);
