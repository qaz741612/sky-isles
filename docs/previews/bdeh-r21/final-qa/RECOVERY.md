## 最新恢復：E新增植栽已再修正，最終同源重渲染中

來源為本輪正式E Blender/GLB，移除第一批新增尖葉外觀，換成鈍圓寬葉、低花叢及連續底層，根部對齊原植生槽。主建築、土地方向、所有實體碰撞和37保護檔案不變。新模型E38,860三角面。check-final25.log為89單元/lint/build通過；候選24完整回歸為中止的中間證據，不能計最終通過。E最終8張64sample渲染正在重輸出，未齊前不宣稱來源一致。已保存舊候選8b04603及iteration-3比較證據。

繼續時先讀目前git status，勿reset/clean；Blender可用render_bdeh_r21.py --code E --output docs/previews/bdeh-r21/final-qa --resume接續（先核對record的sourceBlendSHA256）。最後E兩張details也需重輸出，B/D/H無需重建。新凍結測試端口4297、work/r21-final-candidate25-dist；完整70項回歸、最終擷取／效能／搖桿回放及GitHub雜湊尚待完成。

## 2026-11-07 續作檢查點：鏡頭連續性仍在複驗

四份正式 Blender／GLB、32張同源主視／六視圖及5張補充近景仍存在。正在修正 D 島沿路行走穿越樹冠投影時的突然縮鏡；補上整段可達預測路徑的視線採樣，而非只看預測終點。已確認候選17實際HTTP bundle SHA，沒有用舊伺服器誤判。新增透明玻璃的鏡頭視線分類，原玩家玻璃碰撞不變；樹冠僅作鏡頭殼，不新增draw calls。**最終70項回歸、新版59張遊戲圖、效能與下載雜湊仍待完成，不能視為封版。**

# PR19 R21 最終精修恢復點

基準39f41940fd3af0f432b477ebd36ad5b677a71db1。已先核對Review5800199311及FINAL-QA-FIX-SCOPE。所有原樣37個F/A/C/G／世界檔案鎖定，完整現行四島.blend／GLB／碰撞備份在docs/design/bdeh-r21/final-qa-baseline，沒有reset/clean或刪除其他工作樹成果。

目前施工：局部idle discovery相機，移動不自動轉向、手動orbit/zoom取消自動，F/A/C/G採原constraint/profile。B兩組伴坐座椅與香草床腳部空間；E連續木緣植生槽、葉叢群落、將淺水花園移至論壇側庭及重設觀水座椅；D服務入口識別、H閱讀論壇小型書頁導引。沒有重建主建築、擴島、改22路線或新增NPC／橋景／路燈。

新的重建程序先執行Blender scripts/blender/polish_bdeh_final.py，從已核准的最終39f Blender基底做增量編輯；再以scripts/bdeh/final_collision.py同步語義碰撞。禁止重新跑舊R18/R20研究來源或舊stage1重建覆蓋精修。渲染請指定--output docs/previews/bdeh-r21/final-qa，避免混用歷史圖片。

這是WIP，不能宣稱完成。已保留第一輪視覺研究、第一輪83單元82過1相機測試失敗（新look target使舊夾具取錯body位置）、修正相機夾具後發現的真正E回程座椅阻擋。座椅已再調整並重驗，不以修改路徑規避。相機候選仍需玩家畫面與連續進島路徑複驗；最終全套check／瀏覽器／新32渲染／對照／效能與GitHub下載驗證尚未全部完成。

預覽服務：4274是舊版凍結build，4276/4277僅相機研究，不得冒稱最終。待後續正式freeze新build並記錄真正來源SHA。work/node_modules及pycache是未提交暫存，不能丟棄有用模型或來源。

目前第一輪npm run check已87/87＋lint/build通過。第一輪相機視覺仍發現D構圖與E近距離問題，已保留研究並修正候選；E座椅回程阻擋已實際修正，7項R21幾何／行走／相機單元重驗全過。E水景旁樹冠在主視遮水，已將原樹成組移到乾地西岸；H書籍導引補真實斜台支承，未修改主體。最新源資產仍需重新完成87完整check與最終視覺／連續UI路徑回歸。


2026-11-07 第二保存點：正式源模型已凍結於candidate5（本機4280）；E原樹最終位置(-0.2,-4.6)，並非前述研究岸線位置。87單元、lint、build已重新通過。32張同源Blender／前後118張遊戲PNG及48對原生輸入比對完整；來源與37LOCKS核對通過。所有PNG可解碼。完整70瀏覽器正單獨執行，不能提前聲稱全過；其後排程效能與單指UI連續路徑採樣。所有新畫面在final-qa，歷史根目錄圖不是本輪新版。

第三保存點：四島同源32圖、真實前後118圖與19張聯絡／比較板已保存到ec10c81。完整70瀏覽器首輪桌機35項為30pass、4原有touch限定skip、1全景異步取樣fail；事件觀察式fixture已修正，桌機／手機指定重測排在完整手機回歸之後；此時不可宣稱全套通過。B伴坐點增加往返巡迴後，最新87單元、lint、build再次通過，編譯bundle與candidate5完全相同。下一步為完成剩餘手機、全景指定重測、效能及單指UI回放採樣，最後彙整manifest並從GitHub回下載驗證。

第四保存點：完整candidate5回歸為64pass/4觸控桌機skip/2同類全景取樣fail，事件式桌機與手機指定重測已2/2pass。追加真實D立面長按頂牆測試發現速度被guard歸零時會誤啟動idle轉向（held-wall-before-fix.json）；現已同時讀取Player既有_wish移動意圖，未改Player或任何F/A/C/G檔案。新增單元後88/88、lint、build通過。新凍結candidate6服務4281，正在重拍game-after59張，舊candidate5畫面已由Git ec10c81保留，且本機work/r21-final-qa/game-after-candidate5有原檔。其後完整70項重新從candidate6執行，不靠挑選舊通過。排程後續效能、單指搖桿／手勢採樣及5張同源近景。此時仍未宣稱最終完成。

最新施工保存（仍待最後遊戲複驗）：修正了後插值再次使用stateful endpoint造成的轉向短跳，採按dt縮放的球面跟隨、可見性回退及逐步縮近繞障；同時驗證真實旋轉幅度，避免凍結相機。原Player._wish會被重用為頭部暫存，不能當輸入；改由main的原始update入口將input傳給局部相機setInput，Player.js仍逐位元不變。D長按牆面probe改到正式外側x=-2.0,z=-6（早期-3.1在基座內，不再使用）。新增由同源Blender只讀輸出的48塊樹冠共3840三角形，僅在四島局部鏡頭中檢查，不加入全域／玩家碰撞，不繪製，避免E前景葉冠遮掉角色。89單元、lint、build通過；最新candidate13服務4286，正在跑真實不透明GLB視線、單指時序與橋口到NPC兩平台preflight。未確認最後手機圖、70全套、效能與下載驗證前不得宣稱完工。
