# 本輪可重建程序與畫面來源

本輪從 PR19 `39f41940fd3af0f432b477ebd36ad5b677a71db1` 已完成的正式 Blender 增量精修。**不要重跑早期 R18／R20 或 stage1 建模來源覆蓋本輪工程**。

```sh
npm ci
blender -b -t 1 --python-exit-code 1 --python scripts/blender/polish_bdeh_final.py
/workspace/.venvs/bdeh-r21/bin/python scripts/bdeh/final_collision.py
blender -b -t 1 --python-exit-code 1 --python scripts/blender/audit_bdeh_final.py
blender -b -t 1 --python-exit-code 1 --python scripts/blender/render_bdeh_r21.py -- --output docs/previews/bdeh-r21/final-qa
npm run check
npm run dev -- --port 4280 --strictPort
```

Blender4.3.2；Python 碰撞工具使用現有 NumPy、trimesh、Shapely。沒有新增遊戲依賴。`polish_bdeh_final.py` 自動從 `docs/design/bdeh-r21/final-qa-baseline/` 的正式原檔開啟，保留主體，只做具名的局部增量；可使用 `--code E`。產出的 `work/r21-final-qa/*-polish-parts.json` 為碰撞計算暫存，不是另外一套場景。路網生成器本輪不執行。

正式原檔仍在 `docs/design/bdeh-r21/{B,D,E,H}/`，執行中的 GLB 在 `public/models/bdeh-r21/`。渲染器只讀同一份最終 .blend，輸出每島8張，record 包含原檔SHA。遊戲截圖額外核對 HTTP 實際回傳 GLB 與編譯 JS 的SHA，不能以本機檔案存在代替載入證明。

比較圖重建：分別啟動 `39f4194` 與本輪 production build 在4275及4280，執行：

```sh
node scripts/qa/capture-r21-final.mjs 4275 docs/previews/bdeh-r21/final-qa/game-before --models docs/design/bdeh-r21/final-qa-baseline/public/models/bdeh-r21
node scripts/qa/capture-r21-final.mjs 4280 docs/previews/bdeh-r21/final-qa/game-after --models public/models/bdeh-r21
python scripts/qa/boards-r21-final.py
```

兩側使用相同玩家位置、尺寸、初始原生 profile、5秒停留及一指手勢：先水平-120px，再+240px。實際 camera、quaternion、lookTarget、orbit、FOV 全部在各自 capture-record 中；局部相機修改本來就會使最終觀看方位不同。沒有把 before 也改成新鏡頭來假造對照。

原生桌機1200×800、直式430×932、橫式932×430均 DPR1。**橫式為新開該尺寸頁面**，原始 profile 距離18；直式22，桌機16。不是把直式22距離延用到旋轉橫式的歷史圖片。QA-hero／QA-top 有獨立明確檔名，不作玩家畫面。

局部相機只在四島乾地停穩0.45秒後緩慢提供到達方位；行走中不自動旋轉，手動旋轉或縮放立即接管該次造訪。原始 orbit.pitch、dist、FOV 不變；使用局部 pitch／觀看目標與六探針安全相機。離開四島時 F/A/C/G 原有約束和 profile 照常使用。

瀏覽器測試使用 `SKY_SOFTWARE_QA=1` 控制 SwiftShader 提交量，仍使用真 GLB、原生rAF／物理／UI，對畫面案例顯式繪製。固定60Hz行走稽核及操作回放另行標示，不能當硬體流暢度。避免與 Blender 或其它 WebGL 擷取同時跑；完整結果與失敗證據見 REPORT。
