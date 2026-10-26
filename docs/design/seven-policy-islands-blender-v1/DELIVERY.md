# GitHub 交付紀錄

- 美術審查 Draft PR：[qaz741612/sky-isles #13](https://github.com/qaz741612/sky-isles/pull/13)。
- Head：`codex/seven-policy-islands-blender-assets-v1`。
- Base：`codex/parent-child-glb-integration-v1`，保留現有 PR #12 的既有遊戲成果；來源提交 `75e3af5bb5205e52247011cfe5b59cbbc784e4ed`。
- 完整資產提交：`37ce3d2c125181356fee80afb02c1db3825bb0ec`。
- 7份新 BLEND、7份新 GLB、42張原始 Cycles 渲染、7張六視圖索引及1張同尺度總覽。另有舊交通 BLEND/GLB 原樣備份。
- GitHub 原始檔下載 **152/152** 大小及 SHA256 相符，合計 **162,013,497 bytes**；含全部交付 manifest 檔與8張原始參考。證據：[github-verification.json](github-verification.json)。

## 查看與下載

先看 [七島索引](README.md) 的同尺度總覽，再點各島名稱看六視圖及尺寸。下載模型請點各島 `BLEND`／`GLB`，在 GitHub 檔案頁使用 **Download raw file**；BLEND 用 Blender 4.3 或相容新版開啟。

所有美術圖都是實際 Cycles 渲染；總覽／六視圖索引僅排版實際渲染，不是AI生成成果。GLB隔離 WebGL工程畫面保留於 work，未混入美術圖。

## 修改範圍

- `docs/references/policy-islands/`：8張完整參考、對照與雜湊紀錄。
- `docs/design/seven-policy-islands-blender-v1/`：7套資產、實際渲染、尺寸／苑字相容性、幾何／GLB／WebGL／相機／上傳核對報告及舊車站備份。
- `scripts/blender/build_policy_assets.py`、`policy_assets/`：共用幾何、材質、每島明確配置與語意分組匯出。
- `scripts/blender/render_policy_assets.py`：固定相機六視圖，來源與圖片 SHA 保護。
- 其他同目錄新增 `*policy_asset*`／`*policy_assets*` 稽核工具、最終報告工具、`finish_transport_track.py` 與工具端 requirements；完整逐檔差異見 [PR Files changed](https://github.com/qaz741612/sky-isles/pull/13/files)。
- 遊戲 `src/`、`public/`、套件及正式苑字配置零修改；安心生養原始 BLEND／GLB完全相同。原有5張未提交預覽圖保持其原始內容並排除在新提交外，見 [保留紀錄](source-preservation.json)。

## 驗收與發布狀態

美術驗收未代替使用者決定。花帶較疏、廣場留白較多、玻璃／樹冠與家具簡化等差異見 [VALIDATION](VALIDATION.md)。交通、產業青年、治水圓展台超過12，尤其交通需審查局部拓展，不能直接套回遊戲。

未做七島完整遊戲整合、玩家碰撞、正式橋口聯集、真機FPS或NPC系統。`npm run check`僅證明未修改的既有遊戲50項單元測試、lint及build正常。

未合併任何PR，未推送main或Production，未修改Cloudflare設定，未執行部署。所有資產提交均有 `[CF-Pages-Skip]`。建立PR後查詢此資產提交，GitHub未回傳部署check/status或公開Preview網址；不把未觸發部署解讀成部署成功。

完成本輪，停止並等待一次整體美術驗收。
