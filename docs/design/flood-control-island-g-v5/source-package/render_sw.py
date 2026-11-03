import json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import trimesh
R=Path('/mnt/data/G_V5_work')
from time import time
from numba import njit
scene=trimesh.load(R/'G_V5_hydraulic_campus_design.glb',force='scene')
assert isinstance(scene,trimesh.Scene)
meshes=[]
for key in scene.geometry:
 g=scene.geometry[key]
 if not isinstance(g,trimesh.Trimesh):continue
 meshes.append(g)
print('faces',sum(len(g.faces) for g in meshes))
allverts=np.vstack([m.vertices for m in meshes]);allfaces=np.vstack([m.faces+offset for m,offset in zip(meshes,np.cumsum([0]+[len(x.vertices) for x in meshes])[:-1])]); allcolors=np.vstack([m.visual.face_colors[:,:3] for m in meshes])
assert len(allfaces)==len(allcolors)
F=lambda s:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',s)
views={'hero':([-39,32,43],[0,2,0],18.8), 'back_iso':([41,29,41],[0,2,0],21.5), 'front':([0,16,-59],[0,2,0],23.6),'back':([0,16,59],[0,2,0],23.6), 'left':([-59,16,0],[0,2,0],23.6), 'right':([59,16,0],[0,2,0],23.6),'top':([0.001,65,0],[0,0,0],22.8),'near_dam':([-28,20,-32],[-8,4,6],12.5),'near_command':([27,18,-27],[9,3,4],12.2)}

@njit(cache=True)
def draw_zbuffer(screen,tri,dist,col):
 H,W,_=screen.shape
 zbuf=np.full((H,W),1.e20,dtype=np.float64)
 for i in range(len(tri)):
  x0,y0=tri[i,0];x1,y1=tri[i,1];x2,y2=tri[i,2]
  det=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2)
  if abs(det)<1.e-5:continue
  left=max(0,int(math.floor(min(x0,x1,x2))));right=min(W-1,int(math.ceil(max(x0,x1,x2))))
  top=max(0,int(math.floor(min(y0,y1,y2))));bottom=min(H-1,int(math.ceil(max(y0,y1,y2))))
  if left>right or top>bottom:continue
  for yy in range(top,bottom+1):
   py=yy+.5
   for xx in range(left,right+1):
    px=xx+.5
    a=((y1-y2)*(px-x2)+(x2-x1)*(py-y2))/det
    if a<0 or a>1:continue
    b=((y2-y0)*(px-x2)+(x0-x2)*(py-y2))/det
    if b<0 or a+b>1:continue
    c=1-a-b
    depth=a*dist[i,0]+b*dist[i,1]+c*dist[i,2]
    if depth<zbuf[yy,xx]:
     zbuf[yy,xx]=depth
     for k in range(3):screen[yy,xx,k]=col[i,k]
 return screen

def render(name,geo=None):
 cam,look,sca=views[name]; cam=np.array(cam,float);look=np.array(look,float); forward=(look-cam);forward=forward/np.linalg.norm(forward)
 worldup=np.array([0,0,-1]) if name=='top' else np.array([0,1,0]);right=np.cross(forward,worldup);right=right/np.linalg.norm(right);up=np.cross(right,forward)
 v=allverts if geo is None else geo[0];f=allfaces if geo is None else geo[1];col=allcolors if geo is None else geo[2]
 W,H=1584,992;px_per_world=H/(sca*2);
 # project
 d=v-look
 ux=d@right;uy=d@up;depth=(v-cam)@forward
 projected=np.stack((W*.5+ux*px_per_world,H*.52-uy*px_per_world),axis=1)
 tri=projected[f]; dist=depth[f].mean(axis=1)
 v3=v[f];norm=np.cross(v3[:,1]-v3[:,0],v3[:,2]-v3[:,0]);nl=np.linalg.norm(norm,axis=1);norm/=np.maximum(nl[:,None],1e-6)
 light=np.array([-.42,.80,-.43]);light/=np.linalg.norm(light)
 nd=np.abs(norm@light)
 shade=np.clip(.72+nd*.31,.5,1.05)
 color=np.clip(col*shade[:,None],0,255).astype('uint8')
 order=np.argsort(-dist)
 # bg gradient
 top=np.array([250,240,229],dtype='uint8');bottom=np.array([179,206,219],dtype='uint8')
 ar=np.empty((H,W,3),dtype=np.uint8)
 for y in range(H):
  t=y/H;ar[y,:,:]=np.clip(top*(1-t)+bottom*t,0,255)
 ar=draw_zbuffer(ar,np.ascontiguousarray(tri),np.ascontiguousarray(depth[f]),np.ascontiguousarray(color))
 im=Image.fromarray(ar,'RGB')
 # frame
 im=im.resize((1400,876),Image.Resampling.LANCZOS)
 out=R/f'G_V5_{name}.png';im.save(out,optimize=True)
 print(name,'view render',out.stat().st_size)
for v in views:render(v)
labels={'hero':'45° 主視','back_iso':'反側45°','front':'正面','back':'背面','left':'左側','right':'右側','top':'俯視','near_dam':'水閘近景','near_command':'指揮中心近景'}
def board(title,names,out,cols=3):
 W=1512;cw=(W-72-(cols-1)*20)//cols;ch=int(cw*.77)+52;rows=math.ceil(len(names)/cols)
 im=Image.new('RGB',(W,112+rows*(ch+22)),(244,245,242));d=ImageDraw.Draw(im)
 d.text((31,17),title,font=F(32),fill=(35,54,63));d.text((32,69),'以同一份 GLB 檔案的真實幾何產生｜施工方案，非 Sky Isles 遊戲截圖',font=F(16),fill=(85,99,105))
 for i,name in enumerate(names):
  x=30+(i%cols)*(cw+20);y=108+(i//cols)*(ch+22)
  d.rounded_rectangle((x,y,x+cw,y+ch),radius=11,fill=(255,255,255),outline=(215,219,214),width=2)
  d.text((x+12,y+8),labels[name],font=F(19),fill=(40,58,68))
  img=Image.open(R/f'G_V5_{name}.png').convert('RGB');img.thumbnail((cw-12,ch-48))
  im.paste(img,(x+(cw-img.width)//2,y+42))
 im.save(R/out,quality=92)
board('G｜治水防災 V5　同源六視圖',['hero','front','back','left','right','top'],'G_V5_six_views.jpg')
board('G｜治水防災 V5　工程設施與量體細節',['hero','back_iso','near_dam','near_command','top'],'G_V5_design_board.jpg')
