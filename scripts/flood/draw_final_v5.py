"""Annotated engineering plan from final geometry, not a game screenshot."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[2];O=R/'docs/previews/flood-control-island-g-v5';p=json.loads((R/'src/data/flood-control-plan.json').read_text());s=json.loads((R/'src/data/flood-control-site.json').read_text());y=json.loads((R/'src/data/yuan-layout.json').read_text());c=json.loads((R/'src/data/flood-control-collision.json').read_text());font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';f=lambda n:ImageFont.truetype(font,n);im=Image.new('RGB',(1200,1100),'#f2f4f2');d=ImageDraw.Draw(im)
def q(v):return(600+v[0]*24,550+v[1]*24)
def domain(polys,color):
 for rings in polys:
  d.polygon([q(v)for v in rings[0]],fill=color)
  for hole in rings[1:]:d.polygon([q(v)for v in hole],fill='#b6d2d4')
d.text((35,20),'G V5｜最終空間與碰撞稽核平面',font=f(29),fill='#204649');d.text((35,62),'工程示意圖，非遊戲截圖。原道路中心線、玩家尺度、F/A/C 資產保留。',font=f(18),fill='#44656a')
outer=json.loads((R/'src/data/yuan-plan.json').read_text())['islandFootprintsXZ']['G'];cen=p['centre'];local=[(v[0]-cen[0],v[1]-cen[2])for v in outer];d.polygon([q(v)for v in local],fill='#dae3cb',outline='#51786f',width=3);domain(s['water'],'#6fb9c1');domain(s['floor'],'#e0e1d3');domain(s['paving'],'#d3c0a0')
for v in c['solids']:
 if 'polygon'in v and v['base']<1.6 and v['top']>0:d.polygon([q(pt)for pt in v['polygon']],fill='#708c90')
for v in s['waterRails']:d.line([q(v['a']),q(v['b'])],fill='#314f51',width=2)
for route in y['paths']:
 if route['id']in ['S20','S21','S22']:
  pts=[q([v['x']-cen[0],v['z']-cen[2]])for v in route['points']];d.line(pts,fill='#c47748',width=3)
  vis=[v for v in pts if 30<v[0]<1170 and 140<v[1]<980]
  if vis:d.text(vis[len(vis)//2],route['id'],font=f(22),fill='#8a411e')
for title,pt in [('三道大型閘門',[-12.5,6.6]),('防災指揮中心',[5.5,4]),('觀測室',[11,6.3]),('上游展示水域',[-13,1]),('下游滯洪水域',[-11,12]),('S22 乾式跨水橋',[-9,-4.3])]:d.text(q(pt),title,font=f(16),fill='#123f48',stroke_width=2,stroke_fill='#eff2eb')
x,_,z=p['npc'][0]['position'];d.rectangle([q([x-1.5,z-1.5]),q([x+1.5,z+1.5])],outline='#a55a50',width=3);d.text(q([7.8,-12]),'單一張顧礫 NPC 3×3 預留',font=f(17),fill='#984d42');d.line([q(pt)for pt in p['publicCircuit']],fill='#a3556c',width=3)
d.text((45,1000),'橘線：原道路中心線　紫線：實走公共動線　深線：水岸／跨水橋安全邊界',font=f(19),fill='#2f5357');d.text((45,1036),'S20 保守外緣淨距約 3.39｜水位差 1.14｜道路核心寬 4.8｜建築不開放室內',font=f(19),fill='#2f5357');im.save(O/'spatial-plan-final.png');print('G final geometry schematic saved')
