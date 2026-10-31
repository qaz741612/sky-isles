"""Create editable Blender refinement from imported user V2.2, not a new design.
Precondition: scripts/industry/prepare_c.py --refine has produced editable parts.
Blender -b -t 4 --python scripts/blender/build_industry_c.py [-- --render].
"""
import bpy, bmesh, json, math, sys, hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
V3='--v3'in sys.argv
PASS1='--pass1'in sys.argv
OUT=ROOT/('docs/design/industry-youth-island-c-v3'if V3 else'docs/design/industry-youth-island-c-v2.2')
MEDIA=ROOT/('docs/previews/industry-youth-island-c-v3/'+('iteration-1/blender'if PASS1 else'blender')if V3 else'docs/previews/industry-youth-island-c-v1/blender')
OUT.mkdir(parents=True,exist_ok=True);MEDIA.mkdir(parents=True,exist_ok=True)
PACKAGE=ROOT/'docs/design/industry-youth-island-c-v2.2/source-package/C_產業青年_V2.2'
if V3:
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'docs/design/industry-youth-island-c-v2.2/industry-youth-c.blend'))
    for name in ['EDITABLE_COMPONENTS','EXPORT_AND_RENDER','LOCKED_V2.2_IMPORTED_REFERENCE']:
        c=bpy.data.collections.get(name)
        if c:c.name='ARCHIVE_V2_'+name;c.hide_render=True;c.hide_viewport=True
    for o in list(bpy.context.scene.objects):
        if o.type in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
else:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(PACKAGE/'C_IndustryYouth_V2_RuntimeAssetCandidate.glb'))
    baseline=list(bpy.context.scene.objects)
    reference=bpy.data.collections.new('LOCKED_V2.2_IMPORTED_REFERENCE');bpy.context.scene.collection.children.link(reference)
    for o in baseline:
        for c in list(o.users_collection):c.objects.unlink(o)
        reference.objects.link(o)
    reference.hide_render=True;reference.hide_viewport=True

data=json.loads((ROOT/'work/industry-editable-parts.json').read_text())
editable=bpy.data.collections.new('EDITABLE_COMPONENTS');bpy.context.scene.collection.children.link(editable)
display=bpy.data.collections.new('EXPORT_AND_RENDER');bpy.context.scene.collection.children.link(display)
materials={}
def linear(c):
    c=c/255;return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
for name,col in data['colours'].items():
    m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF')
    color=(*[linear(c)for c in col[:3]],1);p.inputs['Base Color'].default_value=color
    p.inputs['Roughness'].default_value=.72
    if name in ['steel','steel_light','roof']:p.inputs['Metallic'].default_value=.55;p.inputs['Roughness'].default_value=.36
    if name.startswith('glass'):
        p.inputs['Alpha'].default_value=(col[3]/255 if len(col)>3 else .35)
        p.inputs['Roughness'].default_value=.16;m.surface_render_method='DITHERED'
    if name in ['wood','woodlight']:p.inputs['Roughness'].default_value=.52
    if name=='light':p.inputs['Emission Color'].default_value=(1,.7,.35,1);p.inputs['Emission Strength'].default_value=.6
    m.diffuse_color=color;materials[name]=m

def area(name):
    if name.startswith(('factory','sawtooth','roof-','clerestory','PV-','canopy-ribs','side-','rear-','cantilever','entry-','workshop','machine','interior-')):return '01_Workshop'
    if name.startswith(('greenhouse','curved-glass','lettuce','leaflet')):return '02_Greenhouse'
    if name.startswith(('exhibit','pavilion','abstract','bronze')):return '03_Exhibition'
    if any(s in name for s in ['rock','cliff','turf','grass','plaza','public-path','structural-core']):return '00_TerrainAndPlaza'
    return '04_GardensAndFurniture'

buckets={}
for i,part in enumerate(data['parts']):
    mesh=bpy.data.meshes.new(part['name']);mesh.from_pydata([(x,-z,y)for x,y,z in part['vertices']],[],part['faces']);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    o=bpy.data.objects.new('%04d_%s'%(i,part['name']),mesh);editable.objects.link(o);o.data.materials.append(materials[part['material']]);o['sourceComponent']=part['name'];o['sourcePackage']='User V3 architecture / retained PR17 site'if V3 else'User V2.2';o['semanticArea']=area(part['name'])
    if any(s in part['name'] for s in ['podium','canopy','frame','wall','pier','plinth','bench','workbench','door']) and len(part['faces'])<=36:
        mod=o.modifiers.new('Small real edge bevel','BEVEL');mod.width=.012;mod.segments=1
    buckets.setdefault((area(part['name']),part['material']),[]).append(o)

# Make a material-batched display from evaluated editable geometry. Both images
# and GLB use this exact display; editable originals stay in the .blend.
deps=bpy.context.evaluated_depsgraph_get()
for (group,mat),objects in buckets.items():
    verts=[];faces=[]
    for o in objects:
        ev=o.evaluated_get(deps);m=ev.to_mesh();off=len(verts);verts.extend(tuple(v.co)for v in m.vertices);faces.extend(tuple(off+i for i in p.vertices)for p in m.polygons);ev.to_mesh_clear()
    m=bpy.data.meshes.new(group+'_'+mat);m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new(group+'_'+mat,m);display.objects.link(o);m.materials.append(materials[mat]);o['sourceArea']=group
editable.hide_render=True;editable.hide_viewport=True

# Real small readable architectural identifiers, with geometric thickness.
labels=[('YUANLI MAKERS',(4.00,-.25,2.81),.19,-math.pi/2),('GROW / SHARE',(3.99,-7.04,2.56),.14,-math.pi/2)]
if V3:labels=[('YUANLI MAKERS',(4.54,1.09,4.11),.20,-math.pi/2),('YOUTH WORKS',(-6.01,.55,4.52),.20,math.pi/2),('GROW',(6.0,-9.36,2.64),.19,0)]
for label,position,size,rotation in labels:
    curve=bpy.data.curves.new(label,'FONT');curve.body=label;curve.align_x='CENTER';curve.size=size;curve.extrude=.004
    o=bpy.data.objects.new(label,curve);display.objects.link(o);o.location=position;o.rotation_euler=(math.pi/2,0,rotation);o.data.materials.append(materials['cream'])
    bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)

scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=(16 if PASS1 else 32)if V3 else 48;scene.cycles.use_denoising=False
scene.render.resolution_x=1000 if V3 else 1200;scene.render.resolution_y=800 if V3 else 960;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Warm studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.62,.68,.72,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.65
for name,pos,energy,size in [('Key',(-15,-18,28),2200,16),('Fill',(16,-8,18),1500,14),('Rim',(0,15,24),1900,12)]:
    l=bpy.data.lights.new(name,'AREA');l.energy=energy;l.shape='DISK';l.size=size;o=bpy.data.objects.new(name,l);scene.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO';cam.data.lens=45
views={'hero':(-32,36,29),'front':(0,-45,5),'back':(0,45,5),'left':(-45,0,5),'right':(45,0,5),'top':(0,0,55),'workshop-detail':(-7,-14,10),'greenhouse-detail':(1,-15,9)}
if V3:views.update({'hero':(-32,36,29)if PASS1 else(32,-36,29),'workshop-detail':(20,16,12),'youth-detail':(2,-12,9)})
def view(name):
    target=Vector((0,0,-.6));scale=37
    if name=='workshop-detail':target=Vector((8.1,-.7,2.0));scale=13
    if name=='greenhouse-detail':target=Vector((7,-7.1,1.6));scale=10
    if V3 and name=='workshop-detail':target=Vector((9.0,-.7,3));scale=13
    if name=='youth-detail':target=Vector((-9.6,-1.1,2.6));scale=13
    cam.location=views[name];cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
view('hero')
# Export selected display only. The studio, editable/reference archives do not
# become a second runtime scene or unwanted lights/cameras.
bpy.ops.object.select_all(action='DESELECT')
for o in display.objects:o.select_set(True)
glb=ROOT/'public/models/industry-youth-c/industry-youth-c.glb'
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False,export_yup=True,export_materials='EXPORT')
blend=OUT/('industry-youth-c-v3.blend'if V3 else'industry-youth-c.blend');bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=V3)
triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons)for o in display.objects if o.type=='MESH')
allv=[o.matrix_world@v.co for o in display.objects if o.type=='MESH'for v in o.data.vertices]
report={'version':'C-V3'if V3 else'C-V2.2','editableObjects':len(editable.objects),'runtimeMeshes':len(display.objects),'triangles':triangles,'materials':len({m.name for o in display.objects if o.type=='MESH'for m in o.data.materials}),'textures':0,'boundsBlender':[[min(v[i]for v in allv)for i in range(3)],[max(v[i]for v in allv)for i in range(3)]],'blendBytes':blend.stat().st_size,'glbBytes':glb.stat().st_size,'refinement':'V3 workshop / enclosed youth centre / curved greenhouse on unchanged original PR17 terrain'if V3 else'Original V2.2 components, actual workshop wall shell/interior, subtle edge bevels, clear tinted glass, material batches; no route or other asset edits','closedInteriors':['workshop','greenhouse','youth']if V3 else['workshop','greenhouse'],'renderer':'Blender Cycles CPU, %d samples, AgX'%scene.cycles.samples}
(OUT/'model-report.json').write_text(json.dumps(report,indent=2)+'\n')
if '--render' in sys.argv:
    records=[]
    for name in views:
        if PASS1 and name not in ['hero','front','back','left','right','top']:continue
        view(name);scene.render.filepath=str(MEDIA/(name+'.png'));bpy.ops.render.render(write_still=True);records.append({'name':name,'camera':list(cam.location),'rotation':list(cam.rotation_euler),'orthoScale':cam.data.ortho_scale,'size':[scene.render.resolution_x,scene.render.resolution_y]})
    (MEDIA/'render-record.json').write_text(json.dumps({'blendSHA256':hashlib.sha256(blend.read_bytes()).hexdigest(),'sameSource':True,'views':records},indent=2)+'\n')
print('C editable Blender / GLB saved:',triangles,'triangles',len(display.objects),'batches')
