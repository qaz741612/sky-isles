"""Standalone Blender reconstruction from the user's supplied image. MIT.
No game map, model, policy, camera or navigation source is changed.
Run: blender -b -t 2 --python scripts/blender/build_parent_child.py -- --phase architecture
"""
import bpy, math, sys, json, os, random, argparse
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import parent_child_geometry as G
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/design/parent-child-blender-model-v1'
CFG=json.loads((OUT/'layout.json').read_text())
args=argparse.ArgumentParser();args.add_argument('--phase',default='complete');args.add_argument('--samples',type=int,default=96);args.add_argument('--width',type=int,default=1600);args.add_argument('--render',default='hero');args=args.parse_args(sys.argv[sys.argv.index('--')+1:] if '--'in sys.argv else [])
random.seed(741612)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name=='Collection':bpy.data.collections.remove(c)
G.collection('00_MODEL_ROOT');model=G.empty('ParentChildCentre_MODEL');model['design_basis']='User supplied architectural reference, 2026-10-26';model['status']='Artwork for manual review; not integrated into game';model['units']='metres of modelling scale, not engineering approval'
M={}
for key,h,rough,metal in [('cream','EADFC9',.68,0),('stone','DEDACF',.79,0),('trim','F4E8CE',.6,0),('roof','66999B',.4,.12),('seam','4B8894',.44,.15),('wood','C69B60',.55,0),('woodLight','DEBA7F',.58,0),('woodDark','91683F',.65,0),('rail','3F8083',.43,.28),('leaf','93AF62',.86,0),('leafLight','B5CA7D',.86,0),('leafDark','708F48',.9,0),('soil','6A6144',1,0),('sand','E8CF9B',.94,0),('rubber','B7CBB5',.9,0),('rubberBlue','9EBCC3',.9,0),('rubberOchre','E8D28E',.9,0),('coral','DF9E7D',.64,0),('slide','E7BF6B',.42,0),('petal','F8F1DB',.76,0),('petalPink','DDAAA2',.76,0),('greenCloth','AEC1A5',.8,0),('tealCloth','7BA4A1',.8,0),('floor','DED4BF',.7,0),('gray','ACAFAC',.92,0)]:M[key]=G.material(key,h,rough,metal)
M['glass']=G.material('Clear warm architectural glazing','D8E6DA',.14,0,.82)
G.collection('10_ARCHITECTURE');arch=G.empty('Architecture',model);arch['role']='building'

def bx(name,p,d,mat='cream',parent=arch,r=.025):return G.box(name,p,d,M[mat],parent,r)
def bm(name,a,b,w=.07,mat='wood',parent=arch):return G.beam(name,a,b,w,M[mat],parent)
def roof_set(name,p,parent):
    G.roof(name,**p,thickness=.16,mats=[M['roof'],M['cream'],M['trim']],parent=parent)
    span=p['x1']-p['x0'];f=lambda x:G.profile(x,p['x0'],p['x1'],p['left'],p['right'],p['rise'])
    for i in range(1,round(span/.43)):
        x=p['x0']+span*i/round(span/.43);bm(name+'_StandingSeam', (x,p['y0']+.03,f(x)+.012),(x,p['y1']-.03,f(x)+.012),.025,'seam',parent)
    for y in [p['y0']+.035,p['y1']-.035]:
        G.tube(name+'_RolledEave',[(p['x0']+span*i/96,y,f(p['x0']+span*i/96)-.02)for i in range(97)],.026,M['roof'],parent,8)
    for y in [p['y0']+.035,(p['y0']+p['y1'])/2,p['y1']-.035]:
        G.tube(name+'_PanelJoint',[(p['x0']+span*i/96,y,f(p['x0']+span*i/96)+.006)for i in range(97)],.008,M['seam'],parent,6)
    for i in range(1,7):
        x=p['x0']+span*i/7;bm(name+'_SoffitRafter',(x,p['y0']+.08,f(x)-.19),(x,p['y1']-.08,f(x)-.19),.07,'woodLight',parent)
    return f

def front_glass(name,x0,x1,y,z0,z1,parent,door=None):
    n=max(2,round((x1-x0)/.82));step=(x1-x0)/n
    bases=[(x0,x1)] if not door else [(x0,door[0]),(door[1],x1)]
    for a,b in bases:bx(name+'_Sill',((a+b)/2,y,.24),(b-a,.18,.26),'cream',parent)
    for i in range(n):
        a=x0+i*step;b=a+step;segments=[(a,b)]
        if door:segments=[(a,min(b,door[0])),(max(a,door[1]),b)]
        for aa,bb in segments:
            if bb-aa>.08:bx(name+'_Pane',((aa+bb)/2,y,(z0+z1)/2),(bb-aa-.06,.038,z1-z0),'glass',parent,r=.006)
    for i in range(n+1):
        x=x0+i*step
        if not(door and door[0]<x<door[1]):bx(name+'_Mullion',(x,y-.018,(z0+z1)/2),(.085,.10,z1-z0+.1),'woodLight',parent,r=.009)
    for z in [z0,z1]:
        for a,b in (bases if z==z0 else [(x0,x1)]):bx(name+'_Transom',((a+b)/2,y-.018,z),(b-a+.08,.11,.085),'wood',parent,r=.009)

def doors(name,x,y,parent,width=1.6):
    for side in [-1,1]:
        xx=x+side*width/4
        bx(name+'_DoorGlass',(xx,y,1.32),(width/2-.09,.045,2.2),'glass',parent,r=.005)
        for z in [.2,2.43]:bx(name+'_DoorRail',(xx,y-.035,z),(width/2,.11,.09),'wood',parent,r=.01)
        for dx in [-width/4,width/4]:bx(name+'_DoorStile',(xx+dx,y-.035,1.32),(.075,.11,2.31),'woodLight',parent,r=.012)
        bm(name+'_Handle',(x+side*.12,y-.12,1.05),(x+side*.12,y-.12,1.40),.025,'woodDark',parent)
    bx(name+'_Threshold',(x,y-.06,.1),(width+.18,.38,.18),'trim',parent)

def side_windows(name,x,y0,y1,top,parent):
    n=max(2,round(y1-y0));step=(y1-y0)/n
    bx(name+'_Base',(x,(y0+y1)/2,.29),(.20,y1-y0,.42),'cream',parent)
    for i in range(n):
        y=y0+(i+.5)*step;bx(name+'_Glazing',(x,y,(top+.55)/2),(.038,step-.12,top-.55),'glass',parent,r=.005)
    for i in range(n+1):bx(name+'_Post',(x,y0+i*step,(top+.43)/2),(.14,.11,top-.33),'woodLight',parent,r=.012)
    for z in [.5,top]:bx(name+'_Frame',(x,(y0+y1)/2,z),(.14,y1-y0+.14,.09),'wood',parent)

main=G.empty('MainCurvedHall',arch);p=CFG['mainRoof'];f=roof_set('MainWaveRoof',p,main)
bx('MainFoundation',(1.45,3.12,.08),(6.05,4.54,.16),'cream',main)
bx('MainFloor',(1.45,3.12,.17),(5.8,4.28,.08),'floor',main)
for y in [1.0,5.25]:
    x0,x1=-1.35,4.32
    front_glass('MainFront'if y<2 else'MainRear',x0,x1,y,.42,2.7,main,door=(.3,1.9)if y<2 else None)
    for i in range(7):
        a=x0+(x1-x0)*i/7+.04;b=x0+(x1-x0)*(i+1)/7-.04
        G.arch_pane('MainClerestoryGlass',a,b,y,2.77,lambda x:f(x)-.23,M['glass'],main)
    for i in range(8):
        x=x0+(x1-x0)*i/7;top=f(x)-.19
        bx('MainUpperMullion',(x,y-.01,(top+2.74)/2),(.075,.1,top-2.74),'woodLight',main,r=.01)
    G.tube('MainCurvedHeader',[(x0+(x1-x0)*i/80,y-.045,f(x0+(x1-x0)*i/80)-.19)for i in range(81)],.06,M['woodLight'],main,8)
side_windows('EastHallSide',4.32,1.0,5.25,2.93,main)
for x in [-1.43,4.39]:
    for y in [1,5.25]:bx('CreamCornerPier',(x,y,1.55),(.21,.27,3.05),'cream',main)
doors('WelcomeEntry',1.1,.94,main)
bx('EntryOverdoorGlazing',(1.1,.94,2.58),(1.6,.038,.25),'glass',main,r=.005)
bx('EastHallRoofBearing',(4.32,3.125,3.06),(.19,4.25,.24),'cream',main)
bx('WestHallValleyReturn',(-1.43,1.72,3.40),(.18,1.45,.50),'cream',main)
# Open, fully constructed entrance canopy: timber beams, solid ceiling and columns.
entry=G.empty('EntryCanopy',arch)
bx('EntryCanopySolid',(1.1,-.06,2.82),(3.22,1.94,.22),'trim',entry,r=.045)
for i in range(14):bx('EntryCanopySoffitSlat',(-.37+i*.225,-.06,2.69),(.16,1.82,.035),'woodLight',entry,r=.009)
for x in [-.38,2.58]:
    for y in [-.94,.75]:bx('EntryTimberPost',(x,y,1.37),(.115,.115,2.7),'wood',entry,r=.018)
bx('EntranceStep',(1.1,.1,.065),(3.24,1.95,.12),'cream',entry,r=.04)
# Rounded, thick family emblem plaque, not people/NPC models.
outline=[(-.02,2.96),(2.22,2.96)]+[(1.1+1.12*math.cos(i*math.pi/48),2.96+1.12*math.sin(i*math.pi/48))for i in range(1,48)]
G.prism_xz('FamilyEmblem_StonePlaque',outline,-.35,.13,M['trim'],entry)
for name,x,z,size,mat in [('ParentCoral',.9,3.62,.14,'coral'),('ParentTeal',1.28,3.58,.13,'tealCloth'),('ChildWarm',1.14,3.34,.095,'woodLight')]:
    o=G.cylinder(name+'_Head',(x,-.435,z),size,.045,M[mat],entry,32);o.rotation_euler.x=math.pi/2
    G.sphere(name+'_Relief',(x,-.44,z-.26),(size*1.1,.035,size*1.55),M[mat],entry,3)
# Side trellis, authored to match the reference transition between entry and wing.
pergola=G.empty('WestEntryTimberTrellis',arch)
for x in [-2.2,-.62]:bx('PergolaPost',(x,.15,1.28),(.105,.105,2.52),'wood',pergola)
for i in range(9):
    x=-2.32+i*.22;bm('PergolaRafter',(x,-.05,2.57),(x,1.65,2.78),.09,'woodLight',pergola)
bm('PergolaFrontBeam',(-2.45,.03,2.48),(-.45,.03,2.48),.11,'wood',pergola)
# Left ground-floor wing and its raised curved daylight pavilion.
left=G.empty('LeftFamilyReadingWing',arch);w=CFG['leftWing']
bx('LeftWingFoundation',(-4.25,2.875,.085),(6.0,3.35,.17),'cream',left)
low={'x0':-7.5,'x1':-1.1,'y0':.92,'y1':4.7,'left':2.94,'right':3.23,'rise':.10};roof_set('LeftLowerCurvedRoof',low,left)
for y in [1.3,4.45]:front_glass('LeftWingWindows',-7.05,-1.42,y,.48,2.72,left)
side_windows('WestWingSide',-7.10,1.3,4.45,2.71,left)
loft=G.empty('UpperLeftDaylightLevel',arch);u=CFG['upperLeftRoof'];uf=roof_set('UpperLeftWaveRoof',u,loft)
bx('UpperLoftFloor',(-3.35,3.225,3.31),(4.32,1.61,.14),'cream',loft)
for y in [2.42,4.03]:
    x0,x1=-5.4,-1.24
    for i in range(6):
        a=x0+(x1-x0)*i/6+.045;b=x0+(x1-x0)*(i+1)/6-.045
        G.arch_pane('UpperLoftGlazing',a,b,y,3.42,lambda x:uf(x)-.22,M['glass'],loft)
    for i in range(7):
        x=x0+(x1-x0)*i/6;top=uf(x)-.19;bx('LoftOakMullion',(x,y-.04,(3.36+top)/2),(.085,.11,top-3.36),'woodLight',loft,r=.01)
    bx('LoftWindowSill',(-3.32,y,3.37),(4.3,.18,.12),'wood',loft)
for x in [-5.42,-1.23]:
    top=uf(x)-.16;bx('LoftSideWall',(x,3.225,(3.38+top)/2),(.14,1.61,top-3.38),'cream',loft)
# Right low wing, with complete glazed ends and a timber shaded entrance.
right=G.empty('RightCareWing',arch);rw=CFG['rightWing']
bx('RightWingFoundation',(5.69,3.02,.08),(3.0,3.38,.16),'cream',right)
rr={'x0':4.0,'x1':7.35,'y0':1.13,'y1':4.95,'left':2.97,'right':2.8,'rise':.11};roof_set('RightCurvedWingRoof',rr,right)
for y in [1.55,4.65]:front_glass('CareWingGlass',4.45,6.99,y,.4,2.6,right)
side_windows('CareWingEastSide',7.0,1.55,4.65,2.6,right)
for x in [4.67,5.25,5.83,6.41,6.99]:bm('RightShadeRafter',(x,.97,2.55),(x,2.05,2.66),.085,'woodLight',right)
for x in [4.62,6.99]:bx('RightPorchPost',(x,1.03,1.29),(.105,.105,2.55),'wood',right)
# Visible indoor furniture; each item remains independently editable.
print('Architecture shells complete',flush=True)
G.collection('20_INTERIOR');interior=G.empty('InteriorFurniture',model);interior['role']='interior'
def shelf(name,x,y,width=1.3,base=.2,parent=interior,height=1.5):
    bx(name+'_Back',(x,y+.15,base+height/2),(width,.055,height),'cream',parent)
    for z in [base,base+height/3,base+height*2/3,base+height]:bx(name+'_Shelf',(x,y,z),(width,.38,.055),'woodLight',parent,r=.009)
    for xx in [x-width/2,x+width/2]:bx(name+'_Side',(xx,y,base+height/2),(.055,.38,height),'wood',parent,r=.009)
    for row in range(3):
        for i in range(7):bx(name+'_Book',(x-width*.4+i*width*.13,y-.035,base+.03+row*height/3+height*.11),(.10,.23,height*.20+(.025 if i%3 else 0)),['tealCloth','coral','cream','greenCloth'][i%4],parent,r=.008)
def table(name,x,y,radius=.56,z=.72,parent=interior,floor=.18):
    G.cylinder(name+'_Top',(x,y,z),radius,.075,M['woodLight'],parent,48)
    for a in [.6,2.7,4.8]:bm(name+'_Leg',(x+radius*.6*math.cos(a),y+radius*.6*math.sin(a),floor),(x+radius*.42*math.cos(a),y+radius*.42*math.sin(a),z),.055,'wood',parent)
def stool(name,x,y,z=.43,parent=interior,floor=.18):
    G.cylinder(name+'_Seat',(x,y,z),.23,.08,M['greenCloth'],parent,32)
    for a in [0,math.tau/3,2*math.tau/3]:bm(name+'_Leg',(x+.17*math.cos(a),y+.17*math.sin(a),floor),(x+.13*math.cos(a),y+.13*math.sin(a),z-.04),.04,'wood',parent)
for x in [-6.25,-4.70,-3.15,-1.85]:shelf('ReadingLibrary',x,4.10,1.3)
for x,y in [(-4.9,2.5),(-2.8,2.8),(5.8,2.9),(1.65,3.0)]:
    table('FamilyTable',x,y)
    for a in [0,2.1,4.2]:stool('FamilyStool',x+.83*math.cos(a),y+.83*math.sin(a))
shelf('MainHallLibrary',2.6,4.88,2.15)
shelf('CareWingStorage',5.8,4.30,1.45)
shelf('LoftReadingShelf',-3.6,3.72,2.8,3.4,height=.68)
for x in [-4.3,-2.5]:table('LoftTable',x,3.10,.32,3.91,floor=3.4);stool('LoftSeat',x,2.72,3.72,floor=3.4)
for x,y in [(-6.0,1.87),(3.35,3.55)]:
    bx('ReadingSofaBase',(x,y,.39),(1.25,.67,.24),'wood',interior,r=.07)
    bx('ReadingSofaCushion',(x,y,.57),(1.19,.63,.20),'greenCloth',interior,r=.09)
    bx('ReadingSofaBack',(x,y+.29,.87),(1.25,.16,.56),'greenCloth',interior,r=.07)
bx('ReceptionCounter',(-.56,2.40,.62),(1.30,.55,.9),'woodLight',interior,r=.12)
# Ceiling fixtures are geometry, not planar pictures of furnished interiors.
for x,y,z in [(-4.4,2.5,2.55),(1.6,2.9,3.7),(5.8,3.0,2.40)]:
    G.cylinder('PendantShade',(x,y,z),.20,.15,M['cream'],interior,32,r2=.12)
    bm('PendantStem',(x,y,z+.07),(x,y,z+.32),.015,'woodDark',interior)
# Curved solid infills close the low wings to their roof undersides.
for name,roofdata,x0,x1,ys in [('LeftWing',low,-7.1,-1.42,[1.3,4.45]),('CareWing',rr,4.45,6.99,[1.55,4.65])]:
    base=2.76 if name=='LeftWing' else 2.64
    outline=[(x0,base),(x1,base)]+[(x1+(x0-x1)*i/24,G.profile(x1+(x0-x1)*i/24,roofdata['x0'],roofdata['x1'],roofdata['left'],roofdata['right'],roofdata['rise'])-.15)for i in range(25)]
    for y in ys:G.prism_xz(name+'_ClosedFasciaInfill',outline,y,.12,M['cream'],arch)
bx('WestWingRoofBearing',(-7.10,2.875,2.80),(.18,3.15,.18),'cream',arch)
bx('CareEastRoofBearing',(7,3.1,2.72),(.18,3.1,.17),'cream',arch)

# Site, paving and the four reference-image bridge stubs: standalone artwork,
# not changes to the B-plan world or its routes.
print('Interior furniture complete',flush=True)
G.collection('30_SITE_AND_PAVING');site=G.empty('SiteAndBridgeStubs',model);site['role']='standalone reference plinth, exclude when fitting into the game'
R=CFG['siteRadius'];G.cylinder('ClosedCircularPlinth',(0,0,-.20),R,.40,M['stone'],site,128)
G.ring('PlinthUpperMoulding',(0,0),R-.10,R+.025,-.12,.155,M['cream'],site,128)
# Clip each physical paver to the circular boundary.
def clip(poly,a,b):
    out=[]
    def inside(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])>=-1e-7
    for p,q in zip(poly,poly[1:]+poly[:1]):
        ip,iq=inside(p),inside(q)
        if ip:out.append(p)
        if ip!=iq:
            dx,dy=q[0]-p[0],q[1]-p[1];ex,ey=b[0]-a[0],b[1]-a[1];den=dx*ey-dy*ex
            if abs(den)>1e-9:t=((a[0]-p[0])*ey-(a[1]-p[1])*ex)/den;out.append((p[0]+t*dx,p[1]+t*dy))
    return out
circle=[((R-.08)*math.cos(i*math.tau/64),(R-.08)*math.sin(i*math.tau/64))for i in range(64)]
tile_mats=[G.material('LimestonePaver_'+str(i),h,.81)for i,h in enumerate(['E1DCD0','E9E3D6','DED9CE','E5DFD2'])]
for row in range(-13,14):
    y=row*.70
    for col in range(-11,12):
        x=col*.90+(.45 if row%2 else 0)
        if x*x+y*y>(R+1)**2:continue
        if (-6.2<x<4.5 and 1.0<y<5.4)or(4.3<x<7.1 and 1.4<y<4.7):continue
        poly=[(x-.438,y-.338),(x+.438,y-.338),(x+.438,y+.338),(x-.438,y+.338)]
        for a,b in zip(circle,circle[1:]+circle[:1]):
            poly=clip(poly,a,b)
            if len(poly)<3:break
        if len(poly)>=3:
            o=G.prism_xy('IndividuallyEditablePaver',poly,.004,.026,tile_mats[(row+col)%4],site);G.bevel(o,.008,2)
bridges=[]
for i,d in enumerate(CFG['bridgeStubs']):
    a=math.radians(d['angle']);radial=Vector((math.cos(a),math.sin(a),0));tangent=Vector((-math.sin(a),math.cos(a),0));start=math.sqrt(R*R-(d['width']/2)**2)-.05;end=start+d['length'];centre=radial*((start+end)/2)
    o=bx('ReferenceBridgeStub_'+str(i),tuple(centre+Vector((0,0,-.14))),(end-start,d['width'],.28),'stone',site,r=.035);o.rotation_euler.z=a
    bridges.append((a,math.asin((d['width']/2+.10)/R)))
    for side in [-1,1]:
        for j in range(4):
            p=radial*(start+(end-start)*j/3)+tangent*(side*d['width']/2)
            bm('BridgeRailPost',tuple(p+Vector((0,0,.03))),tuple(p+Vector((0,0,1.02))),.048,'rail',site)
        for z in [.53,1.0]:
            bm('BridgeOpenHorizontalRail',tuple(radial*start+tangent*(side*d['width']/2)+Vector((0,0,z))),tuple(radial*end+tangent*(side*d['width']/2)+Vector((0,0,z))),.042,'rail',site)
# Rim rails stop at every actual gate; no rail runs through the bridge opening.
def open_angle(a):return any(abs((a-b+math.pi)%math.tau-math.pi)<half for b,half in bridges)
for i in range(192):
    a=i*math.tau/192;b=(i+1)*math.tau/192
    if open_angle((a+b)/2):continue
    for z in [.53,1.0]:G.tube('CurvedRimRail',[(R*math.cos(t),R*math.sin(t),z)for t in[a,b]],.022,M['rail'],site,8)
for i in range(48):
    a=i*math.tau/48
    if not open_angle(a):bm('RimPost',(R*math.cos(a),R*math.sin(a),.02),(R*math.cos(a),R*math.sin(a),1.02),.046,'rail',site)

# Components for the second pass: play, planted gardens and furniture.
print('Site and paving complete',flush=True)
if args.phase!='architecture':
    exec(compile((Path(__file__).parent/'parent_child_landscape.py').read_text(),str(Path(__file__).parent/'parent_child_landscape.py'),'exec'))

print('Landscape and play complete',flush=True)
G.collection('90_STUDIO_NOT_EXPORTED')
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=args.samples;scene.cycles.use_denoising=True;scene.cycles.adaptive_threshold=.025
scene.cycles.max_bounces=9;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=3;scene.cycles.transmission_bounces=6;scene.cycles.transparent_max_bounces=6
scene.cycles.caustics_reflective=False;scene.cycles.caustics_refractive=False
scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.resolution_x=args.width;scene.render.resolution_y=round(args.width*741/1082);scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8'
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.62,.66,.67,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.50
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.35
G.box('StudioGround',(0,0,-.49),(200,200,.12),M['gray'],None,r=0)
def light(name,pos,power,size,color,target):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);G.COL.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
light('LargeSoftbox',(-8,-10,15),1800,8,(1,.91,.78),(0,0,0))
light('CoolFill',(9,-1,11),850,7,(.82,.93,1),(0,1,1))
light('SoftRoofRim',(-2,8,12),1200,6,(1,.96,.87),(0,2,2))
for x,y,z in [(-3.9,3,2.5),(1.5,3.3,3.8),(5.7,3.2,2.3),(-3.4,3.2,4.35)]:light('WarmInterior',(x,y,z),100,1.3,(1,.76,.44),(x,y,.2))
cameras={
 'hero':G.camera('01_ReferenceHero',CFG['heroCamera']['position'],CFG['heroCamera']['target'],CFG['heroCamera']['orthoScale']),
 'front':G.camera('02_Front',(0,-28,8),(0,1,2.0),21),
 'back':G.camera('03_Back',(0,28,9),(0,1,2),21),
 'left':G.camera('04_Left',(-28,1,9),(0,1,2),21),
 'right':G.camera('05_Right',(28,1,9),(0,1,2),21),
 'top':G.camera('06_Top',(0,0,32),(0,0,0),26),
 'eaves':G.camera('07_SoffitDetail',(4.8,-1.8,1.6),(2.9,.6,3.6),None,24),
 'player':G.camera('08_PlayerHeight',(-.6,-6.8,1.65),(1.1,1.2,2.1),None,25)
}
cameras['top'].rotation_euler=(0,0,0)
scene.camera=cameras['hero']
# All original editable components and non-destructive edge radii remain in .blend.
OUT.mkdir(parents=True,exist_ok=True);(OUT/'renders').mkdir(exist_ok=True);bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'parent-child-centre.blend'),compress=True)
# .glb contains the artwork only, no studio backdrop, cameras or lights.
bpy.ops.object.select_all(action='DESELECT')
for o in [model,*model.children_recursive]:o.select_set(True)
bpy.context.view_layer.objects.active=model
import parent_child_export
web_report=parent_child_export.export_batched(model,OUT/'parent-child-centre.glb')
# Accurate evaluated-mesh counts, dimensions and source attribution.
deps=bpy.context.evaluated_depsgraph_get();report={'blenderVersion':bpy.app.version_string,'phase':args.phase,'renderEngine':'Cycles CPU','samples':args.samples,'referenceSource':'User image visible in conversation; no local original image file supplied','collections':{},'materials':[],'role':'Standalone modelling, NOT game integration','webExport':web_report}
points=[];triangles=0;issues=[]
for c in bpy.data.collections:
    if c.name.startswith('90_'):continue
    objects=[o for o in c.objects if o.type=='MESH'];tris=0
    for o in objects:
        e=o.evaluated_get(deps);m=e.to_mesh();m.calc_loop_triangles();tris+=len(m.loop_triangles);points.extend(tuple(o.matrix_world@v.co)for v in m.vertices);e.to_mesh_clear()
    report['collections'][c.name]={'objects':len(objects),'triangles':tris};triangles+=tris
if points:report['bounds']={'min':[min(p[i]for p in points)for i in range(3)],'max':[max(p[i]for p in points)for i in range(3)]};report['sizeXYZ']=[report['bounds']['max'][i]-report['bounds']['min'][i]for i in range(3)]
report['triangles']=triangles;report['meshObjects']=sum(c['objects']for c in report['collections'].values())
used={slot.material for o in model.children_recursive if o.type=='MESH' for slot in o.material_slots if slot.material}
for m in sorted(used,key=lambda m:m.name):report['materials'].append({'name':m.name,'baseColorLinear':list(m.diffuse_color),'transparent':m==M['glass']})
(OUT/'model-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
for name in args.render.split(','):
    if name=='none':continue
    scene.camera=cameras[name];scene.render.filepath=str(OUT/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)
print('PARENT_CHILD_MODEL_COMPLETE',json.dumps({'objects':report['meshObjects'],'triangles':triangles,'size':report.get('sizeXYZ')}))
