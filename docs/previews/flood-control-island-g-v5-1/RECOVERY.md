# G V5.1 最終驗證進行中

PR18同分支codex/flood-control-island-g-v5。V5基底8849b89，完整基準原檔/資產/214檔保護留存。第一輪ebc4d32已推送，兩輪自查圖及SELF-REVIEW已保存；第二輪發現側牆和消能塊遮水，已在最新版模型修正。

目前模型73655三角面/60批次，從原V5 .blend保留2077個原可編輯物件，沒有重新製作島台、道路或F/A/C。water仍不作地面，NPC預留和22中心線不動。真實落差1.14、三道開度0.78、頂部離原梁0.05。

最終Blender12張圖正在從同一凍結原檔唯讀渲染；正式build、lint、75單元及4261原遊戲逐幀22路往返正在驗證，尚未交付通過聲明。4260為第二輪，4254為原V5比較版，4261為最終模型。不得混舊圖當新版。後續需完整Playwright、實際桌機/手機圖、效能前後比較、manifest下載核對。

流程prepare_v51.py→build_flood_v51.py（打開原V5 .blend並協調差異）→render_saved_flood_v51.py→audit_v51.py。不執行--site或重寫原V5檔案。原G5完整報告與圖片不變，新成果集中v5-1目錄。

work/node_modules/.blend1保留於本地，不提交；不reset/clean，不合併或Production部署，不施工橋景或其他島。
