# 早期診斷（不計入最終通過）

- A 初測的步點位於島緣之外／東南牆角餘裕不足：改圓角不規則地基後 A 全線通過。
- B 初版樹幹與兩處花台侵入道路核心、廊柱與 NPC 區重疊：重排後幾何單元通過。
- 早期環線步點位於樹幹碰撞範圍：改走旁邊已有可用路線，沒有刪掉樹或碰撞。
- 早期 walkways 單元使用舊 G 圓盤/臨時模型 fixture：改為真實新 G 碰撞與屋頂分類後通過。
- 開發版 Vite 熱重載中斷瀏覽器與部分截圖：結果捨棄作驗收，改固定 production build 完整重跑。
- QA 暫停 app frame 時全景按鈕未更新：工程 QA 改為手動呼叫真正 app frame，而非改遊戲 UI，固定版通過。
- Blender 無 OIDN：停用降噪，Cycles CPU 原生 48 samples。
- 跨水護岸錯成實牆：已改有淨空的真實橋底，重新匯出/六視圖/GLB 載入與全22路線驗證。

舊完整日誌仍保留於本機 work/；最終可重現證據是 logs/、routes-*.json、interactions-*.json 與 capture-record.json。
