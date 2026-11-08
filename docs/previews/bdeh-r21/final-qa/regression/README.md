# 回歸證據分層

最終結果以 `playwright-final.json` 及原始 `playwright-implementation-final.json` 為準：同一凍結版本的一次完整 70 案例，未以舊版通過案例補算。`npm-check.json`／`npm-check.log` 保存單元、lint 與 build。

- `history/`、`final26/`、`spatial-critical/`、各 concurrent／companion／diagnostic／in-progress 檔：早期失敗、診斷或關鍵分批重測；不是最終整套認證。
- `continuous-camera-*`：真正 Player 固定 60Hz 橋口至 NPC 路線與相機時序；不是人類操作影片。
- `manual-temporal-portrait.json`：可信觸控驅動的固定步進一指旋轉；不透明結構六探針及正常轉動跨度；不是手機硬體 FPS。
- `spaces-*`、`browser-routes-*` 等：本輪完整回歸輸出的實際稽核資料；島緣為明確抽樣，不冒稱逐厘米證明。

保留先前失敗是為了追溯修正，不把它們與最終通過混合。人工美術、Safari、實體手機 GPU、發熱與長時間舒適度仍待驗收。
