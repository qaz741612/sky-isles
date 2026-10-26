"""Original editable policy-island construction kit. MIT; reuses project primitive helpers.
No live game source is imported or modified. Blender coordinates: +Y rear, +Z up.
"""
import bpy, math, random, sys
from pathlib import Path
from mathutils import Vector
from shapely.geometry import Polygon, Point, LineString, box as sbox
from shapely.ops import triangulate, unary_union
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles, set_precision
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import parent_child_geometry as G
ROOT=Path(__file__).resolve().parents[3]
BASELINE=ROOT/'docs/design/parent-child-blender-refinement-v2/parent-child-centre.blend'

class Kit:
 def __init__(self,key):
  bpy.ops.wm.read_factory_settings(use_empty=True);G._ico_cache.clear();random.seed(741612)
  self.key=key;self.rooms=[];self.exclusions=[];self.paths=[];self.reservations=[];self.water_shapes=[]
  wanted=['cream','stone','trim','roof','seam','wood','woodLight','woodDark','rail','leaf','leafLight','leafDark','soil','sand','coral','slide','petal','petalPink','greenCloth','tealCloth','floor','gray','Clear warm architectural glazing']
  with bpy.data.libraries.load(str(BASELINE),link=False)as(src,dst):dst.materials=[n for n in wanted if n in src.materials]
  self.M={n:bpy.data.materials[n]for n in wanted};self.M['glass']=self.M['Clear warm architectural glazing']
  self.M['trainGlass']=G.material('Smoked vehicle glazing','47747B',.18,.05,.15)
  self.M['grass']=G.material('Meadow lawn','A8BE79',.95)
  self.M['water']=G.material('Clear turquoise water','80C5CD',.16,0,.30)
  self.M['white']=G.material('Soft white markings','F4EEDC',.70)
  self.M['courtBlue']=G.material('Muted blue court','86AEB6',.87)
  self.M['courtCoral']=G.material('Muted clay court','DCA790',.88)
  self.M['pathSage']=G.material('Soft sage stone inlay','CFDCC7',.85)
  self.M['pathPeach']=G.material('Warm peach stone inlay','E7D3BA',.85)
  G.collection('00_ASSET_ROOT');self.root=G.empty(key+'_MODEL');self.root['role']='Standalone editable artwork; NOT live-game integration';self.root['units']='World-scale metres, Z up';self.groups={}
  for n in ['Architecture','Interior','Landscape','Furniture','ThemeFacilities','Site']:
   G.collection(n);self.groups[n]=G.empty(n,self.root)
  self.use('Architecture')
 def use(self,n):G.COL=bpy.data.collections[n];self.parent=self.groups[n];return self.parent
 def group(self,n,parent=None):return G.empty(n,parent or self.parent)
 def box(self,n,p,d,m='cream',parent=None,r=.025):return G.box(n,p,d,self.M[m],parent or self.parent,r)
 def beam(self,n,a,b,w=.06,m='wood',parent=None):return G.beam(n,a,b,w,self.M[m],parent or self.parent)
 def cyl(self,n,p,r,d,m='cream',parent=None,v=32):return G.cylinder(n,p,r,d,self.M[m],parent or self.parent,v)
 def sphere(self,n,p,scale,m='leaf',parent=None,sub=2):return G.sphere(n,p,scale,self.M[m],parent or self.parent,sub)
 def tube(self,n,points,r=.025,m='rail',parent=None,sides=8):return G.tube(n,points,r,self.M[m],parent or self.parent,sides)
 def solid(self,n,poly,z,h,m='stone',parent=None,bev=0):
  poly=set_precision(poly,1e-5)
  if poly.is_empty:return None
  if poly.geom_type=='MultiPolygon':
   return [self.solid(n,p,z,h,m,parent,bev)for p in poly.geoms if p.area>.0001]
  poly=orient(poly,1);verts=[];faces=[];lookup={}
  def idx(x,y,zz):
   key=(round(x,7),round(y,7),round(zz,7))
   if key not in lookup:lookup[key]=len(verts);verts.append(key)
   return lookup[key]
  for tri in constrained_delaunay_triangles(poly).geoms:
   if not poly.covers(tri):continue
   pts=list(orient(tri,1).exterior.coords)[:3];faces.append(tuple(idx(x,y,z+h)for x,y in pts));faces.append(tuple(idx(x,y,z)for x,y in reversed(pts)))
  for ring in [poly.exterior,*poly.interiors]:
   pts=list(ring.coords)
   for (x,y),(xx,yy)in zip(pts,pts[1:]):faces.append((idx(x,y,z),idx(xx,yy,z),idx(xx,yy,z+h),idx(x,y,z+h)))
  o=G.mesh(n,verts,faces,self.M[m],parent or self.parent)
  if bev:G.bevel(o,bev,2)
  return o
 def arc(self,n,x,y,r0,r1,z,h,m='woodLight',parent=None,start=0,end=math.tau,steps=64):return G.ring(n,(x,y),r0,r1,z,h,self.M[m],parent or self.parent,steps,start,end)
 def roof(self,n,x0,x1,y0,y1,left=3.0,right=3.0,rise=.7,parent=None):
  p=parent or self.parent;G.roof(n,x0,x1,y0,y1,left,right,rise,.16,[self.M['roof'],self.M['cream'],self.M['trim']],p)
  f=lambda x:G.profile(x,x0,x1,left,right,rise)
  count=max(2,round((x1-x0)/1.1))
  for j in range(1,count):
   x=x0+(x1-x0)*j/count;self.beam(n+'_QuietSeam',(x,y0+.035,f(x)+.006),(x,y1-.035,f(x)+.006),.012,'seam',p)
  for y in [y0+.025,y1-.025]:self.tube(n+'_FinishedFascia',[(x0+(x1-x0)*j/64,y,f(x0+(x1-x0)*j/64)-.10)for j in range(65)],.045,'trim',p)
  for j in range(1,8):
   x=x0+(x1-x0)*j/8;self.beam(n+'_SoffitRafter',(x,y0+.06,f(x)-.20),(x,y1-.06,f(x)-.20),.07,'woodLight',p)
  return f
 def glazing(self,n,x0,x1,y,top=2.8,parent=None,door=None):
  p=parent or self.parent;cuts=[x0+(x1-x0)*i/max(2,round((x1-x0)/.95))for i in range(max(2,round((x1-x0)/.95))+1)]
  if door:cuts=sorted(set([*cuts,door[0],door[1]]))
  for a,b in zip(cuts,cuts[1:]):
   isdoor=door and door[0]<=a+.001 and b<=door[1]+.001;bottom=.20 if isdoor else .45
   if b-a<.045:continue
   self.box(n+'_Glass',((a+b)/2,y,(bottom+top)/2),(b-a-.035,.038,top-bottom),'glass',p,.004)
   if not isdoor:self.box(n+'_StoneSill',((a+b)/2,y,.27),(b-a,.18,.32),'cream',p,.012)
  for x in cuts:self.box(n+'_TimberMullion',(x,y-.035,(top+.18)/2),(.075,.12,top-.08),'woodLight',p,.01)
  for z in [.42,top]:self.box(n+'_Transom',((x0+x1)/2,y-.035,z),(x1-x0+.08,.13,.08),'wood',p,.01)
  if door:
   cx=sum(door)/2
   for x in [cx-.12,cx+.12]:self.beam(n+'_DoorHandle',(x,y-.15,1),(x,y-.15,1.42),.028,'woodDark',p)
   self.box(n+'_LevelDoorThreshold',(cx,y-.1,.11),(door[1]-door[0]+.15,.45,.19),'trim',p,.025)
 def hall(self,n,x0,x1,y0,y1,eaveL=3.0,eaveR=3.0,rise=.9,doorx=0,canopy=True,clerestory=True):
  self.use('Architecture');p=self.group(n);self.box(n+'_SolidBase',((x0+x1)/2,(y0+y1)/2,.10),(x1-x0,y1-y0,.20),'cream',p,.04)
  self.box(n+'_InteriorFloor',((x0+x1)/2,(y0+y1)/2,.215),(x1-x0-.20,y1-y0-.20,.07),'floor',p,.012)
  f=self.roof(n+'_ClosedCurvedRoof',x0-.43,x1+.43,y0-.46,y1+.40,eaveL,eaveR,rise,p)
  lo=min(eaveL,eaveR)-.28;lower=min(2.78,lo)
  for y in [y0,y1]:
   self.glazing(n+('_Front'if y==y0 else'_Rear'),x0+.12,x1-.12,y,lower,p,(doorx-.8,doorx+.8)if y==y0 and doorx is not None else None)
   if clerestory:
    parts=max(3,round((x1-x0)/.8))
    for j in range(parts):
     a=x0+.10+(x1-x0-.20)*j/parts;b=x0+.10+(x1-x0-.20)*(j+1)/parts
     G.arch_pane(n+'_ShapedUpperGlass',a+.035,b-.035,y,lower+.04,lambda x:f(x)-.22,self.M['glass'],p)
    for j in range(parts+1):
     x=x0+.10+(x1-x0-.20)*j/parts;h=f(x)-.18-lower
     self.box(n+'_UpperTimber',(x,y-.035,lower+h/2),(.075,.12,h),'woodLight',p,.01)
    self.tube(n+'_ArchHeader',[(x0+(x1-x0)*j/64,y-.04,f(x0+(x1-x0)*j/64)-.19)for j in range(65)],.052,'woodLight',p)
  for x in [x0,x1]:
   top=f(x)-.20;count=max(2,round(y1-y0))
   for j in range(count):
    a=y0+(y1-y0)*j/count;b=y0+(y1-y0)*(j+1)/count
    self.box(n+'_SideGlass',(x,(a+b)/2,(top+.45)/2),(.038,b-a-.08,top-.45),'glass',p,.004)
   self.box(n+'_SideSill',(x,(y0+y1)/2,.28),(.22,y1-y0,.34),'cream',p,.02)
   for j in range(count+1):self.box(n+'_SidePost',(x,y0+(y1-y0)*j/count,top/2+.10),(.13,.09,top-.1),'woodLight',p,.012)
   self.box(n+'_SideRoofBearing',(x,(y0+y1)/2,top+.03),(.20,y1-y0,.20),'cream',p,.018)
   for y in [y0,y1]:self.box(n+'_CornerPier',(x,y,top/2),(.24,.25,top),'cream',p,.025)
  self.rooms.append({'name':n,'footprint':[x0,y0,x1,y1],'door':[doorx,y0]if doorx is not None else None,'peak':max(f(x0+(x1-x0)*i/100)for i in range(101))})
  self.exclusions.append(sbox(x0-.05,y0-.05,x1+.05,y1+.05))
  if canopy and doorx is not None:self.canopy(n+'_Entry',doorx,y0-1.0,3.2,1.8,2.72)
  return p,f
 def canopy(self,n,x,y,w,d,z=2.65,parent=None,slatted=True):
  self.use('Architecture');p=self.group(n,parent);self.box(n+'_SolidSoffit',(x,y,z),(w,d,.18),'trim',p,.04)
  for sx in [-1,1]:
   for sy in [-1,1]:self.box(n+'_OakColumn',(x+sx*(w/2-.12),y+sy*(d/2-.10),z/2),(.12,.12,z),'wood',p,.018)
  for j in range(max(5,round(w/.22))):self.box(n+'_TimberCeiling',(x-w/2+.12+j*(w-.24)/max(1,round(w/.22)-1),y,z-.115),(.11,d-.15,.035),'woodLight',p,.008)
  if slatted:
   for side in [-1,1]:
    for j in range(6):self.box(n+'_SideScreen',(x+side*(w/2-.06),y+.1+j*.12,1.40),(.09,.055,2.65),'wood',p,.01)
  return p
 def pergola(self,n,x,y,w,d,z=2.55,roof=False):
  self.use('Architecture');p=self.group(n)
  for sx in [-1,1]:
   for sy in [-1,1]:self.box(n+'_Post',(x+sx*w/2,y+sy*d/2,z/2),(.13,.13,z),'wood',p,.018)
  for sy in [-1,1]:self.box(n+'_Beam',(x,y+sy*d/2,z),(w+.3,.16,.19),'woodLight',p,.02)
  for j in range(max(5,round(w/.28))):self.box(n+'_Rafter',(x-w/2+j*w/(max(5,round(w/.28))-1),y,z+.13),(.11,d+.5,.15),'woodLight',p,.012)
  if roof:self.roof(n+'_LightRoof',x-w/2-.22,x+w/2+.22,y-d/2-.22,y+d/2+.22,z+.45,z+.45,.22,p)
  return p
 def table(self,n,x,y,w=1.25,d=.75,z=.78):
  self.use('Interior');p=self.group(n);self.box(n+'_Top',(x,y,z),(w,d,.09),'woodLight',p,.035)
  for sx in [-1,1]:
   for sy in [-1,1]:self.box(n+'_Leg',(x+sx*(w/2-.10),y+sy*(d/2-.10),z/2),(.065,.065,z-.08),'wood',p,.012)
  return p
 def chair(self,n,x,y,yaw=0):
  self.use('Interior');p=self.group(n)
  for sx in [-1,1]:
   for sy in [-1,1]:self.box(n+'_Leg',(sx*.20,sy*.20,.43),(.05,.05,.40),'wood',p,.01)
  self.box(n+'_Cushion',(0,0,.65),(.52,.50,.11),'greenCloth',p,.05)
  for x1 in [-.22,.22]:self.box(n+'_BackPost',(x1,.22,.85),(.05,.05,.52),'wood',p,.01)
  self.box(n+'_Back',(0,.235,.98),(.50,.055,.28),'greenCloth',p,.025);p.location=(x,y,0);p.rotation_euler.z=yaw;return p
 def shelf(self,n,x,y,w=1.6,h=1.6):
  self.use('Interior');p=self.group(n)
  for xx in [x-w/2,x+w/2]:self.box(n+'_Side',(xx,y,.24+h/2),(.07,.34,h),'wood',p,.01)
  for j in range(5):
   z=.25+j*h/4;self.box(n+'_Shelf',(x,y,z),(w,.36,.055),'woodLight',p,.01)
   if j==4:continue
   for k in range(8):self.box(n+'_Book',(x-w*.42+k*w*.12,y-.035,z+.15),(.065+.01*(k%2),.23,.23+.03*(k%3)),['tealCloth','coral','cream','woodDark'][k%4],p,.008)
  return p
 def bench(self,n,x,y,w=2,yaw=0):
  self.use('Furniture');p=self.group(n)
  for j in range(4):self.box(n+'_SeatSlat',(0,-.20+j*.13,.50),(w,.11,.07),'woodLight',p,.012)
  for sx in [-1,1]:
   for sy in [-1,1]:self.box(n+'_MetalLeg',(sx*w*.38,sy*.15,.25),(.07,.07,.48),'rail',p,.012)
   self.box(n+'_BackUpright',(sx*w*.38,.25,.73),(.055,.055,.55),'rail',p,.009)
  for z in [.78,.98]:self.box(n+'_BackSlat',(0,.27,z),(w,.07,.13),'wood',p,.015)
  p.location=(x,y,0);p.rotation_euler.z=yaw;return p
 def shrub(self,n,x,y,z=.45,r=.32,flowers=True,parent=None):
  p=self.group(n,parent)
  for j in range(4):
   a=j*math.tau/4;self.sphere(n+'_Leaf',(x+.22*r*math.cos(a),y+.22*r*math.sin(a),z+r*.28),(r*.66,r*.62,r*.51),['leaf','leafLight','leafDark'][j%3],p,2)
  if flowers:
   for j in range(7):
    a=j*2.39996;rr=r*.7*math.sqrt((j+.5)/7);xx=x+rr*math.cos(a);yy=y+rr*math.sin(a);zz=z+r*.77
    for k in range(5):
     t=k*math.tau/5;o=self.sphere(n+'_Petal',(xx+.030*math.cos(t),yy+.030*math.sin(t),zz),(.030,.022,.016),'petalPink'if j%4==0 else'petal',p,1);o.rotation_euler.z=t
    self.sphere(n+'_Pollen',(xx,yy,zz+.016),(.015,.015,.012),'slide',p,1)
  return p
 def planter(self,n,x,y,w,d=.7,h=.45,flowers=True):
  self.use('Landscape');p=self.group(n)
  self.box(n+'_Base',(x,y,.12),(w,d,.22),'cream',p,.04)
  for side in [-1,1]:
   self.box(n+'_RimLong',(x,y+side*(d/2-.06),h/2+.08),(w,.12,h),'cream',p,.025)
   self.box(n+'_RimEnd',(x+side*(w/2-.06),y,h/2+.08),(.12,d,h),'cream',p,.025)
  self.box(n+'_Soil',(x,y,h),(w-.18,d-.18,.07),'soil',p,.01)
  count=max(1,round(w/.60))
  for j in range(count):self.shrub(n+'_Garden',x-w*.34+(w*.68*j/max(1,count-1)),y,h,.30,flowers,p)
  self.exclusions.append(sbox(x-w/2,y-d/2,x+w/2,y+d/2));return p
 def pot(self,n,x,y):
  self.use('Landscape');p=self.group(n);o=self.cyl(n+'_Pot',(x,y,.24),.23,.43,'woodLight',p,32)
  self.arc(n+'_Lip',x,y,.21,.27,.40,.07,'wood',p,steps=32)
  for j in range(7):
   a=j*math.tau/7;v=(x+.17*math.cos(a),y+.17*math.sin(a),.79+.08*math.sin(a*2));self.beam(n+'_Stem',(x,y,.43),v,.013,'leafDark',p)
   o=self.sphere(n+'_Fern',v,(.12,.05,.25),'leaf',p,2);o.rotation_euler=(.7*math.cos(a),.7*math.sin(a),a)
  return p
 def tree(self,n,x,y,h=3.8,r=1.10,well=True):
  self.use('Landscape');p=self.group(n);self.cyl(n+'_Trunk',(x,y,h*.40),.16,h*.80,'wood',p,16)
  for j in range(3):
   a=j*2.399;self.beam(n+'_Branch',(x,y,h*.43),(x+.48*math.cos(a),y+.48*math.sin(a),h*.70),.075,'woodDark',p)
  for j,(dx,dy,dz,sc)in enumerate([(-.45,-.12,.08,.82),(.48,.08,.1,.85),(0,.23,.55,.84),(.03,-.43,.17,.75),(0,0,-.20,.86)]):
   o=self.sphere(n+'_Crown',(x+dx*r,y+dy*r,h*.75+dz*r),(r*sc,r*sc*.91,r*sc*.89),['leaf','leafLight','leaf','leafDark','leaf'][j],p,3)
   for v in o.data.polygons:v.use_smooth=False
  if well:
   self.arc(n+'_TreeWell',x,y,.39,.60,.03,.18,'cream',p,steps=48);self.cyl(n+'_Soil',(x,y,.10),.39,.08,'soil',p,32)
  return p
 def treecourt(self,n,x,y):
  self.use('Landscape');p=self.group(n);self.arc(n+'_PlanterWall',x,y,1.24,1.43,.03,.44,'cream',p,steps=96);self.cyl(n+'_Soil',(x,y,.28),1.25,.16,'soil',p,64)
  for j in range(9):
   a=j*math.tau/9;self.shrub(n+'_Flowers',x+1.02*math.cos(a),y+1.02*math.sin(a),.46,.29,True,p)
  for a,b in [(math.radians(5),math.radians(110)),(math.radians(145),math.radians(290))]:
   for j in range(4):self.arc(n+'_BenchSlat',x,y,1.51+j*.11,1.60+j*.11,.51,.07,'woodLight',p,start=a,end=b,steps=36)
   for j in range(4):
    t=a+(b-a)*j/3
    for rr in [1.56,1.88]:self.box(n+'_SeatLeg',(x+rr*math.cos(t),y+rr*math.sin(t),.27),(.07,.07,.48),'rail',p,.012)
  self.tree(n+'_Tree',x,y,4.2,1.30,False);self.exclusions.append(Point(x,y).buffer(2.02,resolution=48));return p
 def lamp(self,n,x,y):
  self.use('Furniture');p=self.group(n);self.cyl(n+'_Base',(x,y,.10),.13,.18,'rail',p,20);self.cyl(n+'_Shaft',(x,y,1.25),.035,2.35,'rail',p,12)
  self.box(n+'_WarmLantern',(x,y,2.50),(.24,.24,.36),'trim',p,.018)
  for sx in [-1,1]:
   for sy in [-1,1]:self.box(n+'_MetalFrame',(x+sx*.13,y+sy*.13,2.50),(.025,.025,.40),'rail',p,.006)
  self.box(n+'_Cap',(x,y,2.72),(.34,.34,.075),'roof',p,.018)
 def board(self,n,x,y,w=1.3,roof=True):
  self.use('Furniture');p=self.group(n)
  for dx in [-w/2,w/2]:self.box(n+'_Post',(x+dx,y,.85),(.09,.12,1.65),'wood',p,.012)
  self.box(n+'_Panel',(x,y,1.15),(w-.10,.075,.88),'tealCloth',p,.025)
  for j in range(3):self.box(n+'_AbstractInfo',(x-w*.30+j*w*.29,y-.05,1.18),(.17,.015,.30),'cream',p,.012)
  if roof:self.roof(n+'_SmallRoof',x-w/2-.16,x+w/2+.16,y-.40,y+.40,1.95,1.95,.08,p)
  return p
 def emblem(self,kind,x,y,z,size=.7):
  self.use('Architecture');p=self.group(kind+'_ReliefEmblem')
  outline=[(x-size,z-size*.45),(x+size,z-size*.45)]+[(x+size*math.cos(j*math.pi/32),z-size*.45+size*math.sin(j*math.pi/32))for j in range(1,32)]
  if kind!='clock':G.prism_xz(kind+'_ThickArchPlaque',outline,y,.13,self.M['trim'],p)
  front=y-.085
  if kind=='clock':
   o=self.cyl('ClockRim',(x,front,z+.10),size*.53,.07,'rail',p,48);o.rotation_euler.x=math.pi/2
   o=self.cyl('ClockFace',(x,front-.045,z+.10),size*.46,.025,'trim',p,48);o.rotation_euler.x=math.pi/2
   for j in range(12):
    a=j*math.tau/12;self.sphere('ClockHour',(x+size*.38*math.sin(a),front-.065,z+.10+size*.38*math.cos(a)),(.018,.014,.018),'rail',p,1)
   self.beam('ClockLongHand',(x,front-.085,z+.10),(x-size*.23,front-.085,z+size*.37),.026,'rail',p);self.beam('ClockShortHand',(x,front-.09,z+.10),(x+size*.09,front-.09,z+size*.37),.028,'rail',p)
  elif kind=='book':
   for side in [-1,1]:
    o=self.box('BookPage',(x+side*.22*size,front,z+.03),(.43*size,.06,.56*size),'cream',p,.025);o.rotation_euler.y=side*-.12
    self.beam('BookLowerBinding',(x,front-.04,z-.24*size),(x+side*.45*size,front-.04,z-.18*size),.032,'rail',p)
   self.beam('BookSpine',(x,front-.05,z-.24*size),(x,front-.05,z+.32*size),.03,'rail',p)
  elif kind=='water':
   self.sphere('RaindropBody',(x,front,z+.23),(.18*size,.045,.24*size),'courtBlue',p,3)
   for j in range(2):self.tube('ReliefWaterWave',[(x-size*.5+t*size,front,z-size*.13-j*.16+.045*math.sin(t*math.tau))for t in [k/24 for k in range(25)]],.025,'rail',p)
  elif kind=='care':
   for dx,m in [(-.18,'coral'),(.18,'tealCloth')]:
    self.sphere('CareHeartUpper',(x+dx*size,front,z+.18),(.22*size,.05,.22*size),m,p,3)
   self.sphere('CareHeartLower',(x,front,z-.04),(.22*size,.055,.25*size),'coral',p,3)
  else:
   for side in [-1,1]:
    o=self.sphere('LeafRelief',(x+side*.19*size,front,z+.13),(.14*size,.045,.29*size),'leaf'if kind=='sprout'else('coral'if side<0 else'tealCloth'),p,3);o.rotation_euler.y=side*.45
   self.beam('ReliefStem',(x,front,z-.24*size),(x,front,z+.15*size),.025,'wood',p)
  return p
 def reserve(self,x,y):
  self.use('Furniture');o=self.group('NPC_RESERVED_NO_MODEL');o.location=(x,y,.03);o.empty_display_type='CIRCLE';o.empty_display_size=.65;o['implemented']=False;o['body_radius']=.35;o['interaction_radius']=1.4;o['facing_blender_yaw']=0.0
  self.reservations.append({'positionBlenderXYZ':[x,y,.03],'positionGLTFXYZ':[x,.03,-y],'bodyRadius':.35,'reservationRadius':.65,'playerStopBlenderXYZ':[x,y-1.3,.03],'interactionRadius':1.4,'implemented':False})
 def garden_ribbon(self,n,points,width=.72):
  self.use('Landscape');p=self.group(n);line=LineString(points);bed=line.buffer(width/2,resolution=12);inner=bed.buffer(-.10)
  self.solid(n+'_ClosedStoneEdge',bed.difference(inner),.025,.32,'cream',p)
  self.solid(n+'_PlantingSoil',inner,.05,.24,'soil',p)
  for j in range(max(2,round(line.length/.53))):
   pt=line.interpolate((j+.5)/max(2,round(line.length/.53)),normalized=True);self.shrub(n+'_Flowers',pt.x,pt.y,.32,.34,True,p)
  self.exclusions.append(bed);return p
 def site(self):
  # Build buildings/landscape FIRST, then infer a platform from measured real geometry.
  bpy.context.view_layer.update();points=[];deps=bpy.context.evaluated_depsgraph_get()
  for obj in self.root.children_recursive:
   if obj.type!='MESH' or 'Crown'in obj.name:continue
   e=obj.evaluated_get(deps);me=e.to_mesh();points.extend(tuple(obj.matrix_world@v.co)for v in me.vertices);e.to_mesh_clear()
  measured=max(math.hypot(p[0],p[1])for p in points);radius=math.ceil((measured+1.0)*5)/5
  self.radius=radius;self.measured_content_radius=measured;self.use('Site');p=self.group('PlatformAndReviewConnections');disk=Point(0,0).buffer(radius,resolution=48);water=unary_union(self.water_shapes)if self.water_shapes else Polygon();surface=disk.difference(water)
  self.solid('ClosedPlatformWithRealWaterRecess',surface,-.46,.46,'stone',p,.025)
  self.solid('WaterBasinBottom',water,-.52,.06,'stone',p)if not water.is_empty else None
  exclusion=unary_union([*self.exclusions,*self.water_shapes])if self.exclusions or self.water_shapes else Polygon();pave=disk.buffer(-.06).difference(exclusion)
  materials=[]
  for j,h in enumerate(['E1DCD0','E9E3D6','DED9CE']):
   k='paver'+str(j);self.M[k]=G.material('WarmLimestonePaver'+str(j),h,.78);materials.append(k)
  rows=math.ceil(radius/.85)+1;cols=math.ceil(radius/1.06)+1;tiles=0
  for row in range(-rows,rows+1):
   y=row*.85
   for col in range(-cols,cols+1):
    x=col*1.06+(.53 if row%2 else 0);tile=sbox(x-.521,y-.416,x+.521,y+.416).intersection(pave)
    if tile.is_empty or tile.area<.025:continue
    self.solid('EditableStonePaver',tile,.003,.026,materials[(row+col)%3],p,0);tiles+=1
  self.tile_count=tiles;self.arc('PlinthMoulding',0,0,radius-.09,radius+.025,-.13,.15,'cream',p,steps=128)
  self.ports=[]
  for j,angle in enumerate([190,225,278,352]):
   a=math.radians(angle);radial=Vector((math.cos(a),math.sin(a),0));tangent=Vector((-math.sin(a),math.cos(a),0));width=4.8;start=math.sqrt(radius**2-(width/2)**2)-.04;end=start+2.25;centre=radial*((start+end)/2)
   o=self.box('ReviewBridgeArm',tuple(centre+Vector((0,0,-.15))),(end-start,width,.30),'stone',p,.025);o.rotation_euler.z=a;self.ports.append({'angleDegrees':angle,'width':width,'startRadius':start,'endRadius':end,'reviewOnly':True})
   for side in [-1,1]:
    for t in [0,.5,1]:
     q=radial*(start+(end-start)*t)+tangent*side*width/2;self.beam('ReviewBridgePost',tuple(q+Vector((0,0,.03))),tuple(q+Vector((0,0,1.02))),.045,'rail',p)
    for z in [.53,1.0]:self.beam('ReviewBridgeRail',tuple(radial*start+tangent*side*width/2+Vector((0,0,z))),tuple(radial*end+tangent*side*width/2+Vector((0,0,z))),.038,'rail',p)
  def opening(a):return any(abs((a-math.radians(q['angleDegrees'])+math.pi)%math.tau-math.pi)<math.asin((q['width']/2+.12)/radius)for q in self.ports)
  for j in range(128):
   a=j*math.tau/128;b=(j+1)*math.tau/128
   if opening((a+b)/2):continue
   for z in [.53,1]:self.tube('PerimeterMetalRail',[(radius*math.cos(a),radius*math.sin(a),z),(radius*math.cos(b),radius*math.sin(b),z)],.021,'rail',p)
   if j%3==0:self.beam('PerimeterRailPost',(radius*math.cos(a),radius*math.sin(a),.03),(radius*math.cos(a),radius*math.sin(a),1.02),.045,'rail',p)
  return radius
