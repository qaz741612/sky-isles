# 技術、檔案與驗證

## 開發範圍

- 基礎提交：`c4c7edf5682c406ac83458b4cb7b3625b8af6486`。
- 獨立分支：`codex/parent-child-blender-model-v1`。
- 新增內容僅位於 `docs/design/parent-child-blender-model-v1/` 與 `scripts/blender/`。
- 沒有修改 `src/`、`public/`、政策 JSON、依賴鎖檔、Vite 設定、B 方案或遊戲主頁。既有未提交的歷史預覽與 `work/` 保留，沒有混入本輪提交。
- 沒有合併 main／任何 PR，也沒有修改 Cloudflare 設定或正式部署分支。既有 Git 整合可能因新分支自動建立公開 Preview；其遊戲仍為原版本，不是本模型的遊戲整合驗收網址。

## 實際模型資料

| 項目 | 實際量測 |
| --- | --- |
| 完整模型，寬／深／高 | 24.458／21.655／5.382 建模單位 |
| 建築群，寬／深／高 | 14.856／6.680／4.982 |
| Blender 評估 Mesh 物件 | 1,757 |
| Blender 評估三角面 | 370,116 |
| GLB 由 Three.js 真正載入後的三角面 | 369,608 |
| GLB 材質網格批次 | 197 |
| GLB 邏輯組件群組 | 36 |
| GLB 材質 | 29 |
| 貼圖／外部圖片 | 0 |
| 玻璃 | Principled／GLTF transmission 約 0.82、roughness 0.14、IOR 1.45 |
| 屋面名義厚度 | 0.16 |
| 玻璃幾何名義厚度 | 0.038 |

Blender 與 GLB 列出各自實際計數，匯出器的三角化與幾何資料處理會使結果不同。**沒有使用 Decimate／Draco 或降低屋頂細分來簡化外觀。**GLB 的 197 個批次按組件及材質合併，保存評估後位置與法線；可編輯 `.blend` 仍保留原物件與倒角修改器。

Blender 為 Z 向上，GLTF 為 Y 向上。前方為 Blender −Y／GLTF +Z。GLB 群組名稱經 Blender 名稱衝突處理後具有 `001` 尾碼，對照見 `assembly-dimensions.json`；不是遺失建築或景觀群組。

## 渲染來源

使用官方 Blender **4.3.0** 的 Cycles CPU 與內建 OpenImageDenoise，AgX 色彩管理。這是實際模型光線追蹤與標準降噪，不是 AI 生成的建築概念圖。

- 主視角：1600×1096、96 samples。
- 其餘七視角：1400×959、64 samples。
- 相機、採樣、來源 `.blend` SHA256 與每張 PNG SHA256：`render-record.json`。
- 頂視圖在渲染時根據完整模型外框自動取景，納入四段橋口；相機覆寫參數有記錄，不縮放模型。其餘相機來自同一個可編輯檔。
- 攝影棚背景、相機與補光留在 `.blend` 供 F12 重現，不包含在 GLB。GLB 材質和幾何可供 Three.js 使用，但正式 WebGL 照明與玻璃效果需整合階段另驗證。

## 實際驗證

1. Blender 評估後 1,757 個 Mesh：非流形邊及非正向體積問題 **0**。這是封閉構件檢查，不等於建築施工、遊戲碰撞或美術認證。
2. 官方 Khronos `gltf-validator`：**0 errors、0 warnings**，完整 JSON 另附。
3. Three.js `GLTFLoader.parseAsync` 真正讀取最終 GLB：**成功、0 缺失材質**。獨立取得建築、室內、遊具、景觀、底座、街道家具並量測尺寸。
4. 比對本輪基礎提交：遊戲與 `public/` 檔案 **沒有修改**。本階段沒有遊戲碰撞、單手操作或真機 FPS 的整合驗收；不把離線渲染當作遊戲效能數據。
5. 八張來源圖片的模型 SHA256 一致；封面索引僅縮小排版，八張原始 PNG 不改圖。
6. 離線對照文件已以 Chromium 驗證選入本機圖、3200×1166 PNG 匯出及 390px 排版。工程測試使用模型渲染當作測試輸入，沒有冒充原圖。受管理的瀏覽器封鎖 `file://`，測試改為空白頁載入相同文件內容；一般本機離線開檔仍待使用者確認。
7. 上傳後以 GitHub 原始下載內容核對檔案大小與 SHA256；記錄於 `github-verification.json`。

## 程式與重現

一般使用者可直接用官方 Blender 4.3 或以上開啟 `.blend`，不需要執行程式。物件、材質、相機與燈光均已保存。

從程式重新建模，請在完整 GitHub 專案根目錄執行：

```sh
blender -b -t 2 --python scripts/blender/build_parent_child.py -- --phase complete --samples 96 --width 1600 --render none
blender -b -t 2 --python scripts/blender/render_parent_child_views.py
```

單獨重出全模型頂視圖：

```sh
blender -b -t 2 --python scripts/blender/render_parent_child_views.py -- --only top
```

也可使用 CPython 3.11 的官方 `bpy==4.3.0` 模組；工具依賴列於 `scripts/blender/requirements-render.txt`。系統套件版 Blender 若沒有編入 OpenImageDenoise，請使用官方版本。本次工具環境位於 `work/`，不改遊戲依賴。

- `parent_child_geometry.py`：厚度屋頂、實體玻璃、型材、環形與曲線構件。
- `build_parent_child.py`：建築、室內、底座、相機及 Cycles 設定。
- `parent_child_landscape.py`：遊具、滑梯、沙坑、植栽、弧椅及燈具。
- `parent_child_export.py`：按組件／原材質合批、保存評估位置與法線，不改原 Blender 物件。
- `render_parent_child_views.py`：實體稽核及八相機真正渲染。
- `validate_parent_child.mjs`：Khronos 與 Three.js 載入／尺寸／範圍驗證。
- `finalize_parent_child_media.py`：原圖載入對照文件、八視角索引、尺寸／SHA manifest 及檢視包。

這是完整的**人工美術驗收稿**。參考圖未提供的背側面與室內採合理延伸；細節差距與未完成的靜態原圖合成項目見 `REFERENCE-COMPARISON.md`。未做下一階段遊戲整合。

Khronos 工具只安裝於工作區，不改專案依賴：`npm install --prefix work/parent-child-blender/gltf-validator gltf-validator`，之後執行 `node scripts/blender/validate_parent_child.mjs`。
