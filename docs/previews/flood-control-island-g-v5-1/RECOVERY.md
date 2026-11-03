# G V5.1 最後交付工程／驗證中

同Draft PR18分支，V5基底8849b89。已保留五輪實際圖/模型/稽核，包含不合格項目，不混作最終圖。最新來源完成墩腳/水道淨寬、解說牌及長椅的實體連接，模型74463三角面/60批次。GLB來源是原V5 .blend，2073個原物件保留，不重造島台/路網/F/A/C。

最終服務4264（work/g-v51-delivery-dist）；4261是全64初次回歸的73655版，4263是壓低基礎後74207版。最終76單元、22路及G相關瀏覽器/首畫面/落水再於4264驗證；不要把中間版案例當單次最終全跑。最新Blender唯讀12張及實際遊戲19張須在根目錄blender/game，iteration-*全為歷史。

FINAL-LOCK記錄最後模型與原始工程SHA，重建需prepare_v51.py→build_flood_v51.py→render_saved_flood_v51.py→audit_v51.py；不執行--site。水位與乾地三角面完全不變，排除負高度支承面避免落水後站在水下構件；已新增實際GLB剖面2.11m與九點復位測試。

214個V5源/模型/歷史交付檔保護，原F/A/C與通用操作/相機/UI不改。work/node_modules/.blend1保存於本地不提交。不reset/clean、不合併/Production部署、不開始橋景或其他島。仍需完成最後圖/報告/效能/manifest及GitHub下載核對才交付。
