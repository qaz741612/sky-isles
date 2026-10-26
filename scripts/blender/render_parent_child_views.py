"""Render all eight final views from the saved editable Blender file. MIT."""
import bpy,bmesh,sys,json,hashlib,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/(sys.argv[sys.argv.index('--out')+1] if '--out' in sys.argv else 'docs/design/parent-child-blender-model-v1');SOURCE=OUT/'parent-child-centre.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));source_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest();scene=bpy.context.scene
model=bpy.data.objects['ParentChildCentre_MODEL'];deps=bpy.context.evaluated_depsgraph_get();audit=[]
for obj in model.children_recursive:
    if obj.type!='MESH':continue
    evaluated=obj.evaluated_get(deps);m=evaluated.to_mesh();bm=bmesh.new();bm.from_mesh(m)
    opened=sum(not edge.is_manifold for edge in bm.edges);volume=bm.calc_volume(signed=True)
    if opened or volume<=0:audit.append({'name':obj.name,'nonManifoldEdges':opened,'signedLocalVolume':volume})
    bm.free();evaluated.to_mesh_clear()
(OUT/'solid-geometry-audit.json').write_text(json.dumps({'sourceBlendSHA256':source_sha,'checkedMeshObjects':sum(o.type=='MESH'for o in model.children_recursive),'issues':audit,'note':'Evaluated editable solid components; flowers and structural joints may overlap intentionally. Not a building-code or game-collision certification.'},indent=2))
if audit:raise RuntimeError('Repair solid geometry before rendering: '+str(audit[:12]))
views=[('hero','01_ReferenceHero',1600,96),('front','02_Front',1400,64),('back','03_Back',1400,64),('left','04_Left',1400,64),('right','05_Right',1400,64),('top','06_Top',1400,64),('eaves','07_SoffitDetail',1400,64),('player','08_PlayerHeight',1400,64)]
only=sys.argv[sys.argv.index('--only')+1] if '--only' in sys.argv else None
records=json.loads((OUT/'render-record.json').read_text())['views'] if only and (OUT/'render-record.json').exists() else []
for name,camera,width,samples in views:
    if only and name!=only:continue
    scene.camera=bpy.data.objects[camera];scene.render.resolution_x=width;scene.render.resolution_y=round(width*741/1082);scene.cycles.samples=samples;scene.cycles.use_denoising=True
    if name=='top' and '--fixed-framing' not in sys.argv:
        bounds=json.loads((OUT/'model-report.json').read_text())['bounds'];a,b=bounds['min'],bounds['max'];scene.camera.location.x=(a[0]+b[0])/2;scene.camera.location.y=(a[1]+b[1])/2;scene.camera.data.ortho_scale=max((b[0]-a[0])*1.08,(b[1]-a[1])*scene.render.resolution_x/scene.render.resolution_y*1.08)
    records=[r for r in records if r['file']!='renders/'+name+'.png']
    path=OUT/'renders'/(name+'.png');scene.render.filepath=str(path);started=time.time();bpy.ops.render.render(write_still=True)
    records.append({'file':str(path.relative_to(OUT)),'camera':camera,'cameraPositionXYZ':list(scene.camera.location),'cameraRotationRadians':list(scene.camera.rotation_euler),'projection':scene.camera.data.type,'lensMM':scene.camera.data.lens,'orthoScale':scene.camera.data.ortho_scale,'size':[scene.render.resolution_x,scene.render.resolution_y],'samples':samples,'seconds':round(time.time()-started,2),'sourceBlendSHA256':source_sha,'imageSHA256':hashlib.sha256(path.read_bytes()).hexdigest()})
    (OUT/'render-record.json').write_text(json.dumps({'blender':bpy.app.version_string,'engine':'Cycles CPU + OpenImageDenoise','views':sorted(records,key=lambda r:[v[0]for v in views].index(Path(r['file']).stem))},indent=2));print('FINAL_VIEW_SAVED',name,flush=True)
print('ALL_EIGHT_FINAL_VIEWS_COMPLETE',flush=True)
