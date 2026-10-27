"""Actual same-source Cycles renders; strict desktop/mobile camera simulations. MIT."""
import bpy,sys,os,json,hashlib,time,argparse,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/design/transport-elevated-station-v9-prototype';p=argparse.ArgumentParser();p.add_argument('--only');p.add_argument('--draft',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else sys.argv[1:]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=OUT/'transport-station-v9.blend';h=sha(source);bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=2;file=OUT/'render-record.json';records=json.loads(file.read_text())['views']if file.exists()else[]
views=[('hero',1440,1080,64),('front',1200,900,40),('back',1200,900,40),('left',1200,900,40),('right',1200,900,40),('top',1440,1080,48),('train-side',1440,1080,48),('player-desktop',1440,900,48),('player-mobile',720,1280,48)]
for name,w,hgt,samples in views:
 if a.only and name not in a.only.split(','):continue
 cam=bpy.data.objects[name];path=OUT/'renders'/(name+'.png');old=next((v for v in records if v['view']==name),None)
 if not a.draft and path.exists()and old and old['sourceBlendSHA256']==h and old['imageSHA256']==sha(path):continue
 scene.camera=cam;scene.render.resolution_x=w if not a.draft else round(w*.65);scene.render.resolution_y=hgt if not a.draft else round(hgt*.65);scene.cycles.samples=samples if not a.draft else 16;scene.render.filepath=str(path if not a.draft else OUT/('draft-'+name+'.png'));started=time.time();bpy.ops.render.render(write_still=True)
 if not a.draft:
  rec={'view':name,'file':'renders/'+name+'.png','size':[w,hgt],'cameraPositionBlenderXYZ':list(cam.location),'cameraRotationRadians':list(cam.rotation_euler),'projection':cam.data.type,'orthoScale':cam.data.ortho_scale if cam.data.type=='ORTHO'else None,'lensMillimetres':cam.data.lens,'sensorFit':cam.data.sensor_fit,'sensorHeight':cam.data.sensor_height,'simulationOnly':bool(cam.get('simulationOnly',False)),'distance':cam.get('distance'),'pitch':cam.get('pitch'),'yaw':cam.get('yaw'),'verticalFOV':cam.get('fov'),'targetWorldXYZ':list(cam.get('targetWorldXYZ',[])),'engine':'Blender Cycles CPU / OIDN','samples':samples,'seconds':round(time.time()-started,2),'sourceBlendSHA256':h,'imageSHA256':sha(path)};records=[v for v in records if v['view']!=name]+[rec];file.write_text(json.dumps({'source':'transport-station-v9.blend','sameSourceGeometry':True,'gameScreenshots':False,'views':records},ensure_ascii=False,indent=2)+'\n')
 print('VIEW_COMPLETE',name,round(time.time()-started,2),flush=True)
assert sha(source)==h;sys.stdout.flush();os._exit(0)
