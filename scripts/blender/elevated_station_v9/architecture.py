"""Authored flat metal station, viaduct, access and rolling stock, not a hall template. MIT."""
import math
from shapely.geometry import box as rect,LineString,Polygon,Point

def terrain(s):
 s.use('Terrain');s.solid('IrregularCastStoneRim',s.site,-.36,.035,'stone');s.solid('RecessedStratum',s.site.buffer(-.13),-.75,-.34,'shadowStone')
 # Sculpt a continuous irregular tapered rock skirt; no disconnected uniform disc wedges.
 top=list(s.site.buffer(-.20).exterior.coords)[:-1];n=len(top);pts=[(x,-.72,z)for x,z in top]+[(x*.78,-1.44-.10*math.sin(i*1.7),z*.78)for i,(x,z)in enumerate(top)];faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
 for i in range(n):faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
 s.mesh('ContinuousFacetedIslandRock',pts,faces,'rock')
 s.use('Paving');surface=s.site.buffer(-.15);s.solid('PavingSubbase',surface,.035,.055,'paverC')
 for row in range(-17,15):
  z=row*.69
  for col in range(-12,13):
   x=col*.96+(row%2)*.48;tile=rect(x-.468,z-.333,x+.468,z+.333).intersection(surface)
   if tile.area>.035:s.solid('IndividualStonePaver',tile,.055,.075,['paverA','paverB','paverC'][(row*7+col*3)%3])
 # Flush tactile guidance and understated transverse stone inlay preserve road clearance.
 for a,b in [((0,-3.02),(0,8.25)),((-8.45,-.48),(8.45,.48))]:
  poly=LineString([a,b]).buffer(.08,cap_style=2).intersection(surface);s.solid('TactileGuidance',poly,.075,.085,'yellow')
 for z in [i*.17 for i in range(-15,48)]:
  if surface.covers(rect(-.045,z-.045,.045,z+.045)):s.box('TactileRib',(0,.09,z),(.13,.012,.035),'yellow',.003)
 s.use('Terrain');edge=s.site.boundary.difference(s.mouths.buffer(.13));s.railing('ExposedIslandBoundary',edge,.06,.98,postSpacing=1.05)
 s.proxy('IslandGround','ground',s.site,-.36,.075,'walkable')

def hall(s):
 s.use('Hall');s.box('StationStoneBase',(0,.14,-4.4),(13.70,.20,2.78),'stone',.04);s.box('IndoorTimberFloor',(0,.255,-4.42),(13.34,.07,2.45),'floor',.012)
 # Front/rear and side glazing: real panes, mullions, recessed jambs, physical thresholds.
 for z in [-3.04,-5.79]:
  for i in range(15):
   x=-6.51+i*.93;door=abs(x)<1.5
   s.box('HallClearGlass',(x,1.28,z),(.85,1.96,.035),'glass',.004)
   s.box('DeepMetalMullion',(x-.46,1.35,z+.025),(.10,2.27,.15),'woodLight',.009)
   if not door:s.box('RecessedStoneSill',(x,.39,z),(.88,.24,.20),'stone',.015)
  for y in [.34,2.22,2.56]:s.box('FrontRearTransom',(0,y,z),(13.62,.075,.13),'wood',.008)
  for i in range(101):s.box('TimberFacadeFin',(-6.75+i*.135,2.40,z+.09),(.07,.65,.16),'wood'if i%4 else'woodLight',.009)
 for x in [-6.85,6.85]:
  for i in range(4):
   z=-5.43+i*.69;s.box('ReturnClearGlass',(x,1.31,z),(.036,2.04,.60),'glass',.003);s.box('ReturnMullion',(x,1.36,z-.345),(.14,2.3,.09),'wood',.006)
  s.box('ReturnStoneSill',(x,.35,-4.42),(.20,.26,2.78),'stone',.02)
  for z in [-3.04,-5.79]:s.box('CornerColumn',(x,1.47,z),(.21,2.79,.22),'wood',.018)
  # Solid side frames, with window voids left genuinely open.
  for y in [.34,2.56]:s.box('SideHeader',(x,y,-4.42),(.22,.15,2.90),'steel',.01)
 # Ground collision shell follows actual walls, split at door openings.
 for xa,xb in [(-6.85,-1.95),(1.95,6.85)]:s.proxy('HallFrontWall','wall',rect(xa,-3.13,xb,-2.95),.25,2.6)
 s.proxy('HallRearWall','wall',rect(-6.85,-5.88,6.85,-5.71),.25,2.6)
 for x in [-6.85,6.85]:s.proxy('HallReturn','wall',rect(x-.12,-5.79,x+.12,-3.04),.25,2.6)
 # Four depth levels at the entrance; no fake black hole.
 s.box('DeepEntryHeader',(0,2.40,-2.86),(4.60,.50,.30),'woodLight',.025)
 for x in [-2.25,2.25]:s.box('EntryPortalPost',(x,1.29,-2.77),(.16,2.43,.19),'steel',.018);s.proxy('EntryColumn','column',rect(x-.08,-2.865,x+.08,-2.675),.075,2.5)
 for x in [-1.88,1.88]:s.box('DoorHandle',(x,1.10,-2.90),(.025,.43,.035),'roofEdge',.008)
 s.box('LevelEntryThreshold',(0,.13,-2.94),(4.0,.11,.42),'stone',.018)
 # Flat standing-seam roof with a real central opening, framed glass sky strip and soffit.
 z0,z1=-6.03,-2.52;roofY=2.84
 for xa,xb in [(-7.08,-2.60),(2.60,7.08)]:
  s.box('StandingSeamRoofWing',((xa+xb)/2,roofY,(z0+z1)/2),(xb-xa,.14,z1-z0),'roof',.022)
  for i in range(math.ceil((xb-xa)/.65)):
   x=xa+.15+i*.65;s.box('RaisedMetalRoofSeam',(x,roofY+.085,(z0+z1)/2),(.025,.035,z1-z0-.06),'roofDark',.007)
 for z in [z0+.18,z1-.22]:s.box('RoofSkyOpeningEnd',(0,roofY,z),(5.20,.14,.36),'roof',.015)
 s.box('HallSkylight',(0,roofY+.07,-4.26),(5.08,.055,2.50),'glass',.006)
 for x in [-2.60,-1.30,0,1.30,2.60]:s.box('SkylightFrame',(x,roofY+.13,-4.26),(.065,.13,2.62),'roofEdge',.008)
 for z in [-5.58,-4.26,-2.94]:s.box('SkylightCrossbar',(0,roofY+.13,z),(5.27,.13,.06),'roofEdge',.008)
 for z in [z0,z1]:s.box('FoldedMetalFascia',(0,roofY-.03,z),(14.25,.19,.09),'roofEdge',.018)
 for x in [-7.08,7.08]:s.box('SideMetalFascia',(x,roofY-.03,-4.28),(.09,.19,3.60),'roofEdge',.018)
 for x in [i*.22 for i in range(-31,32)]:s.box('WarmTimberEaveLining',(x,2.746,-2.74),(.15,.045,.43),'woodLight',.006)
 # Interior ticketing/service facilities visible through glazing and skylight.
 for x in [-1.30,0,1.30]:
  s.box('TicketGatePedestal',(x,.64,-3.67),(.30,.76,.68),'cream',.06);s.box('TicketGateWoodCap',(x,1.04,-3.67),(.32,.055,.66),'woodLight',.018);s.box('TicketGateReader',(x,1.079,-3.49),(.12,.035,.14),'navy',.01);s.box('OpenGateIndicator',(x+.17,.95,-3.50),(.025,.12,.10),'light',.003)
 for x in [-4.8,4.8]:
  s.box('InteriorServiceDesk',(x,.70,-4.85),(2.3,.86,.55),'wood',.03);s.box('ServiceCounterTop',(x,1.16,-4.85),(2.4,.08,.63),'cream',.025)
  for xx in [x-.55,x+.55]:s.box('TicketServiceScreen',(xx,1.40,-4.91),(.37,.35,.05),'navy',.02);s.box('ScreenInset',(xx,1.42,-4.87),(.30,.26,.008),'screen',.003)
 for x in [-5.65,-3.85,3.85,5.65]:s.box('WarmCeilingPanel',(x,2.62,-4.6),(1.05,.035,.34),'light',.006)
 s.use('Identity');s.box('StationIdentityPlaque',(0,2.40,-2.64),(3.8,.58,.13),'cream',.04);s.text('OriginalStationName','苑裡站',(0,2.40,-2.54),.53);s.text('VisionDisclaimer','交通政策願景示意',(0,1.98,-2.66),.115,'woodDark')
 # Original track icon, not an official protected railway logo.
 for x in [-1.5,-1.38]:s.beam('OwnRailIcon',(x,2.24,-2.545),(x,2.55,-2.545),.022,'rail')
 for y in [2.30,2.41,2.51]:s.beam('OwnRailIconSleeper',(-1.56,y,-2.545),(-1.32,y,-2.545),.018,'rail')

def viaduct(s):
 s.use('Viaduct');s.box('ViaductMainDeck',(0,3.50,-7.66),(18.90,.422,3.36),'concrete',.045);s.box('FrontRecessedBand',(0,3.28,-6.02),(18.75,.12,.10),'shadowStone',.012);s.box('RearRecessedBand',(0,3.28,-9.29),(18.75,.12,.10),'shadowStone',.012)
 for x in [-7.65,-2.55,2.55,7.65]:
  for z in [-8.79,-6.63]:
   s.box('TaperedPierFoot',(x,.17,z),(.77,.22,.83),'stone',.045);s.box('ViaductPier',(x,1.63,z),(.42,3.0,.48),'concrete',.045);s.box('PierCapital',(x,3.08,z),(.85,.34,.82),'concrete',.035)
   s.proxy('ViaductPier','column',rect(x-.25,z-.26,x+.25,z+.26),.075,3.289)
 # Real arch-shaped soffit surfaces, repeated on both viaduct elevations.
 for za in [-6.09,-9.21]:
  for xa,xb in [(-7.65,-2.55),(-2.55,2.55),(2.55,7.65)]:
   poly=[(xa+.15,3.30),(xb-.15,3.30),(xb-.15,2.55)]
   for i in range(1,25):
    t=i/24;x=xb-.15-(xb-xa-.30)*t;y=2.55+.63*math.sin(math.pi*t);poly.append((x,y))
   # Extrusion along world Z. Front and back loops have consistent outward winding.
   p=[(x,y,za-.13)for x,y in poly]+[(x,y,za+.13)for x,y in poly];n=len(poly);f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];s.mesh('LoadBearingArchFascia',p,f,'concrete')
 for x in [-5.10,0,5.10]:s.box('BridgeSoffitWarmLight',(x,3.20,-6.25),(1.8,.035,.075),'light',.008)
 s.use('Railway');s.box('RecessedBallast',(0,3.727,-8.20),(18.9,.07,1.67),'shadowStone',.012)
 for i in range(59):s.box('IndividualTrackSleeper',(-9.20+i*.317,3.80,-8.20),(.10,.07,1.55),'woodDark',.008)
 for z in [-8.71,-7.69]:s.box('SteelRailWeb',(0,3.862,z),(18.90,.075,.065),'steel',.008);s.box('RailPolishedHead',(0,3.909,z),(18.90,.023,.085),'roofEdge',.005)
 s.box('PlatformWalkingSurface',(0,3.731,-6.56),(18.65,.038,1.10),'cream',.012)
 for i in range(91):s.box('PlatformTactileDashes',(-9.15+i*.20,3.759,-7.03),(.13,.018,.13),'yellow',.005)
 s.railing('PlatformFrontGuard',LineString([(-8.9,-6.05),(8.9,-6.05)]).difference(rect(-7.15,-6.2,-5.95,-5.9).union(rect(7.05,-6.2,8.35,-5.9))),3.75,1.0,postSpacing=.98);s.railing('PlatformRearGuard',LineString([(-9.25,-9.26),(9.25,-9.26)]),3.75,.95,postSpacing=.98)
 s.proxy('PlatformWalk','platform',rect(-9.3,-7.1,9.3,-6.0),3.65,3.75,'walkable')

def canopy(s):
 s.use('Canopy')
 # Layered long low canopy. Opaque eaves flank a real glazed roof strip.
 for x in [-8.7,-5.8,-2.9,0,2.9,5.8,8.7]:
  for z in [-9.18,-6.08]:
   s.box('CanopySteelColumn',(x,5.17,z),(.095,2.84,.11),'steel',.012);s.box('ColumnBaseShoe',(x,3.85,z),(.19,.16,.21),'roofEdge',.015)
   s.beam('CanopyKneeBrace',(x,6.17,z),(x+.43,6.55,z+(.32 if z<-8 else-.32)),.075,'steel')
  s.box('CanopyCrossRafter',(x,6.53,-7.64),(.13,.17,3.75),'steel',.01)
 for z in [-9.39,-8.52,-7.22,-5.82]:s.box('RoofLongitudinalRib',(0,6.65,z),(19.3,.15,.11),'steel',.012)
 for za,zb in [(-9.49,-8.56),(-7.18,-5.69)]:
  s.box('ThickMetalCanopyPanel',(0,6.76,(za+zb)/2),(19.60,.12,zb-za),'roof',.018)
  for i in range(27):s.box('StandingMetalSeam',(-9.61+i*.74,6.83,(za+zb)/2),(.022,.035,zb-za-.035),'roofDark',.006)
 s.box('UpperRoofGlazedStrip',(0,6.76,-7.87),(19.4,.055,1.30),'glass',.006)
 for i in range(21):s.box('RoofGlazingMullion',(-9.6+i*.96,6.81,-7.87),(.055,.10,1.38),'roofEdge',.007)
 for z in [-9.49,-5.69]:s.box('FoldedCanopyEdge',(0,6.73,z),(19.74,.18,.10),'roofEdge',.017)
 for x in [-9.80,9.80]:s.box('CanopyEndCap',(x,6.73,-7.59),(.10,.18,3.87),'roofEdge',.015)
 # Authored diagonal oak soffit screen, attached to continuous sub-framing.
 for i in range(100):
  x=-9.5+i*.192;s.beam('OakSoffitSlat',(x,6.59,-7.15),(x+.25,6.34,-5.85),.067,'woodLight')
 for z in [-9.29,-6.24]:s.box('WarmLinearCanopyLight',(0,6.51,z),(18.85,.025,.045),'light',.006)
 for x in [-4.6,4.6]:
  s.box('PlatformDisplayHousing',(x,5.92,-6.23),(1.35,.42,.10),'navy',.035)
  s.text('PlatformDisplay','苑裡  願景',(x,5.94,-6.16),.13,'screen')

def access(s):
 s.use('VerticalCirculation');x0,x1=-9.15,-6.90;front,back=-3.12,-6.40;steps=12;rise=3.675/24;run=(front-back)/12
 # First run heads backwards, second returns forwards; a top bridge physically meets platform.
 for flight in [0,1]:
  x=-8.60 if flight==0 else-7.45
  for i in range(steps):
   z=front-(i+.5)*run if flight==0 else back+(i+.5)*run;y=.075+(flight*steps+i+1)*rise
   s.box('PhysicalStairTread',(x,y/2,z),(1.0,y,run+.012),'stone',.012)
   s.box('StairNosing',(x,y+.008,z+(.12 if flight==0 else-.12)),(.97,.017,.026),'roofEdge',.004)
  bottom=.075+flight*1.8375;top=bottom+1.8375
  for xx in [x-.47,x+.47]:
   s.beam('StairSlopingHandrail',(xx,bottom+.85,front if flight==0 else back),(xx,top+.85,back if flight==0 else front),.035,'rail')
   for j in range(5):
    t=j/4;zz=(front*(1-t)+back*t)if flight==0 else(back*(1-t)+front*t);yy=bottom+(top-bottom)*t;s.beam('StairBaluster',(xx,yy,zz),(xx,yy+.86,zz),.032,'rail')
  s.proxy('StairFlight','stairs',rect(x-.5,back,x+.5,front),bottom,top,'stepped_walkable')
 s.box('StairMidLanding',(-8.03,1.8375,-6.86),(2.25,.15,.92),'stone',.02)
 s.box('StairTopLanding',(-7.15,3.67,-3.15),(1.55,.16,.95),'stone',.02)
 s.box('TopAccessBridge',(-6.52,3.67,-4.69),(1.10,.16,3.94),'stone',.02)
 for x in [-7.05,-5.99]:s.railing('UpperStairConnectorGuard',LineString([(x,-3.14),(x,-6.1)]),3.75,.95,postSpacing=.8)
 s.proxy('TopAccessBridge','platform',rect(-7.07,-6.66,-5.97,-2.72),3.59,3.75,'walkable')
 # End opening connects to upper platform; the front guard is split at both real access lanes later.
 s.railing('StairMidBackGuard',LineString([(-9.12,-7.31),(-6.92,-7.31)]),1.91,.85)
 # Right glass lift tower and two real doors, with visible cab, shaft rails and landing.
 cx,cz=7.70,-4.44
 for x in [6.88,8.52]:
  for z in [-5.27,-3.61]:s.box('LiftTowerPost',(x,2.48,z),(.12,4.80,.12),'steel',.015)
 for y in [.20,2.24,3.76,4.78]:
  for z in [-5.27,-3.61]:s.box('LiftTransom',(cx,y,z),(1.78,.11,.13),'roofEdge',.01)
  for x in [6.88,8.52]:s.box('LiftReturnFrame',(x,y,cz),(.13,.11,1.77),'roofEdge',.01)
 for x in [6.88,8.52]:s.box('LiftSideGlass',(x,2.48,cz),(.036,4.5,1.49),'glass',.005)
 s.box('LiftRearGlass',(cx,2.48,-5.27),(1.49,4.5,.035),'glass',.004)
 for y in [1.16,4.12]:
  for x in [cx-.34,cx+.34]:s.box('GlassLiftDoor',(x,y,-3.605),(.65,1.83 if y<2 else 1.16,.035),'glass',.004)
 for x in [7.10,8.28]:s.beam('LiftGuideRail',(x,.23,-5.12),(x,4.5,-5.12),.045,'steel')
 s.box('LiftCabFloor',(cx,3.73,cz),(1.44,.12,1.43),'stone',.02);s.box('LiftFlatRoof',(cx,4.86,cz),(1.95,.20,1.96),'roof',.025)
 s.box('LiftCanopySkylight',(cx,4.98,cz),(1.1,.035,1.12),'glass',.006)
 s.box('LiftLandingBridge',(cx,3.68,-5.68),(1.23,.14,1.05),'stone',.02)
 for x in [7.10,8.30]:s.railing('LiftConnectorGuard',LineString([(x,-5.15),(x,-6.15)]),3.75,.95,postSpacing=.55)
 s.proxy('LiftShaft','lift',rect(6.82,-5.33,8.59,-3.54),.06,4.95,'reserved_nonfunctional_lift')
 s.proxy('LiftLandingBridge','platform',rect(7.08,-6.2,8.32,-5.15),3.6,3.75,'walkable')
 s.use('Identity');s.box('LiftInformationPlaque',(8.60,2.5,-4.10),(.04,.62,.49),'cream',.025);s.text('LiftAccessibleIcon','↑',(8.63,2.5,-4.1),.39,'rail',face='side')

def train(s):
 s.use('TrainRollingStock');parent=s.parent
 # Eight wheels sit exactly on the rail heads; bogies, coupler and two articulated cars.
 for car,(lo,hi)in enumerate([(-8.70,-.22),(.17,8.93)]):
  p=s.group('TrainCar_'+str(car+1));z=-8.20
  s.box('TrainUnderframe',((lo+hi)/2,4.17,z),(hi-lo-.4,.17,1.42),'rubber',.045,p)
  s.box('TrainInteriorFloor',((lo+hi)/2,4.30,z),(hi-lo-.35,.12,1.43),'trainWhite',.035,p)
  s.box('LowerTrainBody',((lo+hi)/2,4.54,z),(hi-lo-.20,.47,1.57),'trainWhite',.12,p)
  for zz in [z-.792,z+.792]:
   s.box('TransportBlueStripe',((lo+hi)/2,4.66,zz),(hi-lo-.24,.23,.023),'trainBlue',.008,p)
   s.box('FineTrainGoldLine',((lo+hi)/2,4.82,zz),(hi-lo-.28,.045,.024),'yellow',.006,p)
   for j in range(10):
    xx=lo+.53+j*(hi-lo-1.10)/10
    door=j in [2,7]
    if door:
     s.box('TrainDoorFrame',(xx,5.17,zz),(.60,1.13,.045),'roofEdge',.035,p);s.box('TrainDoorPanel',(xx,4.95,zz+.012 if zz>z else zz-.012),(.52,.66,.022),'trainWhite',.025,p);s.box('DoorWindow',(xx,5.45,zz+.027 if zz>z else zz-.027),(.41,.39,.025),'trainGlass',.055,p);s.box('DoorJoint',(xx,5.18,zz+.043 if zz>z else zz-.043),(.018,1.10,.018),'steel',.002,p)
    else:
     s.box('TrainWindowRecess',(xx,5.30,zz),(.63,.79,.055),'steel',.075,p);s.box('ActualTrainWindow',(xx,5.30,zz+.031 if zz>z else zz-.031),(.54,.69,.028),'trainGlass',.065,p)
    s.box('TrainWindowPillar',(xx+.37,5.34,zz),(.09,1.00,.11),'trainWhite',.018,p)
   s.box('ContinuousWindowHeader',((lo+hi)/2,5.84,zz),(hi-lo-.28,.21,.12),'trainWhite',.035,p)
  s.box('RoundedCarRoof',((lo+hi)/2,5.99,z),(hi-lo-.04,.31,1.61),'trainWhite',.145,p)
  for xx in [(lo+hi)/2-1.45,(lo+hi)/2+1.45]:
   s.box('RooftopHVAC',(xx,6.19,z),(.95,.13,.77),'roofEdge',.06,p)
   for j in range(7):s.box('HVACVent',(xx-.35+j*.115,6.26,z),(.035,.016,.55),'steel',.003,p)
  for xx in [lo+1.30,hi-1.25]:
   s.box('TrainBogie',(xx,4.095,z),(.92,.20,1.20),'rubber',.025,p)
   for zz in [z-.51,z+.51]:
    o=s.cyl('RailContactWheel',(xx,4.121,zz),.20,.12,'steel',20,p);o.rotation_euler.x=math.pi/2
  for xx in [lo+1.9,lo+4.9]:s.box('TrainVisibleSeat',(xx,4.62,z),(.8,.36,.62),'trainBlue',.08,p)
 # Custom curved front shell, physical trapezoidal windshield and lights.
 p=parent;xc=8.93;z=-8.20
 profile=[(-.72,4.40),(-.79,4.65),(-.77,5.58),(-.62,5.96),(-.39,6.10),(.39,6.10),(.62,5.96),(.77,5.58),(.79,4.65),(.72,4.40)]
 pts=[]
 for x,f in [(8.55,1),(8.90,.98),(9.14,.80)]:pts.extend((x,y,z+zz*f)for zz,y in profile)
 n=len(profile)
 for x,f in [(8.55,1),(8.90,.98),(9.14,.80)]:pts.extend((x,5.25+(y-5.25)*.94,z+zz*f*.94)for zz,y in profile)
 faces=[]
 for k in range(2):
  for j in range(n):
   a=k*n+j;b=k*n+(j+1)%n;c=(k+1)*n+(j+1)%n;d=(k+1)*n+j;faces.extend([(a,b,c,d),(a+3*n,d+3*n,c+3*n,b+3*n)])
 for k in [0,2]:
  for j in range(n):a=k*n+j;b=k*n+(j+1)%n;faces.append((a,a+3*n,b+3*n,b))
 s.mesh('OriginalRoundedCabNose',pts,faces,'trainWhite',p,True)
 # Physically open cab shell: a solid border surrounds a glazed void, with cabin behind it.
 from shapely import constrained_delaunay_triangles
 from shapely.geometry.polygon import orient
 def cab_prism(name,poly,x0,x1,mat):
  poly=orient(poly,1);verts=[];ff=[];lookup={}
  def idx(z,y,x):
   k=(round(x,6),round(y,6),round(z-8.20,6))
   if k not in lookup:lookup[k]=len(verts);verts.append(k)
   return lookup[k]
  for tri in constrained_delaunay_triangles(poly).geoms:
   if not poly.covers(tri):continue
   a=list(orient(tri,1).exterior.coords)[:3];ff.extend([tuple(idx(zz,yy,x1)for zz,yy in a),tuple(idx(zz,yy,x0)for zz,yy in reversed(a))])
  for ring in [poly.exterior,*poly.interiors]:
   a=list(ring.coords)
   for (zz,yy),(z2,y2)in zip(a,a[1:]):ff.append((idx(zz,yy,x0),idx(z2,y2,x0),idx(z2,y2,x1),idx(zz,yy,x1)))
  return s.mesh(name,verts,ff,mat,p)
 opening=Polygon([(-.52,5.02),(.52,5.02),(.45,5.79),(-.45,5.79)]);outer=Polygon([(zz*.80,yy)for zz,yy in profile]);cab_prism('CabNoseFrameWithRealOpening',outer.difference(opening),9.14,9.19,'trainWhite');cab_prism('CabWindowGasket',opening.buffer(.045).difference(opening),9.19,9.215,'rubber');cab_prism('CabActualWindscreen',opening,9.20,9.22,'trainGlass');s.box('CabDashboard',(8.82,4.96,z),(.49,.10,1.1),'navy',.03,p)
 for zz in [-.48,.48]:s.ball('CabHeadlight',(9.25,4.82,z+zz),(.035,.075,.10),'light',2,p)
 s.box('CabBlueBelt',(9.17,4.57,z),(.08,.16,1.25),'trainBlue',.06,p);s.box('FrontCoupler',(9.29,4.27,z),(.28,.13,.21),'rubber',.025,p)
 s.box('IntercarGangway',(-.025,5.15,z),(.31,1.57,1.05),'rubber',.055,p)
 s.proxy('TrainSweptStaticEnvelope','train',rect(-8.8,-9.05,9.45,-7.35),3.92,6.29,'static_display_no_riding')
