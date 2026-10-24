# 本輪修改檔案

## 主要改動

- `src/data/yuan-plan.json`：集中島嶼、節點與曲線控制點；layout/surface 為生成資料。
- `scripts/build-yuan-world.mjs`：可重現共享區域聯集、三角化、外邊界護欄與路網比較。
- `src/world/bridges.js`、`src/sim/walkways.js`：靜態合併路面、護欄與碰撞空間索引。
- `src/world/islands.js`：以集中配置定位，保留原有模型與半徑。
- `src/sim/panorama.js`、`src/main.js`：鏡頭狀態機、平滑投影、全景模式、返回探索及縮放尺寸適配。
- `src/policies.js`、`src/ui.js`、`index.html`：全景入口、暫停輸入、政策入口顯示與恢復。
- `src/sim/player.js`：附近護欄查詢及腳底接縫備援探測。
- `src/world/sky.js`、`clouds.js`：全景時隱藏遮擋、探索時還原。
- `src/world/transport.js`：既有西側道路橋向 +Z 平移 1 單位，保留車站與列車。
- 測試、ESLint 瀏覽器環境、套件鎖定與開源授權補充。
- 本目錄：五張真實 3D PNG、路網比較、測試報告、原始紀錄與圖片 SHA-256。

## 完整清單

- `THIRD_PARTY_NOTICES.txt`
- `docs/previews/yuan-panorama/CHANGES.md`
- `docs/previews/yuan-panorama/NETWORK.md`
- `docs/previews/yuan-panorama/README.md`
- `docs/previews/yuan-panorama/VALIDATION.md`
- `docs/previews/yuan-panorama/desktop-explore.png`
- `docs/previews/yuan-panorama/images-manifest.json`
- `docs/previews/yuan-panorama/logs/browser-panorama.log`
- `docs/previews/yuan-panorama/logs/browser-regression.log`
- `docs/previews/yuan-panorama/logs/build.log`
- `docs/previews/yuan-panorama/logs/lint.log`
- `docs/previews/yuan-panorama/logs/unit.log`
- `docs/previews/yuan-panorama/mobile-explore.png`
- `docs/previews/yuan-panorama/mobile-portrait-panorama.png`
- `docs/previews/yuan-panorama/network-comparison.json`
- `docs/previews/yuan-panorama/panorama-labelled.png`
- `docs/previews/yuan-panorama/panorama-pure.png`
- `eslint.config.js`
- `index.html`
- `package-lock.json`
- `package.json`
- `public/THIRD_PARTY_NOTICES.txt`
- `scripts/build-yuan-world.mjs`
- `src/data/yuan-layout.json`
- `src/data/yuan-plan.json`
- `src/data/yuan-surface.json`
- `src/main.js`
- `src/policies.js`
- `src/sim/panorama.js`
- `src/sim/player.js`
- `src/sim/walkways.js`
- `src/ui.js`
- `src/world/bridges.js`
- `src/world/clouds.js`
- `src/world/islands.js`
- `src/world/sky.js`
- `src/world/transport.js`
- `test/app.e2e.js`
- `test/helpers/walk-tour.js`
- `test/panorama.e2e.js`
- `test/panorama.test.js`
- `test/walkways.e2e.js`
- `test/walkways.test.js`
