# C V3 最終保存／接續紀錄

分支：codex/industry-youth-island-c-v1；沿用 Draft PR17、base codex/flood-control-island-g-v1。沒有合併、重寫歷史、正式部署或引入PR13模型。

已推送檢查點：97a039f 第一輪實物／自查；1506228 第二輪最終模型／Blender渲染；a0830a7 最終遊戲圖、相機及重現程式。後續最終報告／下載核對提交可由本分支git log查得。

## 已保存與驗證

- .blend：docs/design/industry-youth-island-c-v3/industry-youth-c-v3.blend；GLB：public/models/industry-youth-c/industry-youth-c.glb。原V2.2工程、17個保護檔及原地形9,200唯一頂點不變。
- 最終9張Blender圖、17張遊戲圖；game/的模型/碰撞/相機SHA吻合；before/與comparisons/採唯讀舊資產及同機位。
- build、lint、64單元通過；完整瀏覽器初測59通過/4裝置略過/1輸出目錄錯誤，修正與針對重測後逐測項合併60通過/4略過/0未解決。歷史失敗未刪除，詳browser-summary。
- 桌機/手機真正Player全22段雙向不跳躍、C公共動線/相機/全景/復位通過。final-build-evidence封存最後4233建置結果。
- 檔案尺寸/圖片尺寸/SHA256在MANIFEST.json；從GitHub下載的核對收據在GITHUB-VERIFIED.json（完成上傳後產生）。

## 仍需人工

人工美術、真機FPS/發熱/長時間單手與相機舒適度未驗證。手機貼近工坊柱位仍可能局部遮住角色，已在REPORT明列。三棟室內關閉、不製作NPC。維持Draft等待使用者驗收，不開始其他島。

## 環境若再中斷

優先以目前GitHub本分支與MANIFEST/收據恢復，不重建整個世界、不reset/clean，不把work暫存或.blend1當正式成果。若暫存日誌遺失，必須明說並以已提交的browser-summary/同源圖/資產核對為準；需要重測才按RUNBOOK執行。

本工作階段最終production-build本機Preview在4233，並非公開URL；服務停止後以RUNBOOK重啟。
