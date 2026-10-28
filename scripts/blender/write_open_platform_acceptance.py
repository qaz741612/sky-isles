"""Record verified delivery versus manual/runtime gaps, without editing models. MIT."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/design/transport-elevated-station-v9-prototype';load=lambda n:json.loads((OUT/n).read_text());m=load('model-report.json');r=load('render-record.json');web=load('webgl-report.json');gl=load('gltf-summary.json');game=load('existing-game-sanity.json');lock=load('asset-lock.json');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(OUT/f['file'])==f['sha256']for f in lock['files'])
assert len(r['views'])==11 and all(v['sourceBlendSHA256']==m['blendSHA256']and sha(OUT/v['file'])==v['imageSHA256']for v in r['views'])
assert web['allPassed']and all(v['loadedSHA256']==sha(OUT/('transport-station-v9-'+v['mode']+'.glb'))for v in web['results'])
report=f'''# 本輪驗收狀態

這次只完成ca94f48既有資產的渲染、比較、實際載入、報告與下載核對；**沒有重新建模**。所有三個模型的內容仍與ca94f48逐位元一致，見asset-lock.json。

| 項目 | 狀態 | 證據／限制 |
| --- | --- | --- |
| 同步遠端、保留未提交成果 | 已完成 | fast-forward到6d207cd，原五張使用者預覽圖未改、未納入提交；備份在work |
| BLEND／展示及候選GLB鎖定 | 已完成 | asset-lock.json；凍結來源{m['blendSHA256']} |
| 11張新版同源渲染 | 已完成 | render-record.json逐圖來源與PNG SHA；沒有混入舊來源 |
| 主視圖、正背左右、俯視 | 已輸出及製作端檢視 | 原始Cycles圖；低角度四向下緣可見棚拍平面界線，沒有裁切隱藏 |
| 拆棚前後4組同機位比較 | 已完成 | 手機、桌機、主45°、俯視；相機矩陣／鏡頭／尺寸逐項assert |
| 預設鏡頭可見性 | 部分通過，待人工接受 | 手機車頭及入口投影在框內，但小亭／欄杆遮車頭下緣，右端車尾及部分高架裁切；不是完整無遮蔽全島構圖 |
| GLB格式／材質 | 已完成 | 兩份Khronos均零錯誤零警告，33材質、1張內嵌原創木紋，外部貼圖0 |
| 真正Three.js WebGL載入 | 已完成 | 本輪4個桌機／手機尺寸案例，檔案SHA一致、貼圖解碼、缺材質0、GL error0 |
| 軟體GPU效能量測 | 已量測，未達流暢驗收 | SwiftShader／localhost／DPR1／單資產，見PERFORMANCE；不是實機FPS |
| 原有遊戲check | 已完成 | 當前工具回報{game['reportedTestFilesPassed']}個測試檔，0失敗、lint及build成功；不是新模型遊戲整合證明 |
| 四口／NPC／台地幾何 | 離線稽核通過 | 保留ca94f48幾何，最新唯讀檢查通過；無模型變動 |
| 遊戲膠囊／踏階／相機避障 | 未執行，待後續整合 | 模型尚未掛入正式世界，不能據離線幾何或舊遊戲check宣稱通過 |
| 真桌機GPU、iOS／Android、發熱 | 未執行 | 環境只有軟體GPU |
| 人工美術、手機構圖接受度 | 待使用者 | 尤其車頭下緣遮擋與尾端裁切；本輪禁止改模型，僅如實交付 |
| 最終GitHub下載核對 | 見github-verification.json與DELIVERY | 提交後由GitHub實際下載逐檔驗證，不用本地存在代替 |
| PR13基底隔離 | 未執行，依指示保留方案 | BRANCH-ISOLATION.md保持6d207cd原提案，未force-push或改base |
| 地圖／橋邊造景 | 未開始 | 留待下一階段，沒有改苑字或其他島 |

歷史RECOVERY文件描述先前中斷當時的未完成狀態；本輪最新狀態以上表及DELIVERY為準。
'''
(OUT/'ACCEPTANCE.md').write_text(report)
print('ACCEPTANCE_STATUS_WRITTEN')
