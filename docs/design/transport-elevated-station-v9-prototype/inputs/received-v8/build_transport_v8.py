"""Yuanli F transport island, authored single-source parametric design.
Units: Sky Isles world units. Coordinates: x=east, z=north, y=up.
Independent design geometry: not linked to live Three.js ground collider.
"""
from __future__ import annotations
import os, math, json, zipfile
from collections import defaultdict
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import trimesh
import vtk
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray
from shapely.geometry import Point, Polygon, LineString, box
from shapely.affinity import scale, translate
from shapely.ops import triangulate, unary_union
ROOT=Path('/mnt/data/transport_island_v8_viaduct')
VIEWS=ROOT/'views'; VIEWS.mkdir(exist_ok=True)
COLORS={
 'sandstone':'#D4C9BC','strata':'#BDB6AC','strataDark':'#9E9D99','warmSteel':'#667D82','islandStone':'#DFD8CF','ledge':'#CBC5BE','paving':'#E7DFD3','pavingAccent':'#D6CDBE','warmPaver':'#F7E5B7',
 'roof':'#778A9B','roofEdge':'#D5DCE1','roofSeam':'#5D7487','glass':'#9AC6D1','glassClear':'#B9DDE2',
 'steel':'#526A78','teal':'#3B7180','wood':'#C08B55','woodPale':'#E1B984', 'cream':'#F5F2E9',
 'lightGlass':'#E6F4F6','interior':'#F3DEAD','stone':'#D4C6B1','dark':'#3B4C56',
 'trainBase':'#E6EDF0','trainBlue':'#3B8699','trainRoof':'#AABAC2','trainGlass':'#4C7584','trainYellow':'#E8BF68',
 'rail':'#697F86','railGround':'#747D7F','soil':'#6E795B','leaf':'#81A671','leaf2':'#A5C27F',
 'leaf3':'#56795C','blossom':'#F2C3BA','flower':'#F5E4CE','lawn':'#99B783',
 'woodDark':'#8B6B50','yellow':'#DDBE65','shadow':'#BAB6B0', 'black':'#414C53'
}
GEOMS=defaultdict(list)
SPECS={}

def push(group,mat,mesh):
 if mesh is None or len(mesh.faces)==0:return
 GEOMS[(group,mat)].append(mesh)

def mesh_triangles(verts,faces):return trimesh.Trimesh(vertices=np.asarray(verts,dtype=float),faces=np.asarray(faces,dtype=int),process=False)

def cube(group,mat,loc,size):
 m=trimesh.creation.box(extents=size);m.apply_translation(loc);push(group,mat,m)

def capsule_rounded(group,mat,center,size,radius=.18,segments=8):
 # beveled mass in plan, clean rounded train nose
 x,y,z=center; w,h,d=size; rr=min(radius,w*.25,d*.25)
 poly=box(-w/2+rr,-d/2+rr,w/2-rr,d/2-rr).buffer(rr,resolution=segments)
 poly=translate(poly,xoff=x,yoff=z)
 solid_polygon(group,mat,poly,y-h/2,y+h/2)

def quad(group,mat,points):
 verts=np.asarray(points,dtype=float);push(group,mat,mesh_triangles(verts,[[0,1,2],[0,2,3],[2,1,0],[3,2,0]]))

def solid_polygon(group,mat,poly,y0,y1):
 if poly.is_empty:return
 if poly.geom_type=='MultiPolygon':
  for p in poly.geoms:solid_polygon(group,mat,p,y0,y1)
  return
 # triangulate shape even if holes/concavities; clip for accuracy
 verts=[];faces=[]
 for t in triangulate(poly):
  sect=t.intersection(poly)
  if sect.is_empty or sect.area<1e-6:continue
  if sect.geom_type=='Polygon':ps=[sect]
  elif sect.geom_type=='MultiPolygon':ps=list(sect.geoms)
  else:continue
  for pp in ps:
   ext=list(pp.exterior.coords)[:-1]
   if len(ext)<3:continue
   # polygon part triangles or fan (convex)
   for i in range(1,len(ext)-1):
    xz=[ext[0],ext[i],ext[i+1]];base=len(verts)
    verts.extend([(x,y1,z)for x,z in xz]);faces.append([base,base+1,base+2])
    base=len(verts);verts.extend([(x,y0,z)for x,z in xz]);faces.append([base,base+2,base+1])
 for ring in [poly.exterior,*poly.interiors]:
  coords=list(ring.coords)
  for (x,z),(xx,zz) in zip(coords,coords[1:]):
   b=len(verts);verts.extend([(x,y0,z),(xx,y0,zz),(xx,y1,zz),(x,y1,z)]);faces.extend([[b,b+1,b+2],[b,b+2,b+3]])
 push(group,mat,mesh_triangles(verts,faces))

def path_slab(group,mat,points,w,y0,y1):
 solid_polygon(group,mat,LineString(points).buffer(w/2,cap_style=2,join_style=2),y0,y1)

def cyl(group,mat,x,y,z,r,h,sections=10):
 mesh=trimesh.creation.cylinder(radius=r,height=h,sections=sections);mesh.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0]));mesh.apply_translation((x,y,z));push(group,mat,mesh)

def ball(group,mat,x,y,z,r,sub=1,scale3=(1,1,1)):
 m=trimesh.creation.icosphere(subdivisions=sub,radius=r);m.apply_scale(scale3);m.apply_translation((x,y,z));push(group,mat,m)

def beam(group,mat,a,b,radius=.045,sections=8):
 p=np.asarray(a,dtype=float);q=np.asarray(b,dtype=float);axis=q-p;length=np.linalg.norm(axis)
 if length<1e-6:return
 m=trimesh.creation.cylinder(radius=radius,height=length,sections=sections)
 orient=trimesh.geometry.align_vectors([0,0,1],axis/length);m.apply_transform(orient)
 m.apply_translation((p+q)/2);push(group,mat,m)

def sloped_panel(group,mat,x0,x1,z0,z1,func,thick=.10):
 vv=[]
 for yshift in [0,-thick]:
  for x,z in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]:vv.append((x,func(x,z)+yshift,z))
 ff=[[0,1,2],[0,2,3],[6,5,4],[7,6,4]]
 for a,b in [(0,1),(1,2),(2,3),(3,0)]:ff.extend([[a,b,b+4],[a,b+4,a+4]])
 push(group,mat,mesh_triangles(vv,ff))

def roof_y(x,z):
 # one continuous folded aero roof, not a separate roof glued on a box
 return 5.16+0.25*(x/8.7)**2-0.115*(z+2.5)+0.11*math.sin((x+8.7)/17.4*math.pi)

def plant_tree(x,z,rad=1.2,height=3.4,seed=0):
 rng=np.random.default_rng(seed)
 # biological scale: trunk and branching canopy, medium detail stable in mobile
 cyl('Landscape','woodDark',x,height*.245,z,.13,height*.49,10)
 for j,(dx,dz) in enumerate([(-.42,0),(.39,.16),(-.15,-.36)]):
  beam('Landscape','woodDark',(x,.40*height,z),(x+dx*rad,.71*height,z+dz*rad),.061,8)
 parts=[(0,.77,0,.91),(-.43,.72,.19,.67),(.42,.72,-.06,.68),(.04,.84,-.40,.61),(-.15,.89,.26,.57)]
 for i,(dx,yy,dz,r) in enumerate(parts):
  mat=['leaf','leaf2','leaf3','leaf2','leaf'][i]
  ball('Landscape',mat,x+dx*rad,height*yy,z+dz*rad,rad*r,2,(1.05,.83,.94))
 # smaller layered green lobes remove the lollipop silhouette
 for i in range(13):
  t=i*2.399; rr=rad*rng.uniform(.38,.74)
  dx=math.cos(t)*rr; dz=math.sin(t)*rr
  ball('Landscape',['leaf2','leaf','leaf3'][i%3],x+dx,height*(.70+.11*rng.random()),z+dz,
       rad*rng.uniform(.22,.34),1,(1,.77,1))

# =============================================================================

# V8 ELEVATED TRA LINE: 1.5-unit player, four preserved bridge links.
from shapely.prepared import prep
from scipy.ndimage import label
from PIL import ImageFont
import cv2
# Extend material scheme without generic blocks
COLORS.update({'viaduct':'#C8C6BF','pierShade':'#9EA5A5','transom':'#88969B','offWhite':'#FAF7EF','railTeal':'#1F738A','railNavy':'#23566E','railGold':'#E6B95F','windows':'#8CBECB','metal':'#687E8C','metalLight':'#B7C7CC','glassAmber':'#EED29B','roofDark':'#526878','railConcrete':'#BBC1BC','bark':'#775F4C','railFence':'#647E84','plinth':'#EFE8DB','plantDark':'#52785B','brick':'#CCBDA9'})
# Reuses irregular proven outline; geometry not resized into forbidden adjacent roads.
main=Point(0,0).buffer(8.65,resolution=100)
south=box(-8.65,-9.65,8.65,-4.05).buffer(1.52,resolution=36)
site=main.union(south).buffer(.15).buffer(-.15).simplify(.03,preserve_topology=True)
SITE_W,SITE_D=site.bounds[2]-site.bounds[0],site.bounds[3]-site.bounds[1]
# Island stratified exposed edges; no added planar footprint
solid_polygon('01 Island','sandstone',site,-.58,.02)
solid_polygon('01 Island','strata',site.buffer(-.16),-.90,-.55)
solid_polygon('01 Island','strataDark',site.buffer(-.70),-1.25,-.89)
solid_polygon('01 Island','islandStone',site.buffer(-1.12),-1.66,-1.23)
solid_polygon('01 Island','paving',site.buffer(-.34),.02,.07)
# edge retaining seam is not physics obstruction
rim=site.buffer(-.015).difference(site.buffer(-.16));solid_polygon('01 Island','roofEdge',rim,-.11,.014)
# self-contained ornamental slabs NOT covering east-west spine (z +/- 2.4)
for x in np.arange(-9.0,9.1,1.0):
 for z in np.arange(-9.5,8.0,1.0):
  if ((round(x)+round(z))%4):continue
  tile=box(x-.44,z-.44,x+.44,z+.44).intersection(site.buffer(-.4))
  if tile.area>.22:solid_polygon('02 Paving','pavingAccent',tile,.074,.080)
# Road alignment is kept neutral (same material), four bridges land freely.
path_slab('02 Paving','warmPaver',[(-8.4,0),(8.4,0)],.16,.085,.098)
path_slab('02 Paving','warmPaver',[(0,8.3),(0,2.9),(0,0)],.15,.087,.103)
# Crosswalk z from -2.6 to ground transit spine, tactile guidance branch
for x in np.arange(-2.0,2.01,.48):
 cube('02 Paving','offWhite',(x,.101,-2.52),(.28,.009,.34))
path_slab('02 Paving','yellow',[(0,-3.7),(0,-2.5),(0,-.6)],.15,.093,.105)
# ELEVATED RAILWAY: deck centerline z=-7.72 at y=6.10, exposed rail y=6.45
# Elevated deck is long, thin and legible, not a floating opaque monolith.
cube('03 Viaduct','viaduct',(0,5.96,-7.66),(18.9,.58,3.35))
cube('03 Viaduct','pierShade',(0,5.59,-7.66),(18.7,.20,3.35))
for z in [-9.25,-6.07]:cube('03 Viaduct','metalLight',(0,6.16,z),(18.9,.12,.09))
# Structural piers: underpass open; no piers touch east-west spine, all in south half.
PIERS=[]
for x in [-7.65,-2.55,2.55,7.65]:
 for z in [-8.79,-6.63]:
  PIERS.append((x,z))
  cube('04 Elevated piers','viaduct',(x,2.77,z),(.38,5.54,.44))
  cube('04 Elevated piers','pierShade',(x,5.38,z),(.63,.38,.64))
  cube('04 Elevated piers','brick',(x,.14,z),(.92,.26,.9))
  beam('04 Elevated piers','metal',(x,5.16,z),(x+(.44 if x<0 else -.44),5.73,z),.08,8)
# diagonal restrained bridges and anti-sway bracing are visible under deck
for a,b in [(-7.65,-2.55),(-2.55,2.55),(2.55,7.65)]:
 for z in [-8.79,-6.63]:beam('04 Elevated piers','transom',(a,5.28,z),(b,5.28,z),.12,8)
# Track bed rails running east-west x; platform at z=-6.35..-5.45
cube('05 Track','railGround',(0,6.32,-8.35),(18.15,.12,1.74))
for x in np.arange(-8.7,8.8,.53):cube('05 Track','bark',(x,6.41,-8.35),(.16,.10,1.65))
for z in [-8.94,-7.75]:
 beam('05 Track','steel',(-9.0,6.57,z),(9.0,6.57,z),.052,8)
 beam('05 Track','roofEdge',(-9.0,6.615,z),(9.0,6.615,z),.014,6)
# platform extends within deck, barrier west/east and clear vertical circulation at x=-6.3
cube('06 Platform','plinth',(0,6.27,-6.47),(18.65,.16,1.08))
for x in np.arange(-8.8,8.9,.40):cube('06 Platform','yellow',(x,6.365,-7.02),(.25,.012,.11))
# canopy top at 10.3: transparent continuous mid skyband and narrow folded metallic eaves
# supports tie canopy to deck not to unrelated ground hall
for x in [-8.0,-4,0,4,8.0]:
 for z in [-6.25,-8.08]:
  cube('07 Platform canopy','metal',(x,8.36,z),(.16,4.16,.17))
  beam('07 Platform canopy','metal',(x,9.74,z),(x+(0.5 if x<0 else -0.5),10.27,z),.075,8)
# long canopy tier with translucent center and warm timber underlining
for x in np.arange(-8.95,9.0,1.0):
 for z in np.arange(-9.18,-5.27,.72):
  roofmat = 'glassClear' if -8.50<z<-7.14 else 'roofDark'
  cube('07 Platform canopy',roofmat,(x,10.49+.025*abs(x),z),(.975,.14,.70))
for z in [-9.52,-5.06]:cube('07 Platform canopy','metalLight',(0,10.40,z),(19.20,.22,.10))
for x in np.arange(-8.9,9.0,.66):beam('07 Platform canopy','woodPale',(x,10.19,-9.16),(x,10.19,-5.17),.035,6)
for z in np.arange(-9.4,-5.04,.86):beam('07 Platform canopy','roofEdge',(-9.1,10.57,z),(9.1,10.57,z),.028,6)
# Platform overhead passenger digital timetable, actual under roof
def sign_box(x,y,z,w,h,front=-1):
 cube('10 Signs','railNavy',(x,y,z),(w,h,.13))
 cube('10 Signs','offWhite',(x,y,z+front*.079),(w-.18,h-.16,.015))
for x in [-4.4,4.4]:
 sign_box(x,8.71,-5.88,1.85,.56,1)
 for t in range(3):cube('10 Signs','railTeal',(x-.32,8.85-.15*t,-5.785),(.66,.025,.014))
# Train: visible recognizable double-coach body; z=-8.32 behind platform, y=6.7..9.3
for cx in [-3.55,3.55]:
 capsule_rounded('08 Train','trainBase',(cx,7.88,-8.37),(6.92,2.46,1.60),.18)
 capsule_rounded('08 Train','metalLight',(cx,9.14,-8.37),(6.84,.18,1.52),.12)
 for z in [-9.18,-7.56]:
  cube('08 Train','railGold',(cx,7.38,z),(6.85,.12,.025))
  cube('08 Train','railTeal',(cx,7.16,z),(6.84,.20,.026))
  for k,xx in enumerate(np.linspace(cx-2.75,cx+2.75,7)):
   if k in [2,5]:
    cube('08 Train','railTeal',(xx,7.83,z),(.44,1.66,.035))
    cube('08 Train','windows',(xx,8.16,z+(.031 if z>-8 else -.031)),(.32,.47,.022))
   else:
    cube('08 Train','trainGlass',(xx,8.31,z+(.026 if z>-8 else -.026)),(.68,.65,.025))
   cube('08 Train','metal',(xx-.41,8.30,z),(.03,.68,.07))
  cube('08 Train','offWhite',(cx,9.02,z),(6.73,.035,.05))
# underfloor bogies and coupler: ensure train sits on its actual rail envelope
for cx in [-3.55,3.55]:
 cube('08 Train','metal',(cx,6.67,-8.37),(6.25,.24,1.26))
 for dx in [-2.25,2.25]:
  beam('08 Train','railNavy',(cx+dx,6.86,-9.17),(cx+dx,6.86,-7.57),.21,12)
for x,sig in [(-7.1,-1),(7.1,1)]:
 cube('08 Train','railNavy',(x+sig*.035,8.26,-8.37),(.068,1.05,1.06))
 for z in [-8.94,-7.8]:ball('08 Train','railGold',x+sig*.085,7.27,z,.115,1,(.36,.48,.35))
# Entire bridge railings: translucent / airy, interrupts under platform access where needed
for z in [-5.77,-9.20]:
 for x in np.arange(-9,9.1,1.25):
  beam('09 Platform guard','metal',(x,6.4,z),(x,7.50,z),.035,6)
 for h in [6.88,7.48]:beam('09 Platform guard','metal',(-9.15,h,z),(9.15,h,z),.035,6)
# Ground station hall: coherently nestled under elevated rail and presents identity to main road.
# Hall FRONT z=-3.04; east-west protected road spans +/-2.4, >0.64 clearance.
HALL=box(-6.85,-5.79,6.85,-3.04)
cube('11 Hall','plinth',(0,.19,-4.42),(13.7,.32,2.80))
# warm lobby glazing in framed bays; large bright central entrance
for x in [-6.65,-5.1,-3.55,-2.0,2.0,3.55,5.1,6.65]:
 cube('11 Hall','wood',(x,2.23,-3.03),(.12,4.02,.18))
for x in [-5.87,-4.3,-2.77,2.77,4.3,5.87]:
 cube('11 Hall','glassClear',(x,2.18,-3.04),(1.35,3.85,.075))
for x in [-6.75,6.75]:
 cube('11 Hall','plinth',(x,2.22,-4.42),(.18,4.20,2.95))
for x in np.arange(-5.8,6,.88):
 cube('11 Hall','glassAmber',(x,2.16,-5.82),(.84,3.70,.065))
# central door deeper inside to physically provide entrance and textured floor
for x in [-1.2,1.2]:cube('11 Hall','glass',(x,2.04,-3.04),(1.13,3.52,.063))
for x in [-1.78,0,1.78]:cube('11 Hall','metal',(x,2.19,-2.94),(.062,3.90,.16))
cube('11 Hall','woodPale',(0,4.09,-2.99),(13.7,.26,.17))
# Light, human scale roof across ground building, elegant metal glazed 1.8-unit roof stripe
cube('12 Hall roof','roof',(0,4.63,-4.56),(14.45,.25,3.40))
cube('12 Hall roof','glassClear',(0,4.78,-4.40),(5.3,.06,1.60))
for x in np.arange(-7.05,7.10,.68):
 cube('12 Hall roof','metalLight',(x,4.82,-4.56),(.036,.04,3.36))
for z in [-6.28,-2.85]:cube('12 Hall roof','metalLight',(0,4.63,z),(14.43,.27,.09))
for x in np.arange(-6.0,6.01,.34):
 if abs(x)<1.8:continue
 cube('13 Facade','woodPale',(x,3.30,-2.98),(.075,1.22,.11))
# integrated flowers and benches flank the real lobby entrance, attached to frontage outside the road corridor
for px in [-4.72,4.72]:
 cube('13 Facade','plinth',(px,.31,-3.05),(2.35,.40,.35))
 cube('13 Facade','soil',(px,.53,-3.05),(2.16,.07,.24))
 for k in range(18):
  rng=np.random.default_rng(int((px+20)*33)+k)
  bx=px+rng.uniform(-1.0,1.0);bz=-3.05+rng.uniform(-.08,.08)
  ball('17 Landscape',['leaf','blossom','flower','leaf2'][k%4],bx,.65,bz,rng.uniform(.10,.17),0,(.95,.7,.9))
# Main exterior canopy roof projects toward player, without touching road physical floor
cube('13 Facade','roofDark',(0,4.24,-2.65),(5.85,.17,.82))
for x in np.arange(-2.7,2.8,.43):beam('13 Facade','wood',(x,4.06,-3.02),(x,4.06,-2.27),.032,6)
# Main station name sign band — actual modeled 3D font outlines, no deceptive photo text.
# 2D vector glyphs converted into real triangulated faces x/y at FRONT z=-2.49.
cube('14 Station identity','offWhite',(0,3.75,-2.50),(5.75,.82,.12))
# left badge depicts simplified independent rail motif, not the official TRA trademark
cube('14 Station identity','railNavy',(-2.25,3.74,-2.395),(.50,.51,.035))
for dx in [-.11,.11]:beam('14 Station identity','offWhite',(-2.25+dx,3.55,-2.370),(-2.25+dx,3.92,-2.370),.022,6)
beam('14 Station identity','offWhite',(-2.44,3.92,-2.37),(-2.06,3.92,-2.37),.026,6)
# texts contours extracted from a locally installed font, with hole-aware contours
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def glyph_word(text,cx,cy,z,width,targeth=.33,group='14 Station identity',mat='railNavy'):
 font=ImageFont.truetype(FONT,96)
 b=font.getbbox(text);canvas=Image.new('L',(b[2]-b[0]+14,b[3]-b[1]+14),0)
 from PIL import ImageDraw
 d=ImageDraw.Draw(canvas);d.text((7-b[0],7-b[1]),text,font=font,fill=255)
 arr=np.asarray(canvas);cts,h=cv2.findContours((arr>150).astype(np.uint8),cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
 if h is None:return
 h=h[0];scale=min(width/arr.shape[1],targeth/arr.shape[0]); xoffset=cx-arr.shape[1]*scale/2; ytop=cy+arr.shape[0]*scale/2
 for i,c in enumerate(cts):
  if h[i][3]!=-1 or len(c)<3:continue
  exterior=[(xoffset+u[0]*scale,ytop-u[1]*scale)for (u,) in c.tolist()]
  holes=[];j=h[i][2]
  while j!=-1:
   if len(cts[j])>=3:holes.append([(xoffset+u[0]*scale,ytop-u[1]*scale)for (u,) in cts[j].tolist()])
   j=h[j][0]
  poly=Polygon(exterior,holes).buffer(0)
  if poly.area<.00001:continue
  # user-facing XY plane; custom prism from triangulation; thickness 0.025 along Z
  for p in ([poly] if poly.geom_type=='Polygon' else list(poly.geoms)):
   vv=[];ff=[]
   for t in triangulate(p):
    part=t.intersection(p)
    for pp in [part] if part.geom_type=='Polygon' else list(part.geoms) if part.geom_type=='MultiPolygon' else []:
     coords=list(pp.exterior.coords)[:-1]
     for m in range(1,len(coords)-1):
      b0=len(vv)
      vv.extend([(xy[0],xy[1],z-.025)for xy in [coords[0],coords[m],coords[m+1]]]);ff.append([b0,b0+1,b0+2])
   if ff:push(group,mat,mesh_triangles(vv,ff))
glyph_word('鐵路局',-.68,3.75,-2.407,1.68,.47)
glyph_word('苑裡站',1.30,3.75,-2.407,2.05,.47)
# stylish engraved railway sign on public approach x=-4.4
cube('14 Station identity','railNavy',(-5.35,2.30,-2.89),(.78,1.24,.12))
glyph_word('TRA',-5.35,2.68,-2.797,.55,.25,mat='offWhite')
glyph_word('入口',-5.35,2.25,-2.797,.55,.18,mat='offWhite')
# Station interior: visible service desk, ticket machines and turnstiles
cube('15 Lobby','woodPale',(4.9,1.06,-4.58),(2.3,.94,.64))
for x in [-2.2,-1.4,-.6,.2,.98]:
 cube('15 Lobby','metal',(x,.75,-4.72),(.25,1.13,.52))
 cube('15 Lobby','glassClear',(x,1.35,-4.72),(.35,.07,.56))
for x in [-5.5,-4.6]:
 cube('15 Lobby','railNavy',(x,1.20,-5.22),(.47,1.35,.24))
 cube('15 Lobby','glassAmber',(x,1.49,-5.08),(.37,.47,.032))
# Platform access: fully distinct staircase volume at west, elevator at east.
# Above deck y~6.3, elevator at x=+7.65,z=-4.20, enclosed visible glass, entirely within island.
ELEVATOR=box(6.80,-5.30,8.60,-3.58)
cube('16 Vertical circulation','glassClear',(7.65,3.21,-4.38),(1.84,6.18,1.65))
for x in [6.73,8.57]:
 for z in [-5.22,-3.52]:cube('16 Vertical circulation','metal',(x,3.25,z),(.09,6.42,.09))
for y in [2.00,4.0,6.30]:cube('16 Vertical circulation','metalLight',(7.65,y,-4.38),(1.98,.08,1.81))
cube('16 Vertical circulation','roofDark',(7.65,6.53,-4.38),(2.12,.19,1.95))
# short upper pedestrian connector x=+7.65, z=-5.6; structurally joins platform
cube('16 Vertical circulation','viaduct',(7.65,6.15,-5.58),(1.75,.20,.85))
# stairs at left on side land near rail, terrace from y0.1 to platform y6.3.
# parallel flights x=-8.1, z from -3.35 to -5.30; each step has actual treads.
STAIR=box(-9.15,-7.50,-6.90,-3.07)
# Switchback stairs: 2 x 16 risers, 0.192 world-unit rise, 0.25 tread;
# two 3.9-unit flights connected by upper/lower landings, not a fake vertical ladder.
for i in range(16):
 z1=-3.22-i*.25
 y1=.13+(i+.5)*3.08/16
 cube('16 Vertical circulation','plinth',(-8.46,y1,z1),(.83,.13,.25))
 z2=-6.97+i*.25
 y2=3.21+(i+.5)*3.08/16
 cube('16 Vertical circulation','plinth',(-7.30,y2,z2),(.83,.13,.25))
cube('16 Vertical circulation','plinth',(-7.88,3.18,-7.10),(2.00,.18,.56))
cube('16 Vertical circulation','viaduct',(-7.30,6.25,-3.13),(1.05,.17,.55))
for sx in [-8.93,-8.0,-7.72,-6.90]:
 beam('16 Vertical circulation','railFence',(sx,.2,-3.1),(sx,3.65,-7.2),.037,7)
cube('16 Vertical circulation','roofDark',(-7.95,6.72,-5.05),(2.27,.18,4.20))
# Side lobby-to-stair cantilever footbridge at y6.2
cube('16 Vertical circulation','viaduct',(-7.30,6.27,-5.35),(1.20,.17,3.90))
# Public site, grouped vegetation not scattered random circles; stay off protected spine and NPC reservations
PLANTERS=[(-3.36,6.20,1.68,1.23),(3.65,6.18,1.62,1.18),(-5.98,5.19,1.06,.75),(5.98,5.19,1.04,.75),(-6.90,3.77,1.15,.72),(6.85,3.77,1.15,.72)]
# NPC spaces x+-4.0 z4.15 => reserved 3x3: remove overlapping planters if any
NPC=[(-3.70,3.93),(3.65,3.93)]
NPC_POLYS=[box(x-1.5,z-1.5,x+1.5,z+1.5)for x,z in NPC]
PLANTERS=[pl for pl in PLANTERS if all(not box(pl[0]-pl[2]/2,pl[1]-pl[3]/2,pl[0]+pl[2]/2,pl[1]+pl[3]/2).intersects(p.buffer(.18))for p in NPC_POLYS)]
for i,(x,z,ww,dd) in enumerate(PLANTERS):
 p=box(x-ww/2,z-dd/2,x+ww/2,z+dd/2)
 if not site.buffer(-.18).covers(p):continue
 cube('17 Landscape','plinth',(x,.21,z),(ww,.24,dd))
 cube('17 Landscape','soil',(x,.36,z),(ww-.12,.08,dd-.12))
 rr=np.random.default_rng(i+12)
 for j in range(17):
  xx=x+rr.uniform(-ww*.41,ww*.41);zz=z+rr.uniform(-dd*.41,dd*.41)
  ball('17 Landscape',['leaf2','leaf','flower','blossom','plantDark'][j%5],xx,.44+rr.uniform(0,.1),zz,rr.uniform(.095,.18),0,(1,.84,1))
for i,(x,z,r,h) in enumerate([(-3.36,6.20,.82,3.65),(3.65,6.18,.84,3.68),(-6.80,3.78,.60,2.7),(6.80,3.78,.60,2.7)]):
 plant_tree(x,z,r,h,i+41)
# Benches for spectators; not placed in NPC reserved footprints
for x,z in [(-6.2,4.42),(6.2,4.44)]:
 cube('17 Landscape','wood',(x,.58,z),(1.26,.13,.41))
 cube('17 Landscape','wood',(x,.95,z+.16),(1.26,.55,.08))
 for dx in [-.48,.48]:cube('17 Landscape','metal',(x+dx,.28,z),(.065,.44,.065))
# Information stele on edge near left plaza, without NPC clearance interference
cube('18 Furnishing','railNavy',(-7.20,1.15,5.18),(.43,1.72,.16))
cube('18 Furnishing','glassAmber',(-7.2,1.25,5.28),(.34,1.12,.025))
for x,z in [(-6.0,6.0),(6.0,6.0),(-8.5,-9.8),(8.5,-9.8)]:
 beam('18 Furnishing','railTeal',(x,.2,z),(x,2.47,z),.037,8)
 cube('18 Furnishing','glassAmber',(x,2.45,z),(.28,.31,.28))
 cube('18 Furnishing','railNavy',(x,2.64,z),(.33,.06,.33))
# Floating edge safety barrier with four intentional ground-bridge mouths
edge=list(site.exterior.coords)
def ingress(pt):
 x,z=pt
 return (z>7.45 and abs(x)<4.4) or (x<-7.60 and abs(z)<2.85) or (x>7.60 and abs(z)<2.85)
for j,(a,b) in enumerate(zip(edge,edge[1:])):
 x=(a[0]+b[0])/2;z=(a[1]+b[1])/2
 if ingress((x,z)) or math.dist(a,b)<.025:continue
 for y in [.64,1.18]:beam('19 Island barrier','teal',(a[0],y,a[1]),(b[0],y,b[1]),.028,6)
 if j%4==0:beam('19 Island barrier','steel',(a[0],.06,a[1]),(a[0],1.19,a[1]),.04,6)
# Actual 3D spatial envelopes, physics validation not merely display claims.
SPECS.update({'design':'V8_高架交通驛站','roadLinkIDs':['S09','S10','S15','S18'],'worldUnits':'Sky Isles','playerHeight':1.5,'roadWidth':4.8,'siteOuterBoundsXZ':[round(v,3)for v in site.bounds], 'siteSizeWXZ':[round(SITE_W,2),round(SITE_D,2)],'siteArea':round(site.area,2), 'hallBoundsXZ':[-6.85,-5.79,6.85,-3.04],'viaductEnvelopeXYZ':[-9.45,0,-9.35,9.45,10.64,-5.06],'platformHeight':6.35,'deckUnderside':5.57,'maxTrainHeight':9.25,'platformCanopyTop':10.65, 'npcSquaresXZ':NPC})
# Full-footprint objects to check! elevated stuff never counts as ground obstacle.
OBSTACLES=[HALL,ELEVATOR,STAIR,box(-5.9,-3.22,-3.55,-2.88),box(3.55,-3.22,5.9,-2.88)]+[box(x-w/2,z-d/2,x+w/2,z+d/2)for x,z,w,d in PLANTERS]
# train supports at x+-7.65,z-8.79/-6.63, they do not obstruct main ground cross road
OBSTACLES.extend([box(x-.25,z-.27,x+.25,z+.27)for x,z in PIERS])
obs=unary_union(OBSTACLES)
SPECS['viaductFootprintInsideSite']=site.buffer(.001).covers(box(-9.45,-9.35,9.45,-5.98))
SPECS['hallInsideSite']=site.covers(HALL)
SPECS['stairInsideSite']=site.covers(STAIR)
SPECS['elevatorInsideSite']=site.covers(ELEVATOR)
SPECS['npcSquareClear']=[bool(site.buffer(-.40).contains(p) and obs.intersection(p).area<1e-6)for p in NPC_POLYS]
SPECS['piersBlockRoadSpine']=any(box(x-.25,z-.27,x+.25,z+.27).intersection(box(-9.5,-2.4,9.5,2.4)).area>0 for x,z in PIERS)
SPECS['clearanceUnderViaduct']=round(5.57-.07,2)
# Existing authoring coordinate foreign roads from true yuan-plan, approximated by densely sampled Bezier paths
EDGES={
'S05':[(-17.55,-19.656),(-16.146,-14.391),(-15.795,-3.51),(-12.285,-.702)],
'S08':[(-42.12,-1.404),(-31.59,-1.404),(-19.656,-1.404),(-12.285,-.702)],
'S11':[(15.093,.702),(29.133,1.404),(40.716,-.702),(44.226,6.318)],
'S02':[(-17.55,-19.656),(-3.159,-18.603),(12.987,-18.954),(26.676,-18.252)],
'S07':[(26.676,-18.252),(24.219,-11.934),(19.305,-5.967),(15.093,.702)]}
def bezier(p,t):
 p=np.array(p,float)
 return (1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t*t*p[2]+t*t*t*p[3]
other={k:LineString([tuple(bezier(p,t))for t in np.linspace(0,1,121)]).buffer(2.4,cap_style=2)for k,p in EDGES.items()}
SPECS['unrelatedRoadOverlapAreas']={k:round(site.intersection(v).area,4) for k,v in other.items()}
SPECS['familyIslandOverlapArea']=round(site.intersection(Point(-17.55,-19.656).buffer(10.2)).area,4)
# Full ground clearance path grid with 0.36 player diameter radius; 8-neighbor; sampled destinations are entrance zones
safe=site.buffer(-.38).difference(obs.buffer(.34))
RES=.14;xs=np.arange(site.bounds[0],site.bounds[2]+RES,RES);zs=np.arange(site.bounds[1],site.bounds[3]+RES,RES)
pr=prep(safe)
mask=np.zeros((len(zs),len(xs)),dtype=bool)
for i,z in enumerate(zs):
 for j,x in enumerate(xs):mask[i,j]=pr.contains(Point(float(x),float(z)))
labels,number=label(mask,structure=np.ones((3,3),int))
def labelof(x,z):return int(labels[np.argmin(abs(zs-z)),np.argmin(abs(xs-x))])
nav={
 'S09 west':(-7.95,0),'S10 east':(7.95,0),
 'S15 north':(-1.6,7.15),'S18 north':(1.6,7.15),
 'spawn':(0,3.5),'lobby':(0,-2.65),'npcWest':NPC[0],'npcEast':NPC[1],
 'elevator':(7.55,-2.80),'stairs':(-7.55,-2.30)}
SPECS['groundNavComponents']={k:labelof(*p)for k,p in nav.items()}
SPECS['groundNavConnected']=len(set(SPECS['groundNavComponents'].values()))==1 and 0 not in SPECS['groundNavComponents'].values()
SPECS['groundSolidFootprintIntersectMainRoadSpine']=round(obs.intersection(box(-8,-2.4,8,2.4)).area,4)
SPECS['notes']='Full Three.js camera / collider / shader / mobile performance NOT verified; elevated platform accessibility is represented in geometry but not runtime navmesh.'
# Architecture height retuned to retain train-car human-scale and proper platform clearance,
# *while* fitting the existing dist16/pitch.60 spawn viewpoint. A piecewise vertical
# redesign preserves the actual 2.1-unit-tall coach, not a uniform squashed train.
def remap_y(y):
 if y <= 0:return y
 if y <= 6.35:return y*(3.75/6.35)
 if y <= 9.30:return 3.75+(y-6.35)*(2.50/(9.30-6.35))
 return 6.25+(y-9.30)*.40
for (group,material),parts in GEOMS.items():
 for mesh in parts:
  yy=mesh.vertices[:,1].copy()
  mesh.vertices[:,1]=np.array([remap_y(float(t)) for t in yy])
for key in ['platformHeight','deckUnderside','maxTrainHeight','platformCanopyTop','clearanceUnderViaduct']:
 SPECS[key]=round(remap_y(SPECS[key]),3)
SPECS['architecturalHeightRevision']='Piecewise human-scale elevation: deck 3.75, coach 2.08, canopy below 6.9; coordinates in exported GLB are actual revisions.'
SPECS['cameraFramingNotes']='Camera perspective mock-ups use desktop dist16, pitch .60, fov55 and mobile dist22, pitch .67, fov58 aimed at original player spawn. Verify actual game orbit separately.'
# batched consistent trimesh glTF scene with semantic group names
# =============================================================================
SCENE=trimesh.Scene(); material_faces={};mesh_stats={}
for (group,mat),parts in GEOMS.items():
 try:m=trimesh.util.concatenate(parts)
 except Exception as e:
  print('concat error',group,mat,e);continue
 color=tuple(int(COLORS[mat][i:i+2],16)for i in (1,3,5))+((165,) if mat in ('glass','glassClear','lightGlass','trainGlass') else (255,))
 m.visual.vertex_colors=np.tile(np.array(color,dtype=np.uint8),(len(m.vertices),1))
 SCENE.add_geometry(m,node_name=f'{group}::{mat}',geom_name=f'{group}::{mat}')
 mesh_stats[f'{group}::{mat}']={'triangles':len(m.faces),'parts':len(parts)}
# Export preserving categories per scene node
out_glb=ROOT/'F_elevated_station_v8_design.glb'
out_glb.write_bytes(trimesh.exchange.gltf.export_glb(SCENE))
SPECS['meshTrianglesTotal']=int(sum(q['triangles']for q in mesh_stats.values()))
SPECS['glbBytes']=out_glb.stat().st_size
# =============================================================================
# VTK render, same meshes / same coords
# =============================================================================
ren=vtk.vtkRenderer();ren.GradientBackgroundOn();ren.SetBackground(.895,.925,.951);ren.SetBackground2(.984,.99,.992)
for (group,mat),parts in GEOMS.items():
 mesh=trimesh.util.concatenate(parts)
 # triangle array
 pts=np.asarray(mesh.vertices,dtype=np.float32)
 faces=np.hstack([np.full((len(mesh.faces),1),3),mesh.faces]).astype(np.int64)
 pdata=vtk.vtkPolyData();vtkPts=vtk.vtkPoints();vtkPts.SetData(numpy_to_vtk(pts,deep=True));pdata.SetPoints(vtkPts)
 cell=vtk.vtkCellArray();cell.SetCells(len(mesh.faces),numpy_to_vtkIdTypeArray(faces.ravel(),deep=True));pdata.SetPolys(cell)
 mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(pdata)
 act=vtk.vtkActor();act.SetMapper(mapper)
 col=COLORS[mat];rgb=[int(col[i:i+2],16)/255 for i in (1,3,5)];act.GetProperty().SetColor(*rgb)
 act.GetProperty().SetAmbient(.32);act.GetProperty().SetDiffuse(.79);act.GetProperty().SetSpecular(.21);act.GetProperty().SetSpecularPower(26)
 if mat in ('glass','glassClear','trainGlass'):act.GetProperty().SetOpacity(.74 if mat=='glassClear' else .88)
 ren.AddActor(act)
# light and shadows approximation with broad diffused source
L=vtk.vtkLight();L.SetPosition(-18,36,24);L.SetFocalPoint(0,0,0);L.SetIntensity(1.0);L.SetColor(1.0,.94,.87);ren.AddLight(L)
L2=vtk.vtkLight();L2.SetPosition(22,28,-30);L2.SetIntensity(.56);L2.SetColor(.78,.88,1.0);ren.AddLight(L2)
base=vtk.vtkRenderStepsPass();ao=vtk.vtkSSAOPass();ao.SetDelegatePass(base);ao.SetRadius(.82);ao.SetBias(.025);ao.SetKernelSize(48);ao.SetBlur(True);ren.SetPass(ao)
w=vtk.vtkRenderWindow();w.AddRenderer(ren);w.SetOffScreenRendering(1);w.SetMultiSamples(4)
cam=ren.GetActiveCamera()

def render(name,position,focus=(0,1.6,-1.7),up=(0,1,0),parallel=True,scale=15.5,size=(1450,1080),angle=55):
 w.SetSize(*size);cam.SetFocalPoint(*focus);cam.SetPosition(*position);cam.SetViewUp(*up)
 cam.SetParallelProjection(bool(parallel));cam.SetParallelScale(float(scale));cam.SetViewAngle(angle)
 ren.ResetCameraClippingRange();w.Render()
 flt=vtk.vtkWindowToImageFilter();flt.SetInput(w);flt.ReadFrontBufferOff();flt.Update()
 filename=VIEWS/(name+'.png');writer=vtk.vtkPNGWriter();writer.SetInputConnection(flt.GetOutputPort());writer.SetFileName(str(filename));writer.Write()
 return filename


if __name__=='__main__':
 print('VALIDATION',json.dumps(SPECS,ensure_ascii=False,indent=2))
 render('01_hero',(31,23,33),focus=(0,4.9,-2.3),scale=14.2,size=(1700,1280))
 render('02_front',(0,13,42),focus=(0,4.2,-2.4),scale=11.9,size=(1400,970))
 render('03_rear',(0,13,-45),focus=(0,4.2,-2.4),scale=11.9,size=(1400,970))
 render('04_left',(-42,13,0),focus=(0,4.2,-2.3),scale=12.4,size=(1400,970))
 render('05_right',(42,13,0),focus=(0,4.2,-2.3),scale=12.4,size=(1400,970))
 render('06_top',(0,51,-1.3),focus=(0,0,-1.3),up=(0,0,1),scale=13.3,size=(1360,1360))
 render('07_player_desktop',(2.1,10.24,16.5),focus=(0,1.2,3.5),parallel=False,size=(1500,900),angle=55)
 render('08_player_mobile',(2.1,14.86,20.73),focus=(0,1.2,3.5),parallel=False,size=(900,1450),angle=58)
 render('09_high_rail',(36,23,-28),focus=(0,5.5,-5.7),scale=14.2,size=(1700,1280))
 (ROOT/'V8_工程檢核.json').write_text(json.dumps(SPECS,ensure_ascii=False,indent=2),encoding='utf-8')
 # design presentation, one origin for every view
 fontfile='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
 fontbold='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
 f=lambda size,bold=False:ImageFont.truetype(fontbold if bold and Path(fontbold).exists() else fontfile,size)
 from PIL import ImageDraw,ImageOps
 def picture(fpath,size,contain=False):
  im=Image.open(VIEWS/fpath).convert('RGB'); iw,ih=im.size;w,h=size
  fac=(min if contain else max)(w/iw,h/ih);im=im.resize((int(iw*fac),int(ih*fac)),Image.Resampling.LANCZOS)
  if contain:
   bg=Image.new('RGB',(w,h),'#F4F6F5');bg.paste(im,((w-im.width)//2,(h-im.height)//2));return bg
  xx=(im.width-w)//2;yy=(im.height-h)//2;return im.crop((xx,yy,xx+w,yy+h))
 BOARD=Image.new('RGB',(2400,3380),'#F4F6F5');d=ImageDraw.Draw(BOARD)
 d.text((90,48),'交通大升級｜高架鐵路交通驛站',font=f(64,True),fill='#213944')
 d.text((90,132),'V8 · SAME-SOURCE 3D DESIGN / NOT A COMPOSITE OF AI VIEWS',font=f(27),fill='#52727B')
 def cell(name,x,y,w,h,title):
  BOARD.paste(picture(name+'.png',(w,h),contain=(name=='06_top')),(x,y));d.text((x+15,y+h+12),title,font=f(30,True),fill='#2A444C')
 cell('01_hero',90,230,2220,1030,'01  45°主視圖  ·  車站入口 + 上層月台')
 for row,pics in enumerate([['02_front','03_rear'],['04_left','05_right'],['06_top','07_player_desktop']]):
  yy=1340+row*630
  for j,key in enumerate(pics):cell(key,90+j*1130,yy,1090,525,{'02_front':'正面','03_rear':'背面','04_left':'左側','05_right':'右側','06_top':'屋頂俯視','07_player_desktop':'玩家桌機透視'}[key])
 BOARD.save(ROOT/'交通大升級_V8_高架車站_同源六視圖.png')
 # plan — footprint and connection visualization: no false scale
 from PIL import ImageDraw
 MAP=Image.new('RGB',(1550,1700),'#F8FAFB');m=ImageDraw.Draw(MAP)
 m.text((65,48),'V8 | 高架交通島真實尺度與橋口',font=f(53,True),fill='#28444D')
 m.text((65,126),'GLB 同一座標系 | 單位：Sky Isles 世界單位 | 玩家高 1.5',font=f(25),fill='#506E76')
 scale=54;ox=775;oz=870
 xy=lambda x,z:(int(ox+x*scale),int(oz-z*scale))
 def drawpoly(p,fill,line='#A1A8AA',thick=3):
  m.polygon([xy(x,z)for x,z in p.exterior.coords],fill=fill)
  m.line([xy(x,z)for x,z in p.exterior.coords],fill=line,width=thick,joint='curve')
 drawpoly(site,'#E6DFD2')
 for k,p in other.items():
  part=p.intersection(box(-20,-16,20,12))
  if not part.is_empty and part.geom_type=='Polygon':drawpoly(part,'#DEDFDF',line='#BBBBBB',thick=1)
 drawpoly(HALL,'#E0B979',line='#996438')
 drawpoly(ELEVATOR,'#9BCED3',line='#2B7880')
 drawpoly(STAIR,'#CEB4D1',line='#8A6192')
 drawpoly(box(-9.45,-9.35,9.45,-5.98),'#9FAEB7',line='#405E6E',thick=4)
 drawpoly(box(-7.15,-9.17,7.15,-7.55),'#6F9FAC',line='#254F62',thick=3)
 for x,z in PIERS:
  xx,zz=xy(x,z);m.ellipse((xx-9,zz-9,xx+9,zz+9),fill='#6E7677',outline='white',width=2)
 for p in NPC_POLYS:drawpoly(p,'#C6E3CC',line='#458E66')
 for label,(x,z) in nav.items():
  xx,yy=xy(x,z)
  if label.startswith('S') or label=='spawn':
   m.ellipse((xx-8,yy-8,xx+8,yy+8),fill='#D68740',outline='#FFFFFF',width=2)
   m.text((xx+10,yy-15),label,font=f(19,True),fill='#4F5F64')
 # obvious drawn border of ground passable region
 m.text((60,1500),f'島台外接 {SITE_W:.2f} × {SITE_D:.2f}   |   上層月台 y≈6.35',font=f(30,True),fill='#2A434F')
 m.text((60,1550),'沙色=島台  金色=站房  藍灰=高架   淡青=電梯  淡紫=樓梯  綠色=NPC',font=f(22),fill='#4D6469')
 m.text((60,1595),'注意：高架為上空結構；此平面圖不代表高架在地面不可走。',font=f(22),fill='#785C45')
 MAP.save(ROOT/'交通大升級_V8_真實尺度與橋口.png')
