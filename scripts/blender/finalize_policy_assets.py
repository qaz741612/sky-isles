"""Final report/gallery/manifest from completed actual Blender renders. No AI images. MIT."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/design/seven-policy-islands-blender-v1';IDS=['transport','senior','industry','environment','digital','water','education'];NAMES={'transport':'交通大升級','senior':'幸福養老','industry':'產業青年','environment':'宜居環境','digital':'智慧公所','water':'治水防災','education':'教育發展'};VIEWS=['hero','front','back','left','right','top'];VIEWNAMES=['45° 主視角','正面','背面','左側','右側','正上方'];font_path='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';font=ImageFont.truetype(font_path,23);small=ImageFont.truetype(font_path,17)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();models=[];hero_scale=None;hero_pose=None
for key in IDS:
 d=OUT/key;model=json.loads((d/'model-report.json').read_text());records=json.loads((d/'render-record.json').read_text());assert len(records['views'])==6,key
 assert sha(d/(key+'.blend'))==model['blendSHA256'];assert sha(d/(key+'.glb'))==model['glbSHA256'];assert not model['geometryAudit']['issues'];assert not any(n['intersectingObjects']for n in model['npcClearanceChecks'])
 for r in records['views']:
  assert r['sourceBlendSHA256']==model['blendSHA256'];assert sha(d/r['file'])==r['imageSHA256'];
  with Image.open(d/r['file'])as im:im.verify()
  if r['view']=='hero':
   pose=(r['cameraPositionXYZ'],r['cameraRotationRadians'],r['size'])
   if hero_scale is None:hero_scale=r['orthoScale'];hero_pose=pose
   else:assert r['orthoScale']==hero_scale and pose==hero_pose
 sheet=Image.new('RGB',(1200,650),'#f1ebde');draw=ImageDraw.Draw(sheet)
 for i,v in enumerate(VIEWS):
  with Image.open(d/'renders'/(v+'.png'))as source:thumb=ImageOps.contain(source.convert('RGB'),(400,300))
  x=(i%3)*400;y=(i//3)*325;sheet.paste(thumb,(x,y+25));draw.text((x+10,y+1),VIEWNAMES[i],font=small,fill='#385759')
 sheet.save(d/'six-views.png')
 models.append((key,model))
# All hero cameras and resolution match exactly; every thumbnail uses the SAME 0.5 scale.
overview=Image.new('RGB',(2560,1070),'#eee9dd');draw=ImageDraw.Draw(overview)
for i,(key,model)in enumerate(models):
 x=(i%4)*640;y=(i//4)*535
 with Image.open(OUT/key/'renders/hero.png')as im:thumb=im.convert('RGB').resize((640,480),Image.Resampling.LANCZOS)
 overview.paste(thumb,(x,y+45));draw.text((x+18,y+7),NAMES[key],font=font,fill='#32565a')
draw.text((1940,585),'七島相同相機・相同尺度',font=font,fill='#32565a');draw.text((1940,635),'全部來自實際 Blender Cycles 渲染',font=small,fill='#32565a');draw.text((1940,675),f'正交尺度 {hero_scale:.1f}；全圖統一縮小 50%',font=small,fill='#32565a');draw.text((1940,715),'未單獨放大或縮小任何一座島',font=small,fill='#32565a');overview.save(OUT/'seven-islands-overview.png')
rows=[]
for key,m in models:
 load=json.loads((OUT/key/'three-loading-report.json').read_text());s=m['sizeXYZ'];r=m['recommendedPlatform']['radius'];rows.append(f"| [{NAMES[key]}]({key}/README.md) | [{'BLEND'}]({key}/{key}.blend) / [GLB]({key}/{key}.glb) | {s[0]:.2f}×{s[1]:.2f}×{s[2]:.2f} | {load['triangles']:,} | {load['materials']} | {'**' if r>12 else ''}{r:.1f}{'（>12）**'if r>12 else ''} |")
rootreadme='''# 七座政策島｜獨立 Blender 資產

七套可編輯模型與 GLB，依使用者提供的七張正式設計圖製作；安心生養只作美術與複雜度上限基準，原始 BLEND／GLB 不變。本輪沒有將七島整合進現有遊戲，也沒有修改苑字中心線、島中心、Production 或正式政策。

## 相同角度、相同尺度總覽

![七島實際 Blender Cycles 總覽](seven-islands-overview.png)

七個主視圖使用**同一相機位置／旋轉、正交尺度 33.8、1280×960**，總覽每張統一縮成 640×480。未單獨調整島嶼縮放。這是七張真實 Cycles 渲染的排版，不是 AI 概念圖。

## 模型、下載與尺寸

尺寸為完整資產的 Blender X寬×Y深×Z高，**包含獨立展示平台與四個展示橋臂**。半徑是量測建築（含屋簷）、低景觀及設施後，加 1m 邊緣餘裕得到的圓形美術展台；不是已批准套用到遊戲的半徑。

| 政策島 | 可編輯模型／匯出 | 完整包圍盒 | GLB 三角面 | 材質 | 圓展台半徑 |
| --- | --- | --- | ---: | ---: | ---: |
'''+ '\n'.join(rows)+'''

[圖片對照](REFERENCES.md) · [尺寸與苑字路網評估](SITE-PLANNING.md) · [測試／限制](VALIDATION.md) · [可重現流程](WORKFLOW.md) · [舊交通模型備份](legacy-transport-backup/README.md) · [大小／SHA256](media-manifest.json) · [GitHub 上傳核對](github-verification.json)

## 審查界線

- 每島六張 PNG 都由同一份最終 `.blend` 以 Blender 4.3 Cycles 輸出；來源 SHA、相機及採樣見各島 `render-record.json`。
- 幾何封閉、三角面上限、材質、GLTFLoader／Khronos／隔離 WebGL 檢查完成。這些不等於人工美術驗收，也不等於遊戲碰撞與真機效能認證。
- 四個展示橋臂是設計圖展台的一部分，與真正 B 方案橋口不同。未來整合須按原中心線調整平台與橋口介面，保持建築比例。
- 交通的 12.6 圓台會吃進 J1／J2 附近筆畫空間；另提供局部拓展與橢圓方案，不能直接把圓半徑寫回正式世界。
- NPC 只保留 Empty 與結構化站位，不建立人形、對話或任務。列車／水景為獨立展示資產，本輪不加搭乘、任務或水文模擬。
- 屋頂及建築主體按主圖建立；植物花瓣、展板圖示、家具數量、水花等採一致的三維構造，沒有追逐 AI 多視圖中互相矛盾的小細節。玻璃門關閉，沒有宣稱已完成整套可進入室內。

沿用專案 [MIT 授權](../../../LICENSE)，沒有外部模型、貼圖或新音樂。等待使用者整體美術驗收，不自行開始遊戲整合或後續擴充。
'''
(OUT/'README.md').write_text(rootreadme,encoding='utf-8')
descriptions={'transport':'新版不對稱弧形車站、前廊、側向月台雨棚、短鐵道與雙車廂展示列車；候車亭、中央樹池座椅及站前花帶。','senior':'水平社區生活館、兩側連續遮蔭／休憩廊架、交流樹院、花圃及面向庭院的座椅。','industry':'青創工作館、白框實體玻璃溫室、抬高苗床與作物、後方展示棚、工藝展台與無人小型叉車展示。','environment':'真正開放的木構曲頂亭、寵物草地、低矮坡道／木隧道、環形園路、實體凹池及兩岸接地木橋、分層花帶。','digital':'公共服務主館與側翼、數位資訊亭、服務立牌、等候前庭、遮蔭座椅與低花圃。','water':'管理中心與上層觀察室、三跨控制閘門、上游水道／下游滯留池、實體落水面、觀察木平台與雨水花園。','education':'中高弧頂學習館、兩翼教室／閱讀館、玻璃後書架與桌椅、半場活動地坪、籃架、閱讀樹院及戶外書廊。'}
for key,m in models:
 d=OUT/key;s=m['sizeXYZ'];load=json.loads((d/'three-loading-report.json').read_text());r=m['recommendedPlatform']['radius'];n=m['npcReservations'][0]
 text=f'''# {NAMES[key]}｜Blender 資產

{descriptions[key]}

[下載 BLEND]({key}.blend) · [下載 Three.js GLB]({key}.glb) · [正式參考圖](../../../references/policy-islands/{key}-reference.png) · [實際模型規模](model-report.json) · [島台／橋口評估](site-planning.json)

![實際 Blender Cycles 主視圖](renders/hero.png)

## 六個實際角度

![六視角索引](six-views.png)

'''
 text+=' · '.join(f'[{label}](renders/{v}.png)'for v,label in zip(VIEWS,VIEWNAMES))+'\n\n'
 text+=f'''## 實際量測與分組

- 完整包圍盒：**{s[0]:.3f}×{s[1]:.3f}×{s[2]:.3f}**（Blender X/Y/Z；包含展台橋臂）。
- Blender 評估三角面 {m['evaluatedTriangles']:,}；GLB {load['triangles']:,}；材質 {load['materials']}；匯出網格批次 {load['meshes']}。
- 建築、室內可見家具、景觀、主題設施、家具與展台分 Collections；原始構件及非破壞倒角保持可編輯。
- 量測後圓展台半徑 **{r:.1f}**{'，超過 12，原因與替代方案請見島台報告'if r>12 else ''}。不縮小建築，不變更遊戲半徑。
- NPC 只有預留 Empty：本地 Blender XYZ `{n['positionBlenderXYZ']}`，活動預留半徑 {n['reservationRadius']}、互動半徑 {n['interactionRadius']}；玩家接近點 `{n['playerStopBlenderXYZ']}`。沒有角色或對話。
- [Khronos glTF](gltf-validation.json)：0 errors／0 warnings；[Three.js 載入](three-loading-report.json)：缺失材質 0；[實際 WebGL](webgl-compatibility.json)：GL error 0。
- [原始 BLEND 複驗](source-audit.json) · [渲染來源與相機](render-record.json) · [六視角無裁切檢查](camera-fit.json)。

## 尚待人工及整合驗收

主輪廓、曲面與色彩是否達到使用者對主圖的要求，仍由人工美術確認。花瓣分布、看板圖示及家具數量有可控簡化；沒有將原參考圖貼到模型上代替構件。玻璃使用同系列 PBR，但離線棚燈與未來遊戲光照會有差異。

這是獨立資產：正式橋口對齊、玩家地面／護欄／屋簷碰撞、相機避障、NPC 對話與真機 FPS 尚未整合驗證。展示橋臂可與 Site 群組分離，不得當作現有世界已更新。原始 BLEND 與 GLB 都保留供後續授權整合使用。
'''
 (d/'README.md').write_text(text,encoding='utf-8')
# Exact file sizes and hashes, no binary contents in reports.
files=[]
for p in sorted(OUT.rglob('*')):
 if not p.is_file()or p.name in ['media-manifest.json','SHA256SUMS','github-verification.json','DELIVERY.md']:continue
 if p.suffix not in ['.blend','.glb','.png','.json','.md']:continue
 data={'path':str(p.relative_to(OUT)),'repoPath':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}
 if p.suffix=='.png':
  with Image.open(p)as im:im.verify()
  with Image.open(p)as im:im.load();data.update(width=im.width,height=im.height)
 files.append(data)
(OUT/'media-manifest.json').write_text(json.dumps({'modellingReferences':'REFERENCES.md','allArtworkRenders':'Actual Blender Cycles files; overview/contact sheets only arrange those real renders.','files':files},ensure_ascii=False,indent=2)+'\n');(OUT/'SHA256SUMS').write_text(''.join(f['sha256']+'  '+f['path']+'\n'for f in files));print(json.dumps({'assets':7,'blenderRenders':42,'heroCommonScale':hero_scale,'manifestFiles':len(files)},ensure_ascii=False))
