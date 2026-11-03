# V5.1 重建與驗證

Node24、Blender4.3.2；離線Python需numpy、trimesh、Shapely2.1及Pillow。沒有新增遊戲npm依賴、貼圖、即時燈或外部素材。MIT及原第三方聲明保留。

```sh
python scripts/flood/prepare_v51.py
blender -b -t 1 --python scripts/blender/build_flood_v51.py
python scripts/flood/audit_v51.py
node scripts/qa/audit-flood-v51.mjs
blender -b -t 1 --python scripts/blender/render_saved_flood_v51.py
npm run check
```

以原V5的已定稿配置及生成程式產生基底構件，再套用 `src/data/flood-control-art.json` 與 `prepare_v51.py` 中命名的建築／水工構件。Blender建造器實際開啟原V5可編輯工程，保留匹配的原物件，只更新有變更的構件和G專用材質。原V5工程及完整成果不覆寫；新工程、每輪原檔及可追溯報告在 `docs/design/flood-control-island-g-v5-1/`。

島面與道路完全沿用V5，不執行 `generate:yuan` 或 `--site`。新碰撞仍由相同語意來源生成：乾地、可支承實體、牆柱、屋簷與攝影機表面分離；所有負高度水下支承排除於玩家落地面，牆柱仍有對應水平阻擋。單一NPC只有資料和空間，沒有角色/對話。

原始配置控制重建；若手動修改新.blend，需另行保存手改檔或回填生成參數，再匯出，避免下次重建回到腳本版本。GLB按原有區域／材質合批，原檔保留逐構件可編輯性。

實際驗證使用最後固定建置服務4265；4261/4263是明確歸檔的較早施工版本，不是最終驗收頁。可在本機checkout分支後使用：

```sh
npm ci
npm run dev -- --host 0.0.0.0 --port 4265
```

本機開 `http://localhost:4265`；Codex若提供Ports/Preview介面，可開啟該工作區的4265端口。本地地址不代表可從其他裝置直接訪問的公開Preview。本輪沒有執行正式部署。

完整實際Player路網/相機/檢查點工程測試：

```sh
G_QA_PORT=4265 G_QA_DIR=docs/previews/flood-control-island-g-v5-1 node scripts/qa/check-flood-v5.mjs --full
```

最後模型Playwright範例（Chromium軟體GPU時使用已有SoftwareQA）：

```sh
SKY_SOFTWARE_QA=1 PLAYWRIGHT_BASE_URL=http://127.0.0.1:4265 BROWSER_QA_SCALE=1 G_QA_DIR=docs/previews/flood-control-island-g-v5-1/regression-camera npx playwright test test/flood-control.e2e.js test/flood-interactions.e2e.js test/flood-v51.e2e.js test/world-spaces.e2e.js test/panorama.e2e.js --retries=0
node scripts/qa/capture-flood-v51.mjs docs/previews/flood-control-island-g-v5-1/game 4265
```

`measure-flood-v51.mjs` 比較4254原V5與4265最終版，透過實際HTTP GLB SHA確保取對資產；兩版都載入八島、相同視口/站位/QA鏡頭。SwiftShader只作診斷，不能當真手機FPS、熱量或長時間舒適度。

單元測試必須真正啟動子程序並顯示76個案例；受限環境若只有檔案級結果或EPERM，不能當案例通過。大型輸出寫檔，不打印GLB、Blender、Base64或完整測試JSON。不要提交work、node_modules、.blend1及__pycache__。
