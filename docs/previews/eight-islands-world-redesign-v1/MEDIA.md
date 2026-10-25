# 媒體與來源核對

- 最終原生 PNG：89 張（包含 20 張 V4 正常探索／全景、52 張新版探索／建築／全景、16 張固定同光學位置對照、1 張原始實景縮圖總覽）。
- 正常操作 MP4：1280×800，1935.72 秒（32 分 15.72 秒），64,531,811 bytes；原生鍵鼠，自然時間，未傳送、未加速模擬。
- 全部 90 份媒體合計 106,875,126 bytes；逐檔尺寸、大小及 SHA256 位於 [media-manifest.json](media-manifest.json)，可在本目錄執行 `sha256sum -c SHA256SUMS` 核對。
- 最終網站編譯檔：`dist/assets/index-BJC2BLzt.js`，SHA256 `fe201b9c6167eb9d1812aaa20b68d6eeb1e7968b4fe3338a42d8d3e158184343`。
- 原始碼提交：`ecb92f4caa60a77ddcd478c38fb9fe4bd598fb4c`；最終場景程式／資料與建置核對記錄在 [build-record.json](build-record.json)。

影片由完整 WebM 轉為 H264／YUV420 MP4，原始與輸出時長差小於 0.1 秒，未剪接或改變時基；[video-metadata.json](video-metadata.json) 保存兩者時長及原始 WebM 雜湊。原始較大的 WebM 與失敗錄影嘗試保留在 `work/`，不提交 GitHub。

[operation-log.json](operation-log.json) 包含正常鍵鼠路線、八島政策開啟、原風鈴互動、全景返回、最終零意外復位與使用的編譯檔。這不是實機流暢度或真人手持影片；軟體 WebGL 環境使原生操作影片較長，未加速。

QA 特製相機、固定光學位置對照及正常探索鏡頭均分別標記。所有原圖來自真正 Three.js 運行場景；縮圖總覽只排列原始截圖，未使用 AI 概念圖。

**GitHub 上傳後下載核對已完成：90／90 大小與 SHA256 全部相符**，包含完整 MP4；[逐檔結果](github-media-verification.json)。已直接讀取遠端檔案位元組，不以 HTTP 成功代替核對。核對的媒體提交為 `9e460a8685a4f1e2e0e618ef8480524a128c0726`。
