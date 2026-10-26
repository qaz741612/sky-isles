"""Build one of seven standalone, editable policy assets from approved image references.
Run with isolated bpy Python or Blender: -- --island transport [--draft-render]. MIT.
"""
import sys,math,json,hashlib,time,os,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy,bmesh
from mathutils import Vector
from policy_assets.kit import Kit,ROOT,G,BASELINE
from policy_assets.recipes import RECIPES,finish_gardens
from policy_assets.exporter import export
p=argparse.ArgumentParser();p.add_argument('--island',required=True,choices=list(RECIPES));p.add_argument('--draft-render',action='store_true');args=p.parse_args(sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else sys.argv[1:])
OUT=ROOT/'docs/design/seven-policy-islands-blender-v1'/args.island;OUT.mkdir(parents=True,exist_ok=True);(OUT/'renders').mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();manifest=json.loads((ROOT/'docs/references/policy-islands/manifest.json').read_text());ref=next(e for e in manifest['entries']if e['id']==args.island)
assert sha(ROOT/ref['projectPath'])==ref['sha256'];assert sha(BASELINE)=='a5116f37b5c5fb9a3d8f4612d94094fc33680159b80ea1bd5fcf63fc8e5013c0'
script_sources={str(p.relative_to(ROOT)):sha(p)for p in [Path(__file__),*Path(__file__).parent.joinpath('policy_assets').glob('*.py')]};started=time.time();k=Kit(args.island);k.root['source_reference']=ref['projectPath'];k.root['reference_sha256']=ref['sha256'];RECIPES[args.island](k);finish_gardens(k,args.island);bpy.context.view_layer.update();radius=k.site();print('MODEL_GEOMETRY_BUILT',args.island,radius,flush=True)
# Exact evaluated counts and source bounds, excluding the separate render studio.
deps=bpy.context.evaluated_depsgraph_get();points=[];by_role={};solids=[];issues=[]
for o in k.root.children_recursive:
 if o.type!='MESH':continue
 e=o.evaluated_get(deps);g=e.to_mesh();g.calc_loop_triangles();pts=[o.matrix_world@v.co for v in g.vertices];points.extend(tuple(v)for v in pts);par=o
 while par.parent and par.parent!=k.root:par=par.parent
 bucket=by_role.setdefault(par.name,{'objects':0,'triangles':0});bucket['objects']+=1;bucket['triangles']+=len(g.loop_triangles)
 bm=bmesh.new();bm.from_mesh(g);opened=sum(not edge.is_manifold for edge in bm.edges);volume=bm.calc_volume(signed=True);bm.free()
 if opened or volume<=0:issues.append({'name':o.name,'nonManifoldEdges':opened,'signedLocalVolume':volume})
 if par.name not in ['Site','Interior']and min(p.z for p in pts)<1.6 and max(p.z for p in pts)>.23:
  from shapely.geometry import MultiPoint
  poly=MultiPoint([(p.x,p.y)for p in pts]).convex_hull
  if poly.geom_type=='Polygon':solids.append((o.name,poly))
 e.to_mesh_clear()
triangles=sum(v['triangles']for v in by_role.values());materials={s.material.name for o in k.root.children_recursive if o.type=='MESH'for s in o.material_slots if s.material};bounds={'min':[min(p[i]for p in points)for i in range(3)],'max':[max(p[i]for p in points)for i in range(3)]};dimensions=[bounds['max'][i]-bounds['min'][i]for i in range(3)]
from shapely.geometry import Point
npc=[]
for r in k.reservations:
 for kind,pt,rad in [('future_npc',r['positionBlenderXYZ'],.35),('player_stop',r['playerStopBlenderXYZ'],.33)]:
  capsule=Point(pt[0],pt[1]).buffer(rad);hits=[name for name,poly in solids if poly.intersection(capsule).area>.0001];npc.append({'kind':kind,'position':pt,'radius':rad,'intersectingObjects':hits})
report={'policyName':ref['policyName'],'id':args.island,'reference':ref['projectPath'],'referenceSHA256':ref['sha256'],'approvedBaselineSHA256':sha(BASELINE),'blenderVersion':bpy.app.version_string,'phase':'complete','role':'Standalone Blender/GLB asset only. No game integration or world-layout edit.','sourceScripts':script_sources,'blenderDimensionsOrder':'X width, Y depth, Z height; GLB uses X width, Y height, Z negative Blender-Y','bounds':bounds,'sizeXYZ':dimensions,'evaluatedTriangles':triangles,'meshObjects':sum(v['objects']for v in by_role.values()),'materials':sorted(materials),'materialCount':len(materials),'collections':by_role,'recommendedPlatform':{'shape':'circle','radius':radius,'derivedFromActualContentRadius':k.measured_content_radius,'minimumOuterClearance':1.0,'radiusOver12':radius>12,'reviewBridgeArmsExcludedFromRadiusMeasurement':True,'actualWorldNotChanged':True},'rooms':k.rooms,'npcReservations':k.reservations,'npcClearanceChecks':npc,'reviewConnections':k.ports,'geometryAudit':{'checkedMeshes':sum(v['objects']for v in by_role.values()),'issues':issues,'note':'Per-component closed solids; intentional assembly intersections are not boolean-unioned. Not an engineering or runtime collision certification.'},'complexityCap':{'baselineEvaluatedTriangles':381520,'baselineGLBTriangles':380999,'baselineMaterials':29,'trianglesWithinCap':triangles<=381520,'materialsWithinCap':len(materials)<=29}}
(OUT/'model-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
if triangles>381520 or len(materials)>29:raise RuntimeError('Asset exceeds approved baseline complexity cap')
if issues:raise RuntimeError('Repair non-solid source components: '+str(issues[:8]))
if any(r['intersectingObjects']for r in npc):raise RuntimeError('NPC reservation intersects model: '+str(npc))
# Studio and cameras: identical direction, projection and scale across all seven hero renders.
G.collection('90_STUDIO_NOT_EXPORTED');scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=64;scene.cycles.use_denoising=True;scene.cycles.adaptive_threshold=.04;scene.cycles.max_bounces=10;scene.cycles.transmission_bounces=8;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=3;scene.cycles.caustics_reflective=False;scene.cycles.caustics_refractive=False
scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=1280;scene.render.resolution_y=960;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8';scene.world=bpy.data.worlds.new('SoftStudioWorld');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.62,.66,.67,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.35
G.box('StudioGround',(0,0,-.60),(200,200,.12),k.M['gray'],r=0)
def light(n,pos,power,size,color,target):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(n,d);G.COL.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
light('LargeSoftbox',(-10,-12,18),2350,9,(1,.91,.78),(0,0,0));light('CoolFill',(12,-2,14),1050,8,(.82,.93,1),(0,1,1));light('RoofRim',(-2,11,15),1550,7,(1,.96,.87),(0,3,2))
for room in k.rooms:
 x0,y0,x1,y1=room['footprint']
 for fraction in ([.24,.5,.76]if x1-x0>6 else[.5]):
  x=x0+(x1-x0)*fraction;light('WarmInterior',(x,(y0+y1)/2,min(room.get('base',0)+3.1,room['peak']-.4)),110,1.5,(1,.83,.61),(x,(y0+y1)/2,room.get('base',0)+.2))
cameras={'hero':G.camera('01_Hero_CommonScale',(22,-30,24),(0,0,1),33.8),'front':G.camera('02_Front',(0,-38,8),(0,0,1),35),'back':G.camera('03_Back',(0,38,8),(0,0,1),35),'left':G.camera('04_Left',(-38,0,8),(0,0,1),35),'right':G.camera('05_Right',(38,0,8),(0,0,1),35),'top':G.camera('06_Top',(0,0,45),(0,0,0),43)}
scene.camera=cameras['hero'];scene['asset_id']=args.island;scene['hero_common_scale']=33.8;bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(args.island+'.blend')),compress=True)
report['webExport']=export(k.root,OUT/(args.island+'.glb'),args.island);report['blendSHA256']=sha(OUT/(args.island+'.blend'));report['glbSHA256']=sha(OUT/(args.island+'.glb'));report['buildSeconds']=round(time.time()-started,2);(OUT/'model-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('ASSET_SAVED',json.dumps({'id':args.island,'triangles':triangles,'materials':len(materials),'radius':radius,'seconds':report['buildSeconds']}),flush=True)
if args.draft_render:
 scene.render.resolution_x=960;scene.render.resolution_y=720;scene.cycles.samples=32;scene.render.filepath=str(OUT/'draft-hero.png');bpy.ops.render.render(write_still=True)
sys.stdout.flush();os._exit(0)
