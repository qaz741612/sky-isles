"""Render only a frozen G V5 .blend; never edit/save geometry or replace GLB."""
from pathlib import Path
import bpy,json,hashlib,time,sys
R=Path(__file__).resolve().parents[2];D=R/'docs/design/flood-control-island-g-v5';O=R/'docs/previews/flood-control-island-g-v5/blender';O.mkdir(exist_ok=True)
source=D/'flood-control-g-v5.blend';bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;sha=hashlib.sha256(source.read_bytes()).hexdigest();records=[]
for name in ['hero','reference-hero','front','back','left','right','top','near-dam','near-command','s22-crossing']:
 if '--only'in sys.argv and name!=sys.argv[sys.argv.index('--only')+1]:continue
 scene.camera=bpy.data.objects['VIEW_'+name];scene.render.filepath=str(O/(name+'.png'));begin=time.monotonic();bpy.ops.render.render(write_still=True);records.append({'name':name,'sourceBlendSHA256':sha,'cameraBlender':list(scene.camera.location),'rotation':list(scene.camera.rotation_euler),'orthoScale':scene.camera.data.ortho_scale,'size':[scene.render.resolution_x,scene.render.resolution_y],'seconds':time.monotonic()-begin})
 (O/'render-record.json').write_text(json.dumps({'sameSource':True,'frozenSource':str(source.relative_to(R)),'sourceBlendSHA256':sha,'pass':'final after second self-review','engine':'Blender Cycles CPU','samples':scene.cycles.samples,'records':records},indent=2)+'\n')
 print('G V5 frozen render saved',name,flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
