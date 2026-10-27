"""Assemble actual model/render evidence and the explicit reference difference report. MIT."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/design/transport-elevated-station-v9-prototype';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda n:json.loads((OUT/n).read_text());m=load('model-report.json');a=load('source-audit.json');g=load('geometry-space-audit.json');gl=load('gltf-summary.json');web=load('webgl-report.json');rec=load('render-record.json');records={r['view']:r for r in rec['views']};views=['hero','front','back','left','right','top','train-side','player-desktop','player-mobile','player-mobile-zoom28','player-mobile-arrival-overview'];assert sha(OUT/'transport-station-v9.blend')==m['blendSHA256']==a['sourceBlendSHA256']==g['sourceBlendSHA256'];assert len(records)==len(views)
for name in views:
 r=records[name];assert r['sourceBlendSHA256']==m['blendSHA256'];assert sha(OUT/r['file'])==r['imageSHA256'];
 with Image.open(OUT/r['file'])as im:im.verify()
assert gl['allPassed']and web['allPassed']and g['allOfflineChecksPassed'];assert not m['geometryAuditIssues'];fontfile='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';font=ImageFont.truetype(fontfile,25);small=ImageFont.truetype(fontfile,18)
# Comparison is explicitly labelled: user reference at left, real Blender at right.
canvas=Image.new('RGB',(1920,790),'#f0eade');d=ImageDraw.Draw(canvas)
for i,(file,label)in enumerate([('inputs/approved-v9/美術參考_高架車站.png','使用者核准美術參考（非本次模型渲染）'),('renders/hero.png','本次 Blender Cycles｜同一份可編輯原型')]):
 with Image.open(OUT/file)as im:thumb=ImageOps.contain(im.convert('RGB'),(960,720))
 canvas.paste(thumb,(i*960,55));d.text((i*960+18,10),label,font=font,fill='#34575d')
canvas.save(OUT/'reference-comparison.png')
labels={'hero':'45° 主視角','front':'正面','back':'背面','left':'左側','right':'右側','top':'俯視','train-side':'列車側主視角','player-desktop':'桌機預設鏡頭模擬','player-mobile':'手機預設鏡頭模擬（有裁切）','player-mobile-zoom28':'手機既有 zoom28 模擬','player-mobile-arrival-overview':'手機橋口觀察位置（非預設）'}
canvas=Image.new('RGB',(1600,1260),'#f0eade');d=ImageDraw.Draw(canvas)
for i,name in enumerate(views):
 with Image.open(OUT/records[name]['file'])as im:thumb=ImageOps.contain(im.convert('RGB'),(400,380))
 x=i%4*400;y=i//4*420;canvas.paste(thumb,(x+(400-thumb.width)//2,y+35));d.text((x+8,y+7),labels[name],font=small,fill='#34575d')
canvas.save(OUT/'render-index.png')
# Clearly distinct 2D engineering plan; it is never called a Blender render.
canvas=Image.new('RGB',(1100,1100),'#f3eee4');d=ImageDraw.Draw(canvas);scale=40;xy=lambda p:(550+p[0]*scale,520+p[1]*scale)
d.polygon([xy(p)for p in m['sitePolygonXZ']],fill='#c8dbbf',outline='#54796b');d.polygon([xy(p)for p in m['referenceSitePolygonXZ']],fill='#e1d7c7',outline='#8e8f84')
for shell in load('collision-shells.json')['shells']:
 if shell['bottom']<1.5 and shell['top']>.22 and shell['kind']!='guard'and shell['role']!='walkable':d.polygon([xy(p)for p in shell['polygonXZ']],fill='#bda68c')
for q in m['NPCReservedSquaresXZ']:
 d.rectangle([xy((q[0],q[1])),xy((q[2],q[3]))],outline='#b17f29',width=3);d.text(xy((q[0],q[1])), 'NPC 3×3',font=small,fill='#775d22')
for p in g['fourUnchangedBridgePorts']:
 x,y=xy(p['centrelineWorldXZ']);d.ellipse((x-8,y-8,x+8,y+8),fill='#3b788a');d.text((x+9,y-12),p['id']+' / 4.8',font=small,fill='#285867')
d.text((30,20),'幾何配置圖（非渲染）：四橋口、NPC 清空區、側向花園台地提案',font=font,fill='#34575d');d.text((30,1050),'綠：本輪局部台地提案；米灰：V9 原始地界；棕：地面碰撞殼／設施',font=small,fill='#34575d');canvas.save(OUT/'space-plan.png')
show=next(v for v in gl['results']if v['mode']=='showcase');cand=next(v for v in gl['results']if v['mode']=='game-candidate');reduction=(1-cand['triangles']/show['triangles'])*100
rows=[]
for name,b in a['componentBounds'].items():rows.append('| '+name+' | '+' × '.join(f'{n:.3f}'for n in b['sizeWorldXYZ'])+' | '+str([round(n,3)for n in b['minWorldXYZ']])+' → '+str([round(n,3)for n in b['maxWorldXYZ']])+' |')
report=f'''# 交通大升級 V9｜獨立 Blender 精修原型

[可編輯 BLEND](transport-station-v9.blend) · [精修展示 GLB](transport-station-v9-showcase.glb) · [遊戲優化候選 GLB](transport-station-v9-game-candidate.glb) · [尺寸／效能／限制](VALIDATION.md) · [與核准圖逐項比對](ART-REVIEW.md) · [製作流程](WORKFLOW.md)

本輪只製作交通島原型，**沒有整合正式遊戲**。V9 GLB 僅用來量測地界與構件配置；站房、雨棚、橋體、兩節列車、樓梯、玻璃電梯、景觀及材質都是重新建立的原生三維構件，沒有沿用 V9 白模外觀或 `k.hall()`／統一弧形屋頂。

![核准參考與真正 Blender 原型比較](reference-comparison.png)

## 同源實際渲染

![實際 Cycles 主視角](renders/hero.png)

![十一視角索引](render-index.png)

'''
report+=' · '.join(f'[{labels[n]}]({records[n]["file"]})'for n in views)+'\n\n'
report+=f'''十一張均由**同一份最終 BLEND**的幾何輸出。後兩張是另外明確標示的相機模擬，沒有修改模型或原檔。所有來源與圖片 SHA、相機、解析度、採樣見 [render-record.json](render-record.json)。它們是 Blender 渲染，**不是實際 Sky Isles 遊戲截圖**；`qa/` 是另行標示的隔離 Three.js GLB 測試畫面。

## 實測規模

| 檔案 | GLB 實際三角面 | 材質 | 網格批次 | 體積 |
| --- | ---: | ---: | ---: | ---: |
| 精修展示 | {show['triangles']:,} | {show['materials']} | {show['meshPrimitives']} | {show['bytes']/1e6:.2f} MB |
| 遊戲候選 | {cand['triangles']:,} | {cand['materials']} | {cand['meshPrimitives']} | {cand['bytes']/1e6:.2f} MB |

候選減少約 **{reduction:.1f}% 三角面**，保留建築、門窗、軌道及列車位置與主要輪廓，降低倒角細分並略去 {m['candidate']['skippedMicroFoliageObjects']} 個微小植栽構件。沒有縮小整座模型。候選尚未獲遊戲整合或手機效能認證。

## 尺寸、配置與空間

世界座標 X 東／Y 上／Z 北，單位沿用 Sky Isles；玩家身高基準1.5。完整站體包含屋簷，實際尺寸如下。

| 組別 | X寬 × Y高 × Z深 | 世界包圍盒 min → max |
| --- | --- | --- |
'''+ '\n'.join(rows)+f'''

V9 原地界面積 {m['referenceSiteArea']:.3f}；本原型側向花園提案面積 {m['siteArea']:.3f}，增加 **{m['localGardenTerraceProposalAddedArea']:.3f}**。外接框仍約20.33×19.82。這是保留完整兩側花園、四入口及兩塊NPC清空區的局部土地提案，**未寫回正式世界**。四口與其他道路、鄰島分析見 [geometry-space-audit.json](geometry-space-audit.json)。

![四橋口及 NPC 空間圖（工程圖）](space-plan.png)

兩位 NPC 只有預留 Empty／資料，不製作人物或對話。四口 S09/S10/S15/S18 沿用真正 `src/data/yuan-plan.json`，寬4.8，南側雙口共享開放區域；沒有重畫路網。左折返樓梯及其上層連橋、右玻璃電梯與月台連接幾何都存在；實機踏階／電梯操作留待正式整合。

## 原型重要限制

手機預設直式相機會裁到部分高架及列車端部；完整保留了這個結果。另附既有 zoom28，以及玩家步行至橋口 `(0,0.5,7.5)`、yaw0、zoom28 的觀察模擬；補充圖不是預設視角，沒有暗改 FOV。

人工美術驗收、90分整合門檻與真機驗證尚未由工具替使用者宣布通過。逐項差異與自行修正紀錄見 ART-REVIEW。正式遊戲相機避障、膠囊碰撞、上下樓、列車動畫及硬體 FPS 均未整合；本輪無搭乘、NPC、任務或新音樂。

原安心生養 BLEND／GLB、其他七島資產、政策資料、`src/`、`public/`及苑字路網不變。所有原創程式與幾何沿用專案 [MIT](../../../LICENSE)；使用者提供參考與設計包保留原始權利。文字輪廓由 Noto Sans CJK（SIL OFL）產生，沒有複製未提供官方標誌，也沒有外部建築模型。

[檔案大小／SHA256](media-manifest.json) · [GitHub 下載核對](github-verification.json) · [輸入來源](input-audit.json)
'''
(OUT/'README.md').write_text(report,encoding='utf-8')
validation=f'''# 幾何、相機、GLB 與效能檢查

## 實際已執行

- 最終 BLEND 重新開啟檢查：{a['meshObjectsChecked']:,} 個原始網格、{a['evaluatedTriangles']:,} 個 evaluated 三角面，非封閉／非正體積問題0；低位實體與兩處3×3NPC區交疊0。見 source-audit.json。
- 8個車輪最低點與2條軌頂的最大高度差 **{a['wheelRail']['maximumMismatch']:.6f}** 世界單位。
- 全尺寸東西4.8通道與地面殼交疊0，四個橋口／入口／NPC／休息與觀察位置共 **{len(g['groundNavigation']['targets'])}** 個採樣點在同一個保守地面連通元件。使用0.12網格、0.33玩家半徑、四鄰接，避免斜角偷穿；樓梯僅檢查公共接近點，沒有把2D結果冒稱可上樓。所有其他路段及安心生養地界交疊0。
- 精修及候選 GLB：Khronos glTF Validator 都為 **0 errors／0 warnings**；UV、法線、PBR、1張內嵌原創256px木紋完整，沒有外部貼圖依賴。實際glTF編碼會移除少量退化面，因此以gltf-summary的實際檔案三角面為準，與匯出前source計數略有差異。
- Chromium實際GLTFLoader解碼、材質及貼圖載入、WebGL繪圖與下載SHA核對；軟體渲染測量如下。`qa/`畫面是隔離資產檢視器，不是正式遊戲。

## 軟體 WebGL 量測（不是硬體FPS承諾）

| 模式／視口 | 載入至首幀 ms | Draw Calls | 每幀提交面 | 平均幀 ms | 約 FPS |
| --- | ---: | ---: | ---: | ---: | ---: |
'''
for r in web['results']:
 p=r['performance'];validation+=f"| {r['mode']} / {'390×844'if r['mobile']else'1280×800'} | {r['loadToFrameMs']:.1f} | {r['drawCalls']} | {r['submittedTriangles']:,} | {p['meanFrameMs']:.1f} | {p['approxFPS']:.1f} |\n"
validation+='''
環境是受限CPU、Chromium軟體WebGL；每次只載入一個資產，沒有其他七島、角色、物理或遊戲UI。量測在Blender渲染結束後執行，避免兩工作互搶CPU；不外推iOS、Android或桌機GPU真實FPS。透射玻璃會增加額外pass，因此提交面數高於檔案三角面。

候選仍約18MB、90網格批次與多處透射玻璃，不能直接宣稱適合所有手機。後續可在取得外觀驗收後評估meshopt／量化、依距離LOD及玻璃pass；本輪不為降低數字而更改已建立的主輪廓。

## 高度／垂直動線調整

平台步行面維持3.75；前側平台橋底維持3.289，鐵軌處改成真正凹槽斷面，其局部底部約3.02。列車整體向下平移0.38，沒有縮小，車體最高約5.888，與V9約6.208有明確差異；這是修正原代理的輪軌／月台關係。門框高約1.62，車門與內部地板對應；月台至車內仍約0.17–0.23高差，列車為不可搭乘靜態展示。

左側雙跑樓梯每級約0.153、踏深0.273、寬1.0，上層連橋寬1.1，右電梯連橋寬約1.23。幾何相連不能代替原遊戲步階控制：仍需獨立踏階／坡道碰撞及膠囊頭頂驗證。電梯未做升降功能。

## 鏡頭

- 桌機：dist16、pitch0.60、yaw0.16、垂直FOV55、原出生點加1.5目標偏移；完整站房、高架、列車均在畫面內。
- 手機預設：dist22、pitch0.67、yaw0.12、垂直FOV58；有部分棚架、列車及垂直動線被裁切，**不宣稱通過完整車站構圖**。
- 額外zoom28與橋口站位模擬清楚分開標示；不修改正式相機profile。玩家可否在真實手機舒適操作、相機有無遮擋，仍須正式整合後測試。

## 既有遊戲與人工驗收

`npm run check` 成功：50項既有單元測試、lint、Vite build。這只證明未修改的舊遊戲仍可建置，不是新高架站的遊戲碰撞回歸。安心生養來源與苑字JSON以原提交雜湊核對完全一致。

尚待：人工建築／景觀／文化及材質審查、90分且無重大缺陷的整合決策、實機GPU及熱負載、真實八島同載FPS、原人物跳躍／攝影機／風鈴與政策互動回歸。沒有合併、修改Production或執行部署。
'''
(OUT/'VALIDATION.md').write_text(validation,encoding='utf-8')
art='''# 與核准美術圖逐項核對及差異

主效果圖是唯一外觀基準；V9 GLB只提供尺度／位置。下表是製作端自行檢視真實模型後的紀錄，不以測試案例數、GLB面數或自給高分取代人工美術決策。沒有宣稱人工已達90分。

| 項目 | 實作與自審修正 | 仍存在的差異／界線 |
| --- | --- | --- |
| 上下層一體輪廓 | 原生玻璃木質站房、成列橋柱／拱梁、上層凹槽橋面及長雨棚；沒有沿用白模mesh或弧頂小屋 | 原型受固定四口與NPC空間約束，廣場比例比圖中更開闊 |
| 站房入口 | 有厚度屋簷、門廊柱、木窗框、真實玻璃分格、中央天窗、可見服務櫃台／閘機；修正冷灰窗框、暖光與字高 | 完整室內未作可自由探索／互動，家具少於圖中細節；沒有加入官方LOGO |
| 藍灰屋頂 | 立體金屬縫、包邊、框架天窗、木簷底；依首輪圖將木底改斜面以增加可讀層次 | 金屬反射受離線棚燈影響，遊戲shader需另行審查 |
| 高架結構 | 前後拱梁與實體橋柱、柱帽、不同明度立面；重新檢查封邊與法線 | 鐵道處使用凹槽斷面，局部橋底比V9低；不改東西道路與主入口 |
| 雨棚 | 分層金屬面、縱橫骨架、木底斜格柵、真實玻璃帶、柱腳接頭、暖色燈條 | 使用圖中結構語言，非逐像素複製AI圖中不一致的小接頭 |
| 兩節列車 | 原創曲面薄殼車頭、實體前窗開口／玻璃／內部儀表台、獨立門框與窗框、轉向架、8輪與軌頂對位；修正門高與月台關係 | 車頭弧度仍採受控低模；列車向下平移0.38，頂部比V9低；不搭乘、不新增動畫系統 |
| 樓梯／玻璃電梯 | 左雙跑階梯、中間及頂部平台、兩側扶手與上層實體連橋；右透明電梯、上下門與導軌 | 核准圖的電梯位於另一側；依正式規格的「左樓梯／右電梯」保留V9布局，不鏡像假造六視圖；電梯未動作 |
| 前庭花園 | 兩側連續花帶、層次樹冠、前後高低樹、原生立體花朵／葉片、樹池與座椅整合；修正初輪花朵被葉冠遮住 | 兩個NPC 3×3與4.8通道不塞物，中央仍比美術圖留白多；不是把原圖貼到模型上 |
| 島緣與路口 | 採V9不規則輪廓與真正路線生成開口，連續護欄、石材收邊與完整起伏岩體 | 側向增12.568面積只是本原型提案，沒有批准修改正式島面；基本碰撞殼尚未接引擎 |
| 玩家與手機 | 檢查1.5玩家尺度、3×3空間與真正預設相機；保留預設手機裁切並另列觀察點 | 手機預設構圖仍是正式整合前待解決事項，不用特製QA圖冒稱已通過 |

## 自行修正紀錄

首輪未作交付：修正玻璃與暖木層次、文字輪廓封閉、拱梁法線；第二輪修正車頭實際玻璃開口、連續岩體與園藝密度；再校正字高、花朵高度、輪軌接觸、車門比例、凹槽橋面與座椅碰撞殼方向，才凍結同源渲染。

本成果是完整獨立原型與證據，供一次集中檢查；**不能因本報告或工具通過，就宣稱已跨過90分並開始正式整合**。正式整合仍需美術與玩法驗收，尤其手機預設構圖、踏階／電梯與遊戲材質的差異。
'''
(OUT/'ART-REVIEW.md').write_text(art,encoding='utf-8')
workflow='''# 可重現流程

Blender/bpy4.3、Python3.11、Shapely2.2、NumPy、Pillow；Three.js、KhronosValidator與Playwright使用既有專案／work工具環境。不修改runtime依賴。

```sh
node scripts/blender/elevated_station_v9/measure_reference.mjs
python scripts/blender/build_elevated_station_v9.py
python scripts/blender/audit_elevated_station_v9_source.py
python scripts/blender/audit_elevated_station_v9.py
node scripts/blender/validate_elevated_station_v9.mjs
python scripts/blender/render_elevated_station_v9.py
```

GLB量測工具直接讀取專案內 `inputs/approved-v9` 的模型，圖片也保持同一專案來源路徑；work只暫存可重建的量測結果，無需重新上傳原圖。原始建模模組只讀取這些參考及原路線。官方Blender CLI亦可用 `blender --background --python scripts/blender/build_elevated_station_v9.py`。

保存BLEND保留各構件／Collections、可調材質、燈光、相機與另置的隱藏線框碰撞代理。GLB合批包含UV及法線；不包含棚燈／相機／碰撞殼／白模。候選僅在暫存匯出狀態調整倒角與微植栽，絕不回存覆蓋精修BLEND。

預設渲染會核對現有圖片SHA與來源BLEND SHA，只在兩者都一致才續用。十一視圖均為Cycles+OIDN，主視圖1440×1080/64samples，四向1200×900/40samples，其餘48samples；手機720×1280。額外手機相機只在渲染工作記憶體中建立，幾何不變，完整參數記錄於render-record。

```sh
npx vite --host 127.0.0.1 --port 4192 --strictPort
node scripts/blender/check_elevated_station_v9_webgl.mjs
npm run check
python scripts/blender/report_elevated_station_v9.py
```

WebGL只在本機獨立稽核頁執行，不載入政策島遊戲；效能測量避免與Cycles同時運行。最後報告工具強制核對來源、十一張PNG、兩GLB及測試報告，再製作對照圖／索引／manifest。

木紋是原創256px程式紋理，已打包於BLEND與GLB。Noto Sans CJK用於實體文字輪廓及報告標籤，沒有外部建築模型、未授權商標或新音樂。
'''
(OUT/'WORKFLOW.md').write_text(workflow,encoding='utf-8')
# Keep old iteration images out of the final same-source art gallery.
for p in OUT.glob('draft-*.png'):
 dest=ROOT/'work/transport-v9-iterations'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(p),dest)
files=[]
for p in sorted(OUT.rglob('*')):
 if not p.is_file()or p.name in ['media-manifest.json','SHA256SUMS','github-verification.json','DELIVERY.md']:continue
 r={'path':str(p.relative_to(OUT)),'repoPath':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}
 if p.suffix=='.png':
  with Image.open(p)as im:im.verify()
  with Image.open(p)as im:r.update(width=im.width,height=im.height)
  r['role']='source input (not our model render)'if'/inputs/'in str(p)else'actual Cycles same-source render'if'/renders/'in str(p)else'isolated WebGL engineering image'if'/qa/'in str(p)else'comparison/contact-sheet/engineering diagram; see labels'
 files.append(r)
(OUT/'media-manifest.json').write_text(json.dumps({'sourceBlendSHA256':m['blendSHA256'],'allModelRendersSameSource':True,'files':files},ensure_ascii=False,indent=2)+'\n');(OUT/'SHA256SUMS').write_text(''.join(r['sha256']+'  '+r['path']+'\n'for r in files));print(json.dumps({'sameSourceCyclesRenders':len(views),'manifestFiles':len(files),'triangleReductionPercent':reduction},ensure_ascii=False))
