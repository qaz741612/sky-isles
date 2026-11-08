# Concept-stage standalone 3D design geometry, revision R1.
# All meshes in Sky Isles axes: X/Z ground plane, Y vertical.
# Not a game integrated build or a final art approval.
import os, math, json, random, time
import numpy as np
import trimesh
import vtk
from vtk.util.numpy_support import numpy_to_vtk
from PIL import Image, ImageDraw, ImageFont
from collections import defaultdict
from pathlib import Path

OUT=Path('/mnt/data/bdeh_redesign'); (OUT/'renders').mkdir(parents=True,exist_ok=True); (OUT/'models').mkdir(parents=True,exist_ok=True)
C={
 'cliff':'#556b70','cliff2':'#425458','cliff3':'#80908c','cliff_dark':'#33474b', 'earth':'#8d9b89',
 'grass':'#9fc2a0','grass_l':'#c1d4aa','stone':'#d7d5c5','stone2':'#b6beb6','path':'#d9d1bd',
 'teal':'#195b67','teal_l':'#378a92','glass':'#62b9c4','glass2':'#8edbd9','dark':'#183b4c',
 'bronze':'#b08052','wood':'#9a6a3d','wood2':'#c59a61','cream':'#f3e8d0','white':'#e9eeea',
 'copper':'#b56d45','terra':'#bc7556', 'flower':'#dc9f98','flower2':'#f2c3a9',
 'water':'#3e9ea8','water_l':'#8de1db','water_d':'#267b8e', 'blue':'#4a7da1','blue_l':'#86b8ca',
 'gold':'#e8bd69','green':'#638c60','deepgreen':'#3c6f5d','lightgreen':'#b6d19b',
 'brick':'#ba8c77','metal':'#778d91','mullion':'#325e69', 'rooftop':'#346d74',
}
def rgb(h):return tuple(int(h[i:i+2],16) for i in (1,3,5))
def vec(x,z,y=0):return np.array([x,y,z],float)
class Scene:
 def __init__(self,name,rx=19,rz=16,seed=3):
  self.name=name;self.rx=rx;self.rz=rz;self.rng=random.Random(seed);self.meshes=defaultdict(list);self.stats=defaultdict(int)
 def add(self,name,mesh,col):
  if mesh is None:return
  if hasattr(mesh,'faces') and len(mesh.faces):
   self.meshes[col].append(mesh);self.stats[name]+=1
 def box(self,n,x,z,sx,sz,y0,y1,col):
  m=trimesh.creation.box(extents=(sx,max(.025,y1-y0),sz));m.apply_translation((x,(y0+y1)/2,z));self.add(n,m,col)
 def sphere(self,n,x,z,y,r,col,sub=1,sz=None):
  m=trimesh.creation.icosphere(subdivisions=sub,radius=r);m.apply_scale((1,1 if sz is None else sz,1));m.apply_translation((x,y,z));self.add(n,m,col)
 def cyl(self,n,x,z,y0,y1,r,col,sections=9):
  m=trimesh.creation.cylinder(radius=r,height=max(.02,y1-y0),sections=sections);
  m.apply_transform(trimesh.geometry.align_vectors([0,0,1],[0,1,0]));m.apply_translation((x,(y0+y1)/2,z));self.add(n,m,col)
 def beam(self,n,a,b,rad,col,sect=8):
  a=np.array(a,float);b=np.array(b,float);d=b-a;L=np.linalg.norm(d)
  if L<.005:return
  m=trimesh.creation.cylinder(radius=rad,height=L,sections=sect);m.apply_transform(trimesh.geometry.align_vectors([0,0,1],d/L));m.apply_translation((a+b)/2);self.add(n,m,col)
 def prism(self,n,pts,y0,y1,col):
  # pts list (x,z), convex polygon; handles fan triangulation for constructed architecture
  k=len(pts);verts=np.array([[x,y0,z] for x,z in pts]+[[x,y1,z] for x,z in pts],float)
  faces=[]
  for i in range(1,k-1):faces.append([0,i+1,i]);faces.append([k,k+i,k+i+1])
  for i in range(k):j=(i+1)%k;faces.extend([[i,j,k+j],[i,k+j,k+i]])
  self.add(n,trimesh.Trimesh(vertices=verts,faces=faces,process=False),col)
 def patch(self,n,grid,col,thick=.14):
  # 2D array of points (X,Y,Z) with top+bottom and triangulated sides
  grid=np.asarray(grid,float);nz,nx,_=grid.shape;top=grid.reshape(-1,3);bottom=top.copy();bottom[:,1]-=thick;verts=np.vstack([top,bottom]);N=len(top);faces=[]
  for j in range(nz-1):
   for i in range(nx-1):
    a=j*nx+i;b=a+1;c=a+nx;d=c+1
    faces.extend([[a,c,b],[b,c,d],[N+a,N+b,N+c],[N+b,N+d,N+c]])
  edge=[]
  edge.extend([i for i in range(nx)])
  edge.extend([j*nx+nx-1 for j in range(1,nz)])
  edge.extend([(nz-1)*nx+i for i in range(nx-2,-1,-1)])
  edge.extend([j*nx for j in range(nz-2,0,-1)])
  for a,b in zip(edge,edge[1:]+edge[:1]):faces.extend([[a,b,N+b],[a,N+b,N+a]])
  self.add(n,trimesh.Trimesh(vertices=verts,faces=np.array(faces),process=False),col)
 def roof(self,n,x0,x1,z0,z1,func,col,steps=14,thick=.22):
  xs=np.linspace(x0,x1,steps);zs=np.linspace(z0,z1,steps)
  grid=np.array([[[x,func(x,z),z]for x in xs] for z in zs]);self.patch(n,grid,col,thick)
 def linepath(self,n,pts,width,y0,y1,col):
  for a,b in zip(pts[:-1],pts[1:]):
   a=np.array(a);b=np.array(b);v=b-a;ln=np.linalg.norm(v)
   if ln<.05:continue
   m=trimesh.creation.box(extents=(width,y1-y0,ln+.1));M=trimesh.transformations.rotation_matrix(math.atan2(v[0],v[1]),[0,1,0]);m.apply_transform(M);m.apply_translation(((a[0]+b[0])/2,(y0+y1)/2,(a[1]+b[1])/2));self.add(n,m,col)
 def island(self):
  N=88; t=np.linspace(0,2*math.pi,N,endpoint=False)
  rad=1+0.04*np.sin(3*t+1)+.035*np.sin(5*t-.45)+.016*np.sin(9*t+2)
  top=np.c_[self.rx*rad*np.cos(t),self.rz*rad*np.sin(t)]
  def rings(a,y):return np.c_[top[:,0]*a,np.full(N,y),top[:,1]*a]
  levels=[(1.01,.06),(.985,-.65),(.95,-1.15),(.83,-3.0),(.62,-5.6),(.36,-8.0)]
  for j in range(len(levels)-1):
   o=rings(*levels[j]);p=rings(*levels[j+1]);v=np.r_[o,p];faces=[]
   for k in range(N):l=(k+1)%N;faces.extend([[k,l,N+l],[k,N+l,N+k]])
   colors=['stone2','cliff3','cliff','cliff2','cliff_dark'];self.add('floating_rock',trimesh.Trimesh(vertices=v,faces=faces,process=False),colors[j])
  vv=np.r_[rings(1.01,.075),[[0,.075,0]]];f=[[N,i,(i+1)%N] for i in range(N)];self.add('terrain',trimesh.Trimesh(vertices=vv,faces=f,process=False),'grass')
  # rock accents below edges; genuine three-dimensional ridges
  for k in range(0,N,6):
   a=t[k];x=self.rx*.83*math.cos(a);z=self.rz*.83*math.sin(a)
   self.prism('stratified_rock',[(x-1,z-.6),(x+.7,z-1),(x+1.3,z+.3),(x,z+1)],-3.4,-2.65,'cliff3')
  # small rim surface lip
  for k in range(0,N,3):
   a=t[k];b=t[(k+3)%N];x1,z1=top[k];x2,z2=top[(k+3)%N]
   self.beam('coastal_rim',(x1,.14,z1),(x2,.14,z2),.15,'stone2',6)
 def tree(self,x,z,s=1,kind='olive'):
  self.cyl('trees',x,z,.1,2.1*s,.18*s,'wood',7)
  if kind=='olive':
   for dx,dz,dy,r,col in [(-.65,.1,2.5,1.0,'green'),(.48,.12,2.65,.95,'deepgreen'),(0,-.55,3.08,.9,'lightgreen')]:
    self.sphere('foliage',x+dx*s,z+dz*s,dy*s,r*s,col,sub=1,sz=.8)
  if kind=='pink':
   for dx,dz,dy,r in [(-.6,.1,2.6,.92),(.5,.3,2.66,.85),(.1,-.5,3.05,1.02)]:
    self.sphere('flowering_tree',x+dx*s,z+dz*s,dy*s,r*s,'flower',sub=1,sz=.8)
 def garden(self,x,z,sx,sz,col='deepgreen'):
  self.box('garden_bed',x,z,sx,sz,.07,.34,'stone2');self.box('planted_zone',x,z,sx-.45,sz-.45,.34,.45,col)
  for i in range(max(2,int(sx*sz/7))):
   xx=x+self.rng.uniform(-sx*.33,sx*.33);zz=z+self.rng.uniform(-sz*.32,sz*.32)
   self.sphere('plant',xx,zz,.62,self.rng.uniform(.18,.33),'lightgreen',1)
 def lights(self,coords):
  for x,z in coords:
   self.cyl('7_light',x,z,.1,3.6,.11,'dark',8)
   self.beam('7_light',(x,3.5,z),(x-.75,3.5,z),.105,'metal',8)
   self.box('warm_light',x-.7,z,.57,.12,3.36,3.4,'gold')
 def rail(self,a0,a1,rx=None,rz=None):
  # optional segment along outer edge in angular interval, coarse architectural guardrail
  rx=rx or self.rx*.95;rz=rz or self.rz*.94
  ts=np.linspace(a0,a1,max(4,int((a1-a0)*20)))
  pts=[]
  for t in ts:
   x=rx*math.cos(t);z=rz*math.sin(t);pts.append((x,z))
  for i,(x,z) in enumerate(pts):
   if i%4==0:self.cyl('outer_rail_post',x,z,.13,1.2,.075,'metal',6)
  for a,b in zip(pts[:-1],pts[1:]):
   self.beam('outer_railing',(a[0],1.2,a[1]),(b[0],1.2,b[1]),.065,'metal',6)
 def save(self):
  sc=trimesh.Scene();groups={};faces=0;verts=0
  for color,ms in self.meshes.items():
   m=trimesh.util.concatenate(ms);m.visual.face_colors=np.r_[list(rgb(C[color])),255];sc.add_geometry(m,geom_name=color);groups[color]=len(m.faces);faces+=len(m.faces);verts+=len(m.vertices)
  p=OUT/'models'/f'{self.name}-concept-r1.glb';sc.export(p)
  return dict(name=self.name,faces=int(faces),vertices=int(verts),materials=len(groups),file=str(p),bytes=p.stat().st_size,meshgroups=groups,parts=dict(self.stats))
 def vtk_renderer(self):
  renderer=vtk.vtkRenderer();renderer.GradientBackgroundOn();renderer.SetBackground(.94,.965,.974);renderer.SetBackground2(.74,.85,.91)
  renderer.SetUseFXAA(False)
  for color,ms in self.meshes.items():
   m=trimesh.util.concatenate(ms);poly=vtk.vtkPolyData();pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(m.vertices.astype(np.float32),deep=True));poly.SetPoints(pts)
   ca=vtk.vtkCellArray();ca.AllocateEstimate(len(m.faces),3)
   for face in m.faces:
    tri=vtk.vtkTriangle();
    for j in range(3):tri.GetPointIds().SetId(j,int(face[j]));
    ca.InsertNextCell(tri)
   poly.SetPolys(ca);normal=vtk.vtkPolyDataNormals();normal.SetInputData(poly);normal.SplittingOff();normal.ConsistencyOff();normal.AutoOrientNormalsOff();normal.Update()
   mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normal.GetOutputPort());actor=vtk.vtkActor();actor.SetMapper(mapper)
   pp=actor.GetProperty();pp.SetColor(*(n/255 for n in rgb(C[color])));pp.SetAmbient(.39);pp.SetDiffuse(.69);pp.SetSpecular(.12);pp.SetSpecularPower(28)
   renderer.AddActor(actor)
  light=vtk.vtkLight();light.SetLightTypeToSceneLight();light.SetPosition(-32,62,38);light.SetFocalPoint(0,0,0);light.SetIntensity(.8);renderer.AddLight(light)
  return renderer
 def render(self,view='hero',w=1280,h=960):
  ren=self.vtk_renderer();win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(w,h);win.SetMultiSamples(4);win.AddRenderer(ren)
  cam=ren.GetActiveCamera();cam.SetViewUp(0,1,0);cam.ParallelProjectionOn()
  if view=='hero':cam.SetPosition(48,33,50);cam.SetParallelScale(max(self.rx,self.rz)*1.2)
  elif view=='back':cam.SetPosition(-40,28,-48);cam.SetParallelScale(25)
  elif view=='front':cam.SetPosition(0,19,70);cam.SetParallelScale(21)
  elif view=='right':cam.SetPosition(66,18,0);cam.SetParallelScale(22)
  elif view=='top':cam.SetPosition(.01,100,.02);cam.SetViewUp(0,0,-1);cam.SetParallelScale(24)
  cam.SetFocalPoint(0,0,0)
  ren.ResetCameraClippingRange();win.Render()
  w2i=vtk.vtkWindowToImageFilter();w2i.SetInput(win);w2i.SetInputBufferTypeToRGB();w2i.ReadFrontBufferOff();w2i.Update()
  writer=vtk.vtkPNGWriter();p=OUT/'renders'/f'{self.name}-{view}.png';writer.SetFileName(str(p));writer.SetInputConnection(w2i.GetOutputPort());writer.Write();win.Finalize();return str(p)

# B: Interlocking curved timber wellbeing institute around a true open sensory court.
def build_B():
 s=Scene('B',19.2,16.8,seed=13);s.island()
 s.linepath('entrance_axis',[(17,0),(9,0),(3,0),(-2,0)],4.85,.07,.16,'path')
 s.linepath('court_path',[(-2,0),(-6,0),(-7,3)],3,.09,.18,'stone')
 s.garden(-7.2,0,5.7,5.4,'green')
 # U-shape wings, western back span and separate north/south wings; no building crossing entrance path
 s.box('west_wing',-12.1,0,4.6,14.4,.18,5.45,'cream')
 s.box('northeast_gallery',11.5,7.0,4.5,3.6,.18,4.5,'cream')
 s.box('south_wing',-6.4,-7.2,13.8,4.1,.18,4.5,'cream')
 # substantial ground floor shaded portico along courtyard edge
 for z in np.linspace(-6,6,10):
  s.cyl('veranda_post',-9.35,z,.2,4.9,.12,'wood',8)
  s.box('wood_fin',-9.3,z,.22,.17,1.3,4.75,'wood2')
 for x in np.linspace(-11.8,-.6,13):
  s.cyl('south_veranda_post',x,-4.9,.15,4.6,.10,'wood',8)
 for x in np.linspace(10.2,14.6,7):
  s.cyl('northeast_post',x,4.83,.15,4.6,.10,'wood',8)
 # facade glazing on the two wing fronts and back
 for x in np.linspace(-11,-1.6,12):
  s.box('south_glass',x,-9.4,.62,.1,1.15,3.7,'glass')
  s.box('south_mullion',x+.33,-9.4,.08,.16,1.0,4.1,'bronze')
 for x in np.linspace(10.4,14.7,7):
  s.box('gallery_glass',x,9.15,.55,.1,1.15,3.7,'glass2')
  s.box('gallery_mullion',x+.30,9.15,.09,.16,1,4.2,'wood')
 for z in np.linspace(-5.8,5.8,12):
  s.box('court_glazing',-9.65,z,.1,.6,1,4.05,'glass2')
  s.box('wood_mullion',-9.57,z+.30,.11,.06,.95,4.23,'wood')
 # two grand flowing, layered roof ribbons; arch higher at courtyard-facing edge
 def south_roof(x,z):return 5.4+1.65*math.exp(-((x+5.1)/5.0)**2)+.38*math.cos((z+7)*.82)
 def north_roof(x,z):return 5.55+1.65*math.exp(-((x-12.5)/4.8)**2)+.38*math.cos((z-7)*.82)
 s.roof('south_curved_roof',-13.7,1.55,-10.2,-4.35,south_roof,'wood2',18,.28)
 s.roof('north_curved_roof',9.0,16.1,4.35,10.2,north_roof,'copper',18,.28)
 for x in np.linspace(-13,1.2,16):
  for z in [-9.8,-4.45]:s.beam('timber_rib',(x,south_roof(x,z)-.10,z),(x,south_roof(x,z)-.85,z),.11,'wood',7)
 for x in np.linspace(9.2,15.9,10):
  for z in [4.45,9.8]:s.beam('gallery_rib',(x,north_roof(x,z)-.10,z),(x,north_roof(x,z)-.85,z),.11,'bronze',7)
 # west elevated bridge roof over entire spanning wing, visually frames 2 open terraces
 s.roof('west_ribbon',-15.1,-9.8,-9.6,9.6,lambda x,z: 7.25+.55*math.cos(z*.15),'rooftop',16,.26)
 for z in np.linspace(-8.9,8.9,12):s.beam('roof_ribs',(-15,7.5,z),(-9.8,7.5,z),.09,'bronze',7)
 # sensory garden, terrace and secondary community canopy
 for a in np.linspace(0,2*math.pi,20,endpoint=False):
  x=-5.8+2.35*math.cos(a);z=0+2.35*math.sin(a)
  s.cyl('garden_motif',x,z,.12,.23,.18,'stone2',8)
 s.cyl('sensory_tree',-5.8,0,.17,1.5,.19,'wood',9);s.sphere('sensory_canopy',-5.8,0,2.15,1.25,'flower2',2,sz=.68)
 s.garden(9.6,12.0,3.8,1.0,'lightgreen')
 for x,z in [(-15,11),(15,6),(12,-10),(1,-13)]:s.tree(x,z,.82,'pink' if z>0 else 'olive')
 s.garden(8,-8,5,2.1);s.garden(10,12,4,1.5,'green')
 s.lights([(12,-6),(12,4),(-3,-13)])
 s.rail(.15,2.9);s.rail(3.5,6.0)
 return refine_B(s)

# D: Low-slung folded civic roof with tall faceted lantern, services around central open plaza.
def build_D():
 s=Scene('D',21.6,19.4,seed=21);s.island()
 # traverse route from SE to NW, keep uncluttered south-west diagonal
 s.linepath('walk',[(14,-12),(6,-6),(-1,1),(-10,11),(-16,14)],4.85,.07,.16,'path')
 # civic hall to northeast side of route; long cantilevered double wing
 s.box('public_hall',8,7.5,13.5,7.8,.16,5.4,'cream')
 s.box('secondary_wing',12,-1.0,8.0,4.2,.16,3.8,'stone')
 s.box('roof_base',8,7.5,14.3,8.6,5.4,5.72,'stone2')
 # central lantern is a tall hexagonal jewel, not an independent tower
 pts=[(3,5),(5,4.3),(8.2,4.4),(10.1,7.0),(8.0,10.5),(4,10.6),(2.8,8)]
 s.prism('civic_lantern',pts,5.4,9.7,'glass2')
 for xx,zz in pts:s.beam('lantern_spines',(xx,5.25,zz),(xx,10,zz),.17,'dark',8)
 s.prism('lantern_cap',[(2.4,4.5),(5,3.7),(8.6,3.9),(10.6,7.2),(8.5,11.1),(3.5,11.3),(2.2,8.5)],9.55,10.0,'bronze')
 # north fold has broad long-span gesture, west fold deep elegant overhang, no typical pitched roof
 s.roof('public_flight_roof',0,17.1,2.2,13.5,lambda x,z: 6.0+1.7*math.exp(-((x-5.7)/5.5)**2)+.42*((z-6)/6),'teal',20,.38)
 s.roof('entrance_roof',7.0,17.2,-4.1,2.3,lambda x,z: 4.4+.9*((x-2)/15)-.17*((z+9)/9.8),'bronze',16,.3)
 # mullion-rich glass service lobby
 for xx in np.linspace(1.9,14.1,18):
  for zz in [3.55,11.45]:
   s.box('facade_glass',xx,zz,.62,.11,.9,5.22,'glass')
   s.box('facade_vertical',xx+.32,zz,.09,.15,.8,5.4,'dark')
 for zz in np.linspace(4.1,10.7,12):
  for xx in [1.17,14.83]:
   s.box('side_facade',xx,zz,.1,.52,1,5.0,'glass2')
 for x in np.linspace(1.0,16.2,14):s.beam('roof_structural_rib',(x,5.5,3.0),(x,7.0,12.8),.1,'metal')
 # architecture gestures: tall triangular structural V at forecourt
 for x in [7.8,14.2]:
  s.beam('support_pier',(x,.2,2.85),(x+.9,5.35,4.3),.3,'stone2',8)
 # one vast public plaza with elegant concentric digital floor strips as planning only
 s.linepath('public_plaza',[(-10,-5),(-5,-3),(0,-1),(4,0)],4.0,.08,.13,'stone')
 for i in range(5):
  x=-11+i*1.7;s.box('floor_data_inlay',x,2.1,.12,4.3,.12,.14,'gold')
 # reception canopy and interactive display instead of a huge fake screen
 s.box('public_sign_frame',13.2,-5.1,2.65,.23,1.1,3.45,'dark')
 s.box('public_sign_lit',13.2,-4.94,2.25,.08,1.55,2.85,'blue_l')
 for x,z in [(-14,-4),(-6,-13),(17,10),(-9,14)]:s.tree(x,z,.95,'olive')
 s.garden(-11,1,3.2,6,'green');s.garden(9,-12,5.2,2,'deepgreen')
 s.lights([(-12,9),(-2,-11),(15,11)])
 s.rail(.1,2.4);s.rail(3.2,5.8)
 return refine_D(s)

# E: folded earthen eco-wings / wetland canal; no arched greenhouse, preserve four-way route.
def build_E():
 s=Scene('E',23.2,20.4,seed=36);s.island()
 s.linepath('protected_east_west',[(-19,0),(-9,0),(0,0),(10,0),(19,0)],4.85,.08,.16,'path')
 s.linepath('protected_diagonal',[(16,-14),(9,-7),(0,0),(-8,8),(-16,14)],4.85,.08,.16,'stone')
 # build icon in NE quadrant: two 'strata roof' origami ridges with green roofs, no circular greenhouse
 s.box('eco_hall',8.2,8.6,14.4,10.2,.17,5.25,'cream')
 s.box('eco_podium',8.2,8.6,15.8,11.7,.13,.44,'stone2')
 for z in np.linspace(4.2,13.0,13):
  for x in [1.5,14.6]:
   s.box('eco_glass',x,z,.12,.5,.8,5.1,'glass2')
   s.box('eco_vertical',x,z+.28,.18,.12,.8,5.3,'wood')
 for x in np.linspace(2.0,14.0,15):
  s.box('eco_south_glass',x,3.35,.62,.11,1.0,5.12,'glass')
  s.box('eco_south_fin',x+.35,3.2,.095,.33,.85,5.28,'wood2')
 # 3 massive overlapping fold planes (living roof), separated for visible split and light-wells
 for j,(z0,z1) in enumerate([(2.2,6.8),(6.8,11.5),(11.5,16)]):
  s.roof('folded_living_roof',.1,17.1,z0,z1,
   lambda x,z,j=j: 5.7+1.2*math.sin((x+1)/18*math.pi)+.4*j+(.36 if j%2==0 else -.2)*(z-z0),'deepgreen' if j%2==0 else 'green',16,.28)
  for x in np.linspace(1.0,16.2,11):s.beam('eco_roof_rib',(x,5.5,z0+.08),(x,5.5+.25*j,z1-.08),.095,'wood2',6)
 # ecological terraces follow the existing island, not a separate greenhouse
 for x,z,sx,sz in [(10,-10,10,4),(0,12,6,2.4),(-10,-5,5,2.5)]:s.garden(x,z,sx,sz,'green')
 # stone rain-garden / cascaded wetland in SW with low retaining edges
 for k,(x,z,w,l,y) in enumerate([(-9,-9,9,5,.22),(-11,-12,7,3,.38),(-8,-6,7,3,.30)]):
  s.box('wetland_stone',x,z,w,l,.1,y,'stone2')
  s.box('wetland_water',x,z,w-.55,l-.6,y,y+.075,'water' if k!=1 else 'water_d')
  for i in range(7):
   xx=x-w*.4+i*(w*.8/6);zz=z+(i%2)*.22
   s.beam('reed',(xx,y+.1,zz),(xx,y+.8+.17*(i%3),zz),.045,'deepgreen',6)
 # architectural boardwalk crossing away from protected diagonal
 s.linepath('nature_walk',[(-14,-11),(-13,-8),(-12,-5)],2,.25,.42,'wood2')
 # rooftop living-roof gallery roof parapet is not climbable in this phase
 for xx,zz in [(-16,7),(-2,-13),(17,12),(-15,-3)]:s.tree(xx,zz,.91,'olive')
 for x,z in [(-17,2),(15,-12)]:s.lights([(x,z)])
 s.rail(.0,1.95);s.rail(2.4,4.7);s.rail(5.1,6.2)
 return refine_E(s)

# H: Two cantilevered folded 'book leaves' over a daylight education canyon; no clock tower or oval track.
def build_H():
 s=Scene('H',21.4,19.3,seed=42);s.island()
 s.linepath('protected_way',[(-18,0),(-9,-1),(0,-3),(10,-8),(17,-11)],4.85,.07,.16,'path')
 # elevated educational learning canyon across north half
 s.box('reading_west',-8.0,7.1,10.3,7.6,.15,5.35,'cream')
 s.box('learning_east',7.5,7.0,11.5,7.9,.15,5.65,'stone')
 # tall central transparent multipurpose heart - distinct from school block
 s.box('daylit_atrium',0,7.1,5.3,8.2,.2,7.5,'glass2')
 for x in [-2.8,2.8]:
  for z in [3,11.3]:s.beam('atrium_structure',(x,.18,z),(x,8.5,z),.16,'metal',9)
 for x in np.linspace(-2.4,2.4,8):
  s.box('glass_ribs',x,2.95,.11,.17,1.0,7.85,'dark')
  s.box('glass_ribs',x,11.25,.11,.17,1.0,7.85,'dark')
 # massive asymmetrical folded open-book roofs; separated through glass spine
 s.roof('western_leaf',-15.2,-1.4,1.55,14.7,lambda x,z: 5.75+1.85*((-x-1.4)/13.8)+.35*math.sin(z*.36),'blue',17,.34)
 s.roof('eastern_leaf',1.35,15.6,1.55,14.8,lambda x,z: 5.92+2.05*((x-1.35)/14.25)+.27*math.sin(z*.32+.7),'teal',17,.34)
 for z in np.linspace(2.0,14.1,12):
  for xx,yy in [(-14.6,7.6),(-1.55,5.65),(1.6,5.9),(15,7.9)]:
   s.beam('book_spine',(xx,yy-.4,z),(xx,yy+.04,z),.10,'metal',7)
 # actual visible entrances and facade rhythmic glazing
 for xx in np.linspace(-12.4,-3.4,13):
  for z in [3.2,11.0]:
   s.box('west_glass',xx,z,.5,.13,1.0,5.1,'glass')
   s.box('west_mullion',xx+.26,z,.08,.2,.9,5.28,'mullion')
 for xx in np.linspace(3.4,12.6,13):
  for z in [3,11.1]:
   s.box('east_glass',xx,z,.53,.13,1.0,5.4,'glass')
   s.box('east_mullion',xx+.25,z,.085,.16,.9,5.6,'dark')
 # outdoor learning amphitheater on SW terrace, not running track
 for ring in range(4):
  r=4.8-ring*.9
  for a in np.linspace(math.pi*.64,math.pi*1.9,18):
   x=-8+r*math.cos(a);z=-8+r*math.sin(a)
   s.box('learning_seat',x,z,.85,.55,.08,.18+ring*.23,'wood2' if ring%2 else 'stone2')
 s.box('demo_stage',-8,-8,4,3,.1,.32,'stone')
 # floating telescope-inspired STEAM kinetic installation (noninteractable)
 for angle in np.linspace(0,2*math.pi,15,endpoint=False):
  p1=(10+1.8*math.cos(angle),2.8, -7+1.8*math.sin(angle));p2=(10+1.8*math.cos(angle+.45),2.8,-7+1.8*math.sin(angle+.45))
  s.beam('orbital_learning_ring',p1,p2,.14,'gold')
 s.cyl('orbital_installation_stand',10,-7,.12,2.9,.23,'dark')
 for x,z in [(-16,9),(16,10),(-1,-14),(15,-13)]:s.tree(x,z,.89,'pink' if z>0 else 'olive')
 s.garden(-13,-2,4,2);s.garden(12,-13,4.4,1.5,'deepgreen')
 s.lights([(-13,-10),(1,-10),(17,2)])
 s.rail(.1,2.7);s.rail(3.0,5.8)
 return refine_H(s)

# Geometry upgrades, layered on the first model without editing its core site constraints.
def refine_B(s):
 # One spacious grand entrance canopy with structural ribs, no obstacles in 4.8 core
 for x in np.linspace(10.5,14.8,10):
  s.box('northeast_gallery_shade',x,7.0,.12,5.2,4.48,4.66,'wood2')
 # accessible planted courtyard with durable stone edging
 for a in np.linspace(0,2*math.pi,40,endpoint=False):
  x=-5.4+3.55*math.cos(a);z=3.55*math.sin(a)
  s.cyl('courtyard_stone_kerb',x,z,.13,.38,.16,'stone',7)
 for x,z in [(-7.4,3.2),(-8.3,-2.8),(-3.2,2.9)]:s.garden(x,z,1.9,1.0,'green')
 # deep louvred window facade on back of building
 for z in np.linspace(-6.4,6.4,20):s.box('exterior_wood_louvres',-14.5,z,.18,.09,1.2,5.7,'wood')
 # ground-level lookout zone at northeast, not rooftop pseudo-access
 s.box('lookout_deck',11.3,9.5,6,3.1,.15,.40,'wood2')
 for x in np.linspace(9.2,13.2,6):s.box('integrated_seating',x,10.2,.6,.5,.40,.69,'wood')
 return s

def refine_D(s):
 # Transparent multi-sided luminous civic crown; not a standalone tower
 s.prism('civic_lantern_upper',[(3.6,5.7),(5,4.9),(8.1,5.5),(9.6,7.1),(7.8,9.7),(4.0,9.9)],10.0,11.25,'glass')
 for x,z in [(3.7,5.7),(9.3,7.1),(5,9.8)]:s.beam('lantern_reinforcement',(x,9.8,z),(x,11.5,z),.12,'dark')
 for x in np.linspace(2.2,14,14):
  s.box('civic_recessed_entrance_glazing',x,3.52,.60,.10,1.0,5.25,'glass2')
  s.beam('angled_arcade',(x,.18,3.1),(x+.25,5.9,3.36),.13,'stone2')
 for x in np.linspace(1.3,16.1,16):s.beam('roof_soffit_struts',(x,5.5,2.5),(x,6.4,12.5),.11,'bronze',7)
 # major stone public plinth and abstract digital direction inlays
 for i in range(5):s.box('digital_direction_inlay',-9+i*1.7,1.1,.08,3.1,.16,.18,'bronze')
 return s

def refine_E(s):
 # three lifted living-roof folds need explicit timber rib and glazing articulation
 for x in np.linspace(1,16.7,15):
  for z in [2.4,6.6,11.6,15.5]:s.beam('roof_timber_fins',(x,5.4,z),(x,6.5,z),.10,'wood',7)
 for x in [2.2,6.7,11.1,15.5]:
  s.beam('exposed_structural_x',(x,1.3,3.3),(x+1.5,5.4,4.5),.15,'wood2')
  s.beam('exposed_structural_x',(x+1.5,1.3,3.3),(x,5.4,4.5),.12,'bronze')
 for x,z in [(-14,-9),(-13,-11),(-10,-13),(-6,-13)]:s.garden(x,z,2,1.1,'deepgreen')
 # real low-tech water rill as surface geometry rather than repeated white rods
 s.box('water_reuse_runnel',-8.1,-13.1,8.2,.6,.41,.50,'water_l')
 for x in np.linspace(-11.7,-4.5,9):s.box('runnel_foam',x,-13.1,.22,.52,.50,.54,'white')
 return s

def refine_H(s):
 # Reinforced iconic book-leaf ribs, separated by glass atrium
 for x in np.linspace(-14,-2.1,17):s.beam('western_page_ribs',(x,5.7,2.0),(x,7.8,14.2),.15,'metal')
 for x in np.linspace(2.1,14.6,17):s.beam('eastern_page_ribs',(x,5.8,2.0),(x,8.2,14.2),.15,'bronze')
 for z in np.linspace(3,11.2,12):
  for x in (-2.7,2.7):s.box('atrium_wood_fins',x,z,.17,.10,1,7.3,'wood2')
 # educational outdoor tiered room (open amphitheater, no oval school track)
 for k in range(4):s.box('amphitheater_landings',-9,-7.8-k*1.1,8.4-k*.6,1.0,.16,.28+k*.24,'stone2')
 s.sphere('orbital_learning_sculpture',10,-7,3.1,.48,'gold',1)
 return s

def board(images,info):
 W,H=2000,1440;bg=Image.new('RGB',(W,H),'#eef4f3');d=ImageDraw.Draw(bg)
 fonts=['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'];fontpath=next((x for x in fonts if os.path.exists(x)),fonts[-1]);
 title=ImageFont.truetype(fontpath,47);sub=ImageFont.truetype(fontpath,25);small=ImageFont.truetype(fontpath,21)
 d.text((62,28),'苑裡政策島 ｜ B／D／E／H 四島重新設計',font=title,fill='#193f4c')
 d.text((64,94),'實際可重建 3D 幾何研究 · 首輪美術審查 · 未進遊戲／未核准施工',font=sub,fill='#517179')
 entries=[('B','幸福養老｜環抱式療癒院','暖木雙翼 · 開放中庭',images[0]),('D','智慧公所｜折翼公共服務廳','大跨屋面 · 水晶光廳',images[1]),('E','宜居環境｜地景共生館','分層綠屋面 · 雨水花園',images[2]),('H','教育發展｜展頁學習谷','雙葉書頁 · 戶外學習劇場',images[3])]
 for i,(letter,name,tag,p) in enumerate(entries):
  x=42+(i%2)*994;y=142+(i//2)*629
  d.rounded_rectangle((x,y,x+970,y+611),radius=25,fill='white',outline='#c5d5d5',width=2)
  im=Image.open(p).convert('RGB'); im.thumbnail((925,480));bg.paste(im,(x+22+(925-im.width)//2,y+77))
  d.rounded_rectangle((x+20,y+13,x+65,y+57),radius=9,fill='#1c5260');d.text((x+33,y+16),letter,font=sub,fill='white')
  d.text((x+83,y+15),name,font=sub,fill='#173e49');d.text((x+26,y+562),tag,font=small,fill='#55717a')
 bg.save(OUT/'BDEH-redesign-first-review.png')

if __name__=='__main__':
 start=time.time();scenes=[build_B(),build_D(),build_E(),build_H()];infos=[];imgs=[]
 for sc in scenes:
  info=sc.save();infos.append(info)
  for v in ['hero','front','top']:
   p=sc.render(v,w=1180,h=850);print('render',sc.name,v,p,flush=True)
   if v=='hero':imgs.append(p)
  print('GLB',sc.name,info['faces'],'faces',info['bytes'],'bytes',flush=True)
 board(imgs,infos)
 (OUT/'model-report.json').write_text(json.dumps(infos,ensure_ascii=False,indent=2))
 print('DONE in',time.time()-start,'seconds',flush=True)
