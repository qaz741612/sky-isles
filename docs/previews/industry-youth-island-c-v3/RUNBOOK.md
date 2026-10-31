# C V3 重建與驗證

Blender 4.3.2、Node 24、Three.js 0.179.1。Python 資產工具使用 numpy／trimesh／shapely，圖片拼版使用 Pillow；沒有新增遊戲 runtime 套件。

## 資產

在專案根目錄、已安裝依賴的工作副本執行（不需重跑苑字生成器）：

```sh
python scripts/industry/prepare_c_v3.py
blender -b -t 4 --python scripts/blender/build_industry_c.py -- --v3 --render
npm run check
npm run build -- --outDir work/v3-delivery-dist
node node_modules/vite/bin/vite.js preview --outDir work/v3-delivery-dist --host 0.0.0.0 --port 4233 --strictPort
```

Python 建模前處理使用原 PR17 地形／廣場，再採用 source-package 中三個建築函式，沒有採用代理島台組裝函式。Blender 開啟原 V2.2 工程保留 archive，輸出新版檔案與 GLB。`--pass1` 只用於第一輪量體設計的幾何重現，不應覆寫最終資產後推送。

## 真正遊戲與測試

另開命令列；使用軟體 GPU 時建議分批循序執行，不將結果當成真機 FPS：

```sh
C_QA_PORT=4233 node scripts/qa/check-industry-c-v3.mjs --full
node scripts/qa/capture-industry-c.mjs docs/previews/industry-youth-island-c-v3/game 4233 --v3
node scripts/qa/capture-industry-c.mjs docs/previews/industry-youth-island-c-v3/game 4233 --v3 --porch
```

完整瀏覽器回歸使用 `SKY_SOFTWARE_QA=1`、`BROWSER_QA_SCALE=1`、`PLAYWRIGHT_BASE_URL=http://127.0.0.1:4233`、`C_QA_DIR=docs/previews/industry-youth-island-c-v3`、`SKYISLES_QA_OUTPUT_DIR=docs/previews/industry-youth-island-c-v3/regression` 再執行 `npx playwright test --retries=0 --reporter=json`，將 stdout／stderr 導向 `work/` 檔案，不打印完整報告。部分歷史測試仍輸出到原 G／橋梁報告目錄，請保留副本後恢復歷史報告，避免誤標成新版資料。

本次保存的廣泛回歸為 4232 建置；最後 C 相機修正後的 4233 另跑 C 互動、八島公共路徑／相機、安心生養與 F 測試。`browser-summary.json` 留下每輪結果，不隱藏失敗；`final-build-evidence/` 封存 4233 的成功報告，避免較早建置的並行廣泛回歸覆寫同名檔案。

## 比較與封裝

精修前比較使用 `0c7cab7e7e2a75537363a7736206aaa8134787f6` 的獨立唯讀基準遊戲建置（本工作階段 4224），不切換或重設目前分支。`scripts/industry/prepare_c_v3_baseline.py` 只擷取原 GLB／碰撞／相機的雜湊來源到 scratch，不會建立完整基準網站。

Blender 施工前圖由 `scripts/blender/render_c_v3_baseline.py` 唯讀開啟原 V2.2 .blend 產生。遊戲圖使用 capture 程式的 `--v3 --baseline`，連向原建置；前後站位、視窗、orbit 相同，特製 QA 視角另標示。

本次報告封裝程式 `scripts/qa/finalize-industry-c-v3.py` 讀取保存在 work/ 的四輪測試及最終 capture-record；`manifest-industry-c-v3.py` 產生路徑、檔案大小、圖片尺寸及 SHA256。`verify-industry-c-v3.py <完整提交SHA>` 從 GitHub 逐檔串流下載核對，僅印簡短摘要。

不要納入 .blend1、node_modules、work 或 Python cache。不要合併、改正式分支、部署 Production 或修改其它政策島。
