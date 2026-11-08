"""苑裡政策島 B/D/E/H R21 — policy-led standalone architectural 3D design.
Derived from R18/R20 research engine only; new geometry + same project candidate world coordinates.
No modification to GitHub or production. X/Z ground, Y up; local origin per island.
Usage: python build_r21.py [--draft]
"""
import math, json, importlib.util, sys, os
from pathlib import Path
from collections import defaultdict
import numpy as np
import trimesh
from shapely.geometry import Point, Polygon, LineString
from shapely.affinity import scale
from shapely.ops import unary_union, triangulate
from PIL import Image, ImageDraw, ImageFont

BASE=Path(__file__).resolve().parent/'base'
spec=importlib.util.spec_from_file_location('r20', str(BASE/'build_r20.py')); p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
r=p.r
r.ROOT=Path(__file__).resolve().parent
r.base.OUT=r.ROOT
Design=r.Design
C=r.base.C
C.update({
'careRoof':'#A56F48','careLinen':'#EFE5D3','careGlass':'#8CAFA9','careGarden':'#5D835E','careBlossom':'#D8A9B0',
'civicStone':'#DED9C9','civicSteel':'#344B5A','civicGlass':'#80ACBD','civicSky':'#2A597B','civicGold':'#CDA667','civicLight':'#E6CC94',
'ecoLeaf':'#628A65','ecoDeep':'#33594B','ecoLight':'#A0C086','ecoWood':'#B99A66','ecoWater':'#4A929D',
'eduBlue':'#325775','eduCream':'#F0E4C9','eduAmber':'#C89C62','eduGlass':'#7DAFBF','eduCoral':'#BA765E',
'rockSide':'#65675D','dirtWarm':'#967E66','paveLight':'#E1D7BD','plazaDark':'#BBAE93','warmLight':'#F6D8A0',
})
ROOT=Path(__file__).resolve().parent
for d in ['models','renders','qa','source','comparison']:(ROOT/d).mkdir(parents=True,exist_ok=True)
road=json.loads((BASE/'BDEH_R18/data/road-candidate-r2.json').read_text())
NODES=road['nodes']
SIZES={'B':(30,28),'D':(32,29),'E':(34,31),'H':(33,30)}

def bx(s,n,x,z,w,d,a,b,c):s.hardbox(n,x,z,w,d,a,b,c)
def pr(s,n,poly,a,b,c):s.hardprism(n,poly,a,b,c)
def post(s,n,x,z,a,b,rad,c):s.post(n,x,z,a,b,rad,c)
def beam(s,n,a,b,rad,c):s.girder(n,a,b,rad,c)
def panel(s,n,a,b,y0,y1,c,thick=.11):s.panel(n,a,b,y0,y1,c,thick)
def glasswall(s,name,a,b,y0,y1,count,col,frame,spandrel=None):
    a=np.array(a,float);b=np.array(b,float)
    for k in range(count):
        u=a+(b-a)*(k/count);v=a+(b-a)*((k+1)/count)
        panel(s,name+'_glazing',u,v,y0,y1,col,.095)
        if spandrel:panel(s,name+'_levelBand',u,v,(y0+y1)*.50-.12,(y0+y1)*.50+.16,spandrel,.16)
        post(s,name+'_verticalMullion',u[0],u[1],y0,y1,.062,frame)
    post(s,name+'_lastMullion',b[0],b[1],y0,y1,.062,frame)
    panel(s,name+'_cornice',a,b,y1-.12,y1+.07,frame,.16)

def skirt_glazing(s, name, polygon, h0,h1, col,frame,spandrel=None,skip=None):
    skip=set(skip or ())
    for i,(u,v) in enumerate(zip(polygon,polygon[1:]+polygon[:1])):
        if i in skip:continue
        count=max(2,min(19,int(np.linalg.norm(np.array(u)-np.array(v))/.65)))
        glasswall(s,name+f'_side{i}',u,v,h0,h1,count,col,frame,spandrel)

def ellipse(s,n,cx,cz,rx,rz,y0,y1,col,N=58,rotation=0):
    ts=np.linspace(0,math.tau,N,endpoint=False)
    ps=[(cx+rx*math.cos(t)*math.cos(rotation)-rz*math.sin(t)*math.sin(rotation),cz+rx*math.cos(t)*math.sin(rotation)+rz*math.sin(t)*math.cos(rotation)) for t in ts]
    pr(s,n,ps,y0,y1,col)
    return ps

def polyline(s,n,points,y,rad,col):
    for a,b in zip(points[:-1],points[1:]):beam(s,n,(a[0],y,a[1]),(b[0],y,b[1]),rad,col)

def facade_louvers(s,n,a,b,y0,y1,N,mat='warmwood'):
    a=np.array(a);b=np.array(b)
    for t in np.linspace(0,1,N):
        u=a+(b-a)*t
        post(s,n,u[0],u[1],y0,y1,.079,mat)

def sloped_band(s,n,x0,x1,z0,z1,f,mat,thick=.38,nu=22,nv=12):
    s.surface(n,x0,x1,z0,z1,f,mat,nu=nu,nv=nv,thick=thick)

def garden(s,n,x,z,w,d,kind='ecoLeaf'):
    bx(s,n+'_lowDryWall',x,z,w,d,.12,.31,'stone2')
    bx(s,n+'_soil',x,z,w-.20,d-.2,.31,.40,'earthbrown')
    for px in np.linspace(x-w*.35,x+w*.35,max(2,int(w/.65))):
        for pz in np.linspace(z-d*.25,z+d*.25,max(2,int(d/.48))):
            if int(px*9+pz*13)%3==0:
                bx(s,n+'_groupedPlants',px,pz,.24,.14,.40,.62,kind)

def bench(s,n,x,z,w=1.7,c='warmwood'):
    bx(s,n+'_seat',x,z,w,.48,.53,.67,c)
    bx(s,n+'_back',x,z+.23,w,.11,.64,1.26,c)
    for xx in (x-w*.4,x+w*.4):post(s,n+'_leg',xx,z,.14,.55,.064,'copperdark')

def structure_B(s):
    """「年輪·擁抱」built as occupied overlapping crescent wings, not a decorative roof.
    West-south parcel is outside all four gate-traces. Two heights, open court, real verandas.
    """
    cx,cz=-3.95,-3.90
    aa=np.linspace(math.radians(63),math.radians(313),45)
    def xy(r,t):return (cx+r*math.cos(t),cz+r*math.sin(t))
    def arc_ring(r0,r1,start,stop):
        tt=np.linspace(math.radians(start),math.radians(stop),45)
        return [xy(r1,t) for t in tt]+[xy(r0,t) for t in tt[::-1]]
    # Two tectonically related wings; double storey south, one-and-half north.
    arcA=arc_ring(4.18,7.65,83,222)
    arcB=arc_ring(4.18,7.65,227,310)
    for name,outline,level in [('LongStayWing',arcA,5.95),('DayCareWing',arcB,4.65)]:
        pr(s,name+'_groundPlinth',outline,.17,.76,'stone2')
        pr(s,name+'_firstFloor',outline,2.95,3.21,'careLinen')
        pr(s,name+'_capSlab',outline,level-.17,level+.02,'careRoof')
    # Glazed facades, rhythm follows continuous real ground floors.
    for wing,tlist,lev in [('LongStay',np.linspace(83,222,33),5.95),('DayCare',np.linspace(227,310,22),4.65)]:
        for radius,label in [(7.58,'outer'),(4.22,'court')]:
            for idx,(t0,t1) in enumerate(zip(tlist[:-1],tlist[1:])):
                a=xy(radius,math.radians(t0));b=xy(radius,math.radians(t1));
                panel(s,f'{wing}_{label}_glazedBay',a,b,.81,lev-.22,'careGlass',.11)
                if idx%2==0:post(s,f'{wing}_{label}_bentColumn',a[0],a[1],.2,lev+.55,.095,'careRoof')
                panel(s,f'{wing}_{label}_floorLine',a,b,2.87,3.18,'careRoof',.13)
        # roof built from true glulam bending beam ribs and thick shell
        q0,q1=(83,222) if wing=='LongStay' else (227,310)
        az=np.linspace(q0,q1,32)
        grid=[]
        for t in np.linspace(math.radians(q0),math.radians(q1),45):
            pass
        for rad in np.linspace(3.88,8.00,8):
            grid.append([[cx+rad*math.cos(math.radians(t)),lev+.25+.63*math.sin((t-q0)/(q1-q0)*math.pi)+.32*(rad-3.88)/4.12,cz+rad*math.sin(math.radians(t))] for t in az])
        s.patch(wing+'_copperLamellaRoof',np.array(grid),'careRoof' if wing=='LongStay' else 'warmwood',.34)
        s.building_parts.append((wing+'_copperLamellaRoof',s.meshes['careRoof' if wing=='LongStay' else 'warmwood'][-1]))
        for t in np.linspace(q0,q1,19):
            t=math.radians(t);u=xy(4.05,t);v=xy(7.88,t)
            yy=lev+.3+.6*math.sin((t-math.radians(q0))/math.radians(q1-q0)*math.pi)
            beam(s,wing+'_woodLoadRib',(u[0],yy-.18,u[1]),(v[0],yy+.18,v[1]),.10,'copperdark')
    # Their north and east arms touch a shared glazed family forum at rear of entry spine.
    shared=[(.20,-8.7),(3.35,-8.7),(3.45,-4.1),(1.0,-2.55),(-.3,-3.85)]
    pr(s,'SharedFamilyForumSolidPlinth',shared,.18,.63,'stone2')
    pr(s,'FamilyForumExposedMezzanine',shared,3.42,3.72,'careRoof')
    skirt_glazing(s,'FamilyForumTwoLevelGlass',shared,.70,6.2,'careGlass','copperdark','careLinen')
    pr(s,'FamilyForumSawtoothRoof',[(x-.18,z-.2) for x,z in shared],6.2,6.62,'careRoof')
    for x,z in [(2.9,-7.5),(2.9,-5.1)]:post(s,'FamilyForumTimberLoadColumn',x,z,.24,6.25,.14,'copperdark')
    # therapeutic court: fully legible concentric use, NO giant target ring.
    ellipse(s,'HealingCourtyardWalkablePaving',cx,cz,3.75,3.65,.15,.28,'paveLight')
    ellipse(s,'SensoryHerbRing',cx,cz,2.65,2.45,.29,.41,'careGarden')
    ellipse(s,'GardenTreeDryRootZone',cx-.15,cz+.35,.83,.75,.42,.54,'stone2')
    s.tree(cx-.15,cz+.35,.9,'pink')
    for angle in (math.pi*.78,math.pi*1.25,math.pi*1.72):
        x=cx+3.32*math.cos(angle);z=cz+3.1*math.sin(angle)
        bench(s,'CareChatPlace',x,z,1.2)
    # Mature landscape comes in organized two groups, NOT even scattered pots.
    for x,z,w,d in [(-11.2,3.3,2.0,.7),(-6.7,-10.7,1.8,.65)]:
        garden(s,'CareShadeGarden',x,z,w,d,'careGarden')
    for x,z in [(-10.3,5.7),(-8.4,5.7)]:s.tree(x,z,.53,'olive')

def structure_D(s):
    """「城市服務之門」two occupied civic wings separated by a full-clearance diagonal street.
    The connected roof-bridge is the iconic civic portal, not a normal office tower.
    """
    NE=[(2.75,3.15),(11.6,3.15),(11.75,9.0),(7.5,11.0),(2.75,10.25)]
    SW=[(-10.8,-9.9),(-2.75,-9.95),(-2.75,-4.85),(-7.6,-3.95),(-10.8,-6.0)]
    for name,foot,top,frame,gl in [('CivicNEPublicHall',NE,6.35,'civicSteel','civicGlass'),('CivicSWServiceHall',SW,5.18,'civicSteel','mistglass')]:
        pr(s,name+'_foundation',foot,.18,.71,'stone2')
        pr(s,name+'_occupiedSecondFloor',foot,3.2,3.51,'civicStone')
        skirt_glazing(s,name+'_floorheightGlazing',foot,.8,top-.17,gl,frame,'civicStone')
        pr(s,name+'_cornice',foot,top-.1,top+.15,'civicStone')
    # lower public hall features visible desks and civic help-points through transparent enclosure
    for x,z in [(5.0,4.85),(8.5,4.85),(5.2,7.5),(9.2,7.6)]:
        bx(s,'OneStopCivicCounter',x,z,2.0,.65,.75,1.55,'civicStone')
        bx(s,'OneStopCivicTerminal',x,z+.25,.65,.14,1.55,2.23,'civicGlass')
        post(s,'CivicQueueSignPost',x+1.0,z-.2,.4,2.2,.05,'civicGold')
    # Policy-identified civic portal: a diagonal elevated roof BRIDGE ties both occupied wings.
    # Central road runs NW-SE, while this fully structural roof bridges SW-NE across it.
    # Lower envelope above all 4.8m roads: >6.2 world units. No freestanding floating arc.
    tvals=np.linspace(-7.0,6.4,42); offs=np.linspace(-1.55,1.55,11)
    girders=[]
    def zbridge(t,o):
        x=t+o*.707;z=t-o*.707
        y=6.20+3.75*(max(0,1-(abs(t)/7.5)**1.6))+.14*math.cos(o/1.55*math.pi)
        return [x,y,z]
    grid=np.array([[zbridge(t,o) for t in tvals] for o in offs])
    s.patch('CivicIntegratedDiagonalPublicPortal',grid,'civicSky',.48)
    s.building_parts.append(('CivicIntegratedDiagonalPublicPortal',s.meshes['civicSky'][-1]))
    for t in np.linspace(-6.8,6.2,21):
        a=zbridge(t,-1.48);b=zbridge(t,1.48)
        beam(s,'CivicPortalExposedGlulamTruss',(a[0],a[1]-.35,a[2]),(b[0],b[1]-.35,b[2]),.14,'civicGold')
    for t,o in [(-6.5,0),(5.9,0)]:
        x,y,z=zbridge(t,o)
        post(s,'CivicPortalLoadBearingPier',x,z,5.2,y-.4,.26,'civicSteel')
    # Two aligned wings share a single architectural spine and open service threshold.
    # integrated split roof wings above occupiable halls
    def ne_roof(x,z):return [x,6.7+.55*(x-2.75)/9 +.5*(z-3)/8,z]
    sloped_band(s,'CivicNEFoldedServiceRoof',2.80,11.38,3.00,9.65,ne_roof,'civicSky',.32,22,18)
    def sw_roof(x,z):return [x,5.50+.90*(10+x)/7.5 +.12*(z+6)/6,z]
    sloped_band(s,'CivicSWFoldedServicesRoof',-10.8,-2.55,-10.0,-4.0,sw_roof,'civicSteel',.30,22,15)
    # prominent horizontal bilingual-style low-poly data ribbon, no unreadable bitmap screen
    for i in range(13):
        xx=3.3+i*.54
        bx(s,'TransparentServiceDataSpandrel',xx,3.02,.38,.11,5.55,5.72,'civicGold' if i%4==0 else 'civicLight')
    # public wayfinding district: color-inlaid lines, no bulky monument blocking passage
    for x,z in [(12.8,1.0),(10.9,-2.6)]:
        if s._publicCorridor.distance(Point(x,z))>2.8: garden(s,'CivicPublicFlowerBed',x,z,2.2,.72,'ecoLeaf')
    for x,z in [(11,11.7),(-11.7,-10.9)]:
        if s._publicCorridor.distance(Point(x,z))>2.5:s.tree(x,z,.52,'olive')

def structure_E(s):
    """「城市綠脈」one elevated planted continuous walkover + inhabited ecology pavilion.
    Four bridge mouths remain connected below; no greenhouse or stacked roofs.
    """
    NE=[(2.4,4.45),(10.9,4.50),(11.4,8.6),(7.3,10.15),(2.4,9.8)]
    SW=[(-10.65,-10.50),(-3.4,-10.50),(-3.4,-6.50),(-7.8,-5.75),(-10.65,-7.15)]
    for tag,poly_,h,col in [('BioCityCommunityGallery',NE,5.55,'ecoWood'),('RainGardenLearningStation',SW,4.2,'ecoWood')]:
        pr(s,tag+'_stoneBase',poly_,.20,.60,'stone2')
        pr(s,tag+'_mezzanine',poly_,2.8,3.07,'paveLight')
        skirt_glazing(s,tag+'_passiveClimateGlazing',poly_,.63,h-.14,'mistglass','ecoWood','paveLight')
        pr(s,tag+'_roofBearing',poly_,h-.15,h+.06,col)
    # Landscape sculpture is an actual elevated structural green spine linking districts.
    # Deck starts above low buildings, stays >5.15 over road. Not marketed as player traversable.
    path=np.array([[-7.9,-7.85],[-5.8,-3.2],[-2.2,.85],[2.6,3.8],[6.2,7.4]],float)
    tangents=[]
    for i in range(len(path)):
        tangent=path[min(len(path)-1,i+1)]-path[max(0,i-1)]
        tangent=tangent/np.linalg.norm(tangent)
        tangents.append(tangent)
    # smooth Catmull-ish interpolation via sampled splines
    from scipy.interpolate import CubicSpline
    uu=np.arange(len(path),dtype=float)
    spx=CubicSpline(uu,path[:,0],bc_type='natural');spz=CubicSpline(uu,path[:,1],bc_type='natural')
    tt=np.linspace(0,len(path)-1,75)
    center=np.array([[float(spx(t)),float(spz(t))] for t in tt]);dy=np.gradient(center,axis=0);dy/=np.linalg.norm(dy,axis=1)[:,None]
    normals=np.array([-dy[:,1],dy[:,0]]).T
    deck=[];green=[]
    for cross in np.linspace(-1,1,7):
        ribbon=[];grass=[]
        for i,(x,z) in enumerate(center):
            px,pz=np.array([x,z])+normals[i]*cross*1.36
            Y=4.23+1.47*i/(len(center)-1)+2.55*math.sin(i/(len(center)-1)*math.pi)
            ribbon.append([px,Y,pz]);grass.append([px,Y+.25,pz])
        deck.append(ribbon);green.append(grass)
    s.patch('LivingLandscapeSignatureElevatedWalkover',np.array(deck),'ecoWood',.32)
    s.building_parts.append(('LivingLandscapeSignatureElevatedWalkover',s.meshes['ecoWood'][-1]))
    s.patch('BiophilicContinuousGreenRibbon',np.array(green),'ecoLeaf',.19)
    s.building_parts.append(('BiophilicContinuousGreenRibbon',s.meshes['ecoLeaf'][-1]))
    # no unprotected walking claim: continuous high ribbon is a sculptural green roof, not gameplay
    for idx in range(3,72,7):
        x,z=center[idx];dx,dz=normals[idx];Y=4.48+1.47*idx/74+2.55*math.sin(idx/74*math.pi)
        for side in (-1,1):
            xx=x+dx*1.17*side;zz=z+dz*1.17*side
            post(s,'BiophilicRidgeLowNativePlant',xx,zz,Y+.15,Y+.42,.11,'ecoDeep')
    # brace from ground only at endpoints outside core corridor
    for x,z,top in [(-7.9,-7.85,4.25),(6.2,7.4,5.65)]:
        post(s,'LivingGreenSpineLoadBearing',x,z,.21,top-.15,.26,'ecoWood')
    for i in np.linspace(4,68,13,dtype=int):
        x,z=center[i]; Y=4.23+1.47*i/74+2.55*math.sin(i/74*math.pi)
        xp,zp=center[max(0,i-3)]
        beam(s,'GreenWaveUndersideTruss',(x,Y-.38,z),(xp,Y-.55,zp),.077,'ecoWood')
    # NE roof as topographic contour sloping away from inner courtyard, *not* flat green terrace.
    def canopy(x,z):return [x,5.6+.50*(z-4.4)/5.7+.42*math.sin((x-2.4)/9.2*math.pi),z]
    sloped_band(s,'NeighbourhoodEcoInhabitedEarthRoof',2.2,11.4,4.35,9.55,canopy,'ecoDeep',.40,21,15)
    # low ecosystem system for education, rain garden tucked away from four-way road intersection
    ellipse(s,'RainGardenLivingWetlandBase',-7.1,-10.35,2.35,1.0,.13,.33,'stone2')
    ellipse(s,'RainGardenLivingWetlandWater',-7.1,-10.35,2.08,.77,.34,.37,'ecoWater')
    for x,z in [(-10.6,10.8),(-11.8,8.5)]:
        if s._publicCorridor.distance(Point(x,z))>3.1:s.tree(x,z,.56,'olive')
    for x,z in [(-10.5,10.3),(11.0,-10.0)]:
        if s._publicCorridor.distance(Point(x,z))>2.8:garden(s,'RainGardenNativePlanting',x,z,2.4,1.15,'ecoDeep')

def structure_H(s):
    """「展頁探索」inhabited reading halls + broad paper-fold structural shell, clear glazed lobby.
    Lecture garden outside the south spine, no athletics track or clock tower.
    """
    WEST=[(-10.55,4.55),(-1.18,4.55),(-1.18,10.35),(-10.55,10.35)]
    EAST=[(-.18,4.55),(10.45,4.55),(10.45,10.25),(-.18,10.25)]
    for tag,foot in [('ReadingAndStoryWing',WEST),('DiscoverySTEAMWing',EAST)]:
        pr(s,tag+'_paving',foot,.18,.65,'stone2')
        pr(s,tag+'_twoLevelFloor',foot,3.15,3.42,'eduCream')
        skirt_glazing(s,tag+'_fullWindowFacade',foot,.69,6.65,'eduGlass','eduAmber','eduCream')
        pr(s,tag+'_roofEdge',foot,6.55,6.82,'eduBlue')
    # actual central double-height transparent library spine + sunlit clerestory
    AT=[(-1.9,3.95),(1.4,3.95),(1.4,10.4),(-1.9,10.4)]
    pr(s,'SpineAtriumAccessibleFloor',AT,.18,.67,'stone2')
    skirt_glazing(s,'BookSpineTranslucentCurtainWall',AT,.7,8.2,'eduGlass','eduAmber')
    pr(s,'SpineReadingSkylight',AT,8.2,8.52,'eduCream')
    # book-derived roof leaves are folded *occupied* steel-and-glulam shell supported by real pillars.
    for side in (-1,1):
        x0,x1=(-11.25,-.25) if side<0 else (-.25,11.25)
        def leaf(x,z):
            t=abs(x+.25)/11.4
            return [x,7.16+2.45*t**1.55+.34*math.sin((z-4.3)/6.5*math.pi),z]
        sloped_band(s,('Left' if side<0 else 'Right')+'GluLamReadingPage',x0,x1,4.05,10.5,leaf,'eduBlue' if side<0 else 'eduAmber',.36,27,16)
        for z in np.linspace(4.1,10.1,10):
            xx=x0 if side<0 else x1;Y=leaf(xx,z)[1]
            beam(s,'RealBookPageLoadRib',(-.25,7.05,z),(xx,Y-.13,z),.14,'eduCream')
            post(s,'ExternalReadingHallStructuralPier',xx,z,.22,Y-.2,.095,'eduAmber')
    # facades show actual reading & discovery activities through the large panes
    for x,z in [(-8.0,7),(-5.7,7.4),(-3.5,7.0),(4.0,7.2),(6.5,7.2)]:
        bx(s,'VisibleReadingCollectionPlinth',x,z,1.6,.55,.70,1.6,'eduAmber')
        bx(s,'VisibleBooksAndEducationMedia',x,z+.28,1.45,.22,1.6,2.67,'eduBlue' if x<0 else 'eduCoral')
    # Learning forum at south-west, away from main route which crosses z~0 then SE x~9
    for k in range(5):
        z=-5.2-k*.58
        bx(s,'TieredLearningAmphitheatre',-6.3,z,6.7-k*.40,.50,.20+k*.16,.35+k*.16,'paveLight')
        if k<4:bx(s,'AmphitheatreWoodWarmTread',-6.3,z,6.55-k*.40,.37,.35+k*.16,.42+k*.16,'eduAmber')
    # low book-shaped community learning signage on center-facing entry, outside curb
    for x,z in [(-12.45,8.0),(12.5,7.8)]:
        if s._publicCorridor.distance(Point(x,z))>2.7:s.tree(x,z,.55,'pink')

def source_lines(code):
    cx,cz=NODES[code];out={}
    for e in road['allRoutesProposed']:
        if code not in (e['from'],e['to']):continue
        P=np.asarray(e['proposedControlPointsXZ'],float)
        t=np.linspace(0,1,400)[:,None]
        if len(P)==4:Q=(1-t)**3*P[0]+3*(1-t)**2*t*P[1]+3*(1-t)*t**2*P[2]+t**3*P[3]
        else:Q=(1-t)*P[0]+t*P[-1]
        out[e['id']]=LineString(Q-np.array([cx,cz]))
    return out

def bridge_approach(s):
    routes=source_lines(s.code)
    site=scale(Point(0,0).buffer(1,resolution=160),s.rx*.96,s.rz*.96)
    # B's four original radial Bezier branches all ended at the old central island node.
    # In the enlarged civic courtyard they are instead connected along north/east inner island
    # to avoid cutting through the occupied care garden. Gate points remain sourced from the
    # same original curves, and this is ONLY a candidate inner-island retargeting.
    if s.code=='B':
        fixed=scale(Point(0,0).buffer(1,resolution=160),s.rx*.96,s.rz*.96)
        gates={}
        for name,line in routes.items():
            q=line.intersection(fixed.boundary)
            pp=list(q.geoms) if hasattr(q,'geoms') else [q]
            pp=[v for v in pp if v.geom_type=='Point']
            if pp:
                gates[name]=max(pp,key=lambda q:math.hypot(q.x,q.y))
        # 4 continuous genuine public portals, with three grounded connector joints.
        walk=[('S13',(-8.9,7.1),(-3.0,7.6),(4.7,7.0),'S14'),
              ((4.7,7.0),(9.0,4.2),(10.0,-.4),'S08'),
              ((10.0,-.4),(10.5,-4.0),'S12')]
        rr=[]
        for sequence in walk:
            pts=[]
            for x in sequence:
                if isinstance(x,str):
                    if x not in gates:continue
                    pts.append((gates[x].x,gates[x].y))
                else:pts.append(x)
            if len(pts)>1:rr.append(LineString(pts))
        # extend all 4 island bridge mouths to the true terrain shoreline
        for pt in gates.values():
            a=np.array([pt.x,pt.y]); b=a*1.047
            rr.append(LineString([tuple(a),tuple(b)]))
        centerline=unary_union(rr)
        s._innerRoutesRevised=True
    else:
        centerline=unary_union(list(routes.values()))
    corridor=centerline.buffer(2.4,join_style=1,cap_style=1,resolution=12).intersection(site)
    s._publicCorridor=corridor
    s._routeStrings=list(routes.values())
    s._extRoutes=routes
    # actual 4.8 wide real-road source polygons as low ground tris, NOT generic art ring.
    geoms=[corridor] if corridor.geom_type=='Polygon' else [x for x in corridor.geoms if x.geom_type=='Polygon']
    for a in geoms:
        ts=[q for q in triangulate(a) if a.covers(q.representative_point()) and abs(q.area-a.intersection(q).area)<1e-4]
        V=[];F=[]
        for q in ts:
            pts=list(q.exterior.coords)[:3];at=len(V);V.extend([[x,.145,z] for x,z in pts]);F.append([at,at+1,at+2])
        if V:s.add('Protected42_4p8CorridorGround',trimesh.Trimesh(vertices=np.array(V),faces=np.array(F),process=False),'paveLight')
    return corridor


def bounded_floating_island(s):
    """Terrain hard-bounded by the declared island W/H. No 1.06-radii surprise.
    Same X/Z and Y-up conventions as the game; full y=-8..0.075 rock volume.
    """
    N=144;ang=np.linspace(0,math.tau,N,endpoint=False)
    rad=np.minimum(0.999,.989+.0045*np.sin(3*ang+.6)+.004*np.sin(7*ang-.2))
    top=np.c_[s.rx*rad*np.cos(ang),s.rz*rad*np.sin(ang)]
    def ring(k,y):return np.c_[top[:,0]*k,np.full(N,y),top[:,1]*k]
    levels=[(1.0,.075),(.991,-.6),(.96,-1.45),(.81,-3.05),(.61,-5.60),(.37,-8.)]
    colors=['stone2','cliff3','cliff','cliff2','cliff_dark']
    for jj in range(len(levels)-1):
       aa=ring(*levels[jj]);bb=ring(*levels[jj+1]);V=np.r_[aa,bb];F=[]
       for k in range(N):m=(k+1)%N;F.extend([[k,m,N+m],[k,N+m,N+k]])
       s.add('FloatingRockFace',trimesh.Trimesh(vertices=V,faces=np.array(F),process=False),colors[jj])
    V=np.r_[ring(1.0,.075),[[0,.075,0]]];F=[[N,(i+1)%N,i] for i in range(N)]
    s.add('PlayableIslandTop',trimesh.Trimesh(vertices=V,faces=np.array(F),process=False),'grass')

def perimeter_fence(s):
    n=108;theta=np.linspace(0,math.tau,n,endpoint=False);safety=s._publicCorridor
    pts=[(s.rx*.975*math.cos(t),s.rz*.975*math.sin(t)) for t in theta]
    valid=[safety.distance(Point(x,z))>3.2 for x,z in pts]
    for i,(x,z) in enumerate(pts):
        k=(i+1)%n;xx,zz=pts[k]
        if not (valid[i] and valid[k]):continue
        s.girder('PerimeterSafetyGuardrail',(x,1.13,z),(xx,1.13,zz),.044,'metal',role=None)
        if i%3==0:s.post('PerimeterSafetyPost',x,z,.12,1.15,.052,'metal',role=None)

def record(s):
    site=scale(Point(0,0).buffer(1,resolution=192),s.rx*.97,s.rz*.97)
    inner=scale(Point(0,0).buffer(1,resolution=192),s.rx*.945,s.rz*.945)
    roadspace=s._publicCorridor
    failures=[];cautions=[];issues={}
    for name,m in s.building_parts:
        verts=m.vertices;Ylow=float(verts[:,1].min());Yhigh=float(verts[:,1].max())
        footprint=Polygon(verts[:,[0,2]]).convex_hull
        out=footprint.difference(site).area
        cross=footprint.intersection(roadspace).area
        if out>.08:failures.append({'name':name,'reason':'island_edge','area':round(out,3),'height':[round(Ylow,2),round(Yhigh,2)]})
        if cross>.10 and Ylow<3.35:failures.append({'name':name,'reason':'walkway_intrusion','area':round(cross,3),'height':[round(Ylow,2),round(Yhigh,2)]})
        if cross>.12 and Ylow>=3.35:
            # Large elevated roof can be lower at the endpoints outside the road; sample
            # actual mesh vertices that project into the 4.8-road footprint.
            Ys=[float(v[1]) for v in verts if roadspace.covers(Point(float(v[0]),float(v[2])))]
            onroad=min(Ys) if Ys else Ylow
            if onroad<5.0:cautions.append({'name':name,'reason':'overhead_clearance_under_5m','area':round(cross,2),'globalMin':round(Ylow,2),'onRoadMin':round(onroad,2)})
    # A 3x3 NPC target must be safe and outside architecture: place data only, no NPC mesh
    intended={'B':(-.7,-11.2),'D':(11.3,-5.25),'E':(-11.2,7.2),'H':(-6.3,-9.2)}[s.code]
    player=Point(*intended)
    npc_ok=site.contains(player.buffer(1.5)) and roadspace.distance(player)>1.5
    tri=sum(len(m.faces) for ms in s.meshes.values() for m in ms)
    issues={'code':s.code,'island_dimensions':SIZES[s.code],'node_center':NODES[s.code], 'external_route_ids':list(s._extRoutes),'number_of_expected_gates':len(s._extRoutes),'4p8_ground_corridor_connected_parts':len(roadspace.geoms) if hasattr(roadspace,'geoms') else 1,'geometry_parts':len(s.building_parts),'triangles':tri,'edge_and_low_route_errors':failures[:100], 'elevated_cautions':cautions[:40], 'npc_research_spot':intended,'npc_3x3_safe_from_outerroad':bool(npc_ok), 'scope':'Offline candidate; not game collision or player camera QA'}
    return issues

def export(s):
    scene=trimesh.Scene()
    translucent={'careGlass','civicGlass','mistglass','eduGlass','blueglass','glass2','darkglass','deepglass'}
    for mat,meshes in s.meshes.items():
        if not meshes:continue
        m=trimesh.util.concatenate(meshes)
        RG=r.base.rgb(C[mat]);a=168 if mat in translucent else 255
        if mat in translucent:
            m.visual=trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(baseColorFactor=[*RG,a],alphaMode='BLEND',roughnessFactor=.18,metallicFactor=.04,doubleSided=True))
        else:m.visual.face_colors=[*RG,255]
        scene.add_geometry(m,geom_name=mat)
    dest=ROOT/'models'/f'{s.code}_R21_policy_landmark.glb'
    dest.write_bytes(scene.export(file_type='glb'))
    res={'name':dest.name,'file_bytes':dest.stat().st_size, 'number_materials':len(scene.geometry),'sha256':__import__('hashlib').sha256(dest.read_bytes()).hexdigest()}
    return res

def render(s,view):
    import vtk
    ren=s.vtk_renderer();ren.GradientBackgroundOn();ren.SetBackground(.965,.978,.976);ren.SetBackground2(.86,.925,.947)
    actors=ren.GetActors();actors.InitTraversal()
    active_mats=[k for k,meshes in s.meshes.items() if meshes]
    for idx in range(actors.GetNumberOfItems()):
        actor=actors.GetNextActor()
        if actor:
            prop=actor.GetProperty();prop.SetAmbient(.57);prop.SetDiffuse(.54);prop.SetSpecular(.10)
            if idx<len(active_mats) and active_mats[idx] in {'careGlass','civicGlass','mistglass','eduGlass','blueglass','glass2','darkglass','deepglass'}:prop.SetOpacity(.66)
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(1100,850);win.SetMultiSamples(4);win.AddRenderer(ren)
    cam=ren.GetActiveCamera();cam.ParallelProjectionOn();cam.SetFocalPoint(0,1.4,0);cam.SetViewUp(0,1,0)
    coords={'hero':(36,30,-42),'front':(0,18,-60),'back':(0,18,60),'left':(-60,18,0),'right':(60,18,0),'top':(.01,90,.01),'player_entrance':(21,8,-21)}
    cam.SetPosition(*coords[view]);
    if view=='top':cam.SetViewUp(0,0,-1)
    cam.SetParallelScale(18.0 if view!='top' else 19.0)
    ren.ResetCameraClippingRange();win.Render()
    w2i=vtk.vtkWindowToImageFilter();w2i.SetInput(win);w2i.SetInputBufferTypeToRGB();w2i.ReadFrontBufferOff();w2i.Update()
    pth=ROOT/'renders'/f'{s.code}_{view}.png';writer=vtk.vtkPNGWriter();writer.SetFileName(str(pth));writer.SetInputConnection(w2i.GetOutputPort());writer.Write();win.Finalize();return pth



def remove_named_prefix(s,prefix):
    matches=set()
    for c,ms in s.meshes.items():
        matches.update(id(m) for n,m in s.building_parts if n.startswith(prefix))
    for col,ms in list(s.meshes.items()):s.meshes[col]=[m for m in ms if id(m) not in matches]
    s.building_parts=[(n,m) for n,m in s.building_parts if id(m) not in matches]


def ground_clear(s,x,z,r):
    region=scale(Point(0,0).buffer(1,resolution=96),s.rx*.90,s.rz*.90)
    here=Point(x,z).buffer(r,resolution=12)
    if not region.contains(here) or here.intersects(s._publicCorridor):return False
    for _,m in s.building_parts:
        if float(m.vertices[:,1].min())>=2.8:continue
        outline=Polygon(m.vertices[:,[0,2]]).convex_hull
        if outline.intersects(here):return False
    return True


def theme_finish(s):
    """Visible and functional architectural finishing — no generic scatter props."""
    c=s.code
    if c=='B':
        # Sun-oriented second-floor care verandas and timber louvered facade bands.
        cx,cz=-3.95,-3.90
        for angle in np.linspace(95,207,24):
            t=math.radians(angle)
            px=cx+7.7*math.cos(t);pz=cz+7.7*math.sin(t)
            qx=cx+8.05*math.cos(t);qz=cz+8.05*math.sin(t)
            beam(s,'B_CareVerandaShadedSunfin',(px,3.3,pz),(qx,5.7,qz),.059,'careLinen')
            if int(angle)%3==0:
                bx(s,'B_HumanScaleTimberShutter',px,pz,.2,.14,1.1,2.7,'careRoof')
        # Deep community portal cornice with contrasting sunshade under the two wings.
        for x in np.linspace(.55,3.1,11):
            beam(s,'B_CommunityPortalCrossBeams',(x,6.67,-7.7),(x,6.67,-4.5),.09,'careLinen')
        # A tall central flowering tree communicates season and healing; still below key roof ridge.
        s.tree(cx+.75,cz+.65,1.35,'pink')
        # Purposeful low herb and seating terraces adjacent to the care wing, never on road.
        for x,z,wx,wz in [(-10.9,-7.35,2.2,1.1),(-10.15,3.1,2.5,1.1),(-8.2,-11.1,1.9,1.1)]:
            if ground_clear(s,x,z,max(wx,wz)/2):garden(s,'B_HealthRestorationGardens',x,z,wx,wz,'careGarden')
        for x,z in [(-11.35,-2.8),(-9.9,3.0)]:
            if ground_clear(s,x,z,1.1):bench(s,'B_ConversationSeating',x,z,1.5)
        # Distinctive round low oak decking with central specimen tree, visible on top view.
        # All low additions keep the 4.8 city walkway untouched.
    elif c=='D':
        # Big diagonal transparent service spine receives a believable timber/bronze rib cage.
        for t in np.linspace(-6.2,6.0,14):
            x=t;z=t
            Y=6.2+3.75*(max(0,1-(abs(t)/7.5)**1.6))
            a=(x-1.09,Y-.31,z+1.09);b=(x+1.09,Y-.31,z-1.09)
            beam(s,'D_CivicCrossRoofGoldRib',a,b,.076,'civicGold')
            if abs(t)>5.1:
                # Transfer bearing loads from roof to each true public building.
                beam(s,'D_CivicDiagonalStrut',(x,Y-.5,z),(x*.90,Y-1.3,z*.90),.097,'civicSteel')
        # Façade relief: two-storey stone-and-glass civic loggias, not bare glass cubes.
        for t in np.linspace(3.4,11.1,12):
            post(s,'D_CivicNEOpenStoneLoggia',t,3.08,.70,6.5,.080,'civicStone')
        for t in np.linspace(-10.3,-3.1,12):
            post(s,'D_CivicSWOpenServiceLoggia',t,-9.9,.70,5.2,.077,'civicGold')
        # Real physical wayfinding screens integrated into the service wing facade.
        for xx,zz in [(6.3,3.22),(9.2,3.22)]:
            bx(s,'D_OnlineServiceModuleInset',xx,zz,1.6,.20,1.4,2.5,'civicSky')
            for k in range(5):
                bx(s,'D_PublicServiceModuleUI',xx-.55+k*.28,zz-.14,.17,.06,2.2,2.3,'civicLight')
        # Orderly courtyard and low planters in protected spare territory.
        for x,z in [(-10.8,7.6),(-10.9,11.5),(12.7,-8.4)]:
            if ground_clear(s,x,z,1.6):s.tree(x,z,.58,'olive')
        for x,z in [(-12.0,5.6),(12.7,-6.5)]:
            if ground_clear(s,x,z,1.0):garden(s,'D_OrganisedCivicGarden',x,z,1.8,.9,'ecoLeaf')
    elif c=='E':
        # Replace one generic glass box with a genuinely open low-carbon learning terrace:
        # roof, columns, landscape wetland — one enclosed building remains at the other end.
        remove_named_prefix(s,'RainGardenLearningStation_')
        low=[(-10.45,-10.35),(-3.85,-10.35),(-3.85,-6.62),(-10.45,-6.62)]
        pr(s,'E_OpenBioswaleForumFoundation',low,.15,.42,'stone2')
        for xx in (-9.9,-7.45,-4.55):
            for zz in (-9.9,-7.0):
                post(s,'E_OpenTimberCommunityVeranda',xx,zz,.39,3.95,.18,'ecoWood')
        def ecoawning(x,z):
            return [x,4.15+.45*math.sin((x+10.4)/6.8*math.pi)+.22*(z+10.3)/3.8,z]
        sloped_band(s,'E_NativeGreenTimberForumRoof',-10.75,-3.65,-10.6,-6.5,ecoawning,'ecoLeaf',.33,20,12)
        for zz in np.linspace(-9.9,-7.05,7):
            beam(s,'E_EcologyForumWoodRafter',(-10.1,3.97,zz),(-4.2,3.97,zz),.09,'ecoWood')
        # Irrigation demonstration beds grouped in only safe corners, not random grass patches.
        for x,z in [(-12.2,-8.5),(-9.9,10.5),(11.6,-9.1)]:
            if ground_clear(s,x,z,1.25):garden(s,'E_SoilWaterCycleDemonstration',x,z,2.25,1.0,'ecoDeep')
        # Green vein cross-section: discrete continuous planter terraces directly anchored to roof.
        for xx in np.linspace(3,10.9,12):
            zz=9.5
            yy=5.6+.5*(zz-4.4)/5.7+.42*math.sin((xx-2.4)/9.2*math.pi)
            bx(s,'E_NativeGreenRoofBioStrip',xx,zz,.42,.60,yy+.10,yy+.24,'ecoLight')
        # Distinct wave-section downpipes / timber panels clearly show that water reuse is functional.
        for x,z in [(3.1,4.55),(7.4,4.55),(10.85,8.15)]:
            post(s,'E_VisibleRainwaterRecoverySpout',x,z,1.0,5.6,.055,'ecoWater')
    elif c=='H':
        # Transparent glazed reading atrium on which both full book roof leaves actually bear.
        for z in np.linspace(4.35,10.05,14):
            beam(s,'H_OpenBookAtriumWoodRibs',(-1.78,8.38,z),(1.20,8.38,z),.073,'eduAmber')
        # Facade terraces, human-scale outside learning gallery.
        for xx in np.linspace(-10.1,9.9,20):
            if abs(xx)<1.6:continue
            post(s,'H_OutdoorLibraryRealPiers',xx,4.42,.20,6.5,.088,'eduCream')
        # Three STEAM exhibition objects: low geometric displays under glazed building wings.
        for x,z in [(3.2,6.75),(5.4,7.0),(7.35,7.5)]:
            bx(s,'H_VisibleSteamLearningTable',x,z,1.12,.75,.72,1.15,'eduCream')
            bx(s,'H_VisibleSteamBookOrPrototype',x,z,.53,.47,1.15,1.47,'eduCoral')
        # actual reading amphitheatre out front, with benches and trees as organized small garden.
        for xx,zz in [(-12,8.0),(12.1,8.0),(-11.9,-5.3)]:
            if ground_clear(s,xx,zz,1.5):s.tree(xx,zz,.57,'olive')
        for xx,zz in [(-10.9,-8.8),(-9.9,-6.1)]:
            if ground_clear(s,xx,zz,.9):garden(s,'H_OutdoorLearningBotanicalBed',xx,zz,1.5,.8,'ecoLeaf')



def complete_public_realm(s):
    """Functional public spaces; only on terrain safe from current road and building collision.
    Positioned deliberately for each policy theme. Physically in GLB and renders.
    """
    landscapes={
      'B':{'trees':[(3.1,1.0,.63,'pink'),(5.4,-6.1,.61,'olive'),(5.6,-8.7,.57,'pink')],
           'gardens':[(3.2,-10.0,2.3,.90,'careGarden'),(5.0,-2.4,2.3,.85,'careGarden')],
           'seats':[(3.1,-7.1,1.4)]},
      'D':{'trees':[(-11.3,-.1,.68,'olive'),(-4.5,9.7,.62,'olive'),(10.9,-4.4,.58,'olive')],
           'gardens':[(-11.3,2.7,2.25,1.0,'ecoLeaf'),(-2.3,9.6,2.0,.9,'ecoLeaf')],
           'seats':[(-8.4,-1.2,1.8),(3.1,-8.9,1.6)]},
      'E':{'trees':[(-11.3,5.2,.64,'olive'),(-9.5,7.9,.63,'olive'),(-1.2,10.5,.58,'olive'),(1.3,-10.6,.59,'olive'),(11.9,-5.0,.55,'olive')],
           'gardens':[(-12.8,-3.8,2.15,1.12,'ecoDeep'),(-4.3,-11.5,2.25,.95,'ecoLeaf'),(1.1,10.6,2.35,.85,'ecoDeep'),(12,-5,2.0,.75,'ecoLeaf')],
           'seats':[(-10.8,4.7,1.3),(1.7,-8.7,1.5)]},
      'H':{'trees':[(-11.1,-5.3,.67,'olive'),(-6.4,-10.3,.61,'pink'),(3.6,-9.2,.59,'olive'),(12.0,-1.5,.57,'olive')],
           'gardens':[(-9.5,-4.8,2.2,.9,'ecoLeaf'),(2.0,-10.6,2.7,.85,'ecoLeaf'),(12.0,1.0,2.15,.95,'ecoLeaf')],
           'seats':[(-3.0,-8.5,1.7),(3.3,-7.2,1.5)]}
    }[s.code]
    for x,z,sz,kind in landscapes['trees']:
        if ground_clear(s,x,z,1.1*sz):s.tree(x,z,sz,kind)
    for x,z,w,d,col in landscapes['gardens']:
        if ground_clear(s,x,z,max(w,d)*.52):garden(s,'PolicyPublicLifeOrganisedFlowerbeds',x,z,w,d,col)
    for x,z,wx in landscapes['seats']:
        if ground_clear(s,x,z,wx*.52+.25):bench(s,'PolicyCommonsAccessibleSeat',x,z,wx)
    # Dedicate nonblocking grade flush markings to relevant public experience.
    if s.code=='B':
        # long life: two low stone rhythm paths, not a large target or park decoration.
        for x,z in [(4.9,-.5),(5.5,1.4),(6.0,-2.8)]:
            if s._publicCorridor.distance(Point(x,z))>0.3:
                s.box('AccessibleTherapyPathPaver',x,z,.32,.78,.150,.177,'bronze2')
    if s.code=='D':
        for x,z in [(-6.0,5.8),(-3.7,3.55),(-1.2,1.1),(1.7,-2.0),(4.5,-4.5)]:
            s.box('DigitalServicePathInlay',x,z,.32,.90,.146,.164,'civicGold')
    if s.code=='E':
        for x,z in [(-9.0,-.9),(-5.5,-.5),(-2.0,.3),(2.3,.30),(5.2,-.4),(9.5,-.2)]:
            s.box('SpongeCityBluePermeablePavingInlay',x,z,.36,.22,.148,.158,'ecoWater')
    if s.code=='H':
        for x,z in [(-9.6,-1.7),(-6.5,-1.9),(-3.0,-1.6),(.1,-2.1),(3.2,-3.1)]:
            s.box('LifelongLearningTrailColoredInlay',x,z,.53,.24,.149,.165,'eduCoral')
STRUCT={'B':structure_B,'D':structure_D,'E':structure_E,'H':structure_H}

def run():
    result={};out={}
    for code in 'BDEH':
        s=Design(code)
        bounded_floating_island(s)
        bridge_approach(s)
        STRUCT[code](s)
        theme_finish(s)
        complete_public_realm(s)
        perimeter_fence(s)
        aud=record(s);asset=export(s)
        print(code, 'faces',aud['triangles'],'errors',len(aud['edge_and_low_route_errors']),'cautions',len(aud['elevated_cautions']),'npc',aud['npc_3x3_safe_from_outerroad'],flush=True)
        for view in ('hero','front','back','left','right','top'):
            render(s,view)
        result[code]=aud;out[code]=asset
    (ROOT/'qa'/'geometry_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    (ROOT/'qa'/'assets.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
if __name__=='__main__':run()
