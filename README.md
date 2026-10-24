# 苑裡政策島（第一版）

以 MIT 授權的 Sky Isles 為基礎，保留 Three.js 島嶼、動畫、第三人稱移動、雙重跳躍、滑翔、鏡頭拖曳與手機搖桿。

八座政策島：交通大升級、安心生養、幸福養老、產業青年、宜居環境、智慧公所、治水防災、教育發展。點選浮動名稱、島嶼地面或右上角政策選單可開啟介紹。保留風鈴互動，第一版不啟用額外獎勵島。

## 修改政策

編輯 `public/data/policies.json`，不必修改 JavaScript。八筆資料的 `id` 對應場景，請保持不變；`name` 是顯示名稱，`introduction` 是純文字介紹（尚未提供時為 `null`），`items` 是純文字條列陣列（尚未提供時為 `[]`）。所有內容都以純文字顯示。此版未填入任何未提供的政策說明。

```json
{
  "id": "home",
  "name": "交通大升級",
  "introduction": null,
  "items": []
}
```

開發時修改 JSON 後重新整理即可；交付靜態版本請重新執行 `npm run build`。也可直接修改建置目錄的 `data/policies.json`，重新整理後生效。

## 執行與驗證

- `npm ci`：安裝依賴。
- `npm run dev`：啟動本機預覽。
- `npm test`：執行移動、謎題與亂數單元測試。
- `npm run test:e2e`：桌面與手機瀏覽器測試（需 Playwright Chromium）。
- `npm run build`：產生 `dist/` 靜態網站。

鍵盤 WASD／方向鍵移動，空白鍵跳躍，按住空白鍵滑翔；拖曳旋轉鏡頭、滾輪縮放。手機使用左下搖桿、右下跳躍鍵與手指拖曳。政策視窗可按關閉或 Escape 離開。

此版為抽象浮島場景，不代表苑裡真實地理位置，未製作額外建築模型，未進行正式部署。

## 開源授權

原作 Sky Isles：Copyright (c) 2026 Stanislav Sorokin (Bles Software)。原始碼：https://github.com/stas4000/sky-isles 。完整 MIT 授權保留在 `LICENSE`、`public/LICENSE`，並在入口頁提供連結。Three.js、Vite 等第三方依賴授權另見 `THIRD_PARTY_NOTICES.txt`。
