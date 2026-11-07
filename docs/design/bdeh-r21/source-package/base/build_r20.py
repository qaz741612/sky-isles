"""B/D/E/H R20 architectural REDESIGN, actual parametric meshes.
Four original structures, not a post-processing pass. Only offline reference geometry.
Run: python build_r20.py  (generates GLBs, source-aligned images, structural audits).
No GitHub writes or deployments. All positions local XZ, Y-up.
"""
import math, sys, json, zipfile, re
from pathlib import Path
import numpy as np
import trimesh
from shapely.geometry import Point, Polygon
from shapely.affinity import scale
from PIL import Image,ImageDraw,ImageFont
import importlib.util

HERE=Path(__file__).resolve().parent
SRC=HERE/'BDEH_R18'/'source'/'build_r18.py'
spec=importlib.util.spec_from_file_location('r18source',str(SRC)); r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
Design=r.Design
r.ROOT=HERE
r.base.OUT=HERE
for q in ('models','renders','qa'):(HERE/q).mkdir(exist_ok=True)
C=r.base.C
C.update({'copper':'#C68D54','copperdark':'#86664B','softwhite':'#F5EBDB','terracot':'#B68A69','darkglass':'#22556B','aqua':'#4FA5AB','mistglass':'#A7D4D5','ink':'#263C49','silver':'#9FAEAC','sand':'#D9CBAE','moss2':'#56754F','forest':'#355E50','skyline':'#547D94','sunlight':'#F2D49C','redbrown':'#975B43','cyanline':'#9DDCE2'})

# Utility wrappers with real structural geometry.
def box(s,n,x,z,wx,wz,y0,y1,c):s.hardbox(n,x,z,wx,wz,y0,y1,c)
def poly(s,n,p,y0,y1,c):s.hardprism(n,p,y0,y1,c)
def beam(s,n,a,b,radius,c):s.girder(n,a,b,radius,c)
def post(s,n,x,z,y0,y1,radius,c):s.post(n,x,z,y0,y1,radius,c)
def glass(s,n,a,b,y0,y1,div=8,col='mistglass',frame='copperdark'):
  A=np.array(a,dtype=float);B=np.array(b,dtype=float)
  for k in range(div):
    u=A+(B-A)*k/div;v=A+(B-A)*(k+1)/div
    s.panel(n+'_glass',u,v,y0,y1,col,.10)
    post(s,n+'_frame',u[0],u[1],y0,y1,.057,frame)
    if k%2==0:s.panel(n+'_mid_band',u,v,(y0+y1)/2-.09,(y0+y1)/2+.1,'sand',.12)
  post(s,n+'_right',B[0],B[1],y0,y1,.065,frame)
  s.panel(n+'_head',A,B,y1-.13,y1+.04,frame,.15)

def face_loop(s,n,coords,y0,y1,col='ivory',glass_panels=True,skips=()):
  # Occupied facade from real floor slab, not a hollow roof shell
  for i,(a,b) in enumerate(zip(coords,coords[1:]+coords[:1])):
    if i in skips:continue
    if glass_panels:glass(s,f'{n}_bay{i}',a,b,y0,y1,max(2,int(np.linalg.norm(np.array(b)-np.array(a))/.8)),col,'warmwood')
    else:s.panel(n,a,b,y0,y1,col,.15)

def awning(s,n,x0,z0,wx,wz,h):
  box(s,n+'_roof',x0,z0,wx,wz,h,h+.26,'warmwood')
  for x in (x0-wx*.42,x0+wx*.42):
    for z in (z0-wz*.43,z0+wz*.43):post(s,n+'_support',x,z,.3,h,.085,'copperdark')

def arch_roof(s,n,cx,cz,inner,outer,a0,a1,height,mat):
  # Real thick radially supported geometry over a fully glazed curved inhabitable wing.
  def v(angle,r):return cx+r*math.cos(angle),cz+r*math.sin(angle)
  ts=np.linspace(math.radians(a0),math.radians(a1),40)
  # curved roof with centre crest, varying roof height
  for i,(a,b) in enumerate(zip(ts[:-1],ts[1:])):
    U=np.linspace(a,b,3);rr=np.linspace(inner,outer,5)
    grid=np.array([[[cx+r*math.cos(t), height+0.7*math.sin((t-ts[0])/(ts[-1]-ts[0])*math.pi)+0.23*(r-inner)/(outer-inner),cz+r*math.sin(t)] for t in U] for r in rr])
    s.patch(n+'_curved_roof',grid,mat,.33)
    if i%2==0:
      ix,iz=v(a,inner+.20);ox,oz=v(a,outer-.15)
      h=height+.7*math.sin((a-ts[0])/(ts[-1]-ts[0])*math.pi)
      beam(s,n+'_arc_truss',(ix,h-.42,iz),(ox,h+.13,oz),.09,'warmwood')
  return ts

def curve_facade(s,n,cx,cz,r,aa,bb,y0,y1,col='blueglass',nd=35):
  tt=np.linspace(math.radians(aa),math.radians(bb),nd)
  for j,(u,v) in enumerate(zip(tt[:-1],tt[1:])):
    a=(cx+r*math.cos(u),cz+r*math.sin(u));b=(cx+r*math.cos(v),cz+r*math.sin(v))
    s.panel(n+'_glass',a,b,y0,y1,col,.11)
    if j%2==0:post(s,n+'_fin',a[0],a[1],y0,y1,.055,'warmwood')
    if j%5==0:s.panel(n+'_horizontal_lintel',a,b,3.28,3.40,'warmwood',.15)

def planted_border(s,coords,name='Planting'):
  # subtle site plan ground elements outside main path (not part of building collision audit)
  for a,b in zip(coords,coords[1:]):
    beam(s,name+'_low_stone',(a[0],.30,a[1]),(b[0],.30,b[1]),.085,'stone2')

def build_B(s):
  """New: paired inhabited curved wings + joined two-level healing atrium and sunken court.
  The building is the hugging symbol, not a decorative crescent roof above a box.
  """
  cx,cz=-2.75,-1.75;Ri,Ro=4.9,9.0
  a0,a1=52,309
  ts=np.linspace(math.radians(a0),math.radians(a1),45)
  p=lambda rr,a:(cx+rr*math.cos(a),cz+rr*math.sin(a))
  arc=[p(Ro,t) for t in ts]+[p(Ri,t) for t in ts[::-1]]
  poly(s,'CareWingFoundation',arc,.22,.72,'stone2')
  poly(s,'CareTwoOccupiedFloorLevel',arc,3.28,3.57,'sand')
  poly(s,'CareAtticBearingSlab',arc,5.72,6.0,'warmwood')
  # segmented glazed double-level bays; solid piers and true floor bands
  curve_facade(s,'OuterContinuum',cx,cz,Ro-.15,a0,a1,.8,5.75,'mistglass')
  curve_facade(s,'InnerContinuum',cx,cz,Ri+.05,a0,a1,.8,5.75,'glass2')
  for i,t in enumerate(ts[::3]):
    x,z=p(Ro-.13,t);xo,zo=p(Ri+.03,t)
    post(s,'CareWingMassTimberColumn',x,z,.25,6.7,.115,'copperdark')
    post(s,'CareCourtyardColumn',xo,zo,.35,6.50,.095,'warmwood')
    if i%2==0:beam(s,'CareCrossBayGlulam',(x,5.98,z),(xo,6.02,zo),.14,'copper')
  arch_roof(s,'TwoWingsOneRoof',cx,cz,Ri-.45,Ro+.30,a0,a1,6.15,'copper')
  # differentiated inner court: stepped recessed reflecting garden with planted oval
  tt=np.linspace(0,2*math.pi,42)
  inner=[(cx+3.08*math.cos(t),cz+2.3*math.sin(t)) for t in tt]
  poly(s,'CareSensoryGardenSoil',inner,.16,.33,'sage')
  for t in np.linspace(0,2*math.pi,19):
    x,z=cx+3.55*math.cos(t),cz+2.75*math.sin(t)
    if x>cx+1.3:continue
    post(s,'CourtyardShadeTimber',x,z,.23,3.45,.085,'warmwood')
  for t in np.linspace(.6,5.6,18):
    a=(cx+3.85*math.cos(t),cz+3.08*math.sin(t));b=(cx+3.88*math.cos(t+.16),cz+3.08*math.sin(t+.16))
    beam(s,'CourtyardPergolaRim',(a[0],3.52,a[1]),(b[0],3.52,b[1]),.075,'copperdark')
  s.tree(cx-1.5,cz,.70,'pink')
  # physically linked entry wing, long glass gallery, roof not independent mini hut
  poly(s,'CommunityCareEntryHall',[(4.7,-6.7),(7.15,-5.8),(7.5,-1.8),(3.2,-1.45),(2.8,-5.1)],.22,4.8,'ivory')
  glass(s,'CareArrivalPortal',(3.15,-5.55),(7.25,-5.55),.50,4.58,10,'blueglass','copperdark')
  poly(s,'CarePortalRoof',[(2.65,-7.0),(7.80,-6.1),(8.1,-1.4),(2.45,-1.15)],4.82,5.12,'ochre')
  # shared roof pedestrian balcony connects two wings at entry portal
  for a in np.linspace(48,306,32):
    x,z=p(Ri+.12,math.radians(a));post(s,'CareBalconyParapet',x,z,3.55,4.18,.05,'bronze2')
  for x,z in [(-10.3,-10.0),(-9.75,7.65),(-7.0,-11.2)]:
    if s._publicCorridor.distance(Point(x,z))>2.1:s.garden(x,z,2.2,.65,'leaf')

def build_D(s):
  """New: civic glass forum with triangulated branching cantilever and luminous wing structure.
  A real double-height public institution rather than office box and floating roof.
  """
  # footprint south of north edge, east of western public road
  podium=[(-4.4,-.8),(11.3,-.8),(13.2,1.0),(13.2,9.3),(-4.4,9.4),(-5.4,7.7)]
  poly(s,'CivicCityHallPodium',podium,.18,.76,'stone2')
  poly(s,'OnePublicLobbyFloor',podium,.76,1.02,'ivory')
  upper=[(-3.95,1.0),(12.2,1.0),(12.2,9.15),(-3.95,9.1)]
  poly(s,'CivicServiceGalleryFloor',upper,4.18,4.51,'white2')
  poly(s,'CivicRoofBearingCeiling',upper,7.15,7.38,'sand')
  # major facade truly transparent on four sides, with 2nd-floor screens and sun shade
  glass(s,'CivicFrontTransparency',(-4.4,-.84),(12.3,-.84),1.03,7.20,24,'blueglass','ink')
  glass(s,'CivicNorthTransparency',(-4.4,9.4),(12.2,9.4),1.10,7.13,24,'glass2','ink')
  glass(s,'CivicWestPublicCorner',(-4.4,-.8),(-4.4,9.4),1.05,7.18,12,'mistglass','copperdark')
  glass(s,'CivicEastPublicCorner',(12.2,-.8),(12.2,9.4),1.05,7.18,12,'mistglass','copperdark')
  # crest lifted into diagonally spanning frame, with curved cantilevered wings, sculptural V
  for side in (-1,1):
    x0,x1=(-6.6,4.0) if side<0 else (4.0,13.0)
    def rf(x,z,side=side):
      t=abs(x-4.0)/(10.6 if side<0 else 9.0)
      # highest near outside tips to define continuous architectural identity
      return [x,7.52+3.0*t**1.42+.30*math.cos((z-4.1)/6.3*math.pi),z]
    s.surface('PublicRoofWingWest' if side<0 else 'PublicRoofWingEast',x0,x1,-2.1,10.5,rf,'roofblue' if side<0 else 'copperdark',32,17,.42)
    for z in np.linspace(-1.8,10.2,10):
      x=x1 if side>0 else x0;yp=rf(x,z)[1]
      beam(s,'LongSpanCivicTriangulatedRib',(4,7.40,z),(x,yp-.2,z),.13,'silver')
      if z%2<1:post(s,'CivicPerimeterStructuralPier',x,z,.40,yp-.45,.10,'charcoal')
      # diagonals solve roof's structural plausibility
      beam(s,'CivicCrossTension',(4,7.5,z),(x*.85+4*.15,5.1,z+.35),.055,'copper')
  # elevated glazed spine/lantern integrated with occupied upper public hall
  poly(s,'PublicLightwell',[(2.7,1.65),(5.15,1.65),(5.15,8.45),(2.7,8.45)],7.27,9.72,'darkglass')
  glass(s,'LightwellEast',(5.1,1.8),(5.1,8.3),7.5,9.65,8,'mistglass','silver')
  poly(s,'LightwellCrownCap',[(2.2,1.5),(5.6,1.5),(5.6,8.7),(2.2,8.7)],9.8,10.18,'copper')
  # clear public atrium and government service portal, cantilevered entry canopy
  awning(s,'CivicWideEntranceMarquee',3.8,-2.35,10.0,3.2,5.75)
  for x in np.linspace(-3.8,11.1,13):post(s,'VerticalCivicStoneFins',x,-.95,1.0,7.1,.09,'copperdark')
  for x,z in [(10.8,-6.2),(11.8,11.4)]:
    if s._publicCorridor.distance(Point(x,z))>1.7:s.garden(x,z,2.2,.70,'green')

def build_E(s):
  """New: one terraced inhabited *landform* -- sweeping stepped canopy, ecological valley;
  no stacked cuboid towers, no fake lookout pavilion, no transplanted greenhouse.
  """
  # single articulated lower building extends along northern terrace: angled rather than boxy
  outline=[(-6.1,2.7),(5.6,1.15),(12.0,2.9),(13.2,6.9),(8.0,11.95),(-.5,11.7),(-7.1,7.5)]
  poly(s,'EcologicalCommunityLowerGallery',outline,.24,.58,'stone2')
  poly(s,'EcoGroundLevelSolidCore',[(-2.7,4.1),(5,3.3),(7.0,6.15),(2.0,8.7),(-3.6,7.0)],.62,4.20,'ivory')
  # span of continuous public veranda supported by visible structural timber frames
  glass(s,'EcoWaterCycleWest',(-6.1,2.7),(5.6,1.15),.70,3.98,22,'mistglass','warmwood')
  glass(s,'EcoEast',(12,2.9),(13.2,6.9),.70,4.20,9,'blueglass','warmwood')
  glass(s,'EcoNorth',(8,11.95),(-.5,11.7),.70,4.20,16,'glass2','copperdark')
  # actual occupied upper mezzanine supported by stone fins and deep beams
  upper=[(-1.5,6.0),(5.7,5.5),(10.65,7.2),(8.35,11.65),(-.45,10.85)]
  poly(s,'EcoUpperBotanicalResearchFloor',upper,4.1,4.39,'sand')
  for j,(a,b) in enumerate(zip(upper,upper[1:]+upper[:1])):
    glass(s,'EcoUpperGallery',a,b,4.45,6.45,6,'glass2','copperdark')
  # living canopy is not a separate flat roof: rises as one flowing geological strata from SW to NE.
  def living(x,z):
    u=(x+7.0)/20.4;v=(z-1.0)/11.2
    return [x,4.4 + 2.12*v + 1.0*math.sin(math.pi*u*.88)+.27*math.sin(2*math.pi*v),z]
  s.surface('MainOrganicLandformCanopy',-6.45,13.1,1.15,9.0,living,'sage',42,26,.47)
  # continuous raised northern ribbon folds up and connects to mezzanine
  def lift(x,z):
    return [x,6.4+1.23*(z-6.2)/5.8+.43*math.sin((x+1)/12*math.pi),z]
  s.surface('EcoHighTerraceRibbon',-1.8,10.7,6.2,12.0,lift,'darkolive',28,18,.39)
  # real structure: terrace columns, visible trusses, perforated timber sunshades
  for x in np.linspace(-5.25,11.8,16):
    z=3.3 if x<2 else 5.3
    yl=living(x,z)[1]
    post(s,'GeoRoofTimberBearing',x,z,.24,yl-.18,.13,'warmwood')
    beam(s,'EcoWoodDiagonalBracing',(x,.72,z),(x+0.75,yl-.18,z+1.25),.055,'copperdark')
  for z in np.linspace(7.1,11.45,9):
    for x in (0.1,8.8):post(s,'EcoUpperGallerySupport',x,z,4.25,lift(x,z)[1]-.21,.095,'charcoal')
  # low vegetation actually on roof (no random shrubs) as stripes along grade
  for z in np.linspace(3.25,7.15,10):
    for x in np.linspace(-3.7,10.3,14):
      if (int((x+5)*2)+int(z*2))%3:continue
      y=living(x,z)[1]
      box(s,'RooftopPlantedMosaicSedum',x,z,.43,.20,y+.03,y+.16,'lichen')
  # natural watershed environmental park, NOT gates or pond circles
  banks=[(-4.7,.80),(-1.75,.60),(1.55,-.30),(4.55,-1.3),(6.45,-1.8),(8.20,-1.2),(8.75,-.45),(7.95,.25),(6.0,-.75),(4.65,-.55),(.75,.55),(-2.5,1.3)]
  poly(s,'RainGardenFloodplainPaving',banks,.17,.32,'stone2')
  poly(s,'RainGardenCreek',[(x*.98,z*.98) for x,z in banks],.325,.36,'aqua')
  for x,z in [(-8.5,7.9),(-6.7,11.1),(10.1,12.4)]:
    if s._publicCorridor.distance(Point(x,z))>2:s.tree(x,z,.6,'olive')

def build_H(s):
  """New: readable double-book identity built over two full learning halls and an elevated atrium.
  Glazed occupied classrooms, true timber ribs, library colonnade and outdoor debate steps.
  """
  # wide structural platform, two clear academic wings with glazed courtyard front
  base=[(-10.65,.7),(9.6,.7),(10.15,10.0),(-10.3,10.0)]
  poly(s,'EducationStoneLearningPlinth',base,.20,.68,'stone2')
  for c,x0,x1 in [('west',-10.25,-.7),('east',-.55,9.8)]:
    poly(s,'InhabitedTeachingFloor_'+c,[(x0,.84),(x1,.84),(x1,9.84),(x0,9.84)],.71,1.04,'ivory')
    poly(s,'InhabitedSecondFloor_'+c,[(x0,.84),(x1,.84),(x1,9.84),(x0,9.84)],3.76,4.04,'sand')
    glass(s,'BookWestSouthFront_'+c,(x0,.8),(x1,.8),1.06,6.30,17,'mistglass','warmwood')
    glass(s,'BookWestNorthFront_'+c,(x0,9.8),(x1,9.8),1.06,6.25,17,'darkglass','warmwood')
    glass(s,'BookSideWest_'+c,(x0,.85),(x0,9.8),1.06,6.25,11,'glass2','copperdark')
    glass(s,'BookSideEast_'+c,(x1,.85),(x1,9.8),1.06,6.25,11,'glass2','copperdark')
    for x in np.linspace(x0+.45,x1-.4,7):
      post(s,'InhabitedStudyHallLoadColumns',x,1.05,.28,6.25,.10,'copperdark')
  # raised learning atrium spine actually inhabited, unlike floating roof decoration
  box(s,'DoubleHeightReadingSpine',-.64,5.25,2.0,9.15,1.04,8.15,'blueglass')
  for z in np.linspace(1.1,9.2,13):post(s,'CentralReadingSpineFins',-.65,z,1.1,8.25,.080,'ochre')
  box(s,'ReadingSpineGlazedClerestory',-.65,5.25,2.45,9.45,8.20,8.6,'softwhite')
  # TWO page roof surfaces rise outward, with real rib structure bearing down to hall facades
  for side in (-1,1):
    x0,x1=(-11.0,-.65) if side<0 else (-.65,10.8)
    def page(x,z,side=side):
      t=abs(x+.65)/(10.5 if side<0 else 11.4)
      return [x,7.2+3.5*t**1.25+.38*math.sin((z-.5)/10.7*math.pi),z]
    s.surface('WestRisingBookPage' if side<0 else 'EastRisingBookPage',x0,x1,-.4,11.0,page,'roofblue' if side<0 else 'ochre',38,19,.46)
    for z in np.linspace(.15,10.45,11):
      xx=x0 if side<0 else x1;yp=page(xx,z)[1]
      beam(s,'TrueGlulamCantilever',(-.65,7.0,z),(xx,yp-.22,z),.14,'warmwood')
      post(s,'ExposedBookWingLoadPier',xx,z,.20,yp-.35,.12,'copperdark')
      # facade hangs below the pages within real structural frame
      if int(z*3)%2==0:beam(s,'BookPageCrossBrace',(xx,.65,z),(-.7,7.10,z),.05,'silver')
  # ribbon entry threshold, human-scale shelter and small real amphitheater, no mini oval track
  awning(s,'LearningForumEntryRoof',-.65,-1.25,8.6,2.3,4.3)
  for k in range(4):
    z=-2.65-k*.48;wx=8.0-k*.40
    box(s,'OutdoorLearningTerrace',-3.5,z,wx,.75,.24+.19*k,.40+.19*k,'sand')
  for x,z in [(-11.5,11.5),(11.5,11.0)]:
    if s._publicCorridor.distance(Point(x,z))>2:s.tree(x,z,.63,'pink')


def build_E2(s):
  """R21 replacement for E: continuous sculptural *ascending* inhabited roof landscape.
  A terraced eco-civic building, not a greenhouse and not two stacked rectangular roof sheets.
  """
  from math import pi,sin
  lower=[(-5.85,2.45),(6.35,1.7),(10.9,3.55),(11.85,8.55),(5.8,11.15),(-3.75,9.8),(-7.65,6.1)]
  poly(s,'EcologicalCivicAtriumPodium',lower,.2,.6,'stone2')
  # Two actual inhabitable levels, shared light court and resilient service wing
  mid=[(-4.25,3.25),(7.85,2.85),(9.85,6.95),(5.9,10.15),(-4.45,8.65)]
  poly(s,'ClimateCommunityFirstFloor',mid,.65,.9,'ivory')
  poly(s,'ClimateCommunityMezzanine',mid,3.54,3.9,'sand')
  # Real glass shell, timber columns, and living wall
  for i,(a,b) in enumerate(zip(mid,mid[1:]+mid[:1])):
    glass(s,'ContinuousOpenEnvironmentalGallery',a,b,1.0,6.1,max(6,int(np.linalg.norm(np.array(a)-np.array(b))/.72)),'mistglass','copperdark')
    # window spandrel clarifies two floors
    s.panel('ClimateGalleryFloorBand',a,b,3.42,3.75,'warmwood',.21)
  # bookend open outdoor ecology pavilion, attached to atrium side, no extra tall tower
  for x,z in [(-6.7,3.45),(-6.7,6.2),(-3.4,3.45),(-3.4,6.2)]:
    post(s,'EcologyClimatePublicVerandaBearing',x,z,.24,4.1,.125,'warmwood')
  poly(s,'IntegratedEcoVerandaRoof',[(-7.5,2.8),(-2.8,2.75),(-2.8,7),(-7.5,7)],4.1,4.40,'ochre')
  # The sweeping landform includes a single low-edge-to-high-edge roof, divided by
  # a luminous skylight strip; both sides share grade, cantilevers and occupied base.
  def living(x,z):
     a=(x+7.5)/20.1;b=(z-.6)/11.1
     y=1.45+2.3*a+4.45*b+0.75*sin(pi*a)*sin(pi*b)
     return [x,y,z]
  # solar shell with expressive wave geometry, not a stack of slabs
  s.surface('MainLivingLandformWest',-7.5,2.25,.8,10.0,living,'sage',32,24,.54)
  s.surface('MainLivingLandformEast',3.55,12.6,.8,10.0,living,'lichen',31,24,.54)
  # long polycarbonate roof lightwell runs *between* both green wings
  def skyl(x,z):
      a=(x+7.5)/20.1;b=(z-.6)/11.1
      return [x,1.5+2.3*a+4.45*b+.75*sin(pi*a)*sin(pi*b)+.12,z]
  s.surface('RainwaterSkyLight',2.20,3.58,.8,10.0,skyl,'mistglass',6,28,.22)
  # dramatic timber/steel load path from roof into occupied column grid
  for x in np.linspace(-6.55,11.55,17):
    for z in (3.05,7.9):
      y=living(x,z)[1]
      if y>1.7:
        post(s,'EcologyEarthRoofStructure',x,z,.22,y-.18,.105,'warmwood')
        beam(s,'EcologyCrossBracedWoodStructure',(x,.24,z),(x+.7,y-.28,z-.55),.065,'copperdark')
  # real shallow landscape terraces as extensions of the ascending roof
  for k,z in enumerate(np.linspace(4.0,8.55,7)):
      for x in np.linspace(-5.8,11.0,15):
          if (round(x*2)+k)%4==0:
              y=living(x,z)[1]
              box(s,'VegetatedRoofNativeGroundcover',x,z,.58,.30,y+.02,y+.19,'darkolive' if k%2 else 'leaf')
  # Living moss-green stepped parapet leads from public garden to landmark roof
  for x,z in [(-6.2,3.4),(-5.7,4.45),(-5.2,5.5),(-4.6,6.6)]:
      y=living(x,z)[1]
      box(s,'LivingGreenRoofEntrySteps',x,z,1.0,.60,.25,max(.54,y-.22),'stone2')
  # integrated environmental canal, not a second dam / old flat thin stripe
  water=[(-5.9,-.45),(-2.8,-.7),(.2,-1.55),(3.2,-2.4),(6.4,-2.15),(9.5,-1.45),(8.8,-.55),(5.6,-1.28),(2.2,-1.5),(-.85,-.55),(-4.25,.2)]
  poly(s,'SinuousRainGardenStoneBank',water,.14,.31,'stone2')
  poly(s,'SinuousRainGardenWater',[(x*.98,z*.97) for x,z in water],.32,.365,'aqua')
  for x,z in [(-8.7,8.1),(-7.4,11.25),(10.9,11.8)]:
     if s._publicCorridor.distance(Point(x,z))>3:s.tree(x,z,.6,'olive')

BUILDS={'B':build_B,'D':build_D,'E':build_E2,'H':build_H}


def human_scale_detail(s):
  """Landscape deliberately subservient to architecture; only site-specific functional groups.
  All additions derive from same mesh source and thus appear in GLB/6 views.
  """
  c=s.code
  if c=='B':
    # Two concentric veranda levels articulate the continuous occupied hugging wings.
    cx,cz=-2.75,-1.75
    for a in np.linspace(55,305,35):
      t=math.radians(a);xi=cx+4.7*math.cos(t);zi=cz+4.7*math.sin(t)
      if a%12<7:
        beam(s,'B_InteriorCloisterUpperRailing',(xi,3.75,zi),(xi,4.35,zi),.035,'ochre')
        beam(s,'B_CloisterWindowLowerSill',(xi,3.15,zi),(cx+5.1*math.cos(t),3.15,cz+5.1*math.sin(t)),.07,'copperdark')
    # Embedded pairs of stacked glass entrance arches under a timber soffit.
    for xx in (3.1,4.5,5.9,7.3):
      post(s,'B_CareEntryTimberPortal',xx,-6.9,.15,5.30,.13,'copperdark')
      beam(s,'B_EntranceArchSoffit',(xx,5.22,-7.0),(xx,5.58,-4.7),.11,'warmwood')
    # Human-scale sensory garden structure (low-risk path clearances).
    for xx,zz in [(-8.75,-7.85),(-8.2,5.7),(.45,4.7)]:
      if s._publicCorridor.distance(Point(xx,zz))>2.6:
        s.garden(xx,zz,2.7,.82,'deepgreen')
    for x,z in [(-10.8,6.1),(-7.6,7.75)]:
      if s._publicCorridor.distance(Point(x,z))>2:s.tree(x,z,.53,'pink')
  elif c=='D':
    # The giant civic roof has real joinery, human-scale entrance bays and public program.
    for x in np.linspace(-4.3,12.4,22):
      beam(s,'D_FrontWoodSoffitLattice',(x,5.75,-1.0),(x,5.75,-2.2),.05,'copper')
      # Second-floor glazing is not uninterrupted blank glass.
      if int(x*2)%2==0:
        box(s,'D_WarmSpandrelStripe',x,-.86,.13,.18,4.15,4.46,'warmwood')
    # Integrate sculptural civic service portal into roof-bearing front columns.
    for x in (0,2.6,5.2,7.8):
      post(s,'D_MainPortalBearing',x,-2.35,.25,5.7,.12,'warmwood')
    for z in (1.8,4.1,6.4,8.7):
      post(s,'D_NorthTimberLouver',12.4,z,1.0,7.45,.105,'copperdark')
    # Informational civic tower is *low* and part of the building, not another generic tall office block.
    for z in np.linspace(3.0,8.0,8):
      beam(s,'D_LanternCopperFrames',(2.55,8.25,z),(5.35,8.25,z),.045,'copper')
    for x,z in [(-10.8,8.2),(9.9,-8.0)]:
      if s._publicCorridor.distance(Point(x,z))>3:s.garden(x,z,2.1,.88,'green')
  elif c=='E':
    # Cascading terraced timber facade and programmatic outdoor climate gallery.
    for x in np.linspace(-5.8,11.8,19):
      z=2.65+(x+6)*.08
      if -5<x<11.0:
        if s._publicCorridor.distance(Point(x,z))>2.5:
          post(s,'E_ShelteredEcologyPergola',x,z,.25,3.1,.075,'warmwood')
          beam(s,'E_TimberShadeRafter',(x,3.1,z),(x,3.1,z+1.2),.075,'copperdark')
    for x in np.linspace(-3.0,8.5,12):
      # low green bands visually connect terrain to folding building instead of floating balconies.
      z=5.0+(x+3.0)*.2;y=4.85+.38*math.sin((x+3)/12*math.pi)
      if y<6:
        box(s,'E_PlanterEdge',x,z,.60,.35,y,y+.18,'stone2')
    # Climate monitoring elements mounted to glazing, not an isolated tower.
    for x,z in [(8.8,6.75),(10.0,6.90)]:
      post(s,'E_MonitoringFin',x,z,4.1,6.6,.065,'warmwood')
    for x,z in [(-9.0,10.0),(-6.2,12.4)]:
      if s._publicCorridor.distance(Point(x,z))>3:s.garden(x,z,2.5,1.10,'green')
  elif c=='H':
    # Public-facing learning program readable under expressive structural roof.
    for x in np.linspace(-9.7,9.3,17):
      box(s,'H_LibrarySpandrel',x,.68,.12,.20,3.65,4.04,'ochre')
      if int(x*2)%2==0:
        beam(s,'H_DeepLibraryEave',(x,6.4,.82),(x,6.4,-.15),.09,'warmwood')
    # Real library shelving and tables behind the glazing; visible from player scale.
    for x,z in [(-6,3.3),(-4,4.9),(-6,7.1),(3.8,3.4),(5.5,6.4)]:
      box(s,'H_StudyFurniture',x,z,1.5,.55,1.1,1.45,'copperdark')
      box(s,'H_BookStack',x,z+.5,1.4,.28,1.1,2.8,'warmwood')
    for x,z in [(-11.1,9.1),(10.9,10.5)]:
      if s._publicCorridor.distance(Point(x,z))>3:s.garden(x,z,2.3,.9,'green')



def island_functional_landscape(s):
  """Site-specific finishing; no random blanket bushes, keep 4.8 wide circulation clean."""
  from shapely.geometry import Point
  site=scale(Point(0,0).buffer(1,resolution=120),s.rx*.93,s.rz*.93)
  # Building unions include tall roofs; this is intentionally conservative for outdoor props.
  footprints=[]
  for _,m in s.building_parts:
    if np.min(m.vertices[:,1])<3.0:
      footprints.append(Polygon(m.vertices[:,[0,2]]).convex_hull.buffer(.35))
  def safe(x,z,clear=1.0):
    p=Point(x,z)
    return site.contains(p.buffer(clear)) and s._publicCorridor.distance(p)>clear+1.0 and all(q.distance(p)>clear for q in footprints)
  # One real programmatic garden per building + separate planting groups; no repeated template.
  if s.code=='B':
    for x,z,w,d,col in [(-10.8,-6.2,2.6,1.0,'green'),(-8.6,9.1,2.8,.9,'deepgreen'),(3.1,8.8,2.4,.9,'green')]:
      if safe(x,z,1.1):s.garden(x,z,w,d,col)
    for x,z,t,k in [(-11.1,8.7,.66,'pink'),(-12.4,-10.2,.72,'olive'),(1.9,9.7,.61,'pink'),(-1.6,-9.5,.65,'olive')]:
      if safe(x,z,1.1):s.tree(x,z,t,k)
    # Distinct low accessible tactile garden, no fake heavy concrete plaza center.
    for x,z in [(-.5,-11.7),(2.6,-10.0),(3.8,10.2)]:
      if safe(x,z,.65):s.box('SensoryTimberBench',x,z,1.4,.4,.15,.48,'wood2')
  elif s.code=='D':
    # Civic order: axial inlays and organized shade grove at the margins.
    for x,z in [(2.2,-10.6),(4.8,-9.3),(6.4,-8.4)]:
      if safe(x,z,.7):s.box('CivicWayfindingInlaidCopper',x,z,.25,1.45,.14,.185,'bronze2')
    for x,z in [(-11,12.8),(-12.3,9.7),(10,-12),(14.7,-9.4)]:
      if safe(x,z,1.3):s.tree(x,z,.68,'olive')
    for x,z in [(-10.1,12.5),(13.0,-9.3)]:
      if safe(x,z,1.4):s.garden(x,z,2.5,1.1,'deepgreen')
  elif s.code=='E':
    # Ecological learning: a low wetland, sedge-rich edge and shaded outdoor platform.
    for x,z in [(-8.8,9.9),(-10.2,7.4),(-9.0,-10.0),(8.9,-11.0)]:
      if safe(x,z,1.0):s.tree(x,z,.65,'olive')
    for x,z,w,d in [(-8.1,7.9,2.2,1.35),(-5.0,10.6,2.6,1.1),(5.5,-9.9,2.8,.9)]:
      if safe(x,z,1.1):s.garden(x,z,w,d,'deepgreen')
    # One low timber observation boardwalk rather than another enclosed building.
    x,z=(-5.5,-2.55)
    if safe(x,z,2.1):
      s.box('EcologyLearningDeck',x,z,4.0,2.1,.16,.40,'wood2')
      for xx in [-7.1,-5.5,-3.9]:s.beam('DeckDrainageSlat',(xx,.45,z-.9),(xx,.45,z+.9),.045,'copperdark')
  elif s.code=='H':
    # Learning agora centered on reading, not a toy stadium.
    for x,z in [(-12.0,10.5),(11.0,10.0),(-10.8,-8.5),(9,-9.5)]:
      if safe(x,z,1.2):s.tree(x,z,.68,'pink' if x<0 else 'olive')
    for x,z in [(-10.2,8.5),(9.3,8.5)]:
      if safe(x,z,1.3):s.garden(x,z,3.0,1.2,'green')
    for x,z in [(5.3,-3.6),(7.2,-3.3)]:
      if safe(x,z,.6):s.box('StudentReadingBench',x,z,1.3,.35,.20,.52,'wood2')

def keep_in_footprint(s):
  """Final local building placement adjustments before auditable GLB export.
  Scale only spatial envelope modestly: never modify world or island dimensions.
  """
  factors={
    'B':(1.,1.,0.,0.),
    'D':(.915,.915,-.45,-.45),
    'E':(.940,.92,-.25,-.20),
    'H':(.925,.94,.0,-.30),
  }
  fx,fz,dx,dz=factors[s.code]
  for n,m in s.building_parts:
    v=m.vertices.copy();v[:,0]=v[:,0]*fx+dx;v[:,2]=v[:,2]*fz+dz;m.vertices=v

def audit(s):
  # repeat actual source-geometry 2d footprint analysis; own checks independent from R18 reports.
  island=scale(Point(0,0).buffer(1,resolution=150),s.rx*.955,s.rz*.955)
  public=s._publicCorridor
  rows=[];tri=0
  for name,m in s.building_parts:
    tri+=len(m.faces);v=m.vertices
    h=Polygon(v[:,[0,2]]).convex_hull
    if h.is_empty:continue
    out=float(h.difference(island).area)
    bottom=float(v[:,1].min());top=float(v[:,1].max())
    road=float(h.intersection(public).area) if bottom<2.85 else 0.0
    if out>.025 or road>.025:rows.append(dict(part=name,out=round(out,3),road=round(road,3),ymin=round(bottom,2),ymax=round(top,2)))
  return {'code':s.code,'land':r.r12.SIZES[s.code],'roadCoreWidth':4.8,'buildingTriangles':tri,'buildingParts':len(s.building_parts),'fails':rows[:80],'failCount':len(rows),'status':'OFFLINE_GEOMETRY_ONLY_NOT_GAME_TEST'}


def render_landmark_close(s):
  """Same actual source geometry as GLB; camera-only detailed inspection, never a fake concept."""
  import vtk
  ren=s.vtk_renderer()
  ren.GradientBackgroundOn();ren.SetBackground(.96,.971,.968);ren.SetBackground2(.83,.90,.915)
  win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(1280,890);win.SetMultiSamples(8);win.AddRenderer(ren)
  cam=ren.GetActiveCamera();cam.ParallelProjectionOn();cam.SetFocalPoint(0,3,1.4);cam.SetPosition(25,20,-35);cam.SetViewUp(0,1,0);cam.SetParallelScale(11.3)
  ren.ResetCameraClippingRange();win.Render()
  w2i=vtk.vtkWindowToImageFilter();w2i.SetInput(win);w2i.SetInputBufferTypeToRGB();w2i.ReadFrontBufferOff();w2i.Update()
  writer=vtk.vtkPNGWriter();writer.SetFileName(str(HERE/'renders'/f'{s.code}_architecture_close.png'));writer.SetInputConnection(w2i.GetOutputPort());writer.Write();win.Finalize()

def make(code,views=('hero','top')):
  s=Design(code);s.terrain();r.build_pedestrian_routes(s);BUILDS[code](s);human_scale_detail(s);keep_in_footprint(s);island_functional_landscape(s);r.sparse_perimeter(s)
  q=audit(s)
  # export accurately grouped GLB per material
  scene=trimesh.Scene();total=0
  for key,m in s.meshes.items():
    if not m:continue
    joined=trimesh.util.concatenate(m)
    joined.visual.face_colors=np.asarray([*r.base.rgb(r.base.C[key]),255],dtype=np.uint8)
    scene.add_geometry(joined,geom_name=f'{code}_{key}');total+=len(joined.faces)
  dest=HERE/'models'/f'{code}_R20_design.glb';dest.write_bytes(scene.export(file_type='glb'))
  q['totalTriangles']=total;q['GLBBytes']=dest.stat().st_size
  for view in views:r.render(s,view)
  render_landmark_close(s)
  return q

def main():
  codes=sys.argv[1:] or list('BDEH')
  results={}
  for c in codes:
    results[c]=make(c,('hero','top','front','back','left','right'))
    print(c,'total triangles',results[c]['totalTriangles'],'problems',results[c]['failCount'],flush=True)
    if results[c]['fails']:print(' ',results[c]['fails'][:5],flush=True)
  (HERE/'qa'/'geometry_audit.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
