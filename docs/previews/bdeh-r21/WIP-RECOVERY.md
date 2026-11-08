# R21 精修檢查點（尚未完工）

分支codex/bdeh-r21-game-integration，Draft PR19，base為PR18的2b440492。已保存四島可編輯Blender、GLB、三輪模型／圖像歷史與完整來源。最新模型為樹群尺度、立面／承重、H階梯封實和E平台入口踏面精修。

仍需完成：E的NPC方形預留區與4.8路芯分離驗證／微調；全82單元、瀏覽器全回歸、原生桌手機最終截圖、效能及GitHub下載驗證。舊單元已更新過期世界快照與場景夾具；新增六個實際模型／Player／NPC／相機案例，不將未完成項目當作通過。

Blender最終圖正在依各原檔SHA輸出；工作暫存work與node_modules未提交，不得reset/clean。F/A/C/G模型、模組及共用sim/UI/policies均在PROTECTED-BASELINE.json鎖定。保持Draft，不合併或部署。


2026-11-05 checkpoint: all four editable Blender projects and 32 final Cycles views saved. E NPC plot independently corrected to (-12,6.5), real tree relocated; 33 protected baseline hashes. Latest `npm run check`: 82 named unit tests, lint and production build passed. Full 68-case browser run still in progress; checkpoint/fall test driver and final water/glass semantics remain to be reviewed. This is WIP, not final art or real-device acceptance.

Final geometry checkpoint: refined Blender source, GLB and32 render SHA stay identical after semantic collision review. E water no longer creates floor/barrier; real concrete tray supports deliberate falls without taking a dry checkpoint. H thin clerestory glazing has physical collision. Latest npm run check:83 named tests,0 failures; lint and production build pass. Full browser initial run and final affected rechecks remain in progress. Final frozen QA build:work/bdeh-final-83-dist on local4274.


## 最終保存狀態（本輪停止點）

四島最終Blender／GLB／32張同源渲染／38張實際遊戲圖已保存；根目錄README、REPORT、REBUILD、MANIFEST與GitHub下載驗證是驗收入口。83單元、lint、build通過；68瀏覽器首輪60通過4不適用4失敗，修正後受影響6/6通過；詳見完整報告，不能將初輪失敗隱藏。全部最終圖已檢視；手機resize驅動已修正重拍。33個原樣F/A/C/G／共用檔案受保護。最終頁面bundle與最後一次83檢查build逐位元相同。

PR19保持Draft，以PR18 2b44049為base；不合併、不部署、不重寫歷史。下一步只有人工美術、原生硬體／Safari及長時間操作驗收，不自行開始橋景、路燈、NPC或其他擴充。work/node_modules/__pycache__不提交；其他工作樹的未提交資料未清除。最終提交可由GitHub PR19與GITHUB-VERIFIED.json追溯。
