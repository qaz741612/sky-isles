"""Batch evaluated static GLB geometry by logical assembly/material.
The saved .blend retains the independent source objects and modifiers.
Baking preserves each evaluated corner normal, world position and original PBR material.
"""
import bpy
from mathutils import Vector

def export_batched(model,path):
    scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();groups={}
    def key(obj):
        chain=[];node=obj
        while node and node!=model:chain.append(node);node=node.parent
        chain.reverse();role=chain[0].name
        assembly=chain[1].name if len(chain)>2 and chain[1].type=='EMPTY' else role+'_Components'
        return role,assembly
    for obj in model.children_recursive:
        if obj.type!='MESH':continue
        role,assembly=key(obj);e=obj.evaluated_get(deps);mesh=e.to_mesh();mesh.calc_loop_triangles();matrix=obj.matrix_world;normal_matrix=matrix.to_3x3().inverted().transposed()
        for tri in mesh.loop_triangles:
            material=mesh.materials[tri.material_index];batch=groups.setdefault((role,assembly,material.name),{'mat':material,'verts':[],'normals':[],'faces':[],'map':{}});indices=[]
            for loop_index in tri.loops:
                loop=mesh.loops[loop_index];p=matrix@mesh.vertices[loop.vertex_index].co;n=(normal_matrix@mesh.corner_normals[loop_index].vector).normalized();vertex=tuple(round(v,6)for v in p)+tuple(round(v,6)for v in n)
                if vertex not in batch['map']:
                    batch['map'][vertex]=len(batch['verts']);batch['verts'].append(tuple(p));batch['normals'].append(tuple(n))
                indices.append(batch['map'][vertex])
            batch['faces'].append(tuple(indices))
        e.to_mesh_clear()
    collection=bpy.data.collections.new('TEMP_WEB_EXPORT');scene.collection.children.link(collection);created=[]
    def empty(name,parent=None):
        o=bpy.data.objects.new(name,None);collection.objects.link(o);created.append(o)
        if parent:o.parent=parent
        return o
    root=empty('FloodControlPark');root['role']='G island V1; grouped by assembly and material';parents={};triangles=0
    for(role,assembly,name),batch in groups.items():
        if role not in parents:parents[role]=empty(role,root)
        k=(role,assembly)
        if k not in parents:parents[k]=empty(assembly,parents[role])
        mesh=bpy.data.meshes.new(assembly+'__'+name);mesh.from_pydata(batch['verts'],[],batch['faces']);mesh.materials.append(batch['mat']);mesh.update()
        for poly in mesh.polygons:poly.use_smooth=True
        mesh.normals_split_custom_set_from_vertices(batch['normals'])
        obj=bpy.data.objects.new(assembly+'__'+name,mesh);collection.objects.link(obj);obj.parent=parents[k];created.append(obj);triangles+=len(batch['faces'])
    bpy.ops.object.select_all(action='DESELECT')
    for obj in created:obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=False,export_extras=True,export_cameras=False,export_lights=False)
    report={'method':'Original saved Blender source stays independent; web export batches evaluated surfaces per logical assembly and PBR material, preserving custom normals.','meshPrimitives':len(groups),'assemblyGroups':len({(r,a)for r,a,_ in groups}),'triangles':triangles,'originalSourceObjects':sum(o.type=='MESH'for o in model.children_recursive),'textures':0}
    for obj in reversed(created):
        mesh=obj.data if obj.type=='MESH'else None;bpy.data.objects.remove(obj,do_unlink=True)
        if mesh:bpy.data.meshes.remove(mesh)
    bpy.data.collections.remove(collection)
    return report
