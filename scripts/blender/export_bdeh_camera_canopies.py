"""Read only: exact low-poly opaque tree crowns for local camera visibility.
Never export these as floors, player walls, visible geometry or extra GLBs.
"""
import bpy,json,hashlib
from mathutils import Vector,kdtree
from pathlib import Path
R=Path(__file__).resolve().parents[2];rows={}
for code in'BDEH':
 path=R/f'docs/design/bdeh-r21/{code}/{code}-r21.blend';sha=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(path));root=bpy.data.objects[f'R21_{code}_MODEL'];dg=bpy.context.evaluated_depsgraph_get();items=[];glass=[]
 for o in root.children_recursive:
  if o.type!='MESH':continue
  canopy=o.get('sourceComponent','').startswith('foliage');structure=o.get('semanticRole')in['building','roof']
  if not canopy and not structure:continue
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();vertices=[ev.matrix_world@v.co for v in m.vertices];positions=[]
  for t in m.loop_triangles:
   tri=[]
   for index in t.vertices:
    v=vertices[index];tri.append(Vector((v.x,v.z,-v.y)))
   if canopy:
    for v in tri:positions.extend([round(v.x,6),round(v.y,6),round(v.z,6)])
   elif structure and t.material_index<len(o.data.materials):
    mat=o.data.materials[t.material_index];node=mat.node_tree.nodes.get('Principled BSDF')if mat and mat.use_nodes else None
    if node and(node.inputs['Alpha'].default_value<.95 or node.inputs['Transmission Weight'].default_value>.1):glass.append(tri)
  if canopy:items.append({'id':o.name,'positions':positions})
  ev.to_mesh_clear()
 assert sum(len(p['positions'])//9 for p in items)<5000
 assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
 camera=json.loads((R/f'src/data/bdeh-{code.lower()}-collision.json').read_text())['cameraPositions'];faces=[[Vector(camera[i+j:i+j+3])for j in[0,3,6]]for i in range(0,len(camera),9)];tree=kdtree.KDTree(len(faces))
 for i,tri in enumerate(faces):tree.insert(sum(tri,Vector())/3,i)
 tree.balance();removed=set()
 for tri in glass:
  found=False
  for _,i,_ in tree.find_range(sum(tri,Vector())/3,.0002):
   if i not in removed and all(any((v-w).length<.0002 for w in faces[i])for v in tri):removed.add(i);found=True;break
  assert found,('Transparent camera triangle not found',code,[list(v)for v in tri])
 rows[code]={'sourceBlendSHA256':sha,'canopies':items,'triangles':sum(len(p['positions'])//9 for p in items),'transparentCameraTriangles':sorted(removed)}
(R/'src/data/bdeh-camera-canopies.json').write_text(json.dumps({'purpose':'Camera-only exact opaque low-poly tree crowns; local four-island constraint only; no player barriers, no draws, no F/A/C/G camera changes','islands':rows},separators=(',',':'))+'\n')
print('Local camera crowns/transparent faces:',{c:(v['triangles'],len(v['transparentCameraTriangles']))for c,v in rows.items()})
