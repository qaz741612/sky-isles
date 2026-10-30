import os, math, json, hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['font.family']='Noto Sans CJK TC'
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon as PolyPatch, Rectangle, Circle
from shapely.geometry import Polygon, Point, LineString
from build_industry_c_v2 import scene,core,foot,roads,ports,road_centerlines
OUT=Path(__file__).resolve().parent
font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
font_b='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
if not Path(font).exists():
 import subprocess
 font=subprocess.check_output('fc-match -f "%{file}" "Noto Sans CJK TC"',shell=True,text=True).strip(); font_b=font
ZH=FontProperties(fname=font);ZHB=FontProperties(fname=font_b)

def f(size,b=False):return ImageFont.truetype(font_b if b else font,size)
NAVY='#143D48';CYAN='#146b70';TEAL='#286C69';COPPER='#BC8350';BEIGE='#F5F1E9';GRAY='#53676A'
# Exact source geometry plan
fig,ax=plt.subplots(figsize=(11,10),dpi=180);fig.patch.set_facecolor('#F6F4EF');ax.set_facecolor('#F6F4EF')
def paint(poly,col,alpha=1,z=1,edge=None,lw=1):
 for p in (list(poly.geoms) if hasattr(poly,'geoms') else [poly]):
  if p.is_empty or not isinstance(p,Polygon):continue
  xx,yy=p.exterior.xy;ax.fill(xx,yy,color=col,alpha=alpha,zorder=z,ec=edge,lw=lw)
paint(foot,'#AFC9B3',z=1,edge='#355C51',lw=1.8)
paint(core.intersection(foot),'#E7DEC7',z=2)
paint(Point(-1,1.1).buffer(4.9), '#EAE5D9',z=2.3)
paint(Point(-1,1.1).buffer(4.5).difference(Point(-1,1.1).buffer(4.2)), '#C6A67A',z=2.6)
# old island dashed circle
ang=np.linspace(0,2*np.pi,200)
ax.plot(9*np.cos(ang),9*np.sin(ang),ls='--',lw=1.3,color='#76988B',alpha=.62,zorder=2)
# buildings: actual main geometry after shift
buildings={'三段鋸齒屋頂工坊':(4.88,-2.05,12.99,4.07,'#B87D58'),'弧形農業科技溫室':(4.14,5.11,9.85,8.99,'#76AFB3'),'青年創新展廊':(-10.68,-.45,-6.72,3.15,'#CEAD7A')}
for title,(x0,z0,x1,z1,col) in buildings.items():
 ax.add_patch(Rectangle((x0,z0),x1-x0,z1-z0,facecolor=col,edgecolor='#345660',lw=1.5,alpha=.93,zorder=5))
 if title=='三段鋸齒屋頂工坊':
  for zz in [-1.9,0.05,2.05]:ax.plot([5.05,12.7],[zz,zz],color='#F3D7A4',lw=3,zorder=6)
 elif title=='弧形農業科技溫室':
  for xx in np.linspace(x0,x1,7):ax.plot([xx,xx],[z0,z1],color='#E7F9EF',lw=1.1,zorder=6)
 ax.text((x0+x1)/2,(z0+z1)/2,title,color='white' if col=='#B87D58' else '#164653',fontsize=11,fontproperties=ZHB,ha='center',va='center',zorder=8)
# entrance directions, actual curves
for label,pts in road_centerlines.items():
 a=np.asarray(pts)
 ax.plot(a[:,0],a[:,1],color='#3A7883',lw=1.7,ls='--',alpha=.7,zorder=7)
 if label in ('S14','S15'):outer=a[0]
 else:outer=a[-1]
 xy={'S14':(-15.8,-14.2),'S15':(15.0,-14.2),'S16':(-13.8,15.1)}[label]
 ax.annotate(label+' 橋口',xy=outer,xytext=xy,textcoords='data',fontsize=12,color=NAVY,fontproperties=ZHB,zorder=10,
             arrowprops={'arrowstyle':'-|>','color':CYAN,'lw':1.4},ha='center',va='center',
             bbox={'boxstyle':'round,pad=.3','fc':'#F5F1E9','ec':'#B5CECA','lw':1.1})
# placement of preserved interactive elements
npc=Rectangle((-1,6.85),3,3,linewidth=2,edgecolor='#D18A42',facecolor='#F5DAB0',alpha=.63,linestyle='--',zorder=7)
ax.add_patch(npc);ax.text(.5,9.4,'NPC 3×3',ha='center',va='center',fontsize=10,color='#884B23',fontproperties=ZHB,zorder=9)
ax.add_patch(Circle((3.056,3.438),.95,facecolor='#B8A6D6',edgecolor='#6B5489',lw=1.3,alpha=.88,zorder=8))
ax.text(3.056,3.438,'蘑菇',ha='center',va='center',fontsize=8,color='#4F3C68',fontproperties=ZH,zorder=9)
ax.text(-1,1.0,'產業共享廣場',ha='center',va='center',fontsize=12,color='#426662',fontproperties=ZHB,zorder=9)
ax.set_aspect('equal');ax.set_xlim(-19.8,19.2);ax.set_ylim(19,-18);ax.axis('off');fig.tight_layout(pad=.3)
fig.savefig(OUT/'10_exact_road_plan.png',dpi=180,facecolor='#F6F4EF');plt.close(fig)

# Premium 16:9 landscape board using genuine same-source shaded renderer captures
W,H=2000,1400;bg=Image.new('RGB',(W,H),'#F4F1EC');d=ImageDraw.Draw(bg)
d.rectangle((0,0,W,136),fill='#143D48')
d.text((56,27),'C 產業青年島',font=f(64,True),fill='#F9F5EF')
d.text((610,65),'同源實際 3D 設計  /  CONSTRUCTION GEOMETRY V2.2',font=f(27),fill='#A6D7CB')
d.rounded_rectangle((1735,35,1932,101),radius=22,fill='#DBAB74')
d.text((1755,50),'已自行修正',font=f(27,True),fill='#123641')
def paste_panel(img_path,xy,size,label,sub=None):
 x,y=xy;w,h=size
 if img_path.exists():
  im=Image.open(img_path).convert('RGB')
  iw,ih=im.size
  # contain rather than crop, original renders are centered and composition is true to 3D
  rs=min(w/iw,h/ih);im=im.resize((round(iw*rs),round(ih*rs)),Image.Resampling.LANCZOS)
  t=Image.new('RGB',(w,h),'#E7E9E5');t.paste(im,((w-im.width)//2,(h-im.height)//2));bg.paste(t,(x,y))
 d.rectangle((x,y,x+w,y+h),outline='#BED0CC',width=2)
 d.rounded_rectangle((x+18,y+13,x+18+min(len(label)*24+24,w-32),y+62),radius=12,fill='#173D47')
 d.text((x+31,y+21),label,font=f(25,True),fill='#FFFFFF')
 if sub:d.text((x+21,y+h-47),sub,font=f(22),fill='#4E6F74')
paste_panel(OUT/'01_hero.png',(40,161),(1246,823),'01｜45° 主視角')
paste_panel(OUT/'03_top.png',(1304,161),(656,401),'02｜正俯視')
paste_panel(OUT/'08_workshop_detail.png',(1304,583),(656,401),'03｜建築細部')
# bottom row for exact plan and notes
paste_panel(OUT/'10_exact_road_plan.png',(40,1001),(706,341),'04｜實際三橋口配置')
d.rounded_rectangle((766,1001,1961,1342),radius=12,fill='#FFFFFF',outline='#D4DDDA',width=2)
d.text((793,1020),'修正版設計重點',font=f(36,True),fill=NAVY)
for i,(head,desc) in enumerate([
 ('建築', '三組鋸齒屋頂、實體柱梁、採光立面、太陽能板'),
 ('科技農業', '弧形鋼構玻璃溫室、栽培架與內部植栽'),
 ('動線', 'S14／S15／S16 直接採 GitHub 真實曲線'),
 ('玩法', '原彈跳蘑菇保留；NPC 預留完整 3×3 空間'),
]):
 y=1083+i*59
 d.rounded_rectangle((792,y+5,798,y+35),radius=2,fill=COPPER)
 d.text((814,y),head,font=f(25,True),fill=CYAN)
 d.text((933,y),desc,font=f(24),fill=GRAY)
d.text((792,1317),'註：同源幾何設計參考；尚未完成 Sky Isles 正式碰撞、相機與真機效能驗收。',font=f(19),fill='#778688')
bg.save(OUT/'00_C_island_revised_design_board.png',optimize=True)
# 6-view panels (actual 3D render, no independent AI images)
views=[('01_hero.png','45° 主視角'),('03_top.png','俯視'),('04_north.png','北側'),('05_south.png','南側'),('06_west.png','西側'),('07_east.png','東側')]
TW,TH=1830,1540
contact=Image.new('RGB',(TW,TH),'#F5F3EE');dc=ImageDraw.Draw(contact)
dc.rectangle((0,0,TW,127),fill=NAVY)
dc.text((40,20),'C 產業青年｜同源六視圖',font=f(50,True),fill='#FFFFFF')
dc.text((960,64),'全部由同一份 GLB 幾何輸出・非 AI 合成',font=f(25),fill='#B3DCD6')
for i,(path,label) in enumerate(views):
 x=38+(i%2)*895;y=150+(i//2)*452;w,h=858,417
 im=Image.open(OUT/path).convert('RGB');r=min(w/im.width,h/im.height);im=im.resize((round(im.width*r),round(im.height*r)),Image.Resampling.LANCZOS)
 contact.paste(im,(x+(w-im.width)//2,y+(h-im.height)//2))
 dc.rectangle((x,y,x+w,y+h),outline='#CAD9D2',width=2)
 dc.rounded_rectangle((x+14,y+14,x+208,y+55),radius=10,fill=NAVY)
 dc.text((x+26,y+18),label,font=f(24,True),fill='white')
contact.save(OUT/'00_C_island_same_source_six_views.jpg',quality=92,optimize=True)
print('art board / six views done')
