"""Read-only close details of the same final Blender files; not player cameras."""
import bpy,json,hashlib,time,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];O=R/(sys.argv[sys.argv.index('--output')+1]if'--output'in sys.argv else'docs/previews/bdeh-r21/final-qa/details');O.mkdir(exist_ok=True);rows=[]
only=sys.argv[sys.argv.index('--only')+1]if'--only'in sys.argv else'BDEH'
if(O/'render-record.json').exists():rows=[r for r in json.loads((O/'render-record.json').read_text())['records']if r['code']not in only]
views=[('B','courtyard',(7,19,8),(-4.5,.7,-3.9),16),('D','service-threshold',(8,5,-9),(3,1.5,-2.2),14),('E','rain-garden',(10,7,-17),(-.2,.3,-7.8),12),('E','roof-planting',(-12,12,-16),(-3.5,4,-.5),17),('H','reading-forum',(-3,6,-7),(-10.6,1,-5.4),9)]
def convert(p):return Vector((p[0],-p[2],p[1]))
for code,name,position,target,scale in views:
 if code not in only:continue
 path=R/f'docs/design/bdeh-r21/{code}/{code}-r21.blend';sha=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
 if'--samples'in sys.argv:s.cycles.samples=int(sys.argv[sys.argv.index('--samples')+1])
 data=bpy.data.cameras.new('FINAL_QA_DETAIL');camera=bpy.data.objects.new('FINAL_QA_DETAIL',data);s.collection.objects.link(camera);camera.location=convert(position);camera.rotation_euler=(convert(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=scale;s.camera=camera;s.render.filepath=str(O/f'{code}-{name}.png');begin=time.monotonic();bpy.ops.render.render(write_still=True)
 assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
 rows.append({'code':code,'name':name,'kind':'Blender close inspection lens, never a native game/player camera','sourceBlendSHA256':sha,'cameraModelLocalYup':position,'targetModelLocalYup':target,'orthoScale':scale,'size':[s.render.resolution_x,s.render.resolution_y],'seconds':time.monotonic()-begin})
 (O/'render-record.json').write_text(json.dumps({'sameFinalBlenderSources':True,'engine':f'Cycles CPU{s.cycles.samples}, no denoiser','records':rows},indent=2)+'\n');print('Saved final source detail',code,name,flush=True)
