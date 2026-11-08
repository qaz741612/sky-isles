"""Inspect real GLB buffers, normals, primitive costs and transformed bounds."""
from pathlib import Path
import json,struct
import numpy as np
import trimesh
R=Path(__file__).resolve().parents[2];O=R/'docs/previews/bdeh-r21/final-qa';plan=json.loads((R/'src/data/bdeh-plan.json').read_text());rows={}
def inspect(path):
 raw=path.read_bytes();magic,version,total=struct.unpack_from('<III',raw);assert magic==0x46546c67 and version==2 and total==len(raw)
 jlen,jtype=struct.unpack_from('<II',raw,12);assert jtype==0x4e4f534a;doc=json.loads(raw[20:20+jlen]);blen,btype=struct.unpack_from('<II',raw,20+jlen);assert btype==0x004e4942;binary=raw[28+jlen:28+jlen+blen]
 assert not any('uri'in b for b in doc['buffers'])and not doc.get('images'),str(path)+' missing/external texture dependency'
 def array(index):
  a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']];dtype=np.dtype({5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]);n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];offset=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',dtype.itemsize*n)
  return np.ndarray((a['count'],n),dtype=dtype,buffer=binary,offset=offset,strides=(stride,dtype.itemsize))
 prims=[p for m in doc['meshes']for p in m['primitives']];triangles=0;normalLengths=[]
 for p in prims:
  assert p.get('mode',4)==4;positions=array(p['attributes']['POSITION']);normals=array(p['attributes']['NORMAL']);indices=array(p['indices']).ravel();assert len(positions)==len(normals)and np.isfinite(positions).all()and np.isfinite(normals).all();assert indices.min()>=0 and indices.max()<len(positions)and len(indices)%3==0;assert p['material']<len(doc['materials'])
  lengths=np.linalg.norm(normals,axis=1);assert np.all((lengths>.99)&(lengths<1.01)),str(path)+' non-unit normals';normalLengths.extend([float(lengths.min()),float(lengths.max())]);triangles+=len(indices)//3
 scene=trimesh.load_scene(path);bounds=scene.bounds;assert np.isfinite(bounds).all();dims=bounds[1]-bounds[0]
 return{'path':str(path.relative_to(R)),'bytes':len(raw),'triangles':triangles,'meshPrimitives':len(prims),'materialDefinitions':len(doc['materials']),'transparentMaterials':sum(m.get('alphaMode','OPAQUE')=='BLEND'for m in doc['materials']),'textures':len(doc.get('textures',[])),'normalsUnitRange':[min(normalLengths),max(normalLengths)],'boundsYup':bounds.tolist(),'dimensionsXYZ':dims.tolist(),'buffersFiniteAndIndicesValid':True}
for code in'BDEH':
 before=inspect(R/f'docs/design/bdeh-r21/final-qa-baseline/public/models/bdeh-r21/{code}.glb');after=inspect(R/f'public/models/bdeh-r21/{code}.glb');assert np.allclose(np.array(before['boundsYup'])[:,[0,2]],np.array(after['boundsYup'])[:,[0,2]],atol=1e-5),'Unapproved isle/outer dimension change '+code
 assert after['transparentMaterials']==before['transparentMaterials'],'Extra transparent sorting cost '+code
 rows[code]={'fixedIslandXZ':plan['islands'][code]['maxDimensions'],'before':before,'after':after,'outerXZBoundsUnchanged':True}
(O/'glb-integrity-and-sizes.json').write_text(json.dumps({'method':'Read actual glTF binary accessor buffers, index ranges and unit normals; transformed GLB scene bounds via trimesh; no appearance edits or proxy boxes','islands':rows},indent=2)+'\n')
print('4 GLB buffers/materials/normals valid; outer XZ bounds exact; no added transparent materials')
