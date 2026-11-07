// R21's B bridge mouths share one real, rounded north/east courtyard route.
// Only trim the part inside the new B footprint; preserve every exterior sample.
function inside(x,z,ring){let yes=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>z)!==(b[1]>z)&&x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0])yes=!yes;}return yes;}
function rounded(points){
 const clean=points.filter((p,i)=>!i||Math.hypot(p.x-points[i-1].x,p.z-points[i-1].z)>.01),out=[clean[0]];
 for(let i=1;i<clean.length-1;i++){
  const a=clean[i-1],b=clean[i],c=clean[i+1],l=Math.hypot(a.x-b.x,a.z-b.z),r=Math.hypot(c.x-b.x,c.z-b.z),d=Math.min(1.1,l*.25,r*.25);
  const p={x:b.x+(a.x-b.x)*d/l,z:b.z+(a.z-b.z)*d/l},q={x:b.x+(c.x-b.x)*d/r,z:b.z+(c.z-b.z)*d/r};out.push(p);
  for(let k=1;k<=12;k++){const t=k/12;out.push({x:(1-t)**2*p.x+2*(1-t)*t*b.x+t*t*q.x,z:(1-t)**2*p.z+2*(1-t)*t*b.z+t*t*q.z});}
 }
 out.push(clean.at(-1));return out.map(p=>({...p,y:0,s:0}));
}
export function applyIslandApproach(points,edge,plan,nodes){
 for(const[id,a]of Object.entries(plan.islandApproaches??{})){
  if(edge.from!==id&&edge.to!==id)continue;
  const n=nodes.get(id),ring=plan.islandFootprintsXZ[id],outward=edge.from===id?points:points.toReversed();
  const cut=outward.findIndex(p=>!inside(p.x,p.z,ring));if(cut<1)throw Error(`No external mouth ${edge.id}`);
  const way=a.waypointsLocal[edge.id];if(!way)throw Error(`Unspecified internal approach ${edge.id}`);
  const prefix=rounded([...way.toReversed().map(([x,z])=>({x:x+n.x,z:z+n.z})),outward[cut]]),joined=[...prefix,...outward.slice(cut+1)];
  return edge.from===id?joined:joined.toReversed();
 }
 return points;
}
export function applyProtectedApproach(points,edge,plan,baselineCount){
 const request=plan.preservedApproaches?.[edge.id];if(!request)return points;
 const cp=plan.referenceBaselineEdges[edge.id],at=t=>cp[0].map((v,i)=>(1-t)**3*v+3*(1-t)**2*t*cp[1][i]+3*(1-t)*t*t*cp[2][i]+t**3*cp[3][i]);
 const k=Math.round(request.fraction*baselineCount),t=k/baselineCount,q=at(t),derivative=cp[0].map((_,i)=>3*(1-t)**2*(cp[1][i]-cp[0][i])+6*(1-t)*t*(cp[2][i]-cp[1][i])+3*t*t*(cp[3][i]-cp[2][i]));
 const old=Array.from({length:baselineCount+1},(_,i)=>{const p=at(i/baselineCount);return{x:p[0],y:0,z:p[1],s:0};});
 const next=edge.controlPointsXZ,curve=request.end==='to'?[next[0],next[1],q.map((v,i)=>v-derivative[i]*t/3),q]:[q,q.map((v,i)=>v+derivative[i]*(1-t)/3),next[2],next[3]];
 const count=Math.ceil(curve.slice(1).reduce((n,p,i)=>n+Math.hypot(p[0]-curve[i][0],p[1]-curve[i][1]),0)/.6),fresh=Array.from({length:count+1},(_,i)=>{const u=i/count,p=curve[0].map((v,j)=>(1-u)**3*v+3*(1-u)**2*u*curve[1][j]+3*(1-u)*u*u*curve[2][j]+u**3*curve[3][j]);return{x:p[0],y:0,z:p[1],s:0};});
 return request.end==='to'?[...fresh.slice(0,-1),...old.slice(k)]:[...old.slice(0,k),...fresh];
}
