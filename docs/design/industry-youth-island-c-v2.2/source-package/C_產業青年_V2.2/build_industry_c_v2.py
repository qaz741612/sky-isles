"""C 產業青年島 architectural design V2 — authored editable geometry, one source for all views.
Coordinates are C-island local x,z; y up. This is a design source, not game collision.
"""
import os, math, random, json, copy
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, LineString, MultiPolygon, GeometryCollection
from shapely.ops import triangulate, unary_union
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT=os.path.dirname(os.path.abspath(__file__))
rng=random.Random(321041)
COL={
 'cliff_dark':(71,80,92), 'cliff_mid':(105,110,110), 'cliff_light':(162,152,135),
 'stone_cream':(218,206,183),'stone_bright':(237,222,192),'terrace':(199,178,146),
 'grass':(115,156,116),'grass_light':(143,172,124),'moss':(81,122,97),
 'path':(217,204,177),'paver':(188,175,150),'paver_dark':(133,132,125),
 'warmbrick':(159,104,74),'bricklight':(193,145,106),'wood':(153,101,61),'woodlight':(217,164,100),
 'steel':(59,90,98),'steel_light':(112,142,148),'roof':(73,93,101), 'roof_light':(137,164,164),
 'solar':(35,63,81),'solar_hi':(79,127,148),'glass':(94,170,177,160), 'glass_light':(169,222,218,145),
 'glass_shadow':(68,133,147,135),'water':(69,148,163,225),'waterlight':(123,199,205),
 'plant_pine':(48,94,75),'plant_bush':(68,114,83),'plant_leaf':(101,151,98),
 'plant_yellow':(181,167,79),'plant_pink':(220,149,159),'flower':(228,178,122),
 'white':(240,237,218),'cream':(228,221,192),'soil':(119,106,82),
 'rust':(157,98,59),'light':(248,216,142), 'mushroom':(166,140,206),
}
MATERIALS={}
def rgba(k):
 c=COL[k] if isinstance(k,str) else k
 return tuple(c)+(255,) if len(c)==3 else tuple(c)
class Author:
 def __init__(self): self.parts=[];self.counts={};self.objects=[]
 def add(self,mesh,mat,name):
  if mesh is None or len(mesh.faces)==0:return
  mesh=mesh.copy();mesh.visual=trimesh.visual.ColorVisuals(mesh,vertex_colors=np.tile(np.array(rgba(mat),dtype=np.uint8),(len(mesh.vertices),1)))
  self.parts.append((mesh,mat,name));self.objects.append({'name':name,'material':mat,'triangles':len(mesh.faces)})
  self.counts[mat]=self.counts.get(mat,0)+len(mesh.faces)
 def box(self,ctr,size,mat,name='box',angle=0):
  m=trimesh.creation.box(extents=size)
  if angle: m.apply_transform(trimesh.transformations.rotation_matrix(angle,[0,1,0]))
  m.apply_translation(ctr);self.add(m,mat,name)
 def sphere(self,ctr,radius,mat,name='sphere',sub=1,scale=None):
  m=trimesh.creation.icosphere(subdivisions=sub,radius=radius)
  if scale is not None:m.apply_scale(scale)
  m.apply_translation(ctr);self.add(m,mat,name)
 def cyl(self,ctr,r,depth,mat,name='cyl',sections=12,r0=None):
  m=trimesh.creation.cone(r,depth,sections=sections) if r0 is None else trimesh.creation.cylinder(radius=r,height=depth,sections=sections)
  m.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0])); m.apply_translation(ctr)
  self.add(m,mat,name)
 def cone(self,ctr,r,h,mat,name='cone',sections=9):
  m=trimesh.creation.cone(radius=r,height=h,sections=sections)
  m.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0]));m.apply_translation(ctr);self.add(m,mat,name)
 def rod(self,a,b,rad,mat,name='rod',sections=7):
  av=np.array(a,float);bv=np.array(b,float);v=bv-av;length=np.linalg.norm(v)
  if length<1e-5:return
  m=trimesh.creation.cylinder(radius=rad,height=length,sections=sections)
  rot=trimesh.geometry.align_vectors([0,0,1],v/length)
  m.apply_transform(rot);m.apply_translation((av+bv)/2)
  self.add(m,mat,name)
 def quad(self,verts,mat,name='panel',double=False):
  vs=np.array(verts,float);fs=np.array([[0,1,2],[0,2,3]] + ([[2,1,0],[3,2,0]] if double else []))
  self.add(trimesh.Trimesh(vertices=vs,faces=fs,process=False),mat,name)
 def polygon(self,shape,y0,y1,mat,name='polygon'):
  if isinstance(shape,Polygon):polys=[shape]
  elif isinstance(shape,MultiPolygon):polys=list(shape.geoms)
  elif isinstance(shape,(tuple,list)):polys=[Polygon(shape)]
  else:return
  vs=[];fs=[]
  for p in polys:
   if p.is_empty or p.area<.001:continue
   raw=[]
   for tri in triangulate(p):
    inter=tri.intersection(p)
    if isinstance(inter,Polygon) and inter.area>1e-6:
     if len(inter.interiors):continue
     coords=list(inter.exterior.coords)[:-1]
     if len(coords)==3:raw.append(coords)
     else:
      for tt in triangulate(inter):
       if inter.covers(tt.representative_point()): raw.append(list(tt.exterior.coords)[:-1])
    elif isinstance(inter,MultiPolygon):
     for gg in inter.geoms:
      for tt in triangulate(gg):
       if gg.covers(tt.representative_point()):raw.append(list(tt.exterior.coords)[:-1])
   for tri in raw:
    if len(tri)!=3:continue
    i=len(vs);vs.extend([[x,y1,z] for x,z in tri]);fs.append([i,i+1,i+2]);
    if y1-y0>.005:
     i=len(vs);vs.extend([[x,y0,z] for x,z in tri]);fs.append([i,i+2,i+1]);
   if y1-y0>.005:
    for ring in [p.exterior,*p.interiors]:
     coords=list(ring.coords)
     for a,b in zip(coords,coords[1:]):
      i=len(vs);vs.extend([[a[0],y0,a[1]],[b[0],y0,b[1]],[b[0],y1,b[1]],[a[0],y1,a[1]]]);fs.extend([[i,i+1,i+2],[i,i+2,i+3]])
  if vs:self.add(trimesh.Trimesh(vertices=np.array(vs),faces=np.array(fs),process=False),mat,name)
 def ribbon(self,points,width,y0,y1,mat,name='ribbon'):
  self.polygon(LineString(points).buffer(width/2,cap_style=2,join_style=1,resolution=5),y0,y1,mat,name)
 def export(self,path,exclude_names=()):
  sc=trimesh.Scene()
  buckets={}
  for m,mat,name in self.parts:
   if any(name.startswith(pre) for pre in exclude_names):continue
   buckets.setdefault(mat,[]).append(m)
  for mat,lst in buckets.items():
   mesh=trimesh.util.concatenate(lst)
   col=rgba(mat)
   mesh.visual.material=trimesh.visual.material.PBRMaterial(name=mat,baseColorFactor=list(col),roughnessFactor=(.19 if 'steel' in mat else (.34 if mat.startswith('glass') else .8)),metallicFactor=.6 if mat in ['steel','steel_light','roof'] else 0,alphaMode='BLEND' if len(col)==4 and col[3]<255 else 'OPAQUE',doubleSided=True)
   sc.add_geometry(mesh,geom_name=mat,node_name=mat)
  sc.export(path,file_type='glb')
  return sc
scene=Author()

# --- TERRAIN: compact asymmetric 29x26 island with multi-layered cantilever rock shell ---
N=96
angles=np.arange(N)*2*math.pi/N
shape=[]
for t in angles:
 warp=1+0.065*math.sin(3*t+.3)+.042*math.sin(5*t-.8)+.022*math.cos(9*t)
 shape.append((14.28*math.cos(t)*warp,12.7*math.sin(t)*warp))
foot=Polygon(shape)
scene.polygon(foot,-.35,-.10,'grass','landscape-turf')
# layered basal cliff mesh with deterministic angular strata
rings=[]
for y,s,seed in [(-.35,1,0),(-1.02,.977,.028),(-2.03,.94,.055),(-3.12,.80,.08),(-4.35,.66,.12),(-5.45,.43,.13),(-6.28,.10,.08)]:
 pts=[]
 for i,(x,z) in enumerate(shape):
  t=angles[i];v=1+seed*(math.sin(13*t+1)+.4*math.cos(23*t+.4))
  pts.append((x*s*v,y+(.12*math.sin(9*t) if y<-1 else 0),z*s*v))
 rings.append(pts)
for k in range(len(rings)-1):
 verts=[];faces=[]
 for i in range(N):
  i2=(i+1)%N;v=len(verts);verts.extend([rings[k][i],rings[k][i2],rings[k+1][i2],rings[k+1][i]])
  faces.extend([[v,v+1,v+2],[v,v+2,v+3]])
 scene.add(trimesh.Trimesh(vertices=verts,faces=faces,process=False),['stone_cream','cliff_light','cliff_mid','cliff_mid','cliff_dark','cliff_dark'][k],f'floating-rock-layer-{k+1}')
for q in range(48):
 t=q*2*math.pi/48;xx=13.9*math.cos(t)*(.95+.07*rng.random());zz=12.1*math.sin(t)*(.94+.05*rng.random());yy=-.65-1.7*rng.random();rad=rng.uniform(.19,.7)
 scene.sphere([xx,yy,zz],rad,['cliff_light','cliff_mid','cliff_dark'][q%3],f'cliff-scree-{q}',1,scale=[1,.65,1])

# Foliage green terraces skirt main circulation; raised garden contours
scene.polygon(Point(-9.6,-7.4).buffer(2.7,resolution=16).intersection(foot),-.06,.13,'grass_light','NW-grass-terrace')
scene.polygon(Point(-8.2,7.2).buffer(2.9,resolution=16).intersection(foot),-.06,.1,'grass_light','SW-garden-terrace')
scene.polygon(Point(9.2,-7.2).buffer(2.7,resolution=16).intersection(foot),-.06,.15,'grass_light','NE-landscape-terrace')
# show three accurate existing 4.8-unit route corridors; local entrance positions from preflight
ports={'S14':(-6.525,-6.123),'S15':(5.659,-6.989),'S16':(-5.115,7.349)}
centre=(0,0)
# Exact existing PR#15 cubic controls in WORLD XZ, sampled around the C island;
# unlike the previous sketch this preserves the approved Bezier centerline.
WORLD_C=(-20.358,38.610)
EDGE_CONTROLS={
 'S14':[(-42.12,-1.404),(-44.577,10.881),(-34.047,27.027),(-20.358,38.61)],
 'S15':[(0,0),(-1.404,14.04),(-10.53,27.027),(-20.358,38.61)],
 'S16':[(-20.358,38.61),(-33.345,55.458),(-35.802,71.253),(-53.352,87.048)],
}
network=[];road_centerlines={}
for ident,pts in EDGE_CONTROLS.items():
 local=[]
 for j in range(641):
  t=j/640;u=1-t
  x=u**3*pts[0][0]+3*u*u*t*pts[1][0]+3*u*t*t*pts[2][0]+t**3*pts[3][0]-WORLD_C[0]
  z=u**3*pts[0][1]+3*u*u*t*pts[1][1]+3*u*t*t*pts[2][1]+t**3*pts[3][1]-WORLD_C[1]
  if math.hypot(x,z)<21:local.append((x,z))
 road_centerlines[ident]=local
 network.append((local,4.8))
roads=[LineString(route).buffer(w/2,cap_style=2,join_style=1,resolution=7) for route,w in network]
core=unary_union(roads)
# polished sandstone walkway base with double limestone edge; thin thickness
scene.polygon(core.intersection(foot),-.065,.045,'stone_cream','three-road-structural-core')
for route,w in network:
 scene.polygon(LineString(route).buffer((w-.34)/2,cap_style=2,join_style=1,resolution=7).intersection(foot),.045,.074,'path','public-path')
# Bridge transitions installed after defining sculpted island ground; maintain actual 4.8-width corridor
# public architectural plaza to west central, away from east built structures
plaza=Point(-1.0,1.1).buffer(4.9,resolution=32)
plaza=plaza.intersection(foot)
scene.polygon(plaza,-.04,.085,'stone_bright','main-plaza')
scene.polygon(Point(-1.,1.1).buffer(4.35,resolution=32).difference(Point(-1,1.1).buffer(3.95,resolution=32)).intersection(plaza),.08,.12,'terrace','plaza-inlay-ring')
# center promenade inlays (radial seams subtle)
for i in range(24):
 theta=i*math.pi/12;x=-1+4.6*math.cos(theta);z=1.1+4.6*math.sin(theta)
 scene.box([x,.13,z],[.22,.035,.14],'paver_dark',f'plaza-paver-{i}',theta)
# Designed civic plaza floor: concentric limestone + sunburst inlay, entirely flush.
# This gives visual cadence without putting obstacles on the 4.8-unit walkable core.
scene.polygon(Point(-1.,1.1).buffer(2.12,resolution=36).difference(Point(-1.,1.1).buffer(1.98,resolution=36)),.082,.108,'terrace','plaza-inner-limestone-inlay')
scene.polygon(Point(-1.,1.1).buffer(.74,resolution=24),.09,.112,'paver','plaza-centre-copper-medallion')
scene.polygon(Point(-1.,1.1).buffer(.62,resolution=24).difference(Point(-1.,1.1).buffer(.51,resolution=24)),.111,.139,'rust','plaza-medallion-rim')
for k in range(16):
 t=(k+.5)*math.tau/16
 x0,z0=-1+2.35*math.cos(t),1.1+2.35*math.sin(t)
 x1,z1=-1+4.15*math.cos(t),1.1+4.15*math.sin(t)
 scene.ribbon([(x0,z0),(x1,z1)],.044,.091,.103,'paver_dark','plaza-radial-paving-joint')
for k in range(8):
 t=k*math.tau/8
 x0,z0=-1+.26*math.cos(t),1.1+.26*math.sin(t)
 x1,z1=-1+.54*math.cos(t),1.1+.54*math.sin(t)
 scene.ribbon([(x0,z0),(x1,z1)],.07,.12,.141,'woodlight','plaza-inner-motif')

# main building footprint: authoritative geometry group is shifted +0.85 X below
workshop_start=len(scene.parts)
# elegant stepped entry terrace and low plinth
scene.box([8.36,.14,1.0],[7.35,.38,6.25],'terrace','factory-limestone-podium')
scene.box([4.49,.07,1.0],[.42,.13,6.25],'stone_bright','factory-forecourt-step')
# workshop brick foundation, segmented facade glazing
scene.box([8.10,1.78,1.0],[7.48,3.5,6.05],'warmbrick','factory-masonry-shell')
# vertical structure west facade x=4.24: glass bands between timber posts, x inset
for z in np.arange(-1.65,3.7,1.0):
 scene.box([4.225,2.18,z],[.06,2.45,.86],'glass','factory-west-glazing')
for z in np.arange(-2.0,4.05,1.02):
 if core.buffer(.16).covers(Point(4.14,z)):continue
 scene.box([4.14,1.8,z],[.19,3.7,.14],'woodlight','factory-post-west')
scene.box([4.14,3.48,1.03],[.22,.18,6.3],'steel','factory-lintel')
scene.box([4.09,.67,.25],[.08,1.75,1.9],'glass_shadow','factory-main-glass-doors')
# brick east and south/north glazing + mullions
for side in [-1,1]:
 z=1+side*3.02
 for xx in [5.3,6.65,8.,9.35,10.7]:
  scene.box([xx,2.25,z],[.93,1.95,.09],'glass_shadow','side-glazing')
  scene.box([xx+.46,2.25,z],[.07,2.2,.13],'woodlight','side-mullion')
 scene.box([8.1,3.35,z],[7.8,.18,.14],'roof','side-top-trim')
# eastern upper lights and support nodes
for z in np.arange(-1.8,3.85,1.2):
 scene.box([11.9,2.2,z],[.065,1.85,.78],'glass_shadow','rear-workshop-glazing')
 scene.box([11.96,1.75,z+.42],[.14,3.5,.09],'wood','rear-workshop-column')
# 3 visible industrial sawteeth across Z, detailed roof sections
z_start=-2.05;module=2.02
for n in range(3):
 z0=z_start+n*module;z1=z0+module
 ylow=3.65;yhi=5.05
 # seam tooth: lower at north, high at south (vertical glazing riser)
 scene.quad([[4.03,ylow,z0],[12.14,ylow,z0],[12.14,yhi,z1],[4.03,yhi,z1]],'roof',f'sawtooth-zinc-roof-{n}')
 scene.quad([[4.06,ylow+.02,z0],[4.06,yhi+.02,z1],[12.13,yhi+.02,z1],[12.13,ylow+.02,z0]],'roof_light',f'roof-top-reflection-{n}')
 # sharp steel roof ridge and deep fascia ends
 scene.rod([4.0,yhi,z1],[12.2,yhi,z1],.09,'woodlight',f'sawtooth-ridge-{n}')
 scene.rod([4.0,ylow,z0],[12.2,ylow,z0],.08,'steel',f'sawtooth-eave-{n}')
 for x in [4.05,12.14]:scene.rod([x,ylow,z0],[x,yhi,z1],.095,'wood',f'roof-end-beam-{n}')
 # characteristic north-facing vertical clerestory in the raised edge
 if n<2:
  scene.quad([[4.14,3.67,z1+.022],[12.04,3.67,z1+.022],[12.04,5.03,z1+.022],[4.14,5.03,z1+.022]],'glass_light','clerestory-panel')
  for x in [4.15,6.1,8.1,10.1,12.05]:scene.rod([x,3.66,z1+.04],[x,5.04,z1+.04],.05,'steel','clerestory-post')
 # 2x3 luminous photovoltaic strips on roof
 for xx in [6.0,8.0,10.0]:
  aa=np.interp(.16,[0,1],[ylow,yhi]);bb=np.interp(.68,[0,1],[ylow,yhi]);
  za=z0+module*.16;zb=z0+module*.68
  scene.quad([[xx-.74,aa+.065,za],[xx+.74,aa+.065,za],[xx+.74,bb+.065,zb],[xx-.74,bb+.065,zb]],'solar',f'PV-panel-{n}')
  scene.rod([xx-.74,aa+.067,za],[xx-.74,bb+.067,zb],.025,'solar_hi','PV-glint-edge')
# entrance translucent timber canopy and fluted wall
scene.box([3.78,2.62,.2],[1.60,.16,2.85],'woodlight','cantilever-timber-entry-canopy')
for z in [-.9,-.5,.4,.8,1.3]:scene.box([3.69,2.45,z],[1.58,.07,.07],'wood','canopy-ribs')
# factory iconic glowing vertical technology louvers
for z in [-1.6,-1.22,1.45,1.85,2.3,2.72,3.1]:scene.box([4.025,1.76,z],[.11,2.6,.07],'woodlight','factory-front-timber-fins')
# Industrial paved forecourt fixtures and interior equipment
for z in [-1.3,1.9]:scene.box([3.92,.25,z],[.56,.25,.88],'paver','entry-planter-plinth')
for xx,zz in [(6.2,-.5),(8.6,.65),(10.2,2.2)]:
 scene.box([xx,.58,zz],[.88,.82,.62],'steel_light','workshop-machine')
 scene.box([xx,.99,zz],[.57,.2,.47],'solar','machine-top')
for z in np.arange(-1.4,3.8,1.35):
 scene.rod([5.35,3.45,z],[11.5,3.45,z],.058,'steel','interior-ceiling-rail')
# exterior tall display vertical sign and wood base, no fake image labels
scene.box([3.43,2.15,2.6],[.27,3.72,.94],'steel','factory-identity-pylon')
scene.box([3.28,2.25,2.6],[.10,2.95,.67],'stone_bright','factory-identity-panel')
for y in [1.45,1.95,2.45,2.95]:scene.box([3.205,y,2.6],[.11,.075,.46],'rust','identity-line-design')

workshop_end=len(scene.parts)
# --- GREENHOUSE EAST/SOUTH: steel trusses, glass, real vegetation rows ---
gcx,gcz=7.0,7.04;gw,gd=5.35,3.55
scene.box([gcx,.20,gcz],[gw+.35,.43,gd+.32],'stone_cream','greenhouse-foundation')
scene.box([gcx,.48,gcz],[gw-.35,.12,gd-.36],'soil','greenhouse-floor')
# lower glass walls transparent
for zz in [gcz-gd/2,gcz+gd/2]:
 scene.quad([[gcx-gw/2,.42,zz],[gcx+gw/2,.42,zz],[gcx+gw/2,2.5,zz],[gcx-gw/2,2.5,zz]],'glass_light','greenhouse-front-glass')
for xx in [gcx-gw/2,gcx+gw/2]:
 scene.quad([[xx,.42,gcz-gd/2],[xx,.42,gcz+gd/2],[xx,2.5,gcz+gd/2],[xx,2.5,gcz-gd/2]],'glass','greenhouse-side-glass')
# arc barrel roof in 12 curving bands, 7 ribs along x
for ii in range(7):
 xx=gcx-gw/2+ii*gw/6
 for kk in range(12):
  t0=math.pi*kk/12;t1=math.pi*(kk+1)/12
  p0=[xx,2.45+1.24*math.sin(t0),gcz-1.77*math.cos(t0)]
  p1=[xx,2.45+1.24*math.sin(t1),gcz-1.77*math.cos(t1)]
  scene.rod(p0,p1,.055,'steel_light','greenhouse-arched-truss',8)
 if ii>0:
  x1=xx-gw/6
  for kk in range(12):
   t0=math.pi*kk/12;t1=math.pi*(kk+1)/12
   qa=[x1,2.45+1.24*math.sin(t0),gcz-1.77*math.cos(t0)]
   qb=[xx,qa[1],qa[2]]
   qc=[xx,2.45+1.24*math.sin(t1),gcz-1.77*math.cos(t1)]
   qd=[x1,qc[1],qc[2]]
   scene.quad([qa,qb,qc,qd],'glass_light','curved-glass-panel')
for zz in [gcz-gd/2,gcz+gd/2]:
 for xx in np.linspace(gcx-gw/2,gcx+gw/2,7):scene.rod([xx,.48,zz],[xx,2.48,zz],.052,'steel','greenhouse-corner-frame')
# greenhouse working aisle plants on both sides
for xx in np.linspace(gcx-2.2,gcx+2.1,5):
 for z in [gcz-.72,gcz+.70]:
  scene.box([xx,.69,z],[.78,.45,.66],'wood','greenhouse-raised-bed')
  scene.box([xx,.95,z],[.66,.07,.56],'soil','greenhouse-planter-soil')
  for kk in range(3):
   dx=(kk-1)*.18
   scene.rod([xx+dx,.98,z],[xx+dx,1.38+rng.random()*.3,z],.035,'plant_bush','lettuce-stem')
   scene.sphere([xx+dx,1.40,z],.19,'plant_leaf','leaflet',1,scale=[1,.55,.8])
# greenhouse glass door on west facade
scene.box([gcx-gw/2-.02,1.37,gcz],[.055,1.82,.98],'glass_shadow','greenhouse-entrance')
for zz in [gcz-.52,gcz+.52]:scene.rod([gcx-gw/2-.11,.43,zz],[gcx-gw/2-.11,2.48,zz],.057,'steel','greenhouse-door-frame')
# narrow tile path from centre plaza to greenhouse doors
scene.ribbon([(1.7,4.4),(3.55,5.5),(4.23,7.1)],1.35,-.04,.095,'stone_bright','greenhouse-entry-path')

# --- western 'YOUTH LAB' exhibition pavilion, genuine vertical timber ribs & sliding display ---
px,pz=-8.7,1.35;pw,pd=3.55,3.1
scene.box([px,.20,pz],[pw+.4,.38,pd+.5],'terrace','exhibit-stage')
scene.box([px,2.42,pz],[pw+.55,.23,pd+.55],'roof_light','exhibition-floating-canopy')
scene.box([px,2.64,pz],[pw+.9,.07,pd+.85],'woodlight','exhibition-parapet-cap')
for x in [px-pw/2+.2,px+pw/2-.2]:
 for z in [pz-pd/2+.2,pz+pd/2-.2]:scene.box([x,1.26,z],[.15,2.5,.15],'wood','exhibit-wood-columns')
scene.box([px,1.43,pz-pd/2+.07],[pw-.6,1.85,.08],'glass_shadow','exhibit-rear-glass')
for x in np.linspace(px-pw/2+.25,px+pw/2-.25,9):scene.box([x,1.42,pz-pd/2],[.055,2.2,.12],'woodlight','exhibit-vertical-fins')
# workshop side open exhibit with 3 sculptural machinery disks
for x,z in [(-9.3,.95),(-8.2,1.4)]:
 scene.box([x,.55,z],[.95,.8,.75],'steel','exhibit-machinery-table')
 scene.sphere([x,.98,z],.31,'rust','exhibit-machinery-part',1,scale=[1,.45,1])
scene.box([px,2.1,pz+pd/2],[pw,.11,.07],'woodlight','exhibition-entrance-header')
# exhibit forecourt circular motifs (away from main core)
for x,z,r in [(-10.,-1.1,.67),(-6.6,4.8,.55)]:
 scene.cyl([x,.14,z],r,.10,'stone_cream','public-art-pedestal',20,r0=1)
 scene.rod([x,.2,z],[x+.12,1.2,z-.1],.09,'steel','abstract-art-spine')
 scene.sphere([x+.12,1.24,z-.1],.26,'rust','bronze-abstract-art',1,scale=[.8,1.4,.8])
# pedestrian pier/overlook on SW outer edge to make island asymmetry
ov=[(-10.8,5.8),(-8.7,5.8),(-8.9,8.25),(-11.0,7.25)]
scene.polygon(Polygon(ov),-.04,.18,'wood','west-observation-platform')
for x,z in [(-10.9,6.2),(-10.8,7.2),(-9.6,8.1)]:scene.rod([x,-1.3,z],[x,.45,z],.085,'steel','overlook-support')

# --- plaza artwork and outdoor plant experiments, keep the central circulation clear ---
# Slender makers sculpture on far western side of central circle
scene.cyl([-9.6,.16,4.75],.72,.22,'stone_cream','maker-monument-plinth',18,r0=1)
for theta in [0,math.pi/2,math.pi]:
 scene.rod([-9.6+math.cos(theta)*.2,.27,4.75+math.sin(theta)*.2],[-9.6+math.cos(theta+.5)*.55,1.5,4.75+math.sin(theta+.5)*.55],.07,'rust','innovation-sculpture-stem')
for xx,zz in [(-9.3,5.25),(-9.8,4.35)]:scene.sphere([xx,1.55,zz],.23,'woodlight','innovation-sculpture-end',2)
# Preserve original mushroom at exact local coordinate, correct scale/material, protected zone
# Do not add a duplicate mushroom mesh: the existing game-owned jump pad remains authoritative.
# marker: delicate circular paving, no new collision claims
ring=Point(3.056,3.438).buffer(1.1,resolution=24).difference(Point(3.056,3.438).buffer(1.00,resolution=24))
scene.polygon(ring,.09,.105,'paver_dark','mushroom-visual-keepclear-marking')
# marker NPC reserved candidate to be reviewed as programmatic, not installed
scene.box([.5,.09,8.35],[.25,.02,.25],'solar_hi','npc-reservation-reference')

# architecture-focused tree scatter: trees only away from routing + structures + NPC
for idx in range(85):
 theta=rng.random()*math.tau;r=math.sqrt(rng.random())
 x=13.65*math.cos(theta)*r; z=12.05*math.sin(theta)*r
 if not foot.buffer(-.75).contains(Point(x,z)):continue
 if core.buffer(.90).contains(Point(x,z)) or plaza.buffer(.65).contains(Point(x,z)):continue
 if (4.0<x<12.6 and -3.4<z<4.7) or (3.8<x<10.6 and 5.0<z<10.8) or (-11.5<x<-6.5 and -1.1<z<4.0):continue
 if math.hypot(x-3.056,z-3.438)<1.45 or (-3.15<x<3.85 and 5.0<z<11.5):continue
 # layered plant grouping: prominent trees + cone conifers + bush understorey
 if idx%5==0:
  h=2.0+rng.random()*1.7
  scene.rod([x,.15,z],[x,h*.53,z],.115,'wood','tree-trunk',8)
  for j,(ox,oy,oz,s) in enumerate([(0,h*.65,0,.75),(.42,h*.63,.06,.53),(-.25,h*.82,.12,.6),(.10,h*.98,-.35,.52)]):
   scene.sphere([x+ox,oy,z+oz],s,['plant_pine','plant_bush','plant_leaf','plant_yellow'][j%4],f'canopy-leaf-{idx}',1,scale=[1,.79,1])
 elif idx%7==0:
  h=2.0+rng.random()*1.2
  scene.cone([x,.12+h/2,z],.56,h,'plant_pine','conifer-crown',9)
 else:
  rad=.22+rng.random()*.26
  col=['plant_bush','plant_leaf','plant_yellow','plant_pink'][idx%4]
  scene.sphere([x,.18+rad*.4,z],rad,col,f'flowering-underplant-{idx}',1,scale=[1,.58,1])
# intentional planters anchoring main building and greenhouse, away from circulation
for x,z,w,d in [(11.4,-4.3,1.8,.52),(11.2,5.05,1.8,.52),(3.6,-2.65,1.2,.44),(9.9,10.6,1.85,.4),(-10.8,4.2,.35,1.1)]:
 scene.box([x,.30,z],[w,.42,d],'terrace','architectural-raised-planter')
 for n in range(5):
  xx=x+(n-2)*(w/6);zz=z+rng.uniform(-d*.12,d*.12)
  scene.sphere([xx,.55,zz],.15+rng.random()*.1,['plant_leaf','plant_bush','plant_yellow'][n%3],'planter-layer',1,scale=[1,.65,.85])
# benches and low pathlights on non-primary walkway edges
for x,z,yaw in [(-10.5,-4.65,.4),(-10.8,8.25,.9),(11.2,9.3,1.3),(-2.9,10.6,0.2),(10.8,-5.25,.3)]:
 scene.box([x,.40,z],[1.28,.15,.4],'woodlight','plaza-bench-seat',yaw)
 scene.box([x,.22,z-.15],[1.2,.3,.09],'steel','bench-leg',yaw)
for x,z in [(3.45,-3.1),(-4.6,-6.25),(-5.5,5.3),(11.2,8.9),(1.4,10.6)]:
 if core.buffer(.28).contains(Point(x,z)):continue
 scene.box([x,.48,z],[.13,.8,.13],'steel','courtyard-low-bollard')
 scene.box([x,.9,z],[.19,.10,.20],'light','courtyard-low-bollard-light')
# retained walkable bridge sides provisional interface (not collision model)
# create a few metal railing segments around island outer edge, skipping bridge mouths.
for k in range(0,N,2):
 a=np.array(shape[k]);b=np.array(shape[(k+2)%N]);mid=(a+b)/2
 if core.buffer(.32).intersects(LineString([a,b])):continue
 ax,az=a;bx,bz=b
 scene.rod([ax,.15,az],[ax,1.18,az],.038,'steel','island-boundary-post',6)
 scene.rod([ax,1.18,az],[bx,1.18,bz],.035,'steel','island-boundary-toprail',6)
 scene.rod([ax,.66,az],[bx,.66,bz],.024,'steel_light','island-boundary-midrail',6)
# landmark campus portal: slender teal arch between workshop entrance and plaza, not blocking main axis
for z in [1.8,3.3]:scene.box([3.32,1.5,z],[.13,2.9,.13],'wood','maker-portal-frame')
scene.box([3.32,3.0,2.55],[.23,.12,1.65],'woodlight','maker-portal-header')


# === ARCHITECTURAL LANDSCAPE V2.2: layered coherent gardens, paths, bridge interfaces ===
# Pedestrian timber terraces fronting greenhouse; lowered enough to leave skywalk clear
for x,z,w,d in [(3.65,6.6,1.65,.52),(10.25,7.6,.6,2.1),(-11.15,3.6,.6,1.4)]:
 scene.box([x,.20,z],[w,.20,d],'woodlight','architectural-deck-trim')
for x,z,w,d in [(-10,-6.0,2.2,1.15),(10,-5.7,2.0,.65),(-10.3,8.65,1.5,.5)]:
 p=Point(x,z).buffer(.9,resolution=16).intersection(foot)
 scene.polygon(p,-.04,.14,'terrace','terrace-vegetation-foundation')
 for j in range(11):
  a=j*2*math.pi/11+(.1*x);cx=x+(.56+0.16*(j%3))*math.cos(a);cz=z+(.42+.16*(j%3))*math.sin(a)
  if foot.buffer(-.32).contains(Point(cx,cz)) and not core.buffer(.45).contains(Point(cx,cz)):
   scene.sphere([cx,.31,cz],.19,['plant_bush','plant_leaf','plant_yellow','plant_pink'][j%4],f'massed-shrub-garden-{j}',1,scale=[1,.62,.80])
# Pavilion canopy timber battens and skylight/glazed cap, avoid the inert solid roof look
for z in np.linspace(pz-1.42,pz+1.42,13):
 scene.box([px,2.73,z],[pw+.65,.08,.085],'wood','pavilion-canopy-sunshade')
scene.box([px,2.83,pz],[pw-1.0,.13,pd-.92],'glass_shadow','pavilion-central-skylight')
for x in np.linspace(px-1.1,px+1.1,5):
 scene.box([x,2.84,pz],[.04,.1,pd-.92],'steel','pavilion-skylight-crossbar')
# Hands-on makers activity tables and photovoltaic benches in western demonstration garden
for xx,zz in [(-11.65,-1.25),(-9.5,-1.25)]:
 scene.box([xx,.66,zz],[1.42,.10,.73],'woodlight','outdoor-makers-table')
 for dx in [-.48,.48]:scene.box([xx+dx,.30,zz],[.075,.60,.10],'steel','makers-table-leg')
 scene.box([xx,.85,zz],[.48,.23,.3],'solar_hi','maker-prototype-on-display')
# Rhythm of orange architectural lanterns along the front of the main workshop
for zz in np.arange(-1.55,3.55,1.0):
 scene.box([4.00,2.50,zz],[.10,.38,.17],'light','factory-entry-lantern')
# Extending public paths to the ring: exit mouths are precise gate directions,
# while new bridges are design visualization only, not a collision replacement.
for route in ('S14','S15','S16'):
 points=road_centerlines[route]
 if route in ('S14','S15'):points=points[::-1]  # orient from C center outwards
 outside=None
 for i in range(2,len(points)):
  if not foot.contains(Point(*points[i])):
   outside=i;break
 if outside is None:continue
 # follow the TRUE cubic curve at the new island boundary, instead of a radial guess
 a_idx=max(0,outside-8)
 end_idx=outside
 for i in range(outside+1,len(points)):
  if Point(*points[i]).distance(Point(*points[outside]))>=4.7:
   end_idx=i;break
 segment=points[a_idx:end_idx+1]
 scene.ribbon(segment,4.8,-.18,.045,'stone_cream',f'{route}-accurate-skywalk')
 # safety rails only outside the new cliff; never duplicate rails through the center junction
 sel=[segment[j] for j in sorted(set(np.linspace(8,len(segment)-1,6,dtype=int)))]
 for side in [-1,1]:
  rail=[]
  for j,p in enumerate(sel):
   i=max(1,min(len(segment)-2,int(np.linspace(8,len(segment)-1,6,dtype=int)[j])))
   tangent=np.array(segment[i+1])-np.array(segment[i-1]);tangent/=max(1e-8,np.linalg.norm(tangent))
   q=np.array(p)+side*2.31*np.array([-tangent[1],tangent[0]])
   if foot.contains(Point(*q)) and j==0:continue
   scene.rod([q[0],.13,q[1]],[q[0],1.21,q[1]],.037,'steel','bridge-guard-post')
   rail.append(q)
  for p0,p1 in zip(rail,rail[1:]):
   scene.rod([p0[0],1.20,p0[1]],[p1[0],1.20,p1[1]],.042,'steel','bridge-guard-top')
   scene.rod([p0[0],.62,p0[1]],[p1[0],.62,p1[1]],.026,'steel_light','bridge-guard-middle')

# Make a deliberate 0.85-unit easterly setback from the actual S15 Bezier corridor.
for mesh,mat,name in scene.parts[workshop_start:workshop_end]:
 mesh.apply_translation([.85,0,0])
# Preserve front architectural lantern rhythm with the same shift.
for mesh,mat,name in scene.parts:
 if name in ('factory-entry-lantern','maker-portal-frame','maker-portal-header'):
  mesh.apply_translation([.85,0,0])

if __name__=='__main__':
 path=os.path.join(OUT,'C_IndustryYouth_V2_DesignReference.glb')
 model=scene.export(path)
 runtime=scene.export(os.path.join(OUT,'C_IndustryYouth_V2_RuntimeAssetCandidate.glb'),exclude_names=('bridge-guard','S14-accurate-skywalk','S15-accurate-skywalk','S16-accurate-skywalk','island-boundary-','npc-reservation-reference'))
 print('objects',len(scene.parts),'triangles',sum(x['triangles'] for x in scene.objects),'GLB bytes',os.path.getsize(path))
 with open(os.path.join(OUT,'model-report.json'),'w',encoding='utf8') as f:json.dump({'status':'design-reference-unverified','centreWorld':[-20.358,0,38.61],'ports':ports,'basis':'Codex C preflight 3f1c272','geometryObjects':len(scene.parts),'triangles':sum(x['triangles'] for x in scene.objects),'triangleBreakdown':scene.counts,'assetFile':os.path.basename(path),'scope':'Architectural geometry only; physics, bridge clipping, NPC interactions and runtime not tested.'},f,ensure_ascii=False,indent=2)
