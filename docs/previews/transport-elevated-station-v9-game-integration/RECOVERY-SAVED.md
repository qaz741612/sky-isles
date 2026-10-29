# 執行環境恢復與 WIP 保存（非整合交付）

## 本次實際確認

- 命令列 `pwd`、`git status`、`node --version` 正常；Node v24.19.0。
- 原目錄 `/workspace/sky-isles-transport-integration` 仍存在，未提交成果成功取回。
- 已 fetch 原整合分支，遠端恢復點為 `35cf44c16096e58cf569c85cb70ec34d06f85315`。
- 從該提交建立獨立 `codex/transport-elevated-station-v9-recovery-wip`，將現存修改原樣保存。沒有把 PR #13／#14 的分支歷史合入。
- 完整本機備份：`/workspace/recovery-backups/transport-integration-20261029T014124Z/`。包含所有本目錄未提交及未追蹤檔案、符號連結記錄、二進位 diff、index diff、全部 worktree 的狀態清單。封存內容逐檔 SHA256 驗證成功；符號連結未展開成依賴包。
- 其餘 worktree 的未提交圖片、模型及程式保持原樣，沒有 reset、clean、刪除或覆蓋。

## 已取回並保存

1. `scripts/build-yuan-world.mjs`：局部多邊形地基支援草稿。
2. `src/data/yuan-plan.json`：僅新增 `islandFootprintsXZ.F`，與核准基底比較，其餘 top-level 內容完全一致，包括節點、22 段曲線、寬度及既有壓縮結果。本輪沒有執行生成工具。
3. `src/world/islands.js`、`src/world/bridges.js`：準備交由新站接管 home 地面及護欄的未完成修改。
4. `src/sim/walkways.js`：新代理膠囊高度與 noCheckpoint 支援草稿，尚未回歸。
5. `scripts/transport-v9/extract-collision.py`：既有只讀擷取工具，未在本輪執行 Blender。
6. `src/data/elevated-station-model.json`、`elevated-station-collision.json`：現存輸出；JSON 可讀，記錄 2,241 個地面三角形、844 個頂部碰撞三角形、128 個實體區、22 個相機實體區、52 段斜向／階梯側面護欄。這是檔案盤點，並非遊戲驗收通過。
7. 指定候選 GLB 已存在且 SHA256 為 `d9292bf4e7b6c667e75f5e3d668ff5fb52eca2677a7c2cb080a95193b31878ac`，無須重新下載或建模。
8. 本機只讀 Blender 來源 SHA256 為 `5d99e81f8255f815e60ab0d63615ce024e96533c6757821beb74eb777c7eade6`。與兩份來源 JSON、既有擷取紀錄一起另存於 `recovery-inputs/`，供未來重建 work 輸入；不是新模型版本。

`WIP-MANIFEST.json` 記錄已保存原始程式、資料與資產的大小及 SHA256；`RECOVERED-FILES.json` 記錄備份時所有未提交檔案。

## 未存在、必須後續實作的部分

- `src/world/elevated-station.js` 不存在；上輪失敗命令並未寫入。
- `src/main.js`、`src/world/transport.js`、`src/data/transport.json` 仍與核准遊戲基底一致，尚未接入新站或移除舊版重複設施。
- 新地基的衍生路面尚未重新生成；樓梯限制、新站碰撞、相機代理、四入口及互動測試未完成。
- 安心生養共用載入工具 `station-model.js`、`parent-child-model.js` 及玩家速度／基本物理檔案未改。

**此 WIP 不是可玩的版本。home 舊地面碰撞已在草稿中移除，但替代地面尚未接上，可能跌落。不得部署或當成完成整合。**

## 下一個最小步驟（本輪未執行）

在保留本 WIP 後，先實作並單獨檢查新站載入模組與替代地面／阻擋／相機代理，再銜接交通執行路徑；替代地面可靠前不要發布或展示可玩版本。之後才進行衍生幾何生成及遊戲回歸。

若未來需執行現存擷取工具，可由 `recovery-inputs/` 複製來源到新的 `work/`，先核對雜湊；本輪沒有執行任何擷取、建模或渲染。

## 本輪界線與驗證狀態

僅恢復、備份、靜態盤點、來源完整性及 WIP 保存。未執行 build／lint／遊戲／瀏覽器／Blender 驗收，均不得視為通過；沒有新 Preview。沒有合併、重寫歷史、修改 Production、改安心生養、施工橋梁景觀或觸發部署命令。WIP 提交使用 `[CF-Pages-Skip]` 防止既有 Cloudflare Pages 自動建置；不修改平台設定。
