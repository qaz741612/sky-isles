"""Read-only audit of the preserved R21 architecture, terrain and materials."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];D=R/'docs/design/bdeh-r21';O=R/'docs/previews/bdeh-r21/final-qa'
def snapshot(path,code):
 bpy.ops.wm.open_mainfile(filepath=str(path));root=bpy.data.objects[f'R21_{code}_MODEL'];out={}
 for o in root.children_recursive:
  if o.type!='MESH'or o.get('semanticRole')not in['building','roof','terrain','paving','rails']:continue
  payload={'v':[list(v.co)for v in o.data.vertices],'faces':[list(p.vertices)for p in o.data.polygons],'matrix':[list(r)for r in o.matrix_world],'materials':[]}
  for m in o.data.materials:
   p=m.node_tree.nodes.get('Principled BSDF');payload['materials'].append({'name':m.name,'baseColor':list(p.inputs['Base Color'].default_value),'roughness':p.inputs['Roughness'].default_value,'metallic':p.inputs['Metallic'].default_value,'alpha':p.inputs['Alpha'].default_value})
  out[o.name]=hashlib.sha256(json.dumps(payload,separators=(',',':')).encode()).hexdigest()
 return out
rows={}
for c in'BDEH':
 before=snapshot(D/f'final-qa-baseline/docs/design/bdeh-r21/{c}/{c}-r21.blend',c);after=snapshot(D/f'{c}/{c}-r21.blend',c)
 assert before==after,('Approved structure changed',c,[k for k in before if before[k]!=after.get(k)])
 rows[c]={'currentBlendSHA256':hashlib.sha256((D/f'{c}/{c}-r21.blend').read_bytes()).hexdigest(),'unchangedStructuralObjects':len(before),'exactGeometryTransformsAndPBRMaterials':True,'objectHashes':before}
(O/'architecture-preserved.json').write_text(json.dumps({'baseCommit':'39f41940fd3af0f432b477ebd36ad5b677a71db1','method':'Read actual saved Blender mesh vertices/faces/matrices/PBR values in both files; no model writes','islands':rows},indent=2)+'\n');print('All four original building/roof/terrain/paving/rail Blender objects and materials remain exact')
