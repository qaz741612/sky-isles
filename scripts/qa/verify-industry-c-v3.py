"""Stream-download the pinned V3 GitHub delivery and verify bytes and SHA256."""
from pathlib import Path
import json,hashlib,sys,urllib.request,urllib.parse,time,concurrent.futures
root=Path('docs/previews/industry-youth-island-c-v3');commit=sys.argv[1]
assert len(commit)==40 and all(c in '0123456789abcdef'for c in commit)
base=f'https://raw.githubusercontent.com/qaz741612/sky-isles/{commit}/'
def fetch(path,expected=None):
 for attempt in range(3):
  try:
   digest=hashlib.sha256();size=0
   with urllib.request.urlopen(base+urllib.parse.quote(path,safe='/'),timeout=120)as response:
    while chunk:=response.read(1024*1024):digest.update(chunk);size+=len(chunk)
   row={'path':path,'bytes':size,'sha256':digest.hexdigest()}
   if expected:assert size==expected['bytes']and row['sha256']==expected['sha256'],'content mismatch '+path
   return row
  except Exception:
   if attempt==2:raise
   time.sleep(2)
manifest=root/'MANIFEST.json';m=json.loads(manifest.read_text());entry={'bytes':manifest.stat().st_size,'sha256':hashlib.sha256(manifest.read_bytes()).hexdigest()}
manifestReceipt=fetch(str(manifest),entry)
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(lambda v:fetch(v['path'],v),m['files']))
report={'repository':'qaz741612/sky-isles','commit':commit,'method':'Stream raw GitHub bytes and verify size + SHA256; no binary output','manifest':manifestReceipt,'verified':len(rows),'failed':0,'files':rows}
(root/'GITHUB-VERIFIED.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(f'GitHub download verified: {len(rows)} files + manifest, 0 mismatches')
