"""Sky Isles B/D/E/H independent architectural alternatives R8.
Source-aligned XYZ geometry: X/Z plan, Y up. No Blender/Game runtime assumed.
Protected 4.8 road band is read from R7 candidate curves with T4 rightward S06.
Architecture is new: no old R7 roof or building reuse.
"""
import os,sys,math,json,random
from pathlib import Path
import numpy as np
import trimesh
from shapely.geometry import Point,LineString,Polygon,box
from shapely.affinity import scale
from shapely.ops import triangulate, unary_union
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parent))
import vendor_base as base

ROOT=Path(__file__).resolve().parents[1]
for name in ('models','renders','qa'): (ROOT/name).mkdir(exist_ok=True)
base.OUT=ROOT
base.C.update({
    'ivory':'#E8DDD0','slateblue':'#35586B','ochre':'#AF8051','warmwood':'#BE965F','bronze2':'#D6AF70',
    'white2':'#F3EBD8','clay':'#9F6D56','mutedred':'#AC706B','pink2':'#E2B6B0',
    'blueglass':'#83C4CC','deepglass':'#376F83','sage':'#7A9A78','lichen':'#B6C898','leaf':'#6D925F',
    'darkolive':'#425C4A','roofblue':'#376681','moss':'#95B98B','roofbright':'#D2D9BD',
    'lightteal':'#BAD8CF','accentnavy':'#254755','solar':'#365E81','amber':'#E4B65F',
    'charcoal':'#344A53','rockgrey':'#69747B','earthbrown':'#6C675A','palegrey':'#D7DEDB',
    'waterblue':'#4E9CAE','watercream':'#B2DED8'
})
C=base.C
ROAD=json.load(open(Path(__file__).resolve().parents[1]/'data'/'road-candidate-r2.json',encoding='utf8'))
NODE=ROAD['nodes']
SIZES={'B':(30,28),'D':(32,29),'E':(34,31),'H':(33,30)}

# Geometry utility functions. All roofs and glazing are actual mesh faces, not renders.
def polygon_prism(pts,y0,y1):
    """Triangulate a potentially concave XZ polygon, extrude with closed sidewalls."""
    poly=Polygon(pts); poly=poly.buffer(0)
    if poly.geom_type!='Polygon': raise ValueError('invalid polygon')
    triangles=[t for t in triangulate(poly) if poly.covers(t.representative_point()) and abs(t.area-t.intersection(poly).area)<1e-5]
    V=[]; F=[]
    for t in triangles:
        p=np.asarray(t.exterior.coords[:3]); xz=p[:,:2]
        for y,order in [(y1,False),(y0,True)]:
            v0=len(V);V.extend([[x,y,z] for x,z in xz]);
            A,B,D=V[-3:];up=np.cross(np.array(B)-A,np.array(D)-A)[1]>0
            idx=[0,1,2] if up!=order else [0,2,1]
            F.append([v0+i for i in idx])
    coords=list(poly.exterior.coords)[:-1]
    for p,q in zip(coords,coords[1:]+coords[:1]):
        n=len(V);V.extend([[p[0],y0,p[1]],[q[0],y0,q[1]],[q[0],y1,q[1]],[p[0],y1,p[1]]]);F.extend([[n,n+1,n+2],[n,n+2,n+3]])
    return trimesh.Trimesh(vertices=np.asarray(V),faces=np.asarray(F),process=False)

def beam_box(a,b,width,depth):
    a=np.asarray(a,float);b=np.asarray(b,float);dif=b-a;l=np.linalg.norm(dif)
    if l<.001:return None
    # round cylinders look more credible for diagonal supporting ties
    m=trimesh.creation.box(extents=(width,depth,l))
    m.apply_transform(trimesh.geometry.align_vectors([0,0,1],dif/l));m.apply_translation((a+b)/2);return m

class Design(base.Scene):
 def __init__(self,code):
    w,d=SIZES[code]; super().__init__(code,rx=w/2,rz=d/2,seed=51+ord(code))
    self.code=code;self.building_parts=[];self.site_features=[];self.hard=[]
 def mesh(self,n,m,color,role=None):
    self.add(n,m,color)
    if role=='building':self.building_parts.append((n,m))
    if role=='hard':self.hard.append((n,m))
    if role=='site':self.site_features.append((n,m))
 def hardbox(self,n,x,z,sx,sz,y0,y1,color):
    m=trimesh.creation.box(extents=(sx,max(.025,y1-y0),sz));m.apply_translation([x,(y0+y1)/2,z]);self.mesh(n,m,color,'building')
 def hardprism(self,n,pts,y0,y1,col):self.mesh(n,polygon_prism(pts,y0,y1),col,'building')
 def post(self,n,x,z,y0,y1,r=.11,col='wood',sides=8,role='building'):
    m=trimesh.creation.cylinder(radius=r,height=y1-y0,sections=sides);m.apply_transform(trimesh.geometry.align_vectors([0,0,1],[0,1,0]));m.apply_translation([x,(y0+y1)/2,z]);self.mesh(n,m,col,role)
 def girder(self,n,a,b,rad=.10,col='wood',role='building'):
    a=np.asarray(a);b=np.asarray(b);d=b-a;ln=np.linalg.norm(d)
    if ln<.03:return
    m=trimesh.creation.cylinder(radius=rad,height=ln,sections=7);m.apply_transform(trimesh.geometry.align_vectors([0,0,1],d/ln));m.apply_translation((a+b)/2);self.mesh(n,m,col,role)
 def panel(self,n,a,b,y0,y1,col='glass2',thick=.10,role='building'):
    a=np.asarray(a,float);b=np.asarray(b,float);v=b-a;ln=np.linalg.norm(v)
    if ln<.01:return
    m=trimesh.creation.box(extents=(ln,y1-y0,thick));rot=math.atan2(-v[1],v[0]);m.apply_transform(trimesh.transformations.rotation_matrix(rot,[0,1,0]));m.apply_translation([(a[0]+b[0])/2,(y0+y1)/2,(a[1]+b[1])/2]);self.mesh(n,m,col,role)
 def slab(self,n,poly,y0,y1,col,role='building'):self.mesh(n,polygon_prism(poly,y0,y1),col,role)
 def surface(self,n,u0,u1,v0,v1,f,col,nu=28,nv=12,thick=.25):
    U=np.linspace(u0,u1,nu);V=np.linspace(v0,v1,nv)
    grid=np.array([[f(u,v) for u in U] for v in V]);
    # patch added by original primitive with closed edges
    self.patch(n,grid,col,thick)
    self.building_parts.append((n,self.meshes[col][-1]))
 def platform(self,n,x,z,sx,sz,col='stone2',y0=.16,y1=.35):
    self.box(n,x,z,sx,sz,y0,y1,col)
 def fences(self):
    # repeated site rails omitted from QA where bridges meet the island. Preserve 4.8 road mouths.
    rx,rz=self.rx*.97,self.rz*.97;theta=np.linspace(0,2*math.pi,116,endpoint=False)
    rr=local_roads(self.code)
    valid=[]
    for t in theta:
       x,z=rx*math.cos(t),rz*math.sin(t)
       valid.append(not any(v.distance(Point(x,z))<3.0 for v in rr.values()))
    for j,t in enumerate(theta):
       if not valid[j]:continue
       x,z=rx*math.cos(t),rz*math.sin(t)
       if j%4==0:self.post('edge_safety_posts',x,z,.13,1.18,.055,'metal',6,role=None)
       q=(j+1)%len(theta)
       if valid[q]:
          xx,zz=rx*math.cos(theta[q]),rz*math.sin(theta[q]);self.girder('edge_rail',(x,1.17,z),(xx,1.17,zz),.039,'metal',role=None)
 def terrain(self):
    # Lighter multi-strata island with physically credible mass but not thick disk
    self.island()
    # toned-down rock crest sculpture accents; existing base output groups
    self.meshes['cliff_dark']=self.meshes.get('cliff_dark',[])
 def paving(self):
    # R11 routes are functional island-specific schemes: B/E loop for four bridges;
    # D/H curving perimeter spine (not a generic paved ring on every island).
    from shapely.ops import triangulate
    site=scale(Point(0,0).buffer(1,resolution=160),self.rx,self.rz)
    if self.code in ('D','H'):
        nodes=([(-12,11),(-10.9,6),(-10.9,-2.5),(-8,-7.0),(-4,-10.1),(3,-10.3),(10,-10)] if self.code=='D' else [(-15,0),(-12,-5),(-9,-9),(-2,-9),(6,-9),(9,-13)])
        line=LineString(nodes)
        corridor=line.buffer(2.4,join_style=1,cap_style=2).intersection(site)
        self.circulation=corridor
        self.gates=[('entry_public',line)]
        triangles=[q for q in triangulate(corridor) if corridor.covers(q.representative_point())]
        verts=[];faces=[]
        for t in triangles:
            p=list(t.exterior.coords)[:3];i=len(verts)
            verts.extend([[x,.148,z] for x,z in p]);faces.append([i,i+1,i+2])
        if verts:self.add('public_4_8_movement',trimesh.Trimesh(vertices=verts,faces=faces,process=False),'path')
        return
    # proposed internal island circulation: 4.8-wide continuous near-perimeter ring.
    # The external S01...S22 corridors are kept as site directions, but their actual
    # endpoints and inner-island collisions require game integration before approval.
    from shapely.ops import triangulate
    centre=scale(Point(0,0).buffer(1,resolution=160),self.rx*.77,self.rz*.77)
    corridor=centre.boundary.buffer(2.4,join_style=1,resolution=8)
    site=scale(Point(0,0).buffer(1,resolution=160),self.rx,self.rz)
    corridor=corridor.intersection(site)
    self.circulation=corridor
    self.gates=[]
    # triangulated ring, preserving the hole: no false solid disc through buildings.
    tris=[q for q in triangulate(corridor) if corridor.covers(q.representative_point()) and q.intersection(corridor).area>q.area-1e-5]
    verts=[]; faces=[]
    for t in tris:
        pp=list(t.exterior.coords)[:3];i=len(verts)
        verts.extend([[x,.145,z] for x,z in pp]);faces.append([i,i+1,i+2])
    if verts:
        self.add('island_circular_4_8_walk',trimesh.Trimesh(vertices=verts,faces=faces,process=False),'path')
    # Gate stubs in four directions close up to the new ring road; external curved
    # roads must be retargeted to actual ring gates in Codex, never auto-merge.
    for ID,line in local_roads(self.code).items():
        # outgoing vector from center within first 8 world units
        P=np.array(line.coords); q=P[-1] if np.linalg.norm(P[-1])>np.linalg.norm(P[0]) else P[0]
        q=np.asarray(q,float);norm=np.linalg.norm(q)
        if norm<1e-4:continue
        u=q/norm;probe=LineString([(0,0),(float(u[0]*self.rx*1.3),float(u[1]*self.rz*1.3))])
        gap=probe.intersection(site.boundary)
        if not gap.is_empty:
            pt=next(iter(gap.geoms),gap) if hasattr(gap,'geoms') else gap
            if hasattr(pt,'x'):
                out=np.array([pt.x,pt.y]);inner=out*.73
                line2=LineString([inner,out]);self.gates.append((ID,line2))
                crossing=line2.buffer(2.4,cap_style=2).intersection(site)
                for poly in ([crossing] if crossing.geom_type=='Polygon' else list(crossing.geoms)):
                    tri=[r for r in triangulate(poly) if poly.covers(r.representative_point())]
                    v=[];f=[]
                    for r in tri:
                        pts=list(r.exterior.coords)[:3];a=len(v);v.extend([[x,.148,z] for x,z in pts]);f.append([a,a+1,a+2])
                    if v:self.add('gate_'+ID,trimesh.Trimesh(vertices=v,faces=f,process=False),'path')

 def flora(self,items):
    for x,z,kind,s in items:self.tree(x,z,s,kind)
 def windowwall(self,n,start,end,y0,y1,segments,col='blueglass',frame='charcoal'):
    a=np.asarray(start,float);b=np.asarray(end,float)
    for i in range(segments):
       p=a+(b-a)*i/segments;q=a+(b-a)*(i+1)/segments
       self.panel(n+'_glass',p,q,y0,y1,col,role='building')
       self.post(n+'_mullion',p[0],p[1],y0,y1,.064,frame,7)
       if i%3==0:self.panel(n+'_spandrel',p,q,y0+.15,y0+.46,'warmwood',thick=.17)
    self.post(n+'_end',b[0],b[1],y0,y1,.07,frame,7)
    self.panel(n+'_head',a,b,y1-.18,y1,frame,thick=.18)

def local_roads(c):
 cx,cz=NODE[c];out={}
 for e in ROAD['allRoutesProposed']:
    if c not in (e['from'],e['to']):continue
    pts=np.asarray(e['proposedControlPointsXZ'],float)
    t=np.linspace(0,1,350)[:,None]
    if len(pts)==4: p=(1-t)**3*pts[0]+3*(1-t)**2*t*pts[1]+3*(1-t)*t**2*pts[2]+t**3*pts[3]
    else: p=(1-t)*pts[0]+t*pts[1]
    out[e['id']]=LineString(p-np.array([cx,cz]))
 return out

def build_B(s):
    """Crescent-ring communal care hub + central sensory garden; inhabitable arc, not a detached roof."""
    cx,cz=-7.2,-6.3
    # Strong crescent segment curved around a planted, open recovery garden.
    t0,t1=np.deg2rad(74),np.deg2rad(325);ts=np.linspace(t0,t1,23)
    def pt(r,t):return (cx+r*np.cos(t),cz+r*np.sin(t))
    # ring inhabited 2-storey building between radii 3.45 and 5.62
    shell=[pt(5.65,t) for t in ts]+[pt(3.55,t) for t in ts[::-1]]
    s.slab('CrescentStoneBase',shell,.2,1.04,'stone2')
    for k in range(len(ts)-1):
       a,b=pt(5.55,ts[k]),pt(5.55,ts[k+1]);p,q=pt(3.58,ts[k]),pt(3.58,ts[k+1])
       s.panel('outer_glazed_community',a,b,1.0,5.1,'blueglass',.17)
       s.panel('inner_view_veranda',p,q,1,4.85,'glass2',.12)
       # expressed structural pillars every pair bays
       if k%2==0:
           s.post('crescent_oak_outer',*a,.18,6.08,.13,'warmwood')
           s.post('crescent_oak_inner',*p,.18,5.85,.11,'wood2')
       # concrete slab partitions visible on every 2nd bay
       if k%4==1:
           s.panel('care_partition',a,p,1,4.95,'ivory',.16)
    for t in ts[::4]:
       p,q=pt(3.38,t),pt(5.86,t)
       s.girder('crescent_wide_roof_tie',(p[0],5.68,p[1]),(q[0],6.13,q[1]),.11,'wood2')
    # true double-height ribbon roof conforms to ring and connects to occupied façades
    for a,b in zip(ts[:-1],ts[1:]):
        n=5;poly=[]
        for t in np.linspace(a,b,n):poly.append(pt(6.08,t))
        for t in np.linspace(b,a,n):poly.append(pt(3.10,t))
        # offset top toward gently rising 7.3m datum, facet by segment
        height=6.2+.6*math.sin((a+b)/2*2.3)
        s.slab('warm_fanned_roof',poly,height-.3,height,'clay' if a<2.5 else 'ochre')
        # thin outer visible under-eave illuminated rim, physically attached
        aa,bb=pt(6.04,a),pt(6.04,b)
        s.panel('roof_fascia',aa,bb,height-.43,height-.17,'warmwood',.1)
    # two terminal wings tie arc to true building, not arbitrary freestanding canopies
    for t in (t0,t1):
       p=pt(4.55,t);s.hardbox('terminal_gallery',p[0],p[1],2.0,2.0,.2,5.05,'ivory')
    # sheltered therapy court and central timber garden structure
    s.platform('round_therapy_court',cx,cz,5.5,5.5,'stone',.19,.30)
    s.post('care_garden_tree',cx,cz,.3,3.0,.24,'wood',9)
    for dx,dz,rad in [(-.8,0,1.15),(.8,0,1.05),(0,.8,1.1)]: s.sphere('central_blossom',cx+dx,cz+dz,3.15,rad,'flower2',2,.78)
    # armature of entrance canopy outside north-east ring mouth, attached via two timber joists
    for x,z in [(-2.5,-2.5),(-1.7,-3.2)]:
       s.post('entrance_frame',x,z,.2,4.0,.15,'warmwood')
    s.girder('entry_crossbeam',(-2.5,4.05,-2.5),(-1.7,4.05,-3.2),.14,'wood2')
    # rail-free play area and three distinct modest planted borders
    for x,z,sx,sz in [(-10.6,-11.8,3.6,.75),(-12.1,-2.8,2.2,.65)]:s.garden(x,z,sx,sz,'lightgreen')
    s.flora([(-12.8,-9.0,'pink',.65),(-10.3,-1.6,'olive',.68)])

def build_D(s):
    """One connected, double-height civic hall with monumental folded V portal, no standalone high tower."""
    # Build occupies NE precinct, leaving diagonal S16 / S17 public crossing open.
    s.hardbox('civic_hall_lower',7.0,7.6,10.0,7.6,.2,4.0,'ivory')
    s.hardbox('civic_hall_upper',7.6,7.9,8.5,6.1,4.0,6.9,'stone')
    # offset glazing bands and deep spandrels, credible glazed inhabitable volume
    for xx in [2.1,11.9]:
       s.windowwall('west_east_civic_glazing',(xx,4.0),(xx,11.1),.92,6.82,9,'deepglass','slateblue')
    s.windowwall('north_civic_glazing',(2.1,11.37),(11.9,11.37),.8,6.72,14,'glass2','accentnavy')
    s.windowwall('south_civic_glazing',(2.1,3.82),(11.9,3.82),.8,6.72,14,'blueglass','dark')
    # architectural double wing = 2 folded thick bearing roof shells, crest along midline
    # V valley (6.5,6.9) and outward tips (x=1.3 at y9.2, x=13 at y9.5)
    for side in (-1,1):
       x1=6.95+side*5.6; xa,xb=sorted([6.95,x1]);
       def folded(u,v,side=side):
          h=7.25+2.7*(abs(u-6.95)/5.6)**1.25+.14*math.sin((v-4.0)*math.pi/7.4)
          return [u,h,v]
       s.surface('MONUMENTAL_FOLDED_CIVIC_ROOF',xa,xb,3.0,12.1,folded,'roofblue' if side<0 else 'slateblue',22,12,.38)
       for z in (3.25,6.0,9.0,11.7):
          ep=(x1,9.8,z)
          s.girder('exposed_V_support',(6.95,6.89,z),ep,.12,'charcoal')
          s.post('civic_wall_tie',x1,z,.4,9.8,.11,'stone2')
    # high central translucent roof clerestory embedded where the two roofs fold
    s.hardbox('civic_lantern',6.95,7.65,1.65,6.25,6.85,8.70,'blueglass')
    for z in np.linspace(4.4,10.9,7):s.post('lantern_fins',6.95,z,6.9,8.85,.06,'metal')
    # deep entrance steps and four two-floor arcaded columns
    for z in [4.0,6.1,8.2,10.35]:
       s.post('civic_architectural_piers',2.0,z,.18,6.88,.21,'warmwood')
       s.post('civic_architectural_piers',11.9,z,.18,6.88,.21,'warmwood')
    for z in (4.1,11.3):
       s.girder('double_public_fascia',(2.1,7.1,z),(11.9,7.1,z),.16,'bronze2')
    s.platform('public_entry_terrace',7.1,2.42,11.1,1.35,'stone',.16,.33)
    # luminous vertical data fins, NOT screen props
    for x in [3.35,4.05,4.75,9.15,9.85,10.55]:s.hardbox('civic_luminous_fins',x,3.58,.09,.19,.95,3.75,'solar')
    s.garden(-8.8,-7.3,4.9,1.0,'green')
    s.flora([(-12,-7,'olive',.68),(-7,11,'olive',.74)])

def build_E(s):
    """Asymmetric inhabited terraced geology: layered occupied floors with planted balconies, not a greenhouse."""
    # Site NE, SE access reserved, artful terraces rise progressively on opposite banks.
    base_poly=[(3.0,4.1),(10.2,3.5),(13.6,5.6),(13.0,11.4),(4.5,12.4),(2.5,9.4)]
    s.slab('rain_ecology_base_hall',base_poly,.2,3.5,'ivory')
    # intentional recessed glass lobby, divided by angled wood mullions
    s.windowwall('valley_green_gallery',(3.1,4.3),(10.3,3.65),.6,3.45,12,'deepglass','warmwood')
    s.windowwall('eco_east_glazing',(13.3,5.8),(12.8,11.0),.6,3.4,9,'glass2','charcoal')
    for i,(poly,lower,upper,topcol) in enumerate([
       ([(2.1,3.7),(13.4,3.0),(14.35,5.4),(3.2,6.8)],3.55,4.05,'lichen'),
       ([(3.0,6.5),(13.3,5.7),(13.7,9.1),(4.0,10.1)],5.05,5.58,'sage'),
       ([(4.2,9.1),(12.9,8.6),(12.9,12.8),(5.7,13.1)],6.85,7.25,'deepgreen'),
    ]):
       # habitable levels and honest supports beneath each terrace, physically connected
       s.slab(f'layer_{i}_thick_earth',poly,lower,upper,'stone2')
       s.slab(f'layer_{i}_green_crest',poly,upper,upper+.13,topcol)
       for q in poly[::2]:
           if i<2:s.post(f'floor_{i}_supports',q[0],q[1],.2,lower,.13,'warmwood')
       if i in (1,2):
           # occupied upper glass band, not another roof floating in air
           sx=3.9+i*.65;z=6.9+i*2.2
           s.hardbox(f'eco_setback_floor_{i}',8.1,z,6.7,2.45,3.42 if i==1 else 5.62,lower,'glass2')
       for q in poly[:-1]:s.post(f'layer_{i}_edge_posts',q[0],q[1],upper,upper+.5,.06,'bronze')
    # real descending blue-green water retention, small landscape feature not a copy of G's gates
    for j,(x,z,r) in enumerate([(0.4,1.1,1.35),(1.6,.0,1.1),(3.0,-1.6,1.0)]):
        s.post('rain_pond_wall',x,z,.17,.3,r,'stone2',18,role=None) # decorative, not water collider
        s.sphere('rain_basin_water',x,z,.35,r*.48,'waterblue',1,.06)
    # walking deck integrated into botanic display; modest planting groups
    s.garden(-9,7.5,5.2,1.5,'leaf')
    s.flora([(-12,10,'olive',.78),(11,-10,'olive',.75)])

def build_H(s):
    """True inhabited learning rotunda with open-book structural shell and a stepped outdoor forum."""
    # occupy north half, well clear of S19 horizontal & S20 right curve
    s.hardbox('forum_hall',-1.15,7.8,13.8,8.6,.2,5.9,'white2')
    # two deep inhabited wings and connecting glass spine; roof shape supported by all four facades
    s.hardbox('library_wing',-5.3,8.6,5.1,5.8,.2,5.7,'ivory')
    s.hardbox('STEAM_wing',3.1,8.6,5.1,5.8,.2,5.7,'stone2')
    s.hardbox('central_book_spine',-1.05,8.05,2.45,7.2,.2,7.85,'blueglass')
    # reveal glazed facade behind book leaves and a central three-storey void
    s.windowwall('library_façade',(-7.8,3.55),(-1.8,3.55),.65,5.65,10,'blueglass','slateblue')
    s.windowwall('STEAM_façade',(0.5,3.55),(5.55,3.55),.65,5.65,9,'glass2','ochre')
    s.windowwall('glazing_back',(-7.75,12.1),(5.45,12.1),.7,5.7,15,'deepglass','charcoal')
    # organic roof surface; two separate page geometries hinge at x=-1.1 and fan away, curved rise
    for side in (-1,1):
       a,b=(-8.4,-1.1) if side==-1 else (-1.1,6.55)
       def page(u,v,side=side):
         t=abs(u+1.1)/(7.5 if side>0 else 7.3)
         height=6.5+3.2*t**1.22+.44*math.sin((v-3.15)/9.2*math.pi)
         return [u,height,v]
       s.surface('HEAVY_CURVED_BOOK_PAGE',a,b,3.0,12.6,page,'roofblue' if side<0 else 'ochre',34,16,.34)
       for z in np.linspace(3.6,11.8,6):
          x=b if side>0 else a
          s.girder('engineered_laminated_beams',(-1.1,6.38,z),(x,9.55,z),.135,'bronze2')
          s.post('loadbearing_page_pier',x,z,.18,9.55,.12,'warmwood')
    for xx in [-7.0,-3.8,1.7,4.8]:
       s.post('lobby_doubleheight_columns',xx,3.8,.2,6.6,.16,'charcoal')
    # Open forum tiered amphitheater: exterior education, not little running track
    for i in range(4):s.platform('learning_theatre_step',-7,-7.5-i*.7,8.0-i*.85,.72,'stone2',.18,.36+.18*i)
    for x,z in [(-12,9.5),(10.7,10.5)]:s.tree(x,z,.7,'pink' if x<0 else 'olive')
    s.garden(0,-11,5.6,1.0,'green')

def finish_r10(s):
    """Architectural detail pass, all coordinates in recentered R9 local site.
    Structural elements, two-floor façade divisions, drainage and edge articulation.
    Sculptural primary outlines remain from R9, but replace v9 generic appearance.
    """
    C=s.code
    if C=='B':
        # Two-level curved care cloister: repeated radiused floor edges, timber columns, deep eaves
        for a in np.linspace(math.radians(74),math.radians(325),29):
            xo,zo=5.7*math.cos(a),5.7*math.sin(a)
            xi,zi=3.3*math.cos(a),3.3*math.sin(a)
            s.post('arched_care_timber_pier',xo,zo,1.0,5.35,.09,'warmwood')
            s.post('private_court_pier',xi,zi,.22,5.2,.065,'bronze2')
            s.girder('radial_structural_joist',(xi,5.15,zi),(xo,5.2,zo),.075,'wood')
            if 125<a*180/math.pi<295:
                s.post('vertical_cloister_fins',xi,zi,1.2,4.55,.045,'ochre')
        # integrated second-floor balcony ring facing healing garden
        ang=np.linspace(math.radians(74),math.radians(325),55)
        for aa,bb in zip(ang[:-1],ang[1:]):
            p=(3.27*math.cos(aa),3.27*math.sin(aa));q=(3.27*math.cos(bb),3.27*math.sin(bb))
            s.panel('community_balcony_band',p,q,2.9,3.15,'ivory',.14)
            s.panel('upper_gallery_rail',p,q,3.9,3.96,'bronze2',.12)
        # radial pergola + solar blind frame at public entrance between roof terminals
        for a in np.linspace(math.radians(0),math.radians(70),7):
            p=(3.25*math.cos(a),3.25*math.sin(a));q=(6.1*math.cos(a),6.1*math.sin(a))
            s.girder('entrance_bamboo_ceiling',(p[0],4.9,p[1]),(q[0],4.9,q[1]),.07,'ochre')
        # true entry with rectangular glazed service front on lower east end of crescent
        s.hardbox('care_welcome_counter_volume',3.9,-3.2,2.8,1.4,.2,1.55,'ivory')
        s.panel('care_welcome_glazed_counter',(2.6,-3.9),(5.2,-3.9),1.4,2.9,'blueglass',.16)
        # climatic stone ring; small color contrast avoiding all-grass carpet
        for x,z,sz in [(-7.0,-6.5,1.0),(5.7,-5.2,1.2)]:s.garden(x,z,2.0,sz,'leaf')
    elif C=='D':
        # True public service architecture: façade divided into a rational two-floor structural grid
        for x in np.linspace(-4.55,4.65,12):
            for z in (-3.82,4.08):
                s.post('floor_to_floor_steel_frame',x,z,.25,6.85,.095,'charcoal')
                s.hardbox('two_storey_spandrel',x,z,.13,.21,3.14,3.58,'ivory')
        for z in np.linspace(-3.5,4.2,9):
            for x in (-5.05,4.95):
                s.post('civic_glazed_side_frames',x,z,.3,6.86,.075,'warmwood')
        # large continuous suspended glazed foyer under the hinge of the 7-m civic roof
        s.hardbox('recessed_civic_glass_entry',-.05,-3.9,4.6,.18,.34,5.95,'glass2')
        for x in np.linspace(-2.25,2.15,7):s.post('portal_mullion',x,-3.98,.32,5.95,.075,'charcoal')
        # structural luminous fascia and bronze seam make two wings one building
        for side in (-1,1):
           for z in np.linspace(-4.13,4.38,10):
               u=side*5.6; roofh=7.25+2.7+.14*math.sin((z+3.3)*math.pi/7.4)
               s.girder('wing_truss_under_crest',(0,7.14,z),(u,roofh-.35,z),.11,'ivory')
               s.post('civic_secondary_column',u*.88,z,.2,roofh-.5,.09,'stone2')
        # low bench walls + planting directly in the civic court, away from route ring
        for x,z in [(-5.7,6.0),(5.9,6.0)]:
           s.hardbox('civic_entry_terrace_wing',x,z,1.4,.9,.18,.52,'stone2')
        s.hardbox('civic_placemaking_spine',0,-5.9,3.7,.32,.2,1.7,'charcoal')
        s.hardbox('digital_service_fascia',0,-5.7,3.2,.08,.72,1.35,'solar')
    elif C=='E':
        # Three real inhabited floors, no free-floating roof sheets: all sides have façade depth.
        for x in np.linspace(-3.5,5.6,11):
            s.post('eco_first_floor_mullions',x,-4.42,.28,3.65,.11,'warmwood')
            s.hardbox('eco_vertical_shading_louver',x,-4.62,.07,.32,1.55,3.45,'ochre')
        for y,z0,x0,x1 in [(4.17,-3.2,-3.9,6.3),(5.70,.2,-2.5,6.1),(7.35,3.1,-1.6,5.8)]:
            s.hardbox('eco_habitable_soffit', (x0+x1)/2,z0,x1-x0,.3,y-.3,y,'warmwood')
            for x in np.linspace(x0,x1,9):s.post('eco_hanging_vine_screen',x,z0,y-.6,y+.22,.055,'darkolive')
        # diagonal sheltered transition 'green stair': vertically legible tiers, not floating planes.
        for i in range(6):
            x=-5.4+i*.92;z=1.6+i*.5
            s.hardbox('rain_garden_stepped_bridge',x,z,.84,1.75,.20+i*.39,.56+i*.39,'stone2')
            s.hardbox('integrated_plant_stripe',x,z,.72,.48,.56+i*.39,.65+i*.39,'leaf')
        # rain observation tubes/planted terraces as engineering detail, low cost
        for i in range(5):
            s.post('watershed_vertical_scale',4.5+i*.35,-4.25,.34,2.75,.04,'bronze2')
    elif C=='H':
        # Page canopy integrated with two occupied wings; visible structure on all four elevations.
        for z in np.linspace(-4.45,4.2,13):
            for x in (-6.45,-2.55,2.55,6.45):
                s.post('literacy_center_glulam_posts',x,z,.2,6.1,.10,'ochre')
        for x in np.linspace(-6.2,6.3,16):
            for z in (-4.42,4.38):
                s.post('STEAM_twofloor_mullion',x,z,.45,5.9,.065,'charcoal')
                s.hardbox('STEAM_floor_band',x,z,.17,.19,3.0,3.33,'ivory')
        # Book spine is a real multi-storey skylight with vertical mullions and deep cast roof ridge
        for z in np.linspace(-4.3,4.6,9):
            s.post('skylight_book_spine',0,z,5.3,8.2,.085,'slateblue')
        s.hardbox('book_spine_toplight',0,0,.52,8.9,8.0,8.42,'lightteal')
        # modest outside learning forum, built as a stepped retaining bowl
        for i in range(3):
            s.hardbox('learning_forum_solid_step',-.2,6.15+i*.58,5.0-i*.5,.54,.21+i*.21,.44+i*.21,'stone')
        s.hardbox('learning_mural_wall',-6.3,0,.24,3.2,.3,3.2,'solar')
        s.hardbox('learning_mural_frame',-6.3,0,.32,3.5,3.1,3.35,'ochre')

BUILDS={'B':build_B,'D':build_D,'E':build_E,'H':build_H}

def audit(s):
  """Check actual building meshes' horizontal hull against island and route 4.8 cores."""
  island=scale(Point(0,0).buffer(1,resolution=200),s.rx*.98,s.rz*.98)
  route=s.circulation.union(unary_union([v.buffer(2.4,cap_style=2) for _,v in s.gates]))
  rows=[]
  for name,mesh in s.building_parts:
      b=mesh.bounds; hull=Polygon(mesh.vertices[:,[0,2]]).convex_hull
      if hull.is_empty: continue
      outside=hull.difference(island).area
      overlap=hull.intersection(route).area
      rows.append(dict(name=name,outside=round(float(outside),3),roadOverlap=round(float(overlap),3)))
  return dict(island=s.code,dimensions=SIZES[s.code],centre=NODE[s.code],buildingMeshes=len(rows),outsideAreaTotal=round(sum(r['outside'] for r in rows),3),roadCoreOverlapTotal=round(sum(r['roadOverlap'] for r in rows),3),failures=[x for x in rows if x['outside']>.01 or x['roadOverlap']>.01]);

def export_and_render(s):
  import vtk
  from vtk.util.numpy_support import numpy_to_vtk
  scene=trimesh.Scene();nfaces=0
  for color,meshes in s.meshes.items():
     if not meshes:continue
     joined=trimesh.util.concatenate(meshes);joined.visual.face_colors=np.array([*base.rgb(C[color]),255],dtype=np.uint8)
     scene.add_geometry(joined,geom_name=color);nfaces+=len(joined.faces)
  p=ROOT/'models'/f'{s.code}_R8_rebuildable.glb';p.write_bytes(scene.export(file_type='glb'))
  def render(view):
    ren=s.vtk_renderer();ren.GradientBackgroundOff();ren.SetBackground(.91,.941,.949)
    # enable 3D depth cues with offscreen lighting
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(1120,900);win.SetMultiSamples(4);win.AddRenderer(ren)
    cam=ren.GetActiveCamera();cam.ParallelProjectionOn();cam.SetViewUp(0,1,0);cam.SetFocalPoint(0,1.0,0)
    cam.SetPosition(*({'hero':(40,35,-43),'front':(0,14,-65),'back':(0,14,65),'left':(-65,14,0),'right':(65,14,0),'top':(0.01,100,.02)}[view]))
    if view=='top':cam.SetViewUp(0,0,-1)
    cam.SetParallelScale(19 if view!='top' else 19.5)
    ren.ResetCameraClippingRange();win.Render()
    w2i=vtk.vtkWindowToImageFilter();w2i.SetInput(win);w2i.SetInputBufferTypeToRGB();w2i.ReadFrontBufferOff();w2i.Update();w=vtk.vtkPNGWriter();w.SetInputConnection(w2i.GetOutputPort());q=ROOT/'renders'/f'{s.code}_{view}.png';w.SetFileName(str(q));w.Write();win.Finalize();return q
  for v in ('hero','front','back','left','right','top'):render(v)
  return dict(name=s.code,triangles=nfaces,GLBBytes=p.stat().st_size,materials=len(s.meshes),file=p.name)

def run():
   qa={};models=[]
   for code in 'BDEH':
       s=Design(code);s.terrain();s.paving();
       pre_counts={k:len(v) for k,v in s.meshes.items()}
       BUILDS[code](s)
       shift={'B':(7.2,6.3),'D':(-7.0,-7.3),'E':(-6.9,-7.5),'H':(1.1,-7.8)}[code]
       for color,lst in s.meshes.items():
           for mesh in lst[pre_counts.get(color,0):]:mesh.apply_translation([shift[0],0,shift[1]])
       finish_r10(s);s.fences()
       qa[code]=audit(s);models.append(export_and_render(s))
       print(code,'tris',models[-1]['triangles'],'QA fails',len(qa[code]['failures']),flush=True)
   (ROOT/'qa'/'mesh_plan_audit.json').write_text(json.dumps(qa,indent=2,ensure_ascii=False))
   (ROOT/'qa'/'mesh_stats.json').write_text(json.dumps(models,indent=2))
if __name__=='__main__':run()
