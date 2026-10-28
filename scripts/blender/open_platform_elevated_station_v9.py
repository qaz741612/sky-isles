"""Continue PR14's saved artwork: remove upper canopy, finish open platforms.
No world/game edits. Ground station geometry is byte-for-byte preserved. MIT.
"""
import bpy,bmesh,sys,os,json,hashlib,math,random,time,subprocess
from pathlib import Path
from mathutils import Vector
from shapely.geometry import Polygon,Point,LineString,box as rect
from shapely.ops import unary_union
sys.path.insert(0,str(Path(__file__).resolve().parent))
from elevated_station_v9.core import Station,ROOT,OUT,G,W
from elevated_station_v9.exporter import export
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
before=ROOT/'work/open-platform-before';source=OUT/'transport-station-v9.blend';beforeFile=before/'transport-station-v9.blend'
if not beforeFile.exists():
 before.mkdir(parents=True,exist_ok=True)
 for name in ['transport-station-v9.blend','model-report.json','collision-shells.json']:
  (before/name).write_bytes(subprocess.check_output(['git','show','81f7408468bcce2f7452b13e0a9d7ea1d4be62a1:docs/design/transport-elevated-station-v9-prototype/'+name],cwd=ROOT))
assert sha(beforeFile)=='a975409e16bf406b4fe1ae9981d632c527f85244387e3a88111baad4177f2abb'
bpy.ops.wm.open_mainfile(filepath=str(beforeFile));bpy.context.view_layer.update();s=Station.__new__(Station);s.root=bpy.data.objects['YuanliElevatedStationV9'];s.groups={o.name:o for o in s.root.children};s.M={m.name:m for m in bpy.data.materials};s.rng=random.Random(74161209);s.plan=json.loads((ROOT/'src/data/yuan-plan.json').read_text());old=json.loads((before/'model-report.json').read_text());s.site=Polygon(old['sitePolygonXZ']);s.referenceSite=Polygon(old['referenceSitePolygonXZ']);s.lines={e['id']:s.edge(e)for e in s.plan['edges']};s.mouths=unary_union([s.lines[k].buffer(2.4,cap_style=2)for k in ['S09','S10','S15','S18']]);s.npc=[rect(x-1.5,2.43,x+1.5,5.43)for x in [-3.7,3.65]]
s.proxies=json.loads((before/'collision-shells.json').read_text())['shells'];s.proxies=[p for p in s.proxies if not p['id'].startswith(('ThickMetalCanopyPanel','UpperPlanter','TrainSweptStaticEnvelope'))]
# Freeze the retained structures: topology/material assignment/local and world transforms.
def fingerprint(o):
 return hashlib.sha256(json.dumps({'vertices':[list(v.co)for v in o.data.vertices],'faces':[list(f.vertices)for f in o.data.polygons],'matrix':[list(r)for r in o.matrix_world],'materials':[m.name for m in o.data.materials]},sort_keys=True).encode()).hexdigest()
keep={o.name:fingerprint(o)for role in ['Hall','Identity','Viaduct','Railway','VerticalCirculation']for o in s.groups[role].children_recursive if o.type=='MESH'}
# Remove the entire upper-only semantic group, not a name substring across roofs.
removed=[{'name':o.name,'type':o.type}for o in s.groups['Canopy'].children_recursive]
for o in reversed(list(s.groups['Canopy'].children_recursive)):bpy.data.objects.remove(o,do_unlink=True)
bpy.data.objects.remove(s.groups.pop('Canopy'),do_unlink=True)
if 'Canopy'in bpy.data.collections:bpy.data.collections.remove(bpy.data.collections['Canopy'])
# Empty former source-only proxies are regenerated from the revised catalogue below.
col=bpy.data.collections.get('80_COLLISION_PROXIES_NOT_RENDERED')
if col:
 for o in list(col.objects):bpy.data.objects.remove(o,do_unlink=True)
# Retire the small upper-track planters: no planting in the railway swept envelope.
for o in list(s.groups['Gardens'].children):
 if o.name.startswith('UpperTerracePlanter'):
  for c in reversed(list(o.children_recursive)):bpy.data.objects.remove(c,do_unlink=True)
  bpy.data.objects.remove(o,do_unlink=True)
# Same two coaches, full size, same track centre: reverse the train about its bbox centre.
train=s.groups['TrainRollingStock'];train.rotation_euler.z=math.pi;train.location.x=.75;train.location.y=16.4;train['openPlatformOrientation']='180 degrees, front cab faces west; dimensions and wheel contact unchanged'
s.root['designRevision']='Open platform, PR14 revision 2';s.root['not_game_integrated']=True
# Open-platform furniture intentionally kept to the outside of its 1.10m clear lane.
G.collection('OpenPlatform');s.groups['OpenPlatform']=G.empty('OpenPlatform',s.root);s.use('OpenPlatform')
# One small light shelter ONLY at the top of the stair access; no rail/train coverage.
s.box('StairExitShelterRoof',(-6.52,5.76,-3.70),(1.78,.10,1.78),'roof',.018)
for x in [-7.41,-5.63]:s.box('SmallShelterSideFascia',(x,5.74,-3.70),(.045,.12,1.82),'roofEdge',.007)
for z in [-4.59,-2.81]:s.box('SmallShelterEndFascia',(-6.52,5.74,z),(1.82,.12,.045),'roofEdge',.007)
for x in [-7.20,-5.84]:
 for z in [-4.43,-2.98]:
  s.box('ShelterSlenderPost',(x,4.75,z),(.055,1.98,.055),'steel',.006);s.box('ShelterPostShoe',(x,3.80,z),(.10,.10,.10),'roofEdge',.008);s.proxy('ShelterPost','column',rect(x-.028,z-.028,x+.028,z+.028),3.75,5.74)
for x in [-7.20,-5.84]:s.box('ShelterSideBearer',(x,5.66,-3.70),(.075,.10,1.72),'steel',.007)
for i in range(8):s.box('SmallShelterTimberSoffit',(-7.21+i*.195,5.69,-3.70),(.13,.035,1.65),'woodLight',.004)
s.box('ShelterDownlight',(-6.52,5.655,-3.70),(.48,.024,.12),'light',.004)
s.proxy('SmallAccessShelter','ceiling',rect(-7.41,-4.59,-5.63,-2.81),5.69,5.81)
# End barriers meet front/rear guard; diagonal rear returns stay beyond rolling stock.
for x in [-9.34,9.34]:s.railing('PlatformEndReturn',LineString([(x,-6.045),(x,-7.20)]),3.75,1.10,postSpacing=.65)
for x in [-9.34,9.34]:s.railing('RearTrackEndReturn',LineString([(x,-9.26),(x,-9.15)]),3.31,1.10,postSpacing=.4)
# Complete the open platform edge visually; continuous collision rails remain existing.
for a,b in [(-8.9,-7.15),(-5.95,7.05),(8.35,8.9)]:
 s.box('PlatformGuardToe',((a+b)/2,3.82,-6.05),(b-a,.14,.045),'steel',.008)
 for x in [a+i*.14 for i in range(1,int((b-a)/.14))]:s.box('ThinPlatformGuardVertical',(x,4.28,-6.05),(.018,.92,.018),'rail',.003)
# Board edge along track, textured safety warning and transverse tile joints.
s.box('ContinuousPlatformSafetyStripe',(0,3.757,-7.16),(18.66,.014,.055),'yellow',.003)
for x in [-8.8+i*.50 for i in range(36)]:s.box('FlushPlatformPaverJoint',(x,3.751,-6.56),(.012,.002,1.01),'shadowStone',0)
for z in [-6.30,-6.65]:s.box('FlushPlatformLongJoint',(0,3.751,z),(18.65,.002,.010),'shadowStone',0)
# Compact outside-mounted information and low-pole luminaires, no canopy-scale supports.
for x in [-4.80,3.20]:
 s.box('PlatformInfoPost',(x,4.66,-6.04),(.055,1.82,.055),'steel',.005);s.box('PlatformInformationCabinet',(x,5.10,-6.04),(1.00,.40,.095),'navy',.025);s.text('PlatformShortInformation','1  候車示意',(x,5.11,-5.985),.115,'screen')
 s.proxy('PlatformInformationPost','post',rect(x-.035,-6.09,x+.035,-5.99),3.75,5.3)
for x in [-8.4,-2.45,5.65]:
 s.box('OpenPlatformLampPost',(x,4.68,-6.045),(.045,1.85,.045),'steel',.005);s.box('OpenPlatformLampHead',(x,5.62,-6.045),(.27,.09,.15),'roofEdge',.012);s.box('OpenPlatformLampDiffuser',(x,5.565,-6.045),(.22,.018,.10),'light',.004)
 s.proxy('PlatformLamp','post',rect(x-.03,-6.09,x+.03,-6.00),3.75,5.67)
# Short waiting perches attached outside the main path; clear lane is measured below.
for x in [-4.30,4.80]:
 for yy in [3.995,4.16]:s.box('PlatformWoodPerch',(x,yy,-6.125),(1.10,.085,.18),'woodLight',.012)
 for xx in [x-.41,x+.41]:s.box('PlatformPerchBracket',(xx,3.94,-6.10),(.045,.35,.13),'steel',.006)
 s.proxy('PlatformPerch','furniture',rect(x-.55,-6.215,x+.55,-6.035),3.75,4.205)
# Recompose forecourt furniture without filling protected NPC/road space.
# Recompose only the two forward garden tips, leaving every tree and rear band.
for name in ['WestForecourtGarden','EastForecourtGarden']:
 poly=Polygon(next(p['polygonXZ']for p in s.proxies if p['id']==name)).intersection(rect(-20,-20,20,5.93));group=bpy.data.objects[name]
 for child in reversed(list(group.children_recursive)):bpy.data.objects.remove(child,do_unlink=True)
 bpy.data.objects.remove(group,do_unlink=True);s.proxies=[p for p in s.proxies if p['id']!=name];s.plantbed(name,poly)
# Shade seats stand on the actual garden terrace nose, clear of beds and NPC.

for o in s.groups['Furniture'].children:
 if o.name.startswith('GardenWaitingBench'):
  o.rotation_euler.z=math.pi/2 if o.location.x<0 else -math.pi/2;o.location.x=-6.65 if o.location.x<0 else 6.65;o.location.y=-6.35
# Add one warm timber seat at each garden nose, facing the station; keep NPC squares empty.
# Existing benches now form two continuous garden-edge seats; no extra duplicated seats.
# Bench proxy changes follow visible footprint, not invisible old rectangles.
from shapely.affinity import rotate
for p in s.proxies:
 if p['id']=='GardenWaitingBench':
  cx=sum(v[0]for v in p['polygonXZ'][:-1])/4;poly=rotate(Polygon(p['polygonXZ']),90 if cx<0 else -90,origin=(cx,4.1));from shapely.affinity import translate;poly=translate(poly,xoff=-1.10 if cx<0 else 1.10,yoff=2.25);p['polygonXZ']=list(poly.exterior.coords)
# Train collider reflects real reversed geometry; dimensions unchanged, no animation claim.
s.proxy('TrainSweptStaticEnvelope','train',rect(-8.70,-9.06,9.45,-7.34),3.54,5.91,'static_display_no_riding')
# Add semantic source proxies; exporters only visit artwork root, never these.
G.COL=col
for p in s.proxies:
 poly=Polygon(p['polygonXZ'])
 if poly.area<=0:continue
 o=s.solid('COLLIDER_'+p['id'],poly,p['bottom'],p['top'],'concrete')
 if o:o.parent=None;o.hide_render=True;o.display_type='WIRE';o.hide_set(True);o['collision_role']=p['role']
# Same saved strict player cameras; only art hero is chosen from the exposed cab side.
bpy.context.view_layer.update();cam=bpy.data.objects['hero'];cam.location=W((-25,20,30));cam.rotation_euler=(W((0,1.8,-1.2))-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.scene.camera=cam
# Purge genuinely unused roof meshes/materials; shared ground roof PBR is retained.
purged=[]
for me in list(bpy.data.meshes):
 if me.users==0:purged.append(me.name);bpy.data.meshes.remove(me)
for mat in list(bpy.data.materials):
 if mat.users==0:bpy.data.materials.remove(mat)
bpy.context.view_layer.update()
assert all(fingerprint(bpy.data.objects[n])==h for n,h in keep.items()),'Retained station/arches/railways/identity/access changed'
# Exact-source independent topology audit before saving.
issues=[];tris=0;objects=0;bounds=[];deps=bpy.context.evaluated_depsgraph_get()
for o in s.root.children_recursive:
 if o.type!='MESH':continue
 objects+=1;e=o.evaluated_get(deps);me=e.to_mesh();me.calc_loop_triangles();tris+=len(me.loop_triangles);bounds.extend(tuple(o.matrix_world@v.co)for v in me.vertices);bm=bmesh.new();bm.from_mesh(me);bad=sum(not ed.is_manifold for ed in bm.edges);vol=bm.calc_volume(signed=True);bm.free();e.to_mesh_clear()
 if bad or vol<=0:issues.append({'name':o.name,'nonManifoldEdges':bad,'volume':vol})
assert not issues,issues
# Store detailed revision receipts, plus current approved base plan hash.
r=old.copy();r.update(phase='PR14 open-platform revision; standalone artwork, manual acceptance pending',designRevision='open-platform-r2',previousSourceBlendSHA256=sha(beforeFile),worldPlanSHA256=sha(ROOT/'src/data/yuan-plan.json'),sourceMeshObjects=objects,evaluatedTriangles=tris,geometryAuditIssues=[],boundsBlenderXYZ={'min':[min(v[i]for v in bounds)for i in range(3)],'max':[max(v[i]for v in bounds)for i in range(3)]},sourceScriptSHA256={str(q.relative_to(ROOT)):sha(q)for q in [Path(__file__),*Path(__file__).parent.joinpath('elevated_station_v9').glob('*.py')]})
(OUT/'collision-shells.json').write_text(json.dumps({'scope':'Offline collision candidates ONLY, not game capsule physics. Vertical access not implemented; no NPC model.','worldAxes':'X east, Y up, Z north','shells':s.proxies},ensure_ascii=False,indent=2)+'\n')
receipt={'previousSourceBlendSHA256':sha(beforeFile),'removedUpperCanopyObjects':removed,'removedUpperCanopyCount':len(removed),'purgedUnusedMeshCount':len(purged),'remainingUpperCanopyObjects':0,'retainedGeometryFingerprints':keep,'retainedMeshCount':len(keep),'retainedGeometryExact':True,'trainRigidRotationDegrees':180,'trainScale':[1,1,1],'trainBBoxPivotWorldXZ':[.375,-8.2],'shelterFootprintXZ':[-7.41,-4.59,-5.63,-2.81],'shelterRoofY':5.76,'fourPortsNPCsAndSpawnUnchanged':True,'sceneNotIntegrated':True}
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);r['blendSHA256']=sha(source);receipt['finalSourceBlendSHA256']=r['blendSHA256'];(OUT/'open-platform-revision.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');r['showcase']=export(s.root,OUT/'transport-station-v9-showcase.glb');r['showcase']['sha256']=sha(OUT/'transport-station-v9-showcase.glb');(OUT/'model-report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('OPEN_PLATFORM_SAVED',json.dumps({'objects':objects,'triangles':tris,'removedUpperCanopy':len(removed),'retainedExact':len(keep),'sourceSHA256':r['blendSHA256'],'showcase':r['showcase']}),flush=True);sys.stdout.flush();os._exit(0)
