"""Actual original PR17 Blender, same final V3 lens; never save original file."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
p=ROOT/'docs/design/industry-youth-island-c-v2.2/industry-youth-c.blend'
bpy.ops.wm.open_mainfile(filepath=str(p));scene=bpy.context.scene;scene.cycles.samples=16;scene.cycles.use_denoising=False
scene.render.resolution_x=1000;scene.render.resolution_y=800;scene.render.resolution_percentage=100
out=ROOT/'docs/previews/industry-youth-island-c-v3/before/blender';out.mkdir(parents=True,exist_ok=True)
records=[]
for name,loc in [('hero',(32,-36,29)),('top',(0,0,55))]:
 c=scene.camera;c.location=loc;c.rotation_euler=(Vector((0,0,-.6))-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=37
 scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);records.append({'name':name,'location':loc,'target':[0,0,-.6],'orthoScale':37,'size':[1000,800]})
(out/'render-record.json').write_text(json.dumps({'sourceCommit':'0c7cab7','sourceBlendSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'readOnlyOriginal':True,'views':records},indent=2)+'\n')
