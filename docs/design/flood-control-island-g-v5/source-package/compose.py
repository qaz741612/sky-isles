from PIL import Image,ImageDraw,ImageFont,ImageChops
from pathlib import Path
import numpy as np, math
R=Path('/mnt/data/G_V5_work')
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def f(n):return ImageFont.truetype(FONT,n)
def crop3d(name):
    im=Image.open(R/f'G_V5_{name}.png').convert('RGB'); ar=np.asarray(im).astype(np.int16)
    ref=ar[:,3:4,:]
    d=np.max(np.abs(ar-ref),axis=2)
    ys,xs=np.where(d>22)
    if len(xs)<100:return im
    l,r=xs.min(),xs.max();t,b=ys.min(),ys.max()
    px=int((r-l)*.07);py=int((b-t)*.10)
    return im.crop((max(0,l-px),max(0,t-py),min(im.width,r+px),min(im.height,b+py)))
labels={'hero':'45° 實體主視圖','back_iso':'反側 45°','front':'正面','back':'背面','left':'左側','right':'右側','top':'俯視／配置','near_dam':'三道水閘近景','near_command':'指揮中心近景'}
def board(title,names,out,cols=3):
    W=1550;pad=26;gap=18;cw=(W-pad*2-gap*(cols-1))//cols;ch=400;rows=math.ceil(len(names)/cols)
    H=118+rows*(ch+20)+34
    im=Image.new('RGB',(W,H),(245,247,244));d=ImageDraw.Draw(im)
    d.text((pad,20),title,font=f(35),fill=(37,59,66))
    d.text((pad,75),'同一份實際 3D 幾何模型的多角度檢查｜圖像裁切放大，不是 AI 美圖或遊戲實景',font=f(17),fill=(107,117,120))
    for i,name in enumerate(names):
        x=pad+(i%cols)*(cw+gap);y=115+(i//cols)*(ch+20)
        d.rounded_rectangle((x,y,x+cw,y+ch),radius=11,fill=(255,255,255),outline=(217,224,221),width=2)
        d.text((x+14,y+11),labels[name],font=f(21),fill=(37,59,66))
        img=crop3d(name)
        img.thumbnail((cw-14,ch-55),Image.Resampling.LANCZOS)
        im.paste(img,(x+(cw-img.width)//2,y+49+(ch-55-img.height)//2))
    im.save(R/out,quality=92)
board('G｜治水防災 V5　同源六視圖', ['hero','front','back','left','right','top'],'G_V5_six_views.jpg')
board('G｜治水防災 V5　工程建築細部審視',['hero','back_iso','near_dam','near_command','top'],'G_V5_design_board.jpg')
# create a tightly cropped principal and detail stills for convenience
for name in ['hero','near_dam','near_command']:
 im=crop3d(name);im.save(R/f'G_V5_{name}_focus.png')
