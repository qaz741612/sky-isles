# GitHub 交付與人工審查

- 草稿 PR：<https://github.com/qaz741612/sky-isles/pull/11>，open、未合併。
- Base：`codex/transport-station-glb-integration-v1`（`c4c7edf5682c406ac83458b4cb7b3625b8af6486`）。
- Head：`codex/parent-child-blender-model-v1`。
- 模型與媒體提交：`749a9f060fc2d22caa29884940d58866efab927e`。
- 本紀錄與 `github-verification.json` 為上傳後追加的純文件；檢視 ZIP 保持原始模型提交版本。

## 已回讀核對

由 GitHub raw 下載 13 個檔案，檔案大小與 SHA256 全數吻合：BLEND、GLB、八張原始渲染、八視角索引、離線對照 HTML 及完整 ZIP。逐檔 URL、下載長度及結果見 [github-verification.json](github-verification.json)。

既有五張未提交苑字預覽與先前備份逐位元比較一致，沒有覆寫、清除或混入新提交。遊戲 `src/` 與 `public/` 沒有本輪差異。

## 自動 Preview 邊界

GitHub 既有 Cloudflare Pages 整合自動建立公開 Preview，檢查結果 success：
<https://83567017.sky-isles.pages.dev>

**該頁仍為原本遊戲，沒有載入本次親子館模型。**建模成品請看 GitHub 圖庫，或下載 `.blend` 以 Blender 自由旋轉／編輯。沒有手動部署、改動 Cloudflare 設定、合併 PR 或推送 Production。

核對時 Production `codex/yuanli-policy-islands-v1` 仍為 `8adc89ed23d1f74151ca70bab2b3bd730c6e54a5`，main 仍為 `a8a1c07ea1ed1d9d2fe259a97a64d08fcec8f2d1`。

## 等待驗收

請先以主視角及八視角檢視屋頂輪廓、入口、遊具與庭院，再以 Blender 檢查背側面及屋簷。仍有原圖視覺差距，見 [REFERENCE-COMPARISON.md](REFERENCE-COMPARISON.md)。

模型已完成建模交付與格式驗證，**不代表原圖美術相似度已通過驗收**。原圖靜態並排 PNG 尚缺可讀原始影像；離線 HTML 可選入使用者既有2D檔後產出。沒有進入遊戲整合或下一輪擴充。
