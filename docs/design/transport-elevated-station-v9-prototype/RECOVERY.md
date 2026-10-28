# 中斷恢復檢查點（非最終驗收）

2026-10-28 恢復執行環境後確認：上輪原生 Blender 編輯程式、最終一次重建的 BLEND／展示 GLB 仍在。舊 PR #14 工作目錄與五張使用者未提交圖片沒有清除或覆寫。

此檢查點包含可恢復原檔及程式；候選 GLB、圖片與部分報告仍來自較早輸出，必須重新生成並核對，不能將本檢查點稱為完成版本。

本地 worktree：`/workspace/sky-isles-transport-open-v9`，基底為已核准的 PR #11 美術分支 ac433fd。PR #14 遠端仍在 81f7408。此 worktree 只作獨立製作與驗證；交付時只將交通專用檔案回填原 PR #14 工作分支，不修改 PR #13、已核准安心生養或正式遊戲。

中斷診斷：前輪工具回報 exec-server transport disconnected／No usable execution environment。重建 log 尾端 OPEN_PLATFORM_SAVED 已確認成功：BLEND SHA256 `9070e0fbb22c8b494849845de3508fb089e3680e22445752d0d798059b7011b7`。之後須重跑座椅外溢、四口、NPC、GLB及同源渲染驗證。
