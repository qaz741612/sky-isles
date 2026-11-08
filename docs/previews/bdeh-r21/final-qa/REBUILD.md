# 本輪可重建程序與畫面來源

本輪從 PR19 `39f41940fd3af0f432b477ebd36ad5b677a71db1` 已完成的正式 Blender 增量精修。**不要重跑早期 R18／R20 或 stage1 建模來源覆蓋本輪工程**。

```sh
python3 -m venv /tmp/sky-isles-bdeh-tools
/tmp/sky-isles-bdeh-tools/bin/pip install -r scripts/bdeh/final-qa-requirements.txt
npm ci
blender -b -t 1 --python-exit-code 1 --python scripts/blender/polish_bdeh_final.py
/tmp/sky-isles-bdeh-tools/bin/python scripts/bdeh/final_collision.py
blender -b -t 1 --python-exit-code 1 --python scripts/blender/audit_bdeh_final.py
blender -b -t 1 --python-exit-code 1 --python scripts/blender/render_bdeh_r21.py -- --output docs/previews/bdeh-r21/final-qa
blender -b -t 1 --python-exit-code 1 --python scripts/blender/export_bdeh_camera_canopies.py
npm run check
npm run dev -- --port 4302 --strictPort
```

Blender4.3.2；Python 碰撞工具使用現有 NumPy、trimesh、Shapely。沒有新增遊戲依賴。`polish_bdeh_final.py` 自動從 `docs/design/bdeh-r21/final-qa-baseline/` 的正式原檔開啟，保留主體，只做具名的局部增量；可使用 `--code E`。產出的 `work/r21-final-qa/*-polish-parts.json` 為碰撞計算暫存，不是另外一套場景。路網生成器本輪不執行。

正式原檔仍在 `docs/design/bdeh-r21/{B,D,E,H}/`，執行中的 GLB 在 `public/models/bdeh-r21/`。渲染器只讀同一份最終 .blend，輸出每島8張，record 包含原檔SHA。遊戲截圖額外核對 HTTP 實際回傳 GLB 與編譯 JS 的SHA，不能以本機檔案存在代替載入證明。

比較圖重建：分別啟動 `39f4194` 與本輪 production build 在4275及4302，執行：

```sh
node scripts/qa/capture-r21-final.mjs 4275 docs/previews/bdeh-r21/final-qa/game-before --models docs/design/bdeh-r21/final-qa-baseline/public/models/bdeh-r21
node scripts/qa/capture-r21-final.mjs 4302 docs/previews/bdeh-r21/final-qa/game-after --models public/models/bdeh-r21
python scripts/qa/boards-r21-final.py
```

兩側使用相同玩家位置、尺寸、初始原生 profile、5秒停留及一指手勢：先水平-120px，再+240px。實際 camera、quaternion、lookTarget、orbit、FOV 全部在各自 capture-record 中；局部相機修改本來就會使最終觀看方位不同。沒有把 before 也改成新鏡頭來假造對照。

原生桌機1200×800、直式430×932、橫式932×430均 DPR1。**橫式為新開該尺寸頁面**，原始 profile 距離18；直式22，桌機16。不是把直式22距離延用到旋轉橫式的歷史圖片。QA-hero／QA-top 有獨立明確檔名，不作玩家畫面。

局部相機只在四島乾地停穩0.45秒後緩慢提供到達方位；行走中不自動旋轉，手動旋轉或縮放立即接管該次造訪。原始 orbit.pitch、dist、FOV 不變；使用局部 pitch／觀看目標、頭／軀幹硬視線及較寬六探針預測餘裕。行走接近本島真實高牆柱時預先平滑縮臂，原 zoom 值不變，開闊處恢復；不在越過柱影後突然硬拉回。樹冠只讀鏡頭殼與玻璃分類由同源Blender重新匯出，不作玩家碰撞或額外draw calls。單幀快取僅重用同一位置與預測偏移的完全相同視線查詢。離開四島時 F/A/C/G 原有約束和 profile 照常使用。

瀏覽器測試使用 `SKY_SOFTWARE_QA=1` 控制 SwiftShader 提交量，仍使用真 GLB、原生rAF／物理／UI，對畫面案例顯式繪製。固定60Hz行走稽核及操作回放另行標示，不能當硬體流暢度。避免與 Blender 或其它 WebGL 擷取同時跑；完整結果與失敗證據見 REPORT。

補充近景（不改寫源Blender、不取代玩家視角）：`blender -b -t 1 --python-exit-code 1 --python scripts/blender/render_bdeh_final_details.py`。GLB原始buffers／法線／尺寸稽核：`/tmp/sky-isles-bdeh-tools/bin/python scripts/qa/audit-r21-glb.py`；相機作用域：同一Python執行 `scripts/qa/audit-r21-camera-domain.py`。

離線幾何／圖片工具的實際版本已固定於 `scripts/bdeh/final-qa-requirements.txt`；Blender內部Python與遊戲npm依賴分開，不需在遊戲加入Python或新套件。上述/tmp虛擬環境是可攜重建示例，與作者工作階段的既存venv路徑無關。

最終鏡頭查詢使用 `src/sim/r21-triangle-index.js` 的局部靜態三角索引：仍保留原六探針、預測與 Three.js 三角交點規則；不以省略身體可見度檢查換取速度。索引只適用固定的四島鏡頭殼，動態／自訂 raycast 幾何退回原查詢；四島之外沿用原相機。1119組差分射線驗證包含本輪實際模型、鏡射、材質組及實例。索引約12MB CPU buffer 加 Map 管理成本，沒有新增可見網格或 Draw Calls。

完整重驗：`SKY_SOFTWARE_QA=1 PLAYWRIGHT_BASE_URL=http://127.0.0.1:4302 npx playwright test --workers=1 --retries=0 --timeout=240000`。最終資料流水線與畫面輸出順序見 `scripts/qa/final-r21-pipeline.py`，效能基線仍須另開4275。H相同4132 tick CPU診斷的 before/after 明確是工程固定步進，不能當FPS。
