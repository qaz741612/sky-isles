"""Serial final QA against one frozen build. No git mutations or deployment."""
from pathlib import Path
import json,time,subprocess,shutil,re,sys
R=Path(__file__).resolve().parents[2];W=R/'work/r21-final-qa';O=R/'docs/previews/bdeh-r21/final-qa';port=sys.argv[1]if len(sys.argv)>1 else'4305';dist=sys.argv[2]if len(sys.argv)>2 else'work/r21-final-visible-dist';label=sys.argv[3]if len(sys.argv)>3 else'final-visible';raw=W/f'playwright-implementation-{label}.json';progress=W/f'{label}-pipeline-progress.ndjson'
def note(stage,state):
 with progress.open('a')as f:f.write(json.dumps({'stage':stage,'state':state,'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})+'\n')
def run(name,args):
 note(name,'running')
 with(W/f'pipeline-{name}.log').open('w')as log:subprocess.run(args,cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True)
 note(name,'passed')
try:
 note('full-browser-regression','waiting for complete70-case report')
 while True:
  try:
   report=json.loads(raw.read_text());stats=report['stats'];break
  except(FileNotFoundError,json.JSONDecodeError,KeyError):time.sleep(5)
 assert stats['expected']==66 and stats['skipped']==4 and stats['unexpected']==0 and stats.get('interrupted',0)==0 and stats['flaky']==0,stats
 note('full-browser-regression','66passed4intentional-skips')
 shutil.copyfile(raw,W/'playwright-implementation-final.json')
 run('browser-evidence',['python','scripts/qa/merge-r21-browser-evidence.py',dist,port])
 check=(W/f'check-{label}.log').read_text();passed=int(re.search(r'pass\s+(\d+)',check)[1]);total=int(re.search(r'tests\s+(\d+)',check)[1]);assert passed==total and total>=93 and re.search(r'fail\s+0',check)and'built in'in check
 (O/'regression/npm-check.json').write_text(json.dumps({'command':'npm run check','unitTests':total,'passed':passed,'failed':0,'lint':'passed','productionBuild':'passed','log':'npm-check.log','scope':'Final source; actual command complete log preserved, no real-device or human art approval.'},indent=2)+'\n');shutil.copyfile(W/f'check-{label}.log',O/'regression/npm-check.log')
 if '--resume-after-captures' not in sys.argv[4:]:
  run('camera-cpu-native',['node','scripts/qa/profile-r21-spaces.mjs','4306','H',str(W/'H-final-native.json')])
  run('camera-cpu-indexed',['node','scripts/qa/profile-r21-spaces.mjs',port,'H',str(W/'H-final-indexed.json')])
  run('camera-cpu-comparison',['python','scripts/qa/compare-r21-camera-cpu.py',str(W/'H-final-native.json'),str(W/'H-final-indexed.json'),dist+'-native',dist])
  run('manual-input',['node','scripts/qa/check-r21-manual.mjs',port])
  run('final-game-captures',['node','scripts/qa/capture-r21-final.mjs',port,str(O/'game-after')])
 else:
  run('resume-source-preflight',['python','scripts/qa/audit-r21-final-evidence.py'])
  note('resume','Saved complete captures source-verified; restarting only performance and remaining evidence.')
 run('performance',['node','scripts/qa/measure-r21-final.mjs',port,dist])
 run('one-pointer-replay',['node','scripts/qa/replay-r21-final.mjs',port,'BDEH'])
 run('source-consistency',['python','scripts/qa/audit-r21-final-evidence.py'])
 run('comparison-boards',['python','scripts/qa/boards-r21-final.py'])
 note('pipeline','ready for human-model visual inspection by engineering agent; no art approval implied')
except Exception as e:
 note('pipeline','FAILED '+str(e)[:800]);raise
