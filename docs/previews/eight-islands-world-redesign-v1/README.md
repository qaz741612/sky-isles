# 苑裡政策島｜八島建築、景觀與安全空間重製 V1

以交通島 V4 為基礎，完成同一個可玩世界中的八島重製。八島半徑皆為 9；島中心、22 段路線與 4.8 路寬未變，中心線總長仍為 **665.179**。本分支供整體人工美術與遊玩驗收，沒有合併或更新 Production。

[設計取捨與逐島限制](DESIGN.md) · [建置／測試報告](TESTS.md) · [效能報告](PERFORMANCE.md) · [實際操作影片](normal-operation.mp4) · [操作紀錄](operation-log.json) · [媒體來源與 SHA256](MEDIA.md)

## 最終遊戲全景

無政策標籤，實際正交 3D 鏡頭：

![八島無標籤全景](after/panorama-pure.png)

有八島名稱的 QA 全景：

![八島 QA 全景](after/qa-panorama-labelled.png)

[手機直式全景](after/mobile-panorama.png) · [手機橫式探索](after/mobile-landscape-home.png)

## 八島一般探索與手機畫面

各島均採相同本地玩家站位 `(0, 0, 3.5)`、既有桌面／手機初始 orbit 參數。沒有為交付圖片拉遠預設鏡頭，也沒有改變人物、建築或世界比例。這些是工程定位後的**正常探索鏡頭**；定位動作不代表影片使用傳送。

| 島 | 桌面一般探索 | 手機直式探索 |
|---|---|---|
| 交通大升級 | ![交通桌面](after/desktop-home-explore.png) | [手機](after/mobile-home-explore.png) |
| 安心生養 | ![親子桌面](after/desktop-tree-explore.png) | [手機](after/mobile-tree-explore.png) |
| 幸福養老 | ![養老桌面](after/desktop-temple-explore.png) | [手機](after/mobile-temple-explore.png) |
| 產業青年 | ![青年桌面](after/desktop-koi-explore.png) | [手機](after/mobile-koi-explore.png) |
| 宜居環境 | ![環境桌面](after/desktop-meadow-explore.png) | [手機](after/mobile-meadow-explore.png) |
| 智慧公所 | ![公所桌面](after/desktop-windmill-explore.png) | [手機](after/mobile-windmill-explore.png) |
| 治水防災 | ![治水桌面](after/desktop-crystal-explore.png) | [手機](after/mobile-crystal-explore.png) |
| 教育發展 | ![教育桌面](after/desktop-lookout-explore.png) | [手機](after/mobile-lookout-explore.png) |

## 正、側、背面與玩家尺度稽核

以下為清楚區隔的 **QA 特製相機**，不是預設玩家視角；建築稽核暫藏 DOM 操作／標籤，正面圖內保留同一玩家供尺度比較。正常探索與影片保留使用者介面。

[八島正／側／背面實景縮圖總覽](architecture-contact-sheet.png)（僅排列原始截圖，非概念圖）。

| 島 | 正面／玩家尺度 | 側面 | 背面 | 正上方 |
|---|---|---|---|---|
| 交通大升級 | [正面](after/qa-home-front.png) | [側面](after/qa-home-side.png) | [背面](after/qa-home-back.png) | [俯瞰](after/qa-home-top.png) |
| 安心生養 | [正面](after/qa-tree-front.png) | [側面](after/qa-tree-side.png) | [背面](after/qa-tree-back.png) | [俯瞰](after/qa-tree-top.png) |
| 幸福養老 | [正面](after/qa-temple-front.png) | [側面](after/qa-temple-side.png) | [背面](after/qa-temple-back.png) | [俯瞰](after/qa-temple-top.png) |
| 產業青年 | [正面](after/qa-koi-front.png) | [側面](after/qa-koi-side.png) | [背面](after/qa-koi-back.png) | [俯瞰](after/qa-koi-top.png) |
| 宜居環境 | [正面](after/qa-meadow-front.png) | [側面](after/qa-meadow-side.png) | [背面](after/qa-meadow-back.png) | [俯瞰](after/qa-meadow-top.png) |
| 智慧公所 | [正面](after/qa-windmill-front.png) | [側面](after/qa-windmill-side.png) | [背面](after/qa-windmill-back.png) | [俯瞰](after/qa-windmill-top.png) |
| 治水防災 | [正面](after/qa-crystal-front.png) | [側面](after/qa-crystal-side.png) | [背面](after/qa-crystal-back.png) | [俯瞰](after/qa-crystal-top.png) |
| 教育發展 | [正面](after/qa-lookout-front.png) | [側面](after/qa-lookout-side.png) | [背面](after/qa-lookout-back.png) | [俯瞰](after/qa-lookout-top.png) |

## 相同鏡頭修改前後

修改前為 `08e70ce` 的獨立固定建置。以下為額外的 **QA 固定光學位置對照**：使用既有桌面初始 orbit 光學參數，兩版相機位置、方向、尺寸與列車相位完全一致，暫藏人物與介面。原正常探索圖保留在 before／after（[正常鏡頭差異稽核](normal-framing-audit.json)）；舊版部分測試定位點會被景物碰撞推開，因此不宣稱那些正常圖的實際相機位置完全相同。新增島面是土地擴張，人物沒有縮放；本輪建築與景觀另行重製，沒有把整個島群縮放。

| 項目 | V4 | 本輪 |
|---|---|---|
| 交通島、文化牆與列車 | ![交通修改前](comparison/before-home.png) | ![交通修改後](comparison/after-home.png) |
| 社區長廊與花園 | ![養老修改前](comparison/before-temple.png) | ![養老修改後](comparison/after-temple.png) |
| 開放工作坊 | ![青年修改前](comparison/before-koi.png) | ![青年修改後](comparison/after-koi.png) |
| 公共服務入口 | ![公所修改前](comparison/before-windmill.png) | ![公所修改後](comparison/after-windmill.png) |
| 水路與安全穿越 | ![治水修改前](comparison/before-crystal.png) | ![治水修改後](comparison/after-crystal.png) |

[固定光學位置稽核](comparison/camera-audit.json)。其他逐島／手機修改前圖均位於 [before/](before/)，最終圖位於 [after/](after/)。

## 本機可操作驗收

執行 `npm ci`、`npm run dev -- --host 0.0.0.0`，在 Codex 的 Ports／預覽面板開啟 Vite 顯示的連接埠。此為開發伺服器，不會發布正式網站。用 WASD／方向鍵或手機左下單指搖桿行走；拖曳旋轉、滾輪／雙指縮放；點擊政策入口閱讀；用「全景／返回探索」切換。一般跨島不需要跳躍。

影片是正常時間、原生鍵鼠的自動操作，不用傳送、加速、直接改位置或固定 dt 推進；工程路網與島緣稽核則使用明確標示的加速實際 Player 測試。影片無音軌是瀏覽器錄影工具限制，不代表遊戲音樂／音效被刪除。本環境以 SwiftShader 軟體 WebGL 錄製，畫面速度與卡頓不能代表真機流暢度；未加速模擬。

## 待人工整體驗收

請比較八島輪廓、用途、庭院尺度、側背面與預設手機構圖，再決定保留或局部修改。自動化未證明文化詮釋、美術滿意度、實機發熱、長時間單手舒適度、極端縮放／葉片遮擋；這些沒有宣稱通過。刻意跳躍仍可越過部分防護，落下會沿用安全復位。
