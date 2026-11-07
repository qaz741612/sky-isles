"""Read only: exact low-poly opaque tree crowns for local camera visibility.
Never export these as floors, player walls, visible geometry or extra GLBs.
"""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];rows={}
for code in'BDEH':
 path=R/f'docs/design/bdeh-r21/{code}/{code}-r21.blend';sha=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(path));root=bpy.data.objects[f'R21_{code}_MODEL'];dg=bpy.context.evaluated_depsgraph_get();items=[]
 for o in root.children_recursive:
  if o.type!='MESH'or not o.get('sourceComponent','').startswith('foliage'):continue
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();vertices=[ev.matrix_world@v.co for v in m.vertices];positions=[]
  for t in m.loop_triangles:
   for index in t.vertices:
    v=vertices[index];positions.extend([round(v.x,6),round(v.z,6),round(-v.y,6)])
  items.append({'id':o.name,'positions':positions});ev.to_mesh_clear()
 assert sum(len(p['positions'])//9 for p in items)<5000
 assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
 rows[code]={'sourceBlendSHA256':sha,'canopies':items,'triangles':sum(len(p['positions'])//9 for p in items)}
(R/'src/data/bdeh-camera-canopies.json').write_text(json.dumps({'purpose':'Camera-only exact opaque low-poly tree crowns; local four-island constraint only; no player barriers, no draws, no F/A/C/G camera changes','islands':rows},separators=(',',':'))+'\n')
print('Local camera canopy triangles:',{c:v['triangles']for c,v in rows.items()})
