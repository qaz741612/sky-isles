# 本輪檔案範圍

## 模型與審查資料

本目錄 `docs/design/parent-child-blender-refinement-v2/` 新增第二階段 BLEND／GLB、八張最終 Blender 渲染、兩張舊版同構圖重渲染、兩張並排比較、可行走空間圖、WebGL 驗證截圖、尺寸與三角面差異、配置、來源／實體／通行／載入檢查及媒體 SHA256。`README.md` 為入口，`REFINEMENT.md` 記錄設計取捨，`TECHNICAL.md` 列出方法與界線。

第一版的 `docs/design/parent-child-blender-model-v1/` 保持原樣，全部12個已列manifest的模型／媒體檔逐一核對SHA256沒有改變。

## Blender 工具

| 檔案（scripts/blender/） | 修改目的 |
| --- | --- |
| refine_parent_child.py | 新增：開啟PR11既有BLEND，精修曲頂、立面、深度、側廊、玻璃、遊具與景觀；同步匯出GLB |
| render_parent_child_views.py | 加入可指定輸出目錄及固定取景參數，保留原版預設行為 |
| render_parent_child_before_comparison.py | 新增：原BLEND同相機／尺度重渲染，不覆寫舊模型 |
| audit_refinement_lineage.py | 新增：入口幾何保留證據及組件尺寸／屋面分割線統計 |
| audit_parent_child_space.py | 新增：評估實體高度裁切、保守投影、四入口與NPC區檢查 |
| validate_parent_child.mjs | 支援新模型輸出目錄，沿用Khronos與Three.js解析驗證 |
| validate_refined_webgl.mjs | 新增：暫時Chromium頁面真正繪製GLB，非新網站或遊戲場景 |
| finalize_parent_child_refinement.py | 新增：尺寸／面數差異、相同相機驗證、比較／索引／通行圖、manifest與ZIP |
| verify_github_media.py | 支援新輸出目錄，回讀GitHub原始二進位核對SHA256 |
| requirements-render.txt | 隔離工具環境增加shapely，用於幾何稽核，不改遊戲依賴 |

沒有改動 `src/`、`public/`、`package.json`、政策資料、苑字配置、其他島、角色或NPC系統。既有五張未提交的苑字預覽與 `work/` 保留，未混入提交。
