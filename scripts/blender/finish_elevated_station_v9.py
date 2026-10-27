"""Local completion on existing BLEND: train end/side closures and lift mid-glass.
Keeps all other station/garden geometry; never recreates the whole project. MIT.
"""
import bpy,bmesh,sys,os,json,hashlib,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from elevated_station_v9.core import Station,ROOT,OUT,G
from elevated_station_v9.architecture import train
from elevated_station_v9.exporter import export
source=OUT/'transport-station-v9.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(source);bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update();s=Station.__new__(Station);s.root=bpy.data.objects['YuanliElevatedStationV9'];s.groups={o.name:o for o in s.root.children};s.M={m.name:m for m in bpy.data.materials};s.proxies=json.loads((OUT/'collision-shells.json').read_text())['shells'];s.proxies=[p for p in s.proxies if p['id']!='TrainSweptStaticEnvelope'];group=s.groups['TrainRollingStock'];oldOthers={}
for o in s.root.children_recursive:
 p=o
 while p.parent and p.parent!=s.root:p=p.parent
 if o.type=='MESH'and p!=group:oldOthers[o.name]=tuple(tuple(row)for row in o.matrix_world)
for o in reversed(list(group.children_recursive)):bpy.data.objects.remove(o,do_unlink=True)
group.location=(0,0,0);train(s)
s.use('VerticalCirculation')
if 'LiftMiddleFrontGlass'not in bpy.data.objects:s.box('LiftMiddleFrontGlass',(7.70,2.81,-3.605),(1.49,1.46,.035),'glass',.004)
bpy.context.view_layer.update()
for name,matrix in oldOthers.items():assert tuple(tuple(row)for row in bpy.data.objects[name].matrix_world)==matrix,name
# Keep the existing hidden train collision proxy: its overall bounds are unchanged.
file=OUT/'collision-shells.json';collision=json.loads(file.read_text());collision['shells']=s.proxies;file.write_text(json.dumps(collision,ensure_ascii=False,indent=2)+'\n');deps=bpy.context.evaluated_depsgraph_get();issues=[];tris=0;objects=0
for o in s.root.children_recursive:
 if o.type!='MESH':continue
 objects+=1;e=o.evaluated_get(deps);me=e.to_mesh();me.calc_loop_triangles();tris+=len(me.loop_triangles);bm=bmesh.new();bm.from_mesh(me);bad=sum(not x.is_manifold for x in bm.edges);vol=bm.calc_volume(signed=True);bm.free()
 if bad or vol<=0:issues.append({'name':o.name,'nonManifoldEdges':bad,'volume':vol})
 e.to_mesh_clear()
assert not issues,issues;report=json.loads((OUT/'model-report.json').read_text());report['previousSourceBlendSHA256']=before;report['localCompletion']='Trailing coach real window/end wall; side infill around window openings; lift middle glazing. Other existing mesh transforms unchanged.';report['sourceMeshObjects']=objects;report['evaluatedTriangles']=tris;report['geometryAuditIssues']=issues;report['sourceScriptSHA256']={str(p.relative_to(ROOT)):sha(p)for p in [ROOT/'scripts/blender/build_elevated_station_v9.py',Path(__file__),*Path(__file__).parent.joinpath('elevated_station_v9').glob('*.py')]};bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True);report['blendSHA256']=sha(source);report['showcase']=export(s.root,OUT/'transport-station-v9-showcase.glb');report['showcase']['sha256']=sha(OUT/'transport-station-v9-showcase.glb')
for o in s.root.children_recursive:
 for mod in o.modifiers:
  if mod.type=='BEVEL':mod.segments=1
bpy.context.view_layer.update();report['candidate']=export(s.root,OUT/'transport-station-v9-game-candidate.glb',True);report['candidate']['sha256']=sha(OUT/'transport-station-v9-game-candidate.glb');(OUT/'model-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('LOCAL_COMPLETION_SAVED',report['blendSHA256'],tris,objects,flush=True);sys.stdout.flush();os._exit(0)
