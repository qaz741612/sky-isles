# 道路景觀施工恢復紀錄

工作目錄 `/workspace/sky-isles-yuan-landscape`，分支 `codex/yuan-bridges-landscape-v1`。基底 ae13305。

- ea5cd7e：安心生養與 T3 西移，桌機／手機 22 段雙向通過；原 GLB 沒改。
- cce7615：六島資料預留，沒有建立建築或 NPC。
- 9913de7、ed22913、7a10c23、70860c0、a897124：五區逐次施工保存；a897124 的全部 22 段及五側台已使用真實 Player 驗證。
- 本次後續精修已合批共用金屬／植栽，並增加 S20/S22 收筆端的連續花帶及低位燈線；單元、lint、build 通過，最終瀏覽器回歸與 final/ 截圖仍在執行。

唯一配置來源：yuan-plan.json（已套用西移，不可再平移一次）、bridge-landscape-plan.json（五區、人工選定燈位與側台）、future-island-reservations.json（資料而已）。執行 npm run generate:yuan 時以 --report-dir 指向本目錄，勿把衍生 JSON 各自手改。

造景原始多邊形在建置時聯集。道路 4.8 核心未刪減，橋緣擴展在外側，護欄只依整體外邊界生成。側台入口已扣除花帶，不可恢復成橫跨入口的完整花台。S12/S17 為島內步道，S09 只有低位照明。36 處燈位中 34 為高燈，2 為低燈；兩個預選位置因幾何餘裕省略。

本機固定 build 服務 4200；map baseline worktree ea5cd7e 在 4201。請先 git status，保留所有新檔和 work/，不要 reset、clean 或 force push。若新環境遺失，從本分支最新提交恢復；不要從 PR13/14 完整歷史重建。

檢查最終 work/final-browser.log 與 work/final-capture.log 是否完成後，才更新最終報告。軟體 GPU 是 SwiftShader，不得當真機流暢度。標記 custom QA 的圖片不可當預設玩家視角。

沒有合併、Production 部署、Cloudflare 設定修改或六島精細模型。本輪完成後停止。
