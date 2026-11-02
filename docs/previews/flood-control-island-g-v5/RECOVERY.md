# G V5 可恢復狀態（最終驗收進行中）

分支 codex/flood-control-island-g-v5，基於 PR17 cd4bacb；Draft PR18。F/A/C、22條Bezier與36個既有燈錨點保護。

已保存：最終60211三角面/50批次/23材質模型、獨立可編輯Blender、真實水洞/三閘口/西側S22入口凹灣/碰撞/相機。22路雙向與G公共動線在桌機/手機逐幀有限值實走通過，擴島NPC前庭檢查點/全景返回/強制跌落復位通過。71單元與lint/build通過。

最終10張Blender渲染已從同一凍結檔唯讀輸出；俯視取景55為截圖專用，不改遊戲原生相機。來源SHA在render-record.json。

仍進行：最終遊戲圖/軟體GPU前後量測、Playwright補驗、報告與GitHub下載驗證。初版大型回歸55通過/4桌機不適用略過/5失敗；兩個G動線失敗由座椅修正；水邊舊測試將合法端點繞行誤認成穿欄，已加入實際有限欄段掃掠/逐幀接地重驗。首張畫面測試曾在共用軟體GPU逾時，尚須補驗。不把以上待辦標成通過。

重建指令：venv Python scripts/flood/prepare_v5.py --site → npm run generate:yuan -- --report-dir docs/previews/flood-control-island-g-v5 → venv Python scripts/flood/prepare_v5.py → blender -b -t6 --python scripts/blender/build_flood_v5.py → blender -b -t6 --python scripts/blender/render_saved_flood_v5.py。venv需numpy/trimesh/Shapely2.1，Pillow用於對照與manifest。不要執行舊版build-flood-site.mjs覆蓋V5。

保留iteration-1失效NaN報告與iteration-2/3未通過歷史；不要混當最終圖。work/、node_modules、.blend1與__pycache__是未交付暫存，不reset/clean。維持Draft，不合併、不Production部署。
