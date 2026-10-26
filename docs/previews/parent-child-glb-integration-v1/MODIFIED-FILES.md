# 修改檔案

## 執行程式與配置

| 檔案 | 用途 |
| --- | --- |
| `public/models/parent-child-centre/parent-child-centre.glb` | 核准 PR #11 GLB 的位元組相同副本，供遊戲載入 |
| `src/data/parent-child-model.json` | 來源 SHA、1:1 尺寸、四入口島內路線、目的地及 NPC 預留資料 |
| `src/data/parent-child-collision.json` | 從核准 `.blend` 唯讀生成的實體碰撞、地面、頭頂與相機代理 |
| `src/world/parent-child-model.js` | GLB 載入、同材質合批、展示橋臂介面處理、碰撞分塊與局部相機避障 |
| `src/main.js` | 兩個既有／新 GLB 並行載入，單一親子館取代、碰撞接線、靜態陰影與全景真實時間 |
| `src/data/yuan-plan.json` | 只修改 A 島半徑 9→10.2 |
| `src/data/yuan-layout.json`, `src/data/yuan-surface.json` | 原始配置重新生成的地面、橋口與共享安全邊界；沒有手改衍生資料 |
| `src/world/islands.js` | 本島原生草皮藏入石基座下、保留 RNG 序列、移出封閉室內的可選蘑菇 |
| `src/world/bridges.js` | 本島採核准原模型鋪面，移除會穿過封閉館舍的重複直線鋪面 |
| `src/world/policy-scenery.js` | 可注入已核准模型替換舊版親子館，其他島生成器保持原狀 |
| `src/world/station-model.js` | 匯出既有連通分件工具供共用；沒有更改交通島模型或邏輯 |
| `src/sim/walkways.js` | 可指定真實構件厚度 0；原護欄預設厚度與其餘島規則保持原狀 |

## 生成、測試及交付工具

- `scripts/build-yuan-world.mjs`：新增報表輸出目錄參數，避免覆寫前輪預覽。
- `scripts/build-parent-child-collision.py`：Blender evaluated mesh 唯讀匯出；禁止寫回來源。
- `scripts/audit-parent-child-integration.mjs`：來源、材質、其他七島、路網及 NPC 預留稽核。
- `scripts/capture-parent-child-integration.mjs`：真正正式建置的桌面／手機／QA 截圖及渲染統計。
- `scripts/benchmark-parent-child-integration.mjs`：相同遊戲位置／預設相機的前後版本真實 rAF 測量。
- `scripts/record-parent-child-integration.mjs`：原生按鍵／滑鼠實際步行、CDP 影格與原始時間戳。
- `scripts/parent-child-media-manifest.py`、`scripts/verify-parent-child-github.py`：媒體尺寸、大小、SHA256 與 GitHub 原檔回讀。
- `test/parent-child-model.test.js`、`test/parent-child.e2e.js`：真實 GLB、玩家四入口、目的地、頭頂／相機、UI 與全景回復。
- `test/yuan-size-b.test.js`：唯一授權半徑差異。
- `test/walkways.e2e.js`：橋中心線不變，使用真實模型的島內繞行路徑進行完整路線回歸。
- `test/panorama.e2e.js`：等待軟體 GPU、浮點位置容差與暫存輸出位置。
- `test/responsive.e2e.js`、`playwright.config.js`：本機正式建置 URL、明示的功能測試解析度；純 DOM 斷言停止重複 GPU 繪製。
- 本預覽目錄：真正遊戲畫面、錄影、來源／配置／測試／效能／部署與媒體核對報告。

## 明確保留

PR #11 原始 BLEND／GLB 與設計渲染未改。其他七島配置、交通建築／列車、正式政策、玩家控制／速度、音效、解謎及授權檔未改。執行工作開始前已存在的五張 `docs/previews/yuan-panorama/` 未提交圖片變更與 `work/` 暫存未包含於本 PR。
