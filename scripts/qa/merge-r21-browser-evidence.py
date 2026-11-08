"""Publish only one complete fresh70-case report; archive failures separately."""
from pathlib import Path
import json,shutil,sys,hashlib
R=Path(__file__).resolve().parents[2];O=R/'docs/previews/bdeh-r21/final-qa/regression';W=R/'work/r21-final-qa';O.mkdir(exist_ok=True)
def cases(report):
 rows=[]
 def visit(suites):
  for suite in suites:
   for spec in suite.get('specs',[]):
    for test in spec['tests']:
     result=test['results'][-1];rows.append({'file':spec['file'],'title':spec['title'],'project':test['projectName'],'status':result['status'],'durationMs':result['duration']})
   visit(suite.get('suites',[]))
 visit(report['suites']);return rows
dist=R/(sys.argv[1]if len(sys.argv)>1 else'work/r21-final-visible-dist');port=int(sys.argv[2])if len(sys.argv)>2 else 4305
freeze={'port':port,'JSBundleSHA256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in(dist/'assets').glob('index-*.js')},'modelSHA256':{c:hashlib.sha256((dist/f'models/bdeh-r21/{c}.glb').read_bytes()).hexdigest()for c in'BDEH'}}
report=json.loads((W/'playwright-implementation-final.json').read_text());rows=cases(report);stats={**report['stats'],'interrupted':sum(r['status']=='interrupted'for r in rows)};assert len(rows)==70 and stats['expected']==66 and stats['skipped']==4 and stats['unexpected']==0 and stats['flaky']==0
assert all(r['status']in['passed','skipped']for r in rows)
assert sum(r['status']=='passed'for r in rows)==66
previous=json.loads((W/'playwright-implementation-final25.json').read_text());identity=lambda r:(r['file'],r['title'],r['project']);assert {identity(r)for r in rows}=={identity(r)for r in cases(previous)},'Do not drop or rename failed cases'
history=[];folder=O/'history';folder.mkdir(exist_ok=True)
for name in['playwright-serial.json','playwright-panorama-recheck.json','playwright-implementation-final25.json','playwright-final26-critical.json']:
 p=W/name
 if not p.exists():continue
 old=json.loads(p.read_text());shutil.copyfile(p,folder/name);history.append({'file':'history/'+name,'stats':old.get('stats'), 'note':'Earlier run only; never counted as final passing cases.'})
shutil.copyfile(W/'playwright-implementation-final.json',O/'playwright-implementation-final.json')
(O/'playwright-final.json').write_text(json.dumps({'method':'One complete fresh70-case suite against the final frozen spatial-index build, retries0. All66 reported passes and4 original desktop touch-only skips are from that run. No cherry-picked merged passing cases. Prior failed runs/rechecks are explicit history.','frozenBuild':freeze,'stats':stats,'cases':rows,'history':history},indent=2)+'\n')
print('Final fresh suite:66 passed,4 original conditional skips,0 failed; history preserved.')
