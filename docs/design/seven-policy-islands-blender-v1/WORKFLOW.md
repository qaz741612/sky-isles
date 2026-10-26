# 可重複使用的建模／材質／匯出／渲染流程

## 工具

- Blender / bpy 4.3.0、Python 3.11；Shapely 2.2.0 用於工具端封閉平台與裁切石板，沒有加入遊戲 runtime 依賴。
- Pillow 用於原圖驗證及實際渲染的索引／總覽排版；Noto Sans CJK 用於報告標籤，不匯出字型或圖片貼圖到模型。
- 既有 Three.js 0.179、Khronos glTF Validator（隔離 work 工具安裝）、Chromium 軟體 WebGL。不是硬體 GPU 效能測量。

工具端版本鎖定於同資料夾 `blender-assets-requirements.txt`。GLTF Validator 的既有隔離路徑是 `work/parent-child-blender/gltf-validator/node_modules/gltf-validator`；可用 `npm install --prefix work/parent-child-blender/gltf-validator gltf-validator@2.0.0-dev.3.10` 建立，不改遊戲 package。

## 共用與每島配置

- `scripts/blender/policy_assets/kit.py`：原生實體屋頂、窗框、柱、門廊、植栽、木座椅、石板、局部凹池及展台。
- `recipes.py`：七張主效果圖各自的建築量體、庭院、設施、花帶中心線及 NPC 預留；明確設計位置，沒有空位搜尋或隨機塞物件。
- 材質從已核准安心生養 BLEND **唯讀附加材質**，不附加或修改其建築。使用奶油牆、暖木、灰青屋頂與層次綠植，另補必要草地、水及鋪面。
- `exporter.py`：保持 BLEND 可編輯原構件，GLB 按語意組／材質合批、保留法線；Studio／燈光／相機不匯出。列車保留獨立組。

## 建立與驗證

從專案根目錄，在已安裝上述工具的 Python 環境執行；官方 Blender 4.3 背景 CLI 亦可。程式最後在已寫完檔案後結束，請不要直接在開著其他未儲存工程的 GUI 中執行。

```sh
python scripts/blender/build_policy_assets.py --island transport
python scripts/blender/build_policy_assets.py --island senior
python scripts/blender/build_policy_assets.py --island industry
python scripts/blender/build_policy_assets.py --island environment
python scripts/blender/build_policy_assets.py --island digital
python scripts/blender/build_policy_assets.py --island water
python scripts/blender/build_policy_assets.py --island education
python scripts/blender/audit_policy_asset_sources.py
node scripts/blender/validate_policy_assets.mjs
node scripts/blender/policy_asset_footprints.mjs
python scripts/blender/audit_policy_asset_sites.py
```

Blender CLI 範例：`blender --background --threads 2 --python scripts/blender/build_policy_assets.py -- --island transport`。GLB／BLEND 都寫入各島子目錄；不寫任何遊戲檔案。

## 六視圖與最終報告

```sh
python scripts/blender/render_policy_assets.py --island transport --resume
```

對七個 ID 各執行一次。`--resume` 只有在現有圖的來源 BLEND SHA 與圖片 SHA 同時相符時才跳過。主視圖 1280×960／64 samples；四向 1100×825／40 samples；俯視 1200×900／48 samples；Cycles CPU＋OpenImageDenoise。七島主視圖相機與尺度固定相同。

全部六視圖完成後：

```sh
node scripts/blender/check_policy_asset_cameras.mjs
python scripts/blender/write_policy_asset_reports.py
python scripts/blender/finalize_policy_assets.py
```

finalize 會強制核對七份模型、42 張原圖的 SHA 與同一來源、七張主圖相機／正交尺度相同，再製作六視角索引及總覽、更新 bytes／尺寸／SHA256 manifest。

## 隔離 WebGL 相容檢查

```sh
npx vite --host 127.0.0.1 --port 4191 --strictPort
node scripts/blender/check_policy_assets_webgl.mjs
```

工具頁在 `scripts/blender/policy_assets/viewer.html`，僅載入單一 GLB 做真實繪圖；不執行現有政策島遊戲，不是另做一套世界。工程截圖存在 work；圖庫只展示 Blender 渲染。

所有 Git 階段提交均使用 `[CF-Pages-Skip]`，避免既有 Cloudflare 整合為純資產／文件重複建站；不修改 Cloudflare 或 Production。
