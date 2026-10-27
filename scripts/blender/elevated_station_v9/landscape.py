"""Authored layered garden bands and public furniture; exact reserved footprints. MIT."""
import math
from shapely.geometry import box as rect,LineString,Point

def landscape(s):
 # Main garden locations are authored, not auto-placed in leftover space.
 beds=[('WestWindowGarden',rect(-6.6,-3.0,-3.20,-2.79),None),('EastWindowGarden',rect(3.2,-3.0,6.4,-2.55),None),('WestForecourtGarden',rect(-8.40,2.85,-5.65,6.55),(-6.65,3.95,2.85,.82)),('EastForecourtGarden',rect(5.65,2.85,8.40,6.55),(6.65,3.95,2.85,.82)),('WestArrivalGarden',rect(-5.50,5.95,-4.10,6.55),(-4.80,6.18,3.50,1.0)),('EastArrivalGarden',rect(4.10,5.95,5.50,6.55),(4.80,6.18,3.50,1.0)),('WestAccessGarden',rect(-9.9,-9.6,-9.35,-5.4),None),('RearRailGardenWest',rect(-8.9,-10.9,-3.0,-9.74),None),('RearRailGardenEast',rect(3,-10.9,8.9,-9.74),None),('EastLiftGarden',rect(8.9,-6.1,9.9,-3.7),None)]
 for n,p,tree in beds:
  p=p.intersection(s.site.buffer(-.23)).difference(s.mouths.buffer(.12))
  if p.area>.1:s.plantbed(n,p,tree)
 # A pair of benches sit beside, never in, the two 3x3 NPC squares.
 for x in [-5.55,5.55]:s.bench('GardenWaitingBench',x,4.10,0 if x<0 else math.pi,2.0)
 for x in [-7.10,7.10]:s.tree('SecondaryLayerTree',x,5.70,2.45,.70)
 # Short seating under the station eaves, physically framed by the window gardens.
 for x in [-4.6,4.6]:s.bench('WindowWaitingBench',x,-3.38,math.pi/2,1.65)
 # Additional high-level terrace planting, not on railway or at the lift doorway.
 s.use('Gardens')
 for x,z in [(-8.65,-9.00),(8.65,-9.0)]:
  p=s.group('UpperTerracePlanter');s.box('UpperPlanterBase',(x,3.56,z),(.70,.43,.42),'cream',.035,p)
  for i in range(8):s.ball('UpperGardenLeaves',(x-.25+(i%4)*.16,3.88+(i//4)*.1,z),(.15,.16,.14),['leaf','leafDark','leafLight'][i%3],1,p)
 # Lighting and furnishings remain outside all reserved movement bands.
 s.use('Furniture')
 for x,z in [(-6.0,5.3),(6.0,5.3),(-9.4,-3.5),(8.75,-6.6)]:
  s.box('GardenLanternFoot',(x,.14,z),(.24,.20,.24),'stone',.018);s.box('LanternColumn',(x,1.12,z),(.055,1.9,.055),'rail',.009);s.box('WarmLanternGlass',(x,2.13,z),(.23,.33,.23),'light',.025);s.box('LanternMetalCap',(x,2.32,z),(.31,.065,.31),'roof',.02)
  s.proxy('Lantern','post',Point(x,z).buffer(.12),.075,2.4)
 for x,z in [(-2.65,-2.80),(2.65,-2.80)]:s.box('SteelWoodWasteBin',(x,.52,z),(.30,.87,.33),'steel',.045);s.box('BinWoodTrim',(x,.81,z+.18),(.25,.18,.025),'wood',.012)
 s.use('Identity');x,z=5.5,-2.66;s.box('TravelInformationStele',(x,1.12,z),(.64,1.94,.16),'steel',.045);s.box('SteleMap',(x,1.24,z+.09),(.51,1.32,.018),'cream',.012)
 for j in range(4):s.beam('OriginalMapLine',(x-.19+j*.12,.68,z+.112),(x-.15+j*.10,1.75,z+.112),.014,'rail')
 s.text('SteleVisionHeading','願景',(x,1.91,z+.11),.15,'navy')

 # Two entrance pots carry actual sculpted spear leaves, not blue/green billboards.
 s.use('Gardens')
 for x in [-2.90,2.90]:
  s.cyl('EntryTerracottaPot',(x,.30,-2.86),.22,.46,'stone',24)
  for j in range(12):
   a=j*2.39996;r=.22+.06*(j%3);xx=x+r*math.cos(a);zz=-2.86+r*math.sin(a);yy=.92+.12*(j%3)
   pts=[(x-.035,.50,-2.86),(x+.035,.50,-2.86),(xx+.055,yy,zz),(xx,yy+.08,zz),(xx-.055,yy,zz)];pts+= [(a,b,c+.018)for a,b,c in pts];n=5;s.mesh('SculptedSpearLeaf',pts,[tuple(reversed(range(n))),tuple(range(n,2*n)),*[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]],['leaf','leafDark','leafLight'][j%3])
  s.proxy('EntryPot','planter',Point(x,-2.86).buffer(.24),.075,1.25)
