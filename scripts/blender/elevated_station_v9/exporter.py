"""Batched GLB with preserved UVs/normals; source objects stay editable. MIT."""
import bpy

def export(model,path,candidate=False):
 deps=bpy.context.evaluated_depsgraph_get();batches={};skipped=0
 for o in model.children_recursive:
  if o.type!='MESH':continue
  if candidate and o.get('candidateDetail',0):skipped+=1;continue
  chain=[];p=o
  while p and p!=model:chain.append(p);p=p.parent
  chain.reverse();role=chain[0].name;assembly=chain[1].name if role=='TrainRollingStock'and len(chain)>2 and chain[1].type=='EMPTY'else role
  e=o.evaluated_get(deps);me=e.to_mesh();me.calc_loop_triangles();nm=o.matrix_world.to_3x3().inverted().transposed();uv=me.uv_layers.active
  for tri in me.loop_triangles:
   mat=me.materials[tri.material_index];b=batches.setdefault((role,assembly,mat.name),{'mat':mat,'verts':[],'normals':[],'uv':[],'faces':[],'index':{}});face=[]
   for li in tri.loops:
    v=o.matrix_world@me.vertices[me.loops[li].vertex_index].co;n=(nm@me.corner_normals[li].vector).normalized();t=tuple(uv.data[li].uv)if uv else(0,0);key=tuple(round(a,6)for a in v)+tuple(round(a,6)for a in n)+tuple(round(a,6)for a in t)
    if key not in b['index']:b['index'][key]=len(b['verts']);b['verts'].append(tuple(v));b['normals'].append(tuple(n));b['uv'].append(t)
    face.append(b['index'][key])
   if len(set(face))==3:b['faces'].append(tuple(face))
  e.to_mesh_clear()
 col=bpy.data.collections.new('EXPORT_TEMP');bpy.context.scene.collection.children.link(col);objects=[]
 def empty(n,parent=None):
  o=bpy.data.objects.new(n,None);col.objects.link(o);o.parent=parent;objects.append(o);return o
 root=empty('StationV9_GameCandidate'if candidate else'StationV9_Showcase');root['standalone']=True;root['not_game_integrated']=True;groups={}
 for (role,assembly,mat),b in batches.items():
  if(role,assembly)not in groups:groups[(role,assembly)]=empty(assembly,root)
  me=bpy.data.meshes.new(role+'_'+mat);me.from_pydata(b['verts'],[],b['faces']);me.materials.append(b['mat']);me.update()
  for f in me.polygons:f.use_smooth=True
  me.normals_split_custom_set_from_vertices(b['normals']);uv=me.uv_layers.new(name='ArchitecturalUV')
  for i,l in enumerate(me.loops):uv.data[i].uv=b['uv'][l.vertex_index]
  o=bpy.data.objects.new(me.name,me);col.objects.link(o);o.parent=groups[(role,assembly)];objects.append(o)
 for i,x in enumerate([-3.7,3.65]):
  r=empty('NPC_SPACE_ONLY_'+str(i),root);r.location=(x,-3.93,0);r['clearSquareMetres']=3;r['character_model']=False
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=root;bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_extras=True,export_cameras=False,export_lights=False,export_apply=False)
 result={'triangles':sum(len(b['faces'])for b in batches.values()),'meshPrimitives':len(batches),'materials':len(set(k[2]for k in batches)),'bytes':path.stat().st_size,'skippedMicroFoliageObjects':skipped,'UVandNormalsPreserved':True,'mode':'1-segment bevels and omit tagged microfoliage; same architecture/train/door positions'if candidate else'evaluated original source geometry'}
 for o in reversed(objects):
  me=o.data if o.type=='MESH'else None;bpy.data.objects.remove(o,do_unlink=True)
  if me:bpy.data.meshes.remove(me)
 bpy.data.collections.remove(col);return result
