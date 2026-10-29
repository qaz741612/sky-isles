"""MIT. Same saved editable scene for every image; no AI substitutions."""
import bpy,sys,json,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'docs/design/flood-control-island-g-v1';OUT=ROOT/'docs/previews/flood-control-island-g-v1/blender';OUT.mkdir(parents=True,exist_ok=True)
source=D/'flood-control-g.blend';bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;sha=hashlib.sha256(source.read_bytes()).hexdigest()
records=[];only=sys.argv[sys.argv.index('--only')+1] if '--only' in sys.argv else None
for name in ['hero','front','back','left','right','top']:
 if only and name!=only:continue
 s.camera=bpy.data.objects['VIEW_'+name];s.render.resolution_x=1200;s.render.resolution_y=1000;s.cycles.samples=48;s.cycles.use_denoising=False;s.render.filepath=str(OUT/(name+'.png'));start=time.time();bpy.ops.render.render(write_still=True)
 records.append({'name':name,'blender':bpy.app.version_string,'engine':'Cycles CPU','sourceBlendSHA256':sha,'seconds':time.time()-start,'position':list(s.camera.location),'rotation':list(s.camera.rotation_euler),'orthoScale':s.camera.data.ortho_scale,'size':[1200,1000]})
 (OUT/'render-record.json').write_text(json.dumps(records,indent=2))
 print('RENDER_SAVED',name,flush=True)
