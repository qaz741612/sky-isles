# G 治水防災 V5｜人工驗收入口

本輪基於 Draft PR17 的 `cd4bacba72b6a1f7bf607c687566dc14f12c4896`；獨立 Draft PR18，分支 `codex/flood-control-island-g-v5`。不合併、不部署 Production、不施工新的橋景或路燈。美術與實機體驗仍待使用者驗收。

| 類型 | 可直接開啟的成果 |
|---|---|
| 真實遊戲 QA 45° | [G 島主視圖](game/g-hero.png) |
| 真實遊戲 QA 正上方 | [G 島俯視](game/g-top.png) |
| 玩家預設鏡頭 | [桌機](game/desktop-native.png)／[手機直式](game/mobile-native.png)／[手機橫式](game/mobile-landscape.png) |
| 玩家水岸觀察 | [桌機](game/desktop-waterfront-player.png)／[手機](game/mobile-waterfront-player.png)，原生相機距離與俯角，QA 模擬一次旋轉，並非預設朝向 |
| 橋口與公共空間 | [S21](game/s21-player.png)／[S22](game/s22-player.png)／[門廊](game/command-porch-player.png)／[NPC 停留區](game/npc-player.png) |
| 完整苑字 | [桌機無標籤全景](game/yuan-panorama.png)／[手機全景](game/mobile-panorama.png) |
| Blender 同源六視圖 | [六視圖總表](blender-six-views.png)／[原始十張圖與來源紀錄](blender/) |
| 建築／水工近景 | [指揮中心 Blender](blender/near-command.png)／[閘門 Blender](blender/near-dam.png)／[跨水橋 Blender](blender/s22-crossing.png)；[實際遊戲建築](game/command-detail.png)／[水閘](game/sluice-detail.png) |
| 比較與自查 | [PR17 舊 G→V5 同遊戲機位](game-before-after.png)／[第一輪→最終 Blender 同機位](self-review-comparison.png) |
| 空間稽核 | [最終工程平面（非遊戲圖）](spatial-plan-final.png)／[數值](spatial-audit-final.json) |
| 報告 | [設計、碰撞與限制](REPORT.md)／[測試摘要及逐案例來源](test-summary.json)／[效能前後比較](performance-comparison.json)／[重建方式](REBUILD.md) |
| 檔案完整性 | [檔案清單](FILE-LIST.md)／[尺寸、大小、SHA256](MANIFEST.json)／[GitHub 下載核對](GITHUB-VERIFIED.json) |

可編輯工程：[flood-control-g-v5.blend](../../design/flood-control-island-g-v5/flood-control-g-v5.blend)。
遊戲資產：[flood-control-g.glb](../../../public/models/flood-control-g/flood-control-g.glb)。Blender 與 GLB 採用相同構件來源，GLB 另依區域／材質合批。

所有 `game/` 是最終 Three.js 實際畫面；`blender/` 是同一凍結 Blender 工程的 Cycles 渲染。QA 特製鏡頭、預設玩家鏡頭、旋轉觀察分開標示。`source-package/` 是使用者設計參考；`iteration-*` 是歷史稽核，不能作為最終成果或通過證據。

原始預設鏡頭沒有為展示而拉遠。手機直式受原生視角範圍限制，中心朝向不能同時完整展示兩座主體，須旋轉觀察；完整美術辨識度、相機避障的連續手感、真手機效能均待人工確認。
