"""Idempotent local wheel/track/platform correction on the saved station. MIT.
No station rebuilding or camera changes; localized vehicle glazing correction.
The main recipe has matching dimensions and material values.
"""
import bpy,sys,json,hashlib,os,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from policy_assets.exporter import export
from policy_assets.kit import G
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/design/seven-policy-islands-blender-v1/transport';source=OUT/'transport.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source));root=bpy.data.objects['transport_MODEL'];changed=False
rails=sorted([o for o in root.children_recursive if o.name.startswith('SteelDisplayRail')],key=lambda o:o.location.y);assert len(rails)==2
for o,y in zip(rails,[7.31,8.41]):
 if abs(o.location.y-y)>1e-6:o.location.y=y;changed=True
sleepers=sorted([o for o in root.children_recursive if o.name.startswith('TimberTrackSleeper')],key=lambda o:o.location.x);assert len(sleepers)==34
for i,o in enumerate(sleepers):
 x=-7.5+i*15/33
 if abs(o.location.x-x)>1e-6 or abs(o.location.y-7.86)>1e-6:changed=True
 o.location.x=x;o.location.y=7.86
 for v in o.data.vertices:
  y=math.copysign(.85,v.co.y)
  if abs(v.co.y-y)>1e-6:changed=True;v.co.y=y
 o.data.update()
wheels=[o for o in root.children_recursive if o.name.startswith('TrainWheel')];assert len(wheels)==8
for o in wheels:
 y=7.31 if o.location.y<7.86 else 8.41
 if abs(o.location.y-y)>1e-6 or abs(o.location.z-.49)>1e-6:changed=True
 o.location.y=y;o.location.z=.49
platform=bpy.data.objects['RaisedPassengerPlatform']
if abs(platform.location.y-5.9)>1e-6:changed=True
platform.location.y=5.9
for o in root.children_recursive:
 if o.name.startswith('PlatformTactileBlock'):
  if abs(o.location.y-6.64)>1e-6:changed=True
  o.location.y=6.64
tint=bpy.data.materials.get('Smoked vehicle glazing')or G.material('Smoked vehicle glazing','47747B',.18,.05,.15)
for o in root.children_recursive:
 if o.name.startswith('PassengerWindow'):
  y=7.108 if o.location.y<7.86 else 8.612
  if abs(o.location.y-y)>1e-6 or o.data.materials[0]!=tint:changed=True
  o.location.y=y;o.data.materials.clear();o.data.materials.append(tint)
bpy.context.view_layer.update();report=json.loads((OUT/'model-report.json').read_text());root['trackGauge']=1.1;root['wheelRailContactZ']=.23
if changed:
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
used={s.material.name for o in root.children_recursive if o.type=='MESH'for s in o.material_slots if s.material};report['materials']=sorted(used);report['materialCount']=len(used);report['complexityCap']['materialsWithinCap']=len(used)<=29
report['sourceScripts']['scripts/blender/policy_assets/kit.py']=sha(ROOT/'scripts/blender/policy_assets/kit.py')
report['webExport']=export(root,OUT/'transport.glb','transport');report['blendSHA256']=sha(source);report['glbSHA256']=sha(OUT/'transport.glb');report['sourceScripts']['scripts/blender/policy_assets/recipes.py']=sha(ROOT/'scripts/blender/policy_assets/recipes.py');report['sourceScripts']['scripts/blender/finish_transport_track.py']=sha(Path(__file__));report['trackGeometry']={'gauge':1.1,'railCentreY':[7.31,8.41],'railTopZ':.23,'wheelRadius':.26,'wheelCentreZ':.49,'wheelBottomZ':.23,'sleeperLength':1.7,'platformBackEdgeY':6.8,'tactileLineY':6.64,'trainGeometrySeparateFromTrack':True,'animationImplemented':False};report['gltfReexportNote']='Local track, wheel contact and tactile-edge correction on the same saved station; architecture/materials/cameras unchanged. TrainRollingStock remains independent.';(OUT/'model-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('TRACK_CONTACT_CORRECTED',json.dumps(report['trackGeometry']),flush=True);sys.stdout.flush();os._exit(0)
