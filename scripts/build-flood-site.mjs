// MIT. Single G design source -> shared world footprint + public surface with water holes.
import fs from 'node:fs';import {ShapeUtils,Vector2} from 'three';import polygon from 'polygon-clipping';
const p=JSON.parse(fs.readFileSync('src/data/flood-control-plan.json')),yuan=JSON.parse(fs.readFileSync('src/data/yuan-plan.json')),l=JSON.parse(fs.readFileSync('src/data/yuan-layout.json'));
yuan.islandFootprintsXZ.G=p.footprintLocal.map(([x,z])=>[+(x+p.centre[0]).toFixed(5),+(z+p.centre[2]).toFixed(5)]);
yuan.landscapeRetainedLampAnchors=p.preserveLampAnchors;fs.writeFileSync('src/data/yuan-plan.json',JSON.stringify(yuan,null,2)+'\n');
const roads=l.paths.filter(r=>['S21','S22'].includes(r.id)).map(path=>{const edges=path.points.map((v,i,a)=>{const u=a[Math.max(0,i-1)],w=a[Math.min(a.length-1,i+1)],dx=w.x-u.x,dz=w.z-u.z,d=Math.hypot(dx,dz),x=v.x-p.centre[0],z=v.z-p.centre[2];return[[x-dz/d*2.55,z+dx/d*2.55],[x+dz/d*2.55,z-dx/d*2.55]];});const r=[...edges.map(x=>x[0]),...edges.toReversed().map(x=>x[1])];return[[...r,r[0]]];});
const [x,z,X,Z]=p.crosswalk,cross=[[[x,z],[X,z],[X,Z],[x,Z],[x,z]]];
const waters=polygon.union([p.water.upstream],[p.water.downstream]),holes=polygon.difference(waters,...roads,cross),floor=polygon.difference([p.footprintLocal],holes);
const edges=holes.flatMap(rings=>rings.flatMap(r=>r.slice(1).map((b,i)=>({a:r[i],b}))));
fs.writeFileSync('src/data/flood-control-site.json',JSON.stringify({floor,waterHoles:holes,waterRails:edges,protectedRoads:roads,crosswalk:cross}));console.log('G footprint and water-cut floor generated',floor.length,'regions',edges.length,'water edge segments');

const vertices=[],triangles=[];for(const rings of floor){const r=rings.map(r=>r.slice(0,-1)),off=vertices.length;vertices.push(...r.flat().map(([x,z])=>[x,0,z]));triangles.push(...ShapeUtils.triangulateShape(r[0].map(p=>new Vector2(...p)),r.slice(1).map(r=>r.map(p=>new Vector2(...p)))).map(t=>t.map(i=>i+off)));}
for(const t of triangles){const[a,b,c]=t.map(i=>vertices[i]);if((b[0]-a[0])*(c[2]-a[2])-(b[2]-a[2])*(c[0]-a[0])>0)[t[1],t[2]]=[t[2],t[1]];}
fs.writeFileSync('src/data/flood-control-floor.json',JSON.stringify({vertices,triangles}));

const rect=(x,z,X,Z)=>[[[x,z],[X,z],[X,Z],[x,Z],[x,z]]];
const loop=[[0,0],[6.8,0],[6.8,1.5],[0,1.5],[0,3],[0,8],[1,10],[8.5,9.5],[11,7],[11,0],[8.7,-3.1],[6,-4],[0,0],[-9,0],[-10.8,-.3],[-9,0],[-9.5,1],[-9,0],[0,0]],strips=[];
for(let i=1;i<loop.length;i++){const a=loop[i-1],b=loop[i],dx=b[0]-a[0],dz=b[1]-a[1],d=Math.hypot(dx,dz);if(d<.01)continue;const nx=-dz/d*1.0,nz=dx/d*1.0;strips.push([[[a[0]+nx,a[1]+nz],[b[0]+nx,b[1]+nz],[b[0]-nx,b[1]-nz],[a[0]-nx,a[1]-nz],[a[0]+nx,a[1]+nz]]]);}
const paving=polygon.intersection(floor,polygon.union(...roads,cross,rect(3.5,.4,10.4,8.4),...strips));
const pv=[],pt=[];for(const rings of paving){const r=rings.map(r=>r.slice(0,-1)),off=pv.length;pv.push(...r.flat().map(([x,z])=>[x,.012,z]));pt.push(...ShapeUtils.triangulateShape(r[0].map(p=>new Vector2(...p)),r.slice(1).map(r=>r.map(p=>new Vector2(...p)))).map(t=>t.map(i=>i+off)));}
for(const t of pt){const[a,b,c]=t.map(i=>pv[i]);if((b[0]-a[0])*(c[2]-a[2])-(b[2]-a[2])*(c[0]-a[0])>0)[t[1],t[2]]=[t[2],t[1]];}
fs.writeFileSync('src/data/flood-control-paving.json',JSON.stringify({domain:paving,vertices:pv,triangles:pt}));
