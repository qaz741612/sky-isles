"""Index only V3 deliverables and intentional changed source files; no scratch/backups."""
from pathlib import Path
import json,subprocess,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[2];O=R/'docs/previews/industry-youth-island-c-v3';D=R/'docs/design/industry-youth-island-c-v3'
paths=set()
for root in [O,D]:
 for p in root.rglob('*'):
  if p.is_file()and p.suffix.lower()in ['.png','.jpg','.jpeg','.md','.json','.py','.glb','.blend']and p.name not in ['MANIFEST.json','GITHUB-VERIFIED.json','FILE-LIST.md']:paths.add(p)
changed=subprocess.check_output(['git','diff','--name-only','0c7cab7','--','src','scripts','test','public/models/industry-youth-c'],cwd=R,text=True).splitlines()
for f in changed:
 p=R/f
 if p.is_file():paths.add(p)
for f in ['scripts/qa/manifest-industry-c-v3.py','scripts/qa/verify-industry-c-v3.py','scripts/qa/finalize-industry-c-v3.py','scripts/qa/check-industry-c-v3.mjs','scripts/blender/render_c_v3_baseline.py','scripts/industry/prepare_c_v3_baseline.py']:
 paths.add(R/f)
lines=['# V3 修改與交付檔案','', '完整原始檔、來源包、兩輪模型／渲染、最終遊戲圖、測試及報告如下。舊版工程原檔未覆寫；work、node_modules、.blend1 與 __pycache__ 不在交付內。','', '程式及測試以 PR17 V2.2 `0c7cab7` 比較；保留原 17 檔保護及地形頂點證據。','']
lines += ['- `'+str(p.relative_to(R))+'`'for p in sorted(paths)]
filelist=O/'FILE-LIST.md';filelist.write_text('\n'.join(lines)+'\n');paths.add(filelist)
items=[]
for p in sorted(paths):
 item={'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 if p.suffix.lower()in ['.png','.jpg','.jpeg']:
  with Image.open(p)as im:item['image']={'width':im.width,'height':im.height,'format':im.format};im.verify()
 items.append(item)
(O/'MANIFEST.json').write_text(json.dumps({'baseCommit':'0c7cab7e7e2a75537363a7736206aaa8134787f6','scope':'C V3 final delivery, first iteration archive, user source reference, read-only V2.2 comparisons, changed source and tests','excludes':['MANIFEST.json self hash (verified separately)','GITHUB-VERIFIED.json receipt','work/','node_modules/','.blend1','__pycache__/'],'files':items},ensure_ascii=False,indent=2)+'\n')
print(f'V3 manifest: {len(items)} files, {sum(x["bytes"]for x in items):,} bytes; images decoded')
