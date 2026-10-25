# 修改檔案與重現方式

## 運行原始資料

- `src/data/yuan-plan.json`：只改八島半徑為 9 及修訂註記，中心、全部控制點與路寬不變。
- `src/data/island-places.json`：八島手工配置、主量體／庭院／園路／樹群／座椅／水路及未實作 NPC 預留。
- `src/data/transport.json`：側向文化牆座標、方向、尺寸與新的邊界責任註記；四項既有願景文字保留。
- `src/data/yuan-layout.json`、`yuan-surface.json`：生成結果，包含擴島後共享外邊界、橋路碰撞與島內穿行鋪面，禁止分別手修。

## 場景與控制

- `src/world/place-kit.js`：共用材料、幾何構件、門廊、窗框、樹型、家具、薄收邊、柔邊接地影，以及分離的地面／水平牆／相機資料。
- `src/world/policy-scenery.js`：七座非交通島的各自建築與庭院組合，移除自動塞空格的主場景配置。
- `src/world/transport.js`：交通站場與月台雨棚、庭院樹蔭、文化牆、共用材料；全島外緣交由共享邊界，室內外碰撞分離。
- `src/world/bridges.js`：通透細橋欄、新版島緣低牆／欄杆、按島裁切且與橋接合的鋪面。
- `src/world/islands.js`：沿用半徑來源生成島面／岩體；文化牆面板朝向由配置資料控制。
- `src/sim/camera-clearance.js`：八島局部靜態空間索引，限定明確牆／屋頂相機殼體。
- `src/main.js`：組合分離的選取與相機障礙資料，不把所有裝飾當成地面碰撞。

## 生成、稽核與交付工具

- `scripts/build-yuan-world.mjs`：從唯一原始配置生成聯集外緣與島內鋪面，保留原 Bezier 採樣與坡度驗證。
- `scripts/audit-world-redesign.mjs`：固定配置、完整通道、NPC、島邊／筆端與構造紀錄。
- `scripts/compare-world-network.mjs`：V4 前後真正的路網長度、最短距離、半徑與外框比較。
- `scripts/capture-world-redesign.mjs`：桌面／手機正常探索鏡頭與明確標記的 QA 圖。
- `scripts/capture-world-comparison.mjs`：不受舊景物碰撞推位影響的嚴格同光學位置 QA 對照，與正常探索圖分開。
- `scripts/measure-world-performance.mjs`：同尺寸全世界載入後的渲染統計及實際控制器 CPU 比較。
- `scripts/record-world-redesign.mjs`：正常時間、原生鍵鼠的跨八島操作錄影，不直接寫入遊戲狀態。
- `scripts/finalize-world-media.py`、`verify-world-media.py`：最終原始碼／媒體來源核對、尺寸及 SHA256 manifest、GitHub 下載逐檔比對。

## 測試

- 更新 `test/yuan-size-b.test.js`：允許本輪明確要求的半徑變更，繼續嚴格鎖定中心、曲線、採樣與路寬。
- 更新 `test/policy-scenery.test.js`：檢查手工場所、完整通行帶、獨立外緣、NPC 預留及明確碰撞分類。
- 更新 `test/transport.test.js`、`transport-walk.e2e.js`、`transport-v4.e2e.js`：共享外緣責任、搬移後文化牆、正常鏡頭及相機相對輸入。
- 更新 `test/scenery.e2e.js`：八島逐一政策入口與全景回復。
- 新增 `test/world-spaces.e2e.js`：八島門廊／工作灣／書廊／水路跨橋、所有暴露島緣及逐島繞行相機。
- `test/walkways.test.js` 加入實際角色屋頂承載驗證；原有雙向全路網與全部路口保留。
- `test/panorama.e2e.js` 的測試截圖移到 `work/`，避免覆寫歷史交付圖。
- 原有物理、拼圖、觸控、全景、政策資料等測試保留。

`npm run generate:yuan` → `npm run lint` → `npm test` → `npm run build` → `npm run test:e2e -- --workers=1 --retries=0`。

測試／捕圖工具在驗收環境使用 `/usr/bin/chromium`；錄影與 MP4 轉檔需要 Playwright FFmpeg／系統 ffmpeg，媒體整理使用環境既有的 Python Pillow；這些不是網站運行的新依賴。

未改正式政策 JSON、人物、速度、音樂／音效系統、遊戲任務或 Cloudflare 設定；MIT 與既有第三方授權保留。
