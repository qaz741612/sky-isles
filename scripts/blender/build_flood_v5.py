"""MIT. Editable G V5 architecture from traceable parts; same .blend renders and GLB.
Run prepared site/parts, then Blender --python this_file -- --render [--pass1].
"""
import bpy,json,sys,math,hashlib,time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent));from flood_export import export_batched
P=json.loads((R/'work/g-v5/parts.json').read_text());PASS1=P['pass']==1;D=R/'docs/design/flood-control-island-g-v5';O=R/'docs/previews/flood-control-island-g-v5';MEDIA=O/('iteration-1/blender'if PASS1 else'blender');MEDIA.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC'
root=bpy.data.objects.new('FloodG_V5_MODEL',None);s.collection.objects.link(root);groups={}
role_names={'terrain':'Terrain_Foundation','gate':'Triple_Sluice_Mechanics','command':'Command_Centre','observation':'Observation_Room','crossing':'S22_Crossing','water':'Hydraulic_Water','rails':'Walkways_Railings','landscape':'Riparian_Landscape','interior':'Visible_Interior','props':'Civic_Props'}
for role,name in role_names.items():o=bpy.data.objects.new(name,None);s.collection.objects.link(o);o.parent=root;groups[role]=o
aliases={'steel_dark':'steel','leaf4':'leaf2','rock2':'rock','green_dark':'leaf1','white':'concrete2','turf':'green'}
materials={}
for key,color in P['materials'].items():
 actual=aliases.get(key,key)
 if actual in materials:materials[key]=materials[actual];continue
 m=bpy.data.materials.new(actual);m.diffuse_color=(*P['materials'].get(actual,color),1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=m.diffuse_color;b.inputs['Roughness'].default_value=.65
 if actual in ['steel','steel_lite','glass_dark','bronze','gold']:b.inputs['Metallic'].default_value=.35;b.inputs['Roughness'].default_value=.36
 if actual in ['glass','glass2']:
  alpha=.64 if PASS1 else .32;m.diffuse_color=(*color,alpha);b.inputs['Base Color'].default_value=(*color,alpha);b.inputs['Alpha'].default_value=alpha;b.inputs['Roughness'].default_value=.22;m.surface_render_method='DITHERED';m.use_transparency_overlap=False
 if actual.startswith('water')or actual=='ripple':b.inputs['Metallic'].default_value=.1;b.inputs['Roughness'].default_value=.21
 if actual=='foam':b.inputs['Emission Color'].default_value=(*color,1);b.inputs['Emission Strength'].default_value=.12
 materials[key]=m;materials[actual]=m
for idx,p in enumerate(P['parts']):
 mesh=bpy.data.meshes.new(p['name']);verts=[(v[0],-v[2],v[1])for v in p['vertices']];mesh.from_pydata(verts,[],p['faces']);mesh.update();o=bpy.data.objects.new(f'{idx:04d}_{p["name"]}',mesh);s.collection.objects.link(o);o.parent=groups[p['role']];mesh.materials.append(materials[p['mat']]);o['semanticRole']=p['role'];o['sourceComponent']=p['name'];o['solid']=p['solid'];o['floor']=p.get('ground',False);o['roofSupport']=p['roof'];o['source']='V5 architectural source + PR17-derived authored site'
 if len(p['vertices'])==8 and p['mat']not in ['glass','glass2','water_upper','water_lower','foam']:
  bevel=o.modifiers.new('Fabricated edge thickness','BEVEL');bevel.width=.015 if PASS1 else .025;bevel.segments=1 if PASS1 else 2
  o.modifiers.new('Area weighted fabricated normals','WEIGHTED_NORMAL')
# Saved source contains all editable components, not a flattened imported study GLB.
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16 if PASS1 else 32;s.cycles.use_denoising=False;s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Warm studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.62,.68,.72,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.45;s.view_settings.view_transform='AgX';s.view_settings.exposure=.65
for name,pos,energy,size in [('Key',(-22,-25,35),3200,20),('Fill',(25,-13,24),2300,18),('Rim',(0,25,30),2600,16)]:
 light=bpy.data.lights.new(name,'AREA');light.energy=energy;light.shape='DISK';light.size=size;o=bpy.data.objects.new(name,light);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
views={'hero':([-39,32,43],[0,1,0],55),'front':([0,8,-65],[0,1,0],47),'back':([0,8,65],[0,1,0],47),'left':([-65,8,0],[0,1,0],47),'right':([65,8,0],[0,1,0],47),'top':([.001,70,0],[0,0,0],47),'near-dam':([-27,16,-27],[-9.35,3.8,6.1],20),'near-command':([27,14,-24],[9,2.5,4.0],23),'s22-crossing':([-25,13,-20],[-9.7,.2,-3.4],25)}
for name,(pos,target,scale)in views.items():
 camera=bpy.data.objects.new('VIEW_'+name,bpy.data.cameras.new('VIEW_'+name));s.collection.objects.link(camera);camera.location=(pos[0],-pos[2],pos[1]);t=Vector((target[0],-target[2],target[1]));camera.rotation_euler=(t-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=scale
s.camera=bpy.data.objects['VIEW_hero'];bpy.ops.wm.save_as_mainfile(filepath=str(D/'flood-control-g-v5.blend'),compress=True)
runtime=R/'public/models/flood-control-g/flood-control-g.glb';report=export_batched(root,runtime)
report.update({'version':'G-V5','pass':P['pass'],'materials':len({m.name for o in root.children_recursive if o.type=='MESH'for m in o.data.materials}),'textures':0,'scale':1,'glbBytes':runtime.stat().st_size,'blendBytes':(D/'flood-control-g-v5.blend').stat().st_size,'sourceBlendSHA256':hashlib.sha256((D/'flood-control-g-v5.blend').read_bytes()).hexdigest(),'waterIsCollider':False,'upperWaterY':-.66,'lowerWaterY':-1.8,'newRoadLights':0,'renderEngine':'Cycles CPU, AgX','renderSamples':s.cycles.samples})
(D/'model-report.json').write_text(json.dumps(report,indent=2)+'\n')
records=[]
if '--render'in sys.argv:
 for name in views:
  if PASS1 and name not in ['hero','front','back','left','right','top','near-dam','near-command']:continue
  s.camera=bpy.data.objects['VIEW_'+name];s.render.filepath=str(MEDIA/(name+'.png'));begin=time.monotonic();bpy.ops.render.render(write_still=True);records.append({'name':name,'sourceBlendSHA256':report['sourceBlendSHA256'],'cameraGame':views[name][0],'targetGame':views[name][1],'orthoScale':views[name][2],'size':[1000,800],'seconds':time.monotonic()-begin})
  (MEDIA/'render-record.json').write_text(json.dumps({'sameSource':True,'pass':P['pass'],'engine':'Blender Cycles CPU','records':records},indent=2)+'\n')
print('G V5 actual Blender saved/exported:',report['triangles'],'triangles,',report['meshPrimitives'],'runtime batches')
