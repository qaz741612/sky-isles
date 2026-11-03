"""Arrange unaltered Blender/game pixels; verify equal-camera comparisons first."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
R=Path(__file__).resolve().parents[2];O=R/'docs/previews/flood-control-island-g-v5-1'
font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def board(name,title,items,width=700):
 tiles=[]
 for file,label in items:
  with Image.open(O/file)as image:
   image=image.convert('RGB');image.thumbnail((width,680));tile=Image.new('RGB',(width,image.height+64),'#eef3f1');tile.paste(image,((width-image.width)//2,64));ImageDraw.Draw(tile).text((14,16),label,font=ImageFont.truetype(font,19),fill='#264c52');tiles.append(tile)
 height=max(t.height for t in tiles);out=Image.new('RGB',(width*2,height*((len(tiles)+1)//2)+90),'#eef3f1');ImageDraw.Draw(out).text((18,20),title,font=ImageFont.truetype(font,26),fill='#264c52')
 for i,tile in enumerate(tiles):out.paste(tile,((i%2)*width,90+(i//2)*height))
 out.save(O/name)
def records(file):return {r['name']:r for r in json.loads((O/file).read_text())['records']}
a,b=records('before/blender/render-record.json'),records('blender/render-record.json')
for name in ['hero','front','top','near-dam','near-command']:
 for key in ['cameraBlender','rotation','orthoScale','size']:assert a[name][key]==b[name][key],(name,key)
board('six-views.png','G V5.1｜同一份最終 Blender 六視圖',[(f'blender/{n}.png',label)for n,label in [('hero','45°主視'),('front','正面'),('back','背面'),('left','左側'),('right','右側'),('top','完整俯視')]])
board('comparison-blender.png','原 V5 → V5.1｜相同 Blender 機位、尺寸、光照',sum(([('before/blender/'+n+'.png','原 V5｜'+label),('blender/'+n+'.png','V5.1｜'+label)]for n,label in [('hero','主視'),('near-dam','三閘水工'),('near-command','指揮中心'),('top','島面與四區景觀')]),[]))
a,b=records('before/game/capture-record.json'),records('game/capture-record.json')
for name in ['g-hero','g-top']:
 for key in ['camera','args','size']:assert a[name][key]==b[name][key],(name,key)
board('comparison-game.png','原 V5 → V5.1｜Three.js 實際畫面／固定 QA 機位',sum(([('before/game/'+n+'.png','原 V5｜'+label),('game/'+n+'.png','V5.1｜'+label)]for n,label in [('g-hero','主視'),('g-top','俯視')]),[]))
native=[]
for name,label in [('mobile-native','原生方向'),('mobile-waterfront-player','原生水岸旋轉')]:
 for key in ['args','size','orbit']:assert a[name][key]==b[name][key],(name,key)
 native += [('before/game/'+name+'.png','原 V5｜'+label),('game/'+name+'.png','V5.1｜'+label)]
board('comparison-mobile.png','原生手機｜同站位與操作參數；G 局部避障另有修正',native,500)
board('comparison-camera.png','G 入口手機｜相同模型、站位及 orbit；修正低位遮擋',[('iteration-6/game/mobile-command-player.png','修正前｜前景屋簷遮住角色下半身'),('game/mobile-command-player.png','修正後｜六點視線／穩定避障')],500)
print('Five evidence boards saved; camera comparisons checked, image pixels only resized for layout')
