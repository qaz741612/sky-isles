"""Download a committed asset manifest and verify every upload by bytes/SHA256. MIT."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import argparse,hashlib,json,urllib.request,urllib.parse,time
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/design/seven-policy-islands-blender-v1';p=argparse.ArgumentParser();p.add_argument('--commit',required=True);a=p.parse_args();assert len(a.commit)==40 and all(c in '0123456789abcdef'for c in a.commit)
base='https://raw.githubusercontent.com/qaz741612/sky-isles/'+a.commit+'/';stash=ROOT/'work/seven-github-verification'/a.commit;stash.mkdir(parents=True,exist_ok=True)
def fetch(path):
 url=base+urllib.parse.quote(path,safe='/');last=None
 for attempt in range(3):
  try:
   with urllib.request.urlopen(url,timeout=90)as r:data=r.read();assert r.status==200
   dest=stash/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
   return data
  except Exception as e:last=e;time.sleep(1+attempt)
 raise last
manifest_path=str((OUT/'media-manifest.json').relative_to(ROOT));raw=fetch(manifest_path);assert raw==(OUT/'media-manifest.json').read_bytes();manifest=json.loads(raw);entries=list(manifest['files'])
# Original user references are also verified independently from the uploaded source manifest.
refs=json.loads((ROOT/'docs/references/policy-islands/manifest.json').read_text())
for r in refs['entries']:entries.append({'repoPath':r['projectPath'],'bytes':r['bytes'],'sha256':r['sha256']})
def check(item):
 data=fetch(item['repoPath']);digest=hashlib.sha256(data).hexdigest();assert len(data)==item['bytes'] and digest==item['sha256'],item['repoPath'];return {'repoPath':item['repoPath'],'bytes':len(data),'sha256':digest,'passed':True}
results=[]
with ThreadPoolExecutor(max_workers=4)as pool:
 futures={pool.submit(check,item):item['repoPath']for item in entries}
 for f in as_completed(futures):
  r=f.result();results.append(r);print('GITHUB_DOWNLOAD_VERIFIED',r['repoPath'],flush=True)
report={'repository':'qaz741612/sky-isles','verifiedCommit':a.commit,'method':'HTTPS download from raw.githubusercontent.com at exact commit, saved locally then exact size/SHA256 comparison; no binary contents printed.','manifestSHA256':hashlib.sha256(raw).hexdigest(),'allPassed':True,'filesVerified':len(results),'totalBytes':sum(r['bytes']for r in results),'results':sorted(results,key=lambda r:r['repoPath'])};(OUT/'github-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='results'},ensure_ascii=False))
