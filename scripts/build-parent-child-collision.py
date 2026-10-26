"""Read approved Blender source; export only invisible collision data. Never save or remodel it."""
import bpy,json,sys,hashlib,math
from pathlib import Path
from shapely.geometry import MultiPoint
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'src/data/parent-child-collision.json';SOURCE=ROOT/'docs/design/parent-child-blender-refinement-v2/parent-child-centre.blend'
config=json.loads((ROOT/'src/data/parent-child-model.json').read_text());assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==config['sourceBlendSHA256']
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));model=bpy.data.objects['ParentChildCentre_MODEL'];deps=bpy.context.evaluated_depsgraph_get();solids=[];grounds=[];ceilings=[];cameras=[]
for obj in model.children_recursive:
 if obj.type!='MESH':continue
 chain=[];p=obj.parent
 while p and p!=model:chain.append(p.name);p=p.parent
 role=chain[-1];name=obj.name
 # The island's shared union supplies exposed rails/bridge ground. Indoor furniture remains behind closed walls.
 if role in ['InteriorFurniture','SiteAndBridgeStubs']:continue
 e=obj.evaluated_get(deps);m=e.to_mesh();points=[obj.matrix_world@v.co for v in m.vertices];lo=min(v.z for v in points);hi=max(v.z for v in points)
 # Only actual solid in the unchanged player's head/foot envelope. Low finishes are walkable.
 if hi>.23 and lo<1.6:
  cut=[(v.x,-v.y)for v in points if .08<=v.z<=1.6]
  for edge in m.edges:
   a,b=(points[i]for i in edge.vertices)
   for z in [.08,1.6]:
    if min(a.z,b.z)<z<max(a.z,b.z):
     t=(z-a.z)/(b.z-a.z);cut.append((a.x+(b.x-a.x)*t,-a.y-(b.y-a.y)*t))
  if len(cut)>=3:
   hull=MultiPoint(cut).convex_hull.simplify(.008,preserve_topology=True)
   if hull.area>.00003:solids.append({'name':name,'role':role,'base':lo,'top':hi,'polygon':[[round(x,5),round(z,5)]for x,z in list(hull.exterior.coords)[:-1]]})
 # Only real architecture can obstruct camera/head; leaves/flowers never clamp the camera.
 # Closed low-poly hull of each structural component: proxies are never rendered.
 structural=(role=='Architecture' or (role=='Landscape' and (name.startswith('FacetedCrown') or name.startswith('TaperedTreeTrunk')))) and 'glass' not in ''.join(s.material.name.lower()for s in obj.material_slots if s.material)
 if structural:
  hull=MultiPoint([(v.x,-v.y)for v in points]).convex_hull
  if hull.area>.001 and hi-lo>.05:cameras.append({'name':name,'base':lo,'top':hi,'polygon':[[round(x,5),round(z,5)]for x,z in list(hull.exterior.coords)[:-1]]})
 m.calc_loop_triangles()
 for tri in m.loop_triangles:
  pts=[points[i]for i in tri.vertices];a,b,c=pts;normal=(b-a).cross(c-a);length=normal.length
  if length<1e-9:continue
  # Real low steps/floors. Play equipment is an exhibit, not a ride/climbing system.
  isroof=any(name==n for n in ['MainWaveRoof','UpperLeftWaveRoof','LeftLowerCurvedRoof','RightCurvedWingRoof','EntryCanopySolid','WestVerandaSolidCanopy','EastVerandaSolidCanopy'])
  isfloor=hi<=.23 or (role=='Architecture' and isroof) or role=='Playground'
  if isfloor and normal.z/length>.45:grounds.extend([round(v,6)for p in pts for v in[p.x,p.z,-p.y]])
  if ((role=='Architecture' and isroof) or (role=='Playground' and name=='PlayhouseGableRoof')) and normal.z/length<-.4 and min(v.z for v in pts)>1.55:ceilings.extend([round(v,6)for p in pts for v in[p.x,p.z,-p.y]])
 e.to_mesh_clear()
OUT.write_text(json.dumps({'sourceBlendSHA256':config['sourceBlendSHA256'],'role':'Invisible integration proxies only. Approved BLEND and GLB remain unchanged. Heights and XY hulls from evaluated real components; glass is solid, open verandas stay open. Play equipment not climbable; no NPC collider because no NPC exists.','solids':solids,'groundPositions':grounds,'ceilingPositions':ceilings,'cameraSolids':cameras},separators=(',',':')))
print(json.dumps({'solids':len(solids),'groundTriangles':len(grounds)//9,'ceilingTriangles':len(ceilings)//9,'cameraSolids':len(cameras)}),flush=True)
