"""Original V9 elevated station artwork. No hall/curved-roof templates or proxy meshes.
MIT. Author coordinates are Sky Isles X east / Y up / Z north; Blender X/-Z/Y.
"""
import bpy,bmesh,math,random,json,sys
from pathlib import Path
from mathutils import Vector
from shapely.geometry import Polygon,Point,LineString,box as rect
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles,set_precision
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import parent_child_geometry as G
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/design/transport-elevated-station-v9-prototype'
W=lambda p:Vector((p[0],-p[2],p[1]))

class Station:
 def __init__(self):
  bpy.ops.wm.read_factory_settings(use_empty=True);G._ico_cache.clear();self.rng=random.Random(74161209);self.M={};self.groups={};self.proxies=[];self.details=0
  G.collection('00_MODEL');self.root=G.empty('YuanliElevatedStationV9');self.root['role']='Independent original high-detail art; NOT V9 proxy geometry; NOT game integration';self.root['worldAxes']='X east / Y up / Z north; Blender X / -Z / Y';self.root['source_reference']='inputs/approved-v9/美術參考_高架車站.png'
  for key in ['Terrain','Paving','Hall','Viaduct','Canopy','TrainRollingStock','Railway','VerticalCirculation','Gardens','Furniture','Identity']:
   G.collection(key);self.groups[key]=G.empty(key,self.root)
  self.use('Hall');self.palette();r=json.loads((ROOT/'work/transport-v9-reference-measured.json').read_text());self.referenceSite=unary_union([Polygon(t)for t in r['siteTopTrianglesXZ']]);assert self.referenceSite.area>330;self.site=self.referenceSite.union(Point(-6.70,5.20).buffer(2.05,quad_segs=20)).union(Point(6.70,5.20).buffer(2.05,quad_segs=20)).buffer(.10).buffer(-.10);self.root['localGardenTerraceProposalOnly']=True
  self.plan=json.loads((ROOT/'src/data/yuan-plan.json').read_text());self.lines={e['id']:self.edge(e)for e in self.plan['edges']};self.mouths=unary_union([self.lines[k].buffer(2.4,cap_style=2)for k in ['S09','S10','S15','S18']]);self.npc=[rect(x-1.5,3.93-1.5,x+1.5,3.93+1.5)for x in [-3.7,3.65]]
 def edge(self,e):
  c=e['controlPointsXZ']
  if len(c)==2:return LineString(c)
  return LineString([tuple((1-t)**3*c[0][a]+3*(1-t)**2*t*c[1][a]+3*(1-t)*t*t*c[2][a]+t**3*c[3][a]for a in [0,1])for t in [i/400 for i in range(401)]])
 def use(self,key):G.COL=bpy.data.collections[key];self.parent=self.groups[key]
 def mat(self,n,c,r=.6,metal=0,trans=0,emit=0):
  m=G.material(n,c,r,metal,trans);self.M[n]=m
  if emit:
   p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(*G.linear(c),1);p.inputs['Emission Strength'].default_value=emit
  return m
 def palette(self):
  for n,c,r,me,tr in [('stone','D4C9BC',.76,0,0),('cream','EEE8DA',.65,0,0),('concrete','C1BDB4',.79,0,0),('shadowStone','ACA99F',.82,0,0),('rock','A7A59B',.95,0,0),('darkRock','858F8D',.96,0,0),('roof','778A9B',.46,.46,0),('roofDark','687E8E',.43,.48,0),('roofEdge','9DAEB7',.31,.65,0),('steel','667D82',.31,.72,0),('rail','3B7180',.36,.58,0),('wood','C08B55',.55,0,0),('woodLight','DBB47C',.52,0,0),('woodDark','8E6544',.66,0,0),('glass','DDECE8',.04,0,.98),('trainGlass','486E7A',.16,.08,.68),('trainWhite','E6EDF0',.28,.24,0),('trainBlue','3B8699',.33,.32,0),('yellow','E8BF68',.55,.1,0),('rubber','374248',.68,0,0),('soil','74664E',.95,0,0),('leafDark','496A3C',.85,0,0),('leaf','76954C',.84,0,0),('leafLight','9AB765',.82,0,0),('leafTip','BDCD7F',.8,0,0),('petal','F2E7BD',.67,0,0),('petalPink','E3A89F',.7,0,0),('paverA','DDD4C5',.85,0,0),('paverB','E8DFD0',.82,0,0),('paverC','CFC6B6',.89,0,0),('floor','CEBCA1',.74,0,0)]:self.mat(n,c,r,me,tr)
  self.mat('light','FFDF9F',.4,0,0,3);self.mat('screen','EFD28C',.48,0,0,.55);self.mat('navy','345768',.45,.2,0)
  # The subtle wood grain is a packed original 256px procedural texture, exported in GLB.
  import numpy as np
  rng=np.random.default_rng(902);xx=np.arange(256)[None,:];yy=np.arange(256)[:,None];grain=.035*np.sin(yy*.67+np.sin(xx*.035)*2)+.014*rng.normal(size=(256,256));texture=bpy.data.images.new('OriginalWarmWoodGrain',width=256,height=256);base=np.array([.49,.29,.12]);rgb=np.clip(base+grain[:,:,None],0,1);rgba=np.concatenate([rgb,np.ones((256,256,1))],axis=2);texture.pixels.foreach_set(rgba.astype('float32').ravel());texture.filepath_raw=str(OUT/'textures/original-wood-grain.png');texture.file_format='PNG';Path(texture.filepath_raw).parent.mkdir(parents=True,exist_ok=True);texture.save();texture.pack()
  for name in ['wood','woodLight']:
   mat=self.M[name];nodes=mat.node_tree.nodes;tex=nodes.new('ShaderNodeTexImage');tex.image=texture;mat.node_tree.links.new(tex.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color'])
 def uv(self,o):
  if o.type!='MESH' or o.data.uv_layers:return o
  uv=o.data.uv_layers.new(name='ArchitecturalUV')
  for f in o.data.polygons:
   axis=max(range(3),key=lambda a:abs(f.normal[a]));axes=[a for a in range(3)if a!=axis]
   for li in f.loop_indices:
    v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]*.65,v[axes[1]]*.65)
  return o
 def box(self,n,p,d,m='cream',bevel=.018,parent=None):
  o=G.box(n,W(p),(d[0],d[2],d[1]),self.M[m],parent or self.parent,bevel);self.uv(o);return o
 def beam(self,n,a,b,w=.07,m='steel',parent=None):return self.uv(G.beam(n,W(a),W(b),w,self.M[m],parent or self.parent))
 def cyl(self,n,p,r,h,m='steel',v=16,parent=None):return G.cylinder(n,W(p),r,h,self.M[m],parent or self.parent,v)
 def ball(self,n,p,s,m='leaf',sub=1,parent=None):return G.sphere(n,W(p),(s[0],s[2],s[1]),self.M[m],parent or self.parent,sub)
 def group(self,n):return G.empty(n,self.parent)
 def mesh(self,n,pts,faces,m,parent=None,smooth=False):
  o=G.mesh(n,[W(p)for p in pts],faces,self.M[m],parent or self.parent,smooth);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free();o.data.update();return self.uv(o)
 def solid(self,n,poly,y0,y1,m='stone',parent=None):
  poly=set_precision(poly,1e-5)
  if poly.is_empty:return
  if poly.geom_type=='MultiPolygon':return [self.solid(n,g,y0,y1,m,parent)for g in poly.geoms if g.area>1e-5]
  poly=orient(Polygon([(x,-z)for x,z in poly.exterior.coords],[[(x,-z)for x,z in h.coords]for h in poly.interiors]),1);verts=[];faces=[];look={}
  def idx(x,z,y):
   key=(round(x,6),round(z,6),round(y,6))
   if key not in look:look[key]=len(verts);verts.append(key)
   return look[key]
  for tri in constrained_delaunay_triangles(poly).geoms:
   if not poly.covers(tri):continue
   pts=list(orient(tri,1).exterior.coords)[:3];faces.extend([tuple(idx(x,z,y1)for x,z in pts),tuple(idx(x,z,y0)for x,z in reversed(pts))])
  for ring in [poly.exterior,*poly.interiors]:
   pts=list(ring.coords)
   for (x,z),(xx,zz)in zip(pts,pts[1:]):faces.append((idx(x,z,y0),idx(xx,zz,y0),idx(xx,zz,y1),idx(x,z,y1)))
  return G.mesh(n,verts,faces,self.M[m],parent or self.parent)
 def proxy(self,n,kind,poly,y0,y1,role='solid'):
  self.proxies.append({'id':n,'kind':kind,'polygonXZ':list(poly.exterior.coords),'bottom':y0,'top':y1,'role':role,'integrationImplemented':False})
 def text(self,n,string,p,size,m='navy',parent=None,face='front'):
  c=bpy.data.curves.new(n,'FONT');c.body=string;c.size=size;c.align_x='CENTER';c.align_y='CENTER';c.resolution_u=5;c.fill_mode='BOTH'
  if not hasattr(self,'font'):self.font=bpy.data.fonts.load('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
  c.font=self.font;o=bpy.data.objects.new(n,c);G.COL.objects.link(o);bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');me=o.data;me.calc_loop_triangles()
  # Union actual font triangles, then extrude closed glyph solids. No unsealed font cap seams.
  poly=unary_union([Polygon([(me.vertices[i].co.x,me.vertices[i].co.y)for i in t.vertices])for t in me.loop_triangles]);from shapely.affinity import scale;poly=scale(poly,xfact=size/(poly.bounds[3]-poly.bounds[1]),yfact=size/(poly.bounds[3]-poly.bounds[1]),origin=(0,0));verts=[];faces=[];lookup={}
  def ix(x,y,z):
   key=(round(x,7),round(y,7),z)
   if key not in lookup:lookup[key]=len(verts);verts.append(key)
   return lookup[key]
  parts=list(poly.geoms)if poly.geom_type=='MultiPolygon'else[poly]
  for poly in parts:
   poly=orient(poly,1)
   for tri in constrained_delaunay_triangles(poly).geoms:
    if not poly.covers(tri):continue
    pts=list(orient(tri,1).exterior.coords)[:3];faces.extend([tuple(ix(x,y,.012)for x,y in pts),tuple(ix(x,y,0)for x,y in reversed(pts))])
   for ring in [poly.exterior,*poly.interiors]:
    pts=list(ring.coords)
    for (x,y),(xx,yy)in zip(pts,pts[1:]):faces.append((ix(x,y,0),ix(xx,yy,0),ix(xx,yy,.012),ix(x,y,.012)))
  bpy.data.objects.remove(o,do_unlink=True);bpy.data.meshes.remove(me);o=G.mesh(n,verts,faces,self.M[m],parent or self.parent);o.location=W(p);o.rotation_euler=(math.pi/2,0,0)if face=='front'else(math.pi/2,0,math.pi/2);o['textContent']=string;return o
 def railing(self,n,line,y0=0,height=1.05,m='rail',postSpacing=1.0):
  if line.is_empty:return
  if line.geom_type=='MultiLineString':
   for i,l in enumerate(line.geoms):self.railing(n+str(i),l,y0,height,m,postSpacing)
   return
  pts=list(line.coords)
  for i,(a,b)in enumerate(zip(pts,pts[1:])):
   if math.dist(a,b)<.005:continue
   for h in [.48,height]:self.beam(n+'_Rail',(a[0],y0+h,a[1]),(b[0],y0+h,b[1]),.036,m)
  for i in range(max(1,math.ceil(line.length/postSpacing))+1):
   q=line.interpolate(min(i*postSpacing,line.length));self.box(n+'_Post',(q.x,y0+height/2,q.y),(.047,height,.047),m,.006)
  self.proxy(n,'guard',line.buffer(.035,cap_style=2),y0,y0+height)
 def bench(self,n,x,z,yaw=0,width=1.7,y=.06):
  self.use('Furniture');p=self.group(n)
  for j in range(5):self.box(n+'_Seat',((j-2)*.1,y+.47,0),( .085,.065,width),'woodLight',.009,p)
  for xx in [-.2,.2]:
   for zz in [-width*.39,width*.39]:self.box(n+'_Leg',(xx,y+.23,zz),(.055,.46,.065),'rail',.008,p)
  for yy in [.76,.93]:self.box(n+'_Back',(-.25,y+yy,0),(.06,.12,width),'wood',.012,p)
  for zz in [-width*.38,width*.38]:self.beam(n+'_Upright',(-.25,y+.4,zz),(-.25,y+1.02,zz),.045,'rail',p)
  p.location=W((x,0,z));p.rotation_euler.z=yaw;from shapely.affinity import rotate;foot=rotate(rect(x-.35,z-width/2,x+.35,z+width/2),-math.degrees(yaw),origin=(x,z));self.proxy(n,'furniture',foot,.06,1.05)
 def tree(self,n,x,z,h=3.3,r=1.05):
  self.use('Gardens');p=self.group(n);self.cyl(n+'_Trunk',(x,h*.30,z),.14,h*.60,'woodDark',12,p)
  rng=self.rng
  for j in range(7):
   a=j*2.39996;xx=x+math.cos(a)*r*.65;zz=z+math.sin(a)*r*.65;hh=h*(.65+.09*(j%3));self.beam(n+'_Branch',(x,h*.4,z),(xx,hh,zz),.065,'woodDark',p)
   for k in range(18):
    az=rng.uniform(0,math.tau);rr=rng.uniform(.15,.56)*r;py=hh+rng.uniform(-.30,.40)*r;s=rng.uniform(.17,.30)*r
    o=self.ball(n+'_LeafCluster',(xx+rr*math.cos(az),py,zz+rr*math.sin(az)),(s*1.3,s*.8,s),['leafDark','leaf','leafLight','leafTip'][(j+k)%4],1,p);o['candidateDetail']=1 if k%4==0 else 0
  self.proxy(n,'trunk',Point(x,z).buffer(.18),.06,h*.6)
 def plantbed(self,n,poly,tree=None):
  assert all(poly.intersection(q).area<.00001 for q in self.npc),(n,'NPC intrusion')
  assert self.site.buffer(.002).covers(poly),(n,'outside site')
  self.use('Gardens');p=self.group(n);self.solid(n+'_Retaining',poly,.06,.38,'cream',p);inner=poly.buffer(-.10);self.solid(n+'_Soil',inner,.38,.405,'soil',p)
  for j in range(max(5,round(inner.area*8))):
   for attempt in range(40):
    x=self.rng.uniform(inner.bounds[0],inner.bounds[2]);z=self.rng.uniform(inner.bounds[1],inner.bounds[3])
    if inner.contains(Point(x,z)):break
   r=self.rng.uniform(.17,.28)
   for k in range(3):
    a=k*2.09;self.ball(n+'_Shrub',(x+.1*math.cos(a),.51+(.06 if k==1 else 0),z+.1*math.sin(a)),(r,r*.75,r),['leaf','leafDark','leafLight'][k],1,p)
   if j%1==0:
    for k in range(3):
     az=k*2.39;xx=x+.12*math.cos(az);zz=z+.12*math.sin(az)
     for a in range(5):
      aa=a*math.tau/5;oo=self.ball(n+'_Petal',(xx+.042*math.cos(aa),.82,zz+.042*math.sin(aa)),(.067,.030,.046),'petalPink'if j%4==0 else'petal',1,p);oo['candidateDetail']=1 if k==2 else 0
     self.ball(n+'_Pollen',(xx,.845,zz),(.022,.018,.022),'yellow',1,p)
  self.proxy(n,'planter',poly,.06,.85)
  if tree:self.tree(n+'_Tree',*tree)
 def light(self,n,pos,target,power,size,col):
  G.COL=bpy.data.collections['90_STUDIO'];d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=col;o=bpy.data.objects.new(n,d);G.COL.objects.link(o);o.location=W(pos);o.rotation_euler=(W(target)-o.location).to_track_quat('-Z','Y').to_euler()
