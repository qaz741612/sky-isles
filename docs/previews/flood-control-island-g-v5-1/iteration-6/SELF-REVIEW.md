# 真實手機近廊視角：修正G局部避障

本輪模型、12張Blender圖與GLB已定稿，不再改幾何。19張實際遊戲圖檢查發現，mobile-command-player的角色下半部被前景屋檐遮住；原G避障只驗物理頭/躯幹，未涵蓋較矮視覺角色完整輪廓。不能作合格最終玩家畫面。

只修改src/world/flood-control.js的floodCameraConstraint函式：增加低位/側向可見性探針及穩定偏角記憶，其他載入/建造程式前綴、通用相機/人物/main、F/A/C原樣。原意圖orbit/zoom不改，G外完全委派原約束。最新遊戲圖需以新執行版重出，Blender原檔/GLB/同機位模型對照不變。
