import math,random,json,os
from pathlib import Path
import numpy as np
import trimesh
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import triangulate
from shapely import constrained_delaunay_triangles
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('/mnt/data/G_V5_work')
random.seed(14)
# Game-space X/right Y/up Z/depth.  G center remains (44.928,0,45.279).
COL={
'concrete':(0.73,0.74,0.68), 'concrete2':(0.87,0.85,0.75),'concrete_shadow':(0.45,0.49,0.50),
'steel':(0.095,0.22,0.25),'steel_lite':(0.21,0.40,0.42), 'steel_dark':(0.07,0.14,0.18),
'bronze':(0.74,0.49,0.26),'gold':(0.90,0.72,0.39),'glass':(0.31,0.60,0.63), 'glass2':(0.52,0.78,0.76),'glass_dark':(0.17,0.37,0.43),
'white':(0.93,0.91,0.83),'floor':(0.74,0.72,0.62), 'earth':(0.39,0.40,0.37),
'rock':(0.37,0.42,0.44), 'rock2':(0.47,0.50,0.49), 'rock3':(0.28,0.35,0.37),
'green':(0.59,0.73,0.56), 'turf':(0.44,0.65,0.49), 'green_dark':(0.27,0.48,0.40),
'water_upper':(0.16,0.51,0.56), 'water_lower':(0.12,0.45,0.56), 'foam':(0.75,0.94,0.91), 'wood':(0.62,0.42,0.26),
'leaf1':(0.26,0.47,0.38), 'leaf2':(0.49,0.63,0.40),'leaf3':(0.65,0.72,0.40),'leaf4':(0.32,0.60,0.55), 'ground_dirt':(0.54,0.53,0.48),
}
items=[]
def add(mesh,mat,name):
    mesh.visual.face_colors=np.tile(np.append(np.array(COL[mat])*255,255).astype('uint8'),(len(mesh.faces),1))
    items.append({'mesh':mesh,'mat':mat,'name':name})
def box(x,y,z,w,h,d,mat,name):
    m=trimesh.creation.box([w,h,d]);m.apply_translation([x,y,z]);add(m,mat,name)
def cyl(x,y,z,r,h,mat,name,n=12,axis='y'):
    m=trimesh.creation.cylinder(radius=r,height=h,sections=n)
    if axis=='y':m.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0]));
    m.apply_translation([x,y,z]);add(m,mat,name)
def rod(a,b,r,mat,name,n=8):
    a=np.array(a);b=np.array(b);dv=b-a;L=np.linalg.norm(dv)
    if L<.01:return
    m=trimesh.creation.cylinder(radius=r,height=L,sections=n)
    m.apply_transform(trimesh.geometry.align_vectors([0,0,1],dv/L))
    m.apply_translation((a+b)/2);add(m,mat,name)
def tapered_disc(x,y,z,rx,ry,rz,mat,name,sub=1):
    m=trimesh.creation.icosphere(subdivisions=sub,radius=1.0);m.apply_scale([rx,ry,rz]);m.apply_translation([x,y,z]);add(m,mat,name)
def poly_3d(name,poly,top,depth,mat,side=None):
    if not isinstance(poly,Polygon):poly=Polygon(poly)
    if not poly.is_valid:poly=poly.buffer(0)
    # Shapely Delaunay clipping with intersection for complex polygon; append top triangles
    vs=[];fs=[]
    for t in constrained_delaunay_triangles(poly).geoms:
        if not poly.covers(t.representative_point()):continue
        coords=list(t.exterior.coords)[:3]
        base=len(vs);vs += [[x,top,z] for x,z in coords];fs.append([base,base+1,base+2])
        if depth:
            base=len(vs);vs += [[x,top-depth,z] for x,z in coords];fs.append([base,base+2,base+1])
    m=trimesh.Trimesh(vertices=vs,faces=fs,process=False);add(m,mat,name)
    if depth:
        for ring in [poly.exterior]+list(poly.interiors):
            cr=list(ring.coords)
            for a,b in zip(cr[:-1],cr[1:]):
                if math.dist(a,b) <.02:continue
                p=[[a[0],top,a[1]],[b[0],top,b[1]],[b[0],top-depth,b[1]],[a[0],top-depth,a[1]]]
                q=trimesh.Trimesh(vertices=p,faces=[[0,1,2],[0,2,3]],process=False);add(q,side or mat,name+' side')
# floating island plan: 38.5 wide x 34 high, expansion on original radius 14 x13
shell_pts=[]
for i in range(72):
    t=2*math.pi*i/72
    rr=1.0+0.025*math.sin(t*5+0.6)+0.02*math.cos(t*7)
    shell_pts.append((19.2*math.cos(t)*rr,17.2*math.sin(t)*rr))
shell=Polygon(shell_pts)
# Water aligned north-south, visibly joined through triple sluice gate; wide hydraulic space
upper=Polygon([(-16.1,6.8),(-14.4,13.2),(-10.6,14.6),(-3.2,13.6),(-2.3,11.0),(-1.6,6.8)])
lower=Polygon([(-16.3,5.8),(-16.6,1.3),(-15.7,-3.4),(-12.8,-6.7),(-9.2,-7.0),(-4.2,-4.6),(-2.0,0.5),(-1.5,5.8)])
# Hydraulic polygons must remain wholly within the new island, with minimum 0.9u coping clearance.
upper=upper.intersection(shell.buffer(-.9));lower=lower.intersection(shell.buffer(-.9))
assert upper.geom_type=='Polygon' and lower.geom_type=='Polygon'
assert shell.covers(upper) and shell.covers(lower)
water_shapes=[upper,lower]
land=shell.difference(upper.union(lower))
# rocky foundation with two-tone strata and jagged lower level
poly_3d('floating plateau shelf',land,-.26,1.12,'rock2','rock')
base_pts=[(x*.86+0.18*math.sin(i*.9),z*.84+0.25*math.cos(i*.8)) for i,(x,z) in enumerate(shell_pts)]
poly_3d('floating bedrock mid stratum',base_pts,-2.25,1.7,'rock','rock3')
base2=[(x*.60,z*.57) for x,z in shell_pts]
poly_3d('lower tapered floating stone',base2,-3.95,2.7,'rock3')
# upper green terrain with water cavities (no fake solid green underneath water)
poly_3d('actual dry grass with two water voids',land,0,.29,'green','concrete')
for i,water in enumerate(water_shapes):
    y=-.66 if i==0 else -1.8
    poly_3d('upstream basin water' if i==0 else 'downstream flood basin water',water,y,.035,'water_upper' if i==0 else 'water_lower')
    # inner retaining walls and capstone; water surface sits below bank
    cs=list(water.exterior.coords)
    for j,(a,b) in enumerate(zip(cs[:-1],cs[1:])):
        L=math.dist(a,b)
        if L<.2:continue
        # stone concrete wall up to ground
        ca=[a[0],-.03,a[1]];cb=[b[0],-.03,b[1]];da=[a[0],y-.08,a[1]];db=[b[0],y-.08,b[1]]
        v=[ca,cb,db,da];m=trimesh.Trimesh(vertices=v,faces=[[0,1,2],[0,2,3]],process=False);add(m,'concrete_shadow','reinforced flood basin retaining wall')
        rod([a[0],.015,a[1]],[b[0],.015,b[1]],.065,'concrete2','basin coping',6)
# island edge perimeter curb and safety rail on perimeter spaced, road link later
ring=list(shell.exterior.coords)
for k,(a,b) in enumerate(zip(ring[:-1],ring[1:])):
    rod([a[0],.06,a[1]],[b[0],.06,b[1]],.12,'concrete2','island rim coping')
# FLOWING WATER: foam stream near gate and stepped water race
for lane in range(3):
    x=-13.6+(lane+.5)*3.15
    for k in range(9):
        z=5.6- k*.73
        y=-.87-.10*k
        if k<=4:
            box(x+0.04*math.sin(k),y,z,2.18,.045,.40,'foam' if k%3==0 else 'water_lower','falling stepped discharge ribbon')
        for j in range(2):
            dx=(-.8 if j==0 else .8) +.14*math.sin(k)
            box(x+dx,y+.06,z,0.055,.02,.28,'foam','water turbulence edge')
# Sluice dam: 3 bays; front face z~6.3, aligned over water; heavy civil structure
GATE_X=[-14.0,-10.9,-7.8,-4.7]
for pi,x in enumerate(GATE_X):
    box(x,2.6,6.25,.95,7.6,3.6,'concrete','major dam pier concrete')
    box(x,5.95,6.25,1.25,.33,4.0,'concrete2','pier cap')
    box(x,1.0,4.55,1.4,3.2,.55,'concrete_shadow','gate base reinforced shear wall')
    for y in [0.3,1.9,3.4,4.8]:
        box(x+.5,y,5.8,.11,.065,2.0,'concrete2','dam pier construction seams')
# 3 solid gate leaves and machinery
for k in range(3):
    x=(GATE_X[k]+GATE_X[k+1])/2
    box(x,1.70,6.0,2.28,4.42,.34,'steel','sluice gate deep steel leaf')
    box(x,4.12,5.80,2.4,.22,.48,'steel_dark','upper gate header plate')
    for yy in [0.15,.9,1.6,2.3,3.0]:box(x,yy,5.79,2.38,.10,.12,'steel_lite','vertical sluice steel ribs')
    for xx in [-.8,0,.8]:box(x+xx,1.72,5.72,.1,4.3,.11,'steel_lite','sluice leaf vertical ribs')
    cyl(x,6.55,6.1,.43,.45,'steel_dark','hoist gear assembly',16)
    cyl(x,6.82,6.1,.23,.09,'gold','gear indicator',16)
    rod([x,4,6.15],[x,6.65,6.15],.115,'bronze','threaded gate screw')
    box(x,7.04,6.10,1.3,.46,.95,'steel_dark','hoist housing')
    for xx in [-.95,.95]:rod([x+xx,.3,5.73],[x+xx,5.72,5.73],.055,'concrete2','gate guide track')
# dam crossbeam+catwalk
box(-9.35,5.45,6.15,12.5,.78,3.4,'concrete2','massive dam bridge crossbeam')
box(-9.35,7.42,6.1,13.4,.20,3.8,'steel_lite','hoist service catwalk')
for z in [4.1,8.0]:
    for x in np.linspace(-15.5,-3.2,15):
        rod([x,7.52,z],[x,8.54,z],.044,'steel','dam walkway baluster',6)
    rod([-15.5,8.55,z],[-3.2,8.55,z],.065,'steel','dam walkway guardrail')
# cross truss diagonal brace highlights
for i in range(4):
    x=-14.7+i*3.1
    rod([x,6.05,7.77],[x+2.3,7.1,7.77],.082,'steel_lite','dam gantry diagonal brace')
command_group_start=len(items)
# Comms command building right of basin, glass with cantilever bands and facade walls
# footprint x=2.3..16; z 2.0..10.8 main 12x7, lobby front toward centre z=-1
box(9.5,1.5,5.5,12.5,3,7.2,'concrete','control centre ground podium')
box(9.6,3.65,5.5,12.6,1.25,7.3,'glass_dark','upper command glazed volume')
box(9.1,5.15,5.5,14.3,.45,8.0,'steel_lite','command cantilever roof')
box(9.1,4.86,5.5,14.25,.10,8.1,'bronze','thin copper soffit line')
# Lower glass facade front z=1.7 with piers and boxed window cassettes
for x in np.linspace(4.1,15.0,8):
    box(x,1.70,1.82,1.23,2.58,.08,'glass','control room glass panel')
    box(x-.62,1.72,1.67,.09,2.72,.19,'steel','control room front mullion')
for yy in [0.45,3.0]:box(9.5,yy,1.64,12.0,.12,.19,'bronze','front facade horizontal stringcourse')
# side glass panels x walls
for z in np.linspace(2.6,8.4,5):
    box(3.25,1.65,z,.08,2.58,1.00,'glass2','glass side module')
    box(15.80,1.65,z,.08,2.58,.95,'glass2','glass side module')
    box(3.18,2,z+.49,.12,3,.10,'steel','side mullion')
    box(15.9,2,z+.49,.12,3,.10,'steel','side mullion')
# Rear elevation: continuous glazed monitoring wall and vertical shade fins (no empty grey box)
for x in np.linspace(4.2,14.95,9):
    box(x,1.72,9.13,1.04,2.43,.07,'glass2','rear control glass panel')
    box(x+.52,1.75,9.23,.07,2.63,.10,'steel','rear control fin mullion')
box(9.5,3.1,9.19,12.15,.12,.14,'bronze','rear upper spandrel')
# Additional vertical landmark ribs align with facade columns
for x in [4.05,6.4,8.75,11.1,13.45,15.7]:
    box(x,2.6,1.55,.18,4.5,.27,'concrete2','command civic vertical fin')
# Overlook parapet integrated in main building, overlooking the sluice
box(2.99,4.05,5.7,.22,.86,5.2,'glass2','monitoring balcony glazing')
# Roof louvers and solar panels
for i in range(7):
    x=4.2+i*1.65
    box(x,5.41,5.6,1.24,.075,3.8,'steel_lite','sun shade roof louvers')
    box(x,5.48,5.6,1.08,.04,3.24,'glass_dark','solar roof strips')
# elevated observation lantern with outriggers anchored on building corner
box(13.8,6.9,7.0,3.0,3.1,3.3,'glass2','tower glazing envelope')
box(13.8,8.62,7.0,4.1,.42,4.1,'steel_dark','civic observation crown')
for x in [12.3,15.3]:
    for z in [5.4,8.6]:box(x,6.9,z,.15,3.6,.15,'steel','observatory mullion')
for yy in [5.4,8.0]:box(13.8,yy,7.0,3.2,.17,3.5,'bronze','observation tower belt')
# Small vertical antenna mast
rod([13.8,8.9,7.0],[13.8,10.0,7.0],.075,'steel_dark','sensor mast')
cyl(13.8,10.0,7.0,.15,.15,'gold','sensor cap',12)
# public glass entrance overhang, door and fascia
box(7.6,3.35,1.0,5.2,.22,2.0,'steel_dark','public entrance canopy')
box(7.6,3.15,1.02,5.1,.065,2.1,'bronze','entrance soffit')
for x in [5.35,9.9]:box(x,1.55,.15,.16,3.05,.16,'steel','canopy support')
box(7.7,1.65,1.58,2.15,2.75,.08,'glass2','closed command lobby entry')
# append separate low-rise emergency operations wing at east/south
box(11.2,1.5,-2.7,7.8,3.0,4.1,'concrete2','emergency services annex')
box(11.2,3.2,-2.7,8.5,.31,4.8,'bronze','annex roof rim')
box(11.2,3.40,-2.7,8.9,.31,5,'steel_lite','emergency centre wing roof')
for x in np.linspace(8.45,13.95,6):
    box(x,1.65,-4.79,.73,2.3,.10,'glass','emergency wing glazing')
    box(x+.39,1.65,-4.88,.06,2.55,.1,'steel','emergency window dividers')
# light roof vent
box(12.85,3.66,-2.6,2.0,.35,1.4,'concrete','vent stack housing')
# Display board at front of courtyard
box(3.5,1.45,-2.7,.28,2.0,2.4,'steel_dark','public flood information monolith')
box(3.29,1.48,-2.7,.04,1.45,1.7,'glass2','info display screen')
for y in [.92,1.17,1.42]:box(3.26,y,-2.55,.04,.045,1.16,'gold','info map graphic lines')
# Refit the large command architecture into the new irregular island boundary,
# without shrinking the gate, player, path width, or global world.
for it in items[command_group_start:]:
    scale=np.eye(4);scale[0,0]=.87;scale[0,3]=1.05;scale[2,2]=.87;scale[2,3]=.12
    it['mesh'].apply_transform(scale)
# Public route floor: preserve exact S21/S22 cubic centreline and a 4.8-wide dry core.
# Unlike the rejected old V4, part of S22 is now a real elevated hydraulic crossing.
G_CENTER=np.array([44.928,45.279])
ROUTE_CONTROLS={
'S21':np.array([[44.226,6.318],[47.736,13.338],[53.001,33.696],[44.928,45.279]])-G_CENTER,
'S22':np.array([[44.928,45.279],[37.908,46.683],[36.504,40.716],[31.239,37.557]])-G_CENTER}
def bezier(cp,t):return (1-t)**3*cp[0]+3*(1-t)**2*t*cp[1]+3*(1-t)*t*t*cp[2]+t**3*cp[3]
route_polys={}
for label,cp in ROUTE_CONTROLS.items():
    line=LineString([bezier(cp,i/120) for i in range(121)])
    zone=line.buffer(2.4,cap_style=2,join_style=2).intersection(shell)
    route_polys[label]=zone
    poly_3d('protected '+label+' 4.8 public promenade',zone,.13,.24,'floor','concrete_shadow')
    if label=='S22':
        # Continuous bridge guardrails on both sides of the wide S22 crossing (not on the 4.8 core).
        cp=ROUTE_CONTROLS['S22'];points=[bezier(cp,i/160) for i in range(161)]
        for side in [-1,1]:
            exposed=[]
            for i in range(1,160,3):
                cur=np.array(points[i]);tng=np.array(points[i+1])-np.array(points[i-1]);tng/=np.linalg.norm(tng)
                norm=np.array([-tng[1],tng[0]]);q=cur+norm*2.6*side
                if lower.buffer(.4).contains(Point(cur)) and shell.buffer(-.35).contains(Point(q)):
                    exposed.append((float(q[0]),float(q[1])))
            for j,(x,z) in enumerate(exposed):
                rod([x,.16,z],[x,1.42,z],.058,'steel','S22 bridge protective baluster',7)
                if j>0 and math.dist(exposed[j-1],exposed[j])<2.9:
                    rod([exposed[j-1][0],1.42,exposed[j-1][1]],[x,1.42,z],.072,'steel','S22 bridge continuous top handrail',8)
        # Visible elevated superstructure wherever this protected passage passes over lower water.
        wet=zone.intersection(lower.buffer(.10))
        if not wet.is_empty:
            for unit in ([wet] if wet.geom_type=='Polygon' else list(wet.geoms)):
                if unit.area>.2:poly_3d('S22 suspended water crossing structural slab',unit,-.13,.48,'concrete2','concrete_shadow')
                # Below ground the original flow is kept clear; rebuilt head clearance required by Codex.

# Pre-render road collision manifest, but *not* official in-game navigation validation.
route_audit={s:{'protectedRoadArea':round(poly.area,3),'waterOverlapLower':round(poly.intersection(lower).area,3), 'waterOverlapUpper':round(poly.intersection(upper).area,3)} for s,poly in route_polys.items()}
# Major culvert walk + viewpoint on basin rim avoiding water
box(-1.2,.18,6.65,2.2,.30,11.0,'concrete2','north water edge inspection promenade')
for z in np.linspace(1.7,11.2,10):
    rod([-.12,.37,z],[-.12,1.5,z],.047,'steel','inspection balcony guardrail')
rod([-.12,1.50,1.7],[-.12,1.50,11.2],.066,'steel','inspection promenade top rail')
# Primary Zhang Gu-li guide reserve: relocated to an actually dry public space, behind the safe approach route.
NPC_STOP=(10.2,-9.1); NPC_AREA=Polygon([(8.7,-10.6),(11.7,-10.6),(11.7,-7.6),(8.7,-7.6)])
poly_3d('NPC future guide reserve 3x3 dry civic plaza',NPC_AREA,.14,.11,'concrete2')
for z in [-10.1,-9.1,-8.1]:box(10.2,.153,z,2.75,.018,.055,'bronze','guide plaza paving band')
# Waterfront landscaping not random tiny balls, three groups of coherent planting
for cx,cz,rx,rz in [(-15.7,-10.2,2.0,1.0),(15.6,-10.7,2.5,1.2),(0.0,12.7,1.7,1.1)]:
    cyl(cx,.15,cz,rx,.28,'concrete2','raised garden planter',18)
    for i in range(5):
        px=cx+random.uniform(-.65,.65)*rx;pz=cz+random.uniform(-.65,.65)*rz
        tapered_disc(px,.54,pz,.38,.31,.40,'leaf2' if i%2 else 'leaf1','planted grass')
# 11 varied trees in clusters, not wall of spheres
for x,z,s in [(16,-12,1),(-17,-8,.76),(17,0,1.1),(-18,0,.85),(16,12,1.0),(0,14,1.0),(3,13,.76),(18,6,.92),(8,-12,.7),(-13,-13,.8),(4,-13,.73)]:
    cyl(x,.82*s,z,.18*s,1.65*s,'wood','tree trunk',9)
    for j,(ox,oy,oz) in enumerate([(0,2.2,0),(.4,2.55,0),(-.42,2.6,.16),(.12,2.8,-.2)]):
        tapered_disc(x+ox*s,oy*s,z+oz*s,.75*s,.62*s,.65*s,['leaf1','leaf2','leaf3','leaf4'][j],'mixed woodland canopy',1)
# Tiered riverbank resilience exhibit — civil landscaping, not a row of identical bushes.
# Both bands must be on dry terrain away from bridge navigation, or build fails.
levee_bands=[
 Polygon([(-12.4,-11.2),(-6.6,-11.2),(-5.7,-10.1),(-11.5,-9.9)]),
 Polygon([(-11.4,-10.65),(-6.0,-10.65),(-5.75,-9.75),(-10.7,-9.65)])]
for k,p in enumerate(levee_bands):
    if not land.buffer(-.09).covers(p):
        raise RuntimeError('Levee exhibit crosses dry land boundary')
    if any(r.intersects(p) for r in route_polys.values()):
        raise RuntimeError('Levee exhibit crosses protected public core')
    poly_3d('layered flood protection earth berm '+str(k),p,.28+k*.12,.24,'concrete2','concrete_shadow')
    inset=p.buffer(-.21)
    if not inset.is_empty:poly_3d('levee vegetated crest '+str(k),inset,.34+k*.12,.08,'turf')
# Flood warning gauge on separate engineered platform
box(-13.7,.22,-10.3,1.2,.40,1.2,'concrete2','flood gauge podium')
rod([-13.7,.42,-10.3],[-13.7,3.6,-10.3],.10,'steel','levee benchmark pole')
box(-13.7,3.4,-10.3,.35,.5,.42,'bronze','high water warning head')
for yy in [.95,1.35,1.75,2.15,2.55]:box(-13.59,yy,-10.3,.035,.055,.26,'white','vertical high water graduation')
# equipment / flood alert demonstration on secondary pad
cyl(16.4,.18,-4.7,.9,.32,'concrete2','sensor podium',16)
rod([16.4,.38,-4.7],[16.4,3.75,-4.7],.09,'steel','sensor pylon')
box(16.4,3.45,-4.7,.56,.45,.42,'gold','flood level telemetry head')
# wooden benches facing flood facilities
for x,z in [(16,-8),(2.0,10.6),(-17,8)]:
    box(x,.53,z,1.7,.18,.53,'wood','riverside seating')
    for xx in [-.60,.6]:box(x+xx,.3,z,.09,.42,.43,'steel','bench supports')
# understated public lanterns; no new real light sources
for x,z in [(2.5,-12),(3.6,-8),(18,-3),(17,9),(-1,12),(-16,-5)]:
    rod([x,0,z],[x,3.7,z],.075,'steel','site light column')
    rod([x,3.7,z],[x+.68,3.7,z],.075,'steel','site light projecting head')
    box(x+.66,3.67,z,.35,.11,.17,'foam','architectural LED bar')
# finish mesh assembly
scene=trimesh.Scene();
for i,x in enumerate(items):scene.add_geometry(x['mesh'],geom_name=f"{i:04d}_{x['name']}")
scene.export(ROOT/'G_V5_hydraulic_campus_design.glb')
summary={'design':'G V5 expanded original location, study-only hydraulic campus', 'GworldCentre':[44.928,0,45.279],
 'newFootprint':shell_pts,'oldNominal':[28,26],'newNominal':[38.4,34.4],
 'waterBodies':[list(poly.exterior.coords) for poly in water_shapes],
 'diagramRoutes':'schematic only; S21/S22 centreline must be derived from PR17 Bezier data',
 'buildingEnvelopes':{'sluice':[-15.65,-3.2,4.1,8.5,8.6], 'commandCentre':[2.75,15.2,1.42,8.45,10.15], 'operationsWing':[7.4,14.5,-4.5,-.3,3.6]},
 'polygonArea':shell.area,'waterArea':upper.area+lower.area,
 'meshCount':len(items),'triangles':int(sum(len(x['mesh'].faces) for x in items)),
 'routeAudit':route_audit,'npcProposed':{'position':[10.2,0,-9.1],'standingArea':[3,3], 'priorWaterGuideInvalid':True}}
(ROOT/'G_V5_design_manifest.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print('geometry generated')
