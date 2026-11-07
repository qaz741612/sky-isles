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
stats={'expected':sum(v['status']=='passed'for v in a.values()),'skipped':sum(v['status']=='skipped'for v in a.values()),'unexpected':sum(v['status']not in['passed','skipped']for v in a.values()),'interrupted':sum(v['status']=='interrupted'for v in a.values()),'flaky':0}
assert stats['expected']+stats['skipped']==70 and stats['unexpected']==0
shutil.copyfile(W/'playwright-serial.json',O/'playwright-full-serial.json');shutil.copyfile(W/'playwright-panorama-recheck.json',O/'playwright-panorama-recheck.json')
(O/'playwright-final.json').write_text(json.dumps({'method':'70 logical cases from complete serial full-suite run, with both platform panorama cases independently rerun after correcting asynchronous test sampling to exact production entry/return events. Initial failure remains in the raw full report. Not72 distinct tests or a clean first pass. Four desktop touch-only cases retain original conditional skips. No production panorama behavior changed.','stats':stats,'originalFullRunStats':raw['stats'],'recheckStats':recheck['stats'],'replaced':replaced,'cases':list(a.values())},indent=2)+'\n')
print('Browser logical coverage:',stats['expected'],'passed,',stats['skipped'],'intentional skips,',stats['unexpected'],'unresolved; failed original and2 rechecks preserved')
