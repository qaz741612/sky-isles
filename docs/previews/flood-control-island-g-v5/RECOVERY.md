# G V5 施工恢復點

基底PR17 cd4bacba72b6a1f7bf607c687566dc14f12c4896；分支codex/flood-control-island-g-v5；Draft PR18。原F/A/C源與資產、中心及22曲線不動，36路燈錨點相同。

第一輪b623cae有模型/圖。第一輪通行判定因漏攔退化樹幹邊的NaN已撤回，兩張原生畫面無效；iteration-1紀錄已標示不可作驗收。

現已完成三閘/機械/水位/玻璃指揮中心、原點擴島西側內凹與S22外部橋口/跨水厚板、單NPC、完整碰撞/相機與擴島檢查點。第二輪圖/模型存iteration-2；第三輪修正北岸座椅及門廊柱旁路徑；目前原始工程/GLB 60,211三角面、50批次，71單元/lint/build通過。

最終可玩建置4254：work/g-v5-playable-dist。嚴格每幀finite的G全22段雙向與32方位鏡頭檢查正在重跑(work/g-v5-full-routes-fixed.log)，不要沿用先前失敗資料。廣泛64案仍在4252較早建置執行(work/g-v5-browser-all.json)，最後需在4254重測受G影響案例。原生截圖與Frozen Blender圖也必須從最後資產再產生並核對SHA；現blender/為前一個bench版本，不能混作最後圖。

Blender最終輸出由scripts/blender/render_saved_flood_v5.py唯讀開啟已凍結.blend，不重新生成幾何。source產生流程prepare_v5.py --site → generate:yuan → prepare_v5.py → build_flood_v5.py(先不加--render)，先過實際路線才渲染。模型變更後要重新輸出相同來源圖。

未完：最終嚴格遊戲/瀏覽器/水邊與鏡頭回歸、最後十視圖和桌機手機遊戲圖、舊G1效能對比、報告/manifest/GitHub下載核對。不要宣稱美術通過或真機FPS通過，不合併不部署。禁止清除或reset原工作目錄；保留.blend1、work與node_modules但不要提交它們。
