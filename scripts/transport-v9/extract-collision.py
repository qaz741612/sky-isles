"""Read-only ca94f48 BLEND -> runtime collision data; never saves or remodels. MIT."""
import bpy,sys,os,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from shapely.geometry import Polygon,box,MultiPoint
from shapely import constrained_delaunay_triangles
ROOT=Path(__file__).resolve().parents[2];source=ROOT/'work/transport-station-v9.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();expected='5d99e81f8255f815e60ab0d63615ce024e96533c6757821beb74eb777c7eade6';assert sha(source)==expected
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update();root=bpy.data.objects['YuanliElevatedStationV9'];deps=bpy.context.evaluated_depsgraph_get();offset=-.075;report=json.loads((ROOT/'work/source-model-report.json').read_text());shells=json.loads((ROOT/'work/source-collision.json').read_text())['shells'];site=Polygon(report['sitePolygonXZ']);ground=[];ceilings=[];camera=[];solids=[];sloping=[];walkNames=('PhysicalStairTread','StairMidLanding','StairTopLanding','TopAccessBridge','LiftLandingBridge','PlatformWalkingSurface','StationStoneBase','IndoorTimberFloor','LevelEntryThreshold','StandingSeamRoofWing','RoofSkyOpeningEnd','HallSkylight','StairExitShelterRoof','LiftFlatRoof','RoundedCarRoof','RooftopHVAC')
for tri in constrained_delaunay_triangles(site).geoms:
 if site.covers(tri):
  p=list(tri.exterior.coords)[:3];ground.extend([p[0][0],0,p[0][1],p[2][0],0,p[2][1],p[1][0],0,p[1][1]])
siteGroundFloats=len(ground)
ceilNames=('StandingSeamRoofWing','RoofSkyOpeningEnd','HallSkylight','DeepEntryHeader','ViaductRecessedRailDeck','LoadBearingArchFascia','PhysicalStairTread','StairMidLanding','StairTopLanding','TopAccessBridge','LiftLandingBridge','StairExitShelterRoof','LiftFlatRoof')
for o in root.children_recursive:
 if o.type!='MESH':continue
 role=o
 while role.parent and role.parent!=root:role=role.parent
 if role.name not in ['Hall','Viaduct','Railway','VerticalCirculation','OpenPlatform','TrainRollingStock','Furniture']:continue
 e=o.evaluated_get(deps);me=e.to_mesh();me.calc_loop_triangles();v=[o.matrix_world@p.co for p in me.vertices];world=[(p.x,p.z+offset,-p.y)for p in v]
 for t in me.loop_triangles:
  a,b,c=[Vector(world[i])for i in t.vertices];n=(b-a).cross(c-a);length=n.length
  if length<1e-10:continue
  ny=n.y/length;pts=[*a,*b,*c]
  if o.name.startswith(walkNames)and ny>.65:ground.extend(pts)
  if o.name.startswith(ceilNames)and ny<-.35 and min(a.y,b.y,c.y)>.65:ceilings.extend(pts)
 # Bench collision follows each actual plank/leg, not the former filled bench box.
 if o.name.startswith(('GardenWaitingBench','WindowWaitingBench')):
  poly=MultiPoint([(p[0],p[2])for p in world]).convex_hull
  if poly.geom_type=='Polygon':solids.append({'name':o.name,'kind':'furniture','polygon':list(poly.exterior.coords),'base':min(p[1]for p in world),'top':max(p[1]for p in world)})
 if o.name.startswith('StairSlopingHandrail'):
  lo=min(p.co.z for p in me.vertices);hi=max(p.co.z for p in me.vertices);a=o.matrix_world@Vector((0,0,lo));b=o.matrix_world@Vector((0,0,hi));sloping.append({'a':[a.x,a.z+offset-.85,-a.y],'b':[b.x,b.z+offset-.85,-b.y],'height':.85,'thickness':.035,'source':o.name})
 e.to_mesh_clear()
# Authored wall/column/planter/guard footprints; separate floor/roof semantics.
for s in shells:
 if s['role']in ['walkable','stepped_walkable']or s['kind']in ['ground','platform','ceiling','stairs']:continue
 if s['id']in ['GardenWaitingBench','WindowWaitingBench']:continue
 solids.append({'name':s['id'],'kind':s['kind'],'polygon':s['polygonXZ'],'base':s['bottom']+offset,'top':s['top']+offset})
# Existing glass is closed, although the old offline shell left its central opening empty.
solids.append({'name':'ActualClosedEntranceGlass','kind':'wall','polygon':list(box(-1.95,-3.13,1.95,-2.95).exterior.coords),'base':.175,'top':2.525})
# Real lower stair side faces: exclude low risers so native step logic still has true surfaces.
for flight,x in [(0,-8.6),(1,-7.45)]:
 for i in range(12):
  run=3.28/12;z=-3.12-(i+.5)*run if flight==0 else -6.40+(i+.5)*run;top=(flight*12+i+1)*(3.675/24)
  for xx in [x-.50,x+.50]:
   sloping.append({'a':[xx,0,z-run/2],'b':[xx,0,z+run/2],'height':top,'thickness':.02,'source':'actual-solid-stair-side'})
# Camera sees building masses, ceilings and columns, never all flowers/sign meshes.
for s in solids:
 if s['kind']in ['wall','column','lift','train']:camera.append(s)
# Same source footprint, a local foundation proposal only; no node/Bezier changes.
planPath=ROOT/'src/data/yuan-plan.json';plan=json.loads(planPath.read_text());plan['islandFootprintsXZ']={'F':report['sitePolygonXZ']};planPath.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
config={'url':'/prototypes/transport-elevated-station-v9/transport-station-v9-game-candidate.glb','sourceCommit':'ca94f48bccdc89a00e5a0688479214d6114915d6','referenceDocumentsCommit':'114a134c608026e97b08b0c2a2015e1e3d82c549','sha256':'d9292bf4e7b6c667e75f5e3d668ff5fb52eca2677a7c2cb080a95193b31878ac','scale':1,'yaw':0,'position':[0,offset,0],'capsuleHeight':1.6,'footprintXZ':report['sitePolygonXZ'],'upperAccess':'display-only; visible ground stair closure and closed lift glass','entrance':[0,0,-2.45],'entryRecess':[0,0,-2.45]}
(ROOT/'src/data/elevated-station-model.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n');data={'sourceBlendSHA256':expected,'sourceGLBSHA256':config['sha256'],'worldOffsetY':offset,'groundPositions':ground,'siteGroundFloats':siteGroundFloats,'ceilingPositions':ceilings,'solids':solids,'cameraSolids':camera,'slopingGuards':sloping};(ROOT/'src/data/elevated-station-collision.json').write_text(json.dumps(data,separators=(',',':'))+'\n');assert sha(source)==expected
print(json.dumps({'groundTriangles':len(ground)//9,'ceilingTriangles':len(ceilings)//9,'solids':len(solids),'cameraSolids':len(camera),'sourceUnchanged':True}),flush=True);sys.stdout.flush();os._exit(0)
