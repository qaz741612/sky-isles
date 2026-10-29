"""MIT. Re-export saved editable geometry, deduplicate identical exported faces.
Adds only real upward roof surfaces to explicit support; never turns water into floor.
"""
import bpy,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'docs/design/flood-control-island-g-v1';sys.path.insert(0,str(Path(__file__).parent));from flood_export import export_batched
bpy.ops.wm.open_mainfile(filepath=str(D/'flood-control-g.blend'));root=bpy.data.objects['FloodControlPark_MODEL'];deps=bpy.context.evaluated_depsgraph_get();tops=[]
for o in root.children_recursive:
 if o.type!='MESH' or not any(o.name.startswith(n)for n in ['Deep projecting roof','Open entrance canopy','Clerestory canopy','Reading landscape pergola roof','Pier crown','Gate maintenance lintel','Observation cap']):continue
 e=o.evaluated_get(deps);m=e.to_mesh();m.calc_loop_triangles()
 for t in m.loop_triangles:
  vs=[o.matrix_world@m.vertices[i].co for i in t.vertices];n=(vs[1]-vs[0]).cross(vs[2]-vs[0])
  if n.z<=0 or n.z/max(.0000001,n.length)<.85:continue
  for v in vs:tops.extend([round(v.x,6),round(v.z,6),round(-v.y,6)])
 e.to_mesh_clear()
p=ROOT/'src/data/flood-control-collision.json';c=json.loads(p.read_text());c['roofSupportPositions']=tops;p.write_text(json.dumps(c,separators=(',',':')))
r=json.loads((D/'model-report.json').read_text());r.update(export_batched(root,ROOT/'public/models/flood-control-g/flood-control-g.glb'));r.update({'roofSupportTriangles':len(tops)//9,'sourceBlendSHA256':hashlib.sha256((D/'flood-control-g.blend').read_bytes()).hexdigest()});(D/'model-report.json').write_text(json.dumps(r,indent=2));print('FINAL_EXPORT',json.dumps(r),flush=True)
