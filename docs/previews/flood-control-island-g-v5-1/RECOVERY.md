# G V5.1 施工檢查點（未宣告完成）

基底PR18 `8849b89e99163c179973a31571498115c6c80e7c`，同一分支接續，未改寫歷史。原V5輸出完整保留，另存baseline原檔、GLB、碰撞及同機位圖。

已完成第一輪真實模型精修：三閘葉開度0.78（頂部離原梁0.05）、曲面出流／白沫／消能塊／內渠壁、觀測塔與入口構件、四功能區地坪及前庭植栽、保留樹冠與座椅精修；不改場址、路網、4.8核心及NPC資料。從原V5可編輯Blender保留2077個原物件，局部替換／新增660個，第一輪81081三角面／60批次。此版本只作第一輪自查，尚未通過遊戲及最終美術驗收。

工作流程：Python虛擬環境執行scripts/flood/prepare_v51.py（重用V5幾何與碰撞生成段，但不寫舊V5稽核或世界地形），Blender執行scripts/blender/build_flood_v51.py（開啟原V5 .blend，保留匹配原物件，局部更新），唯讀render_saved_flood_v51.py出圖。需再實際看圖修正，優化新增小構件倒角，重新完整渲染與測試。

V5.1原始調整集中src/data/flood-control-art.json；所有場址來源仍是原flood-control-plan.json，未更動。public G GLB與G collision將更新；F/A/C及原V5文檔的214檔保護SHA存於docs/design/flood-control-island-g-v5-1/protected-baseline.json。未新增透明水、即時燈、NPC或橋景。work/node_modules/.blend1不提交。不合併、不Production部署。
