# G V5 最終恢復點

Draft PR18，分支codex/flood-control-island-g-v5，基底PR17 cd4bacba72b6a1f7bf607c687566dc14f12c4896。模型、生成資料、10張同源Blender圖、17張實際遊戲圖、3張舊版比較圖、測試及效能已存檔。

最終GLB SHA256：99030fd7b8c32d831926cf835914dc6b86496691cd2144bd53efd45144eb620e。Blender SHA：3653b9334f1e303083d477773799a67bfc9888f619387bd1d3c4a01bdada0a2a。主要配置為src/data/flood-control-plan.json，重建見REBUILD.md。

71單元與lint/build通過；增量Playwright有效60通過/4桌機不適用略過，所有原始失敗紀錄保留。最終兩尺寸22段各雙向及G公共動線逐幀有限值、檢查點/全景/強制跌落通過。初版NaN誤報已撤回，不可引用iteration-1為驗收通過。

F/A/C資產與模組、玩家程式、政策JSON、22條中心線及36燈位保護。無NPC、無橋景施工、無正式部署、不合併。美術、真機效能、完整人工周緣與長時間手感尚未驗收，詳REPORT.md。

work/、node_modules、.blend1、__pycache__為保留的本機暫存，不納入提交；不reset/clean。GitHub下載manifest收據另記錄釘選提交，最終分支可能多一筆收據提交，不改資產。
