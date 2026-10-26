"""Render six real Cycles views from each saved BLEND. Same hero projection for all.
No geometry changes, no AI output. MIT.
"""
import bpy,sys,json,time,hashlib,os,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--island',required=True);p.add_argument('--only');p.add_argument('--resume',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else sys.argv[1:]);out=ROOT/'docs/design/seven-policy-islands-blender-v1'/a.island;source=out/(a.island+'.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source_hash=sha(source)
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=2
views=[('hero','01_Hero_CommonScale',1280,64),('front','02_Front',1100,40),('back','03_Back',1100,40),('left','04_Left',1100,40),('right','05_Right',1100,40),('top','06_Top',1200,48)];recordpath=out/'render-record.json';records=json.loads(recordpath.read_text())['views']if recordpath.exists()else[]
for name,cam,width,samples in views:
 if a.only and name!=a.only:continue
 path=out/'renders'/(name+'.png');old=next((r for r in records if r['view']==name),None)
 if a.resume and path.exists()and old and old['sourceBlendSHA256']==source_hash and old['imageSHA256']==sha(path):continue
 scene.camera=bpy.data.objects[cam];scene.render.resolution_x=width;scene.render.resolution_y=round(width*.75);scene.cycles.samples=samples;scene.cycles.use_denoising=True;scene.render.filepath=str(path);started=time.time();bpy.ops.render.render(write_still=True)
 rec={'view':name,'file':'renders/'+name+'.png','camera':cam,'cameraPositionXYZ':list(scene.camera.location),'cameraRotationRadians':list(scene.camera.rotation_euler),'projection':scene.camera.data.type,'orthoScale':scene.camera.data.ortho_scale,'size':[scene.render.resolution_x,scene.render.resolution_y],'samples':samples,'seconds':round(time.time()-started,2),'sourceBlendSHA256':source_hash,'imageSHA256':sha(path)};records=[r for r in records if r['view']!=name]+[rec];recordpath.write_text(json.dumps({'blenderVersion':bpy.app.version_string,'engine':'Cycles CPU with OpenImageDenoise','geometryEditedDuringRender':False,'asset':a.island,'views':sorted(records,key=lambda r:[v[0]for v in views].index(r['view']))},indent=2)+'\n');print('VIEW_COMPLETE',a.island,name,rec['seconds'],flush=True)
assert sha(source)==source_hash;sys.stdout.flush();os._exit(0)
