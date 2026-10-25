"""Verify committed media and original models by downloading from GitHub."""
import json,hashlib,urllib.request,urllib.parse,sys,time
from pathlib import Path
root=Path('docs/previews/transport-station-glb-integration-v1');commit=sys.argv[1]
files=[{'path':str(root/d['path']),'bytes':d['bytes'],'sha256':d['sha256']} for d in json.load(open(root/'media-manifest.json'))['files']]
for p in ['public/prototypes/transport-station/transport-station.glb','docs/design/transport-station-blender-prototype/transport-station.blend']:
 b=Path(p).read_bytes();files.append({'path':p,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
results=[]
for d in files:
 url='https://raw.githubusercontent.com/qaz741612/sky-isles/'+commit+'/'+urllib.parse.quote(d['path'],safe='/')
 for attempt in range(3):
  try:
   with urllib.request.urlopen(url,timeout=120) as r:b=r.read()
   break
  except Exception:
   if attempt==2:raise
   time.sleep(2)
 ok=len(b)==d['bytes'] and hashlib.sha256(b).hexdigest()==d['sha256'];results.append({**d,'url':url,'downloadedBytes':len(b),'verified':ok});print(d['path'],ok,flush=True)
 assert ok,'GitHub content mismatch'
(root/'github-media-verification.json').write_text(json.dumps({'commit':commit,'verified':len(results),'total':len(files),'method':'Downloaded committed raw GitHub files and compared exact byte count and SHA256. Includes all 8 PNGs, native MP4 and both original model files.','files':results},ensure_ascii=False,indent=2)+'\n')
