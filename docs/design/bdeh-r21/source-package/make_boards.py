from pathlib import Path
import json,math,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageOps
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse
ROOT=Path(__file__).resolve().parent
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
font=lambda n,bold=False:ImageFont.truetype(BOLD if bold else FONT,n)
COL={'B':'#A06F49','D':'#2D667E','E':'#487B59','H':'#9B7853'}
TEXT={'B':('幸福養老','年輪環抱・療癒生活院','兩道承重木構長翼／日間照護與交流廳／開放療癒庭院'),
      'D':('智慧公所','市民服務之門','雙翼公共服務館／跨街一體拱／可見樓層與服務櫃台'),
      'E':('宜居環境','城市綠脈・雨水共生園','斜升綠脈／開放生態廊／雨水回收花園與環境教育'),
      'H':('教育發展','展頁探索・未來學習院','雙頁結構屋頂／透明閱讀中庭／STEAM 體驗與戶外論壇')}
SIZES={'B':'30 × 28','D':'32 × 29','E':'34 × 31','H':'33 × 30'}

def rounded(draw,box,fill,outline='#D3DFDE',r=20,weight=2):draw.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=weight)
def imgfit(path,size):
 im=Image.open(path).convert('RGB');im.thumbnail(size,Image.Resampling.LANCZOS)
 cv=Image.new('RGB',size,(238,246,247));cv.paste(im,((size[0]-im.width)//2,(size[1]-im.height)//2));return cv

def four_board():
 W,H=2600,1780
 im=Image.new('RGB',(W,H),'#F4F8F7');d=ImageDraw.Draw(im)
 d.text((58,34),'苑裡政策島｜四座政策主題建築・同源 3D 設計',font=font(54,True),fill='#163943')
 d.text((60,105),'B / D / E / H　│　主體幾何、實際島體尺度、候選 4.8 步道一併檢查',font=font(25),fill='#5F7983')
 cardw=1210;cardh=735;gap=45
 for i,c in enumerate('BDEH'):
  x=58+(i%2)*(cardw+gap);y=165+(i//2)*(cardh+35)
  rounded(d,(x,y,x+cardw,y+cardh),'#FFFFFF')
  d.rounded_rectangle((x+24,y+24,x+91,y+90),12,fill=COL[c])
  d.text((x+43,y+31),c,font=font(39,True),fill='white')
  name,tag,blurb=TEXT[c]
  d.text((x+108,y+24),name+'  '+tag,font=font(31,True),fill='#1B3B41')
  d.text((x+110,y+71),'基地：'+SIZES[c]+' 單位｜與 R20 不同的政策導向主體',font=font(19),fill='#71868A')
  im.paste(imgfit(ROOT/'renders'/f'{c}_hero.png',(780,530)),(x+24,y+115))
  im.paste(imgfit(ROOT/'renders'/f'{c}_top.png',(375,252)),(x+809,y+115))
  im.paste(imgfit(ROOT/'renders'/f'{c}_front.png',(375,252)),(x+809,y+392))
  d.text((x+805,y+369),'俯視（同一幾何）',font=font(18),fill='#48626A')
  d.text((x+805,y+646),'正立面（同一幾何）',font=font(18),fill='#48626A')
  d.text((x+28,y+668),blurb,font=font(19),fill='#3D5960')
 d.text((60,H-62),'驗證範圍：真實 GLB／同源多視圖／離線候選道路；未宣稱 Blender 正式工程、Three.js 手機或實機 FPS 已驗證。',font=font(20),fill='#5A737A')
 p=ROOT/'renders'/'BDEH_四島主題設計_自我審查板.png';im.save(p,optimize=True);return p

def single_board(c):
 W,H=2060,1500
 im=Image.new('RGB',(W,H),'#F4F8F7');d=ImageDraw.Draw(im)
 name,tag,desc=TEXT[c]
 d.text((50,20),f'{c}｜{name}  {tag}',font=font(48,True),fill='#1B3B41')
 d.text((52,88),'實際模型六視圖・同源渲染　｜　候選建築設計，非遊戲畫面',font=font(22),fill='#647E84')
 view=[('hero','45° 主視'),('front','正面'),('back','背面'),('left','左側'),('right','右側'),('top','俯視')]
 for i,(v,label) in enumerate(view):
  x=48+(i%3)*660;y=155+(i//3)*635
  rounded(d,(x,y,x+640,y+605),'#FFFFFF',r=18)
  d.text((x+20,y+14),label,font=font(28,True),fill='#284A55')
  im.paste(imgfit(ROOT/'renders'/f'{c}_{v}.png',(600,535)),(x+20,y+56))
 d.text((55,1436),'設計約束：'+SIZES[c]+' 單位｜4.8 單位步道；最終碰撞、NPC 與真實手機視角須於遊戲確認。',font=font(22),fill='#526D74')
 p=ROOT/'renders'/f'{c}_真實六視圖_候選.png';im.save(p,optimize=True);return p

def mapplan():
 js=json.loads((ROOT/'base/BDEH_R18/data/road-candidate-r2.json').read_text())
 sz={'B':(30,28),'D':(32,29),'E':(34,31),'H':(33,30)}
 from matplotlib import font_manager as fm
 fm.fontManager.addfont(FONT)
 plt.rcParams['font.family']=fm.FontProperties(fname=FONT).get_name()
 fig,ax=plt.subplots(figsize=(11,8.3),dpi=180)
 fig.set_facecolor('#F8FBFA');ax.set_facecolor('#F8FBFA')
 for e in js['allRoutesProposed']:
  P=np.array(e['proposedControlPointsXZ'],float);t=np.linspace(0,1,280)[:,None]
  if len(P)==4:Q=(1-t)**3*P[0]+3*(1-t)**2*t*P[1]+3*(1-t)*t**2*P[2]+t**3*P[3]
  else:Q=P[0][None,:]*(1-t)+P[-1][None,:]*t
  ax.plot(Q[:,0],Q[:,1],color='#879B9E',lw=4,alpha=.7,zorder=1)
  k=int(len(Q)*.52)
  ax.text(Q[k,0],Q[k,1],e['id'],fontsize=7,color='#456A73',ha='center',va='center',bbox=dict(facecolor='#F8FBFA',edgecolor='none',pad=.8),zorder=4)
 for c,node in js['nodes'].items():
  if c not in list('ABCDEFGH'):continue
  x,z=node
  if c in sz:
   w,h=sz[c];col=COL[c];alpha=.18
  else:w,h=(26,23) if c!='G' else (38.8,34.5);col='#7692A1';alpha=.13
  ax.add_patch(Ellipse((x,z),w,h,facecolor=col,edgecolor=col,lw=1.5,alpha=.65 if c in sz else .35,zorder=2))
  ax.text(x,z,c,ha='center',va='center',color='#173C49',fontsize=14,fontweight='bold',zorder=5)
 t4=js['nodes']['T4'];ax.scatter([t4[0]],[t4[1]],s=110,c='#E48A44',zorder=6)
 ax.annotate('T4 右移 (51, -47)\nS06 左斜線',xy=t4,xytext=(31,-58),fontsize=8,color='#A65D28',arrowprops=dict(arrowstyle='->',color='#A65D28'))
 ax.set_aspect('equal');ax.set_xlim(-94,82);ax.set_ylim(-66,119)
 ax.grid(True,alpha=.12);ax.set_xlabel('X  遊戲單位');ax.set_ylabel('Z  遊戲單位')
 ax.set_title('「苑」字 22 段 Bezier 路網與四島候選尺寸｜不代表正式部署地圖',fontsize=13,pad=18)
 plt.tight_layout();p=ROOT/'renders'/'苑字路網_四島候選配置.png';fig.savefig(p,facecolor=fig.get_facecolor());plt.close(fig);return p

if __name__=='__main__':
 print(four_board());print(mapplan())
 for c in 'BDEH':print(single_board(c))
