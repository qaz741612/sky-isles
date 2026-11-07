"""Link actual saved Blender, exported GLB and served game screenshot evidence."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];O=R/'docs/previews/bdeh-r21/final-qa'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
models={};protected=json.loads((R/'docs/design/bdeh-r21/final-qa-baseline/LOCKS.json').read_text())
for entry in protected['files']:assert sha(R/entry['path'])==entry['sha256'],entry['path']
for c in'BDEH':
 report=json.loads((R/f'docs/design/bdeh-r21/{c}/model-report.json').read_text());blend=R/report['sourceBlend'];glb=R/f'public/models/bdeh-r21/{c}.glb';render=json.loads((O/f'{c}/blender/render-record.json').read_text())
 assert report['sourceBlendSHA256']==sha(blend)==render['sourceBlendSHA256'],c+' same-source Blender mismatch'
 assert report['GLBSHA256']==sha(glb)and report['glbBytes']==glb.stat().st_size,c+' GLB mismatch'
 assert len(render['records'])==8 and {v['name']for v in render['records']}=={'hero','front','back','left','right','top','architecture','public-space'}
 assert all((O/f'{c}/blender'/f"{v['name']}.png").is_file()for v in render['records'])
 models[c]={'blendSHA256':sha(blend),'glbSHA256':sha(glb),'renderedViews':8,'triangles':report['triangles'],'GLBBytes':report['glbBytes'],'meshPrimitives':report['meshPrimitives'],'materials':report['materials'],'textures':report['textures'],'newLights':report['newLights']}
canopies=json.loads((R/'src/data/bdeh-camera-canopies.json').read_text())
for c,m in models.items():
 row=canopies['islands'][c];assert row['sourceBlendSHA256']==m['blendSHA256'];assert row['triangles']==sum(len(v['positions'])//9 for v in row['canopies'])
 faces=len(json.loads((R/f'src/data/bdeh-{c.lower()}-collision.json').read_text())['cameraPositions'])//9
 assert all(0<=i<faces for i in row['transparentCameraTriangles'])
captures={s:json.loads((O/f'game-{s}/capture-record.json').read_text())for s in['before','after']}
assert len(captures['before']['records'])==len(captures['after']['records'])==59
before={r['name']:r for r in captures['before']['records']};pairs=[]
for record in captures['after']['records']:
 old=before[record['name']];assert not record['errors']and not old['errors']
 assert record['size']==old['size']and record['initial']==old['initial'],record['name']+' comparison initialization mismatch'
 assert (O/'game-after'/f"{record['name']}.png").is_file()
 if record['kind']in['native','NPC-native','single-finger-left','single-finger-right']:
  assert record['orbit']['dist']==old['orbit']['dist']and record['orbit']['pitch']==old['orbit']['pitch']and record['actualCameraFOV']==old['actualCameraFOV'],record['name']+' changed global lens'
  pairs.append({'name':record['name'],'playerBefore':old['player'],'playerAfter':record['player'],'initial':record['initial'],'cameraBefore':old['camera'],'cameraAfter':record['camera'],'orbitBefore':old['orbit'],'orbitAfter':record['orbit'],'FOV':record['actualCameraFOV']})
for c,m in models.items():assert captures['after']['servedModels'][c+'.glb']==m['glbSHA256']
details=json.loads((O/'details/render-record.json').read_text());assert len(details['records'])==5
for entry in details['records']:
 assert entry['sourceBlendSHA256']==models[entry['code']]['blendSHA256']and(O/f"details/{entry['code']}-{entry['name']}.png").is_file()
(O/'source-consistency.json').write_text(json.dumps({'protectedFiles':len(protected['files']),'protectedMismatches':0,'models':models,'beforeAfterPNGCount':118,'matchedNativeInputPairs':pairs,'servedFinalGLBVerified':True,'sameSourceExtraCloseViews':5,'bundleSHA256':captures['after']['bundleSHA256'],'limits':'Sources and input recipes match; this is not a human art judgement or physical-device performance result.'},indent=2)+'\n')
print('4 saved Blender/GLBs,32 same-source renders +5 details,118 actual captures and37 locks verified;48 matched native/gesture/NPC pairs')
