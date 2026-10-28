"""Hash-gated open-platform delivery: actual source, renders and tests. MIT."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,hashlib,re,subprocess,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/design/transport-elevated-station-v9-prototype';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads((OUT/p).read_text());m=load('model-report.json');a=load('source-audit.json');s=load('geometry-space-audit.json');o=load('open-platform-audit.json');g=load('gltf-summary.json');web=load('webgl-report.json');r=load('render-record.json');b=load('before-render-record.json');revision=load('open-platform-revision.json');profile=load('camera-profile-audit.json');assert profile['allPassed'];source=sha(OUT/'transport-station-v9.blend');views=['hero','front','back','left','right','top','train-side','player-desktop','player-mobile','player-mobile-zoom28','player-mobile-arrival-overview'];records={v['view']:v for v in r['views']};before={v['view']:v for v in b['views']}
assert source==m['blendSHA256']==a['sourceBlendSHA256']==s['sourceBlendSHA256']==o['sourceBlendSHA256']==revision['finalSourceBlendSHA256']
assert a['allClosedPositiveVolume']and s['allOfflineChecksPassed']and o['groundStructuralSupportsAllInsideSite']and g['allPassed']and web['allPassed']
for name in views:
 rec=records[name];assert rec['sourceBlendSHA256']==source and sha(OUT/rec['file'])==rec['imageSHA256']
 with Image.open(OUT/rec['file'])as im:im.verify()
for name,rec in before.items():
 assert rec['sourceBlendSHA256']=='a975409e16bf406b4fe1ae9981d632c527f85244387e3a88111baad4177f2abb'and sha(OUT/rec['file'])==rec['imageSHA256'];now=records[name];assert rec['size']==now['size']
 for k in ['cameraPositionBlenderXYZ','cameraRotationRadians']:assert max(abs(x-y)for x,y in zip(rec[k],now[k]))<1e-6,(name,k)
 assert rec['projection']==now['projection']
 if name in ['hero','top']:assert abs(rec['orthoScale']-now['orthoScale'])<1e-6
 else:
  for k in ['distance','pitch','yaw','verticalFOV','lensMillimetres','sensorHeight']:assert abs(rec[k]-now[k])<1e-6,(name,k)
  assert rec['sensorFit']==now['sensorFit']and rec['targetWorldXYZ']==now['targetWorldXYZ']
for z in g['results']:assert z['sha256']==sha(OUT/('transport-station-v9-'+z['mode']+'.glb'))
for z in web['results']:assert z['loadedSHA256']==sha(OUT/('transport-station-v9-'+z['mode']+'.glb'))
fontpath='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';font=ImageFont.truetype(fontpath,28);small=ImageFont.truetype(fontpath,21)
# Exact pixel comparison: no fit/crop/zoom of either source image.
for name in ['hero','top','player-desktop','player-mobile']:
 left=Image.open(OUT/before[name]['file']).convert('RGB');right=Image.open(OUT/records[name]['file']).convert('RGB');assert left.size==right.size;w,h=left.size;canvas=Image.new('RGB',(w*2,h+110),'#f0eade');d=ImageDraw.Draw(canvas);canvas.paste(left,(0,60));canvas.paste(right,(w,60));d.text((18,12),'修改前｜PR #14 長頂棚',font=font,fill='#34575d');d.text((w+18,12),'修改後｜開放式月台（相同機位／尺寸）',font=font,fill='#34575d');footer='Blender Cycles 渲染，非遊戲整合截圖。手機預設右端車尾仍有裁切。'if name=='player-mobile'else'Blender Cycles 同機位實際渲染；沒有縮放模型、裁切或改變相機製造差異。';d.text((18,h+72),footer,font=small,fill='#34575d');canvas.save(OUT/('comparison-'+name+'.png'))
labels={'hero':'45° 主視角（西側車頭）','front':'正面','back':'背面','left':'左側','right':'右側','top':'正上方','train-side':'列車側面','player-desktop':'桌機預設模擬','player-mobile':'手機預設模擬（車尾裁切）','player-mobile-zoom28':'補充 zoom28，非預設','player-mobile-arrival-overview':'補充橋口站位，非預設'}
canvas=Image.new('RGB',(1600,1260),'#f0eade');d=ImageDraw.Draw(canvas)
for i,name in enumerate(views):
 with Image.open(OUT/records[name]['file'])as im:thumb=ImageOps.contain(im.convert('RGB'),(400,380))
 x=i%4*400;y=i//4*420;canvas.paste(thumb,(x+(400-thumb.width)//2,y+35));d.text((x+8,y+7),labels[name],font=small,fill='#34575d')
canvas.save(OUT/'render-index.png')
canvas=Image.new('RGB',(1920,790),'#f0eade');d=ImageDraw.Draw(canvas)
for i,(file,label)in enumerate([('inputs/approved-v9/美術參考_高架車站.png','原核准參考（長棚已由新指令取消）'),('renders/hero.png','本輪實際 Blender｜開放式高架月台')]):
 with Image.open(OUT/file)as im:thumb=ImageOps.contain(im.convert('RGB'),(960,720))
 canvas.paste(thumb,(i*960,55));d.text((i*960+14,10),label,font=font,fill='#34575d')
canvas.save(OUT/'reference-comparison.png')
# Distinct engineering plan, not a render or fake overlay in the game.
canvas=Image.new('RGB',(1100,1100),'#f3eee4');d=ImageDraw.Draw(canvas);xy=lambda p:(550+p[0]*40,520+p[1]*40)
d.polygon([xy(p)for p in m['sitePolygonXZ']],fill='#c8dbbf',outline='#54796b');d.polygon([xy(p)for p in m['referenceSitePolygonXZ']],fill='#e1d7c7',outline='#8e8f84')
for p in load('collision-shells.json')['shells']:
 if p['bottom']<1.5 and p['top']>.22 and p['kind']!='guard'and p['role']!='walkable':d.polygon([xy(q)for q in p['polygonXZ']],fill='#bda68c')
for q in m['NPCReservedSquaresXZ']:
 d.rectangle([xy((q[0],q[1])),xy((q[2],q[3]))],outline='#b17f29',width=3);d.text(xy((q[0],q[1])),'NPC 3×3',font=small,fill='#775d22')
for p in s['fourUnchangedBridgePorts']:
 x,y=xy(p['centrelineWorldXZ']);d.ellipse((x-8,y-8,x+8,y+8),fill='#3b788a');d.text((x+9,y-12),p['id']+' / 4.8',font=small,fill='#285867')
d.text((24,18),'工程平面圖（非渲染）：四橋口、NPC 清空區與已校正的座椅',font=font,fill='#34575d');d.text((24,1052),'綠：前輪已存在的台地提案；米灰：V9 原地界；棕：碰撞候選區',font=small,fill='#34575d');canvas.save(OUT/'space-plan.png')
show,cand=g['results'];assert show['mode']=='showcase'and cand['mode']=='game-candidate';previous=ROOT/'work/open-platform-before';old=json.loads((previous/'gltf-summary.json').read_text());oldShow,oldCand=old['results']
# Parse the actual latest command log, never recycle an earlier 50-case claim.
log=ROOT/'work/open-platform-pr14-game-check.log';txt=log.read_text();passed=int(re.search(r'ℹ pass (\d+)',txt).group(1));assert 'ℹ fail 0'in txt and '> eslint'in txt and 'built in'in txt
shutil.copy2(log,OUT/'existing-game-check.log');(OUT/'existing-game-sanity.json').write_text(json.dumps({'command':'npm run check','nodeVersion':subprocess.check_output(['node','--version'],text=True).strip(),'exitCode':0,'reportedTestFilesPassed':passed,'reportedFailures':0,'lintPassed':True,'buildPassed':True,'logSHA256':sha(OUT/'existing-game-check.log'),'scope':'Existing unchanged PR14 game only. Node reports test files in this run; not a new-model gameplay integration test.'},ensure_ascii=False,indent=2)+'\n')
mobile=next(f for f in o['framing']if f['camera']=='player-mobile');count=len(o['groundStructuralSupports']);rows='\n'.join('| '+name+' | '+' × '.join(f'{n:.3f}'for n in v['sizeWorldXYZ'])+' |'for name,v in a['componentBounds'].items());reduction=100*(1-cand['triangles']/oldCand['triangles']);batch=100*(1-cand['meshPrimitives']/oldCand['meshPrimitives'])
readme=f'''# 交通大升級 V9｜開放式高架月台修訂

[Draft PR #14](https://github.com/qaz741612/sky-isles/pull/14) · [可編輯 BLEND](transport-station-v9.blend) · [展示 GLB](transport-station-v9-showcase.glb) · [遊戲候選 GLB](transport-station-v9-game-candidate.glb)

**本次收尾沒有重新建模**；BLEND與兩GLB仍和ca94f48逐位元一致，見[鎖定核對](asset-lock.json)。以下改造描述是ca94f48已保存的成果。

既有 V9 Blender 修訂完整移除高架長棚的 **{revision['removedUpperCanopyCount']}** 個物件及孤立網格，保留地面站房金屬屋頂、玻璃天窗、木格柵、招牌及入口；沒有重建整座車站或沿用弧形屋頂模板。橋體／拱梁、軌道、月台、樓梯與電梯也保留。

![實際 Blender 開放式月台主視圖](renders/hero.png)

兩節列車保持原尺寸、輪軌關係與軌道中心，只繞自身中心迴轉180°朝西；45°主視角改由西側觀看。小型遮雨亭僅覆蓋樓梯出口，與列車平面重疊0。月台補端部護欄、細直欄、靠軌安全線、鋪面收邊、候車資訊、獨立照明與短坐靠設施。前庭花園只縮短兩個前端，座椅回到真正鋪面內；樹木、暖木、主要花帶與留白保留。

## 同源六視圖與玩家鏡頭

![同一份最終原檔的11個視角](render-index.png)

'''+ ' · '.join(f'[{labels[n]}]({records[n]["file"]})'for n in views)+f'''

全部修改後圖源自同一 BLEND：`{source}`。六視圖為正／背／左／右／俯視及45°主視角。這些是 **Blender Cycles 渲染與原遊戲相機參數模擬，不是遊戲整合截圖**。

## 真正同機位修改前後

![手機預設鏡頭前後比較](comparison-player-mobile.png)

[桌機預設比較](comparison-player-desktop.png) · [45°同機位比較](comparison-hero.png) · [俯視比較](comparison-top.png) · [相機逐項核對](before-render-record.json)

手機兩側固定720×1280渲染像素（360×640 CSS／DPR2）、dist22、pitch0.67、yaw0.12、垂直FOV58、目標(0,2,3.5)，出生點(0,0.5,3.5)不動；這是出生瞬間加1.5目標高度的靜態模擬，未冒稱落地後／避障中的實際相機。已用原src/sim/camera-profile.js核對兩組參數，見camera-profile-audit.json。未用zoom28或橋口觀察點代替預設圖。修改後車頭與站房入口的投影範圍完整入鏡，車頭中心視線先撞到車頭本身；這不是全部車頭像素均無遮蔽的證明，小亭／欄杆仍遮住車頭下緣，正面讀感待人工判斷。**右端車尾及部分外側高架仍裁切，沒有宣稱整列車／全島均在手機預設窄幅內**。補充拉遠圖明確標示，請勿混用。

## 本輪測量

| 版本 | GLB實際三角面 | 材質 | 網格批次 | 大小 |
| --- | ---: | ---: | ---: | ---: |
| 前輪展示 | {oldShow['triangles']:,} | {oldShow['materials']} | {oldShow['meshPrimitives']} | {oldShow['bytes']/1e6:.2f} MB |
| 本輪展示 | {show['triangles']:,} | {show['materials']} | {show['meshPrimitives']} | {show['bytes']/1e6:.2f} MB |
| 前輪候選 | {oldCand['triangles']:,} | {oldCand['materials']} | {oldCand['meshPrimitives']} | {oldCand['bytes']/1e6:.2f} MB |
| 本輪候選 | {cand['triangles']:,} | {cand['materials']} | {cand['meshPrimitives']} | {cand['bytes']/1e6:.2f} MB |

候選較前輪三角面減{reduction:.1f}%、靜態材質合批後批次減{batch:.1f}%；主建築沒有縮小。薄玻璃近似、微植栽與倒角差異仍限候選，不回寫展示原檔。33材質仍全部有實際用途；頂棚原本共用站房屋面／玻璃／木材，不能連共用材質一併刪除。

## 檢查與界線

- {a['meshObjectsChecked']:,}個源網格重新開啟，全部封閉／正體積；{revision['retainedMeshCount']}個保留構件的幾何、材質指派、變換完全相同。
- {count}個低位結構支承以實際三角面投影檢查，越出台地0；兩NPC 3×3空間、S09/S10/S15/S18、15地面採樣點與3上層平面通道通過離線檢查。
- 安心生養以10.2半徑保守檢查，交通提案島台與其交疊0；其他非接入路段交疊0。四口與原苑字控制點不改。
- 兩GLB Khronos為0 errors／0 warnings，實際Three.js GLTFLoader／WebGL與量測另列[報告](PERFORMANCE.md)。
- 原PR14既有遊戲`npm run check`：本輪Node實際回報{passed}個測試檔通過、0失敗，lint與build成功；不沿用舊50項文字，也不把這結果當新模型整合證據。

[空間／碰撞候選稽核](VALIDATION.md) · [美術自審及待驗](ART-REVIEW.md) · [基底安全整理方案（未執行）](BRANCH-ISOLATION.md) · [重現流程](WORKFLOW.md) · [修改清單](MODIFIED-FILES.md) · [媒體大小／SHA256](media-manifest.json)

RECOVERY.md及RECOVERY-INTERRUPTION-2.md保留為先前中斷的歷史紀錄，本輪最新狀態以本README、VALIDATION及ACCEPTANCE為準。

沒有修改安心生養、其他島、正式遊戲、政策、苑字路網、main或Production；沒有處理全地圖橋邊景觀。本輪不整合、不合併、不部署。等待人工美術與手機視角驗收。
'''
(OUT/'README.md').write_text(readme)
validation=f'''# 尺寸、幾何、碰撞候選與測試

來源BLEND SHA256：`{source}`。

## 實體及保留核對

上層Canopy語意組完整刪除，含241個屋面、玻璃帶、柱、梁、斜撐、簷底及懸掛資訊物件；未按模糊的roof字串跨層刪除。孤立網格移除{revision['purgedUnusedMeshCount']}份。共享屋面／玻璃／木質PBR仍供地面站房及小亭使用。保留841個站房／招牌／橋拱／軌道／樓梯電梯構件的頂點、面、材質指派及world matrix指紋一致。列車只作剛性180°旋轉，尺度1，輪軌最大差{a['wheelRail']['maximumMismatch']:.6f}。

| 實際組件 | X寬 × Y高 × Z深 |
| --- | --- |
{rows}

小亭屋面1.78×1.78，世界Y5.76；覆蓋XZ(-7.41,-4.59)至(-5.63,-2.81)，屋底至上層步行面淨高1.94。列車最高約5.888，平台步行面3.75；前側平台橋底3.289，凹槽軌道局部底部約3.02。接面因原工程共面黑塊，TopAccessBridge／LiftLandingBridge抬0.003，StairTopLanding抬0.006；導盲線合併為一份實體以消除交叉黑縫。未新增上樓控制／電梯動作／搭乘列車。

## 空間檢查方法及結果

- 四個4.8橋口及真正Bezier不動；南側共享口不分隔。兩處NPC預留仍為3×3，不建立人物或對話。
- 0.12四鄰接網格、0.33人物半徑，地面15個目標連通，東西全寬道路與地面殼交疊0。源BLEND低位實體NPC侵入0。
- 上層月台與左右連橋三條中心路線各擴0.33，與柱、資訊、坐靠及護欄候選區交疊0；小亭與列車掃掠包絡平面交疊0。這不證明原遊戲角色可自動踏階。
- {count}個花圃收邊、座椅、樹幹、燈座及資訊設施，用實際evaluated三角面XZ聯集而非凸包檢查，越出台地0。植物樹冠與屋簷的設計懸挑另處理，不把它們誤判為無地面支承。
- 島緣沿前輪原型島台邊界配置，四口留空；側向花園局部土地提案仍增加約12.568，沒有再擴大或寫回正式配置。安心生養按10.2半徑檢查交疊0，非接入路段交疊0。
- 重新開啟{a['meshObjectsChecked']}個網格：封閉／正向體積問題0，木紋packed，無外部材質遺失。GLB實際三角面可能少於evaluated數，匯出會略去退化微面。

## 已執行

`npm run check`於原PR14工作目錄執行，Node{subprocess.check_output(['node','--version'],text=True).strip()}回報{passed}個測試檔通過、0失敗；lint、正式build成功。完整log及SHA在existing-game-check.log／existing-game-sanity.json。50是前輪報告的計數，本輪只引用實際工具結果。兩GLB Khronos零錯誤零警告，瀏覽器載入檔案hash、貼圖解碼與實際WebGL繪圖已獨立執行。

## 明確未驗證

此模型未接Sky Isles runtime，碰撞殼只是可編輯候選。沒有新車站的遊戲膠囊碰撞、樓梯步階、上下層頭頂、電梯操作、相機避障、列車動畫、解謎與政策UI整合回歸；沒有真iOS／Android或桌機GPU驗收。桌機／手機Blender相機是參數模擬，非實際角色操作畫面。原遊戲測試不會替上述項目背書。

手機預設可見西側車頭、主要車身、站房入口及大部分高架；東側車尾／外側結構仍有裁切。投影頂點比例不是屏幕面積或可見性比例，不能拿來宣稱87%視覺通過。車頭中心兩條ray只證明該點無前置物體遮擋，不代表所有窗面與車身像素均無遮擋。
'''
(OUT/'VALIDATION.md').write_text(validation)
perf=f'''# 遊戲候選優化與實測

| 檔案 | 以前三角面 → 現在 | 以前大小 → 現在 | 以前批次 → 現在 |
| --- | --- | --- | --- |
| 展示 | {oldShow['triangles']:,} → {show['triangles']:,} | {oldShow['bytes']/1e6:.3f} → {show['bytes']/1e6:.3f} MB | {oldShow['meshPrimitives']} → {show['meshPrimitives']} |
| 候選 | {oldCand['triangles']:,} → {cand['triangles']:,} | {oldCand['bytes']/1e6:.3f} → {cand['bytes']/1e6:.3f} MB | {oldCand['meshPrimitives']} → {cand['meshPrimitives']} |

模型不整體縮放。候選使用一段倒角、略去{m['candidate']['skippedMicroFoliageObjects']}個原先標記微植栽；同一交通島內靜態物件依材質合批，法線／UV／PBR參數保留，列車仍按車廂組織。其他島沒有合併進巨大世界網格。候選透明薄玻璃建築alpha0.25、列車alpha0.54，取消折射pass；延續前輪候選做法，不回存展示BLEND。不是靠簡化主建築輪廓達標。

## 本輪真正隔離Three.js量測

| 模式／視口 | 首幀ms | Draw calls | 提交三角面 | 平均幀ms | 約FPS |
| --- | ---: | ---: | ---: | ---: | ---: |
'''
for z in web['results']:
 p=z['performance'];perf+=f"| {z['mode']}／{z['viewport'][0]}×{z['viewport'][1]} | {z['loadToFrameMs']:.1f} | {z['drawCalls']} | {z['submittedTriangles']:,} | {p['meanFrameMs']:.1f} | {p['approxFPS']:.3f} |\n"
perf+='''
只在Cycles完成後量測，各24樣本。Chromium SwiftShader CPU軟體GPU、DPR1、localhost、一次一個模型；沒有世界其他島、角色物理、遊戲UI或真網路。數值不是桌機GPU／真手機FPS，不宣稱達到流暢門檻。前輪與本輪隔了環境重啟，不能將兩次CPU FPS當成嚴格同硬體前後比較；GLB三角面／批次與bytes是直接檔案量測，可重現。

## 進一步降低成本的方案（尚未採用）

1. glTF量化／meshopt無損或受控誤差壓縮：優先減下載體積，先核對玻璃、欄杆小構件及法線再採用。這不是三角面減量，不混為同一數字。
2. 遠景時只替微小花朵、樹葉與不可見室內家具建立LOD；近景保留已完成造型，須經同機位A/B確認。
3. 植栽、重複鋪磚與欄杆可用實例化取代大量獨立頂點；保留按島剔除，列車和玻璃分開。需要未來Three.js loader整合，不在本輪新增runtime依賴。
4. 合批後49 primitives中仍含列車分車廂／玻璃材質；若列車確定永不動才考慮進一步合批。本輪保留可維護結構，不為數字破壞動畫準備。
''';(OUT/'PERFORMANCE.md').write_text(perf)
art='''# 美術第一輪自審與待人工檢視

本輪正式方向為「開放式高架月台、完整展示列車」，取代舊參考的長棚要求；原核准圖仍作暖木、綠植、車站細節及建築完成度基準。

| 項目 | 已自行檢查與修正 | 待人工確認／具體限制 |
| --- | --- | --- |
| 主輪廓與焦點 | 移除全部上層長棚與支架；保留完整兩車，車頭朝西，主45°取景由西；地面站房作第二焦點 | 月台已開放，整體輪廓與舊長棚美術圖刻意不同；不自給美術分數 |
| 站房 | 屋頂、玻璃天窗、木格柵、立面字牌、入口及室內層次保留；841件指紋核對 | 玻璃門關閉，未作可深入室內玩法；離線燈光與未來遊戲不同 |
| 小亭與月台 | 只在左樓梯出口設1.78方亭，木簷底／細柱／照明；增端欄、細直欄、候車資訊、鋪面線及短坐靠 | 小亭是否足夠輕巧、細欄節奏與列車比例仍需人工美術驗收；右電梯自身小屋頂保留 |
| 列車 | 同尺寸剛性迴轉，不改兩車比例、窗框或車頭；輪軌接觸不變，主視圖完整兩車可見 | 靜態不可搭乘；手機預設車尾被裁，不宣稱全列車入鏡 |
| 庭院與植栽 | 原六棵樹與主要花帶保留，兩側前花圃縮短；先修座椅侵NPC，再修座椅越出台地，最終用實際三角投影重驗 | 廣場為四口與兩NPC留白，不能靠塞裝飾填滿；暖木及微花遠景讀感待人工 |
| 六面完成度 | 同一最終原檔輸出45°、正／背／左右／頂，無平面假背面或AI概念圖 | 純側面本來看不到完整車頭正面，不能用它取代主角度；未製作完整室內漫遊 |
| 原預設玩家鏡頭 | 桌機全列車及入口入鏡；手機車頭與入口投影入鏡；小亭／欄杆遮到車頭下緣，保留真實裁切結果，同站位同FOV | 手機右車尾及部分橋端仍裁切，車頭下緣有小亭／欄杆遮擋；zoom28與橋口補充圖只作補充，非預設驗收 |
| 邊界與玩法 | 四橋口、NPC、出生、世界中心線不改；局部支承與候選通行檢查通過 | 離線通行不是遊戲膠囊、相機、踩階或解謎驗證；未做全地圖橋邊造景 |

四向低仰角棚拍圖下緣仍可見棚拍平面界線，保留原始渲染不裁切隱藏；這不是建築破面。

未由工具宣稱人工美術驗收通過。人工仍需評估暖木、玻璃、站房識別、開放月台完整度、手機車尾裁切是否可接受。未接runtime前，不開始下一輪橋梁景觀或其他島工作。
''';(OUT/'ART-REVIEW.md').write_text(art)
# Legacy closed-canopy generator is intentionally retained for historical reproduction.
workflow='# 本輪只讀模型的重現流程\n\n本輪禁止重新建模。固定使用ca94f48的BLEND、展示GLB與候選GLB；asset-lock.json列出精確SHA與Git blob ID。不得執行open_platform_elevated_station_v9.py、build_elevated_station_v9.py、finish_elevated_station_v9.py或optimize_elevated_station_v9_candidate.py來覆蓋本輪模型。這些程式僅保留為歷史可恢復來源。\n\n工具：Blender/bpy4.3、Python3.11、Shapely、NumPy、Pillow，既有Three.js／Playwright／Khronos工具環境；未修改runtime依賴。文字輪廓採Noto Sans CJK（SIL OFL），原檔已有mesh與packed原創木紋；沿用專案MIT及既有授權。\n\n```sh\npython scripts/blender/render_elevated_station_v9.py\npython scripts/blender/render_open_platform_before.py\npython scripts/blender/audit_elevated_station_v9_source.py\npython scripts/blender/audit_elevated_station_v9.py\npython scripts/blender/audit_open_platform_v9.py\nnode scripts/blender/check_open_platform_camera_profile.mjs\nnode scripts/blender/validate_elevated_station_v9.mjs\n```\n\nPython使用已安裝bpy的工具虛擬環境，如work/parent-child-blender/render-env/bin/python。渲染不儲存修改原檔，逐圖來源與PNG SHA都吻合才續用；11張最終圖使用同一BLEND，原始樣本及解析度見render-record.json。\n\n拆棚前來源固定為81f7408的BLEND，SHA a975409e16bf406b4fe1ae9981d632c527f85244387e3a88111baad4177f2abb。before/有明確舊來源標記。前後桌機／手機／45°／頂視相機位置、方向、鏡頭、正交尺度與像素尺寸都由報告工具assert；補充zoom28不代替手機預設。\n\n等Cycles完成後再測量，避免與軟體GPU爭CPU：\n\n```sh\nnpx vite --host 127.0.0.1 --port 4192 --strictPort\nnode scripts/blender/check_elevated_station_v9_webgl.mjs\nnpm run check\npython scripts/blender/report_open_platform_v9.py\npython scripts/blender/write_open_platform_acceptance.py\npython scripts/blender/finalize_open_platform_delivery.py\n```\n\nWebGL只載入單一資產的本機viewer，不是正式遊戲；DPR1的1280×800及390×844，不宣稱真機GPU效能。Blender手機720×1280對應360×640 CSS／DPR2的原手機profile，並非720 CSS寬。\n\n最後verify_elevated_station_v9_github.py以精確提交SHA下載manifest及每個檔案，比對byte數與SHA256。manifest本身直接與本地檔案逐byte比較；下載收據及DELIVERY另列，避免自我雜湊循環。全程保留ca94f48三個模型SHA不變，不合併或部署。\n'
(OUT/'WORKFLOW.md').write_text(workflow)
# This is a proposal only. No force push/base retarget occurs in this task.
branch='''# PR #14 基底隔離方案（本輪不執行）

## 現況

PR14仍為Draft，base是未核准PR13來源codex/seven-policy-islands-blender-assets-v1。僅把base下拉選單改成較早分支會把PR13的七島資產一起列入差異，不能直接這樣做。

本輪將交通專用變更正常fast-forward提交回原PR14 head codex/transport-elevated-station-v9-blender-prototype；沒有重寫遠端歷史、沒有改PR13、沒有合併。恢復的獨立worktree以已明確核准的PR11美術來源ac433fd為基底，已驗證交通工具僅依賴該基底存在的parent_child_geometry通用工具，不依賴七島hall模板。

## 正式整合前的安全流程

1. 將當時PR14最終head SHA另存備份tag，確認原BLEND／GLB／圖片／程式SHA完整；保留PR13原分支。所有步驟採Cloudflare skip提交，不改Production。
2. 由已核准PR11來源codex/parent-child-blender-model-v1的ac433fd建立暫存隔離分支，**只取transport-only-paths.txt列出的交通專用路徑**。不cherry-pick整個PR13，不restore整個docs/design或scripts目錄。
3. 比較ac433fd到隔離分支：變更清單必須僅為交通原型／專用工具，且src、public、政策、套件與安心生養檔案完全不變。四口／NPC及候選模型依該基底重跑。PR12遊戲整合仍為Draft，不將其視為已核准而默默帶入。
4. 取得基底確認後，可把PR14 head換成該隔離歷史並retarget base；若沿用同一head，必須先保存遠端舊SHA，再用帶明確舊SHA的force-with-lease，拒絕覆蓋期間他人提交。亦可用已核對的獨立整合PR，PR14繼續作美術紀錄；這屬後續整合決策。
5. 在GitHub再次核對Files changed不含seven-policy-islands資產，下載核對所有模型與媒體SHA，保持Draft等待審查，才討論整合。任何PR均不自動合併。

本輪只提出方案，**未改base、未force-push、未建立無關原型／新PR、未將已完成成果刪除**。若未完成上述隔離，不應合入PR14，否則仍會攜帶未核准七島歷史。
''';
if not (OUT/'BRANCH-ISOLATION.md').exists():(OUT/'BRANCH-ISOLATION.md').write_text(branch)

# Preserve source-build script hashes and separately record current reproduction script hashes.
m['currentReproductionScriptsSHA256']={str(p.relative_to(ROOT)):sha(p)for p in sorted((ROOT/'scripts/blender').rglob('*'))if p.is_file()and(p.name.endswith(('.py','.mjs','.html')))and('elevated_station_v9'in str(p)or'open_platform'in p.name)};(OUT/'model-report.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
# Actual current GLB JSON material inventory, not an inherited report.
materials={}
for mode in ['showcase','game-candidate']:
 data=(OUT/('transport-station-v9-'+mode+'.glb')).read_bytes();length=int.from_bytes(data[12:16],'little');doc=json.loads(data[20:20+length]);materials[mode]=[{'name':mat.get('name'),'pbr':mat.get('pbrMetallicRoughness'),'alphaMode':mat.get('alphaMode','OPAQUE'),'doubleSided':mat.get('doubleSided',False),'emissiveFactor':mat.get('emissiveFactor'),'extensions':mat.get('extensions')}for mat in doc['materials']]
(OUT/'material-report.json').write_text(json.dumps(materials,ensure_ascii=False,indent=2)+'\n')
for p in OUT.glob('draft-*.png'):
 dst=ROOT/'work/open-platform-iterations'/p.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.move(p,dst)
# manifest will be regenerated by the final delivery helper, after preservation/delivery docs.
print(json.dumps({'sourceSHA256':source,'finalSameSourceRenders':len(views),'sameCameraComparisons':len(before),'reportedGameTestFiles':passed,'candidateTriangles':cand['triangles'],'candidatePrimitives':cand['meshPrimitives']},ensure_ascii=False))
