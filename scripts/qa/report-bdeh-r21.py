"""Publish a bounded, evidence-linked final report; do not infer art approval."""
from pathlib import Path
import json,hashlib,subprocess,shutil
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];O=R/'docs/previews/bdeh-r21';D=R/'docs/design/bdeh-r21'
read=lambda p:json.loads(p.read_text())
base='2b4404927f33096ab28539a01f5e6236d670c038'
models={c:read(D/c/'model-report.json')for c in'BDEH'};audit=read(O/'geometry-stage-2.json');config=read(R/'src/data/bdeh-plan.json');network=read(O/'network-comparison-r21.json');perf=read(O/'performance.json');capture=read(O/'game/capture-record.json');initial=read(O/'regression-final/full-initial-summary.json');recheck=read(O/'regression-final/playwright-affected-recheck.json')
assert recheck['stats']['expected']==6 and recheck['stats']['unexpected']==0
assert len(capture['records'])==38 and all(not r['errors']for r in capture['records'])
assert len(perf['results'])==4 and all(r['allEightLoaded']==8 and r['webGLError']==0 for r in perf['results'])
for c,m in models.items():assert m['GLBSHA256']==capture['assets'][c]
for r in capture['records']:
 assert abs(r['cameraAspect']-r['size']['width']/r['size']['height'])<.0001
 assert r['canvas']==[r['size']['width'],r['size']['height']]
protected=read(D/'PROTECTED-BASELINE.json')['files']
for item in protected:assert hashlib.sha256((R/item['path']).read_bytes()).hexdigest()==item['sha256']

# Regressions from inherited suites can write into historical report folders.
# Preserve new evidence under this delivery, restore only our generated reports.
for name in ['docs/previews/industry-youth-island-c-v1/interactions-desktop.json','docs/previews/industry-youth-island-c-v1/interactions-mobile.json','docs/previews/yuan-bridges-landscape-v1/zone-check-desktop.json','docs/previews/yuan-bridges-landscape-v1/zone-check-mobile.json']:
 p=R/name
 if subprocess.check_output(['git','diff','--name-only','--',name],cwd=R,text=True).strip():
  shutil.copy2(p,O/'regression-final'/('inherited-'+p.parent.name+'-'+p.name));p.write_bytes(subprocess.check_output(['git','show','HEAD:'+name],cwd=R))

rows=[];npc=[]
for c,m in models.items():
 a=audit[c];lo,hi=a['sceneBounds'];size=[hi[i]-lo[i]for i in range(3)];n=config['islands'][c]['npc'][0]
 rows.append(f"| {c} | {size[0]:.3f}×{size[2]:.3f} | {hi[1]:.3f} / {size[1]:.3f} | {m['triangles']:,} | {m['materials']} | {m['meshPrimitives']} | {m['glbBytes']/1048576:.3f} |")
 npc.append(f"| {c} | ({n['position'][0]}, {n['position'][2]}) | ({n['playerStop'][0]}, {n['playerStop'][2]}) | {n['facing']:.3f} | {a['NPCRoadEdgeClearance']:.3f} |")
perfRows=[]
for r in perf['results']:
 for v in r['views']:
  cpu='—'if v['controllerCPUms']is None else f"{v['controllerCPUms']:.3f}"
  perfRows.append(f"| {r['stage']} | {'觸控直式'if r['mobile']else'桌機'} | {v['name']} | {v['drawCalls']} | {v['triangles']:,} | {v['synchronizedSoftwareFrameMs']['median']:.2f} | {cpu} |")
before,after=network['before'],network['after'];delta=(after['totalCentrelineLength']/before['totalCentrelineLength']-1)*100
unit=(O/'regression-final/check-83.log').read_text();assert 'ℹ tests 83'in unit and'ℹ pass 83'in unit and'ℹ fail 0'in unit
intro='''# B／D／E／H R21 Blender 精修與遊戲整合

四島已在同一個真正Sky Isles世界載入，替換舊臨時造景；可編輯Blender、正式GLB、同源渲染、桌手機遊戲畫面及驗證資料已提交。維持Draft PR19，等待使用者人工美術及真機驗收。沒有合併、正式部署、NPC、室內、橋景或新路燈施工。

基準PR18 G V5.1：`'''+base+'''`。獨立分支：`codex/bdeh-r21-game-integration`。來源ZIP48檔、原manifest47項核對相符；只執行R21建築函式。設計包中的R18/R20檔案是原始碼依賴引擎，與禁止導入的GitHub PR13資產無關，未選用其建築。
'''
report=intro+'''
## 實際完成範圍與藝術審查

- B：雙翼環抱生活院、療癒庭院、交流前廳；補端面、樓層邊緣、木構支承、樹冠及真正的北／東公共接入。
- D：雙服務館與跨通道公共門廊；補屋架承座、角柱、入口雨棚、柱列與真實低門檻。
- E：生態館、連續木構植生脊、開放論壇、雨水花園；補梁肋、承座、連續種植槽、座椅及實體入口踏階。
- H：閱讀／探索雙翼、展頁屋頂、中庭與五階戶外論壇；補高窗、斜撐、實體階梯及玻璃碰撞。

保留研究設計輪廓，沒有發明四棟不同建築，也沒有把研究GLB整座覆蓋正式地形。Blender來源有獨立命名構件，匯出才按島／語義／材質合批，可按區域剔除。沒有新增npm依賴、外部素材、貼圖或即時燈。

第一輪檢視主視與四面、庭院，修正缺端面、屋頂承座、論壇接地與樹冠尺度。第二輪檢視32張同源圖與38張實際遊戲圖，修正H重複階梯黑紋、色彩空間、E入口高差、完整3×3 NPC與植栽衝突、水面／淺盆底與薄高窗碰撞。每島有具體紀錄：[B](B/SELF-REVIEW.md)、[D](D/SELF-REVIEW.md)、[E](E/SELF-REVIEW.md)、[H](H/SELF-REVIEW.md)。

Cycles64 samples的最終八視圖、模型報告與.blend SHA逐一核對。初輪模型／渲染、失敗的顏色與階梯版本、原生截圖驅動問題各自保留，不能混充最終成果。初輪遊戲GLB與初輪Blender工程各有獨立SHA，並非同一份最終模型；前後比較標示「施工初輪→精修」，不是PR18舊版四島美術圖。

## 模型與尺度

| 島 | 實測X×Z | 最高Y / 含岩體總高 | 三角面 | 材質 | 合批mesh | GLB MiB |
|---|---|---|---:|---:|---:|---:|
'''+ '\n'.join(rows)+'''

島台上限B30×28、D32×29、E34×31、H33×30全部保留，模型尺度1，沒有縮放玩家、世界或F/A/C/G。岩體最低Y=-8，總高包含浮島岩體，不代表建築層高。四個GLB共'''+f"{sum(m['glbBytes']for m in models.values()):,}"+''' bytes、'''+f"{sum(m['triangles']for m in models.values()):,}"+'''個獨有三角面、125個語義合批mesh；每島低於10萬三角面，新增貼圖／燈為0。模型尺寸由真實頂點計算。

## 路網、地形及既有成果

F/A/C/G的33份資產、碰撞、玩家／相機profile／政策／UI等檔案逐位元相同，中心與島形另有結構斷言。沒有繼承PR13歷史或模型。已認可島嶼的生成報告亦未覆寫；本次既有測試輸出的新證據移到本目錄。

採包內R21候選B/E/T4/T6/T7座標，T4=(51,-47)、S06左斜線；D/H中心不變。變更S02/S03/S06/S07/S08/S12/S13/S14/S17的候選曲線，其餘13條實際樣本完全相同。候選S14切入C原座椅，故保留原末40%精確道路與C橋口；S02保留原前28%以保護A。B四入口沿北／東側接到本地(4.7,7)共享節點，不再讓放射線穿過照護翼樓。詳見[衝突處理](ROAD-CONFLICTS.md)。

只改 `yuan-plan.json` 原始配置並重跑生成器；地面、橋面、聯集邊界、實體護欄、路燈錨點與碰撞同源。八島為同一個聯通網，22段道路、21節點、4.8核心、道路碰撞三角面坡度0。島體外邊界沒有內欄封橋口。四新島低位實體與4.8核心交疊均為0；新島彼此與F/A/C/G島面相交為0。

原始r欄位保留供既有比例／隨機種子與玩法相容；真正新島面由 `islandFootprintsXZ` 多邊形控制，並非半徑9草皮。新增地面有ownerIsland/walkway標記，能在擴大區域保存安全檢查點。

真正PR18→R21路長：'''+f"{before['totalCentrelineLength']:.3f}→{after['totalCentrelineLength']:.3f}，+{delta:.2f}%"+'''。增加來自包內擴大四島、末端調整與B安全內部繞行，沒有再次乘壓縮比例（.585仍為既有 metadata）。[完整八島最短路矩陣](network-comparison-r21.json)以真實路徑長和節點圖計算，並非各門到門距離。舊生成器的歷史A比較另存 `network-comparison.json`，不得拿其1137數值冒充本輪基準。

保留36盞既有燈ID，11個錨點隨已變道路重投影，其餘路段燈完全原樣。這是接入資料同步，不是新五區橋景或7字路燈設計／施工；後續仍需另行核准設計。

## NPC與通行

四島各保留一個3×3乾地區，未新增人物或對話。完整方形與建築／植栽／島緣／4.8路芯檢查，不沿用研究包只有圓形的檢查。下表為島內X/Z；facing以rad記，位置與面向集中在 `src/data/bdeh-plan.json`。

| 島 | NPC預留 | 玩家停留 | 面向 | 3×3方形至路芯距離 |
|---|---|---|---:|---:|
'''+ '\n'.join(npc)+'''

另獨立驗證3×3方形外加.35邊距不侵入核心，玩家以真實.33膠囊半徑內縮取樣，九點皆乾地且無低位阻擋。資料Y=.15是預留值，未來實作NPC需以真實地面probe貼地。舊 `future-island-reservations.json` 是前期歷史預留，不是本輪四島有效NPC來源。

可走的是地面公共通道、B庭院、D門檻、E半戶外論壇、H戶外論壇；樓內、E高架植生屋頂、D跨通道屋頂均不宣稱開放。牆柱玻璃有水平阻擋，地面、支承、屋頂、頂棚和相機障礙分離。E水面不作地面／牆，真實淺盆底Y=.33承托，視覺水面Y=.37；這是4cm淺水花園，不是G深水域，G九處水面跌落復位回歸仍通過。水盆底不保存乾地檢查點。

## 工程驗證與測試失敗追蹤

- `npm run check`：83個具名單元測試通過、lint通過、正式build通過。沒有把subprocess EPERM造成的檔案數當案例數。
- 完整Playwright首輪68項：60通過、4跳過、4失敗。完整原始結果保存在 [regression-initial/playwright.json](regression-initial/playwright.json)。兩個失敗是未等.4復位抬高落地就判斷位置；兩個是放大後逐個曲線小面邊界的browser測試超時。
- 修正斷言等待落地，未改Player／重生邏輯。島緣browser改為每島按順序均勻抽24段，完整邊界的掃掠碰撞另有單元幾何檢查；未假稱browser逐一走完全部細分線段。F的0個通用島緣取樣由原V9北／東／西實走護欄測試另行覆蓋。
- 最終production build（17,171.87kB JS、gzip2,014.09kB）重跑受影響6項，6/6通過、0跳過、0重試：[最終Playwright](regression-final/playwright-affected-recheck.json)。合併案例身分為64通過／4不適用，**不是聲稱單次最終全套68項全部通過**。四個桌機觸控不適用跳過可見原報告；真觸控瀏覽器對應案例已測。
- 桌機／觸控尺寸均實際載入四個GLB並核HTTP SHA；真實Player走四島公共迴路、NPC接近、8個orbit方向／島、全景進出狀態完整恢復、擴大區檢查點與跌落復位。Node相機測試另有128個頭／軀幹／低輪廓姿態。
- 22段S01–S22雙向、無跳躍；最終既有橋景路測每個profile18690ticks、0復位。八島公共空間實走與島緣sample每個profile139個有效起點，未採用的乾地／實體阻擋起點逐筆列於spaces報告，不能算成通過。原生鍵盤及單指搖桿跨島既有案例亦通過。
- F新版車站四口、A四口與建築遮擋、C NPC及彈跳、G路網／水邊／九次濕區復位、五風鈴身分／home真按鍵互動、政策八項開關／手機資訊、全景、縮放與輸入等既有回歸保留。

初期另曾發現C座椅與S14真實衝突、D橋景一片Float32零面積三角形、過期全世界快照／r9夾具、B花床路徑、E高差；分別修正真幾何、剔除零面積耳片及更新明確R21相容契約，沒有刪掉批准資產的檢查。33份原樣鎖定與13段精確樣本斷言均通過。

截圖驅動曾因orientation resize在人工draw後清canvas，使D/E及手機全景空白；證據保留 `iteration-5-capture-driver/`。加入真實canvas尺寸／camera aspect斷言與兩次原生rAF等待後重拍全部38張，已重新檢視，沒有以改遊戲相機或替換圖片解決。

## 效能比較

以下均為同一個八島載入世界，before為F/A/C/G資產SHA一致的PR18凍結build；相同F原出生位置／原生camera profile與正交全景，桌機1200×800、觸控直式430×932、DPR1。數字是Three renderer.info（含既有陰影pass的提交量），不是獨有模型三角形。每視角2warmup後6次gl.finish；CPU為5批100個真實idle Player ticks中位數。

| 階段 | 尺寸 | 視角 | Draw Calls | 提交三角面 | 軟體單幀中位ms | idle控制CPU ms/tick |
|---|---|---|---:|---:|---:|---:|
'''+ '\n'.join(perfRows)+'''

完整 [performance.json](performance.json) 有每次樣本、模型fetch／decode／建造時間、記憶體geometry／texture數與GPU字串。四島GLB本機fetch+decode約123–340ms；頁面loading解除時間before約16.9–81.3s、after約52.3–83.6s，變異很大，含軟體瀏覽器與整個既有世界初始化，**不是正式網路或真機首次可操作延遲**。

全景提交量1089→1187calls（+9.0%）、1,644,970→1,929,986三角面（+17.3%）；這是四座正式建築、較大島體及陰影的實際增加，不宣稱零成本。軟體全景frame變慢，原生視角時間變異，不能推論真機FPS。新增材質沒有貼圖、透明只用必要玻璃，沒有新增動態燈或每幀重造建築；當前idle控制CPU約1.0–1.2ms/tick。build仍有大bundle警告：後續可將各島碰撞資料分塊／壓縮與延後解析、量測靜態陰影快取，這些優化本輪**未做**，不為達數字破壞已完成建築。

## 尚待人工與真機驗收／限制

1. 四島是否達C V3以上的主觀美術品質、建築用途及文化詮釋，仍須使用者正式批准；兩輪自查不等於批准。
2. 真實手機GPU／Safari、長時間單手手感、發熱、電量、弱網載入與硬體FPS未驗證。這次Chromium觸控尺寸＋SwiftShader不能冒稱實機。
3. 角色能在地面探索，室內與屋頂高架植生不開放；沒有NPC本體／對話。E植生仍屬低成本景觀示意，並非植物品種精修。
4. 預設鏡頭在建築旁會裁切高屋頂或看向另一側，保留真實原生圖；正常orbit能看到建築，QA總覽才完整包住整島。沒有拉遠預設鏡頭或改FOV來偽裝預設品質。所有自由視角的舒適度與視覺跳轉仍需人工玩測。
5. 一般步行護欄已測；刻意跳躍／滑翔越界不能宣稱完全防跌，保留安全復位。
6. 工程迴路會在島間傳送起點、以固定60Hz輸入加速驗證，並非連續真人跨八島影片。原生鍵盤／單指案例另測；本輪未要求或交付操作影片。
7. 既有橋景與36燈資料保留，本輪未實施新的五區景觀／7字路燈；Production與Cloudflare設定未更動。

目前沒有仍失敗的受影響自動化案例；上述未測項目不能列為通過。維持Draft、不合併、不正式部署，等待整體人工驗收。
'''
(O/'REPORT.md').write_text(report)
gallery=intro+'''
## 驗收入口

[完整工程、美術與限制報告](REPORT.md) · [重建與在Codex操作](REBUILD.md) · [修改檔案清單](FILE-LIST.md) · [SHA256與圖片尺寸](MANIFEST.json) · [GitHub逐檔下載收據](GITHUB-VERIFIED.json)

![四島同機位Blender總覽](four-island-blender-overview.png)

![真正遊戲QA四島總覽](four-island-game-overview.png)

![手機原生profile，正常orbit轉向](four-island-mobile-overview.png)

## 每島模型與多視圖

| 島 | 可編輯Blender | 正式GLB | 同源六視圖 | 美術審查／比較 |
|---|---|---|---|---|
'''
for c,title in [('B','幸福養老'),('D','智慧公所'),('E','宜居環境'),('H','教育發展')]:
 gallery+=f'| {c} {title} | [工程](../../design/bdeh-r21/{c}/{c}-r21.blend) | [GLB](../../../public/models/bdeh-r21/{c}.glb) | [六視圖]({c}/six-views.png) | [兩輪紀錄]({c}/SELF-REVIEW.md)、[初輪→精修]({c}/before-after-blender.png) |\n'
gallery+='''
## 真正遊戲／玩家畫面

每島 `game/{B,D,E,H}-desktop-native.png` 與 `mobile-native.png` 為原生距離／pitch／FOV；`-facing` 是正常orbit轉向；`-hero`、`-top` 是QA特製相機，不能當作預設畫面。手機直式430×932、橫式932×430、桌機1200×800，均DPR1。Blender800×600、Cycles64 samples。完整位置、camera、orbit、地面狀態、GPU、served bundle／GLB SHA見 [capture-record](game/capture-record.json)。

| 島 | 桌機原生／轉向 | 手機直式原生／轉向 | 手機橫式 | 全島QA | NPC預留視線 |
|---|---|---|---|---|---|
'''
for c in'BDEH':gallery+=f'| {c} | [原生](game/{c}-desktop-native.png)／[轉向](game/{c}-desktop-facing.png) | [原生](game/{c}-mobile-native.png)／[轉向](game/{c}-mobile-facing.png) | [橫式](game/{c}-mobile-landscape.png) | [主視](game/{c}-hero.png)／[俯視](game/{c}-top.png) | [桌機](game/{c}-desktop-npc-reservation.png)／[手機](game/{c}-mobile-npc-reservation.png) |\n'
gallery+='''
![真正八島苑字全景，無政策標籤](game/yuan-desktop-panorama.png)

[手機完整全景](game/yuan-mobile-panorama.png) · [實際路網前後矩陣](network-comparison-r21.json) · [碰撞與NPC空間稽核](geometry-stage-2.json) · [效能比較](performance.json)

## 實際可操作預覽

本機production preview使用4274；在同一Codex工作環境的Ports／Preview開啟4274即可操作，或checkout此分支執行 `npm ci`、`npm run dev -- --port 4274 --strictPort`。GitHub PNG／GLB頁面不是可操作網站。未啟動正式部署；若既有Cloudflare整合沒有產生可用Preview，不提供虛構網址。

## 驗證結果與界線

83個具名單元＋lint＋build通過。全套瀏覽器首輪60通過／4不適用／4失敗，修正驅動及資料後受影響6/6通過；按相同案例身分彙整64通過／4不適用，不冒稱單次最終68全通。22道路雙向與四島公共空間、NPC、鏡頭、政策、全景、復位已測，詳細範圍與排除起點在REPORT及JSON內。

**待人工批准：** 四島最終美術與用途辨識、真機手機FPS／Safari、長時間觸控及熱／電量。室內、屋頂、NPC、橋景／新燈未實作；不得視為已驗收。沒有合併PR或更新Production。
'''
(O/'README.md').write_text(gallery)
(O/'ROAD-CONFLICTS.md').write_text('''# R21 場址衝突及已驗證修正

1. B放射線切入R21曲線照護翼樓：保留四個真橋口，採包內北／東公共走廊，接到本地(4.7,7)共享hub。曲線、實際路面、護欄、碰撞與測試使用同一生成結果。
2. 原候選S14切入C原座椅：不移動C，保留原道路後40%精確樣本及末端；S02前28%同樣保護A。已在83單元及22段雙向browser重驗。
3. 原研究NPC只驗圓形與路線。完整3×3方形檢查發現B/D植栽、H花床及E道路衝突，明確成組移動植栽並重選乾地；最終NPC方形加.35m邊距不碰4.8路芯，建築／植栽重疊均0。
4. 初次多邊形聯集浮點掃描樹失敗：固定精度1e-5逐段聯集，未增加前端布林依賴。D細縫單片Float32零面積耳片在geometry生成時剔除，不改橋景美術。
5. E論壇地台不是障礙盒，而是真實可行走半戶外地板；入口兩段實體低階消除.345高差，實走無跳躍。水面不碰撞，真實混凝土淺盆底保留；H上層薄玻璃補實體碰撞厚度。

本輪R21四島最多30×28／32×29／34×31／33×30，沒有再擴大。F/A/C/G中心、島形、資產／玩法原樣。完整幾何與玩家驗證結果見REPORT、geometry-stage-2及regression-final；人工美術與真機仍待驗收。
''')
print('Final R21 report/gallery:83 units,6 affected browser cases,32 Blender views,38 real game frames;33 protected hashes verified')
