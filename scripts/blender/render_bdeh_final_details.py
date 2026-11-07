"""Read-only close details of the same final Blender files; not player cameras."""
import bpy,json,hashlib,time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];O=R/'docs/previews/bdeh-r21/final-qa/details';O.mkdir(exist_ok=True);rows=[]
views=[('B','courtyard',(11,12,-5),(-4.5,.7,-3.9),18),('D','service-threshold',(8,5,-9),(3,1.5,-2.2),14),('E','rain-garden',(10,7,-17),(-.2,.3,-7.8),12),('E','roof-planting',(-12,12,-16),(-3.5,4,-.5),17),('H','reading-forum',(-16,5,-12),(-9,1.5,-6),12)]
def convert(p):return Vector((p[0],-p[2],p[1]))
for code,name,position,target,scale in views:
 path=R/f'docs/design/bdeh-r21/{code}/{code}-r21.blend';sha=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
 data=bpy.data.cameras.new('FINAL_QA_DETAIL');camera=bpy.data.objects.new('FINAL_QA_DETAIL',data);s.collection.objects.link(camera);camera.location=convert(position);camera.rotation_euler=(convert(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=scale;s.camera=camera;s.render.filepath=str(O/f'{code}-{name}.png');begin=time.monotonic();bpy.ops.render.render(write_still=True)
 assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
 rows.append({'code':code,'name':name,'kind':'Blender close inspection lens, never a native game/player camera','sourceBlendSHA256':sha,'cameraThreeYup':position,'targetThreeYup':target,'orthoScale':scale,'size':[s.render.resolution_x,s.render.resolution_y],'seconds':time.monotonic()-begin})
 (O/'render-record.json').write_text(json.dumps({'sameFinalBlenderSources':True,'engine':'Cycles CPU64, no denoiser','records':rows},indent=2)+'\n');print('Saved final source detail',code,name,flush=True)
