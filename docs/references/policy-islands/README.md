# 八座政策島設計參考圖

**八張已全部存檔並完成讀取驗證（8 / 8）。** 本階段只整理參考，不建模、不修改遊戲場景，已進入使用者另行授權的七島資產建模階段。

七張新政策島原圖來自使用者提供的 `7島圖.zip`；安心生養沿用與聊天基準圖視覺一致的專案既有核准 PNG。所有存入本目錄的圖片均保留來源檔案原始位元組，未壓縮、裁切或重繪。

[機器可讀索引](manifest.json) · [完整驗證結果](verification.json) · [SHA256 清單](SHA256SUMS)

## 專案檔案路徑

後續建模直接讀取下表檔案，或使用 `manifest.json` 的 `projectPath`；不將整批圖像或 base64 輸出到對話。

| 政策島 | 檔案（目錄：docs/references/policy-islands/） | 尺寸 | 用途 | 驗證 |
| --- | --- | --- | --- | --- |
| 交通大升級 | [transport-reference.png](transport-reference.png) | 1448×1086 PNG | 後續建模參考 | 通過 |
| 安心生養 | [family-reference.png](family-reference.png) | 1600×1096 PNG | 已核准美術基準 | 通過 |
| 幸福養老 | [senior-reference.png](senior-reference.png) | 1448×1086 PNG | 後續建模參考 | 通過 |
| 產業青年 | [industry-reference.png](industry-reference.png) | 1448×1086 PNG | 後續建模參考 | 通過 |
| 宜居環境 | [environment-reference.png](environment-reference.png) | 1448×1086 PNG | 後續建模參考 | 通過 |
| 智慧公所 | [digital-reference.png](digital-reference.png) | 1448×1086 PNG | 後續建模參考 | 通過 |
| 治水防災 | [water-reference.png](water-reference.png) | 1448×1086 PNG | 後續建模參考 | 通過 |
| 教育發展 | [education-reference.png](education-reference.png) | 1448×1086 PNG | 後續建模參考 | 通過 |

七張新圖均包含 45° 主視角及正面、背面、左側、右側、俯視的多角度版面。圖片「教育」對應政策島「教育發展」，只作檔案索引，不改正式政策名稱或文字。

## 來源與確認方式

- ZIP 來源：`7島圖.zip`，14,098,052 bytes，CRC 全部通過。
- ZIP SHA256：`70d1441143e064ebc97e62519ba050b07bc668f858317af82dde4d7f1500c8d4`。
- 依原圖標題核對：ZIP 尾碼 1=交通、2=宜居、3=產業、4=養老、5=智慧、6=治水、7=教育；沒有按聊天傳送次序猜測。
- 每張保存檔都經 Pillow `verify()`、重新開啟後完整像素 `load()`、檔案大小及 SHA256 比對；8 個圖片雜湊皆不同，沒有漏圖或錯存重複圖。
- 七張新圖的原 ZIP 檔名、來源路徑與 CRC 記錄於 manifest；存檔與 ZIP 成員逐位元組相同。
- 安心生養原核准來源：`docs/design/parent-child-blender-refinement-v2/renders/hero.png`。本目錄副本與該來源位元組相同；沒有聲稱能對不可取得的聊天預覽原始位元組作比對。
- 安心生養：1600×1096 PNG、2,297,672 bytes，SHA256 `085f73ea9870ec5fd7b2c3cd663ec8a025c8fe9a1770b690e517aeb84c42d758`。

僅供內部核對的縮小標題索引留在 `work/policy-reference-intake/`，不作為建模來源、不取代原圖，也不列入此目錄的八張原始參考。

## 後續界線

收件與檔案驗證已齊全。`readyForModellingInstructions=true` 只表示已可接收正式建模指令；`modellingAuthorised=true`：使用者已提供正式七島 Blender 建模指令。僅製作獨立資產，不修改安心生養、遊戲場景或苑字路網。圖片中的描述僅作設計參考，不新增政策內容或施工核定資訊。
