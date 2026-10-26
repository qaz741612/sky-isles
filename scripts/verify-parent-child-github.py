"""Verify all integrated game media and approved GLB by GitHub raw readback."""
from pathlib import Path
import json,hashlib,urllib.request,urllib.parse,sys,time
root=Path('docs/previews/parent-child-glb-integration-v1');commit=sys.argv[1]
if len(commit)!=40 or any(c not in '0123456789abcdef'for c in commit):raise ValueError('Complete commit SHA required')
results=[]
for f in json.loads((root/'media-manifest.json').read_text())['files']:
 url='https://raw.githubusercontent.com/qaz741612/sky-isles/'+commit+'/'+urllib.parse.quote(f['repoPath'],safe='/')
 for attempt in range(3):
  try:
   with urllib.request.urlopen(url,timeout=120)as response:b=response.read()
   break
  except Exception:
   if attempt==2:raise
   time.sleep(2)
 ok=len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['sha256'];results.append({**f,'url':url,'downloadedBytes':len(b),'verified':ok});print(f['repoPath'],ok,flush=True)
 if not ok:raise ValueError('GitHub artifact mismatch')
(root/'github-verification.json').write_text(json.dumps({'commit':commit,'method':'Download original committed bytes from GitHub; compare size and SHA256 for every final screenshot, video and public GLB.','total':len(results),'verified':sum(r['verified']for r in results),'files':results},ensure_ascii=False,indent=2)+'\n')
