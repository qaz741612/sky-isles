"""Assemble unaltered actual captures; never render or invent scene pixels."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).resolve().parents[2];O=R/'docs/previews/bdeh-r21/final-qa';P=O/'comparisons';P.mkdir(exist_ok=True)
def board(paths,labels,target,cell=(400,330),columns=2):
 w,h=cell;out=Image.new('RGB',(w*columns,(len(paths)+columns-1)//columns*(h+30)),'#eef0ed');draw=ImageDraw.Draw(out)
 for i,(path,label)in enumerate(zip(paths,labels)):
  with Image.open(path)as im:im=ImageOps.contain(im.convert('RGB'),(w,h));x=(i%columns)*w;y=(i//columns)*(h+30);out.paste(im,(x+(w-im.width)//2,y+30+(h-im.height)//2));draw.text((x+8,y+8),label,fill='#203d42')
 out.save(target)
for code in'BDEH':
 views=['hero','front','back','left','right','top','architecture','public-space']
 board([O/code/'blender'/f'{v}.png'for v in views],[code+' Blender '+v for v in views],P/f'{code}-blender-eight.jpg',(400,300),4)
 for profile in['desktop','portrait','landscape']:
  kinds=['native','single-finger-left','single-finger-right','NPC-native'];paths=[];labels=[]
  for kind in kinds:
   for stage in['before','after']:paths.append(O/f'game-{stage}'/f'{code}-{profile}-{kind}.png');labels.append(f'{code} {profile} {kind} {stage}')
  board(paths,labels,P/f'{code}-{profile}-before-after.jpg',(300,650)if profile=='portrait'else(600,400),2)
board([O/c/'blender/hero.png'for c in'BDEH'],[c+' final Blender hero'for c in'BDEH'],P/'four-islands-blender.jpg',(560,420),2)
board([O/'game-after'/f'{c}-portrait-native.png'for c in'BDEH'],[c+' original portrait profile + local discovery'for c in'BDEH'],P/'four-islands-native-portrait.jpg',(280,607),4)
board([O/'game-after'/f'{c}-desktop-native.png'for c in'BDEH'],[c+' original desktop profile + local discovery'for c in'BDEH'],P/'four-islands-native-desktop.jpg',(560,375),2)
print('19 comparison/contact boards created from actual source PNGs')
