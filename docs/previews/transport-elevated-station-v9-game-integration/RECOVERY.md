# 開放式高架車站遊戲整合：基底與恢復檢查點

狀態：**整合尚未完成；沒有新車站的遊戲Preview或驗收結果。** 本提交僅保存已確認的來源與架構發現，不宣稱模型已掛入遊戲。

## 獨立基底

- 分支：`codex/transport-elevated-station-v9-game-integration`。
- 基底：`codex/parent-child-glb-integration-v1`，提交`75e3af5bb5205e52247011cfe5b59cbbc784e4ed`。
- GitHub PR #12現行head已確認為該提交；包含PR #11已核准安心生養GLB的既有遊戲整合。
- PR #13以75e3af5為起點，故本分支沒有PR #13後續未核准七島資產。不得改從PR14整條分支建立遊戲整合基底。

## 只取指定車站資產

模型來源：PR #14的`ca94f48bccdc89a00e5a0688479214d6114915d6`。文件與驗證參考：`114a134c608026e97b08b0c2a2015e1e3d82c549`。

- BLEND SHA256：`5d99e81f8255f815e60ab0d63615ce024e96533c6757821beb74eb777c7eade6`。
- 展示GLB SHA256：`32d021a0df38853012f752d0b1d1e3ff52d6dff2d0b4abfd90f8127f05c52980`，516,324三角面／40.65 MB／91 primitives。
- 遊戲候選GLB SHA256：`d9292bf4e7b6c667e75f5e3d668ff5fb52eca2677a7c2cb080a95193b31878ac`，201,740三角面／17.63 MB／49 primitives。
- 候選薄玻璃與展示PBR有既有近似差異；遊戲選擇與全世界載入成本需實測，不能冒稱相同材質性能。
- 模型目前尚未複製至本分支public，也尚未載入runtime。後續須取指定blob／檔案、核對SHA，不能cherry-pick整個PR14或PR13歷史。

## 已直接從GitHub原始碼確認的整合風險

1. `src/world/parent-child-model.js`從`station-model.js`匯入`components`與`stationHeadroom`。不可直接刪除舊車站模組，破壞已核准安心生養的共用物理工具。
2. 舊`station-model.json`使用scale0.74、position(-0.5,-0.0259,-3.2)，且選取特定舊GLB名稱。V9資產是自己的世界尺度／節點命名，不能只換URL後保留舊變換或選取過濾。
3. `transport.js`另生成地面展示鐵道、移動小列車、月台、廣場與庭院。整合V9時須逐項排除重複幾何與碰撞，保留文化牆、願景互動和原玩法。
4. 既有安心生養模組分離地面、牆柱、頭頂與相機代理，可沿用該系統的介面；不能把所有可見mesh一律當地面或相機障礙。
5. PR14碰撞JSON只是離線候選，不能直接當作已驗證的遊戲碰撞；上下層需真正測試。未開放的樓梯／電梯應有可理解限制。

## 必須完成後才可交付

- 交通島地基／四入口S09、S10、S15、S18接合，苑字中心線不動，安心生養建築不動。
- 原出生點、五風鈴、文化牆、政策、跳躍與滑翔相容。
- 實際角色地面、牆柱、護欄、頭頂／攝影機避障；不可只以GLB載入成功宣稱完成。
- 原出生點、安心生養橋口及全景的真遊戲截圖與前後比較；桌機／手機操作、載入與FPS。
- SwiftShader只列軟體GPU結果，真GPU／手機待實測，不冒充硬體效能。
- 完成後獨立Draft PR及可操作Preview；不合併、不更新Production、不施工22橋綠植／裝飾／7字形路燈。

## 目前阻礙與恢復方式

命令工具回報`exec-server transport disconnected`，後續`No usable execution environment is available`；已附執行環境狀態為unavailable。狀態服務雖回報running，不能當作命令環境可用。沒有可執行瀏覽器或讀寫本機的途徑，故尚未進行runtime程式修改、實際碰撞、建置或Preview。

恢復後先讀取所有工作目錄git status並保留未提交成果，再從本分支建立獨立worktree；不得reset／覆蓋舊PR14製作目錄、安心生養或使用者的五張未提交預覽圖。

此檢查點未改src、public、苑字路網或任何模型；未改Cloudflare設定、正式部署、合併PR或重寫Git歷史。提交使用[CF-Pages-Skip]。
