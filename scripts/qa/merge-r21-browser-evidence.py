"""Keep the failed full run and matching corrected rechecks separately visible."""
from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parents[2];O=R/'docs/previews/bdeh-r21/final-qa/regression';W=R/'work/r21-final-qa'
def cases(report):
 result={}
 def walk(suites):
  for suite in suites:
   for spec in suite.get('specs',[]):
    for test in spec['tests']:
     key=(spec['file'],spec['title'],test['projectName']);result[key]={'file':key[0],'title':key[1],'project':key[2],'status':test['results'][-1]['status'],'durationMs':test['results'][-1]['duration']}
   walk(suite.get('suites',[]))
 walk(report['suites']);return result
raw=json.loads((W/'playwright-serial.json').read_text());recheck=json.loads((W/'playwright-panorama-recheck.json').read_text());a=cases(raw);b=cases(recheck);assert len(a)==70 and len(b)==2
assert all(v['status']=='passed'for v in b.values())and recheck['stats']['unexpected']==0
assert all(k in a for k in b)
replaced=[{'before':a[k],'recheck':v}for k,v in b.items()];a.update(b)
finalReport=json.loads((W/'playwright-implementation-final.json').read_text());a=cases(finalReport);assert len(a)==70;assert finalReport['stats']['unexpected']==0 and finalReport['stats']['interrupted']==0
shutil.copyfile(W/'playwright-implementation-final.json',O/'playwright-implementation-final.json')
stats={'expected':sum(v['status']=='passed'for v in a.values()),'skipped':sum(v['status']=='skipped'for v in a.values()),'unexpected':sum(v['status']not in['passed','skipped']for v in a.values()),'interrupted':sum(v['status']=='interrupted'for v in a.values()),'flaky':0}
assert stats['expected']+stats['skipped']==70 and stats['unexpected']==0
shutil.copyfile(W/'playwright-serial.json',O/'playwright-full-serial.json');shutil.copyfile(W/'playwright-panorama-recheck.json',O/'playwright-panorama-recheck.json')
(O/'playwright-final.json').write_text(json.dumps({'method':'70 logical cases from a complete fresh full-suite run against final candidate6 (including real held-input wall regression). Earlier candidate5 full-suite and2 corrected panorama rechecks remain historical. Final reported cases are wholly from candidate6, not a cherry-picked merged pass. Four desktop touch-only cases retain original conditional skips. No production panorama behavior changed.','stats':stats,'originalFullRunStats':raw['stats'],'recheckStats':recheck['stats'],'finalFullRunStats':finalReport['stats'],'replaced':replaced,'cases':list(a.values())},indent=2)+'\n')
print('Browser logical coverage:',stats['expected'],'passed,',stats['skipped'],'intentional skips,',stats['unexpected'],'unresolved; failed original and2 rechecks preserved')
