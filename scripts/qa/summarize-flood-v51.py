"""Versioned incremental evidence; never hide unsuccessful or interrupted runs."""
from pathlib import Path
import json,shutil,re,hashlib
R=Path(__file__).resolve().parents[2];O=R/'docs/previews/flood-control-island-g-v5-1';T=O/'regression-evidence';T.mkdir(exist_ok=True)
sha=lambda path:hashlib.sha256((R/path).read_bytes()).hexdigest()
sources=[
 ('broad64','playwright-final.json',4261,'73655 triangles, original G camera; two rendering timeouts retained'),
 ('hydraulic10','playwright-locked.json',4263,'74207 triangles; scoped geometry regression'),
 ('hydraulic-app2','playwright-app-locked.json',4263,'desktop rendering and panorama timeout rechecks'),
 ('supported10','playwright-delivery.json',4264,'74463 frozen geometry, original G camera'),
 ('supported-app2','playwright-app-delivery.json',4264,'74463 frozen geometry, original G camera'),
 ('cancelled-driver','playwright-camera-final.json',4265,'Intentionally interrupted: missing requested test filename and software-render budget flag; superseded by corrected10. Its skipped cases are NOT final acceptance.'),
 ('final-camera10','playwright-camera-corrected.json',4265,'Frozen74463 geometry plus G-only silhouette/idle stability fix, correct G tests and software QA'),
 ('final-camera-app2','app-camera-corrected.json',4265,'Same final runtime; real WebGL non-uniform pixels and console errors')]
rows={};runs=[]
def walk(s,run):
 for spec in s.get('specs',[]):
  for t in spec['tests']:
   result=t['results'][-1]if t['results']else{};key=(spec['file'],spec['title'],t['projectName'])
   rows[key]={'file':spec['file'],'title':spec['title'],'project':t['projectName'],'status':t['status'],'run':run,'durationMs':result.get('duration'),'error':result.get('error',{}).get('message')}
 for child in s.get('suites',[]):walk(child,run)
for name,file,port,purpose in sources:
 p=R/'work/g-v51'/file;d=json.loads(p.read_text());assert d.get('stats'),file
 if name=='final-camera10':assert d['stats']['expected']==10 and d['stats']['unexpected']==0
 if name=='final-camera-app2':assert d['stats']['expected']==2 and d['stats']['unexpected']==0
 shutil.copyfile(p,T/(name+'.json'));runs.append({'name':name,'port':port,'stats':d['stats'],'purpose':purpose});walk(d,name)
counts={key:sum(r['status']==key for r in rows.values())for key in ['expected','skipped','unexpected','flaky']};assert len(rows)==66 and counts=={'expected':62,'skipped':4,'unexpected':0,'flaky':0},(len(rows),counts)
log=(R/'work/g-v51/check-camera-final.log').read_text();unit={k:int(re.search(r'(?:#|ℹ) '+k+r' (\d+)',log).group(1))for k in ['tests','pass','fail','skipped']};assert unit['tests']==76 and unit['pass']==76
shutil.copyfile(R/'work/g-v51/check-camera-final.log',T/'build-lint-unit.log');shutil.copyfile(R/'work/g-v51/routes-camera-final.log',T/'routes.log')
routes={dev:json.loads((O/f'routes-{dev}.json').read_text())for dev in ['desktop','mobile']}
water={dev:json.loads((O/'regression-camera'/f'water-interactions-{dev}.json').read_text())for dev in routes}
wet={dev:json.loads((O/'regression-camera'/f'wet-recovery-{dev}.json').read_text())for dev in routes}
assert all(r['passed']and len(r['routes'])==22 and len(r['cameras'])==160 for r in routes.values())
assert all(r['passed']and len(r['rows'])==9 and r['nativeEntryCamera']['clearProbes']==6 and r['nativeEntryCamera']['panoramaRestored']for r in wet.values())
report={'baseCommit':'8849b89e99163c179973a31571498115c6c80e7c','finalAssetSHA256':sha('public/models/flood-control-g/flood-control-g.glb'),'finalGModuleSHA256':sha('src/world/flood-control.js'),'method':'Incremental regression, NOT one final66-case run. Original64 on first art model; all ten affected G/world/panorama cases plus app2 rerun on final frozen geometry and G-local camera. Latest result per exact file/title/project; all unsuccessful/interrupted reports retained. Common player/camera/main, F/A/C, roads and policy files byte-protected.','build':{'passed':True,'lintPassed':True,'unit':unit,'log':'regression-evidence/build-lint-unit.log'},'runs':runs,'effectiveCaseCount':len(rows),'effectiveCounts':counts,'cases':list(rows.values()),'strictRealPlayer':{dev:{'routes':len(r['routes']),'bidirectional':True,'noJump':True,'cameraSamples':len(r['cameras']),'checkpoint':r['extendedForecourtCheckpoint'],'panoramaRestores':r['panoramaRestores'],'forcedRecovery':r['forcedRecovery'],'routeStartsTeleported':True,'fixedHz':60}for dev,r in routes.items()},'waterEdges':{dev:{'actualPushes':sum(bool(x.get('blocked'))for x in j['waterEdge']),'midpointsNotPushed':sum(bool(x.get('skipped'))for x in j['waterEdge']),'minFiniteRailDistance':min(x['minimumDistance']for x in j['waterEdge']if x.get('blocked')),'modelPolicyPicking':j['modelPicking'],'panoramaRestores':j['panoramaRestores'],'forcedRecovery':j['forcedFallRecovery']}for dev,j in water.items()},'wetFalls':{dev:{'actualWetFalls':len(j['rows']),'allReturnDryCheckpoint':True,'progressPreserved':True,'nativeEntryCamera':j['nativeEntryCamera']}for dev,j in wet.items()},'limits':['Four desktop touch-only cases remain inapplicable skips; corresponding mobile cases pass.','Four water-edge midpoints lack isolated dry approach; NOT counted as actual browser pushes. All segments have additional unit sweeps.','Nine wet falls deliberately start below water to test recovery; not a claim that every possible manual jump was walked.','Fixed60Hz real Player with route-start teleports is not a continuous human tour.','G camera unit matrix additionally checks six silhouette rays and idle stability; real browser entry verifies six rays and panorama camera state. This does not prove every freely chosen hand-controlled composition.','SwiftShader, DPR1 and software QA render scheduling do not establish real-device FPS, heat or long-term touch comfort.','Art quality, C V3 style threshold and cultural interpretation require human acceptance; no automatic art pass is claimed.']}
(O/'test-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('76 units; effective62 Playwright passes,4 inapplicable skips,0 unresolved; run provenance saved')
