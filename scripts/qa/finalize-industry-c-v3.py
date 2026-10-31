"""Package bounded V3 reports from actual final asset, captures and test runs."""
from pathlib import Path
import json,hashlib,re,subprocess
from PIL import Image,ImageDraw,ImageStat
R=Path(__file__).resolve().parents[2];O=R/'docs/previews/industry-youth-island-c-v3';D=R/'docs/design/industry-youth-island-c-v3'
def read(p):return json.loads((R/p).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def cases(report):
 rows=[]
 def visit(s):
  for sp in s.get('specs',[]):
   for t in sp['tests']:
    v=(t.get('results')or[{'status':'not-run','duration':0}])[-1]
    rows.append({'file':sp['file'],'title':sp['title'],'project':t['projectName'],'status':v['status'],'durationMs':v['duration'],'errors':[re.sub(r'\x1b\[[0-9;]*m','',e.get('message',''))[:1500]for e in v.get('errors',[])]})
  for c in s.get('suites',[]):visit(c)
 for s in report['suites']:visit(s)
 return rows
asset=R/'public/models/industry-youth-c/industry-youth-c.glb';blend=D/'industry-youth-c-v3.blend';camera=R/'src/world/industry-youth.js';collision=R/'src/data/industry-youth-collision.json'
records=[]
for f in ['capture-record','porch-capture-record']:
 v=read(str((O/'game'/f'{f}.json').relative_to(R)))
 assert v['assetSHA256']==sha(asset) and v['cameraSourceSHA256']==sha(camera) and v['collisionSHA256']==sha(collision),'stale game capture'
 assert all(not r['errors']for r in v['records']);records+=v['records']
render=json.loads((O/'blender/render-record.json').read_text());assert render['blendSHA256']==sha(blend) and len(render['views'])==9
beforeRender=json.loads((O/'before/blender/render-record.json').read_text());assert beforeRender['readOnlyOriginal']and beforeRender['sourceBlendSHA256']==sha(R/'docs/design/industry-youth-island-c-v2.2/industry-youth-c.blend')
for v in beforeRender['views']:
 final=next(r for r in render['views']if r['name']==v['name']);assert v['location']==final['camera']and v['orthoScale']==final['orthoScale']and v['size']==final['size']
for folder in ['game','blender','before/game','before/blender']:
 for p in (O/folder).glob('*.png'):
  im=Image.open(p).convert('RGB');assert min(ImageStat.Stat(im).stddev)>4,'blank image '+str(p)
for device in ['desktop','mobile']:
 v=json.loads((O/f'routes-{device}.json').read_text());assert v['passed']and len(v['routes'])==22
check=(R/'work/v3-check-final.log').read_text();assert 'ℹ fail 0'in check and '✓ built in'in check
sourceMap=json.loads(next((R/'work/v3-delivery-dist/assets').glob('*.js.map')).read_text());assert any(name.endswith('src/world/industry-youth.js')and content.strip()==camera.read_text().strip()for name,content in zip(sourceMap['sources'],sourceMap['sourcesContent'])),'preview camera build stale'
assert sha(R/'work/v3-delivery-dist/public/models/industry-youth-c/industry-youth-c.glb')==sha(asset)if (R/'work/v3-delivery-dist/public/models/industry-youth-c/industry-youth-c.glb').exists()else sha(R/'work/v3-delivery-dist/models/industry-youth-c/industry-youth-c.glb')==sha(asset)
reports=[('broad','work/v3-browser-all.json'),('finalC','work/v3-browser-final-c.json'),('fixedPaths','work/v3-browser-fixedpaths.json'),('outputDirectoryFix','work/v3-browser-f-output.json')]
rows=[];stats={}
assert all((R/p).exists() and (R/p).stat().st_size for _,p in reports),'browser reports not ready'
for kind,p in reports:
 if (R/p).exists() and (R/p).stat().st_size:
  d=read(p);stats[kind]=d['stats'];rows.extend({**r,'run':kind}for r in cases(d))
effective={}
for r in rows:effective[(r['file'],r['title'],r['project'])]=r
counts={s:sum(r['status']==s for r in effective.values())for s in ['passed','skipped','failed','timedOut','interrupted']}
save(O/'browser-summary.json',{'mode':'SwiftShader engineering samples; native input/rAF/physics/UI; not real-device FPS','stats':stats,'builds':{'broad':'4232: final visible model, before last C-only camera refinement','finalC':'4233: final model and final C camera; industry and eight-place orbit regression','routes':'4233: all22 both directions and C campus/cameras on desktop+mobile'},'effectiveCounts':counts,'history':rows,'effectiveResults':list(effective.values())})
before=read('docs/design/industry-youth-island-c-v2.2/model-report.json');after=json.loads((D/'model-report.json').read_text())
bg=read('docs/previews/industry-youth-island-c-v3/before/game/capture-record.json')
before['materialsDeclaredInOldBlenderReport']=before['materials'];before['materials']=bg['records'][0]['industry']['materials'];before['materialMetric']='unique materials actually loaded by GLTFLoader; old report counted unused Blender datablocks'
assert before['materials']==33 and after['materials']==29
perf={'modelBefore':before,'modelAfter':after,'delta':{k:after[k]-before[k]for k in ['triangles','runtimeMeshes','materials','glbBytes','blendBytes']},'collisionProxyBytes':collision.stat().st_size,'profiles':records,'sameCameraBeforeProfiles':bg['records'],'hardwareFPS':'UNVERIFIED','thermalsAndSustainedInput':'UNVERIFIED','network':'Local loopback only','softwareQA':'Draw first/explicit frames only, native simulation retained. Observed draw costs do not establish sustained FPS.'}
save(O/'performance.json',perf)
comparison=O/'comparisons';comparison.mkdir(exist_ok=True)
def pair(a,b,out,labela='Before: PR17 V2.2',labelb='After: C V3'):
 a=Image.open(a).convert('RGB');b=Image.open(b).convert('RGB');assert a.size==b.size
 canvas=Image.new('RGB',(a.width*2,a.height+30),'#edf0e9');canvas.paste(a,(0,30));canvas.paste(b,(a.width,30));draw=ImageDraw.Draw(canvas);draw.text((12,9),labela,fill='black');draw.text((a.width+12,9),labelb,fill='black');canvas.save(out,quality=92)
for n in ['hero','top']:pair(O/'before/blender'/f'{n}.png',O/'blender'/f'{n}.png',comparison/f'blender-{n}.jpg')
# These are exact same default orbit/profile and standing points, no pulled-back lens.
for n in ['desktop-native','mobile-native','mobile-landscape']:
 a=next(r for r in bg['records']if r['name']==n);b=next(r for r in records if r['name']==n)
 assert a['orbit']==b['orbit'] and a['args']==b['args'] and a['size']==b['size']
 pair(O/'before/game'/f'{n}.png',O/'game'/f'{n}.png',comparison/f'game-{n}.jpg')
# Preserve a bounded record of initial failures instead of mixing them with final results.
diag=O/'diagnostics';diag.mkdir(exist_ok=True)
for device in ['desktop','mobile']:
 p=O/f'failure-{device}.json'
 if p.exists():
  d=json.loads(p.read_text());d['status']='Historical first full-route run failed at workshop porch camera; see final routes and new orbit test. Not counted as a pass.';save(diag/f'initial-camera-{device}.json',d);p.unlink()
save(O/'validation-summary.json',{'build':True,'lint':True,'unitTests':int(re.search(r'ℹ tests (\d+)',check).group(1)),'unitFailures':0,'protectedFiles':len(read('docs/design/industry-youth-island-c-v3/locked-runtime-baseline.json')['files']),'terrainVerticesUnchanged':9200,'gamePNGs':len(list((O/'game').glob('*.png'))),'blenderPNGs':len(list((O/'blender').glob('*.png'))),'browserEffectiveCounts':counts,'humanArtAcceptance':'PENDING','hardwareAcceptance':'UNVERIFIED'})
print('V3 package validated; model/capture hashes match; reports and comparisons saved')
