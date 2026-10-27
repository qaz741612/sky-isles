# 交通大升級 V9 原型｜GitHub交付

- 審查 Draft PR：[qaz741612/sky-isles #14](https://github.com/qaz741612/sky-isles/pull/14)。
- Base：`codex/seven-policy-islands-blender-assets-v1`；Head：`codex/transport-elevated-station-v9-blender-prototype`。
- 完整資產提交：`d05f0029ea7dd994d3501120a9ea813b294cca6a`。
- 精修BLEND來源SHA256：`a975409e16bf406b4fe1ae9981d632c527f85244387e3a88111baad4177f2abb`。
- 交付一份可編輯BLEND、精修展示GLB、遊戲優化候選GLB、十一張同源Cycles圖、核准參考並排圖、配置圖與完整工程報告。
- GitHub實際下載 **76/76** 檔案大小及SHA256相符，合計 **114,444,043 bytes**；[逐檔核對](github-verification.json)。

## 查看

[模型及全部視圖索引](README.md) · [逐項美術差異](ART-REVIEW.md) · [尺寸／軟體效能／未驗證項目](VALIDATION.md) · [原成果保留證據](source-preservation.json)。

點BLEND／GLB後在GitHub檔案頁使用 **Download raw file** 下載；BLEND使用Blender4.3或相容新版開啟。幾何及材質已保存在原檔，文字是實體mesh、木紋packed，開檔不必尋找外部原圖或字型。按數字鍵0可切入已保存的主相機，F12會用原生場景渲染。

## 已測及限制

- BLEND全源網格封閉／正體積，實際NPC清空區與輪軌接觸通過；四橋口、15個地面點及其他道路／安心生養交疊檢查通過。
- 兩GLB Khronos 0 errors／0 warnings；四組桌機／手機尺寸的Chromium實際載入、材質／圖片與WebGL檢查完成。
- SwiftShader軟體環境的候選平均約0.88fps（1280×800）、1.83fps（390×844），完整表格及24幀樣本見VALIDATION；這些不是桌機GPU或真手機FPS，也不是可直接上線的效能認證。
- 既有遊戲50項單元、lint、build通過，沒有宣稱新模型已進入遊戲物理或上下樓／電梯驗證。
- 預設手機鏡頭仍裁切部分上層；補充站位與zoom28圖明確標示為非預設。局部花園台地提案增加12.568面積，未寫回正式世界。候選透明薄玻璃近似與精修PBR的差異亦明列。
- 本報告與工具不能替人工確認90分美術／整合門檻；保持原型隔離，等待集中檢視，不開始NPC、任務、其他七島或正式整合。

未合併任何PR，未推送main或Production，未修改Cloudflare設定，未執行部署。所有提交有 `[CF-Pages-Skip]`；建立PR後查詢完整資產提交沒有部署check/status或公開Preview回報，不能把沒有觸發部署說成部署成功。
