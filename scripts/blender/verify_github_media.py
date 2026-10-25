"""Read back committed Blender assets from GitHub and compare exact bytes/SHA256."""
import hashlib,json,sys,time,urllib.parse,urllib.request
from pathlib import Path
root=Path('docs/design/parent-child-blender-model-v1')
commit=sys.argv[1]
if len(commit)!=40 or any(c not in '0123456789abcdef' for c in commit):raise ValueError('Expected complete commit SHA')
entries=json.loads((root/'media-manifest.json').read_text())['files']
bundle=json.loads((root/'bundle-manifest.json').read_text())
entries.append({'path':bundle['file'],'bytes':bundle['bytes'],'sha256':bundle['sha256']})
results=[]
for d in entries:
 url='https://raw.githubusercontent.com/qaz741612/sky-isles/'+commit+'/'+urllib.parse.quote(str(root/d['path']),safe='/')
 for attempt in range(3):
  try:
   with urllib.request.urlopen(url,timeout=90)as response:data=response.read()
   break
  except Exception:
   if attempt==2:raise
   time.sleep(2)
 verified=len(data)==d['bytes'] and hashlib.sha256(data).hexdigest()==d['sha256']
 results.append({**d,'url':url,'downloadedBytes':len(data),'verified':verified})
 print(d['path'],verified,flush=True)
 if not verified:raise ValueError('GitHub artifact content mismatch')
(root/'github-verification.json').write_text(json.dumps({'commit':commit,'verified':len(results),'total':len(entries),'method':'Download committed raw GitHub bytes; compare file size and SHA256. Includes blend, GLB, 8 original renders, contact sheet, comparison HTML and ZIP.','files':results},ensure_ascii=False,indent=2)+'\n')
