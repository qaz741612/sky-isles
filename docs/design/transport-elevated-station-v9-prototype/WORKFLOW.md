# 可重現流程

Blender/bpy4.3、Python3.11、Shapely2.2、NumPy、Pillow；Three.js、KhronosValidator與Playwright使用既有專案／work工具環境。不修改runtime依賴。工具端Python可依 `scripts/blender/blender-assets-requirements.txt` 安裝；Khronos可用 `npm install --prefix work/parent-child-blender/gltf-validator gltf-validator@2.0.0-dev.3.10` 建立隔離路徑。Noto Sans CJK字型用於產生實體文字；原檔已是mesh與packed材質，開啟BLEND不需要外部字型或圖片。

```sh
node scripts/blender/elevated_station_v9/measure_reference.mjs
python scripts/blender/build_elevated_station_v9.py
python scripts/blender/optimize_elevated_station_v9_candidate.py
python scripts/blender/audit_elevated_station_v9_source.py
python scripts/blender/audit_elevated_station_v9.py
node scripts/blender/validate_elevated_station_v9.mjs
python scripts/blender/render_elevated_station_v9.py
```

GLB量測工具直接讀取專案內 `inputs/approved-v9` 的模型，圖片也保持同一專案來源路徑；work只暫存可重建的量測結果，無需重新上傳原圖。原始建模模組只讀取這些參考及原路線。官方Blender CLI亦可用 `blender --background --python scripts/blender/build_elevated_station_v9.py`。

保存BLEND保留各構件／Collections、可調材質、燈光、相機與另置的隱藏線框碰撞代理。GLB合批包含UV及法線；不包含棚燈／相機／碰撞殼／白模。候選僅在暫存匯出狀態調整倒角與微植栽，並另用optimize工具改薄玻璃；絕不回存覆蓋精修BLEND或展示GLB。

預設渲染會核對現有圖片SHA與來源BLEND SHA，只在兩者都一致才續用。十一視圖均為Cycles+OIDN，主視圖1440×1080/64samples，四向1200×900/40samples，其餘48samples；手機720×1280。額外手機相機只在渲染工作記憶體中建立，幾何不變，完整參數記錄於render-record。

```sh
npx vite --host 127.0.0.1 --port 4192 --strictPort
node scripts/blender/check_elevated_station_v9_webgl.mjs
npm run check
python scripts/blender/report_elevated_station_v9.py
```

WebGL只在本機獨立稽核頁執行，不載入政策島遊戲；效能測量避免與Cycles同時運行。最後報告工具強制核對來源、十一張PNG、兩GLB及測試報告，再製作對照圖／索引／manifest。

木紋是原創256px程式紋理，已打包於BLEND與GLB。Noto Sans CJK用於實體文字輪廓及報告標籤，沒有外部建築模型、未授權商標或新音樂。
