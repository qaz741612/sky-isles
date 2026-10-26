"""Re-render the unmodified PR11 BLEND with the exact refined framing. MIT."""
import bpy,sys,json,hashlib,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OLD=ROOT/'docs/design/parent-child-blender-model-v1';OUT=ROOT/'docs/design/parent-child-blender-refinement-v2';SOURCE=OLD/'parent-child-centre.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;source_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest();views=json.loads((OLD/'render-record.json').read_text())['views'];(OUT/'before').mkdir(exist_ok=True)
records=[];framing=json.loads((OUT/'layout.json').read_text())['renderFraming']
for name,width,samples in [('hero',1600,96),('top',1400,64)]:
 scale=framing[name]
 rec=next(v for v in views if Path(v['file']).stem==name);camera=bpy.data.objects[rec['camera']];camera.location=rec['cameraPositionXYZ'];camera.rotation_euler=rec['cameraRotationRadians'];camera.data.ortho_scale=scale
 scene.camera=camera;scene.render.resolution_x=width;scene.render.resolution_y=round(width*741/1082);scene.cycles.samples=samples;scene.cycles.use_denoising=True;path=OUT/'before'/(name+'.png');scene.render.filepath=str(path);start=time.time();bpy.ops.render.render(write_still=True)
 records.append({'file':str(path.relative_to(OUT)),'sourceBlendSHA256':source_sha,'imageSHA256':hashlib.sha256(path.read_bytes()).hexdigest(),'camera':camera.name,'cameraPositionXYZ':list(camera.location),'cameraRotationRadians':list(camera.rotation_euler),'orthoScale':scale,'size':[scene.render.resolution_x,scene.render.resolution_y],'samples':samples,'seconds':round(time.time()-start,2)})
 (OUT/'before-render-record.json').write_text(json.dumps({'engine':'Blender Cycles CPU + OpenImageDenoise','note':'Original PR11 geometry/materials/light sources; only framing matches the new counterpart. No original BLEND saved or modified.','views':records},indent=2));print('BEFORE_COMPARISON_RENDERED',name,flush=True)
