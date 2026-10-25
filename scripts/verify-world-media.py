"""Download committed GitHub media and compare with the committed local manifest."""
import concurrent.futures,hashlib,json,sys,time,urllib.request
from pathlib import Path
commit=sys.argv[1];root=Path('docs/previews/eight-islands-world-redesign-v1')
base=f'https://raw.githubusercontent.com/qaz741612/sky-isles/{commit}/{root.as_posix()}/'
manifest_bytes=(root/'media-manifest.json').read_bytes()
remote_manifest=urllib.request.urlopen(base+'media-manifest.json',timeout=60).read()
assert remote_manifest==manifest_bytes,'Uploaded manifest differs'
manifest=json.loads(manifest_bytes)
def check(item):
    for attempt in range(3):
        try:
            digest=hashlib.sha256();count=0
            with urllib.request.urlopen(base+item['path'],timeout=120) as response:
                while chunk:=response.read(1024*1024):digest.update(chunk);count+=len(chunk)
            result={'path':item['path'],'bytes':count,'sha256':digest.hexdigest(),'matches':count==item['bytes'] and digest.hexdigest()==item['sha256']}
            assert result['matches'],f'Upload mismatch: {result}'
            return result
        except Exception:
            if attempt==2:raise
            time.sleep(2)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(check,manifest['files']))
report={'repository':'qaz741612/sky-isles','mediaCommit':commit,'manifestSha256':hashlib.sha256(remote_manifest).hexdigest(),'checkedFrom':'raw.githubusercontent.com, downloaded bytes (not HTTP status alone)','verifiedCount':len(results),'allMatch':all(r['matches'] for r in results),'files':results}
(root/'github-media-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='files'}))
