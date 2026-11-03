# G 治水防災 V5.1｜驗收入口

延續 Draft PR18，基準 `8849b89`。保留原V5歷史與可編輯工程，精修三孔水工、指揮中心與四個功能景觀區，沒有重做島台、苑字路網或F/A/C。主觀美術與真機體驗仍待人工驗收；自查、實際遊戲與自動化結果分開列於報告。

| 成果 | GitHub 可直接查看 |
|---|---|
| 實際 Three.js QA主視圖 | [主視圖](game/g-hero.png)／[俯視](game/g-top.png) |
| 原生桌機相機 | [預設方向](game/desktop-native.png)／[水岸旋轉觀察](game/desktop-waterfront-player.png)／[入口旋轉觀察](game/desktop-command-player.png) |
| 原生手機相機 | [直式預設](game/mobile-native.png)／[橫式](game/mobile-landscape.png)／[水岸](game/mobile-waterfront-player.png)／[指揮中心](game/mobile-command-player.png) |
| 公共動線 | [S21](game/s21-player.png)／[S22](game/s22-player.png)／[門廊](game/command-porch-player.png)／[NPC預留](game/npc-player.png) |
| 完整苑字 | [桌機無標籤](game/yuan-panorama.png)／[手機直式](game/mobile-panorama.png) |
| 最終 Blender 同源六視圖 | [六視圖總表](six-views.png)／[12張原圖與來源SHA](blender/) |
| 水工／建築細節 | [閘門](blender/near-dam.png)／[下游出流](blender/downstream-detail.png)／[指揮中心](blender/near-command.png)／[觀測塔](blender/tower-detail.png) |
| 同機位比較 | [水工與建築](comparison-blender.png)／[實際遊戲](comparison-game.png)／[手機](comparison-mobile.png)／[G低位避障修正](comparison-camera.png) |
| 自主挑刺 | [第一輪](iteration-1/SELF-REVIEW.md)／[第二輪](iteration-2/SELF-REVIEW.md)／[後續結構稽核](SELF-REVIEW-FINAL.md) |
| 驗證 | [完整報告](REPORT.md)／[測試與版本來源](test-summary.json)／[效能比較](performance-comparison.json)／[實際GLB水工剖面](hydraulic-geometry-comparison.json)／[空間及保護稽核](spatial-audit-final.json) |
| 維護與完整性 | [重建](REBUILD.md)／[修改清單](FILE-LIST.md)／[尺寸、大小與SHA256](MANIFEST.json)／[GitHub下載核對](GITHUB-VERIFIED.json) |

模型：[可編輯 Blender](../../design/flood-control-island-g-v5-1/flood-control-g-v5-1.blend)／[正式遊戲 GLB](../../../public/models/flood-control-g/flood-control-g.glb)／[集中藝術配置](../../../src/data/flood-control-art.json)。

`game/` 均為最終Three.js實際場景；`blender/` 為同一份最後原檔的Cycles渲染。QA特製鏡頭與原生玩家鏡頭分列；「旋轉觀察」只模擬使用者旋轉，不改原生距離、俯角或FOV。手機狹長畫面須轉動視角觀看不同主體，不把拉遠特寫冒充預設畫面。

`before/` 是原V5，`iteration-*` 是歷史施工自查，不能當最後版本。原V5完整入口仍保留於[舊報告](../flood-control-island-g-v5/README.md)。C V3風格對照使用[已認可真實模型圖](../industry-youth-island-c-v3/blender/hero.png)，不以面數宣稱品質更高。

沒有合併、正式部署或修改Cloudflare設定；本輪止於G V5.1，等待整體人工驗收。
