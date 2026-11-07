# R21 可重建流程

基準：PR18 `2b4404927f33096ab28539a01f5e6236d670c038`。本工作在獨立 worktree `codex/bdeh-r21-game-integration`，沒有重寫既有歷史。原始ZIP的48個檔案保存在 `docs/design/bdeh-r21/source-package/`，其中47個原始manifest項目逐項相符。`build_r21.py` 才是建築來源；R18/R20檔案是其幾何工具依賴，不是選用舊建築。

## 版本與相依

本次環境：Blender4.3.2、Node24.19、Python3、numpy、scipy、trimesh、Shapely2.1、VTK、Pillow。npm依賴沿用lockfile，未新增npm套件。Blender沒有OpenImageDenoise，最終使用Cycles CPU64 samples，沒有冒稱使用降噪。原生模型物件保持獨立可編輯，匯出才按島／語義／材質合批；世界沒有合成單一巨大網格。

建議在新worktree重建，避免覆寫已驗證的歷史圖片／工程。正常開發只需 `npm ci`、`npm run check`、`npm run dev`。可編輯最終工程與正式GLB已提交，不需要為了查看而重跑Blender。

## 完整幾何重建順序

```sh
python scripts/bdeh/configure_site.py
npm run generate:yuan
python scripts/bdeh/prepare.py --stage1
blender -b -t 1 --python scripts/blender/build_bdeh_r21.py -- --stage1 --render
python scripts/bdeh/prepare.py
blender -b -t 1 --python scripts/blender/build_bdeh_r21.py
blender -b -t 1 --python scripts/blender/render_bdeh_r21.py -- --resume
npm run check
```

`configure_site.py` 以保存的原基準開始，沒有再次乘縮放比例。只修改唯一配置來源 `yuan-plan.json`，再產生layout/surface及既有橋景錨點。`island-approaches.mjs` 保護A/C既有近端道路，為B明確配置島內轉彎，不讓研究用直線穿進曲線翼樓。

`prepare.py` 讀取原始R21命名構件，寫入可重建parts、四島碰撞及NPC資料；沒有把研究GLB整座蓋到正式島面。臨時parts在 `work/bdeh/`，不提交。`--code E` 等選項可只更新一座模型，避免覆寫其餘模型。最終readonly渲染器開啟已保存.blend，核對SHA，不重新改寫模型。

## 遊戲與驗證

```sh
npm run dev -- --port 4274 --strictPort
SKY_SOFTWARE_QA=1 PLAYWRIGHT_BASE_URL=http://127.0.0.1:4274 BROWSER_QA_SCALE=1 npx playwright test --workers=1 --retries=0 --reporter=json > work/browser-report.json
```

在Codex Ports／Preview開啟4274即可真正操作。正式截圖使用production build的本機preview，原生玩家鏡頭、QA俯視及Blender渲染各自標示。瀏覽器測試必須使用可建立subprocess及本機HTTP的執行環境；不能將EPERM導致的測試檔案計數當成真正案例通過。

實際遊戲截圖：`scripts/qa/capture-bdeh-r21.mjs <輸出目錄> <port> <該凍結build的models/bdeh-r21>`。它會核對伺服器GLB及編譯bundle SHA。使用原生第三人稱距離、pitch與FOV；facing只是一般orbit轉向，hero/top明確是QA相機。

效能：`scripts/qa/measure-bdeh-r21.mjs` 讀取保存的PR18 build與最終build，相同F出生視角／全景、桌機／觸控尺寸比較。連接埠和路徑集中在檔頭，換環境時須調整。SwiftShader數據不能當成真實手機FPS。

## 保護、交付與界線

33份原樣模型／碰撞／玩家／政策／UI檔案用 `PROTECTED-BASELINE.json` 鎖定，F/A/C/G中心、島形與13段未變路線另有結構斷言。舊版全世界快照失效的8份衍生資料改以明確R21契約檢查，未放寬已認可模型檢查。

`manifest-bdeh-r21.py` 將交付、來源、修改程式及相依檔案列SHA並解碼檢查所有圖片。推送後用 `verify-bdeh-r21.py <40字commit>` 從GitHub逐檔串流下載，生成下載驗證收據。不輸出二進位、Base64或大型JSON。

不合併、不部署Production、不製作NPC、室內、音樂、橋景或新路燈。新增四島美術仍須人工驗收。
