"""Evidence boards: arrange unchanged real render/screenshot pixels with captions."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[2];O=R/'docs/previews/flood-control-island-g-v5';font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';f=lambda n:ImageFont.truetype(font,n)
def board(name,title,items,width=800):
 h=0;tiles=[]
 for file,label in items:
  with Image.open(O/file)as src:
   src=src.convert('RGB');src.thumbnail((width,640));tile=Image.new('RGB',(width,src.height+65),'#f0f4f0');tile.paste(src,((width-src.width)//2,65));ImageDraw.Draw(tile).text((15,15),label,font=f(21),fill='#264c52');h=max(h,tile.height);tiles.append(tile)
 im=Image.new('RGB',(width*2,h*((len(tiles)+1)//2)+100),'#f0f4f0');ImageDraw.Draw(im).text((20,22),title,font=f(29),fill='#264c52')
 for i,t in enumerate(tiles):im.paste(t,((i%2)*width,100+(i//2)*h))
 im.save(O/name)
board('self-review-comparison.png','G V5｜實際 Blender 第一輪 → 最終修正，同機位',[('iteration-1/blender/hero.png','第一輪：共面黑斑／不完整機械層／水岸待修'),('blender/reference-hero.png','最終：相同位置、目標與正交比例55'),('iteration-1/blender/front.png','第一輪正面：原始立面與水工構件'),('blender/front.png','最終正面：三閘口、機械／玻璃／基座精修')])
board('game-before-after.png','G 島｜PR17 舊版 → V5，實際遊戲同機位',[('before-game/g-hero.png','PR17 cd4bacb｜QA固定鏡頭'),('game/g-hero.png','G V5｜同世界座標／相機／畫面尺寸'),('before-game/g-top.png','PR17 舊島面｜QA正上方'),('game/g-top.png','V5 擴島與西側入口凹灣｜同正上方鏡頭')])
board('blender-six-views.png','G V5｜同一份最終 Blender 模型六視圖',[('blender/hero.png','45°主視圖'),('blender/front.png','正面'),('blender/back.png','背面'),('blender/left.png','左側'),('blender/right.png','右側'),('blender/top.png','俯視（取景55，完整島台）')],650)
print('Three real-image evidence boards saved; no synthetic scenery or enhancement')
