# 交付狀態

- PR： https://github.com/qaz741612/sky-isles/pull/12 （Draft，等待人工整合／美術／實機驗收）。
- Base：`codex/parent-child-blender-model-v1`，仍為 `ac433fd5d23f00d3aab9470d96349114e1a37b24`；Head：`codex/parent-child-glb-integration-v1`。
- 正常可操作 Preview： https://34a8b999.sky-isles.pages.dev 。由既有 Cloudflare GitHub 整合自動建立公開 Preview，執行程式提交為 `657ec0aa7ec984b5e0f71a168ec85f6a1b116ba0`，相同本機測試／截圖 bundle `index-9F6Uh_WJ.js`。
- 媒體提交：`90c23a8f492b1de78ef0856b63b5dfc1550339f3`。後續文件／錄影工具及本驗證資料採 `[CF-Pages-Skip]`，沒有更改 src／public runtime，無需重複部署同一份程式。
- [GitHub 回讀結果](github-verification.json)：7 張 PNG、1 部 H.264 MP4 及 1 份公開 GLB，9/9 的 byte size 與 SHA256 相符。下載的是該完整媒體提交的 GitHub raw 原檔，未使用聊天附件。
- 原生影片：960×640、238.08 秒、7,497,317 bytes；原始擷取 237.033 秒，最後 1 秒靜止尾幀。沒有加速或插值，六個路點完成、0 意外復位。低 FPS 已保留，不能代表真機手感。
- `npm run check` 通過；選定瀏覽器功能 12 個不同案例分批通過、2 個裝置限定跳過，初次 5 個逾時及後續重跑均保留紀錄。
- CPU 軟體 GPU 實測：整合版桌面 0.187 FPS、手機模擬 0.278 FPS；**不流暢，不宣稱效能驗收通過**。原版在相同環境也只有 2.527／4.328 FPS。真實顯示卡、iOS／Android、長時間熱量及操作舒適度待人工。
- 執行環境代理阻擋 pages.dev CONNECT（403）；Cloudflare GitHub 檢查回報成功，遠端實際操作仍待使用者開啟。沒有把代理拒絕當成網站本身故障。
- NPC 只保留站位與接近資料，不新增 NPC／對話或隱形阻擋；實際 NPC 身體測試 N/A。
- 其他七島美術、22 段固定橋網、正式政策、人物速度及核准 BLEND／GLB 保留。只將安心生養島半徑設為 10.2，重新生成相接路面與安全邊界。
- main 仍為 `a8a1c07ea1ed1d9d2fe259a97a64d08fcec8f2d1`；Production 分支 `codex/yuanli-policy-islands-v1` 仍為 `8adc89ed23d1f74151ca70bab2b3bd730c6e54a5`。
- 工作開始前存在的五張 `docs/previews/yuan-panorama/` 圖片與 work 暫存保留，沒有提交入本 PR。

完成本輪整合交付後停止；不合併、不修改 Cloudflare 設定或 Production、不開始其他島、NPC 或美術重製。
