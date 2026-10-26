"""Stage-two comparative metrics and inspection media; only actual Blender render sources. MIT."""
from pathlib import Path
import json,math,hashlib,subprocess,zipfile
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2];OLD=ROOT/'docs/design/parent-child-blender-model-v1';OUT=ROOT/'docs/design/parent-child-blender-refinement-v2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((OLD/'model-report.json').read_text());new=json.loads((OUT/'model-report.json').read_text());before=json.loads((OLD/'three-loading-report.json').read_text());after=json.loads((OUT/'three-loading-report.json').read_text());cfg=json.loads((OUT/'layout.json').read_text())
def diff(a,b):return {'before':a,'after':b,'difference':b-a,'percent':round((b/a-1)*100,3)}
metrics={'dimensionsOrder':'Blender source XYZ = width/depth/height; Three.js GLB XYZ = width/height/depth','standaloneSiteRadius':diff(cfg['previousRadius'],cfg['siteRadius']),'circularSiteArea':diff(math.pi*cfg['previousRadius']**2,math.pi*cfg['siteRadius']**2),'sourceEvaluatedTriangles':diff(old['triangles'],new['triangles']),'glbTriangles':diff(before['triangles'],after['triangles']),'editableMeshObjects':diff(old['meshObjects'],new['meshObjects']),'glbMeshBatches':diff(before['meshes'],after['meshes']),'glbBytes':diff(before['bytes'],after['bytes']),'sourceSizeXYZ':{'before':old['sizeXYZ'],'after':new['sizeXYZ']},'glbMaterials':diff(before['materials'],after['materials']),'sourceBlendSHA256':{'before':sha(OLD/'parent-child-centre.blend'),'after':sha(OUT/'parent-child-centre.blend')},'materials':{'glassRoughness':diff(.14,.045),'glassTransmission':diff(.82,1),'roofSeamNominalSpacing':diff(.43,1.1)},'note':'Whole isolated model, including standalone plinth and four bridge stubs. No game map size changes. Rendering triangle counts with transmission passes are separate from model triangle count.'}
(OUT/'metrics-comparison.json').write_text(json.dumps(metrics,indent=2)+'\n')
font_path=subprocess.check_output(['fc-match','-f','%{file}','Noto Sans CJK TC'],text=True).strip();font=ImageFont.truetype(font_path,27);small=ImageFont.truetype(font_path,20)
# Useful even before all render jobs finish: plan is derived from the final model-space audit.
try:
 from shapely.geometry import shape,Point,LineString,Polygon
 from shapely.ops import unary_union
 components=json.loads((OUT/'space-footprints.json').read_text())['components'];obstacles=unary_union([shape(c['footprint'])for c in components]);R=cfg['siteRadius'];site=Point(0,0).buffer(R,quad_segs=128)
 for gate in json.loads((OLD/'layout.json').read_text())['bridgeStubs']:
  a=math.radians(gate['angle']);d=(math.cos(a),math.sin(a));t=(-d[1],d[0]);w=gate['width'];start=math.sqrt(R*R-(w/2)**2)-.05;end=start+gate['length'];site=site.union(Polygon([(d[0]*r+t[0]*s,d[1]*r+t[1]*s)for r,s in [(start,-w/2),(end,-w/2),(end,w/2),(start,w/2)]]))
 walk=site.buffer(-.35).difference(obstacles.buffer(.35));anchor=Point(cfg['npcReservation']['playerApproach'][:2]);regions=list(walk.geoms)if hasattr(walk,'geoms')else[walk];connected=next(g for g in regions if g.covers(anchor))
 size=(1600,1500);image=Image.new('RGB',size,'#f5f2e9');draw=ImageDraw.Draw(image);factor=49;origin=(800,700)
 def xy(p):return(origin[0]+p[0]*factor,origin[1]-p[1]*factor)
 def paint(g,fill,outline=None):
  if g.is_empty:return
  if g.geom_type=='Polygon':
   draw.polygon([xy(p)for p in g.exterior.coords],fill=fill,outline=outline)
   for h in g.interiors:draw.polygon([xy(p)for p in h.coords],fill='#f5f2e9')
  elif hasattr(g,'geoms'):
   for part in g.geoms:paint(part,fill,outline)
 paint(site,'#e0dcd2','#7e8782');paint(connected,'#d4e7ca');paint(obstacles,'#9ca5a0')
 colours=['#348791','#af8052','#497b57','#bf795a']
 for route,colour in zip(cfg['routes'],colours):
  line=LineString(route['points']);paint(line.buffer(.6,cap_style=2),colour)
  pts=[xy(p)for p in route['points']];draw.line(pts,fill='#fff9e9',width=3);x,y=pts[0];draw.ellipse((x-9,y-9,x+9,y+9),fill=colour,outline='white',width=2)
  labels={'west':'西入口','southwest':'西南入口','south':'南入口','east':'東入口'};dx=-85 if route['id']=='east'else 10;draw.text((x+dx,y+12),labels[route['id']],font=small,fill='#29494c')
 npc=cfg['npcReservation'];nx,ny=xy(npc['position']);r=npc['activityRadius']*factor;draw.ellipse((nx-r,ny-r,nx+r,ny+r),fill='#efd491',outline='#89683a',width=3);draw.text((nx+36,ny-7),'NPC 預留區',font=small,fill='#6b512d')
 px,py=xy(npc['playerApproach']);r=.35*factor;draw.ellipse((px-r,py-r,px+r,py+r),fill='#edece7',outline='#324d64',width=3);draw.text((px+27,py+10),'玩家接近點',font=small,fill='#324d64')
 draw.text((40,25),'玩家與 NPC 可行走空間｜實際模型幾何平面稽核',font=font,fill='#29494c')
 for i,text in enumerate(['淺綠：直徑 0.70 的玩家中心可達室外區；深灰：身體高度 0.22–1.78 的實體投影。','四色帶：四入口至門廊的 1.2 寬規劃通道；金色：NPC 活動半徑 0.65。','建築玻璃門保持關閉；路線止於門廊，不宣稱可穿過門或已完成遊戲物理。','保守包絡稽核；不是無障礙法規認證，未模擬跳躍、移動相機或動態人物。']):draw.text((40,1320+i*35),text,font=small,fill='#465f5c')
 draw.line((70,1260,70+2*factor,1260),fill='#29494c',width=5);draw.text((70,1270),'2 建模單位',font=small,fill='#29494c')
 image.save(OUT/'walkable-space.png');(OUT/'walkable-space.json').write_text(json.dumps({'connectedOutdoorPlayerCentreArea':connected.area,'playerAuditRadius':.35,'gamePlayerRadiusForReference':.33,'headHeightSlab':[.22,1.78],'note':'Conservative plan-space design audit only; no live-game integration.'},indent=2)+'\n')
except ImportError:print('Install isolated shapely to produce measured plan diagram');raise
# All remaining outputs require final eight renders and both matched-framing before renders.
if not(OUT/'before-render-record.json').exists()or not(OUT/'render-record.json').exists():print('Metrics and walkable plan ready; waiting for render sources.');raise SystemExit(0)
newviews=json.loads((OUT/'render-record.json').read_text())['views'];oldviews=json.loads((OUT/'before-render-record.json').read_text())['views']
if len(newviews)!=8 or len(oldviews)!=2:print('Waiting for all eight final and two before views.');raise SystemExit(0)
originalViews=json.loads((OLD/'render-record.json').read_text())['views']
for rec in newviews:
 original=next(r for r in originalViews if r['camera']==rec['camera'])
 for key in ['cameraPositionXYZ','cameraRotationRadians']:
  assert all(abs(a-b)<1e-5 for a,b in zip(original[key],rec[key]))
 assert abs(original['lensMM']-rec['lensMM'])<1e-5
 assert rec['sourceBlendSHA256']==metrics['sourceBlendSHA256']['after'];assert rec['imageSHA256']==sha(OUT/rec['file'])
for rec in oldviews:
 assert rec['sourceBlendSHA256']==metrics['sourceBlendSHA256']['before'];assert rec['imageSHA256']==sha(OUT/rec['file'])
 matched=next(r for r in newviews if Path(r['file']).stem==Path(rec['file']).stem)
 for key in ['cameraPositionXYZ','cameraRotationRadians','orthoScale','size']:assert all(abs(a-b)<1e-5 for a,b in zip(rec[key],matched[key]))if isinstance(rec[key],list)else abs(rec[key]-matched[key])<1e-5
space=json.loads((OUT/'space-audit.json').read_text());solid=json.loads((OUT/'solid-geometry-audit.json').read_text());web=json.loads((OUT/'three-webgl-validation.json').read_text());lineage=json.loads((OUT/'lineage-audit.json').read_text())
assert space['sourceBlendSHA256']==metrics['sourceBlendSHA256']['after'] and solid['sourceBlendSHA256']==metrics['sourceBlendSHA256']['after']
assert space['allRoutesPlayerClear'] and not space['npcActivityOverlappingRoutes'] and space['npcReservation']['clear'] and not solid['issues']
assert not after['khronosErrors'] and not after['missingMaterials'] and not web['webglError'] and not web['pageErrors'] and lineage['entranceGeometryUnchanged']
assert after['bytes']==(OUT/'parent-child-centre.glb').stat().st_size
(OUT/'quality-gates.json').write_text(json.dumps({'allEightCamerasRetainOriginalPositionsAnglesAndLenses':True,'allEightRendersFromFinalBlend':True,'twoMatchedFramingBeforeAfterComparisons':True,'fourRoutesPlayerClear':True,'fourRoutesCorridorsWithoutObstacleOverlap':all(r['corridorOverlapArea']<.0001 for r in space['routes']),'npcReservationClearOfGeometryAndRoutes':True,'retainedEntranceGeometryIdentical':True,'solidGeometryIssues':0,'khronosErrors':after['khronosErrors'],'khronosWarnings':after['khronosWarnings'],'threeWebglError':web['webglError'],'sourceBlendSHA256':metrics['sourceBlendSHA256']['after'],'note':'Engineering and artifact checks only; not an artistic pass, live-game collision certification or real-device performance result.'},indent=2)+'\n')
for name in ['hero','top']:
 a=Image.open(OUT/'before'/(name+'.png')).convert('RGB');b=Image.open(OUT/'renders'/(name+'.png')).convert('RGB');assert a.size==b.size
 canvas=Image.new('RGB',(a.width*2,a.height+70),'#f5f2e9');d=ImageDraw.Draw(canvas);d.text((24,15),'修改前｜PR #11，半徑 9.2',font=font,fill='#29494c');d.text((a.width+24,15),'第二階段精修｜半徑 10.2',font=font,fill='#29494c');canvas.paste(a,(0,70));canvas.paste(b,(a.width,70));canvas.save(OUT/('comparison-'+name+'.png'))
names=[('hero','主視角'),('front','正面'),('back','背面'),('left','左側'),('right','右側'),('top','正上方'),('eaves','屋簷與構件'),('player','1.65m 玩家視線')]
contact=Image.new('RGB',(1600,636),'#f5f2e9');d=ImageDraw.Draw(contact)
for i,(name,label)in enumerate(names):
 im=Image.open(OUT/'renders'/(name+'.png')).convert('RGB');im.thumbnail((392,270),Image.Resampling.LANCZOS);x=(i%4)*400+(400-im.width)//2;y=(i//4)*318+5;contact.paste(im,(x,y));d.text(((i%4)*400+14,(i//4)*318+282),label,font=small,fill='#29494c')
contact.save(OUT/'eight-views.png')
files=[]
for p in [OUT/'parent-child-centre.blend',OUT/'parent-child-centre.glb',*sorted(OUT.rglob('*.png'))]:
 item={'path':str(p.relative_to(OUT)),'bytes':p.stat().st_size,'sha256':sha(p),'kind':('actual Blender Cycles render' if p.parent.name in ['renders','before'] else 'actual Three.js WebGL screenshot' if p.name.startswith('three-webgl') else 'measured geometry planning diagram' if p.name=='walkable-space.png' else 'actual-render composite' if p.suffix=='.png' else 'editable or exchange 3D model')}
 if p.suffix=='.png':
  with Image.open(p)as im:item.update(width=im.width,height=im.height)
 files.append(item)
(OUT/'media-manifest.json').write_text(json.dumps({'sourceBlendSHA256':metrics['sourceBlendSHA256']['after'],'files':files},indent=2)+'\n');(OUT/'SHA256SUMS').write_text(''.join(f['sha256']+'  '+f['path']+'\n'for f in files))
with zipfile.ZipFile(OUT/'parent-child-refinement-review.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6)as bundle:
 for p in sorted(OUT.rglob('*')):
  if p.is_file()and p.suffix!='.zip'and p.name not in ['github-verification.json','bundle-manifest.json','DELIVERY.md']:bundle.write(p,str(p.relative_to(OUT)))
 bundle.write(ROOT/'LICENSE','LICENSE')
p=OUT/'parent-child-refinement-review.zip';(OUT/'bundle-manifest.json').write_text(json.dumps({'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'kind':'ZIP review bundle'},indent=2)+'\n');print(json.dumps({'eightFinalViews':8,'matchedBeforeViews':2,'comparisons':2,'manifestFiles':len(files),'bundleBytes':p.stat().st_size}))
