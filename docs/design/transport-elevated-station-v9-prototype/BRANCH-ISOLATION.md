# PR #14 基底隔離方案（提案，尚未執行）

PR14仍為Draft，base為未核准PR13來源 `codex/seven-policy-islands-blender-assets-v1`。本輪只正常提交交通修改到既有head；沒有改base、force-push或合併。

只將base下拉選單換成較早分支，會把PR13七島資產一起列入差異，不能這樣直接處理。

1. 保存當時PR14最終head備份tag與BLEND／GLB／圖片／程式manifest，確認下載SHA一致；保留PR13原分支。
2. 從已明確核准的PR11美術來源 `codex/parent-child-blender-model-v1`／`ac433fd5d23f00d3aab9470d96349114e1a37b24` 建立暫存隔離分支。只取本輪 `docs/design/transport-elevated-station-v9-prototype/` 與交通專用離線工具，不cherry-pick整個PR13，不restore整個docs/design或scripts目錄。
3. 驗證ac433fd至隔離分支差異僅為交通原型／工具；src、public、政策、套件與安心生養檔案必須不變。已檢查通用parent_child_geometry工具在該基底存在且與PR14一致，不依賴七島hall模板。四口、NPC與鄰島以10.2半徑再驗。
4. PR12遊戲整合仍為Draft，不應默認其已獲整合核准。正式整合的最終基底需要明確確認；本次提出方案，不替使用者批准未核准版本。
5. 確認隔離差異後，可將PR14改接該乾淨歷史並retarget base。若沿用同一head，先備份遠端原SHA，再用附明確舊SHA的force-with-lease；若期間有新提交，必須拒絕覆蓋並重新閱讀。也可保留PR14美術紀錄、另開乾淨整合PR，由使用者決定。
6. 最後在GitHub核對Files changed不含seven-policy-islands資產，下載核對模型／圖片manifest，繼續保持Draft等待驗收。

本輪沒有執行上述重寫或新開無關PR。**目前PR14仍依附PR13；在隔離完成前，不應直接合入已核准分支。** 未修改main、Production、Cloudflare或已核准安心生養。

第二次執行環境中斷時，已保存交通模型提交為ca94f48；詳見RECOVERY-INTERRUPTION-2.md。不得因整理基底而丟失該提交或本地尚未完成的圖片。
