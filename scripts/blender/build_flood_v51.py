"""Refine the saved approved V5 .blend in place, preserving unchanged objects.
Only removed/changed geometry is replaced. No model reconstruction from a proxy.
"""
import bpy,json,sys,hashlib,collections,time
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent));from flood_export import export_batched
D=R/'docs/design/flood-control-island-g-v5-1';W=R/'work/g-v51';P=json.loads((W/'parts.json').read_text());source=R/'docs/design/flood-control-island-g-v5/flood-control-g-v5.blend';bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;root=bpy.data.objects['FloodG_V5_MODEL'];root.name='FloodG_V51_MODEL';groups={o.name:o for o in root.children};role_names={'terrain':'Terrain_Foundation','gate':'Triple_Sluice_Mechanics','command':'Command_Centre','observation':'Observation_Room','crossing':'S22_Crossing','water':'Hydraulic_Water','rails':'Walkways_Railings','landscape':'Riparian_Landscape','interior':'Visible_Interior','props':'Civic_Props'};roles={r:groups[n]for r,n in role_names.items()}
aliases={'steel_dark':'steel','leaf4':'leaf2','rock2':'rock','green_dark':'leaf1','white':'concrete2','turf':'green'};materials={}
for key,color in P['materials'].items():
 actual=aliases.get(key,key)
 if actual in materials:materials[key]=materials[actual];continue
 m=bpy.data.materials.get(actual)or bpy.data.materials.new(actual);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');col=P['materials'].get(actual,color);m.diffuse_color=(*col,1);b.inputs['Base Color'].default_value=(*col,1);b.inputs['Roughness'].default_value=.69
 if actual in ['steel','steel_lite','glass_dark','bronze','gold']:b.inputs['Metallic'].default_value=.35;b.inputs['Roughness'].default_value=.36
 if actual in ['glass','glass2']:
  m.diffuse_color=(*col,.28);b.inputs['Base Color'].default_value=(*col,.28);b.inputs['Alpha'].default_value=.28;b.inputs['Roughness'].default_value=.18;m.surface_render_method='DITHERED';m.use_transparency_overlap=False
 if actual.startswith('water')or actual=='ripple':b.inputs['Metallic'].default_value=.1;b.inputs['Roughness'].default_value=.25
 if actual=='foam':b.inputs['Emission Color'].default_value=(*col,1);b.inputs['Emission Strength'].default_value=.10
 materials[key]=m;materials[actual]=m
old=[o for o in root.children_recursive if o.type=='MESH'];lookup=collections.defaultdict(list)
def signature(name,verts,faces):
 a=np.asarray(verts);return(name,len(verts),faces,tuple(np.round(a.min(axis=0),4)),tuple(np.round(a.max(axis=0),4)))
for o in old:
 v=[list(x.co)for x in o.data.vertices];lookup[signature(o.get('sourceComponent',''),v,len(o.data.polygons))].append(o)
used=set();retained=0;new=0
for idx,p in enumerate(P['parts']):
 verts=[(v[0],-v[2],v[1])for v in p['vertices']];key=signature(p['name'],verts,len(p['faces']));pool=lookup.get(key,[]);o=pool.pop(0)if pool else None
 if o is not None:retained+=1
 else:
  mesh=bpy.data.meshes.new(p['name']);mesh.from_pydata(verts,[],p['faces']);mesh.update();o=bpy.data.objects.new('V51_'+str(idx)+'_'+p['name'],mesh);s.collection.objects.link(o);new+=1
  if len(p['vertices'])==8 and p['mat']not in ['glass','glass2','water_upper','water_lower','foam']:
   bevel=o.modifiers.new('Fabricated refined edges','BEVEL');bevel.width=min(.018,min(np.ptp(np.asarray(verts),axis=0))*.24);bevel.segments=1 if min(np.ptp(np.asarray(verts),axis=0))<.14 else 2;o.modifiers.new('Area weighted fabricated normals','WEIGHTED_NORMAL')
 o.parent=roles[p['role']];o.data.materials.clear();o.data.materials.append(materials[p['mat']]);o['sourceComponent']=p['name'];o['semanticRole']=p['role'];o['solid']=p['solid'];o['floor']=p.get('ground',False);o['roofSupport']=p['roof'];o['source']='Approved V5 editable objects + authored V5.1 refinements';used.add(o)
for o in old:
 if o not in used:bpy.data.objects.remove(o,do_unlink=True)
# Preserve original studio/light/world/profile for true matched-camera evidence.
s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=False;s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100;bpy.data.objects['VIEW_top'].data.ortho_scale=55
for name,pos,target,scale in [('downstream-detail',[-25,6,-11],[-9.35,-.4,5],19),('tower-detail',[23,13,-2],[12.7,6.8,6.2],12)]:
 o=bpy.data.objects.new('VIEW_'+name,bpy.data.cameras.new('VIEW_'+name));s.collection.objects.link(o);o.location=(pos[0],-pos[2],pos[1]);t=Vector((target[0],-target[2],target[1]));o.rotation_euler=(t-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=scale
s.camera=bpy.data.objects['VIEW_hero'];D.mkdir(exist_ok=True);dest=D/'flood-control-g-v5-1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
runtime=R/'public/models/flood-control-g/flood-control-g.glb';report=export_batched(root,runtime);report.update({'baseCommit':'8849b89e99163c179973a31571498115c6c80e7c','baseBlendSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'sourceBlendSHA256':hashlib.sha256(dest.read_bytes()).hexdigest(),'sourceBlend':str(dest.relative_to(R)),'version':'G-V5.1','unchangedEditableObjectsRetained':retained,'changedOrNewEditableObjects':new,'previousObjectsRemoved':len(old)-retained,'materials':len({m.name for o in root.children_recursive if o.type=='MESH'for m in o.data.materials}),'textures':0,'glbBytes':runtime.stat().st_size,'blendBytes':dest.stat().st_size,'authoredArtSHA256':hashlib.sha256((R/'src/data/flood-control-art.json').read_bytes()).hexdigest(),'partsSHA256':hashlib.sha256((W/'parts.json').read_bytes()).hexdigest(),'renderEngine':'Cycles CPU, unchanged studio, AgX','renderSamples':64,'waterIsCollider':False,'newRealtimeLights':0,'scale':1})
(D/'model-report.json').write_text(json.dumps(report,indent=2)+'\n');print('V5.1 editable saved:',retained,'V5 objects retained,',new,'refined/new;',report['triangles'],'triangles;',report['meshPrimitives'],'batches')
