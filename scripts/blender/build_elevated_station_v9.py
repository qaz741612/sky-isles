"""Build the original approved-image station prototype, never the live game. MIT."""
import sys,os,math,json,time,hashlib,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy,bmesh
from mathutils import Vector
from elevated_station_v9.core import Station,ROOT,OUT,W,G
from elevated_station_v9.architecture import terrain,hall,viaduct,canopy,access,train
from elevated_station_v9.landscape import landscape
from elevated_station_v9.exporter import export
p=argparse.ArgumentParser();p.add_argument('--draft',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else sys.argv[1:]);OUT.mkdir(parents=True,exist_ok=True);(OUT/'renders').mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();started=time.time();s=Station()
for fn in [terrain,hall,viaduct,canopy,access,train,landscape]:fn(s);print('BUILT',fn.__name__,flush=True)
# Practical shell catalogue derives small physical furniture/ceiling bounds from real source meshes.
from shapely.geometry import box as rect
for o in list(s.root.children_recursive):
 if o.type!='MESH' or not o.name.startswith(('TicketGatePedestal','InteriorServiceDesk','SteelWoodWasteBin','TravelInformationStele','StandingSeamRoofWing','RoofSkyOpeningEnd','HallSkylight','ThickMetalCanopyPanel')):continue
 bpy.context.view_layer.update();pts=[o.matrix_world@Vector(v)for v in o.bound_box];xs=[p.x for p in pts];zs=[-p.y for p in pts];ys=[p.z for p in pts];s.proxy(o.name,'ceiling'if 'Roof'in o.name or 'Skylight'in o.name else'furniture',rect(min(xs),min(zs),max(xs),max(zs)),min(ys),max(ys))
# Explicit future NPC spaces: Empty boxes, no person model or dialog system.
s.use('Identity')
for i,x in enumerate([-3.70,3.65]):
 o=G.empty('NPC_RESERVED_'+str(i),s.root);o.location=W((x,.075,3.93));o.empty_display_type='CUBE';o.empty_display_size=1.5;o['clearSquareXZ']=[x-1.5,2.43,x+1.5,5.43];o['facingWorldXYZ']=[0,0,-1];o['interactionRadius']=1.4;o['playerStopWorldXYZ']=[x,.075,2.75];o['implemented']=False
# Real reference geometry is never appended, imported or exported as visible art.
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();bounds=[];triangles=0;objects=0;issues=[];byrole={}
for o in s.root.children_recursive:
 if o.type!='MESH':continue
 objects+=1;e=o.evaluated_get(deps);me=e.to_mesh();me.calc_loop_triangles();triangles+=len(me.loop_triangles);bounds.extend(tuple(o.matrix_world@v.co)for v in me.vertices);bm=bmesh.new();bm.from_mesh(me)
 # Recalculate custom model caps before reporting only if the original has reversed normals.
 opened=sum(not ed.is_manifold for ed in bm.edges);vol=bm.calc_volume(signed=True);bm.free()
 if opened or vol<=0:issues.append({'name':o.name,'nonManifoldEdges':opened,'signedLocalVolume':vol})
 e.to_mesh_clear()
report={'phase':'standalone Blender prototype, manual art acceptance pending','blenderVersion':bpy.app.version_string,'artSource':'inputs/approved-v9/美術參考_高架車站.png','artSHA256':sha(OUT/'inputs/approved-v9/美術參考_高架車站.png'),'geometryReferenceOnly':'inputs/approved-v9/F_elevated_station_v9_design.glb','geometryReferenceSHA256':sha(OUT/'inputs/approved-v9/F_elevated_station_v9_design.glb'),'geometrySourceReusedAsArt':False,'curvedHallTemplateUsed':False,'worldPlanSHA256':sha(ROOT/'src/data/yuan-plan.json'),'sourceScriptSHA256':{str(q.relative_to(ROOT)):sha(q)for q in [Path(__file__),*Path(__file__).parent.joinpath('elevated_station_v9').glob('*.py')]},'sourceMeshObjects':objects,'evaluatedTriangles':triangles,'geometryAuditIssues':issues,'sitePolygonXZ':list(s.site.exterior.coords),'siteArea':s.site.area,'referenceSiteArea':s.referenceSite.area,'referenceSitePolygonXZ':list(s.referenceSite.exterior.coords),'localGardenTerraceProposalAddedArea':s.site.difference(s.referenceSite).area,'localGardenTerraceProposalOnly':True,'siteBoundsXZ':list(s.site.bounds),'NPCReservedSquaresXZ':[[x-1.5,2.43,x+1.5,5.43]for x in [-3.7,3.65]],'worldSourceUnchanged':True,'boundsBlenderXYZ':{'min':[min(v[i]for v in bounds)for i in range(3)],'max':[max(v[i]for v in bounds)for i in range(3)]}}
(OUT/'model-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(OUT/'collision-shells.json').write_text(json.dumps({'scope':'Practical editable proxy proposals only; not registered in game physics, no runtime certification. Stair flights need their actual stepped treads, not an opaque stair AABB. Lift intentionally nonfunctional in standalone artwork.','worldAxes':'X east, Y up, Z north','shells':s.proxies},ensure_ascii=False,indent=2)+'\n');print('SOURCE_GEOMETRY_AUDIT',objects,triangles,'issues',len(issues),flush=True)
if issues:raise RuntimeError('Repair source geometry before saving final: '+str(issues[:8]))
# Hidden wireframe proxy collection stored in BLEND, excluded from artwork GLBs.
G.collection('80_COLLISION_PROXIES_NOT_RENDERED');coll=bpy.data.collections['80_COLLISION_PROXIES_NOT_RENDERED'];coll.hide_render=True
for r in s.proxies:
 poly=r['polygonXZ']
 if len(poly)>2:
  o=s.solid('COLLIDER_'+r['id'],__import__('shapely').geometry.Polygon(poly),r['bottom'],r['top'],'concrete',None)
  if o:
   # s.solid's explicit parent default is source group: detach to keep export separation.
   o.parent=None;o.display_type='WIRE';o.hide_render=True;o.hide_set(True);o['collision_role']=r['role']
# Studio lights are all excluded from GLB.
G.collection('90_STUDIO');scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=48;scene.cycles.use_denoising=True;scene.cycles.adaptive_threshold=.045;scene.cycles.max_bounces=10;scene.cycles.transmission_bounces=8;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=3;scene.cycles.caustics_reflective=False;scene.cycles.caustics_refractive=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=1440;scene.render.resolution_y=1080;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.world=bpy.data.worlds.new('WarmDaylight');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.77,.80,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.65;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.45
G.box('StudioBackdrop',(0,0,-1.84),(200,200,.12),s.M['concrete'],r=0)
s.light('DaylightKey',(-12,19,14),(0,0,0),2600,10,(1,.91,.78));s.light('DaylightFill',(13,14,4),(0,2,-4),1300,8,(.80,.90,1));s.light('RailwayRim',(2,16,-14),(0,3,-6),1900,8,(1,.95,.85))
s.light('FrontArchitecturalFill',(0,8,8),(0,1,-4),650,7,(1,.91,.75))
for x in [-4.4,0,4.4]:s.light('WarmHall',(x,2.50,-4.55),(x,.2,-3.4),220,1.5,(1,.78,.50))
for x in [-5.0,5.0]:s.light('WarmViaduct',(x,3.20,-6.25),(x,1,-4.1),60,1.4,(1,.78,.49))
# Identical saved source used for every camera; player cameras are explicit simulations.
cams=[('hero',(25,20,30),(0,1.8,-1.2),29.6),('front',(0,7.3,35),(0,2,-1.3),29.6),('back',(0,7.3,-36),(0,2,-1.3),29.6),('left',(-35,7.3,-1),(0,2,-1.3),29.6),('right',(35,7.3,-1),(0,2,-1.3),29.6),('top',(0,42,-1),(0,0,-1),29.6),('train-side',(16,9.2,7),(1,4.6,-7.3),25)]
for name,pos,tgt,ortho in cams:G.camera(name,W(pos),W(tgt),ortho)
for name,dist,pitch,fov,yaw in [('player-desktop',16,.60,55,.16),('player-mobile',22,.67,58,.12)]:
 target=Vector((0,2.0,3.5));pos=target+Vector((math.sin(yaw)*math.cos(pitch)*dist,math.sin(pitch)*dist,math.cos(yaw)*math.cos(pitch)*dist));cam=G.camera(name,W(pos),W(target));cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=32;cam.data.lens=16/math.tan(math.radians(fov)/2);cam['simulationOnly']=True;cam['distance']=dist;cam['pitch']=pitch;cam['yaw']=yaw;cam['fov']=fov;cam['targetWorldXYZ']=list(target)
scene.camera=bpy.data.objects['hero'];bpy.context.preferences.filepaths.save_version=0;source=OUT/'transport-station-v9.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);report['blendSHA256']=sha(source)
report['showcase']=export(s.root,OUT/'transport-station-v9-showcase.glb');report['showcase']['sha256']=sha(OUT/'transport-station-v9-showcase.glb')
# Candidate modifies only the transient export state, NEVER the saved approved-art source.
for o in s.root.children_recursive:
 for m in o.modifiers:
  if m.type=='BEVEL':m.segments=1
bpy.context.view_layer.update();report['candidate']=export(s.root,OUT/'transport-station-v9-game-candidate.glb',True);report['candidate']['sha256']=sha(OUT/'transport-station-v9-game-candidate.glb');report['buildSeconds']=round(time.time()-started,2);(OUT/'model-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('SAVED_FINAL_SOURCE_AND_TWO_GLB',json.dumps({'seconds':report['buildSeconds'],'showcase':report['showcase'],'candidate':report['candidate']}),flush=True)
if a.draft:
 bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.render.resolution_x=1100;scene.render.resolution_y=825;scene.cycles.samples=24;scene.render.filepath=str(OUT/'draft-hero.png');bpy.ops.render.render(write_still=True)
sys.stdout.flush();os._exit(0)
