"""Create bounded delivery reports/manifests; never prints model/report payloads."""
from pathlib import Path
import json,hashlib,subprocess,re,math,shutil
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image,ImageStat

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/previews/industry-youth-island-c-v1'
def read(p):return json.loads((ROOT/p).read_text())
def save(p,v):(OUT/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cases(report):
    rows=[]
    def visit(s):
        for spec in s.get('specs',[]):
            for t in spec['tests']:
                r=(t.get('results')or[{'status':'not-run','duration':0}])[-1]
                rows.append({'file':spec['file'],'title':spec['title'],'project':t['projectName'],'status':r['status'],'durationMs':r['duration'],'errors':[re.sub(r'\x1b\[[0-9;]*m','',e.get('message',''))[:1400]for e in r.get('errors',[])]})
        for child in s.get('suites',[]):visit(child)
    for suite in report['suites']:visit(suite)
    return rows

broad=read('work/browser-regression.json');latest=read('work/browser-verified.json')
rows=cases(broad);targeted=cases(latest);effective={(r['file'],r['title'],r['project']):r for r in rows}
for r in targeted:effective[(r['file'],r['title'],r['project'])]=r
assert all(r['status']in['passed','skipped']for r in effective.values())
assert latest['stats']['expected']==4 and latest['stats']['unexpected']==0
counts={s:sum(r['status']==s for r in effective.values())for s in ['passed','skipped','failed']}
save('browser-summary.json',{'mode':'SwiftShader engineering mode, native rAF/input/physics; real first and explicit frames; not hardware FPS','broadStats':broad['stats'],'finalTargetedStats':latest['stats'],'effectiveCounts':counts,'initialBroadResults':rows,'finalTargetedResults':targeted,'effectiveResults':list(effective.values()),'resolutions':['C rail probe changed from a radial push that can slide around finite segment ends to a perpendicular push across each sampled segment. Runtime rail geometry was not removed.','Panorama positional assertions use 1e-10 tolerance for observed ~1e-16 ground Float32 settling; orbit and progress equality retained.'],'continuousRenderAttempt':'Initial unbounded continuous SwiftShader run interrupted after timeouts; diagnostic summary below, not counted as passing.'})
diag=OUT/'diagnostics';diag.mkdir(exist_ok=True)
if (OUT/'failure-desktop.json').exists():
    a=json.loads((OUT/'failure-desktop.json').read_text());a['status']='Historical checkpoint-A probe/API failure; resolved, not a current acceptance result';(diag/'checkpoint-a-initial-failure.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n');(OUT/'failure-desktop.json').unlink()
old=ROOT/'work/browser-regression-continuous-interrupted.json'
if old.exists():
    a=json.loads(old.read_text());(diag/'continuous-render-interruption.json').write_text(json.dumps({'status':'interrupted; not a pass','stats':a['stats'],'results':cases(a)},ensure_ascii=False,indent=2)+'\n')

asset=ROOT/'public/models/industry-youth-c/industry-youth-c.glb';blend=ROOT/'docs/design/industry-youth-island-c-v2.2/industry-youth-c.blend'
camera=ROOT/'src/world/industry-youth.js';collision=ROOT/'src/data/industry-youth-collision.json'
game=read('docs/previews/industry-youth-island-c-v1/game/capture-record.json');porch=read('docs/previews/industry-youth-island-c-v1/game/porch-capture-record.json')
for capture in[game,porch]:
    assert capture['assetSHA256']==sha(asset) and capture['cameraSourceSHA256']==sha(camera) and capture['collisionSHA256']==sha(collision)
    assert all(not r['errors']for r in capture['records'])
render=read('docs/previews/industry-youth-island-c-v1/blender/render-record.json');assert render['blendSHA256']==sha(blend)and len(render['views'])==8
for p in (OUT/'game').glob('*.png'):
    im=Image.open(p).convert('RGB');assert min(ImageStat.Stat(im).stddev)>4,'blank capture '+p.name
for device in['desktop','mobile']:
    a=read('docs/previews/industry-youth-island-c-v1/routes-'+device+'.json');assert a['passed']and len(a['routes'])==22
    a=read('docs/previews/industry-youth-island-c-v1/interactions-'+device+'.json');assert a['modelPicking']and a['springVy']>10 and len(a['outerEdges'])>=6
check=(ROOT/'work/final-check.log').read_text();assert 'ℹ fail 0'in check and '✓ built in'in check
source=read('docs/design/industry-youth-island-c-v2.2/model-report.json');audit=read('docs/previews/industry-youth-island-c-v1/geometry-audit.json')
build=(ROOT/'work/build-verified.log').read_text();bundle=next(l.strip()for l in build.splitlines()if re.search(r'assets/.*\.js',l))
perf={'asset':{'sourceCandidateBytes':1266956,'sourceCandidateTriangles':37448,'sourceCandidateBatches':31,'finalBytes':asset.stat().st_size,'triangles':44552,'meshBatches':66,'materials':33,'textures':0,'newRealtimeLights':0},'bundle':bundle,'collisionProxyBytes':collision.stat().st_size,'proxyPrecision':1e-5,'profiles':[],'hardwareFPS':'UNVERIFIED','softwareContinuousFPS':'Not used for hardware claims; original continuous renderer attempt timed out; engineering samples only','network':'Local loopback only, not public mobile network','limits':['Real phone GPU/FPS, thermals, WAN and prolonged input comfort unverified.','Inherited locked station/family assets dominate some full-world views; C alone stays below 100k triangles.']}
for record in game['records']+porch['records']:
    perf['profiles'].append({k:record[k]for k in ['name','kind','size','gpu','render','memory','industry','firstFrameSubmissionMs']})
save('performance.json',perf)

entrances='\n'.join(f"| {v['id']} | {v['newFootprintCrossingsWorldXZ'][0][0]:.3f}, {v['newFootprintCrossingsWorldXZ'][0][1]:.3f} | 4.8 |"for v in audit['entrances'])
radius=max(math.hypot(x,z)for x,z in read('src/data/industry-youth-plan.json')['footprintLocal'])
stamp=datetime.now(ZoneInfo('Asia/Taipei')).isoformat(timespec='seconds')
(OUT/'REPORT.md').write_text(f'''# C 產業青年島 V2.2｜建模與遊戲整合報告

日期：{stamp}。狀態：工程交付，等待人工美術與遊玩驗收；維持 Draft。

## 基底與保護

基於 ae2a63f（PR #16 工程保留、美術待精修），沿用 preflight／8aad08c 恢復紀錄，工作分支 codex/industry-youth-island-c-v1。沒有繼承 PR #13 七島模型。交通、安心生養、治水防災與舊交通備份 GLB 的 SHA256 均與基底一致；正式政策、音效、玩家外觀未修改。所有島中心、22 段 Bezier、4.8 路寬及既有燈錨點保持不變。

## 同源模型與設計對照

使用使用者提供的 RuntimeAssetCandidate，原包 12 個檔案保留在 docs/design/industry-youth-island-c-v2.2/source-package/。DesignReference 的示意橋面／欄杆沒有匯入遊戲。包內文字提及的 revised_design_board.png 不在 ZIP 中，對照使用實際附帶的 00_設計總覽.jpg。

| 核准元素 | 實作與精修 |
| --- | --- |
| 東側三片鋸齒屋頂、太陽能板 | 原輪廓、比例、採光帶與 PV 保留；梁柱接頭與低成本倒角補足 |
| 工坊銅木色與玻璃立面 | 原不透明內部量體改為有厚度的牆、基座、窗間柱；保留機具並補工作桌、門框及把手 |
| 東南弧形溫室 | 原弧形分格、鋼桁架、栽培床保留，調整玻璃透光與材質 |
| 西側開放展廊與廣場 | 木格棚、天窗、展示、環形鋪面及植栽布局保留 |
| 原有蘑菇 | 原座標、力量及遊戲物件保留；GLB 不加第二個蘑菇 |
| 通行餘裕 | 原北側入口小花台向東 0.4；位於 (3.6,-2.65) 的小花台與植栽移至 (7.2,-3.25)，清出 4.8 核心 |

.blend 包含 727 個可編輯構件與隱藏的原始匯入參考；渲染／GLB 僅使用同一套 EXPORT_AND_RENDER 顯示物件。最終 44,552 三角面、66 批次、33 材質、0 貼圖，GLB {asset.stat().st_size:,} bytes。參考候選為 37,448 三角面／31 批次／1,266,956 bytes；精修後的法線、細節及分區批次有成本，未宣稱免費提升品質。

Blender 六視圖及兩張細節均來自同一 .blend SHA，Cycles CPU 48 samples / AgX。環境沒有 OpenImageDenoise，最終沒有使用該功能；前期失敗或過時的圖未混入最終成果。Blender 圖僅顯示資產；遊戲圖另含既有橋梁、聯集護欄與蘑菇。

## 地形、入口與預留

C 中心 (-20.358,0,38.610) 不變。附件不規則地面外框約 29.703 × 25.400，面積 {audit['footprintArea']:.3f}；包覆圓半徑約 {radius:.3f}（超過 12 的原因是完整工坊、溫室、展廊及廣場）。沒有整體縮放建築／人物。yuan-plan 中 C 的 r=9 保留相容用途，實際碰撞與外欄使用原始來源生成的 footprint；不是把半徑 9 當成最終外緣。

| 橋口 | 新島緣中心線交點（世界 X,Z） | 核心寬 |
| --- | --- | --- |
{entrances}

島面與另外七島、19 條非 C 路段核心沒有平面重疊。三盞靠 C 的既有燈沒有搬移；擴地改變肩帶時，生成連通的實體支腳保住原錨點。外欄沿島面與道路共享聯集外緣生成，三個橋口沒有內欄。原始配置來自附件 Python；prepare_c.py 與 generate:yuan 產生衍生資料。

NPC 僅資料／空間預留：本地 (.5,0,8.35)，3×3 X[-1,2]、Z[6.85,9.85]；地面 -.1，未來角色需貼地。面向 π，互動建議 1.6，玩家停留 (.5,0,6.95)，距離 1.4。沒有 NPC 模型或對話。舊 future-island-reservations 的 C 項屬歷史 preflight，本輪有效資料集中在 industry-youth-plan.json。

## 碰撞、鏡頭與玩法

乾地、矮平台／木台、實體上表面、屋頂、牆柱、門與相機障礙分開。模型不是整批當成地面。樓板／屋頂無安全檢查點；乾地可更新檢查點。工坊與溫室維持關閉的展示建築，可走門廊與戶外接近路徑，沒有實作室內開門玩法。

C 專屬避障在屋簷把鏡頭推近人物時，選擇鄰近清楚視線，必要時採低位門廊視線；記住側向偏移，保持 orbit／zoom 狀態。已修正手機門廊近頭遮擋。直式預設探索仍無法一次容納整個園區，需正常旋轉或切全景；不將 QA 拉遠視角稱為預設玩家鏡頭。

一般步行護欄驗證與刻意跳躍／滑翔越界分開。保留跳躍與蘑菇彈跳，玩家刻意越欄仍可能離開安全區，再依檢查點復位；本輪沒有以隱形天花板取消原能力。

## 實際驗證與限制

- npm run check：18 個單元測試檔通過、lint 通過、正式 build 通過。另 C 專項測試驗證真 GLB／材質／數值、八處地面、全部序列化牆欄阻擋、NPC／道路核心及門廊鏡頭。
- 桌機與手機逐段工程實走：22 段各雙向，C 公共路徑與 40 個鏡頭樣本、全景返回、跌落復位通過。逐段測試在各路段起點傳送後使用真正 Player 走完；不是人工操作影片。
- 廣泛 Playwright 首輪：41 通過、3 有意略過、2 初測失敗。修正有限線段護欄測試的徑向推進方式，以及約 1e-16 位移的精確等值斷言（改為 1e-10 容差）；最終建置針對 C／全景的 4 項重測全部通過。合併同一測項的最新結果為 {counts['passed']} 通過、{counts['skipped']} 略過、0 未解決；詳細歷史保留在 browser-summary.json。
- C 專項包含原蘑菇不自動彈起、主動跳躍彈跳、實際島緣推進、點模型開政策與關閉，兩種裝置皆通過。既有回歸涵蓋安心生養、交通四入口、五風鈴邏輯、政策閱讀、鍵盤／單指連續八島、全景與取消觸控。
- SwiftShader 的原始連續渲染嘗試逾時，已保留中斷診斷。SKY_SOFTWARE_QA=1 只提交首幀／明確視覺採樣，保留原生 rAF、輸入、物理、UI、相機；不拿此結果證明連續畫面流暢度。
- 14 張最終遊戲 PNG 含桌機、直式／橫式、三橋口及苑字全景；8 張 Blender PNG 加六視圖拼版、參考對照，共 24 張 PNG。每張遊戲圖有 GLB、碰撞與鏡頭來源 SHA。轉向後曾有一張截圖緩衝清空，已以 QA preserveDrawingBuffer 及轉向穩定等待重拍，最終逐張讀取／非空白檢查通過。這個截圖緩衝設定不屬正式遊戲改動。

## 效能與待人工驗收

最終 JS bundle：{bundle}。碰撞代理採 1e-5 精度，將本輪精修前的約 6.07 MB bundle 降至約 4.62 MB；正式建置仍有大 chunk 警告。沒有新增 runtime 套件、貼圖或即時燈光；按島與構件區域材質合批，保留區域剔除。

各視角的 Draw Calls、三角面、GLB 下載／解碼與首幀提交時間見 performance.json，皆為本機 loopback、DPR1、SwiftShader。不是真實手機 GPU，也不是公網載入。真機 FPS、發熱、記憶體峰值、長時間單手操作與連續相機手感：**未驗證**。

未宣稱人工美術通過。待確認：材質與核准安心生養的協調、幾何化植栽輪廓、玻璃排序／反光、遊戲接地陰影較 Blender 弱、直式探索裁切與需旋轉查看的舒適度、字形因 C 擴地後的主觀辨識度。沒有已知未修復的測試阻擋／墜落失敗，但自動化不涵蓋任意玩家路徑與所有設備。

既有 MIT 及第三方聲明保留。原包為使用者提供設計來源；本輪不新增外部美術素材。沒有合併或修改 Production。若 GitHub 既有整合自動產生公開 Preview，另在 PR 回報狀態；不手動部署。
''')
(OUT/'README.md').write_text('''# C 產業青年島 V2.2｜審查入口

維持 Draft，等待人工美術／遊玩驗收。工程結果與限制見 [REPORT.md](REPORT.md)，不以案例數宣稱美術通過。

## 實際遊戲

![遊戲45度QA主視角](game/c-hero.png)

| 全島 QA | 原生玩家鏡頭（站位以 QA 傳送到達） |
| --- | --- |
| [俯視](game/c-top.png)／[入口QA](game/c-entrance.png) | [桌機廣場](game/desktop-native.png)／[手機廣場](game/mobile-native.png) |
| [S14 玩家鏡頭](game/s14-player.png)／[S15](game/s15-player.png)／[S16](game/s16-player.png) | [手機門廊](game/mobile-porch-native.png)／[手機橫式](game/mobile-porch-landscape.png) |
| [完整苑字](game/yuan-panorama.png) | [手機全景](game/mobile-panorama.png) |

手機門廊圖使用原生鏡頭參數及正式 C 避障，沒有另拉遠相機。廣場直式圖如實保留建築裁切，整個園區請旋轉或使用全景。捕捉紀錄在 game/ 的兩份 JSON；QA framebuffer 設定只供穩定截圖。

## Blender 同源模型

![Blender主視圖](blender/hero.png)

[六視圖拼版](blender/six-views.png)：[正面](blender/front.png)／[背面](blender/back.png)／[左](blender/left.png)／[右](blender/right.png)／[俯視](blender/top.png)／[45度](blender/hero.png)。另有 [工坊細節](blender/workshop-detail.png)、[溫室細節](blender/greenhouse-detail.png) 與 [原設計對照](reference-comparison.png)。全部為同一份最終 Blender 工程的實際渲染。

- [可編輯 .blend](../../design/industry-youth-island-c-v2.2/industry-youth-c.blend)
- [遊戲 GLB](../../../public/models/industry-youth-c/industry-youth-c.glb)
- [模型數據](../../design/industry-youth-island-c-v2.2/model-report.json)
- [幾何／保護檢查](geometry-audit.json)、[瀏覽器結果與初測失敗歷史](browser-summary.json)、[效能](performance.json)
- [檔案清單](FILE-LIST.md)、[SHA256／圖片尺寸](MANIFEST.json)、上傳後的 GITHUB-VERIFIED.json

## 重現與本機預覽

使用含 numpy/trimesh/shapely/Pillow 的 Python 執行 prepare_c.py --refine，再 generate:yuan。Blender 4.3 執行 scripts/blender/build_industry_c.py -- --render 可重建可編輯工程、GLB 與八視圖。原始 V2.2 工程來源完整保留；不需要讀取先前七島模型。

```sh
npm ci
python scripts/industry/prepare_c.py --refine
npm run generate:yuan -- --report-dir docs/previews/industry-youth-island-c-v1
blender -b -t 4 --python scripts/blender/build_industry_c.py -- --render
npm run check
npm run dev -- --port 4224
```

此工作階段另有最終正式建置預覽在 4224 連接埠（工作區環境內，非公開 URL）。可在 Codex 的連接埠／Preview 面板開啟；環境停止後以以上 dev 指令重啟。沒有修改 Cloudflare 設定或 Production。
''')
print('Saved final report, gallery, browser matrix and performance; no unresolved automated failures')
