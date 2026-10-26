"""Second pass: authored playground, tree court and planted edges from reference.
Executed in the building script's shared geometry/material context. MIT.
"""
G.collection('40_PLAYGROUND');play=G.empty('Playground',model);play['role']='play'
px,py=CFG['playhouse'];house=G.empty('PlayhouseAndPlatform',play)
# Poured-rubber, genuinely thick organic areas with independent colour patches.
def blob(name,x,y,rx,ry,z,mat,parent,phase=0):
    pts=[]
    for i in range(96):
        a=i*math.tau/96;r=1+.045*math.sin(a*3+phase)+.035*math.cos(a*5+phase)
        pts.append((x+rx*r*math.cos(a),y+ry*r*math.sin(a)))
    return G.prism_xy(name,pts,z,.035,M[mat],parent)
matroot=G.empty('SoftPlaySurface',play)
blob('SoftPlaySage',-4.1,-3.3,3.25,1.75,.038,'rubber',matroot)
blob('SoftPlayOchre',-2.65,-2.5,1.5,.88,.077,'rubberOchre',matroot,.4)
blob('SoftPlayBlue',-4.6,-4.1,1.7,.85,.078,'rubberBlue',matroot,.8)
for x in [px-.61,px+.61]:
    for y in [py-.53,py+.53]:bx('PlayhouseOakPost',(x,y,1.10),(.09,.09,2.18),'wood',house,r=.015)
for i in range(7):bx('PlayhouseDeckBoard',(px-.56+i*.185,py,.88),(.17,1.12,.09),'woodLight',house,r=.012)
# Solid small pitched roof, front/back and soffit finished.
roofpoints=[(px-.82,2.07),(px,2.61),(px+.82,2.07),(px+.82,1.94),(px,2.46),(px-.82,1.94)]
G.prism_xz('PlayhouseGableRoof',roofpoints,py,1.48,M['roof'],house)
for i in range(7):
    x=px-.74+i*.247;z=2.61-abs(x-px)*.66+.012;bm('PlayhouseRoofSeam',(x,py-.74,z),(x,py+.74,z),.018,'seam',house)
# Ladder, doorway and rail panels with real circular openings.
for x in [px-.62,px-.30]:bm('PlayLadderSide',(x,py+.55,.12),(x,py+.55,1.24),.06,'wood',house)
for z in [.26,.48,.7,.92]:bx('PlayLadderRung',(px-.46,py+.57,z),(.38,.06,.045),'woodLight',house,r=.012)

def hole_panel(name,x,y,z,width,height,yaw,parent):
    n=32;verts=[];hw=width/2;hh=height/2;hole=min(width,height)*.27
    for depth in [-.025,.025]:
        for radius in ['outer','inner']:
            for j in range(n):
                a=j*math.tau/n;c,s=math.cos(a),math.sin(a);r=min(hw/max(abs(c),1e-8),hh/max(abs(s),1e-8))if radius=='outer'else hole
                xx=r*c;zz=r*s;verts.append((x+xx*math.cos(yaw)-depth*math.sin(yaw),y+xx*math.sin(yaw)+depth*math.cos(yaw),z+zz))
    faces=[]
    for j in range(n):
        k=(j+1)%n;faces.extend([(j,k,n+k,n+j),(2*n+j,3*n+j,3*n+k,2*n+k),(j,2*n+j,2*n+k,k),(n+j,n+k,3*n+k,3*n+j)])
    o=G.mesh(name,verts,faces,M['tealCloth'],parent);G.bevel(o,.012,2);return o
for side in [-1,1]:
    hole_panel('PlayhouseWindowPanel',px+side*.61,py,1.28,.85,.52,math.pi/2,house)
bridge=G.empty('LowPlayBridge',play)
for i in range(9):
    t=i/8;x=px+.6+t*1.65;y=py+.02-.32*t;z=.87-.50*t
    bx('PlayBridgeBoard',(x,y,z),(.18,.78,.07),'woodLight',bridge,r=.012)
for side in [-1,1]:
    for i in range(4):
        t=i/3;x=px+.68+1.5*t;y=py+side*.44-.32*t;z=.93-.50*t
        bx('PlayBridgePost',(x,y,z),(.065,.065,1.05),'wood',bridge,r=.015)
        if i<3:hole_panel('PlayBridgeCirclePanel',x+.24,y-.05,z+.1,.48,.45,-.20,bridge)
# Lofted, closed U-section slide; underside and side-wall thickness are real.
slide=G.empty('CurvedSlide',play);sections=48;cross=[(-.43,.18),(-.36,.18),(-.36,.025),(.36,.025),(.36,.18),(.43,.18),(.43,-.04),(-.43,-.04)];verts=[]
for i in range(sections+1):
    t=i/sections;y=py-.57-1.4*t;z=.14+.78*(1-t)**2;flare=1+.12*t**4
    verts.extend((px+.6*t**1.5+dx*flare,y,z+dz)for dx,dz in cross)
faces=[];k=len(cross)
for i in range(sections):
    for j in range(k):a=i*k+j;b=i*k+(j+1)%k;faces.append((a,a+k,b+k,b))
faces.extend([tuple(range(k)),tuple(reversed([sections*k+j for j in range(k)]))])
G.mesh('ClosedCurvedYellowChute',verts,faces,M['slide'],slide,True)
for side in [-1,1]:G.tube('SlideRolledSafetyRim',[(px+.6*(i/48)**1.5+side*.40*(1+.12*(i/48)**4),py-.57-1.4*i/48,.32+.78*(1-i/48)**2)for i in range(49)],.025,M['slide'],slide,8)
house.scale.z=.85;bridge.scale.z=.85;slide.scale.z=.85
# Recessed sand, closed oval rim and actual toys.
sandbox=G.empty('SandPlayAndToys',play);sx,sy=CFG['sandbox']
o=G.ring('OvalSandboxCurb',(0,0),1.30,1.43,.07,.11,M['woodLight'],sandbox,96);o.location=(sx,sy,0);o.scale.x=1.12;o.scale.y=.85
sand=G.cylinder('SandSurface',(sx,sy,.095),1.30,.045,M['sand'],sandbox,96);sand.scale.x=1.12;sand.scale.y=.85
for x,y,z,r in [(sx+.45,sy-.22,.30,.16),(sx+.88,sy-.05,.42,.18),(sx+.87,sy+.43,.32,.16)]:
    G.cylinder('SteppingStump',(x,y,z/2+.13),r,z,M['wood'],sandbox,24)
    G.ring('StumpGrowthRing',(x,y),r*.45,r*.48,z+.1303,.0006,M['woodDark'],sandbox,32)
# Bucket is open at the top; its wall and bottom are independently visible.
G.ring('OpenToyBucket',(sx-.62,sy-.20),.10,.135,.13,.22,M['coral'],sandbox,32)
G.cylinder('BucketBottom',(sx-.62,sy-.20,.135),.11,.025,M['coral'],sandbox,32)
G.tube('BucketHandle',[(sx-.62+.13*math.cos(t),sy-.20,.34+.13*math.sin(t))for t in [i*math.pi/24 for i in range(25)]],.009,M['woodLight'],sandbox,6)
spade=G.empty('SandSpade',sandbox);bm('SpadeHandle',(sx-.31,sy+.03,.14),(sx-.14,sy+.15,.55),.025,'wood',spade)
o=bx('SpadeBlade',(sx-.34,sy+.02,.145),(.14,.18,.035),'coral',spade,r=.04);o.rotation_euler.z=-.4

# Purposefully planted edges, tree canopies and the courtyard ring.
G.collection('50_LANDSCAPE');land=G.empty('Landscape',model);land['role']='landscape'
def join_children(root,name):
    objs=[o for o in root.children_recursive if o.type=='MESH']
    if not objs:return
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:o.select_set(True)
    objs[0].data=objs[0].data.copy() # Joining must never mutate the cached reusable leaf mesh.
    bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();objs[0].name=name

def bush(name,x,y,z,r,parent,flowers=True):
    root=G.empty(name,parent)
    for i in range(6):
        a=i*math.tau/6;G.sphere(name+'_LeafMass',(x+.40*r*math.cos(a),y+.40*r*math.sin(a),z+r*.30),(r*.56,r*.53,r*.52),M[['leaf','leafLight','leafDark'][i%3]],root,2)
    if flowers:
        for i in range(12):
            a=i*2.39996;rr=r*.72*math.sqrt((i+.5)/12);xx=x+rr*math.cos(a);yy=y+rr*math.sin(a);zz=z+r*.90+.025*math.sin(a*2)
            for j in range(5):
                p=j*math.tau/5;o=G.sphere('FlowerPetal',(xx+.030*math.cos(p),yy+.030*math.sin(p),zz),(.028,.021,.016),M['petalPink'if i%4==0 else'petal'],root,1);o.rotation_euler.z=p
            G.sphere('FlowerCentre',(xx,yy,zz+.02),(.018,.018,.014),M['slide'],root,1)
    join_children(root,name+'_EditableFloweringShrub');return root

def planter(name,x,y,w,d,h=.42,parent=land,flowers=True):
    root=G.empty(name,parent)
    bx(name+'_Bottom',(x,y,.09),(w,d,.16),'cream',root,r=.055)
    for side in [-1,1]:
        bx(name+'_LongRim',(x,y+side*(d/2-.055),h/2+.08),(w,.11,h),'cream',root,r=.035)
        bx(name+'_ShortRim',(x+side*(w/2-.055),y,h/2+.08),(.11,d,h),'cream',root,r=.035)
    bx(name+'_Soil',(x,y,h-.03),(w-.18,d-.18,.07),'soil',root,r=.015)
    for i in range(max(1,round(w/.5))):bush(name+'_Plant',x-w*.33+i*w*.66/max(1,round(w/.5)-1),y,h,.28,root,flowers)
    return root

def pot(name,x,y,parent=land):
    root=G.empty(name,parent);o=G.cylinder('PlanterBody',(x,y,.22),.20,.40,M['woodLight'],root,32,r2=.28)
    G.ring('PotLip',(x,y),.23,.29,.39,.07,M['wood'],root,48);G.cylinder('PotSoil',(x,y,.405),.235,.025,M['soil'],root,32)
    for i in range(9):
        a=i*math.tau/9;p=(x+.16*math.cos(a),y+.16*math.sin(a),.75+.10*math.sin(a*2));bm('PlantStem',(x,y,.43),p,.012,'leafDark',root)
        o=G.sphere('FernLeaf',p,(.105,.045,.25),M[['leafDark','leaf'][i%2]],root,2);o.rotation_euler=(.65*math.cos(a),.65*math.sin(a),a)
    return root
planter('WindowGarden',-4.1,.92,3.55,.56,.42)
planter('EntryFlowerBed',3.65,-.10,1.85,.85,.40)
planter('PlaygroundFlowerBorder',-3.5,-5.65,2.55,.70,.40)
planter('SouthwestCornerFlowers',-6.55,-4.78,1.0,.78,.38)
planter('SoutheastTreeFlowers',8.1,.1,1.15,1.0,.38)
planter('ForecourtRimFlowers',2.33,-7.225,1.20,.78,.35)
planter('RearGardenA',-3.7,6.35,2.5,.66,.42)
planter('RearGardenB',1.4,6.6,2.0,.66,.42)
for x,y in [(-1.25,.25),(2.90,.10),(-5.95,1.08),(5.00,1.05)]:pot('DoorwayFern',x,y)
# White ring planter with real planting and two separate curved seating arcs.
tx,ty=CFG['treeCourt'];court=G.empty('TreeCourtPlanter',land)
G.ring('CircularTreeBedWall',(tx,ty),1.29,1.47,.035,.43,M['cream'],court,128)
G.cylinder('TreeCourtSoil',(tx,ty,.28),1.29,.1,M['soil'],court,96)
for i in range(11):
    a=i*math.tau/11;bush('TreeCourtFlowers',tx+1.03*math.cos(a),ty+1.03*math.sin(a),.42,.30,court,True)
for num,(a,b)in enumerate([(math.radians(130),math.radians(285)),(math.radians(5),math.radians(80))]):
    bench=G.empty('CurvedTreeBench_'+str(num),land)
    for j in range(4):G.ring('CurvedTimberSeatSlat',(tx,ty),1.54+j*.105,1.63+j*.105,.47,.065,M['woodLight'],bench,64,start=a,end=b)
    for t in [a+(b-a)*j/4 for j in range(5)]:
        for r in [1.60,1.88]:bx('BenchMetalSupport',(tx+r*math.cos(t),ty+r*math.sin(t),.25),(.075,.075,.43),'rail',bench,r=.015)
# Faceted multi-crown trees, with deliberate branch structure.
for index,(x,y,height,rad)in enumerate(CFG['trees']):
    tree=G.empty('Tree_'+str(index),land);tree.location.z=.25 if index==3 else 0;spec=[(0,0,.84,1),(-.52,.05,.71,.78),(.55,.10,.74,.83),(.06,-.43,.69,.81),(.05,.35,.76,.84),(0,0,.99,.70)];factor=height/max(height*dz+rad*size*.85 for _,_,dz,size in spec);trunk=height*.57*factor
    G.cylinder('TaperedTreeTrunk',(x,y,trunk/2+.15),.13,trunk,M['woodDark'],tree,12,r2=.085)
    for j in range(4):
        a=j*math.tau/4+.35;end=(x+.44*rad*math.cos(a),y+.44*rad*math.sin(a),height*.78*factor)
        bm('TreeBranch',(x,y,trunk*.72),end,.085,'woodDark',tree)
    for j,(dx,dy,dz,size)in enumerate(spec):
        G.sphere('FacetedCrown',(x+dx*rad,y+dy*rad,height*dz*factor),(rad*size,rad*size*.92,rad*size*.85*factor),M[['leaf','leafLight','leafDark','leaf','leafLight','leafLight'][j]],tree,2)
    if index not in [2,3]:
        G.ring('SmallTreeWell',(x,y),.44,.62,.03,.14,M['cream'],tree,64);G.cylinder('TreeWellSoil',(x,y,.08),.44,.05,M['soil'],tree,48)
# Daylight lanterns: closed glass shell, trim, roof and proper bases.
G.collection('60_SITE_FURNITURE');street=G.empty('StreetFurniture',model);street['role']='furniture'
for x,y in [(-8.1,-1.8),(7.2,-2.0)]:
    lamp=G.empty('CourtyardLantern',street)
    G.cylinder('LanternBase',(x,y,.09),.13,.16,M['rail'],lamp,24)
    G.cylinder('LanternPole',(x,y,1.25),.038,2.35,M['rail'],lamp,16)
    bx('LanternGlassBody',(x,y,2.49),(.25,.25,.40),'trim',lamp,r=.02)
    for dx in [-.13,.13]:
        for dy in [-.13,.13]:bx('LanternFrame',(x+dx,y+dy,2.49),(.025,.025,.43),'rail',lamp,r=.007)
    bx('LanternCap',(x,y,2.72),(.34,.34,.07),'roof',lamp,r=.025)
    bx('LanternLowerRail',(x,y,2.27),(.30,.30,.06),'rail',lamp,r=.015)
board=G.empty('ChildrenActivityBoard',street)
bx('ActivityBoardPanel',(5.70,.78,.77),(1.05,.07,.67),'leafDark',board,r=.025)
for x in [5.14,6.26]:bx('ActivityBoardPost',(x,.78,.57),(.07,.09,1.13),'wood',board,r=.015)
for z in [.42,1.13]:bx('ActivityBoardTimber',(5.70,.78,z),(1.19,.09,.07),'woodLight',board,r=.012)
for j in range(3):
    x=5.36+j*.34;mat=M[['cream','woodLight','coral'][j]]
    G.sphere('ActivityHandPalm',(x,.72,.73),(.060,.018,.075),mat,board,2)
    for finger in range(4):G.sphere('ActivityHandFinger',(x-.055+finger*.036,.72,.84+(.02 if finger in [1,2]else 0)),(.015,.018,.045),mat,board,2)
    G.sphere('ActivityHandThumb',(x+.076,.72,.76),(.033,.018,.021),mat,board,2)
