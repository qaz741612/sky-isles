"""Bounded-output final/historical G delivery index; never include scratch/binary dumps."""
from pathlib import Path
import json,hashlib,subprocess
from PIL import Image
R=Path(__file__).resolve().parents[2];O=R/'docs/previews/flood-control-island-g-v5';D=R/'docs/design/flood-control-island-g-v5';exclude={'MANIFEST.json','GITHUB-VERIFIED.json','FILE-LIST.md'};paths=set()
for root in [O,D]:
 for p in root.rglob('*'):
  if p.is_file()and p.name not in exclude and p.suffix not in ['.blend1','.pyc','.stdout']and '__pycache__'not in p.parts:paths.add(p)
for f in subprocess.check_output(['git','diff','--name-only','cd4bacba72b6a1f7bf607c687566dc14f12c4896','--','src','scripts','test','public/models/flood-control-g'],cwd=R,text=True).splitlines():
 p=R/f
 if p.is_file():paths.add(p)
for folder,pattern in [('scripts/flood','*.py'),('scripts/qa','*flood*v5*'),('scripts/blender','*flood*v5.py')]:
 for p in(R/folder).glob(pattern):
  if p.is_file():paths.add(p)
# Correct glob for underscore Blender entrypoints, explicit scripts retained.
for f in ['scripts/blender/build_flood_v5.py','scripts/blender/render_saved_flood_v5.py','scripts/qa/manifest-flood-v5.py','scripts/qa/verify-flood-v5.py']:paths.add(R/f)
paths={p for p in paths if p.exists()};changed=[str(p.relative_to(R))for p in sorted(paths)if not str(p.relative_to(R)).startswith(('docs/','public/models/'))]
text=['# G V5 修改及交付檔案','', '基底PR17 cd4bacb。最終、設計參考及歷史失敗證據均列入；iteration-*不是最終驗收通過資料。work/node_modules/.blend1/__pycache__未提交。','', '主要原始配置為flood-control-plan；yuan-plan只改G footprint及保留燈錨點清單，生成資料按流程更新；F/A/C資產、模組與人物物理未改。','', '## 程式及測試','']+['- `'+f+'`'for f in changed]+['','## 模型、圖像及報告','']+['- `'+str(p.relative_to(R))+'`'for p in sorted(paths)if str(p.relative_to(R)).startswith(('docs/','public/models/'))];filelist=O/'FILE-LIST.md';filelist.write_text('\n'.join(text)+'\n');paths.add(filelist);rows=[]
for p in sorted(paths):
 row={'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 if p.suffix.lower()in['.png','.jpg','.jpeg']:
  with Image.open(p)as im:row['image']={'width':im.width,'height':im.height,'format':im.format};im.verify()
 rows.append(row)
(O/'MANIFEST.json').write_text(json.dumps({'baseCommit':'cd4bacba72b6a1f7bf607c687566dc14f12c4896','scope':'G V5 only; final same-source Blender/game evidence, reference package, all unsuccessful historical iterations and changed source; not a blanket art/hardware acceptance','excludes':['MANIFEST self hash verified separately','GITHUB-VERIFIED receipt','work','node_modules','.blend1','__pycache__','empty blocked-child stdout'],'files':rows},ensure_ascii=False,indent=2)+'\n');print('G V5 indexed',len(rows),'files;',sum(x['bytes']for x in rows),'bytes; all image files decoded')
