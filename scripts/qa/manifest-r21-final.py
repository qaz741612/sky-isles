"""Scoped final-polish manifest; previous R21 delivery stays pinned historical."""
from pathlib import Path
import json,hashlib,subprocess
from PIL import Image
R=Path(__file__).resolve().parents[2];O=R/'docs/previews/bdeh-r21/final-qa';base='39f41940fd3af0f432b477ebd36ad5b677a71db1';paths=set()
for root in[O,R/'docs/design/bdeh-r21/final-qa-baseline']:
 paths.update(p for p in root.rglob('*')if p.is_file()and p.name not in['MANIFEST.json','GITHUB-VERIFIED.json','FILE-LIST.md']and p.suffix not in['.blend1','.pyc']and'__pycache__'not in p.parts)
for code in'BDEH':
 paths.update([R/f'docs/design/bdeh-r21/{code}/{code}-r21.blend',R/f'docs/design/bdeh-r21/{code}/model-report.json',R/f'public/models/bdeh-r21/{code}.glb'])
for name in subprocess.check_output(['git','diff','--name-only',base,'--','src','scripts','test','docs/previews/bdeh-r21'],cwd=R,text=True).splitlines():
 p=R/name
 if p.is_file()and p.suffix not in['.blend1','.pyc']and p.name not in['MANIFEST.json','GITHUB-VERIFIED.json']:paths.add(p)
for name in['scripts/qa/check-r21-manual.mjs','scripts/qa/debug-r21-continuity.mjs','scripts/blender/export_bdeh_camera_canopies.py','test/helpers/r21-arrival-audit.js','scripts/qa/manifest-r21-final.py','scripts/qa/verify-r21-final.py','scripts/qa/boards-r21-final.py','scripts/qa/replay-r21-final.mjs','scripts/qa/capture-r21-final.mjs','scripts/qa/measure-r21-final.mjs','scripts/qa/report-r21-final.py','scripts/qa/merge-r21-browser-evidence.py','scripts/qa/audit-r21-final-evidence.py','scripts/qa/audit-r21-camera-domain.py','scripts/qa/audit-r21-glb.py','scripts/blender/render_bdeh_final_details.py','scripts/blender/polish_bdeh_final.py','scripts/blender/audit_bdeh_final.py','scripts/blender/render_bdeh_r21.py','scripts/blender/flood_export.py','scripts/bdeh/final_collision.py','test/r21-final-qa.e2e.js','test/helpers/software-qa.js','src/world/station-model.js','src/sim/player.js','package.json','package-lock.json','LICENSE']:
 paths.add(R/name)
locks=json.loads((R/'docs/design/bdeh-r21/final-qa-baseline/LOCKS.json').read_text())
locked=locks['files']if isinstance(locks,dict)and'files'in locks else locks
if isinstance(locked,list):paths.update(R/v['path']for v in locked)
else:paths.update(R/n for n in locked)
names=sorted(str(p.relative_to(R))for p in paths)
(O/'FILE-LIST.md').write_text('# 最終精修交付檔案\n\n基準 `'+base+'`。work、node_modules、pycache、blend1 排除；iteration-*與game-before僅歷史證據，game-after及四島blender才是本輪最終畫面。\n\n'+'\n'.join('- `'+n+'`'for n in names)+'\n')
paths.add(O/'FILE-LIST.md');rows=[]
for p in sorted(paths):
 row={'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 if p.suffix.lower()in['.png','.jpg','.jpeg']:
  with Image.open(p)as im:row['image']={'width':im.width,'height':im.height,'format':im.format};im.verify()
 if p.suffix=='.mp4':
  data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=width,height,r_frame_rate,duration','-of','json',str(p)]));row['video']=data['streams'][0]
 rows.append(row)
(O/'MANIFEST.json').write_text(json.dumps({'baseCommit':base,'scope':'PR19 final polish: current four models, delta source, baseline snapshots, final evidence, explicit historical iterations and protected dependencies; no real-device/human art approval','files':rows},ensure_ascii=False,indent=2)+'\n')
print('Final manifest:',len(rows),'files;',sum(v['bytes']for v in rows),'bytes; images decoded')
