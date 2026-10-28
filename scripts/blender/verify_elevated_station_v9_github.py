"""Download exact committed prototype files and compare actual bytes/SHA256. MIT."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,hashlib,argparse,urllib.request,urllib.parse,time
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/design/transport-elevated-station-v9-prototype';p=argparse.ArgumentParser();p.add_argument('--commit',required=True);a=p.parse_args();assert len(a.commit)==40 and all(c in '0123456789abcdef'for c in a.commit);base='https://raw.githubusercontent.com/qaz741612/sky-isles/'+a.commit+'/';dest=ROOT/'work/transport-v9-github-verification'/a.commit

def fetch(path):
 for attempt in range(3):
  try:
   with urllib.request.urlopen(base+urllib.parse.quote(path,safe='/'),timeout=120)as r:b=r.read();assert r.status==200
   q=dest/path;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b);return b
  except Exception:
   if attempt==2:raise
   time.sleep(attempt+1)
manifest=fetch(str((OUT/'media-manifest.json').relative_to(ROOT)));assert manifest==(OUT/'media-manifest.json').read_bytes();entries=json.loads(manifest)['files']
def check(r):
 b=fetch(r['repoPath']);h=hashlib.sha256(b).hexdigest();assert len(b)==r['bytes']and h==r['sha256'],r['repoPath'];return {'repoPath':r['repoPath'],'bytes':len(b),'sha256':h,'passed':True}
results=[]
with ThreadPoolExecutor(max_workers=4)as pool:
 for future in as_completed([pool.submit(check,r)for r in entries]):
  r=future.result();results.append(r);print('GITHUB_VERIFIED',r['repoPath'],flush=True)
report={'repository':'qaz741612/sky-isles','verifiedCommit':a.commit,'allPassed':True,'filesVerified':len(results),'totalBytes':sum(r['bytes']for r in results),'method':'Exact GitHub raw HTTPS downloads saved to work, compared by file length and SHA256. No binary printed.','results':sorted(results,key=lambda r:r['repoPath'])};(OUT/'github-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='results'},ensure_ascii=False))
