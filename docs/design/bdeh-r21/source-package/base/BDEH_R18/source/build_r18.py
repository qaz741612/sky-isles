"""Sky Isles / BDEH / R18 — independently rebuildable landmark concept geometry.

Source for standalone 3D proposals. X,Z ground, Y up. Never writes to GitHub.
Route geometry is candidate interior planning, not game-ready collision or production layout.
"""
import importlib.util, math, json, os, sys
from pathlib import Path
import numpy as np
import trimesh
from shapely.geometry import Point, LineString, Polygon
from shapely.affinity import scale
from shapely.ops import triangulate, unary_union
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
S12=str(ROOT/'source'/'base_r12.py')
spec=importlib.util.spec_from_file_location('r12',S12); r12=importlib.util.module_from_spec(spec);spec.loader.exec_module(r12)
Design=r12.Design; base=r12.base
base.OUT=ROOT
for d in ('models','renders','qa'):(ROOT/d).mkdir(exist_ok=True)

palette={
'B':dict(roof='ochre',warm='warmwood',facade='ivory',glass='blueglass',accent='clay',path='stone'),
'D':dict(roof='roofblue',warm='bronze2',facade='white2',glass='blueglass',accent='solar',path='stone'),
'E':dict(roof='darkolive',warm='warmwood',facade='ivory',glass='glass2',accent='sage',path='stone'),
'H':dict(roof='slateblue',warm='ochre',facade='white2',glass='glass2',accent='roofblue',path='stone'),
}

# Lines are independent of global Bezier: retain real bridge approach directions, route
# around new landmark footprints; the game network must be re-generated and tested.
ROUTE={
'B':[[ (12.7,-6.7),(10.0,-5.8),(10.3,-1.9),(10.5,4.8),(7.4,10.4),(-0.1,11.7),(-9.0,10.2)], [(10.3,-1.9),(14.1,-1.82)]],
'D':[[ (9.6,-10.3),(4.3,-10.8),(-3.9,-9.3),(-10.2,-3.8),(-11.9,3.5),(-10.7,9.8)]],
'E':[[(-16.1,0.35),(-12.3,-1.2),(-9.1,-6.4),(-3,-8.5),(6.8,-7.9),(12.1,-3.3),(16.13,.80)],
     [(-9.66,11.8),(-13.0,6.1),(-12.3,-1.2)],
     [(6.8,-7.9),(8.8,-12.4)]],
'H':[[(-15.6,0),(-12.1,-5.0),(-6.9,-8.8),(0.6,-10.2),(7.4,-10.9),(8.65,-11.89)]]
}

# General model utilities: named, editably parameterized pieces, no screenshots-as-model.
def prism(s,n,p,y0,y1,c):s.hardprism(n,p,y0,y1,c)
def rect(s,n,x,z,w,d,y0,y1,c):s.hardbox(n,x,z,w,d,y0,y1,c)
def post(s,n,x,z,y0,y1,rad,c):s.post(n,x,z,y0,y1,rad,c)
def brace(s,n,a,b,rad,c):s.girder(n,a,b,rad,c)
def pv(s,n,a,b,y0,y1,col,thick=.12):s.panel(n,a,b,y0,y1,col,thick)

def curve_rail(s,n,pts,y=.45,h=1.1,c='bronze2',count=30):
    pts=np.array(pts,float);dist=np.sqrt(((pts[1:]-pts[:-1])**2).sum(axis=1));tot=dist.sum()
    if tot<.01:return
    xx=np.r_[0,np.cumsum(dist)]
    inter=np.linspace(0,tot,count)
    P=np.stack([np.interp(inter,xx,pts[:,d]) for d in range(2)],axis=1)
    for i,q in enumerate(P):
       if i%3==0: post(s,n+'_vertical',q[0],q[1],y,y+h,.035,c)
    for a,b in zip(P[:-1],P[1:]):brace(s,n+'_handrail',(a[0],y+h,a[1]),(b[0],y+h,b[1]),.032,c)

def banded_glass(s,n,a,b,y0,y1,count,glass='blueglass',metal='slateblue'):
    a=np.array(a); b=np.array(b);nvec=b-a
    for i in range(count):
        x=a+nvec*i/count;z=a+nvec*(i+1)/count
        pv(s,n+'_glass',x,z,y0,y1,glass,.10)
        pv(s,n+'_lower_band',x,z,y0+.05,y0+.35,'warmwood',.16)
        if i%2==0:pv(s,n+'_floor_division',x,z,(y0+y1)/2-.13,(y0+y1)/2+.12,'ivory',.16)
        post(s,n+'_mullion',x[0],x[1],y0,y1,.057,metal)
    post(s,n+'_end',b[0],b[1],y0,y1,.057,metal)
    pv(s,n+'_top',a,b,y1-.18,y1,metal,.15)

def annular_building(s, cx,cz,ro,ri,a0,a1,h0=1.0,h1=6.25,mat='ivory'):
    # ONE connected inhabitable wing, not roof plates detached from rooms.
    t=np.linspace(a0,a1,30)
    p=lambda rad,angle:(cx+rad*math.cos(angle),cz+rad*math.sin(angle))
    shell=[p(ro,ang) for ang in t]+[p(ri,ang) for ang in t[::-1]]
    prism(s,'CrescentOccupiedTwoStoreyShell',shell,.22,h1,mat)
    for i,(aa,bb) in enumerate(zip(t[:-1],t[1:])):
       a,b=p(ro+.02,aa),p(ro+.02,bb)
       c,d=p(ri-.04,aa),p(ri-.04,bb)
       pv(s,'CrescentOuterRealGlass',a,b,h0,h1-.32,'blueglass',.11)
       pv(s,'CrescentCourtInnerGlazing',c,d,h0,h1-.32,'glass2',.12)
       if i%2==0:
          post(s,'CrescentOuterWoodPier',a[0],a[1],.2,h1+.33,.09,'warmwood')
          post(s,'CrescentInnerWoodPier',c[0],c[1],.2,h1+.33,.075,'bronze2')
       if i%4==1:pv(s,'VerticalCareBays',a,c,h0,h1-.28,'stone2',.12)
    return p,t

def landmark_B(s):
    """B: inhabitable embracing pair, luminous healing court; warm timber not resort cottages."""
    # distinctive almost clasping arms; site 30x28, landmark spans ca 18 wide.
    center=(-2.65,-2.05)
    p,t=annular_building(s,*center,ro=8.7,ri=5.3,a0=math.radians(43),a1=math.radians(307),h1=5.9)
    # A single continuous folded/curved roof follows whole inhabited outer + inner facade.
    def roof_theta(ang):return 6.35+1.0*math.sin((ang-math.radians(43))/(math.radians(264))*math.pi)**2
    for a,b in zip(t[:-1],t[1:]):
       u=np.linspace(a,b,3);grid=[]
       for rr in np.linspace(5.03,9.25,5):
          grid.append([[center[0]+rr*math.cos(ang),roof_theta(ang)+.34*(rr-5.03)/4.2,center[1]+rr*math.sin(ang)] for ang in u])
       s.patch('FoldedContinuousWoodRibbon',np.array(grid),'ochre',.38)
       aa=p(9.2,a);bb=p(9.2,b);brace(s,'VisibleRoofSoffit',(aa[0],roof_theta(a)-.22,aa[1]),(bb[0],roof_theta(b)-.22,bb[1]),.08,'wood2')
    # glass atrium at opening of crescent: physically attached via 2 visible beams
    rect(s,'CommunityEntryAtrium',4.25,-5.25,5.65,5.0,.22,5.45,'ivory')
    banded_glass(s,'AtriumGlazedEntrance',(2,-7.78),(6.6,-7.78),.63,5.3,8,'blueglass','ochre')
    rect(s,'GlassAtriumLuminousRoof',4.25,-5.25,6.0,5.5,5.45,5.98,'bronze2')
    for x in np.linspace(2,6.5,8):brace(s,'AtriumTimberTrusses',(x,5.45,-7.6),(x,6.2,-2.9),.07,'warmwood')
    # accessible inward court, separate low planters; do not choke safe walkway.
    s.platform('HealingCourtyardStone',*center,7.6,7.0,'stone',.14,.28)
    for rad in (2.1,3.05):
       steps=np.linspace(0,2*math.pi,36)
       coords=[(center[0]+rad*math.cos(a),center[1]+rad*.8*math.sin(a)) for a in steps]
       for a,b in zip(coords[:-1],coords[1:]):brace(s,'SensoryGardenLowEdge',(a[0],.32,a[1]),(b[0],.32,b[1]),.085,'stone2')
    s.tree(center[0],center[1],.85,'pink')
    # facade level structure under real roof + bridge-like entrance to protected approach
    for a in np.linspace(t[0],t[-1],20):
       i=p(5.0,a);o=p(9.0,a)
       brace(s,'ExposedArchedGlulamGirder',(i[0],5.8,i[1]),(o[0],6.65,o[1]),.12,'warmwood')
    for x,z in [(-11.5,7.7),(-10.6,-10.7),(5,7)]:s.tree(x,z,.62,'olive')


def landmark_D(s):
    """D: long-span municipal hall with occupiable atrium, spectacular single crest and lateral wings."""
    # building in northeast; main hall + stepped floorplates occupy c.20x13, no token box.
    rect(s,'CivicFoundation',4.0,4.0,19.8,13.6,.14,.9,'stone2')
    rect(s,'PublicServiceLowerHall',4.0,4.45,18.4,11.4,.9,4.6,'white2')
    rect(s,'CivicSecondFloor',3.55,5.1,16.6,8.6,4.6,7.35,'ivory')
    # 2-level full glazing and projecting inhabited side wing, not an empty roof.
    banded_glass(s,'PrincipalPublicAtrium',(-5.4,-1.30),(13.35,-1.30),.95,7.2,24,'deepglass','slateblue')
    banded_glass(s,'NorthernCivicGlazing',(-5.15,10.05),(13.0,10.05),1.3,7.25,22,'blueglass','charcoal')
    banded_glass(s,'WestSide',(-5.4,-1.25),(-5.4,9.5),.95,7.0,12,'blueglass','slateblue')
    banded_glass(s,'EastSide',(13.3,-1.25),(13.3,9.5),.95,7.0,12,'blueglass','slateblue')
    # folding crest is one roof integrated into upper level with deep exposed V-bow; 21 x 15.
    def wave(x,z):
        xnorm=abs(x-3.9)/10.8
        return [x,7.55+3.0*xnorm**1.33 +.22*math.cos((z-4.5)/7.8*math.pi),z]
    s.surface('MonumentalConnectedCivicRoof',-6.9,14.8,-2.65,11.15,wave,'roofblue',38,18,.50)
    for zz in np.linspace(-2.0,10.5,12):
        for xx in (-6.45,14.25):
            y=wave(xx,zz)[1]-.18
            brace(s,'CivicWingDeepBearing',(3.9,7.42,zz),(xx,y,zz),.14,'bronze2')
            post(s,'CivicStructuralBays',xx,zz,.22,y,.105,'charcoal')
    # landmark central vertical glass lightwell, not a generic tall office building.
    rect(s,'TransparentPublicLantern',3.9,4.85,3.1,8.7,7.15,9.75,'blueglass')
    for z in np.linspace(1,8.7,8):post(s,'LanternTimberFins',3.9,z,7.1,10.0,.077,'warmwood')
    rect(s,'LightwellCrown',3.9,4.85,3.65,9.2,9.9,10.20,'bronze2')
    # four articulated portico piers and a monumental public arrival apron.
    for xx in (-3.95,1.2,6.35,11.50):
        post(s,'PublicPorticoStructure',xx,-2.0,.18,7.5,.20,'bronze2')
        rect(s,'PublicEntryPierFooting',xx,-2.0,.58,.58,.18,.44,'stone2')
    rect(s,'CivicEntryLanding',3.9,-3.25,13.3,2.0,.1,.29,'stone')
    # quiet civic landscaping, low structural retaining wall
    for zz in (-8.0,12.5):s.garden(-9.2,zz,4.3,.95,'green')
    s.tree(-11,-9.4,.72,'olive')


def landmark_E(s):
    """E: genuine split-level inhabited terraces connected by continuous inhabited green roof."""
    # On NE sector, stacked offset concrete/wood floors with different heights and inset facades.
    plans=[[(0.4,1.1),(13.1,1.1),(14.3,4.8),(12.4,11.35),(1.6,11.6),(-.8,6.2)],
           [(2.0,4.1),(14.0,4.6),(12.1,10.75),(3.4,11.65)],
           [(4.0,7.0),(12.3,7.3),(11.2,12.1),(5.2,11.95)]]
    colors=['ivory','stone2','warmwood']
    for i,p in enumerate(plans):
       y0=[.23,3.8,6.2][i];y1=[3.75,6.15,8.15][i]
       prism(s,f'InhabitedSteppedEcoFloor_{i}',p,y0,y1,colors[i])
       # Offset green roof/terrace with a non-flat crest, 3D with actual thickness.
       roof=[(x+.13,z+.18) for x,z in p]
       prism(s,f'IntegratedGreenTerrace_{i}',roof,y1,y1+.32,['lichen','sage','darkolive'][i])
       for a,b in zip(p,p[1:]+p[:1]):
           pv(s,f'WarmWoodClimateFacade_{i}',a,b,y0+.30,y1-.28,'blueglass' if i%2==0 else 'glass2',.10)
           # wood timber fins genuinely attached to façade, not freestanding poles
           for t in np.linspace(0,1,5,endpoint=False):
               q=(np.array(a)*(1-t)+np.array(b)*t)
               post(s,f'EcoFacadeFins_{i}',q[0],q[1],y0+.15,y1,.067,'warmwood')
    # A proper continuous zigzag landscaped circulation ramp above built floors:
    # roof to terrace structural beams; no player-access claim.
    for i in range(2):
       z=5.0+i*3.0;left=(1.1+i*2.2,z);right=(12.7-i*.8,z+1.2)
       brace(s,'TerraceStructuralSteel',(left[0],3.8+i*2.4,left[1]),(right[0],5.7+i*2.35,right[1]),.15,'charcoal')
    # narrow rainwater recovery garden away from waterworks G and away from E roads
    for x,z,scale_ in [(6.7,13.1,.9),(10.2,12.8,.7)]:s.tree(x,z,scale_,'olive')
    for x,z in [(-4.1,9.2),(-1.7,11.1)]:s.garden(x,z,3.15,1.2,'deepgreen')
    # Rainwater feature should be not a flat circular basins row; descending contour pond in front.
    water=[(2.0,0.8),(5.25,.4),(7.7,-.6),(8.15,-1.45),(5.25,-1.10),(2.0,-.25)]
    prism(s,'EcologicalRillStoneLining',water,.17,.34,'stone2')
    prism(s,'EcologicalRillWater',[(x*.99,z*.96) for x,z in water],.35,.385,'waterblue')
    for x in np.linspace(2.4,6.8,8):brace(s,'RainWaterFlowDirection',(x,.405,-.22),(x+.35,.405,-.43),.028,'watercream')


def landmark_H(s):
    """H: two book leaves truly bearing on expansive full-scale learning gallery and column spans."""
    # large full-length 2-storey library/learning center placed north of main 4.8 spine
    rect(s,'LearningHallStonePodium',-.9,5.4,20.9,12.45,.20,.64,'stone2')
    rect(s,'InhabitedLearningGallery',-.9,5.25,19.0,10.0,.64,6.35,'white2')
    # deep central atrium and three recognizable program wings
    rect(s,'LearningCentralAtrium',-.90,5.45,4.2,10.1,.65,8.2,'blueglass')
    banded_glass(s,'BookLearningEntrance',(-10.4,.45),(8.65,.45),.8,6.25,24,'blueglass','slateblue')
    banded_glass(s,'LearningRearElevation',(-10.4,10.1),(8.65,10.1),.8,6.2,24,'deepglass','charcoal')
    banded_glass(s,'StudyEastFacade',(8.8,.6),(8.8,9.95),.8,6.2,12,'glass2','warmwood')
    banded_glass(s,'StudyWestFacade',(-10.4,.6),(-10.4,9.95),.8,6.2,12,'glass2','warmwood')
    # True thick, curved 'pages' with folding ridges, long timber beams & matching support piers.
    for side in (-1,1):
        lo,hi= (-12.4,-.9) if side==-1 else (-.9,10.4)
        def leaf(x,z,side=side):
           t=abs(x+.9)/(11.5 if side==-1 else 11.3)
           return [x,7.0+3.7*t**1.28+0.36*math.sin((z-.2)/10.7*math.pi),z]
        s.surface('TrueLongSpanFoldedBookLeaf',lo,hi,-.85,11.3,leaf,'roofblue' if side==-1 else 'ochre',38,19,.48)
        for zz in np.linspace(-.38,10.65,10):
            x=lo if side==-1 else hi
            brace(s,'PageRoofLaminatedRibs',(-.9,7.12,zz),(x,leaf(x,zz)[1]-.1,zz),.145,'bronze2')
            post(s,'StructuralOuterBookPiers',x,zz,.21,leaf(x,zz)[1]-.38,.107,'warmwood')
    rect(s,'BookSkylightBetweenLeaves',-.9,5.3,1.8,10.8,7.0,8.35,'blueglass')
    for z in np.linspace(0,10.45,9):post(s,'ReadingSpineStructuralFins',-.9,z,6.9,8.45,.065,'slateblue')
    # Real tiered learning agora with long accessible runaround, instead of toy stadium.
    for i in range(4):
       z=-3.0-i*.85
       rect(s,'OutdoorLearningAmphitheater',-3.75,z,10.5-i*.50,.75,.18+i*.19,.32+i*.19,'stone2')
    for x,z in [(-11,11.2),(12,10.4)]:s.tree(x,z,.65,'pink' if x<0 else 'olive')


def remove_solid_volume(s, names):
    """Replace facade-blocking boxes with modeled floorplates, cross-beams and public glass."""
    keep=[]
    for n,m in s.building_parts:
        if n in names:
            for color,group in s.meshes.items():
                for i,v in enumerate(group):
                    if v is m:group.pop(i);break
        else:keep.append((n,m))
    s.building_parts=keep

def landmark_E_v15(s):
    """E: one inhabited folded landform, two interlocking terrace wings and environmental court.
    Not a glass greenhouse or three stacked cuboids. Object spaces x,z local.
    """
    lower=[(-1.7,2.4),(6.5,1.25),(12.9,2.0),(13.7,6.3),(9.9,9.9),(1.4,9.0),(-2.3,6.1)]
    upper=[(1.6,5.8),(5.6,5.1),(12.5,6.7),(11.2,12.4),(4.15,13.3),(1.2,10.2)]
    prism(s,'LowEcologyCommunityLevel',lower,.20,4.15,'ivory')
    prism(s,'UpperEcologyResearchLevel',upper,4.20,7.25,'stone2')
    # Fully expressed first and second floor glazed envelope, with timber piers.
    for idx, (poly,y0,y1) in enumerate([(lower,.65,4.00),(upper,4.52,7.08)]):
        for k,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
            if idx==0 and k in (2,3):continue
            pv(s,f'IntegratedHabitableEcologyGlazing_{idx}',a,b,y0,y1,'blueglass' if idx==0 else 'glass2',.10)
            for t in np.linspace(0,1,5,endpoint=False):
                x,z=np.array(a)*(1-t)+np.array(b)*t
                post(s,f'EcologyTimberFaçadeRibs_{idx}',x,z,y0-.25,y1+.17,.08,'warmwood')
            pv(s,f'EcoGlazingTwoLevelBand_{idx}',a,b,y0+.9 if idx else 2.85,y0+1.05 if idx else 3.08,'warmwood',.18)
    # Broad sculptural landform canopy: rises from western planted promontory to high lookout.
    def landroof(x,z):
        u=(x+2.4)/16.25;v=(z-1.6)/11.6
        return [x,4.5+3.35*v+.90*math.sin(math.pi*u*.88)+.22*(1-u),z]
    s.surface('ContinuousFoldedEarthRoof',-2.15,13.5,1.45,9.1,landroof,'sage',39,23,.38)
    # Upper roof wing moves diagonally and has its own deep earth structure, not hovering above.
    def upper_roof(x,z):
        return [x,7.4+1.08*(z-6.1)/6.8+.40*(x-3.0)/9.4,z]
    s.surface('TerraceGeoCrest',3.0,11.7,6.1,12.75,upper_roof,'darkolive',24,19,.36)
    for x in np.linspace(-1.5,12.8,12):
        zz=6.3
        brace(s,'TerraceMainRoofStructure',(x,4.06,zz),(x,landroof(x,zz)[1]-.2,zz),.115,'warmwood')
    for x in np.linspace(3.4,11.25,9):
        brace(s,'UpperTerraceTimberBents',(x,7.10,9.1),(x,upper_roof(x,9.1)[1],9.1),.115,'charcoal')
    # Cultivated green roofs: true low planting geometry resting on sloped surfaces.
    for z in np.linspace(3.1,7.8,5):
       for x in np.linspace(-.65,10.8,12):
          y=landroof(x,z)[1]
          if ((round(x*7)+round(z*5))%4)!=0:
              # Grounded, thin sedum geometry, not spherical floating plants.
              s.hardbox('ActualGreenRoofSedumStrip',x,z,.48,.27,y+.02,y+.12,'lichen')
    for z in (8.0,9.7,11.1):
       for x in (5.1,7.0,9.0):
          y=upper_roof(x,z)[1]
          s.hardbox('UpperGreenRoofSedum',x,z,.48,.35,y+.02,y+.14,'leaf')
    # Eco ridgeline ventilation core INTEGRATED with the highest inhabitable terrace.
    # No helipad-like freestanding lookout. It is a roof-connected passive environmental fin.
    ridge=[(8.65,8.50),(10.45,8.7),(10.95,11.25),(9.25,11.45)]
    prism(s,'EcoPassiveClimateAtrium',ridge,6.45,9.45,'glass2')
    for i,(a,b) in enumerate(zip(ridge,ridge[1:]+ridge[:1])):
        pv(s,'ClimateAtriumGlazing',a,b,7.05,9.45,'blueglass',.10)
        post(s,'EcoClimateLoadPosts',a[0],a[1],6.10,9.55,.12,'warmwood')
    # A tapered sloping crest grows directly out of the living roof, same green palette.
    for i,x in enumerate(np.linspace(8.35,11.5,9)):
        z=8.75 + (x-8.35)*.85
        y=9.55+(x-8.35)*.30
        brace(s,'EcoClimateTimberSunFins',(x,7.25,z),(x,y,z),.105,'warmwood')
    prism(s,'EcoCrestIntegratedRoof',[(8.0,8.45),(11.20,8.60),(11.8,11.65),(8.85,12.0)],9.48,9.81,'darkolive')
    brace(s,'CrestStructuralAttachment',(8.5,7.25,8.2),(9.0,9.52,9.1),.15,'charcoal')
    # Exposed horizontal balconies, real load-bearing piers and a diagonal vegetated terrace edge.
    s.slab('HabitableRoofTerraceMain',[(.5,5.6),(10.3,5.8),(9.65,6.45),(0,6.5)],4.15,4.55,'wood2')
    for x in np.linspace(1.1,9.8,14):
        post(s,'TerracePublicBalustrade',x,5.93,4.55,5.45,.052,'bronze2')
    brace(s,'GreenTerraceHandrail',(1.1,5.45,5.93),(9.8,5.45,5.93),.06,'bronze2')
    # Native rain garden along foot of building: water channel is landscaped and grounded.
    banks=[(1.3,-.2),(3.2,-.55),(6.2,-.86),(8.5,-.95),(9.2,-1.6),(6.6,-1.7),(3.0,-1.3)]
    prism(s,'EnvironmentalRillBase',banks,.13,.27,'stone2')
    prism(s,'EnvironmentalRillFlow',[(x*.985,z*.96) for x,z in banks],.28,.31,'waterblue')
    for x,z in [(-5.0,9.2),(-7.0,7.0),(-3.6,11.2),(11.2,12.2)]:s.tree(x,z,.59,'olive')
    s.garden(-6.2,2.9,4.3,1.15,'deepgreen')
    s.garden(-5.4,8.9,3.9,1.05,'green')

def reinforce_public_landmarks(s):
    if s.code=='D':
        remove_solid_volume(s,{'PublicServiceLowerHall','CivicSecondFloor'})
        # Two real occupied levels and a smaller closed service core behind extensive civic glass.
        rect(s,'CivicGroundFloorStructuralSlab',4.0,4.35,18.1,10.9,.9,1.17,'stone2')
        rect(s,'CivicUpperFloorStructuralSlab',4.0,4.35,18.1,10.9,4.2,4.5,'ivory')
        rect(s,'AdministrativeSolidCore',10.65,6.9,4.3,6.5,1.0,7.22,'stone2')
        for zz in np.linspace(-.4,9.1,11):
            for xx in (-4.6,12.6):post(s,'CivicPerimeterLoadPosts',xx,zz,.22,7.4,.14,'bronze2')
    elif s.code=='H':
        remove_solid_volume(s,{'InhabitedLearningGallery'})
        rect(s,'LearningLowerFloorSlab',-.9,5.25,18.8,9.9,.65,.96,'stone2')
        rect(s,'LearningUpperFloorSlab',-.9,5.25,18.8,9.9,3.5,3.78,'white2')
        rect(s,'LearningBookshelfSolidCore',6.8,6.9,2.5,4.1,1.0,6.2,'ivory')
        for xx in (-10,9.1):
            for zz in (1.0,4.3,7.3,9.85):post(s,'LoadBearingReadingColumns',xx,zz,.3,6.4,.12,'bronze2')
    elif s.code=='B':
        # U-shaped foyer emphasized as architectural entrance without creating a second building.
        rect(s,'WarmEntryFascia',4.25,-8.15,6.4,.32,5.12,5.53,'warmwood')
        for x in np.linspace(1.8,6.6,9):post(s,'EntryHumanScaleScreens',x,-8.05,.25,5.33,.052,'ochre')


LANDMARKS={'B':landmark_B,'D':landmark_D,'E':landmark_E_v15,'H':landmark_H}


def architectural_finish(s):
    """Detailing pass after landmark form, prior to scaling; distinct across each site."""
    if s.code=='B':
        # Deep continuous veranda on courtyard-facing elevations, two real occupied levels.
        c=(-2.65,-2.05)
        for a in np.linspace(math.radians(46),math.radians(304),48):
            x,z=c[0]+5.10*math.cos(a),c[1]+5.10*math.sin(a)
            if int((a-math.radians(46))*100)%3==0:
                pv(s,'CareSecondFloorBalconyBand',(x-.13,z-.13),(x+.13,z+.13),3.45,3.67,'warmwood',.13)
            post(s,'WarmVerticalSunScreen',x,z,3.7,5.8,.042,'bronze2')
        for j,a in enumerate(np.linspace(math.radians(48),math.radians(306),21)):
            x,z=c[0]+8.8*math.cos(a),c[1]+8.8*math.sin(a)
            # prominent fin bracket under roof casting facade shadow
            brace(s,'TimberRoofDeepBracket',(x,4.7,z),(x,6.35,z),.055,'wood2')
        s.garden(-9.6,-8.55,2.8,.7,'deepgreen')
    elif s.code=='D':
        # Rational civic facade, clear two floors with centered entrance, no billboard.
        for zz in np.linspace(-1.1,9.7,13):
            for xx in (-5.5,13.4):
                post(s,'HighCivicVerticalShade',xx,zz,1.05,6.8,.073,'bronze2')
        for xx in np.linspace(-4.8,13.0,18):
            brace(s,'TransparentFoyerUpperBand',(xx,4.45,-1.5),(xx,4.48,-1.1),.048,'bronze2')
        # Braced entrance portal and durable stone apron
        for xx in (1.65,6.15):
            brace(s,'CivicLaminatedDoorFrame',(xx,.35,-2.15),(xx,7.3,-2.15),.16,'warmwood')
        for zz in np.linspace(-1.0,9.8,11):
            brace(s,'MunicipalRoofFasciaProfile',(-6.4,10.0,zz),(14.3,10.0,zz),.023,'bronze2')
    elif s.code=='E':
        return # R15 iconic geology is authored directly in landmark_E_v15.
        # Terrace becomes green landform with actual ribbed roof and occupied bay depth.
        for x,z,level,w in [
            (1.7,4.6,3.75,3.9),(4.8,8.3,6.15,3.6),(8.2,11.65,8.15,3.2)]:
            s.garden(x,z,w,.9,'green')
            for dx in np.linspace(-w*.33,w*.33,6):
                s.sphere('TerraceDiverseLowFoliage',x+dx,z,level+.48,.18,'lightgreen',1)
        # uppermost geo-crest is attached and pitches up to the north-east as a landmark.
        def eco_fold(u,v):
            return [u,8.36+.85*(u-3.4)/9.0 + .35*(v-7.1)/5.5,v]
        s.surface('ContinuousGeologyRidgeRoof',3.5,12.4,7.0,12.65,eco_fold,'lichen',24,15,.36)
        for x in np.linspace(3.8,12.1,8):
            brace(s,'GeoRidgeEngineeredTimberSupport',(x,7.7,8.0),(x,eco_fold(x,8.0)[1],8.0),.10,'warmwood')
        # small rain gardens run parallel to crossing, do not become a G-style dam.
        for x,z in [(-5.7,8.7),(-4.0,10.25)]:
            s.sphere('NativePollinatorGarden',x,z,.52,.36,'lichen',1)
    elif s.code=='H':
        # Double-height glass and reading terraces: visually a building, not a book roof on a box.
        for xx in np.linspace(-10.0,8.1,18):
            pv(s,'ContinuousBookMainElevation',(xx,.39),(xx+0.67,.39),.79,6.15,'blueglass',.11)
            post(s,'ReadingArcadeFrontFrames',xx,.3,.21,6.2,.08,'bronze2')
        for xx in np.linspace(-10.2,8.5,20):
            brace(s,'BookLeafUnderRidge',(xx,6.5,1.0),(xx,6.72,10.3),.062,'warmwood')
        # Exposed upper level terrace and library cantilever, connected to real floor slab
        rect(s,'LearningSecondFloorOutline',-1.0,5.0,17.6,9.5,3.6,3.82,'stone2')
        for xx in [-9.75,-7.2,5.7,8.2]:
            post(s,'LearningGalleryColumns',xx,4.8,.30,6.50,.12,'warmwood')

def fit_building_to_site(s):
    """Reduce only the building in constrained corners, never enlarge the 30-34 site."""
    factors={'B':(1,1,0,0),'D':(.865,.865,-1.2,-1.2),
             'E':(.90,.81,-1.2,-1.25),'H':(.89,.89,.25,-.55)}
    fx,fz,tx,tz=factors[s.code]
    done=set()
    for n,m in s.building_parts:
        if id(m) in done:continue
        done.add(id(m))
        v=m.vertices.copy();v[:,0]=v[:,0]*fx+tx;v[:,2]=v[:,2]*fz+tz;m.vertices=v



def final_site_architecture(s):
    """Function-linked public placemaking. Each landscape element tied to a public use;
    avoid dense arbitrary shrub fields and keep core paths/bridge mouths clear."""
    code=s.code
    if code=='B':
        # Therapeutic outdoor corridor (planted bands + seating) west of the sheltered court.
        # These are low beds. Existing crescent is already the landmark.
        for x,z,w,d in [(-10.9,-10.3,3.5,.68),(-9.9,8.35,3.6,.62),(-8.0,-10.8,2.1,.65)]:
            if s._publicCorridor.distance(Point(x,z))>2.15:s.garden(x,z,w,d,'green')
        # a purposeful warm-oak conversation circle on the recovery terrace
        for a in np.linspace(.25,2.65,7):
            x=-2.65+3.9*math.cos(a);z=-2.05+3.3*math.sin(a)
            if s._publicCorridor.distance(Point(x,z))>1.25:
                s.box('CurvedTherapyGardenSeat',x,z,.55,.22,.27,.64,'wood2')
    elif code=='D':
        # A public services compass defined in floor pavers, not large 3D clutter.
        for j in range(7):
            x=-6.1+j*.74;z=-4.3-j*.11
            if s._publicCorridor.distance(Point(x,z))>1.0:
                s.box('QuietCivicWayfindingPavers',x,z,.48,.075,.14,.175,'bronze2')
        # Double-sided civic information monolith, self-supporting on plaza, not a fake screen.
        x,z=-6.2,5.8
        if s._publicCorridor.distance(Point(x,z))>2.5:
            s.box('ServiceInformationStoneBase',x,z,1.8,.68,.15,.39,'stone2')
            s.box('ServiceInformationMetalFrame',x,z,1.55,.36,.39,3.6,'charcoal')
            s.box('ServiceInformationGlassPanel',x,z-.22,1.2,.10,1.2,3.25,'blueglass')
    elif code=='E':
        # Planted rain gardens form one low basin along the eco ridge; not giant floating pool.
        for x,z,w,d in [(-5.6,5.3,3.4,1.6),(-6.2,9.3,3.2,1.2)]:
            if s._publicCorridor.distance(Point(x,z))>2.7:s.garden(x,z,w,d,'green')
        # the lower promenade has a covered eco-learning observation point
        if s._publicCorridor.distance(Point(-4.2,4.0))>3.4:
            for x,z in [(-5.9,2.9),(-2.2,2.9),(-5.9,5.1),(-2.2,5.1)]:
                post(s,'EcoOutdoorLearningPosts',x,z,.15,3.4,.13,'warmwood')
            rect(s,'EcoOutdoorLearningCanopy',-4.05,4.0,4.1,2.7,3.35,3.58,'ochre')
    elif code=='H':
        # Graduated forum is organized as two amphitheater terraces, not a toy sports oval.
        for i in range(3):
            x,z=-4.4,-2.45-i*.66
            if s._publicCorridor.distance(Point(x,z))>1.55:
                s.box('KnowledgeForumTerraceStep',x,z,7.7-i*.4,.50,.18+i*.2,.34+i*.2,'stone2')
        for x,z in [(-11.5,9.7),(11.7,9.6)]:
            if s._publicCorridor.distance(Point(x,z))>2:s.tree(x,z,.58,'olive')



def cohesive_site_details(s):
    """Entry, terrace, learning / ecological site cues; no same-template scattered planters."""
    def safe(x,z,r=1.0):
        return (x/s.rx)**2+(z/s.rz)**2<.78 and s._publicCorridor.distance(Point(x,z))>r+1.1
    if s.code=='B':
        # Organized shade grove on the quiet side of the occupied crescent.
        for x,z,t in [(-10.8,-9.4,.67),(-7.9,-10.4,.61),(-6.6,8.2,.63)]:
            if safe(x,z,1.3):s.tree(x,z,t,'pink')
        # Timber low wall links outdoors to the inhabited crescent.
        for i in range(7):
            x=-8.75+i*.51;z=-7.4
            if safe(x,z,.6):s.box('TherapyCommunalLowSeat',x,z,.46,.32,.20,.57,'wood2')
    elif s.code=='D':
        # Plaza has order: a recessed public services compass and grounded planted edge.
        for x,z in [(9.1,-6.5),(11.1,-6.4),(-7.8,-7.4)]:
            if safe(x,z,1.3):s.tree(x,z,.67,'olive')
        for x,z in [(-3.6,-6.0),(1.3,-6.1)]:
            if safe(x,z,1.25):
                s.box('DigitalCivicLinearBench',x,z,2.0,.53,.19,.56,'stone2')
                s.box('DigitalCivicWarmTop',x,z,1.9,.39,.56,.69,'warmwood')
    elif s.code=='E':
        # Site has an educational water garden, NOT a second dam; low planting in one crescent.
        for x,z in [(-9.8,8.5),(-7.7,10.0),(2.0,12.8)]:
            if safe(x,z,1.15):s.tree(x,z,.62,'olive')
        for x,z in [(-6.2,4.8),(-5.4,6.9)]:
            if safe(x,z,1.2):s.garden(x,z,3.2,1.1,'green')
    elif s.code=='H':
        # The outdoor learning agora is framed by 2 staggered native shade groves.
        for x,z in [(12.0,8.5),(-10.0,11.0),(-12.0,5.2)]:
            if safe(x,z,1.3):s.tree(x,z,.62,'pink' if x<0 else 'olive')
        # Education wayfinding threshold as a physical low timber structure (not an unreadable label).
        if safe(5.9,-3.1,1.0):
            s.box('LearningWayfindingPlinth',5.9,-3.1,2.2,.58,.21,.72,'warmwood')
            s.box('LearningWayfindingInset',5.9,-3.46,1.85,.14,.40,.70,'solar')

def add_path(s,poly):
    poly=poly.buffer(0)
    polys=[poly] if poly.geom_type=='Polygon' else list(poly.geoms)
    for v in polys:
        tris=[t for t in triangulate(v) if v.covers(t.representative_point()) and v.intersection(t).area>t.area-1e-6]
        if not tris:continue
        vv=[];ff=[]
        for t in tris:
           pp=list(t.exterior.coords)[:3];k=len(vv);vv.extend([[x,.135,z] for x,z in pp]);ff.append([k,k+1,k+2])
        s.mesh('PublicAccessibleGround4p8',trimesh.Trimesh(vertices=vv,faces=ff,process=False),'stone',role=None)

def build_pedestrian_routes(s):
    routes=[LineString(p) for p in ROUTE[s.code]]
    site=scale(Point(0,0).buffer(1,resolution=140),s.rx*.96,s.rz*.96)
    region=unary_union([r.buffer(2.4,join_style=1,cap_style=1,resolution=8) for r in routes]).intersection(site)
    add_path(s,region)
    s._publicCorridor=region
    s._routeStrings=routes
    # sparse wayfinding pavers, not bright continuous giant ring
    for idx,path in enumerate(routes):
       step=max(2.4,path.length/12)
       for k in np.arange(2.5,path.length-2.5,step):
          q=path.interpolate(k)
          if site.contains(q.buffer(.35)):
             s.box('GuideStoneInlay',q.x,q.y,.38,.17,.137,.156,'bronze2')

def sparse_perimeter(s):
    # 1.1 safety rails excluding near candidate gates; accessible real-world bridge mouths require rebuild.
    gates=[np.asarray(path.coords[0]) for path in s._routeStrings]
    gates+= [np.asarray(path.coords[-1]) for path in s._routeStrings]
    t=np.linspace(0,2*math.pi,105,endpoint=False)
    pts=[(s.rx*.974*math.cos(a),s.rz*.974*math.sin(a)) for a in t]
    okay=[min(np.linalg.norm(np.asarray(p)-q) for q in gates)>3.15 for p in pts]
    for i,p in enumerate(pts):
        j=(i+1)%len(pts)
        if not okay[i] or not okay[j]:continue
        a=pts[j]
        s.girder('SafetyRailContinuous',(p[0],1.08,p[1]),(a[0],1.08,a[1]),.044,'metal',role=None)
        if i%4==0:s.post('SafetyRailPost',p[0],p[1],.15,1.10,.058,'metal',role=None)

def audit(s):
    site=scale(Point(0,0).buffer(1,resolution=192),s.rx*.955,s.rz*.955)
    path=s._publicCorridor
    failures=[];tot_out=0;tot_road=0;roof_collisions=[]
    for n,m in s.building_parts:
       v=m.vertices[:,[0,2]];h=Polygon(v).convex_hull
       out=h.difference(site).area
       b=m.bounds
       road=h.intersection(path).area
       if out>.04 or (road>.04 and b[0][1]<2.8):failures.append({"part":n,"offIslandArea":round(out,3),"groundRoadOverlap":round(road,3),"height":round(float(b[0][1]),2)})
       tot_out+=out
       if b[0][1]<2.8:tot_road+=road
       if road>.05 and b[0][1]>=2.8:roof_collisions.append({'part':n,'area':round(road,2),'minHeight':round(float(b[0][1]),2)})
    return {'island':s.code,'dimensions':r12.SIZES[s.code],'centre':r12.NODE[s.code], '4.8mCandidateRoutes':len(s._routeStrings), 'buildingParts':len(s.building_parts),'outsideTotal':round(float(tot_out),2),'groundRoadOverlapTotal':round(float(tot_road),2),'failures':failures[:60], 'highRoofOverPublicRoute':roof_collisions[:12], 'limitations':'2D corridor over candidate local paths only; not imported to Three.js, no actual collision or mobile FPS testing'}

def render(s,view):
    import vtk
    ren=s.vtk_renderer();ren.GradientBackgroundOff();ren.SetBackground(.93,.957,.967)
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(1100,850);win.SetMultiSamples(4);win.AddRenderer(ren)
    cam=ren.GetActiveCamera();cam.ParallelProjectionOn();cam.SetFocalPoint(0,1.0,0);cam.SetViewUp(0,1,0)
    xyz={'hero':(34,32,-45),'front':(0,16,-60),'back':(0,16,60),'left':(-65,16,0),'right':(65,16,0),'top':(.01,90,.01)}[view]
    cam.SetPosition(*xyz)
    if view=='top':cam.SetViewUp(0,0,-1)
    cam.SetParallelScale(17.5 if view not in ('top',) else 19.5)
    ren.ResetCameraClippingRange();win.Render()
    w2i=vtk.vtkWindowToImageFilter();w2i.SetInput(win);w2i.SetInputBufferTypeToRGB();w2i.ReadFrontBufferOff();w2i.Update()
    output=ROOT/'renders'/f'{s.code}_{view}.png';writer=vtk.vtkPNGWriter();writer.SetFileName(str(output));writer.SetInputConnection(w2i.GetOutputPort());writer.Write();win.Finalize();return output

def export(s):
    from collections import defaultdict
    scene=trimesh.Scene();ntri=0
    for c,meshes in s.meshes.items():
        if not meshes:continue
        m=trimesh.util.concatenate(meshes);m.visual.face_colors=np.asarray([*base.rgb(base.C[c]),255],dtype=np.uint8)
        scene.add_geometry(m,geom_name=c);ntri+=len(m.faces)
    p=ROOT/'models'/f'{s.code}_R18_landmark_concept.glb';p.write_bytes(scene.export(file_type='glb'))
    return {'glb':p.name,'triangles':int(ntri),'bytes':p.stat().st_size,'materials':len(s.meshes)}

def main():
    qa={};stats={}
    for code in 'BDEH':
        s=Design(code);s.terrain();build_pedestrian_routes(s);LANDMARKS[code](s);architectural_finish(s);reinforce_public_landmarks(s);fit_building_to_site(s);final_site_architecture(s);cohesive_site_details(s);sparse_perimeter(s)
        qa[code]=audit(s);stats[code]=export(s)
        print(code,'tri',stats[code]['triangles'],'failures',len(qa[code]['failures']),'outside',qa[code]['outsideTotal'],'ground overlap',qa[code]['groundRoadOverlapTotal'],flush=True)
        for view in ('hero','front','back','left','right','top'):
           render(s,view)
    (ROOT/'qa'/'architecture_audit.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
    (ROOT/'qa'/'assets.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
