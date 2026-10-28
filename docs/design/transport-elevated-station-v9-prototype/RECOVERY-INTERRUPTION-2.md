# 第二次執行環境中斷：已保存成果與待完成項目

狀態：**尚未完成最終交付，PR #14 維持 Draft**。本檔不是美術或遊戲整合通過證明。

## 已推送的可恢復版本

- 程式恢復點：`0b02820658e5c9ccf4821c58dfe2c2547e93d756`。
- 原檔與兩 GLB／接縫修正：`ca94f48bccdc89a00e5a0688479214d6114915d6`。
- 最終凍結 BLEND SHA256：`5d99e81f8255f815e60ab0d63615ce024e96533c6757821beb74eb777c7eade6`。
- 展示 GLB：516,324 三角面，40,649,088 bytes，91 primitives；SHA256 `32d021a0df38853012f752d0b1d1e3ff52d6dff2d0b4abfd90f8127f05c52980`。
- 候選 GLB：201,740 三角面，17,633,080 bytes，49 primitives；SHA256 `d9292bf4e7b6c667e75f5e3d668ff5fb52eca2677a7c2cb080a95193b31878ac`。

中斷後已透過 GitHub 重新讀取 gltf-summary／source-audit／open-platform-audit／open-platform-revision JSON，確認 ca94f48 已保存上述版本。這不是重新下載二進位檔案的 SHA 核對；最終下載驗證仍待完成。

## 已實作與驗證

直接開啟 PR14 原 BLEND，移除上層長棚241物件；地面站房屋頂、天窗、木格柵、招牌保留，841個保留構件幾何／變換／材質指派指紋一致。列車原尺寸剛性迴轉180°，小亭僅在樓梯出口，補月台欄杆／資訊／照明。兩前花圃與座椅重排，座椅越出台地0。

修正原工程共面黑塊：TopAccessBridge與LiftLandingBridge抬0.003，StairTopLanding抬0.006；導盲線交叉改為實體聯集。沒有改苑字中心線或安心生養模型。

8,451網格重新開啟封閉／正體積通過；兩NPC區淨空、四口、地面15採樣點與3條上層平面通行帶離線檢查通過；兩GLB Khronos零錯誤零警告。這些不是遊戲膠囊、踏階或真手機驗收。

原PR14工作目錄已執行 npm run check，實際 Node v24.19.0 回報12個測試檔、0失敗，lint／build成功；本輪不沿用舊50項計數，也不把既有遊戲測試作新模型整合證明。最新完整log在本機 work/open-platform-pr14-game-check.log，尚未完成最終報告上傳。

## 尚未完成

- 接縫修正後整套同源11圖與舊模型同機位對照；中斷前只有部分圖完成，不能混用前一版本圖。
- 手機／桌機預設前後並排圖、最終圖庫自審。
- 新GLB實際瀏覽器載入與無Cycles競爭下的軟體WebGL量測；舊 webgl-report.json 不是本輪結果。
- 最終README／媒體manifest／GitHub逐檔下載驗證。
- 真遊戲碰撞與實機FPS原本即不在本輪完成範圍，仍待整合。

手機比較固定原出生(0,.5,3.5)加目標高度1.5；dist22／pitch.67／yaw.12／vFOV58，720×1280輸出對應360×640 CSS、DPR2。這是出生靜態相機模擬，不是假裝已跑遊戲避障；車頭及入口入鏡，右端車尾仍有裁切。不得用zoom28補充圖取代預設圖。

## 診斷與恢復位置

第二次工具實際錯誤：
`exec-server transport disconnected; failed to resume exec-server session: recovery timed out after 25s`，
隨後 `No usable execution environment is available`。

環境狀態工具仍回報connected／running，但命令工具無可用執行環境；沒有OOM／GPU故障證據，不能猜測原因。保留各工作目錄，不reset、不清除。

- 原PR14 worktree：`/workspace/sky-isles`。
- 獨立製作worktree：`/workspace/sky-isles-transport-open-v9`，本地恢復提交7250a4c、d6bae48，後續凍結來源5d99e81f已另推ca94f48。
- 渲染：獨立worktree的 work/open-platform-final-render.log、work/open-platform-pipeline.log；以render-record.json逐張SHA判斷可續用，不憑檔案存在判斷完成。
- 原PR14 worktree的五張使用者未提交苑字預覽圖，最近核對全部與原備份一致，不納入本輪。

本檔由GitHub連線直接保存；恢復後先fetch核對遠端新提交，再保留本地尚未提交工具／圖片，不可用reset硬覆蓋。PR base仍依附PR13，未改base或force-push；見BRANCH-ISOLATION.md。沒有合併、部署、變更Production或處理全地圖橋邊造景。
