# 工程與實際驗證

## 修改範圍與重現

基礎為 PR #11 的 `a3474c26c81ce826090c491fec94a8e615a69271`。精修工具 **先開啟這份既有 BLEND**，檢查來源 SHA256，再修改其屋頂、窗構、側翼、材料及景觀。主入口成功的木雨棚／拱牌和側向木格柵以評估後世界座標網格 hash 比對，形體與位置保留完全一致，見 `lineage-audit.json`。

第一版原始模型與渲染保留於 `../parent-child-blender-model-v1/`。本輪不修改遊戲 `src/`、`public/`、正式政策、其他七島、相機控制、遊戲依賴或部署設定；沒有遊戲建置／玩法回歸成果冒充本階段模型驗收。

一般使用者直接用 Blender 4.3 開啟本輪 `parent-child-centre.blend` 即可編輯與渲染。單位為建模尺度，不是正式建築測繪尺寸。Blender Z-up；匯出 GLB Y-up。

在專案根目錄，具 Cycles／OpenImageDenoise 的官方 Blender 4.3 可執行：

```sh
blender -b -t 2 --python scripts/blender/refine_parent_child.py
blender -b -t 2 --python scripts/blender/render_parent_child_views.py -- --out docs/design/parent-child-blender-refinement-v2 --fixed-framing
blender -b -t 2 --python scripts/blender/render_parent_child_before_comparison.py
```

空間稽核與媒體排版需要隔離 Python 工具環境中的 `shapely>=2,<3`、Pillow 與 bpy 4.3.0，列於 `scripts/blender/requirements-render.txt`。沒有安裝進 Vite 遊戲依賴。

```sh
python scripts/blender/audit_parent_child_space.py
python scripts/blender/audit_refinement_lineage.py
python scripts/blender/finalize_parent_child_refinement.py
```

配置集中於 `layout.json`：平台半徑、側翼前後面、屋頂參數、遊具／樹木變換、NPC 位置及四入口規劃線。原平台生成器沿用 PR #11 的同一段實作，隨半徑重建底座、鋪面、橋口與開口欄杆；不是修改遊戲生成配置。

## 實際檢查

| 檢查 | 結果與依據 |
| --- | --- |
| 來源版本 | 本機與遠端 PR #11 分支同為 a3474c2 後開始；來源 BLEND SHA256 精確核對 |
| 成功入口保留 | 入口雨棚／拱牌、入口側格柵的評估網格與世界座標 hash 與原檔一致 |
| 實體構件 | 1,872 個評估 Mesh，非流形／非正向體積問題 0，見 solid-geometry-audit.json |
| 四入口規劃 | 四條 1.2 寬規劃通道對實體包絡重疊面積 0；半徑0.35玩家中心路線無接觸 |
| NPC 預留 | 單一活動半徑0.65保留區、玩家接近點與模型實體無重疊；不侵入四條規劃通道 |
| GLB 格式 | 官方 Khronos gltf-validator：0 errors、0 warnings |
| Three.js 解析 | GLTFLoader 真正載入最終 GLB，缺失材質0，模型尺寸及材質另記錄 |
| 真正 WebGL | Chromium 實際繪製並截圖，WebGL error 0，未捕獲頁面 JS 錯誤 |
| 八視角來源 | 相同最終 BLEND SHA256、逐張相機／採樣／大小／PNG SHA256 |
| 公平前後比較 | 舊 BLEND 另重渲染主視角、俯視圖；前後位置、旋轉、正交尺度、尺寸相同 |

空間稽核把評估後實體裁至高度 **0.22～1.78**，取各構件 XY 保守凸包，低於0.22的地板／踏步視為可踏面，高於頭部的屋簷不當作地面阻擋。先設計位置，再稽核並修正西入口燈柱／樹冠、西南花台／攀爬架及 NPC 保留區。此方法沒有模擬坡面行走、階梯高度、相機、動態角色或跳躍，不能聲稱已通過遊戲碰撞或無障礙認證。

主通道規劃止於玻璃門前的半戶外雨棚；不以路線穿過關閉門扇。1.2寬走廊採平端帽；玩家半徑0.35另用圓形端帽檢查。最近的中心線障礙距約0.423出現在終點靠門處，不表示整條走廊只有0.846寬。

## GLB 與渲染成本

GLB **380,999 三角面、207 材質網格批次、29 材質、20,239,060 bytes**。Blender 修改器評估後為 **381,520 三角面**；匯出器處理後略不同，兩種實際計數分別保留，沒有以 Decimate 偷改外觀。

`.blend` 保留原物件及非破壞修改器，GLB 仍按可獨立調整的組件／材質合批。核心屋頂、窗、遊具與樹木都有實際幾何，沒有使用外部貼圖或假室內畫片。

瀏覽器驗證的 renderer.info 量得 **414 calls**、**761,998 rendered triangles**，包含 transmission 所需的額外繪製；不能把它當成模型有76萬三角面。GLB無圖片貼圖，WebGL內部1個texture為傳輸渲染目標。驗證為軟體 Chromium、單模型及測試光照，**不是手機 FPS 或完整八島效能報告**。

```sh
npm install --prefix work/parent-child-blender/gltf-validator gltf-validator
node scripts/blender/validate_parent_child.mjs docs/design/parent-child-blender-refinement-v2
node scripts/blender/validate_refined_webgl.mjs
```

以上工具不啟動政策島服務、不修改遊戲、不發布網站。WebGL畫面光照與Cycles不同，只用於確認實際 GLB 可繪製與材質存在。

## 相機與輸出

沿用八個既有方位及位置，主視角1600×1096／96 samples，其餘1400×959／64 samples，Cycles CPU + OpenImageDenoise。正交視角為較大平台調整取景範圍，沒有變更觀察角或縮放模型。兩個修改前重渲染使用同一組取景參數，因此比較不以遠近製造大小錯覺。正／背面以完整建築立面為主，部分橋端邊角不在畫內；完整平台輪廓請看主視角與頂視圖。

主斜視角沿用 PR #11 的相機，俯角約29°；依需求通稱的「45°主視角」製作比較，沒有擅自轉成另一個不相同的精確45°俯角。屋簷及玩家高度相機保留既有鏡頭。

`renders/`：八張最終實際Blender渲染；`before/`：兩張真實舊模型重渲染；`comparison-*.png`／`eight-views.png`：上述圖片排版；`walkable-space.png`：由實際幾何計算的規劃圖；`three-webgl-validation.png`：實際GLB繪製。媒體種類、尺寸、大小與SHA256分開記錄，不把示意圖當遊戲截圖。

## 不部署

本輪不合併PR或部署。若更新原PR分支，提交使用 Cloudflare 官方支援的 **`[CF-Pages-Skip]` 前綴**略過自動部署，不改Cloudflare設定。依據：[Cloudflare GitHub integration — Skip build](https://developers.cloudflare.com/pages/configuration/git-integration/github-integration/)。上傳後另核對該提交的檢查／部署紀錄，與上一輪已存在的Preview分開。

人工仍需確認本輪美術品質與平台尺度；整合階段再驗證真正角色碰撞、控制、相機、LOD及實機負載。本輪完成後停止。
