"""Evaluated GLB batching adapted from the project's MIT parent_child_export utility.
Separate source BLEND objects stay editable. No decimation, cameras or studio exported.
"""
import bpy

def export(model,path,key):
 scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();batches={};mesh_count=0
 for o in model.children_recursive:
  if o.type!='MESH':continue
  mesh_count+=1;chain=[];p=o
  while p and p!=model:chain.append(p);p=p.parent
  chain.reverse();role=chain[0].name
  # Retain building/vehicle assembly boundaries, merge repeated small garden components.
  assembly=chain[1].name if role in ['Architecture','ThemeFacilities']and len(chain)>2 and chain[1].type=='EMPTY'else role+'_Components'
  # A future moving train must remain separate from the fixed track/platform.
  if any(v.name.startswith('TrainRollingStock')for v in chain):assembly='TrainRollingStock'
  e=o.evaluated_get(deps);g=e.to_mesh();g.calc_loop_triangles();normal=o.matrix_world.to_3x3().inverted().transposed()
  for t in g.loop_triangles:
   mat=g.materials[t.material_index];b=batches.setdefault((role,assembly,mat.name),{'material':mat,'vertices':[],'normals':[],'faces':[],'index':{}});face=[]
   for li in t.loops:
    p=o.matrix_world@g.vertices[g.loops[li].vertex_index].co;n=(normal@g.corner_normals[li].vector).normalized();signature=tuple(round(v,6)for v in p)+tuple(round(v,6)for v in n)
    if signature not in b['index']:b['index'][signature]=len(b['vertices']);b['vertices'].append(tuple(p));b['normals'].append(tuple(n))
    face.append(b['index'][signature])
   if len(set(face))==3:b['faces'].append(tuple(face))
  e.to_mesh_clear()
 col=bpy.data.collections.new('TEMP_GLTF_EXPORT');scene.collection.children.link(col);created=[]
 def empty(n,parent=None):
  o=bpy.data.objects.new(n,None);col.objects.link(o);o.parent=parent;created.append(o);return o
 root=empty(key+'_Asset');root['role']='Standalone policy vision artwork, not integrated or approved engineering';root['source_reference']=model.get('source_reference','');roles={};assemblies={}
 for(role,assembly,name),b in batches.items():
  if role not in roles:roles[role]=empty(role,root)
  if(role,assembly)not in assemblies:assemblies[(role,assembly)]=empty(assembly,roles[role])
  g=bpy.data.meshes.new(assembly+'__'+name);g.from_pydata(b['vertices'],[],b['faces']);g.materials.append(b['material']);g.update()
  for f in g.polygons:f.use_smooth=True
  g.normals_split_custom_set_from_vertices(b['normals']);o=bpy.data.objects.new(g.name,g);col.objects.link(o);o.parent=assemblies[(role,assembly)];created.append(o)
 for o in model.children_recursive:
  if o.type=='EMPTY'and o.name.startswith('NPC_RESERVED'):
   reserve=empty('NPC_RESERVED_NO_MODEL',root);reserve.matrix_world=o.matrix_world.copy()
   for k in o.keys():reserve[k]=o[k]
 bpy.ops.object.select_all(action='DESELECT')
 for o in created:o.select_set(True)
 bpy.context.view_layer.objects.active=root
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_extras=True,export_cameras=False,export_lights=False,export_apply=False)
 report={'sourceMeshObjects':mesh_count,'meshPrimitives':len(batches),'assemblyGroups':len(assemblies),'triangles':sum(len(b['faces'])for b in batches.values()),'textures':0,'method':'Evaluated original geometry batched per semantic assembly and material; corner normals preserved; original BLEND objects remain separate; no polygon decimation.'}
 for o in reversed(created):
  g=o.data if o.type=='MESH'else None;bpy.data.objects.remove(o,do_unlink=True)
  if g:bpy.data.meshes.remove(g)
 bpy.data.collections.remove(col);return report
