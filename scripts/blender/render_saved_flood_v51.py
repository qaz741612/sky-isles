"""Read-only actual Blender renders, tied to the frozen saved source SHA."""
from pathlib import Path
import bpy,json,hashlib,time,sys
R=Path(__file__).resolve().parents[2];D=R/'docs/design/flood-control-island-g-v5-1';args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[]
def arg(k,default):return args[args.index(k)+1]if k in args else default
source=R/arg('--source','docs/design/flood-control-island-g-v5-1/flood-control-g-v5-1.blend');O=R/'docs/previews/flood-control-island-g-v5-1'/arg('--folder','blender');O.mkdir(parents=True,exist_ok=True);sha=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;records=[]
views=arg('--views','hero,reference-hero,front,back,left,right,top,near-dam,near-command,s22-crossing,downstream-detail,tower-detail').split(',')
for name in views:
 s.camera=bpy.data.objects['VIEW_'+name];s.render.filepath=str(O/(name+'.png'));begin=time.monotonic();bpy.ops.render.render(write_still=True);records.append({'name':name,'cameraBlender':list(s.camera.location),'rotation':list(s.camera.rotation_euler),'orthoScale':s.camera.data.ortho_scale,'size':[s.render.resolution_x,s.render.resolution_y],'seconds':time.monotonic()-begin});(O/'render-record.json').write_text(json.dumps({'version':'G-V5.1','source':str(source.relative_to(R)),'sourceBlendSHA256':sha,'engine':s.render.engine,'samples':s.cycles.samples,'sameSource':True,'records':records},indent=2)+'\n');print('V5.1 frozen rendered',name,flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
