# PR19 R21 最終精修恢復點

基準39f41940fd3af0f432b477ebd36ad5b677a71db1。已先核對Review5800199311及FINAL-QA-FIX-SCOPE。所有原樣37個F/A/C/G／世界檔案鎖定，完整現行四島.blend／GLB／碰撞備份在docs/design/bdeh-r21/final-qa-baseline，沒有reset/clean或刪除其他工作樹成果。

目前施工：局部idle discovery相機，移動不自動轉向、手動orbit/zoom取消自動，F/A/C/G採原constraint/profile。B兩組伴坐座椅與香草床腳部空間；E連續木緣植生槽、葉叢群落、將淺水花園移至論壇側庭及重設觀水座椅；D服務入口識別、H閱讀論壇小型書頁導引。沒有重建主建築、擴島、改22路線或新增NPC／橋景／路燈。

新的重建程序先執行Blender scripts/blender/polish_bdeh_final.py，從已核准的最終39f Blender基底做增量編輯；再以scripts/bdeh/final_collision.py同步語義碰撞。禁止重新跑舊R18/R20研究來源或舊stage1重建覆蓋精修。渲染請指定--output docs/previews/bdeh-r21/final-qa，避免混用歷史圖片。

這是WIP，不能宣稱完成。已保留第一輪視覺研究、第一輪83單元82過1相機測試失敗（新look target使舊夾具取錯body位置）、修正相機夾具後發現的真正E回程座椅阻擋。座椅已再調整並重驗，不以修改路徑規避。相機候選仍需玩家畫面與連續進島路徑複驗；最終全套check／瀏覽器／新32渲染／對照／效能與GitHub下載驗證尚未全部完成。

預覽服務：4274是舊版凍結build，4276/4277僅相機研究，不得冒稱最終。待後續正式freeze新build並記錄真正來源SHA。work/node_modules及pycache是未提交暫存，不能丟棄有用模型或來源。

目前第一輪npm run check已87/87＋lint/build通過。第一輪相機視覺仍發現D構圖與E近距離問題，已保留研究並修正候選；E座椅回程阻擋已實際修正，7項R21幾何／行走／相機單元重驗全過。E水景旁樹冠在主視遮水，已將原樹成組移到乾地西岸；H書籍導引補真實斜台支承，未修改主體。最新源資產仍需重新完成87完整check與最終視覺／連續UI路徑回歸。
