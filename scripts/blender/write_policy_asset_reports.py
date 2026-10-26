"""Generate engineering/art-review notes from actual saved asset reports. MIT."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/design/seven-policy-islands-blender-v1';site=json.loads((OUT/'site-planning-summary.json').read_text());names={r['id']:r['policyName']for r in site['results']};ids=list(names);models={k:json.loads((OUT/k/'model-report.json').read_text())for k in ids};loads={k:json.loads((OUT/k/'three-loading-report.json').read_text())for k in ids}
lines=['# 實際尺寸與既有苑字路網：只作建議','', '先依主效果圖建立建築與完整景觀，從真實 evaluated mesh 量測，最後才生成美術展台。沒有把模型壓進半徑 9，也沒有縮放人物或已定稿世界。','', '圓展台以建築（含屋簷）、低景觀及設施實際最大徑向尺寸加 1m，再向上取到 0.2；樹冠可自然外挑。展示橋臂在這次計算之外。完整包圍盒仍包含橋臂，不能直接把完整寬度的一半當成島半徑。','', '| 島 | 實測內容最大半徑 | 圓展台半徑 | 超過12 | 橢圓替代 X/Y 半軸 | 局部拓展面積 |','| --- | ---: | ---: | --- | --- | ---: |']
for r in site['results']:
 m=models[r['id']];a=r['proposals']['ellipse'];lines.append(f"| {r['policyName']} | {m['recommendedPlatform']['derivedFromActualContentRadius']:.3f} | {r['assetReviewPlatformRadius']:.1f} | {'**是**'if r['circleRadiusOver12']else'否'} | {a['radiusX']:.1f} / {a['radiusY']:.1f} | {r['proposals']['localExtension']['area']:.1f} |")
lines+=['','## 超過半徑12的理由','','- **交通 12.6**：主站、列車與後方長雨棚保持正常比例，後方屋簷／軌道角點實測約 11.56，另留 1m 外側餘裕。','- **產業青年 12.8**：完整溫室、抬高苗床、後方展示棚與小型產業展示占據較深角點，不壓縮建築及工作庭院。','- **治水防災 12.4**：需容納上游渠道、閘門、下游真實凹池、觀察平台與管理中心，保留各區間可理解的岸線及停留空間。','','沒有因此縮小建築；具體物件尺寸／三角面見各島 model-report.json。','','## 鄰島距離','','八島中心位置完全沿用現有 B 方案；安心生養仍採其已核准 10.2，其他七島僅使用本輪建議值作**離線假設**。',f"若全部先以建議圓形估算，28 組島對沒有圓形本體重疊，最小島邊距 **{site['minimumCircleEdgeGap']:.3f}**。這不能證明路口與其他筆畫都相容。",'', '## 交通島是需要特別處理的案例','','12.6 圓台會進入 **J1、J2** 交會平台周圍，並包入非直接連往交通島的 **S05、S08** 既有筆畫部分。這不是新增路線的許可，也不能把本輪展台直接當成新的正式島面。','']
traffic=next(r for r in site['results']if r['id']=='transport')
lines+=['| 路口 | 全圓展台重疊面積 | 局部拓展提案重疊面積 |','| --- | ---: | ---: |']
for j in traffic['nearbyJunctionOverlaps']:lines.append(f"| {j['node']} | {j['circleOverlapArea']:.3f} | {j['localExtensionOverlapArea']:.3f} |")
lines+=['','**後續交通整合優先審查局部拓展**：保留現有前庭圓區，朝實際站體／後站月台包絡增加土地；`site-planning.json` 附可重現局部輪廓。橢圓方案也有資料，但仍須重新聯集、護欄與政策標籤檢查。不能藉由移動島中心或重畫 Bezier 來掩蓋問題。','','## 真正橋口與展台橋臂','','美術模型的四個 4.8 寬橋臂沿參考展台方向，標記為 reviewOnly。真實 B 路網每島接入數目與方位不盡相同；各島 site-planning.json 列出既有中心線在建議圓周的實際交點、世界座標、本地 Blender 座標及方向差。整合時只能處理橋口／島面介面，不改中央路線。','','部分既有島內直線接近帶會穿過本輪已封閉的館舍，已逐項列出 inIslandApproachConflicts。這是未來**島內**入口繞行設計及碰撞工作，不宣稱本輪已可在遊戲四入口實走。','','## 三種資料的用途','','1. 圓形：目前 BLEND/GLB 的美術檢視展台與尺寸上界。','2. 橢圓：從實際內容包絡＋1m 尋找較小面積半軸，附輪廓。','3. 局部拓展：現有島面圓形與實際內容凸包＋1m 聯集；可降低不必要的前庭／側向擴大。','','所有選項、28 組距離、路口及非相鄰筆畫交會見 [完整 JSON](site-planning-summary.json)。未執行任何正式世界生成、半徑更新或路線控制點改寫。']
(OUT/'SITE-PLANNING.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
validation='''# 驗證、實際差異與待人工項目

## 已完成的資產檢查

- 八張參考原圖 SHA256／格式／完整解碼再次通過，七島與對應圖的清單見 REFERENCES.md。
- 七份 `.blend` 保存可編輯構件與 Collections；另外重新開啟最終原檔，重新評估全部幾何，非封閉邊及非正體積問題為 0、外部圖片依賴 0，三角面與匯出報告相符；來源 SHA 檢查前後不變。逐島證據見 `source-audit.json`。
- 七份 GLB 以真正 Three.js GLTFLoader 解析成功；Khronos glTF Validator 全部 **0 errors、0 warnings**；缺失材質 0、非有限法線 0。
- 隔離 Chromium WebGL 真正繪製七份 GLB：瀏覽器實際下載位元組 SHA256 與交付檔完全相同，GL error 0、非空像素成立、缺失材質 0；工程截圖保留在 work，不混入 Blender 美術圖庫。這不是遊戲整合或手機 FPS 測試。
- 所有新模型的三角面、材質數均低於安心生養的 380,999 GLB 三角面／29 材質上限。沒有靠整體縮小模型、減少樓層或貼圖片替代主體。
- 七組 NPC 身體圓 0.35、玩家接近圓 0.33 與模型低位實體包絡沒有重疊；NPC 本體、對話、任務沒有製作。
- 六視圖來源、圖片 SHA、相機及採樣逐張記錄；最終交付核對模型／圖片來源一致、全部完整解碼。相同尺度總覽只排版真實渲染。

## 既有專案健全性與繪圖規模

`npm run check` 成功：既有單元測試 **50/50**、lint、Vite 正式建置通過，見 `existing-game-sanity.json`。這些測試跑的是未修改的原遊戲，不能算成七份新資產的遊戲碰撞驗證。

隔離檢視器每次只載入一島：實際繪圖呼叫約 **84–154**、每幀三角提交約 **352,950–466,218**（透射材質的額外 pass 使提交量高於模型三角面），不是七島合併後的手機負載；未宣稱真機 FPS。可在後續整合審查材質批次、透射 pass 與遠景 LOD，不先改已確認外觀。

## 過程中發現並修正

初輪鋪面在曲線裁切交點曾觸發 Blender 薄片倒角問題；改為工具端受限三角化與 0.00001 格精度，保留真實石板厚度及接縫，最終全構件封閉。主視圖自審後補齊各庭院花帶與木構亭、改善溫室內可見植物／棚燈，公園橋加實體弧形承梁與兩岸基座。這些以同一原模型構件調整，不另造替代網站。

交通列車重新校正輪軌：軌距 1.10、軌頂 Z=0.23，八輪最低點與軌頂最大高度誤差 0.000000015；安全觸感帶移至真正月台後緣（Y=6.64），車窗稍微外移避免門片共面閃爍。

交通與教育鐘面依主圖放回主要立面；車站列車獨立為 GLB TrainRollingStock 組，沒有併進固定軌道，方便後續授權動畫。BLEND 原構件保持獨立；沒有採用或覆寫舊交通模型。

## 人工審查逐島重點

| 島 | 已製作的主要空間 | 人工重點及具體限制 |
| --- | --- | --- |
| 交通 | 曲頂站房、前廊、後方月台雨棚、短鐵道、雙車廂、候車與樹院 | 原圖正面視線下列車仍有部分被站房遮擋，側／背面可看完整；列車為靜態展示，沒有搭乘或行駛控制；12.6 圓台需改以局部拓展審查 |
| 幸福養老 | 生活館、兩側遮簷、茶座、花園步道及交流樹池 | 是社區生活場景，不是完整長照機構；室內只製作透過玻璃可見家具，不含照護設備或操作流程 |
| 產業青年 | 工作館、完整玻璃溫室、苗床作物、展示棚及小型展示車 | 溫室植栽採有限類型，叉車無人且靜態；不新增產業政策或實際生產模擬 |
| 宜居環境 | 開放木亭、寵物草地、低遊具、園路、凹池與木橋 | 沒有動物 NPC 或攀爬玩法；水面與植栽為靜態幾何，接地已建模但未做玩家碰撞整合 |
| 智慧公所 | 服務館與翼廊、資訊亭、數位立牌、等候樹院 | 螢幕與看板用簡潔幾何圖示，沒有另做便民網站、真實申辦內容或新 UI |
| 治水防災 | 管理館、觀察室、三跨閘門、上下游水路、滯留池與觀察台 | 真實凹池／落水幾何，但沒有流體／水文模擬；高架控制室不是已驗證可由遊戲玩家進入的室內 |
| 教育 | 中高學習館、兩翼閱讀／教室、戶外半場、籃架與樹下閱讀 | 不是全套校園；書架與家具按主圖用途簡化，沒有學生 NPC、課程或遊戲任務 |

## 尚未宣稱通過的項目

- 主要輪廓、比例、材質與綠植是否達使用者美術標準，仍待一次整體人工驗收。實際版本的花帶密度低於參考圖，廣場留白較多；玻璃較淡、樹冠較簡化，這些都是本輪需人工比較的具體差異。圖示、花瓣分布與家具數量有一致的三維化簡化，不宣稱逐像素複製 AI 多視角圖。
- 真正遊戲橋口、島面聯集、角色地面／護欄／屋簷碰撞、相機避障、檢查點與政策 UI 相容，留在另行授權的整合階段。
- 新模型在真實桌機／iOS／Android 的 FPS、發熱、材質表現及長時間手感未測試。隔離 WebGL 成功只證明載入與繪圖，不以此宣稱手機效能通過。
- 原設計中遮擋或多視圖次要矛盾，按主效果圖與一致的三維結構處理；背面與側面完整封閉，不補造核定工程、預算或期程。

安心生養原始 BLEND／GLB、原遊戲 src／public／套件、正式苑字配置與必要授權保持不變；未合併 main，未發布正式網站。資產與工具均在獨立開發分支，等待人工驗收後停止。
'''
(OUT/'VALIDATION.md').write_text(validation,encoding='utf-8')
workflow='''# 可重複使用的建模／材質／匯出／渲染流程

## 工具

- Blender / bpy 4.3.0、Python 3.11；Shapely 2.2.0 用於工具端封閉平台與裁切石板，沒有加入遊戲 runtime 依賴。
- Pillow 用於原圖驗證及實際渲染的索引／總覽排版；Noto Sans CJK 用於報告標籤，不匯出字型或圖片貼圖到模型。
- 既有 Three.js 0.179、Khronos glTF Validator（隔離 work 工具安裝）、Chromium 軟體 WebGL。不是硬體 GPU 效能測量。

工具端版本鎖定於同資料夾 `blender-assets-requirements.txt`。GLTF Validator 的既有隔離路徑是 `work/parent-child-blender/gltf-validator/node_modules/gltf-validator`；可用 `npm install --prefix work/parent-child-blender/gltf-validator gltf-validator@2.0.0-dev.3.10` 建立，不改遊戲 package。

## 共用與每島配置

- `scripts/blender/policy_assets/kit.py`：原生實體屋頂、窗框、柱、門廊、植栽、木座椅、石板、局部凹池及展台。
- `recipes.py`：七張主效果圖各自的建築量體、庭院、設施、花帶中心線及 NPC 預留；明確設計位置，沒有空位搜尋或隨機塞物件。
- 材質從已核准安心生養 BLEND **唯讀附加材質**，不附加或修改其建築。使用奶油牆、暖木、灰青屋頂與層次綠植，另補必要草地、水及鋪面。
- `exporter.py`：保持 BLEND 可編輯原構件，GLB 按語意組／材質合批、保留法線；Studio／燈光／相機不匯出。列車保留獨立組。

## 建立與驗證

從專案根目錄，在已安裝上述工具的 Python 環境執行；官方 Blender 4.3 背景 CLI 亦可。程式最後在已寫完檔案後結束，請不要直接在開著其他未儲存工程的 GUI 中執行。

```sh
python scripts/blender/build_policy_assets.py --island transport
python scripts/blender/build_policy_assets.py --island senior
python scripts/blender/build_policy_assets.py --island industry
python scripts/blender/build_policy_assets.py --island environment
python scripts/blender/build_policy_assets.py --island digital
python scripts/blender/build_policy_assets.py --island water
python scripts/blender/build_policy_assets.py --island education
python scripts/blender/audit_policy_asset_sources.py
node scripts/blender/validate_policy_assets.mjs
node scripts/blender/policy_asset_footprints.mjs
python scripts/blender/audit_policy_asset_sites.py
```

Blender CLI 範例：`blender --background --threads 2 --python scripts/blender/build_policy_assets.py -- --island transport`。GLB／BLEND 都寫入各島子目錄；不寫任何遊戲檔案。

## 六視圖與最終報告

```sh
python scripts/blender/render_policy_assets.py --island transport --resume
```

對七個 ID 各執行一次。`--resume` 只有在現有圖的來源 BLEND SHA 與圖片 SHA 同時相符時才跳過。主視圖 1280×960／64 samples；四向 1100×825／40 samples；俯視 1200×900／48 samples；Cycles CPU＋OpenImageDenoise。七島主視圖相機與尺度固定相同。

全部六視圖完成後：

```sh
node scripts/blender/check_policy_asset_cameras.mjs
python scripts/blender/write_policy_asset_reports.py
python scripts/blender/finalize_policy_assets.py
```

finalize 會強制核對七份模型、42 張原圖的 SHA 與同一來源、七張主圖相機／正交尺度相同，再製作六視角索引及總覽、更新 bytes／尺寸／SHA256 manifest。

## 隔離 WebGL 相容檢查

```sh
npx vite --host 127.0.0.1 --port 4191 --strictPort
node scripts/blender/check_policy_assets_webgl.mjs
```

工具頁在 `scripts/blender/policy_assets/viewer.html`，僅載入單一 GLB 做真實繪圖；不執行現有政策島遊戲，不是另做一套世界。工程截圖存在 work；圖庫只展示 Blender 渲染。

所有 Git 階段提交均使用 `[CF-Pages-Skip]`，避免既有 Cloudflare 整合為純資產／文件重複建站；不修改 Cloudflare 或 Production。
'''
(OUT/'WORKFLOW.md').write_text(workflow,encoding='utf-8')
print('Wrote site options, per-island scope and reproducible workflow')
