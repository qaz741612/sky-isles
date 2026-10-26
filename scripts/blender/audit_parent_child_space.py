"""Measured plan-space clearance from evaluated Blender geometry, not a game physics test. MIT."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from shapely.geometry import MultiPoint,Point,LineString,mapping
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/design/parent-child-blender-refinement-v2';SOURCE=OUT/'parent-child-centre.blend';cfg=json.loads((OUT/'layout.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));model=bpy.data.objects['ParentChildCentre_MODEL'];deps=bpy.context.evaluated_depsgraph_get();obstacles=[];components=[]
for obj in model.children_recursive:
 if obj.type!='MESH':continue
 e=obj.evaluated_get(deps);mesh=e.to_mesh();points=[obj.matrix_world@v.co for v in mesh.vertices];z0=min(p.z for p in points);z1=max(p.z for p in points)
 # Ignore traversable low floor finishes/thresholds and overhead pieces. Other geometry is conservatively projected.
 if z1<=.22 or z0>=1.78:e.to_mesh_clear();continue
 cut=[(p.x,p.y)for p in points if .22<=p.z<=1.78]
 for edge in mesh.edges:
  a,b=(points[i]for i in edge.vertices)
  for z in [.22,1.78]:
   if min(a.z,b.z)<z<max(a.z,b.z):
    t=(z-a.z)/(b.z-a.z);cut.append((a.x+t*(b.x-a.x),a.y+t*(b.y-a.y)))
 e.to_mesh_clear()
 if len(cut)<3:continue
 hull=MultiPoint(cut).convex_hull
 if hull.area<.00005:continue
 obstacles.append(hull);components.append({'name':obj.name,'minZ':z0,'maxZ':z1,'footprint':mapping(hull)})
occupied=unary_union(obstacles);routes=[]
for route in cfg['routes']:
 line=LineString(route['points']);corridor=line.buffer(route['width']/2,cap_style=2,join_style=1)
 touching=[c['name']for c,p in zip(components,obstacles)if corridor.intersection(p).area>.0001]
 actor_contacts=[c['name']for c,p in zip(components,obstacles)if line.buffer(.35,cap_style=1).intersection(p).area>.0001]
 routes.append({'id':route['id'],'centrelineLength':line.length,'proposedWidth':route['width'],'minimumCentrelineObstacleDistance':line.distance(occupied),'corridorOverlapArea':corridor.intersection(occupied).area,'corridorContacts':touching,'playerRadius':.35,'playerContacts':actor_contacts,'playerClear':not actor_contacts})
npc=cfg['npcReservation'];centre=Point(npc['position'][:2]);player=Point(npc['playerApproach'][:2]);npc_contacts=[c['name']for c,p in zip(components,obstacles)if centre.buffer(npc['activityRadius']).intersection(p).area>.0001];stand_contacts=[c['name']for c,p in zip(components,obstacles)if player.buffer(.35).intersection(p).area>.0001]
npc_route_contacts=[r['id']for r in cfg['routes']if LineString(r['points']).buffer(r['width']/2,cap_style=2).intersection(centre.buffer(npc['activityRadius'])).area>.0001]
report={'npcActivityOverlappingRoutes':npc_route_contacts,'sourceBlendSHA256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'method':'Conservative convex XY hull of each evaluated solid clipped to height slab 0.22..1.78; low finishes <=0.22 are treated as stepping surfaces. Overhead pieces are excluded. This is a clearance design audit, not game physics or accessibility-code certification.','siteRadius':cfg['siteRadius'],'obstacleComponents':len(components),'routes':routes,'npcReservation':{**npc,'nearestObstacleDistance':centre.distance(occupied),'activityContacts':npc_contacts,'approachContacts':stand_contacts,'clear':not npc_contacts and not stand_contacts},'allRoutesPlayerClear':all(r['playerClear']for r in routes)}
(OUT/'space-audit.json').write_text(json.dumps(report,indent=2));(OUT/'space-footprints.json').write_text(json.dumps({'components':components},separators=(',',':')))
print(json.dumps(report),flush=True)
