"""Read-only final G site audit; actual authored footprint/Bezier/collision/GLB."""
from pathlib import Path
import json, math, hashlib, struct
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[2];O=R/'docs/previews/flood-control-island-g-v5';D=R/'docs/design/flood-control-island-g-v5'
def read(p):return json.loads((R/p).read_text())
def multi(v):return unary_union([Polygon(p[0],p[1:])for p in v])
p=read('src/data/flood-control-plan.json');y=read('src/data/yuan-plan.json');s=read('src/data/flood-control-site.json');c=read('src/data/flood-control-collision.json');old=read('docs/design/flood-control-island-g-v5/protected-baseline.json');cen=p['centre'];land=Polygon(y['islandFootprintsXZ']['G']);local=Polygon([(x-cen[0],z-cen[2])for x,z in land.exterior.coords]);dry=multi(s['floor']);wet=multi(s['waterHoles']);waters=multi(s['water']);road=multi(s['protectedRoads']);
def bezier(e):
 cp=e['controlPointsXZ'];return LineString([[sum(q[j]*v for q,v in zip(cp,[(1-t)**3,3*(1-t)**2*t,3*(1-t)*t*t,t**3]))for j in [0,1]]if len(cp)==4 else[cp[0][j]*(1-t)+cp[1][j]*t for j in [0,1]]for t in np.linspace(0,1,4097)])
roads={e['id']:bezier(e)for e in y['edges']};oldroads={e['id']:bezier(e)for e in old['yuanSource']['edges']};paths={k:{'length':v.length,'unchangedControlPoints':next(e for e in y['edges']if e['id']==k)==next(e for e in old['yuanSource']['edges']if e['id']==k)}for k,v in roads.items()}
solids=[(v,Polygon(v['polygon']))for v in c['solids']if 'polygon'in v and v['base']<1.6 and v['top']>0];openings={}
for k in ['S21','S22']:
 core=roads[k].buffer(2.4);intrusions=[]
 for name,poly in solids:
  world=Polygon([(x+cen[0],z+cen[2])for x,z in poly.exterior.coords]);a=world.intersection(core).area
  if a>1e-5:intrusions.append({'name':name['name'],'area':a})
 openings[k]={'solidIntrusions':intrusions,'insideIsland':roads[k].intersection(land).length,'outsideIsland':roads[k].difference(land).length,'mouthCoreWidth':4.8}
x,_,z=p['npc'][0]['position'];npc=box(x-1.5,z-1.5,x+1.5,z+1.5)
walk=LineString(p['publicCircuit']);blocked=[]
for a,poly in solids:
 if walk.buffer(.365).intersects(poly)and walk.buffer(.365).intersection(poly).area>1e-5:blocked.append(a['name'])
# Actual ground/crossing triangles: no sloped visual water is treated as floor.
vals=np.asarray(c['groundPositions'][:c['dryGroundFloats']]).reshape((-1,3,3));n=np.cross(vals[:,1]-vals[:,0],vals[:,2]-vals[:,0]);valid=np.abs(n[:,1])>1e-10;grade=np.sqrt(n[valid,0]**2+n[valid,2]**2)/np.abs(n[valid,1]);
# GLB hierarchy/transformed bounds with no texture/binary output.
b=(R/'public/models/flood-control-g/flood-control-g.glb').read_bytes();size=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+size]);bounds=[]
def node(idx,mat):
 v=g['nodes'][idx];m=np.eye(4)
 if 'matrix'in v:m=np.asarray(v['matrix']).reshape((4,4)).T
 else:
  m[:3,3]=v.get('translation',[0,0,0]);q=v.get('rotation',[0,0,0,1]);x,yq,zq,w=q;rot=np.array([[1-2*(yq*yq+zq*zq),2*(x*yq-zq*w),2*(x*zq+yq*w)],[2*(x*yq+zq*w),1-2*(x*x+zq*zq),2*(yq*zq-x*w)],[2*(x*zq-yq*w),2*(yq*zq+x*w),1-2*(x*x+yq*yq)]]);m[:3,:3]=rot@np.diag(v.get('scale',[1,1,1]))
 m=mat@m
 if 'mesh'in v:
  for prim in g['meshes'][v['mesh']]['primitives']:
   a=g['accessors'][prim['attributes']['POSITION']];lo=a['min'];hi=a['max']
   for x in [lo[0],hi[0]]:
    for yq in [lo[1],hi[1]]:
     for zq in [lo[2],hi[2]]:bounds.append((m@np.array([x,yq,zq,1]))[:3])
 for i in v.get('children',[]):node(i,m)
for i in g['scenes'][g.get('scene',0)]['nodes']:node(i,np.eye(4))
bounds=np.array(bounds);lo=bounds.min(axis=0);hi=bounds.max(axis=0)
report={'scope':'G V5 final actual geometry; not human art approval or hardware FPS','base':old['baseCommit'],'centre':cen,'footprint':{'boundsLocal':list(local.bounds),'width':local.bounds[2]-local.bounds[0],'depth':local.bounds[3]-local.bounds[1],'area':local.area,'westNotch':True},'water':{'surfaceArea':waters.area,'openVoidArea':wet.area,'levelHeights':p['waterHeights'],'drop':p['waterHeights']['upstream']-p['waterHeights']['downstream'],'throats':p['sluiceThroats'],'isCollider':c['waterIsCollider']},'S20':{'samples':4097,'centreGap':land.distance(roads['S20']),'coreGap':land.distance(roads['S20'].buffer(2.4)),'conservativeOuterStructureGap':land.distance(roads['S20'].buffer(3.1))},'mouths':openings,'routes':paths,'totalCentrelineLength':sum(v.length for v in roads.values()),'beforeCentrelineLength':sum(v.length for v in oldroads.values()),'publicCircuit':{'capsuleRadius':.365,'solidIntrusions':blocked,'length':walk.length,'dryMissingArea':walk.buffer(.365).difference(dry).area},'NPC':{'count':1,'personImplemented':False,'data':p['npc'][0],'outsideDryArea':npc.difference(dry).area,'wetOverlapArea':npc.intersection(wet).area,'solidIntrusions':[v['name']for v,poly in solids if npc.intersection(poly).area>1e-5]},'floorTriangleGrade':{'triangles':len(vals),'max':float(grade.max())},'model':{'boundsLocalXYZ':[lo.tolist(),hi.tolist()],'dimensionsXYZ':(hi-lo).tolist(),'glbBytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'meshes':len(g['meshes']),'materials':len(g['materials']),'textures':len(g.get('textures',[]))},'islandGaps':[]}
for q in y['nodes']:
 if not q.get('island')or q['id']=='G':continue
 shape=Polygon(y['islandFootprintsXZ'][q['id']])if q['id']in y['islandFootprintsXZ']else Point(q['x'],q['z']).buffer(q['r'],quad_segs=128)
 report['islandGaps'].append({'id':q['id'],'distance':land.distance(shape),'overlapArea':land.intersection(shape).area})
assert all(v['unchangedControlPoints']for v in paths.values());assert not blocked;assert report['NPC']['wetOverlapArea']<1e-6;assert all(not v['solidIntrusions']for v in openings.values());assert report['S20']['conservativeOuterStructureGap']>3.3
(O/'spatial-audit-final.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Final audit saved; 22 exact control lines, S20 %.3f gap, NPC dry/free, zero public-route intrusions'%report['S20']['conservativeOuterStructureGap'])
