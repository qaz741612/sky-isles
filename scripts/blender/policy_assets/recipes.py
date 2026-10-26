"""Seven authored layouts following the supplied 45-degree references. MIT.
Dimensions derive from architectural/player proportions, not a radius-9 constraint.
"""
import math, bpy
from shapely import affinity
from shapely.geometry import Point,Polygon,box
from .kit import G

def furnish(k,x0,x1,y0,y1,kind='reading'):
 mid=(x0+x1)/2
 if kind in ['reading','care','office']:
  k.shelf(kind+'_RearLibrary',mid,y1-.38,min(3.4,x1-x0-1),1.55)
  for x in [x0+1.15,x1-1.15]:
   k.table(kind+'_Table',x,(y0+y1)/2,1.25,.75)
   k.chair(kind+'_Chair',x,(y0+y1)/2-.75,math.pi)
   k.chair(kind+'_Chair',x,(y0+y1)/2+.75)
 if kind=='work':
  for x in [x0+1.3,x1-1.3]:
   k.table('WorkshopBench',x,(y0+y1)/2,1.9,.85)
   for j in range(3):k.box('CraftDisplayObject',(x-.55+j*.55,(y0+y1)/2,.95),(.25,.25,.26),['cream','tealCloth','woodDark'][j],k.parent,.035)
  k.shelf('WorkshopStorage',mid,y1-.38,2.4,1.5)
 if kind=='station':
  k.use('Interior');k.box('TicketCounter',(x0+1.4,y1-1, .76),(2.2,.65,1.02),'woodLight')
  k.box('CounterInset',(x0+1.4,y1-1.34,.85),(1.8,.03,.48),'tealCloth')
  k.bench('IndoorWaitingBench',x1-1.8,y1-1.1,2.2)

def garden_edges(k,points):
 for n,(x,y,w)in enumerate(points):k.planter('AuthoredFlowerBorder_'+str(n),x,y,w,.68)

def court_rings(k,x,y,r=3.3):
 k.use('Landscape');k.exclusions.append(Point(x,y).buffer(r+.1,resolution=48))
 for a,b,m in [(0,r*.62,'paver0'),(r*.62,r*.83,'pathPeach'),(r*.83,r,'pathSage')]:
  # paver material registered before use; the centre is genuine stone, not a decal.
  if m=='paver0':m='stone'
  k.cyl('CourtyardCentreStone',(x,y,.0245),b,.025,m,v=96)if a==0 else k.arc('CourtyardStoneInlay',x,y,a,b,.012,.025,m,steps=96)

def station(k):
 k.hall('ModernYuanliStation',-5.9,5.6,1.25,5.1,3.05,2.93,1.48,0)
 furnish(k,-5.9,5.6,1.25,5.1,'station');k.emblem('clock',0,1.12,3.58,.91)
 k.bench('FrontHallWaitingSeat',3.0,2.45,2.1)
 k.use('Interior');k.box('FrontTicketDesk',(-3.4,2.20,.74),(1.7,.64,1.0),'woodLight');k.box('TicketDeskTop',(-3.4,2.20,1.28),(1.82,.73,.10),'trim')
 k.use('Architecture');k.box('RightScreen',(5.38,1.12,1.64),(.18,.20,2.9),'wood')
 # Long, side-open platform canopy and full short train behind station.
 p=k.pergola('SidePlatformCanopy',0,7.1,15.4,2.15,3.15,True)
 k.use('ThemeFacilities');platform=k.group('PlatformAndDisplayTrack')
 k.box('RaisedPassengerPlatform',(0,5.90,.19),(15.6,1.8,.36),'stone',platform,.04)
 for j in range(42):k.box('PlatformTactileBlock',(-7.45+j*.36,6.64,.39),(.28,.15,.018),'slide',platform,.006)
 for y in [7.31,8.41]:k.beam('SteelDisplayRail',(-8.1,y,.20),(8.1,y,.20),.06,'gray',platform)
 for j in range(34):k.box('TimberTrackSleeper',(-7.5+j*15/33,7.86,.11),(.12,1.70,.12),'woodDark',platform,.01)
 train=k.group('TrainRollingStock',platform);train.location.x=1.9
 for c in [-1,1]:
  cx=c*2.55;car=k.group('EditableCarriage',train)
  k.box('CarriageBody',(cx,7.86,1.19),(4.90,1.44,1.50),'cream',car,.17)
  k.box('CarriageTealBelt',(cx,7.12,.86),(4.65,.045,.25),'rail',car,.025)
  k.box('CarriageRoof',(cx,7.86,2.01),(4.74,1.47,.19),'gray',car,.11)
  for y in [7.12,8.60]:
   for j in range(7):k.box('PassengerWindow',(cx-1.9+j*.63,y+(-.012 if y<7.86 else .012),1.50),(.46,.035,.50),'trainGlass',car,.05)
   for xx in [cx-1.35,cx+1.35]:k.box('TrainDoor',(xx,y,1.18),(.48,.035,1.14),'trim',car,.03)
  for xx in [cx-1.5,cx+1.5]:
   for y in [7.31,8.41]:o=k.cyl('TrainWheel',(xx,y,.49),.26,.12,'gray',car,20);o.rotation_euler.x=math.pi/2
  # Distinct sloped cab at the outer end; real front glass and paired headlights.
  sign=c;xx=cx+sign*2.52
  outline=[(xx-sign*.1,.55),(xx+sign*.32,.65),(xx+sign*.36,1.3),(xx-sign*.08,1.91)]
  G.prism_xz('SlopingTrainCab',outline,7.86,1.36,k.M['cream'],car)
  o=k.box('DriverWindscreen',(xx+sign*.18,7.86,1.53),(.04,1.07,.54),'rail',car,.06);o.rotation_euler.y=sign*-.3
  for y in [7.40,8.32]:k.sphere('TrainHeadlamp',(xx+sign*.34,y,.89),(.035,.11,.07),'trim',car,2)
 # Waiting shelter and forecourt stay outside central arrival.
 k.pergola('SmallWaitingShelter',-7.5,.1,2.6,1.4,2.45,True);k.bench('ShelterWaitingBench',-7.5,.20,2.0);k.board('StationRouteMap',-8.2,.70,1.0,False)
 court_rings(k,-.6,-4.2,3.65);k.treecourt('StationForecourtTree',-.6,-4.2)
 garden_edges(k,[(-3.9,.7,2.9),(3.9,.7,2.5),(-7,-5.9,1.1),(6.4,-5.2,1.8),(-6.8,-3.5,2.4),(4.2,-6.7,2.3)])
 for n,(x,y,h,r)in enumerate([(-8.8,3.4,4.2,1.1),(8.0,-1.0,3.9,1.05)]):k.tree('StationShadeTree'+str(n),x,y,h,r)
 k.board('TransportVisionInfo',6.5,-2.9,1.2,False)
 for x,y in [(-6.4,-1.0),(7.8,-4.1),(-2.6,-7.8)]:k.lamp('StationLantern',x,y)
 k.pot('StationDoorFern',-1.7,.15);k.pot('StationDoorFern',1.7,.15);k.reserve(3,-2.4)

def senior(k):
 k.hall('CommunityLifeHall',-4.8,4.6,1.30,5.75,3.05,2.96,1.03,.3)
 furnish(k,-4.8,4.6,1.3,5.75,'care');k.emblem('care',.3,.30,3.31,.78)
 # Continuous lightweight galleries flank a wide garden forecourt.
 for n,x,w in [('WestRestGallery',-7,3.3),('EastGardenGallery',6.8,3.1)]:
  k.pergola(n,x,2.3,w,3.15,2.55,n=='WestRestGallery');k.bench(n+'_FacingGarden',x,2.65,2.3)
 k.table('OutdoorTeaTable',-6.8,1.35,1.25,.65)
 for x in [-7.5,-6.1]:k.chair('OutdoorRestChair',x,1.4,math.pi/2)
 court_rings(k,-.9,-3.4,4.4);k.treecourt('CommunityConversationTree',-.9,-3.4)
 garden_edges(k,[(-3.1,.72,2.7),(3.3,.72,2.5),(-7,-3.3,1.3),(5.8,-2.7,2.6),(-5.7,-6.6,1.4),(5.7,5,2.1)])
 for n,(x,y,h,r)in enumerate([(-8.4,5.6,4.3,1.2),(8,4.4,4.1,1.15),(5.8,-5.0,3.5,.95)]):k.tree('GardenShade'+str(n),x,y,h,r)
 k.bench('GardenFacingBench',-4.8,-6.4,2.0,math.pi);k.bench('GardenFacingBench',4,-5.6,2.0,math.pi)
 k.board('CareInformation',7.3,-4.3,1.1,False)
 for x,y in [(-8,-.8),(7.5,.2),(4.2,-6.8)]:k.lamp('GardenLantern',x,y)
 for x in [-1.4,1.9]:k.pot('EntryFern',x,.25)
 k.reserve(2.7,-1.9)

def greenhouse(k,x,y,w=3.6,d=4.8):
 k.use('Architecture');p=k.group('AgriculturalGlasshouse');floor=.20;low=2.15;peak=3.25
 k.box('GreenhouseMasonryBase',(x,y,.18),(w,d,.34),'cream',p,.03)
 for j in range(5):
  yy=y-d/2+j*d/4
  for side in [-1,1]:
   k.beam('GreenhouseUpright',(x+side*w/2,yy,.3),(x+side*w/2,yy,low),.075,'trim',p)
   k.beam('GreenhouseRafter',(x+side*w/2,yy,low),(x,yy,peak),.075,'trim',p)
  k.beam('GreenhouseTie',(x-w/2,yy,low),(x+w/2,yy,low),.07,'trim',p)
 for side in [-1,1]:
  k.box('GreenhouseSideGlass',(x+side*w/2,y,(low+.35)/2),(.035,d,low-.35),'glass',p,.003)
  k.beam('GreenhouseEave',(x+side*w/2,y-d/2,low),(x+side*w/2,y+d/2,low),.08,'trim',p)
  # Closed pitched glazing slab, proper thickness and frame junctions.
  roof=G.prism_xz('GreenhouseRoofGlass',[(x+side*w/2,low),(x,peak),(x,peak-.045),(x+side*w/2,low-.045)],y,d,k.M['glass'],p)
 for yy in [y-d/2,y+d/2]:
  G.prism_xz('GreenhouseEndGlass',[(x-w/2,.35),(x+w/2,.35),(x+w/2,low),(x,peak),(x-w/2,low)],yy,.035,k.M['glass'],p)
  for dx in [-.45,.45]:k.beam('GreenhouseDoorFrame',(x+dx,yy,.25),(x+dx,yy,2.05),.06,'trim',p)
 k.beam('GreenhouseRidge',(x,y-d/2,peak),(x,y+d/2,peak),.08,'trim',p)
 k.exclusions.append(box(x-w/2,y-d/2,x+w/2,y+d/2))
 for xx in [x-w*.28,x+w*.28]:
  k.planter('GreenhouseRaisedBed',xx,y, .72,d-.55,.50,False)
  for j in range(6):
   pot=k.pot('SeedlingPot',xx,y-d*.35+j*d*.14);pot.location.z=.42
   k.shrub('GreenhouseCropFoliage',xx,y-d*.35+j*d*.14,.65,.27,False)
 k.rooms.append({'name':'AgriculturalGlasshouse','footprint':[x-w/2,y-d/2,x+w/2,y+d/2],'door':None,'peak':peak})
 return p

def industry(k):
 k.hall('YouthInnovationWorkshop',-5.5,3.3,1.25,5.75,3.0,3.04,1.55,-1.0)
 furnish(k,-5.5,3.3,1.25,5.75,'work');k.emblem('sprout',-1,.25,3.32,.78)
 greenhouse(k,6.0,2.35,3.5,4.7)
 k.pergola('CraftExhibitionCanopy',5.7,6.5,6.0,1.7,2.85,True)
 k.use('ThemeFacilities');p=k.group('SmallIndustryDisplay')
 for j,(x,y)in enumerate([(4.3,6.3),(5.3,6.8),(6.7,6.4)]):
  k.box('TimberShippingCrate',(x,y,.60),(.83,.77,1.12),'woodLight',p,.025)
  for xx in [-.35,0,.35]:k.box('CrateBoardBatten',(x+xx,y-.4,.6),(.045,.04,1.10),'wood',p,.008)
  for zz in [.18,1.02]:k.box('CrateEndBand',(x,y-.42,zz),(.80,.045,.06),'woodDark',p,.008)
 # Miniature forklift is an exhibit, no driver or NPC.
 cx,cy=8.0,5.4;k.box('ForkliftChassis',(cx,cy,.47),(1.2,.85,.62),'tealCloth',p,.10)
 for xx in [cx-.40,cx+.40]:
  for yy in [cy-.46,cy+.46]:o=k.cyl('ForkliftWheel',(xx,yy,.22),.22,.12,'gray',p,20);o.rotation_euler.x=math.pi/2
 for xx in [cx-.35,cx+.35]:k.beam('ForkliftCabPillar',(xx,cy+.25,.5),(xx,cy+.25,1.8),.055,'rail',p)
 k.box('ForkliftRoof',(cx,cy+.05,1.82),(1.05,.90,.09),'rail',p,.025)
 for xx in [cx-.22,cx+.22]:k.box('ForkliftRaisedFork',(xx,cy-.95,.13),(.08,1.3,.08),'gray',p,.008)
 court_rings(k,-1.5,-4.0,3.8);k.treecourt('MakerCourtTree',-1.5,-4.0)
 k.board('LocalCraftDisplay',-7.6,.0,1.25);k.board('YouthInformation',-6.0,-.7,1.15,False)
 garden_edges(k,[(-3.8,.72,2.8),(2.2,.70,1.4),(-7.0,-4,1.2),(7,-3.1,2.7),(3.9,-5.8,2.8)])
 for n,(x,y,h,r)in enumerate([(-8,3.9,4,1.2),(7.5,-1.8,4,1.1),(-5.9,6.5,3.8,1.0)]):k.tree('ProductiveGardenTree'+str(n),x,y,h,r)
 for x,y in [(-7,-2),(7,-4.8),(1.6,-7.3)]:k.lamp('MakerLantern',x,y)
 k.pot('MakerFern',-2.6,.18);k.pot('MakerFern',.6,.18);k.reserve(2,-2.0)

def park_bridge(k,x,y):
 k.use('ThemeFacilities');p=k.group('RealTimberPondBridge');xs=[x-1.7+3.4*j/20 for j in range(21)]
 for xx in xs:
  t=(xx-x+1.7)/3.4;z=.15+.48*math.sin(math.pi*t);k.box('BridgeDeckBoard',(xx,y,z),(.155,1.30,.09),'woodLight',p,.012)
 for side in [-1,1]:
  k.box('BridgeStoneAbutment',(x+side*1.7,y,-.18),(.45,1.5,.48),'stone',p,.035)
  k.tube('BridgeStructuralStringer',[(xx,y+side*.48,.075+.48*math.sin(math.pi*(xx-x+1.7)/3.4))for xx in xs],.065,'wood',p)
  for j in range(6):
   t=j/5;xx=x-1.7+3.4*t;z=.15+.48*math.sin(math.pi*t);k.beam('BridgeHandrailPost',(xx,y+side*.70,z),(xx,y+side*.70,z+.85),.07,'wood',p)
  for offset in [.50,.90]:k.tube('CurvedFootbridgeHandrail',[(xx,y+side*.70,.15+.48*math.sin(math.pi*(xx-x+1.7)/3.4)+offset)for xx in xs],.035,'woodLight',p)

def park(k):
 k.hall('OpenGardenPavilion',.4,6.4,2.7,5.8,2.75,2.7,.70,None,False,False)
 # Remove glazing and sills from this truly open shelter, retaining columns/roof.
 p=k.groups['Architecture'].children[0]
 for o in list(p.children_recursive):
  if any(s in o.name for s in ['Glass','Sill','Transom','TimberMullion','SidePost','ArchHeader']):bpy.data.objects.remove(o,do_unlink=True)
 for o in p.children_recursive:
  if 'CornerPier'in o.name:
   o.data.materials.clear();o.data.materials.append(k.M['wood'])
 k.use('Architecture')
 for j in range(12):k.box('PavilionRearSunScreen',(1.0+j*.44,5.70,1.42),(.065,.095,2.30),'woodLight',p,.012)
 k.bench('PavilionRestBench',3.4,4.85,3.0)
 lawn=Point(-3.7,-1.6).buffer(3.9,resolution=64);k.use('Landscape');k.solid('PetFriendlyGrass',lawn,.025,.07,'grass');k.exclusions.append(lawn.buffer(.22))
 k.solid('CurvedGardenPathBorder',lawn.buffer(.45).difference(lawn.buffer(.18)),.015,.035,'trim')
 pond=Point(4,-3.3).buffer(3.0,resolution=64);pond=affinity.scale(pond,1.22,1.0,origin=(4,-3.3));k.water_shapes.append(pond);k.solid('RealPondWater',pond,-.16,.10,'water');k.solid('PondStoneBank',pond.buffer(.20).difference(pond),-.12,.37,'cream')
 park_bridge(k,4.0,-6.0)
 k.use('ThemeFacilities');p=k.group('PetFriendlyLowPlay')
 for j in range(8):k.box('DogRampSlat',(-5.6+j*.19,-1.0,.10+j*.08),(.19,.90,.08),'woodLight',p,.015)
 for xx in [-5.7,-4.2]:k.beam('LowRampSafetyHandrail',(xx,-1.5,.15),(xx,-1.5,1.0),.055,'wood',p)
 # Real open circular timber tunnel, closed annular walls.
 o=k.arc('PetTunnel',0,0,.40,.51,0,1.15,'woodLight',p,steps=48);o.rotation_euler.x=math.pi/2;o.location=(-2.9,-1.0,.55)
 for xx,yy,h in [(-1.9,-.8,.35),(-2.4,-1.8,.55),(-1.3,-2.2,.40)]:k.cyl('LowPetSteppingStump',(xx,yy,h/2+.08),.24,h,'wood',p,20)
 for x,y in [(3.5,-2.1),(5.1,-3.1),(2.0,-4.2)]:
  k.cyl('LilyPad',(x,y,-.035),.27,.02,'leaf',p,24)
 for x,y in [(1.6,-2),(6.7,-1.8),(2.1,-4.7)]:
  for j in range(5):k.beam('PondReed',(x+.08*j,y,.03),(x+.08*j-.15,y+.08,.65+.09*(j%3)),.035,'leaf',p)
 for x,y,s in [(1.8,-1.3,.45),(6.5,-1.4,.60),(2.3,-4.8,.40)]:k.sphere('WaterEdgeRock',(x,y,.13),(s,s*.7,s*.75),'gray',p,2)
 k.treecourt('GardenRestTree',-.5,-6.1);k.bench('WestParkBench',-8,-2.8,2.1,-.5)
 garden_edges(k,[(-7,3.4,2.7),(-4.2,5.5,2.1),(2.8,2.1,2.3),(6.7,3.3,1.5),(7.8,-6.2,1.6)])
 for n,(x,y,h,r)in enumerate([(-7.5,.2,4.3,1.4),(-5.6,4.8,4.6,1.35),(.2,6.8,4.5,1.3),(7.7,5.5,4.1,1.2)]):k.tree('PurposefulParkCanopy'+str(n),x,y,h,r)
 k.board('PetParkInformation',7.1,.8,1.0,False)
 for x,y in [(-7,-4.8),(-5.4,2.7),(7.6,-3.7)]:k.lamp('ParkLantern',x,y)
 k.reserve(1.4,1.0)

def digital(k):
 k.hall('CivicServiceHall',-4.8,5.1,1.1,6.2,3.20,3.08,1.20,.2)
 k.hall('WestServiceWing',-7.8,-4.4,1.4,5.4,2.8,2.85,.22,None,False)
 furnish(k,-4.8,5.1,1.1,6.2,'office');k.emblem('civic',.2,.10,3.47,.78)
 k.use('Interior');k.box('PublicServiceCounter',(2.8,3.3,.90),(3.1,.72,1.30),'cream');k.box('AccessibleServiceCounter',(.8,3.3,.70),(.9,.72,.90),'woodLight')
 k.pergola('NoticeShelter',7.3,.2,2.3,1.3,2.25,False);k.board('PublicNoticeBoard',7.3,.40,1.8,False)
 # Separate low digital information kiosk; no fictional policy text.
 k.hall('InformationKiosk',-8.0,-5.65,-1.5,.5,2.25,2.25,.25,None,False,False)
 k.use('ThemeFacilities');p=k.group('DigitalServiceFacilities')
 k.box('KioskScreenHousing',(-6.7,-1.56,1.20),(.75,.10,1.15),'rail',p,.035)
 for j in range(6):k.box('KioskTouchIcon',(-6.89+(j%2)*.38,-1.63,1.53-(j//2)*.31),(.22,.025,.18),'cream',p,.02)
 k.box('SelfServiceStele',(5.6,-3.6,1.2),(.75,.25,2.2),'cream',p,.10);k.box('SteleFace',(5.6,-3.75,1.35),(.55,.04,1.5),'tealCloth',p,.05)
 for j in range(4):k.box('SteleServiceLine',(5.6,-3.79,1.75-j*.28),(.34,.015,.045),'trim',p,.006)
 court_rings(k,-.2,-4.0,3.3);k.treecourt('CivicShadedWaitingTree',-3.8,-4.3)
 garden_edges(k,[(-3,.5,2.1),(3.4,.5,2.0),(6,-4.9,2.0),(-7.8,-4.3,1.2),(2.2,-7,2.0)])
 for n,(x,y,h,r)in enumerate([(-7.5,6.3,4.2,1.2),(7.6,4.6,4.3,1.25)]):k.tree('CivicGardenTree'+str(n),x,y,h,r)
 k.bench('WaitingSeat',1.9,-6.3,2.3,math.pi)
 for x,y in [(-8.6,-2.6),(6.6,-1.5),(4.6,-6.2)]:k.lamp('CivicLantern',x,y)
 for x in [-1.4,1.8]:k.pot('CivicDoorFern',x,-.1)
 k.reserve(1.5,-2.2)

def water(k):
 k.hall('DisasterManagementCentre',.15,8.3,1.9,6.8,3.03,2.95,1.12,3.6)
 furnish(k,.15,8.3,1.9,6.8,'office');k.emblem('water',3.6,.9,3.35,.78)
 loft,_=k.hall('UpperObservationRoom',.5,3.5,4.4,6.2,1.40,1.40,.18,None,False,False);loft.location.z=3.4;k.rooms[-1]['base']=3.4;k.rooms[-1]['peak']+=3.4
 k.use('Architecture');k.box('ObservationLoftFloor',(2,5.3,3.40),(3.2,2,.20),'cream')
 # Main water basin is a real cut into the platform, not a blue flat patch.
 pond=Polygon([(-8.8,-1),(-5.8,.8),(-1.5,1.2),(2.1,-.9),(7.1,-1.8),(8.0,-4.2),(5.4,-6.8),(-1.0,-7.1),(-7.0,-5.7)]).buffer(.40,resolution=12)
 k.water_shapes.append(pond);k.use('ThemeFacilities');k.solid('LowerRetentionWaterVolume',pond,-.20,.14,'water');k.solid('ContinuousFloodBasinCoping',pond.buffer(.23).difference(pond),-.10,.42,'cream')
 upper=box(-8.2,.9,-2.2,4.9);k.water_shapes.append(upper);k.solid('UpperChannelRaisedBed',upper,-.30,1.05,'stone');k.solid('UpperChannelWater',upper.buffer(-.18),.75,.10,'water')
 for x in [-8.25,-2.15]:k.box('CanalRetainingWall',(x,2.9,.70),(.22,4.25,1.5),'cream')
 # Floodgate with three bays, piers, open maintenance deck and control room.
 gate=k.group('ThreeBayFloodControlGate')
 for x in [-8.2,-6.2,-4.2,-2.2]:k.box('GatePier',(x,.9,1.02),(.28,.62,2.12),'cream',gate,.04)
 k.box('MaintenanceBridge',(-5.2,.9,2.08),(6.65,1.25,.25),'stone',gate,.035)
 for x in [-7.2,-5.2,-3.2]:
  k.box('RaisedSluiceGate',(x,1.14,1.36),(1.64,.12,1.1),'gray',gate,.035)
  for xx in [x-.66,x+.66]:k.beam('GateGuideRail',(xx,1.02,.9),(xx,1.02,2.4),.055,'rail',gate)
  # Closed curved falling sheet and localized foam. Static demonstration, no simulation.
  cross=[]
  for j in range(25):
   t=j/24;cross.append((.9-1.15*t,.78*(1-t)**.6-.06))
  verts=[]
  for xx,off in [(x-.70,0),(x+.70,0),(x-.70,-.045),(x+.70,-.045)]:verts.extend((xx,y,z+off)for y,z in cross)
  n=len(cross);faces=[]
  for j in range(n-1):faces.extend([(j,j+1,n+j+1,n+j),(2*n+j,3*n+j,3*n+j+1,2*n+j+1),(j,2*n+j,2*n+j+1,j+1),(n+j,n+j+1,3*n+j+1,3*n+j)])
  faces.extend([(0,n,3*n,2*n),(n-1,3*n-1,4*n-1,2*n-1)])
  G.mesh('FallingWaterSheet',verts,faces,k.M['water'],gate,True)
  for j in range(12):k.sphere('CascadeFoam',(x-.68+j*.125,-.38+.06*math.sin(j),-.025),(.11,.08,.035),'white',gate,1)
 for y in [.35,1.45]:
  for x in [-8.2,-6.5,-4.8,-3.1,-2.2]:k.beam('MaintenanceRailPost',(x,y,2.2),(x,y,3.15),.045,'rail',gate)
  for z in [2.65,3.12]:k.beam('MaintenanceHorizontalRail',(-8.3,y,z),(-2.1,y,z),.04,'rail',gate)
 booth,_=k.hall('FloodgateControlBooth',-3.7,-2.1,2.6,4.3,1.95,1.95,.10,None,False,False);booth.location.z=1.8;k.rooms[-1]['base']=1.8;k.rooms[-1]['peak']+=1.8
 k.use('ThemeFacilities');k.box('ControlBoothSupportDeck',(-2.9,3.45,1.82),(2.0,2.1,.22),'stone')
 for x in [-3.6,-2.2]:
  for y in [2.7,4.2]:k.box('ControlBoothSupportPier',(x,y,1.05),(.20,.20,1.55),'cream')
 # Safe lower observation deck beside basin, with a schematic relief map.
 deck=Point(-6.0,-6.8).buffer(2.1,resolution=48);k.solid('ObservationTimberDeck',deck,-.1,.20,'woodLight');k.exclusions.append(deck)
 k.box('WatershedDisplayTable',(-6,-6.8,.90),(1.9,1.05,.13),'woodLight',r=.035)
 for side in [-1,1]:k.box('WatershedTableLeg',(-6+side*.65,-6.8,.46),(.13,.65,.80),'wood')
 k.tube('RiverSchematic',[(-6.7+j*.07,-6.8+.22*math.sin(j*.33),.975)for j in range(21)],.035,'courtBlue')
 for x,y in [(-.6,-4.6),(6,-3.9),(1.2,.0)]:
  for j in range(6):k.beam('RainGardenReed',(x+j*.09,y,.04),(x+j*.09-.15,y,.7+.12*(j%3)),.035,'leaf')
  k.sphere('RainGardenStone',(x+.4,y+.3,.15),(.4,.3,.35),'gray',sub=2)
 k.board('ResilienceInformation',8,-.6,1.5)
 garden_edges(k,[(1.6,1.35,2.0),(6.3,1.35,2.3),(-8.4,4.7,1.0),(8.0,-6.5,1.3)])
 for n,(x,y,h,r)in enumerate([(-.8,7.1,4.4,1.2),(9.0,4.2,4.5,1.25)]):k.tree('WaterGardenTree'+str(n),x,y,h,r)
 k.bench('WaterObservationBench',5.6,-.9,2.0)
 for x,y in [(-9.2,2),(8.8,-3.4),(8.2,6.6)]:k.lamp('WaterLantern',x,y)
 k.reserve(7.8,.2)

def education(k):
 k.hall('LearningHall',-3.8,3.7,1.8,6.1,3.45,3.45,1.3,-.1)
 k.hall('WestClassroomWing',-7.5,-3.6,2.0,5.75,2.75,2.90,.20,None,False)
 k.hall('LibraryReadingWing',3.4,7.8,.5,5.7,2.85,2.85,.57,None,False)
 furnish(k,-3.8,3.7,1.8,6.1,'reading');furnish(k,3.4,7.8,.5,5.7,'reading')
 k.emblem('clock',-.1,1.66,3.82,.92);k.emblem('book',5.7,.1,2.66,.65)
 # Real scaled half court (not a complete school squeezed into a toy island).
 court=box(-7.5,-6.6,.3,-1.2);k.exclusions.append(court.buffer(.18));k.use('ThemeFacilities');p=k.group('OutdoorActivityHalfCourt')
 k.solid('CourtCreamBorder',court.buffer(.17),.028,.055,'trim',p)
 k.box('HalfCourtBlue',(-5.5,-3.9,.10),(4.0,5.30,.035),'courtBlue',p,.008)
 k.box('HalfCourtClay',(-1.6,-3.9,.10),(3.80,5.30,.035),'courtCoral',p,.008)
 for x in [-7.35,.15]:k.beam('CourtSideline',(x,-6.43,.13),(x,-1.37,.13),.038,'white',p)
 for y in [-6.43,-1.37]:k.beam('CourtBaseline',(-7.35,y,.13),(.15,y,.13),.038,'white',p)
 k.beam('CourtCentreLine',(-3.5,-6.43,.13),(-3.5,-1.37,.13),.038,'white',p)
 k.arc('HalfCourtArc',-7.18,-3.9,2.45,2.49,.116,.022,'white',p,start=-math.pi/2,end=math.pi/2,steps=72)
 k.box('BasketballPost',(-8.0,-3.9,1.6),(.11,.11,3.1),'rail',p,.02);k.beam('BasketballReach',(-8,-3.9,2.8),(-7.35,-3.9,2.8),.09,'rail',p)
 k.box('BasketballBackboard',(-7.32,-3.9,2.80),(.10,1.32,.88),'rail',p,.035);k.box('BackboardWhiteInset',(-7.25,-3.9,2.8),(.015,1.14,.71),'cream',p,.015)
 k.arc('BasketballRim',-6.95,-3.9,.22,.245,2.46,.032,'coral',p,steps=48)
 for j in range(8):
  a=j*math.tau/8;k.tube('OpenBasketballNet',[(-6.95+.22*math.cos(a),-3.9+.22*math.sin(a),2.46),(-6.95+.14*math.cos(a),-3.9+.14*math.sin(a),2.10)],.009,'white',p,6)
 k.treecourt('ReadingCourtyardTree',5.0,-4.8);k.pergola('OutdoorReadingPergola',8,-2.6,2.0,1.4,2.35)
 k.board('SchoolInformation',6.8,-1.3,1.25,False)
 garden_edges(k,[(-5.6,1.45,2.8),(2.3,1.2,1.6),(-4.3,-7.7,2.2),(7.8,-5.5,1.0)])
 for n,(x,y,h,r)in enumerate([(-8.7,3,4.2,1.2),(-6.0,6.5,4.3,1.2),(8.5,5.5,4,1.1)]):k.tree('CampusShadeTree'+str(n),x,y,h,r)
 k.bench('CourtCaregiverSeat',-3.5,-7.5,2.3,math.pi)
 for x,y in [(-8.7,-.8),(2.5,-6.6),(8,-.8)]:k.lamp('CampusLantern',x,y)
 for x in [-1.6,1.4]:k.pot('SchoolEntryFern',x,.65)
 k.reserve(1.7,-1.6)

RECIPES={'transport':station,'senior':senior,'industry':industry,'environment':park,'digital':digital,'water':water,'education':education}


def finish_gardens(k,key):
 # Authored bed centre-lines establish courtyard edges; no vacancy search/random placement.
 beds={
 'transport':[('WestArrivalFlowers',[(-8.8,-.4),(-9.0,1.0),(-8.9,2.0)]),('WaitingCourtBorder',[(-6.3,-5.2),(-5.7,-5.4),(-4.8,-5.6)]),('StationFrontGarden',[(2.0,-7.6),(3.6,-7.4),(5.0,-6.8)])],
 'senior':[('QuietGardenWest',[(-7.7,-1.6),(-7.9,-3.0),(-7.1,-4.4)]),('RestCourtFlowers',[(2.8,-6.5),(3.7,-5.8),(4.3,-4.8)]),('BackGalleryGarden',[(3.5,6.6),(5.1,6.4),(6.3,5.8)]),('WestShelterGarden',[(-7.7,4.7),(-6.7,5.5),(-5.5,5.9)])],
 'industry':[('MakerForecourtGarden',[(-7.7,-2.4),(-7.8,-3.6),(-7.1,-5.0)]),('GreenhouseVisitorBorder',[(6.7,-3.9),(6.0,-4.5),(4.8,-5.1)]),('ProductiveGardenEdge',[(1.5,-7.4),(2.5,-7.2),(3.2,-6.8)])],
 'environment':[('WoodlandBackBorder',[(-7.7,2.4),(-6.5,3.7),(-4.6,4.6),(-2.3,5.8)]),('LawnGardenCrescent',[(-7.5,-3.4),(-6.6,-4.4),(-5.1,-5.2),(-3.4,-5.6)]),('ReedAndFlowerBank',[(.6,-1.0),(.8,-2.0),(1.1,-2.8)]),('PondFlowerBorder',[(6.8,-.9),(7.6,-2.2),(7.7,-3.2)]),('PavilionPlantedEdge',[(6.8,1.7),(7.2,2.8),(7.2,3.8)])],
 'digital':[('WestServiceCourtGreen',[(-8.0,-3.1),(-7.5,-4.3),(-6.6,-5.2)]),('WaitingGardenFront',[(.8,-6.9),(2.0,-7.3),(3.5,-7.0)]),('EastServiceGarden',[(8.0,1.5),(8.0,3.0),(7.8,4.0)])],
 'water':[('RainGardenBack',[(-1.3,6.5),(-1.2,7.3),(.0,7.5)]),('BasinGardenWest',[(-9.3,-3.5),(-8.9,-4.9),(-7.8,-5.8)]),('EastRainGarden',[(8.6,-4.9),(8.9,-3.6),(8.9,-2.7)])],
 'education':[('ClassroomGardenEdge',[(-8.7,1.1),(-8.8,2.4),(-8.2,4.0)]),('LibraryGardenFlowers',[(8.5,-2.0),(8.6,-3.2),(8.1,-4.0)]),('ReadingCourtBorder',[(3.7,-7.5),(5.3,-7.5),(6.8,-6.9)])]
 }
 for n,pts in beds[key]:k.garden_ribbon(n,pts,.75)
 if key=='industry':
  k.use('Landscape');p=k.group('WorkshopClimbingGarden')
  for j in range(5):
   k.shrub('WorkshopFacadeClimber',-5.38+(.1 if j%2 else 0),1.06,.55+j*.38,.24,False,p)
