# 本次剩餘工作交付與下載核對

[Draft PR #14](https://github.com/qaz741612/sky-isles/pull/14)。本次渲染、同機位比較、最新GLB載入量測與報告已交付；人工美術及真實遊戲整合仍待驗收。

**成果提交：7ee30fa56d720728e433bca807406002c9df4995。** 後續收據提交只更新本檔及github-verification.json，模型／圖片內容不變。

- [最新45°主視圖](https://github.com/qaz741612/sky-isles/blob/7ee30fa56d720728e433bca807406002c9df4995/docs/design/transport-elevated-station-v9-prototype/renders/hero.png)
- [手機預設同機位比較](https://github.com/qaz741612/sky-isles/blob/7ee30fa56d720728e433bca807406002c9df4995/docs/design/transport-elevated-station-v9-prototype/comparison-player-mobile.png)
- [11視角圖庫與模型下載](README.md)
- [逐項通過／未通過／待驗](ACCEPTANCE.md) · [本輪效能](PERFORMANCE.md) · [相機資料](render-record.json)

## 真正下載驗證

已從GitHub原檔下載125/125檔案，總128,387,104 bytes，每檔byte數及SHA256都相符。包含ca94f48的三模型、11張同源Cycles圖、4張舊來源比較用圖、4組並排比較、WebGL圖、資料與重現程式。詳見github-verification.json。

manifest本身直接與本地檔案逐byte核對；manifest／SHA256SUMS／本交付檔／下載收據避免自我雜湊循環，不列入manifest的遞迴hash。下載收據及本交付檔另作最後提交核對。

## 鎖定模型，沒有重新建模

asset-lock.json證明BLEND與兩份GLB仍和ca94f48完全相同。

| 資產 | SHA256 | 實際GLB三角面／大小 |
| --- | --- | --- |
| BLEND | 5d99e81f8255f815e60ab0d63615ce024e96533c6757821beb74eb777c7eade6 | 原可編輯檔，未重存 |
| 展示GLB | 32d021a0df38853012f752d0b1d1e3ff52d6dff2d0b4abfd90f8127f05c52980 | 516,324／40.65 MB |
| 候選GLB | d9292bf4e7b6c667e75f5e3d668ff5fb52eca2677a7c2cb080a95193b31878ac | 201,740／17.63 MB／49 primitives |

11張最終圖皆為上述BLEND來源，並逐圖核對PNG SHA。拆棚前圖放before/，來源另標a975409e...，沒有混入新版renders/。桌機／手機的相機位置、方向、鏡頭、尺寸保持一致；zoom28補充圖不冒充預設圖。它們是Blender玩家鏡頭模擬，非正式遊戲截圖。

## 實際測試與未通過事項

兩GLB Khronos零錯誤零警告；4組最新GLTFLoader／材質貼圖／WebGL測試通過、載入SHA與交付檔一致。原遊戲npm run check回報12個測試檔、0失敗，lint及build通過，不把舊50項或舊報告當新版整合證明。

SwiftShader軟體GPU的候選版桌機尺寸約1.06 FPS、手機尺寸約2.07 FPS，均53 draw calls；這不是實機FPS或流暢驗收。模型尚未接遊戲runtime，膠囊、踏階、相機避障與真機熱負載仍待整合。

手機預設車頭下緣仍被小亭／欄杆遮到，右端車尾及部分高架仍裁切；圖像與人工接受度列為部分通過／待人工，未偷偷拉遠。原始低角度棚拍圖下緣保留平面界線，未裁切掩飾。沒有宣稱美術90分或人工已通過。

## 分支與發布

既有PR14 head正常fast-forward更新，未reset、rebase或force-push。base仍為PR13來源，BRANCH-ISOLATION.md保持6d207cd原提案，未執行隔離。正式整合前仍須依方案排除未核准七島資產。

main、Production codex/yuanli-policy-islands-v1、PR13來源ref均維持原值；src、public、安心生養與苑字路網未改。既有五張使用者未提交預覽圖完整保留、未納入提交。沒有全地圖橋邊造景、合併、正式部署或Cloudflare設定變更；提交使用[CF-Pages-Skip]。完成後停止等待人工驗收。
