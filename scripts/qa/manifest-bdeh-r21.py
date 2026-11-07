"""Manifest complete R21 deliverables, source provenance, images and changes."""
from pathlib import Path
import json,hashlib,subprocess
from PIL import Image
R=Path(__file__).resolve().parents[2];O=R/'docs/previews/bdeh-r21';D=R/'docs/design/bdeh-r21';base='2b4404927f33096ab28539a01f5e6236d670c038';paths=set()
for root in [O,D,R/'public/models/bdeh-r21',R/'scripts/bdeh']:
 for p in root.rglob('*'):
  if p.is_file()and p.name not in ['MANIFEST.json','GITHUB-VERIFIED.json','FILE-LIST.md']and p.suffix not in ['.blend1','.pyc','.stdout']and'__pycache__'not in p.parts:paths.add(p)
for name in subprocess.check_output(['git','diff','--name-only',base,'--','src','scripts','test'],cwd=R,text=True).splitlines():
 p=R/name
 if p.is_file():paths.add(p)
for pattern in ['*bdeh-r21*']:
 paths.update(p for p in(R/'scripts/qa').glob(pattern)if p.is_file())
paths.update((R/'scripts/blender').glob('*bdeh_r21.py'))
deps=['scripts/blender/flood_export.py','src/world/station-model.js','src/sim/player.js','src/data/yuan-plan.json','src/data/yuan-layout.json','src/data/yuan-surface.json','src/data/bridge-landscape.json','test/helpers/software-qa.js','package.json','package-lock.json','LICENSE']
deps+= [r['path'] for r in json.loads((D/'PROTECTED-BASELINE.json').read_text())['files']]
paths.update(R/n for n in deps if(R/n).is_file())
names=sorted(str(p.relative_to(R))for p in paths)
lines=['# B／D／E／H R21 修改與交付清單','','基準PR18 `'+base+'`；四島新增資產、R21候選路網與語義碰撞；保護33份F/A/C/G及共用檔案。','','`iteration-*`和before是歷史證據；根目錄blender/game才是最終成果。work、node_modules、.blend1、pycache未提交。','','## 程式、測試及相依','']+['- `'+n+'`'+('（原樣依賴）'if n in deps else'')for n in names if not n.startswith(('docs/','public/'))]+['','## 資產、圖片及報告','']+['- `'+n+'`'for n in names if n.startswith(('docs/','public/'))]
filelist=O/'FILE-LIST.md';filelist.write_text('\n'.join(lines)+'\n');paths.add(filelist);rows=[]
for p in sorted(paths):
 row={'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 if p.suffix.lower()in['.png','.jpg','.jpeg']:
  with Image.open(p)as im:row['image']={'width':im.width,'height':im.height,'format':im.format};im.verify()
 rows.append(row)
(O/'MANIFEST.json').write_text(json.dumps({'baseCommit':base,'scope':'R21 final assets, source files, Blender/game evidence, test reports and clearly separate historical review evidence; not hardware or human approval','excludes':['manifest self and GitHub receipt','work','node_modules','.blend1','pycache'],'files':rows},ensure_ascii=False,indent=2)+'\n')
print('R21 manifest:',len(rows),'files,',sum(r['bytes']for r in rows),'bytes; all images decoded')
