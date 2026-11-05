"""MIT. R21 original named geometry -> real editable Blender + batched game GLB.
Stage2 opens the stage1 .blend and retains every unchanged native mesh object.
Use --stage1 --render, or --render [--code B] for the refined source asset.
"""
import bpy,json,sys,hashlib,time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent));from flood_export import export_batched
stage=1 if '--stage1'in sys.argv else 2;codes=[sys.argv[sys.argv.index('--code')+1]]if '--code'in sys.argv else list('BDEH')
for code in codes:
 P=json.loads((R/f'work/bdeh/{code}-parts.json').read_text());assert P['stage']==stage
 D=R/f'docs/design/bdeh-r21/{code}';O=R/f'docs/previews/bdeh-r21/{code}';D.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
 media=O/('iteration-1/blender'if stage==1 else'blender');media.mkdir(parents=True,exist_ok=True)
 first=D/f'iteration-1/{code}-r21.blend';dest=first if stage==1 else D/f'{code}-r21.blend';dest.parent.mkdir(exist_ok=True)
 if stage==2:bpy.ops.wm.open_mainfile(filepath=str(first));root=bpy.data.objects[f'R21_{code}_MODEL']
 else:
  bpy.ops.wm.read_factory_settings(use_empty=True);root=bpy.data.objects.new(f'R21_{code}_MODEL',None);bpy.context.scene.collection.objects.link(root)
 s=bpy.context.scene;s.unit_settings.system='METRIC';bpy.context.preferences.filepaths.save_version=0
 groups={o.name.removeprefix('ROLE_'):o for o in root.children};roles=['terrain','paving','building','roof','rails','landscape']
 for role in roles:
  if role not in groups:
   o=bpy.data.objects.new('ROLE_'+role,None);s.collection.objects.link(o);o.parent=root;groups[role]=o
 glass={'careGlass','civicGlass','mistglass','eduGlass','blueglass','glass2','darkglass','deepglass'};materials={}
 for key,color in P['materials'].items():
  m=bpy.data.materials.get(key)or bpy.data.materials.new(key);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');m.diffuse_color=(*color,1);b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=.73
  if key in glass:
   alpha=.52 if stage==1 else .27;m.diffuse_color=(*color,alpha);b.inputs['Base Color'].default_value=(*color,alpha);b.inputs['Alpha'].default_value=alpha;b.inputs['Roughness'].default_value=.19;b.inputs['Metallic'].default_value=.04;m.surface_render_method='DITHERED';m.use_transparency_overlap=False
  elif any(t in key.lower()for t in ['steel','metal','sky','blue','copperdark']):b.inputs['Metallic'].default_value=.28;b.inputs['Roughness'].default_value=.39
  elif 'water'in key.lower():b.inputs['Roughness'].default_value=.25;b.inputs['Metallic'].default_value=.08
  materials[key]=m
 old={o.name:o for o in root.children_recursive if o.type=='MESH'};wanted=set();retained=0;created=0
 for part in P['parts']:
  name=part['name'];wanted.add(name);signature=hashlib.sha256(json.dumps([part['vertices'],part['faces']],separators=(',',':')).encode()).hexdigest();o=old.get(name)
  if o and o.get('geometrySHA256')==signature:retained+=1;continue
  if o:
   mesh=o.data;bpy.data.objects.remove(o,do_unlink=True);bpy.data.meshes.remove(mesh)
  mesh=bpy.data.meshes.new(name);mesh.from_pydata([(x,-z,y)for x,y,z in part['vertices']],[],part['faces']);mesh.materials.append(materials[part['material']]);mesh.update();o=bpy.data.objects.new(name,mesh);s.collection.objects.link(o);o.parent=groups[part['role']];o['geometrySHA256']=signature;o['sourceComponent']=part['sourceName'];o['semanticRole']=part['role'];o['source']='User R21 build_r21.py plus documented game/site and stage2 refinements'
  if part['role']=='roof'and len(mesh.polygons)>200:
   for face in mesh.polygons:face.use_smooth=True
  if stage==2 and len(part['vertices'])==8 and part['material']not in glass and part['role']not in ['terrain','paving']:
   bevel=o.modifiers.new('Fine fabricated arris','BEVEL');bevel.width=.012;bevel.segments=1;o.modifiers.new('Fabricated face normals','WEIGHTED_NORMAL')
  created+=1
 for name,o in old.items():
  if name not in wanted:mesh=o.data;bpy.data.objects.remove(o,do_unlink=True);bpy.data.meshes.remove(mesh)
 # Add small bevels to retained boxes too; geometry object stays independently editable.
 if stage==2:
  for o in root.children_recursive:
   if o.type=='MESH'and len(o.data.vertices)==8 and o.get('semanticRole')not in ['terrain','paving']and o.data.materials[0].name not in glass and not o.modifiers:
    bevel=o.modifiers.new('Fine fabricated arris','BEVEL');bevel.width=.012;bevel.segments=1;o.modifiers.new('Fabricated face normals','WEIGHTED_NORMAL')
 s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16 if stage==1 else 64;s.cycles.use_denoising=False;s.render.resolution_x=800;s.render.resolution_y=600;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.exposure=.6
 if stage==1:
  s.world=bpy.data.worlds.new('Soft shared studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.62,.68,.72,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.45
  for name,pos,energy,size in [('Key',(-22,-25,35),3200,20),('Fill',(25,-13,24),2300,18),('Rim',(0,25,30),2600,16)]:
   light=bpy.data.lights.new(name,'AREA');light.energy=energy;light.shape='DISK';light.size=size;o=bpy.data.objects.new(name,light);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
  views={'hero':([36,30,-42],[0,1.4,0],45),'front':([0,13,-60],[0,1,0],39),'back':([0,13,60],[0,1,0],39),'left':([-60,13,0],[0,1,0],39),'right':([60,13,0],[0,1,0],39),'top':([.001,80,.001],[0,0,0],43),'architecture':([26,13,-24],[0,3,0],29),'public-space':([-22,12,-25],[0,1,0],33)}
  for name,(pos,target,scale)in views.items():
   camera=bpy.data.objects.new('VIEW_'+name,bpy.data.cameras.new('VIEW_'+name));s.collection.objects.link(camera);camera.location=(pos[0],-pos[2],pos[1]);camera.rotation_euler=(Vector((target[0],-target[2],target[1]))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=scale
 s.camera=bpy.data.objects['VIEW_hero'];bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
 runtime=R/f'public/models/bdeh-r21/{code}.glb';runtime.parent.mkdir(parents=True,exist_ok=True);report=export_batched(root,runtime,f'R21_{code}_PolicyPlace',f'{code} policy island; user R21 refined Blender source, semantic batches')
 report.update({'code':code,'stage':stage,'sourceObjectsRetained':retained,'newOrChangedObjects':created,'partsSHA256':hashlib.sha256((R/f'work/bdeh/{code}-parts.json').read_bytes()).hexdigest(),'sourceBlend':str(dest.relative_to(R)),'sourceBlendSHA256':hashlib.sha256(dest.read_bytes()).hexdigest(),'GLBSHA256':hashlib.sha256(runtime.read_bytes()).hexdigest(),'glbBytes':runtime.stat().st_size,'blendBytes':dest.stat().st_size,'scale':1,'newLights':0,'materials':len({m.name for o in root.children_recursive if o.type=='MESH'for m in o.data.materials})})
 reportPath=D/('iteration-1/model-report.json'if stage==1 else'model-report.json');reportPath.write_text(json.dumps(report,indent=2)+'\n')
 records=[]
 if '--render'in sys.argv:
  for name in (['hero']if stage==1 else['hero','front','back','left','right','top','architecture','public-space']):
   s.camera=bpy.data.objects['VIEW_'+name];s.render.filepath=str(media/(name+'.png'));begin=time.monotonic();bpy.ops.render.render(write_still=True);records.append({'name':name,'cameraBlender':list(s.camera.location),'rotation':list(s.camera.rotation_euler),'orthoScale':s.camera.data.ortho_scale,'size':[800,600],'seconds':time.monotonic()-begin});(media/'render-record.json').write_text(json.dumps({'stage':stage,'sameSource':True,'sourceBlendSHA256':report['sourceBlendSHA256'],'engine':'Cycles CPU','samples':s.cycles.samples,'records':records},indent=2)+'\n')
 print(code,'editable .blend + actual GLB',report['triangles'],'triangles;',report['meshPrimitives'],'batches;',retained,'native objects retained',flush=True)
