## 最終可恢復成果：移樹後完整自動複驗與畫面檢查完成

93單元/lint/build；同一4305凍結版本完整70為66通過／4原裝置條件跳過，0失敗／中斷／重試。32+5同源Blender渲染、前後118遊戲圖／48對同條件原生輸入、37保護檔無差異；四島真正CDP搖桿回放均完成。相同最終資產H原生／索引查詢隔離實驗218.933→15.499秒，非硬體FPS。最終圖片已實際看過，D近牆縮鏡、H NPC近景屋頂裁切及真機／人工美術未批准等限制見REPORT。

正式遊戲snapshot work/r21-final-visible-dist（4305），4306是僅供CPU比較的原生查詢別名版本，不能作遊戲交付；原始before仍為4275。最終結果以REPORT、source-consistency、MANIFEST及GitHub下載收據GITHUB-VERIFIED為準。若收據尚不存在，先完成資產提交／推送及逐檔下載SHA核對，再用僅收據的後續提交保存；不要宣稱已完成網路驗證。維持Draft PR19，不合併／部署／開始後續工程。

## 最終模型與32+5渲染已同步；新完整70正在執行

E原生、左右單指及NPC圖已看過，角色完整可見；相機預設完整恢復原設定。移樹後4關鍵案例通過，93單元/lint/build及4島單指時序通過；B真實CDP搖桿連續路線完成。E新8+2的source SHA均核對，所有32+5渲染對應目前.blend。完整70進度work/r21-final-qa/final-visible-progress.ndjson；完成後同一shell會跑final-r21-pipeline.py 4305 work/r21-final-visible-dist final-visible。該pipeline接著序列量測4306原生backend／4305索引backend的相同H稽核、59張新圖、整世界效能與4島單指回放，最後來源與19比較板。不要把前一版66/4當本次最終驗證；source-consistency暫明確pending，舊資料在iteration-5。新報告產生器會拒絕GLB／bundle不相符的舊結果。完成後還需親自看最終原生圖、產生REPORT／manifest、push、逐檔GitHub下載驗SHA、收據專用後續提交並更新Draft PR19。不得合併／部署。

## 最新施工檢查點：E樹冠遮擋實體修正，尚在複驗

完整66/4先前通過後，看最終圖仍抓出E直式樹冠遮身。追加真正GLB的0.35/0.5m身體射線，舊版確實失敗；iteration-5保存證據。兩個改yaw候選犧牲構圖均未採用，已恢復完全相同相機設定。只將E既有樹從(-0.2,-4.6)側移至(-3.4,-4.6)，保留建築、島面、道路、距離和FOV；碰撞／鏡頭殼同步重生，93單元/lint/build通過。最新遊戲4305/work/r21-final-visible-dist，原生backend對照4306/work/r21-final-visible-dist-native。E8+2同源64sample渲染與加強後4關鍵案例進行中；必須重跑最終70、擷取與效能後才交付。前次66/4及CPU時序不是本次移樹後全套驗證。

## 2026-11-08 最終凍結版：完整70案例已複驗

同一4302凍結build的一次完整Playwright：66通過、4原裝置條件跳過、0失敗／中斷／重試；未拼接舊版案例。93單元、lint、build通過。原始完整結果與失敗歷史見regression。四島32+5最終Blender視圖及GLB源保持677208f；H相同4132ticks CPU稽核224.577→15.875秒，不能當FPS。最終59張遊戲圖、效能及單指操作擷取仍在序列執行，完成後必須做來源核對與畫面檢視；尚不宣稱全輪交付完畢。

## 最新可恢復程式：局部靜態三角索引，93單元通過

保留9001863的完整六探針／未來路徑／角速與位移約束，沒有放寬腳部或變更玩家物理。只將R21不透明殼與樹冠查詢改為靜態世界座標三角網格，含射線格內高度剔除。1,119條原生Three對照射線一致；npm run check93單元/lint/build通過。規則字串等價證據camera-rule-equivalence.json；原global camera-clearance.js與F/A/C/G模型、土地不改。

完整32+5最終Blender視圖與模型仍為677208f。frozen spatial端口4302/work/r21-final-spatial-dist。先前有限搜尋試驗未改善H成本（198.9秒），已保留iteration-4並不採用；第一版XZ索引同H稽核20.7秒。新版含高度剔除正以同一路徑做前後CPU比較、接續單指操作與4個關鍵瀏覽器重測，再跑最終完整70及截圖／效能pipeline。不把舊64/4/2或逾時列為完成。

## 目前修正檢查點：候選26，90單元與E桌機到達測試通過

E新增desktopFallbackYaw=-1.8（直式維持-3），不改dist/FOV或世界比例。修正final25桌機雨水花園出框。另對靜態鏡頭殼、完全相同的head/yaw/pitch/range/forecast/group-matrix輸入重用純端點搜尋，逐幀實際視線及插值仍照做；手動旋轉／縮放有新增真實位置斷言，90單元/lint/build已通過。world-spaces未放寬420秒限制，新增每島進度檔，候選26桌機目前已到第8島；手機仍待本輪重測。

frozen26端口4298，work/r21-final-candidate26-dist。關鍵4案例報告work/r21-final-qa/playwright-final26-critical.json及final26-critical-progress.ndjson；所有模型與32+5Blender來源仍為677208f，不重建。後續完成受影響26案例的分批重跑、最終59張遊戲畫面、性能及單指回放。完整final25的64/4/2保留，不能宣稱最終70項單次全過。

## 2026-11-08 環境恢復：本機成果仍存在，完整回歸2項未通過

目前分支codex/bdeh-r21-game-integration，模型／32張同源視圖／5近景已在677208f。命令列曾短暫不可用，新工作區資訊後成功恢復；未reset/clean。完整final25結果64通過、4依裝置跳過、2未通過：E桌機雨水花園NDC y=-1.2686超出初始畫面；mobile world-spaces420秒逾時。原始報告、progress、check紀錄與摘要見recovery-20261108/。尚未開始最後59張遊戲圖與效能／操作回放。不要把候選6／23的game-after當新版E最終成果。

原本未提交的效能工具與可攜重建依賴已取回並另存WIP；git完整binary差異備份在work/r21-final-qa/recovery-20261108-uncommitted.patch（暫存不提交）。接續只修兩項已證實問題，保留F/A/C/G及原路網。

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
