"""Final report only after test, source, image and geometry proofs exist."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];O=R/'docs/previews/flood-control-island-g-v5-1';D=R/'docs/design/flood-control-island-g-v5-1'
load=lambda p:json.loads(p.read_text());model=load(D/'model-report.json');old=load(D/'baseline/model-report.json');tests=load(O/'test-summary.json');audit=load(O/'spatial-audit-final.json');perf=load(O/'performance-comparison.json');capture=load(O/'game/capture-record.json');renders=load(O/'blender/render-record.json')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert tests['effectiveCounts']['unexpected']==0 and tests['build']['unit']['pass']==76
assert len(capture['records'])==19 and len(renders['records'])==12
assert capture['assetSHA256']==tests['finalAssetSHA256']==sha(R/'public/models/flood-control-g/flood-control-g.glb')
assert capture['runtimeSHA256']==tests['finalGModuleSHA256']==sha(R/'src/world/flood-control.js')
assert renders['sourceBlendSHA256']==sha(D/'flood-control-g-v5-1.blend')
assert all(not row['errors']for row in capture['records'])
assert len(perf['results'])==4
table=['| 版本／視口 | G HTTP下載＋解析 ms | 初始化觀察 ms | 原生 calls／三角面 | 水閘QA calls／三角面 | 全景 calls／三角面 | 原生控制器 CPU ms/tick |','|---|---:|---:|---|---|---|---:|']
for row in perf['results']:
 v=row['views'];table.append('| '+('V5'if row['stage']=='before'else'V5.1')+'／'+('430×932'if row['mobile']else'1200×800')+f" | {row['assetLoad']['totalMilliseconds']:.1f} | {row['navigationReadyAtMs']:.1f} | "+' | '.join(str(q['drawCalls'])+'／'+str(q['triangles'])for q in v)+f" | {v[0]['controllerCPUms']:.3f} |")
report=f'''# G 治水防災 V5.1｜交付與工程驗證

延續 Draft PR18，施工基準 `8849b89e99163c179973a31571498115c6c80e7c`。保持原 V5 歷史、島中心、土地、三閘與指揮中心總體配置。本輪是既有真實 Blender 工程精修及 G 局部視線修正，沒有重建世界、NPC、橋景或其他五島。沒有合併、正式部署或修改 Cloudflare 設定。

[驗收圖庫與原檔入口](README.md)／[自主挑刺與修正](SELF-REVIEW-FINAL.md)／[重建](REBUILD.md)／[逐檔清單](FILE-LIST.md)／[GitHub下載核對](GITHUB-VERIFIED.json)。

## 實際改造

水工：閘板、導軌與門頭提高0.78，門頭與上梁仍有約0.05間隔。上游水位-0.66、下游-1.80，差1.14。新增不透明弧面跌流、分段流線、破碎白沫與消能構件；混凝土內壁隨水流下降。沒有流體模擬、透明粒子、貼圖或新增即時燈。

直接對實際 GLB 三角面量測：指定下游剖面 `Y=-1.72,Z=5.25` 三個閘口淨寬各由約1.30變2.11；這是指定水工剖面，不是聲稱全水系最小寬度或玩家通道寬度。原寬基礎頂面下沉至-1.95，原墩與窄連接柱有0.075搭接、柱與基礎有0.225搭接，並非懸空。16個非公共水下支承三角面從玩家落地面排除，牆柱阻擋仍保留；原公共乾地三角資料逐值相同。[GLB剖面證據](hydraulic-geometry-comparison.json)。

指揮中心：保留量體，完善塔頂、屋簷／封板、四角框架、玻璃橫框、入口木格雨棚、四面遮陽／窗間板、觀測設備和實際支座。保持可用門廊，沒有假樓梯或新增室內玩法。

景觀四區：迎賓區用低位水循環鋪面與兩段成組植栽導引；前庭用連續景觀床界定停留區，保留廣場淨空；觀閘區有接地水位刻度／導覽牌及既有實體護欄；S22凹灣用連續石收邊、減少重複欄柱，保留所有必要橫向安全邊界。原11處樹幹和4張座椅位置保留，補樹冠分枝及8根靠背支柱，不隨機增加盆栽／座椅。

原生手機入口曾有前景屋簷遮住角色下半身；原頭部中心探針未發現。只在G局部避障函式增加六條角色輪廓視線、較細角度候選與穩定偏移保持，原方向連續8幀安全才釋放，避免待機反覆拉回遮擋。原orbit、zoom、FOV及共用玩家相機未變；G外仍走原委派。最終入口畫面重新截取，沒有只挑QA遠鏡頭掩飾。

## 空間與保護

中心仍 `(44.928,0,45.279)`；島台約38.799×34.463，完整模型包圍盒約38.889×16.725×34.553（含底部岩體及塔頂）。尺度1，沒有放大全世界。S21／S22的4.8核心無新實體侵入；S22真正跨水橋、橋底和安全欄保留。

22條Bezier及原路面、土地、燈錨、F/A/C原檔和模組逐位元保護。214項原基準中213檔完全相同，唯一例外是G專用模組末尾避障函式；該模組載入／建造前綴仍與V5原始碼完全相同。沒有偷改原基準雜湊。S20連既有景觀／欄杆裕量對G構件保守投影淨距約2.947。單一張顧礫NPC3×3乾地、接近點及未來導覽視線保留，未新增人物。迎賓植栽距實際S21中心線最小2.820、距NPC預留邊界最小0.447。[空間稽核](spatial-audit-final.json)。

## 模型成本

| 項目 | 原 V5 | V5.1 |
|---|---:|---:|
| 三角面 | 60,211 | {model['triangles']:,} |
| GLB區域／材質批次 | 50 | {model['meshPrimitives']} |
| 材質 | 23 | {model['materials']} |
| G貼圖 | 0 | 0 |
| GLB bytes | 3,665,000 | {model['glbBytes']:,} |
| 新即時燈 | 0 | 0 |

面數增加約23.7%、GLB大小增加約26.2%，不能宣稱零成本。第一輪81,081面已降至74,463（減約8.2%）；使用原有區域與材質合批，不把全世界合成不可剔除巨網格。保留2,073個未改原可編輯物件，另745個更新或新構件；正式GLB仍小於100,000面。[模型資料](../../design/flood-control-island-g-v5-1/model-report.json)。

## 工程結果

- `npm run check`：正式Build、Lint、76個真正啟動的單元案例全部通過；沒有以檔案級子程序假結果代替案例。完整輸出存檔。
- Playwright採增量回歸：原64案例完整執行，再對最終模型及G相機補跑全部10個受影響案例＋2個實際渲染案例；有效66個身份合併結果為62通過、4桌機觸控專用不適用略過、0未解失敗。不是宣稱單次最後66全跑。早期兩個渲染／全景逾時與一次刻意取消的測試驅動保留；最後同身份重新通過，不刪除失敗證據。[逐輪來源](test-summary.json)。
- 桌機／手機尺寸各22段雙向、不跳躍，G公共廣場／門廊／觀景／NPC停留點通過；路段起點使用工程傳送，實際Player60Hz移動，不冒稱人工連續遊覽。
- 桌機／手機各18個水岸實際推撞、有限欄段掃掠、模型點選政策窗、全景返回與強制跌落復位通過；各4個中點無獨立乾地接近條件，沒有列為實際推撞，另有整段單元掃掠。
- 各9個刻意落入閘口水域的實際Player測試回到乾地檢查點，保存解謎進度。水面不當地面；刻意進水不代表開放玩家走入水下。
- 原生桌機／手機入口六視線、相機與orbit全景復原通過；單元另測320個方向／站位／尺寸組合、靜止60ticks穩定與G外委派。嚴格實際遊戲路測另各160個相機方向。
- 最後19張遊戲圖核對HTTP取得GLB與目前資產SHA一致，0頁面錯誤；12張Blender圖來自同一份最後原檔，原檔SHA一致。無舊圖混入最終game/blender目錄。

## 八島同時載入的效能觀察

Chromium／ANGLE SwiftShader、DPR1、共用雲端CPU；原V5在4254，最終V5.1在4265。同視口、站位、固定QA主視及全景；兩者都載入8島。每視角2次暖身＋6次`gl.finish`同步渲染，另5批各100個原生控制器ticks。每次量測另核對實際HTTP模型SHA。這不是硬體FPS，也不是網路冷啟動基準。

{chr(10).join(table)}

完整同步軟體frame樣本及CPU記錄在[效能比較](performance-comparison.json)。初始化讀值含其餘世界載入與測試初始化，不能當G模型單獨下載時間，亦不能當第一次硬體可操作幀。軟體雲端初始化仍可能很慢，**沒有宣稱載入時間或真實手機FPS已通過**。G模型本身仍增加檔案和批次，後續可在人工確認外觀後評估離線壓縮或保守合批；本輪沒有為了達數字破壞建築。

## 畫面與未完成驗收

固定Blender及QA比較逐欄核對相機位置、旋轉／取景、尺寸。原生手機比較是同站位、同orbit／FOV／距離；G避障修正後實際相機位置可不同，另有同模型遮擋前後圖。不用拉遠QA畫面代替玩家鏡頭。

兩輪以上美術自查與後續結構、接地、低位遮擋問題均有圖和修正記錄；主觀美術品質、是否達到使用者C V3以上的門檻、苑字辨識、自由鏡頭全部姿態、真人全周緣步行、真機FPS／發熱、長時間單手舒適度仍待人工驗收。靜態水流不是水文模擬，室內與NPC不在範圍；Cycles64樣本圖有少量顆粒，沒有用後製或AI圖冒充幾何提升。

目前無未解自動化碰撞／路網失敗；上述硬體與人工項目**未驗證**，不是通過。本輪止於G V5.1，不開始橋景、路燈、其他島或正式發布。
'''
(O/'REPORT.md').write_text(report)
print('Final report saved;19 game frames,12 same-source Blender views and current module/asset SHA confirmed')
