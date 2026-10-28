"""Final source-preservation, paths and SHA manifest for PR14 open platform. MIT."""
import json,hashlib,subprocess,shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/design/transport-elevated-station-v9-prototype';BASE='81f7408468bcce2f7452b13e0a9d7ea1d4be62a1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();git=lambda *args:subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
protected=['src','public','package.json','package-lock.json','LICENSE','docs/design/parent-child-blender-refinement-v2','docs/design/seven-policy-islands-blender-v1'];changed=git('diff',BASE,'--name-only','--',*protected);assert not changed,changed
# Current game and approved family source are independently hash-locked, not copied/recreated.
protectedFiles=[]
for p in ['src/data/yuan-plan.json','docs/design/parent-child-blender-refinement-v2/parent-child-centre.blend','docs/design/parent-child-blender-refinement-v2/parent-child-centre.glb']:
 old=subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT);h=sha(ROOT/p);assert hashlib.sha256(old).hexdigest()==h;protectedFiles.append({'path':p,'sha256':h,'unchanged':True})
previews=[]
for p in (ROOT/'work/preserved-before-station-integration').glob('*.png'):
 q=ROOT/'docs/previews/yuan-panorama'/p.name
 if q.exists():assert sha(p)==sha(q);previews.append({'path':str(q.relative_to(ROOT)),'sha256':sha(q),'unchangedFromPreExistingBackup':True})
assert len(previews)==5
(OUT/'source-preservation.json').write_text(json.dumps({'comparisonBaselineCommit':BASE,'comparisonBaselineRole':'previous submitted PR14 head, not the current PR base','PRBaseBranch':'codex/seven-policy-islands-blender-assets-v1','PRBaseSHA':'19a568279424278dad5b7ce45dba11fca53c0145','headBranch':'codex/transport-elevated-station-v9-blender-prototype','protectedPathsUnchanged':protected,'protectedFiles':protectedFiles,'preExistingUserPreviewEditsPreservedAndExcludedFromCommits':previews,'productionConfigChanged':False,'gameIntegrationPerformed':False,'PRBaseRetargetPerformed':False,'forcePushPerformed':False,'transportOnlyApprovedBaseProposal':'BRANCH-ISOLATION.md','recoveryCodeCommit':'0b02820658e5c9ccf4821c58dfe2c2547e93d756','recoveryModelsCommitShort':'ca94f48'},ensure_ascii=False,indent=2)+'\n')
# Exact transport-only restore allowlist for the later approved-base cleanup.
scripts=[]
for p in (ROOT/'scripts/blender').rglob('*'):
 if not p.is_file()or p.suffix not in ['.py','.mjs','.html']:continue
 if'elevated_station_v9'in str(p)or'open_platform'in p.name:scripts.append(str(p.relative_to(ROOT)))
scripts=sorted(set(scripts));paths=['docs/design/transport-elevated-station-v9-prototype',*scripts];(OUT/'transport-only-paths.txt').write_text('\n'.join(paths)+'\n')
# Explain modifications relative to the old PR14, without touching prior user previews.
changes=git('diff',BASE,'--name-only','--','docs/design/transport-elevated-station-v9-prototype','scripts/blender').splitlines();untracked=git('ls-files','--others','--exclude-standard','--','docs/design/transport-elevated-station-v9-prototype','scripts/blender').splitlines();changes=sorted(set(changes+untracked))
(OUT/'MODIFIED-FILES.md').write_text('''# 修改檔案

本輪僅交通原型、離線工具、同源渲染與報告；沒有改遊戲runtime或其他島。恢復程式提交0b02820先上傳供備援。最終檔案以此資料夾manifest／GitHub diff核對。

- `open_platform_elevated_station_v9.py`：直接開啟舊原檔，移除上層棚、保留站房／橋拱、剛性迴轉列車，補月台／小亭，修正花圃座椅。
- `elevated_station_v9/exporter.py`：同島靜態材質合批，列車分組保留，不改法線／UV。
- `audit_open_platform_v9.py`：新增上層通道、實際結構三角投影、車頭／入口鏡頭及視線檢查。
- `audit_elevated_station_v9.py`：支援已核准模型基底與現有PR14的嚴格比對；只接受相同22條中心線和八島中心，鄰島以10.2檢查。
- `render_open_platform_before.py`：舊原檔與新原檔同機位對照，保留嚴格手機預設參數。
- `report_open_platform_v9.py`／`finalize_open_platform_delivery.py`：驗證所有來源hash及真正測試紀錄，產生圖表與manifest。
- `.blend`／兩GLB、11視角與4組前後比較、各項檢查／效能／基底方案：見本目錄。

不把前輪的5張使用者未提交預覽圖納入本輪。

'''+ '\n'.join('- `'+p+'`'for p in changes)+'\n')
# Raw diagnostics preserve the actual completed recovery build and previous test log.
diag=OUT/'recovery-diagnostics';diag.mkdir(exist_ok=True)
(diag/'environment-interruption.txt').write_text('''診斷來源：上一輪工具與本輪恢復結果，非硬體故障推定。
上一輪 exec-server transport disconnected; failed to resume exec-server session: recovery timed out after 25s。
後續工具回報 No usable execution environment is available。
2026-10-28恢復後最後重建log確認OPEN_PLATFORM_SAVED成功，source SHA9070e0...；環境中斷原因未得到OOM／GPU故障等證據，不臆測。
候選、幾何與全部最終渲染已在恢復後重新驗證；WIP7250a4c和已推送0b02820只作恢復點，不是最終驗收。
''')
for name in ['open-platform-build.log','open-platform-final-gltf.log','open-platform-source.log','open-platform-before-render.log']:
 p=ROOT/'work'/name
 if p.exists():shutil.copy2(p,diag/name)
# Snapshot current source script hashes without rewriting the frozen BLEND.
m=json.loads((OUT/'model-report.json').read_text());m['currentReproductionScriptsSHA256']={p:sha(ROOT/p)for p in scripts};(OUT/'model-report.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
files=[]
for p in sorted(OUT.rglob('*')):
 if not p.is_file()or p.name in ['media-manifest.json','SHA256SUMS','github-verification.json','DELIVERY.md']:continue
 r={'path':str(p.relative_to(OUT)),'repoPath':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}
 if p.suffix=='.png':
  with Image.open(p)as im:im.verify()
  with Image.open(p)as im:r.update(width=im.width,height=im.height)
  r['role']='provided reference (not our model render)'if'/inputs/'in str(p)else'final actual same-source Cycles render'if'/renders/'in str(p)else'previous PR14 actual render, camera-verified'if'/before/'in str(p)else'isolated Three.js WebGL engineering screenshot'if'/qa/'in str(p)else'comparison/contact sheet/engineering diagram/texture; see labels'
 files.append(r)
for p in scripts:
 f=ROOT/p;files.append({'path':'repo:'+p,'repoPath':p,'bytes':f.stat().st_size,'sha256':sha(f),'role':'transport-only reproduction tool'})
(OUT/'media-manifest.json').write_text(json.dumps({'sourceBlendSHA256':m['blendSHA256'],'allFinalModelRendersSameSource':True,'finalRenders':11,'sameCameraBeforeAfterPairs':4,'manifestExcludesSelfAndDownloadReceipts':True,'files':files},ensure_ascii=False,indent=2)+'\n');(OUT/'SHA256SUMS').write_text(''.join(r['sha256']+'  '+r['repoPath']+'\n'for r in files));print(json.dumps({'manifestFiles':len(files),'totalBytes':sum(r['bytes']for r in files),'protectedRuntimeAndFamilyUnchanged':True,'preexistingUserPreviewsPreserved':5},ensure_ascii=False))
