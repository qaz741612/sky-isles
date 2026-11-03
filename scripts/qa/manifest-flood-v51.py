"""Bounded delivery index with decoded image sizes and streaming-compatible hashes."""
from pathlib import Path
import json,hashlib,subprocess
from PIL import Image
R=Path(__file__).resolve().parents[2];O=R/'docs/previews/flood-control-island-g-v5-1';D=R/'docs/design/flood-control-island-g-v5-1';paths=set()
for root in [O,D]:
 for p in root.rglob('*'):
  if p.is_file()and p.name not in ['MANIFEST.json','GITHUB-VERIFIED.json','FILE-LIST.md']and p.suffix not in ['.blend1','.pyc','.stdout']and '__pycache__'not in p.parts:paths.add(p)
for name in subprocess.check_output(['git','diff','--name-only','8849b89e99163c179973a31571498115c6c80e7c','--','src','scripts','test','public/models/flood-control-g'],cwd=R,text=True).splitlines():
 p=R/name
 if p.is_file():paths.add(p)
for folder,pattern in [('scripts/flood','*v51.py'),('scripts/qa','*flood-v51*'),('scripts/blender','*flood_v51.py')]:paths.update(p for p in(R/folder).glob(pattern)if p.is_file())
# Immutable rebuild inputs belong to the index as dependencies, not claimed new changes.
deps=['scripts/flood/prepare_v5.py','scripts/flood/audit_final_v5.py','scripts/qa/check-flood-v5.mjs','scripts/blender/flood_export.py','src/data/flood-control-plan.json','src/data/yuan-plan.json','src/data/yuan-layout.json','src/data/yuan-surface.json','docs/design/flood-control-island-g-v5/flood-control-g-v5.blend','docs/design/flood-control-island-g-v5/source-package/build.py']
for name in deps:
 p=R/name
 if p.is_file():paths.add(p)
names=sorted(str(p.relative_to(R))for p in paths)
lines=['# G V5.1 修改與交付清單','','基準8849b89；沿用PR18歷史，只有G美術、對應碰撞及G局部避障。213份既有檔案逐位元相同，G模組載入／建造前綴亦相同。沒有修改苑字地形、22道路、F/A/C或共用玩家／UI。','','正式成果為根目錄的game/、blender/與模型；before/及iteration-*明確是比較或失敗自查，不能混稱最終驗收。work、node_modules、.blend1、__pycache__未提交。','','## 程式、測試及原樣依賴','']+['- `'+s+'`'+('（原樣依賴）'if s in deps else'')for s in names if not s.startswith(('docs/','public/models/'))]+['','## 資產、圖片與報告','']+['- `'+s+'`'+('（原樣依賴）'if s in deps else'')for s in names if s.startswith(('docs/','public/models/'))]
filelist=O/'FILE-LIST.md';filelist.write_text('\n'.join(lines)+'\n');paths.add(filelist);rows=[]
for p in sorted(paths):
 row={'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 if p.suffix.lower()in ['.png','.jpg','.jpeg']:
  with Image.open(p)as im:row['image']={'width':im.width,'height':im.height,'format':im.format};im.verify()
 rows.append(row)
(O/'MANIFEST.json').write_text(json.dumps({'baseCommit':'8849b89e99163c179973a31571498115c6c80e7c','scope':'G V5.1 final assets, actual renders/game captures, unchanged baseline dependencies and separately identified review history; not hardware or human art acceptance','excludes':['manifest self hash verified separately','GITHUB-VERIFIED receipt','work','node_modules','.blend1','__pycache__'],'files':rows},ensure_ascii=False,indent=2)+'\n')
print('V5.1 manifest:',len(rows),'files,',sum(x['bytes']for x in rows),'bytes; every image decoded')
