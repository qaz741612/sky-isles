最新交付：62379b4 保存修正橋底模型，最新 GLB 四項與 17 單元模組通過、六視圖同源且 game/12 張均為最後資產。最終報告見 REPORT.md；後續提交只保存證據與 GitHub 核對。

最新：檢查點 B 六張同源渲染已完成，見 CHECKPOINT-B.md。後續正執行遊戲整合回歸。

# G 島恢復紀錄

Base 7c1b39b，分支 codex/flood-control-island-g-v1，工作目錄 /workspace/sky-isles-flood-g。

檢查點 A：Blender 結構模型已接入真實遊戲，桌機實走 22 段雙向及 G 公共環線通過（browser-A3）。初次繞建築測試發現東南島緣餘裕不足，已改為 28×26 圓角不規則輪廓後重測。水面不作地面，乾燥地面扣除水域但保留加寬到 6.5 的跨水路段。四周邊界使用重新生成的聯集，S21/S22 無內欄。

這是結構檢查點，不是最終美術。draft GLB 約 33k 三角面。正式美術尚待完成、手機及整合回歸尚未驗收。Blender 此環境不支援 OpenImageDenoise，已停用降噪，使用 Cycles CPU 原生渲染。

source: src/data/flood-control-plan.json。先 node scripts/build-flood-site.mjs，再 npm run generate:yuan -- --report-dir docs/previews/flood-control-island-g-v1，再 Blender build_flood_g.py；最後 runtime 由獨立 flood-control.js replacement 接入。勿混入 PR13 歷史。已核准車站及安心生養資產不變。

保留 work/ 與 Blender .blend1 本機備份；不要 reset/clean。服務 4210 是本機 Vite，不是正式部署。

最新水路修正：覆蓋水道的 18 個內側護岸面已改為橋側邊梁，橋底 -.32、上游水面 -.55，留下 .23 可視淨空，並補真實橋底。資產已保存到本機 final .blend / GLB，GLB 42,773 三角面；原 dry-floor/collision、玩家路線與 NPC 不變。最新 GLB 的 17 個單元模組、lint、build 通過，包含穿越橋底的水平幾何射線。正在重跑新版 GLB 桌機/手機四項與 final 遊戲圖片。最終六視圖尚在依次更新，檢查 render-record.json 全部 SHA 一致後才交付。

原固定版 16 項瀏覽器回歸為 15 通過、1 桌機觸控不適用跳過，詳 work/browser-fixed-build.log。不要把更早 Vite HMR 中斷的紀錄當最後驗收。
