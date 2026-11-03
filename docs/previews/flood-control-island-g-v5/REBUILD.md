# 重建、測試與預覽

單一手調來源為 `src/data/flood-control-plan.json`。來源包只取建築構件；不匯入參考用島台、道路、NPC 或局部護欄。原始幾何腳本中的歷史壓縮已反映在建築座標，不再乘算。

環境使用 Node24、Blender4.3.2；Python 需 numpy、trimesh、Shapely2.1（constrained_delaunay_triangles）、Pillow。這些僅為離線工具，沒有新增遊戲 npm 依賴或外部素材。

依序執行（`python` 指向具上述套件的虛擬環境）：

```sh
python scripts/flood/prepare_v5.py --site
npm run generate:yuan -- --report-dir docs/previews/flood-control-island-g-v5
python scripts/flood/prepare_v5.py
blender -b -t 6 --python scripts/blender/build_flood_v5.py
blender -b -t 6 --python scripts/blender/render_saved_flood_v5.py
python scripts/flood/audit_final_v5.py
npm run check
```

Blender 建模器先產生可編輯原檔，再輸出靜態合批 GLB。唯讀渲染器不改模型／GLB，正上方 QA 取景55避免裁切，來源SHA與相機完整存於 render-record。舊 `build-flood-site.mjs` 在V5明確停止，避免舊流程覆寫新水洞與C島燈錨點。`init_v5.py` 僅為第一輪初始化，已有V5時立即返回，不用它覆寫最終配置。

預覽（另開終端，沒有正式部署）：

```sh
npm run dev -- --host 0.0.0.0 --port 4254
```

在 Codex 的 Ports／Preview 介面開啟4254。若外部介面無通道，可本機 checkout 此分支後以相同命令開 `http://localhost:4254`。此輪驗收用的4254是獨立最終建置；4233是唯讀PR17比較版本，並非對外部署網址。

逐幀無跳躍路網驗證：

```sh
G_QA_PORT=4254 G_QA_DIR=docs/previews/flood-control-island-g-v5 node scripts/qa/check-flood-v5.mjs --full
```

Playwright 使用既有 `SKY_SOFTWARE_QA=1` 模式，保留原生輸入、物理與UI，限制軟體GPU持續提交，不驗證真機連續FPS。範例：

```sh
SKY_SOFTWARE_QA=1 PLAYWRIGHT_BASE_URL=http://127.0.0.1:4254 BROWSER_QA_SCALE=1 G_QA_DIR=docs/previews/flood-control-island-g-v5/regression-final npx playwright test test/flood-control.e2e.js test/flood-interactions.e2e.js test/world-spaces.e2e.js test/panorama.e2e.js --retries=0
node scripts/qa/capture-flood-v5.mjs docs/previews/flood-control-island-g-v5/game 4254
```

效能比較需要同時啟動原始PR17比較版4233，並在 `work/g-v5-baseline/` 保存原始資產供SHA核對。`measure-flood-v5.mjs` 本輪以4個獨立頁面量測，遇量測器30秒等待預算不足時保存有效桌機樣本再以180秒回應等待續測；診斷保留在 diagnostics，並非遊戲通過條件。

不要提交 node_modules、work、.blend1 或 __pycache__；原V1 Blender與舊成果仍保留，未reset、clean或改寫歷史。MIT及既有第三方聲明沿用。
