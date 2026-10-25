"""Package actual Blender renders, metadata and a local reference comparison document.
No images are AI generated. The source reference bytes are not available to this worker.
"""
from pathlib import Path
import json,hashlib,base64,subprocess,zipfile
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/design/parent-child-blender-model-v1'
names=[('hero','45° 主視角'),('front','建築正面'),('back','建築背面'),('left','建築左側'),('right','建築右側'),('top','正上方'),('eaves','屋簷底部與構件'),('player','1.65m 站立視線')]
records=json.loads((OUT/'render-record.json').read_text())['views'];assert len(records)==8
source=hashlib.sha256((OUT/'parent-child-centre.blend').read_bytes()).hexdigest()
assert all(v['sourceBlendSHA256']==source for v in records)
for v in records:assert hashlib.sha256((OUT/v['file']).read_bytes()).hexdigest()==v['imageSHA256']
# A labelled index only. The eight source PNG renders remain untouched.
font_path=subprocess.check_output(['fc-match','-f','%{file}','Noto Sans CJK TC'],text=True).strip();font=ImageFont.truetype(font_path,21)
contact=Image.new('RGB',(1600,2*318),(247,245,239));draw=ImageDraw.Draw(contact)
for i,(name,label)in enumerate(names):
 image=Image.open(OUT/'renders'/(name+'.png')).convert('RGB');image.thumbnail((392,270),Image.Resampling.LANCZOS);x=(i%4)*400+(400-image.width)//2;y=(i//4)*318+5;contact.paste(image,(x,y));draw.text(((i%4)*400+14,(i//4)*318+282),label,font=font,fill=(47,78,81))
contact.save(OUT/'eight-views.png')
# Self-contained local document: use the user's exact 2D file, never recreate it.
hero=base64.b64encode((OUT/'renders/hero.png').read_bytes()).decode()
html='''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>安心生養｜原圖與 Blender 並排對照</title><style>
*{box-sizing:border-box}body{overflow-wrap:anywhere;margin:0;padding:24px;background:#f4f1e9;color:#29494c;font:16px/1.6 system-ui,sans-serif}h1{font-size:23px}p{max-width:1000px}.toolbar{display:flex;gap:20px;align-items:center;flex-wrap:wrap;margin:18px 0}button,label.pick{border:1px solid #9dafaa;padding:9px 15px;border-radius:8px;background:white;cursor:pointer}input[type=file]{max-width:260px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.grid>section{min-width:0}.frame{background:#deded9;aspect-ratio:1082/741;position:relative;display:grid;place-items:center;overflow:hidden;border:1px solid #bdc7c2}.frame img{width:100%;height:100%;object-fit:contain}.empty{padding:25px;text-align:center}.frame img:not([src]){display:none}h2{font-size:17px}.small{font-size:13px;color:#647873}@media(max-width:800px){.grid{grid-template-columns:1fr}}
</style><h1>安心生養島｜原始效果圖 × Blender 實際模型</h1><p>只有 2D 圖檔即可對照，不需要原本的 3D 檔。請選入您手上的效果圖，左側會顯示原圖，右側為交付模型的真實 Cycles 渲染。圖片僅在本機處理，不上傳，也不重新生成原圖。</p><div class="toolbar"><input id="file" type="file" accept="image/png,image/jpeg,image/webp"><button id="save" disabled>儲存並排 PNG</button><span id="info" class="small">原圖由使用者選入；未將聊天圖片重畫成原圖。</span></div><div class="grid"><section><h2>使用者原始效果圖</h2><div class="frame"><span id="empty" class="empty">選擇原始 PNG／JPG 圖檔後，即可並排檢查。</span><img id="ref"></div></section><section><h2>Blender Cycles｜實際 3D 模型</h2><div class="frame"><img id="model" src="data:image/png;base64,HERO_BASE64"></div></section></div><p>建議依序比較：雙層弧屋頂、入口與格柵、窗框及室內深度、側翼、遊具與沙坑、樹池與弧椅、材質配色、整體構圖。背面與未見區域為依相同建築語言延伸的設計，並非原圖提供的事實。</p><p class="small">這是離線對照文件，不是政策島遊戲的新網站。八視角、模型及差距報告另見 README.md。主渲染 SHA256：HERO_SHA</p><script>
const file=document.getElementById('file'),ref=document.getElementById('ref'),model=document.getElementById('model');let local;
file.onchange=()=>{const f=file.files[0];if(!f)return;if(local)URL.revokeObjectURL(local);local=URL.createObjectURL(f);ref.onload=()=>{document.getElementById('empty').hidden=true;document.getElementById('save').disabled=false;document.getElementById('info').textContent=f.name+' · '+ref.naturalWidth+'×'+ref.naturalHeight+'（只在本機顯示）';};ref.src=local;};
document.getElementById('save').onclick=()=>{const w=1600,h=Math.round(w*741/1082),canvas=document.createElement('canvas');canvas.width=w*2;canvas.height=h+70;const c=canvas.getContext('2d');c.fillStyle='#f4f1e9';c.fillRect(0,0,canvas.width,canvas.height);c.font='28px system-ui,sans-serif';c.fillStyle='#29494c';c.fillText('使用者原始效果圖',24,45);c.fillText('Blender Cycles 實際渲染',w+24,45);for(const[image,x]of[[ref,0],[model,w]]){const s=Math.min(w/image.naturalWidth,h/image.naturalHeight),iw=image.naturalWidth*s,ih=image.naturalHeight*s;c.drawImage(image,x+(w-iw)/2,70+(h-ih)/2,iw,ih);}canvas.toBlob(blob=>{const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='parent-child-reference-comparison.png';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);});};
</script></html>'''
html=html.replace('HERO_BASE64',hero).replace('HERO_SHA',hashlib.sha256((OUT/'renders/hero.png').read_bytes()).hexdigest());(OUT/'comparison.html').write_text(html)
files=[]
for p in [OUT/'parent-child-centre.blend',OUT/'parent-child-centre.glb',OUT/'eight-views.png',OUT/'comparison.html',*[OUT/'renders'/(n+'.png')for n,_ in names]]:
 d={'path':str(p.relative_to(OUT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 if p.suffix=='.png':
  with Image.open(p)as image:d.update(width=image.width,height=image.height)
 files.append(d)
(OUT/'media-manifest.json').write_text(json.dumps({'sourceBlendSHA256':source,'source':'Actual Blender Cycles renders; no image-generation models used. Original 2D file is selected locally in the offline comparison document.','files':files},ensure_ascii=False,indent=2)+'\n')
(OUT/'SHA256SUMS').write_text(''.join(d['sha256']+'  '+d['path']+'\n'for d in files))
# A focused downloadable bundle avoids downloading unrelated repository history.
with zipfile.ZipFile(OUT/'parent-child-model-review.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in sorted(OUT.rglob('*')):
  if p.is_file()and p.suffix!='.zip'and p.name not in ['github-verification.json','bundle-manifest.json']:z.write(p,str(p.relative_to(OUT)))
 z.write(ROOT/'LICENSE','LICENSE')
p=OUT/'parent-child-model-review.zip';(OUT/'bundle-manifest.json').write_text(json.dumps({'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()},indent=2)+'\n')
print(json.dumps({'eightRenders':8,'allFromSameBlend':True,'bundleMB':round(p.stat().st_size/1e6,2),'referenceImageBytesAvailable':False}))
