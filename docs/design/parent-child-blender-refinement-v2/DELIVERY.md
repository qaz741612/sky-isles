# 第二階段交付紀錄

更新同一份草稿 PR：[PR #11](https://github.com/qaz741612/sky-isles/pull/11)。來源分支維持 `codex/parent-child-blender-model-v1`，Base 維持 `codex/transport-station-glb-integration-v1`。沒有新建另一個網站或合併任何 PR。

模型與媒體提交：`5bffc3e1f7e9face5ff3661f1b15496421736160`。

## 已回讀核對

**18/18** 個檔案由 GitHub raw 重新下載，大小與 SHA256 全部一致：BLEND、GLB、八張最終 Cycles 渲染、兩張原模型同構圖重渲染、兩張並排比較、八視角索引、幾何規劃圖、WebGL實際截圖與完整ZIP。

[逐檔URL及雜湊結果](github-verification.json) · [媒體種類／尺寸／大小／SHA256](media-manifest.json) · [完整包SHA256](bundle-manifest.json)

下載包約29.3MB，包含模型、全部圖片及打包當時的設計／測試資料；本上傳後紀錄、遠端核對與部署觀察是另追加的文件，不回寫已核對的ZIP。

原PR11的12個模型／媒體檔與原manifest逐一比對一致。既有五張未提交的苑字預覽與先前備份逐位元相同，`work/` 保留；沒有混入本輪提交。

## 不部署及分支核對

模型及後續文件提交都採 **`[CF-Pages-Skip]`** 前綴，使用既有Cloudflare整合官方支援的略過機制，不修改設定、不手動部署。

觀察到模型提交在GitHub的check runs及commit statuses都是0，未出現Cloudflare新部署檢查；不是把上一輪Preview當成本輪成品。此環境沒有直接查詢Cloudflare內部部署清單，證據範圍與時間見 [deployment-check.json](deployment-check.json)。

遠端Production `codex/yuanli-policy-islands-v1` 仍是 `8adc89ed23d1f74151ca70bab2b3bd730c6e54a5`，main 仍是 `a8a1c07ea1ed1d9d2fe259a97a64d08fcec8f2d1`。遊戲src/public/政策資料沒有本輪變更。

## 等待人工驗收

八視角、比較、尺寸差異、NPC空間及限制均在[圖庫說明](README.md)；本輪沒有遊戲整合、NPC模型、真正物理或真機效能驗收。格式及空間稽核通過不代表美術已經定稿。

完成本輪後停止，不自動進行整合或下一輪擴充。
