"""Load the user's R21 geometry unchanged from a disposable, path-relocated copy.
Original ZIP contents remain immutable; R18/R20 files are dependency engines,
never selected as replacement buildings. No rendering/import-time /mnt writes.
"""
from pathlib import Path
import importlib.util,shutil,hashlib,json
R=Path(__file__).resolve().parents[2];D=R/'docs/design/bdeh-r21';W=R/'work/bdeh';W.mkdir(parents=True,exist_ok=True)
def load_reference():
 src=D/'source-package';dst=W/'reference-runtime'
 for p in src.rglob('*'):
  if p.suffix not in ['.py','.json']:continue
  q=dst/p.relative_to(src);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
 p=dst/'base/BDEH_R18/source/vendor_base.py';s=p.read_text().replace("Path('/mnt/data/bdeh_redesign')",'Path(__file__).resolve().parents[1]');p.write_text(s)
 spec=importlib.util.spec_from_file_location('approved_r21',dst/'build_r21.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 # Named independently editable meshes survive source routines that prune parts.
 original=m.Design.add;old_tree=m.Design.tree
 def add(self,name,mesh,color):
  original(self,name,mesh,color)
  if mesh is not None and hasattr(mesh,'faces')and len(mesh.faces):
   if not hasattr(self,'named'):self.named=[]
   self.named.append({'name':name,'mesh':mesh,'material':color,'tree':getattr(self,'tree_origin',None),'garden':getattr(self,'garden_origin',None)})
 def tree(self,x,z,size=1,kind='olive'):
  self.tree_origin=[float(x),float(z),float(size),kind]
  try:return old_tree(self,x,z,size,kind)
  finally:self.tree_origin=None
 old_garden=m.garden
 def garden(s,name,x,z,w,d,kind='ecoLeaf'):
  s.garden_origin=[float(x),float(z),name]
  try:return old_garden(s,name,x,z,w,d,kind)
  finally:s.garden_origin=None
 m.garden=garden
 m.Design.add=add;m.Design.tree=tree
 return m
