"""Read-only final R21 saved Blender renders. Never rebuild or replace a GLB."""
import bpy,json,sys,hashlib,time
from pathlib import Path
R=Path(__file__).resolve().parents[2];only=sys.argv[sys.argv.index('--only')+1]if '--only'in sys.argv else None
codes=[sys.argv[sys.argv.index('--code')+1]]if '--code'in sys.argv else list('BDEH')
output=sys.argv[sys.argv.index('--output')+1]if '--output'in sys.argv else 'docs/previews/bdeh-r21'
for code in codes:
 source=R/f'docs/design/bdeh-r21/{code}/{code}-r21.blend';sha=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
 if '--samples'in sys.argv:s.cycles.samples=int(sys.argv[sys.argv.index('--samples')+1])
 out=R/output/code/'blender';out.mkdir(parents=True,exist_ok=True);record=out/'render-record.json';records=[]
 if '--resume'in sys.argv and record.exists():
  old=json.loads(record.read_text());assert old['sourceBlendSHA256']==sha,'Cannot mix renders of different .blend versions';records=old['records']
 for name in ['hero','front','back','left','right','top','architecture','public-space']:
  if only and name!=only:continue
  if any(r['name']==name for r in records):continue
  s.camera=bpy.data.objects['VIEW_'+name];s.render.filepath=str(out/(name+'.png'));begin=time.monotonic();bpy.ops.render.render(write_still=True);records.append({'name':name,'cameraBlender':list(s.camera.location),'rotation':list(s.camera.rotation_euler),'orthoScale':s.camera.data.ortho_scale,'size':[s.render.resolution_x,s.render.resolution_y],'seconds':time.monotonic()-begin});record.write_text(json.dumps({'sameSource':True,'sourceBlendSHA256':sha,'engine':'Cycles CPU, no denoiser available','samples':s.cycles.samples,'records':records},indent=2)+'\n');print('R21 frozen render',code,name,flush=True)
 assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
