"""Verify retained PR11 entrance geometry and measure the refined assemblies. MIT."""
import bpy,json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OLD=ROOT/'docs/design/parent-child-blender-model-v1';OUT=ROOT/'docs/design/parent-child-blender-refinement-v2'
def inspect(source):
 bpy.ops.wm.open_mainfile(filepath=str(source));deps=bpy.context.evaluated_depsgraph_get();data={'assemblies':{},'retainedGeometry':{},'roofSeams':{}}
 for name in ['MainCurvedHall','UpperLeftDaylightLevel','LeftFamilyReadingWing','RightCareWing','EntryCanopy','WestEntryTimberTrellis']:
  root=bpy.data.objects[name];objects=[o for o in root.children_recursive if o.type=='MESH'];points=[];payload=[]
  for obj in sorted(objects,key=lambda o:o.name):
   e=obj.evaluated_get(deps);m=e.to_mesh();world=[tuple(obj.matrix_world@v.co)for v in m.vertices];points.extend(world);payload.append({'name':obj.name,'worldVertices':world,'polygons':[list(p.vertices)for p in m.polygons]});e.to_mesh_clear()
  data['assemblies'][name]={'min':[min(v[i]for v in points)for i in range(3)],'max':[max(v[i]for v in points)for i in range(3)],'sizeXYZ':[max(v[i]for v in points)-min(v[i]for v in points)for i in range(3)]}
  if name in ['EntryCanopy','WestEntryTimberTrellis']:data['retainedGeometry'][name]=hashlib.sha256(json.dumps(payload,separators=(',',':')).encode()).hexdigest()
  data['roofSeams'][name]=sum('StandingSeam'in o.name or 'QuietRoofSeam'in o.name for o in objects)
 return data
before=inspect(OLD/'parent-child-centre.blend');after=inspect(OUT/'parent-child-centre.blend');preserved=before['retainedGeometry']==after['retainedGeometry'];assert preserved,'Successful entrance geometry was changed'
(OUT/'lineage-audit.json').write_text(json.dumps({'basePR':11,'method':'Open original and final BLEND separately; hash actual evaluated world-space vertices and polygons for retained entrance assemblies. Material changes are intentionally excluded.','entranceGeometryUnchanged':preserved,'before':before,'after':after},indent=2)+'\n');print('PR11 entrance and timber trellis geometry preserved exactly',flush=True)
