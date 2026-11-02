"""G-only generated site, art parts and semantic collision, from one authored plan.
No proxy terrain, routes, partial rails, lights or NPC meshes are imported.
"""
from pathlib import Path
import json,math,sys,hashlib
import numpy as np
import trimesh
from shapely.geometry import Polygon,MultiPolygon,LineString,Point,MultiPoint,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path(__file__).resolve().parents[2];D=R/'docs/design/flood-control-island-g-v5';W=R/'work/g-v5';W.mkdir(parents=True,exist_ok=True)
P=json.loads((R/'src/data/flood-control-plan.json').read_text());C=P['centre'];shell=Polygon(P['footprintLocal']);up=Polygon(P['water']['upstream']);low=Polygon(P['water']['downstream']);throats=[Polygon(r)for r in P['sluiceThroats']];waters=unary_union([up,low,*throats]);dry=shell.difference(waters)
def load(p):return json.loads((R/p).read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n')
def polygons(p):return [p]if p.geom_type=='Polygon'else [g for g in p.geoms if g.geom_type=='Polygon']
def domain(p):return [[list(map(list,g.exterior.coords)),*[list(map(list,r.coords))for r in g.interiors]]for g in polygons(p)]
def fromdomain(p):return unary_union([Polygon(r[0],r[1:])for r in p])
layout=load('src/data/yuan-layout.json');lines={}
for route in layout['paths']:
 if route['id']in ['S20','S21','S22']:lines[route['id']]=LineString([(v['x']-C[0],v['z']-C[2])for v in route['points']])
roads=unary_union([lines[s].buffer(P['crossingHalfWidth'],cap_style=2,join_style=2)for s in ['S21','S22']]).intersection(shell)
inspection=box(*P['crosswalk']);accessible=dry.union(roads).union(inspection).intersection(shell);holes=shell.difference(accessible)
path=LineString(P['publicCircuit']).buffer(.95,cap_style=2,join_style=1)
npc=P['npc'][0];nx,_,nz=npc['position'];npcarea=box(nx-1.5,nz-1.5,nx+1.5,nz+1.5)
paving=unary_union([roads,path,npcarea,inspection,box(5.0,-.7,10.5,1.15)]).intersection(accessible)
def triangles(p,y):
 verts=[];faces=[]
 for poly in polygons(p):
  for t in constrained_delaunay_triangles(poly).geoms:
   q=list(t.exterior.coords)[:3];idx=len(verts);vs=np.array([[x,y,z]for x,z in q]);
   if np.cross(vs[1]-vs[0],vs[2]-vs[0])[1]<0:vs=vs[[0,2,1]]
   verts.extend(vs.tolist());faces.append([idx,idx+1,idx+2])
 return verts,faces
site={'revision':'G-V5','floor':domain(accessible),'dryLand':domain(dry),'water':domain(waters),'waterHoles':domain(holes),'protectedRoads':domain(roads),'paving':domain(paving),'crossing':domain(roads.intersection(waters)),'waterRails':[]}
for poly in polygons(holes):
 for ring in [poly.exterior,*poly.interiors]:
  cs=list(ring.coords)
  for a,b in zip(cs[:-1],cs[1:]):
   if math.dist(a,b)>.015:site['waterRails'].append({'a':list(a),'b':list(b),'coveredCrossing':roads.boundary.distance(LineString([a,b]).interpolate(.5,normalized=True))<.03})
if '--site'in sys.argv:
 yuan=load('src/data/yuan-plan.json');yuan['islandFootprintsXZ']['G']=[[round(x+C[0],5),round(z+C[2],5)]for x,z in P['footprintLocal']];yuan['landscapeRetainedLampAnchors']=list(dict.fromkeys(yuan.get('landscapeRetainedLampAnchors',[])+P['retainedExistingLampIds']+P['preserveLampAnchors']));(R/'src/data/yuan-plan.json').write_text(json.dumps(yuan,ensure_ascii=False,indent=2)+'\n')
 save(R/'src/data/flood-control-site.json',site)
 for file,geom,y in [('flood-control-floor.json',accessible,0),('flood-control-paving.json',paving,P['publicY'])]:
  v,f=triangles(geom,y);save(R/'src/data'/file,{'vertices':v,'triangles':f})
 vv,ff=triangles(roads.intersection(waters),-.395);ff=[list(reversed(f))for f in ff]
 save(R/'src/data/flood-control-bridge-soffit.json',{'revision':'G-V5','vertices':vv,'triangles':ff,'minimumWaterClearance':1.405,'note':'S22 deck actual underside -.395, lower pool -1.8. No water floor collider.'})
 print('G V5 floor/water holes, crossing and footprint source generated');sys.exit(0)
# Execute only the supplied geometry section, never its export or rasterizer.
source=(D/'source-package/build.py').read_text();ns={};exec(compile(source[:source.index('# finish mesh assembly')],str(D/'source-package/build.py'),'exec'),ns)
parts=[];mats=ns['COL'].copy();mats.update({'interior':(.78,.69,.52),'chair':(.27,.43,.40),'ripple':(.47,.76,.73)})
def add(mesh,mat,name,role='props',solid=False,roof=False,head=False):
 m=trimesh.Trimesh(vertices=np.array(mesh.vertices),faces=np.array(mesh.faces),process=False)
 if np.ptp(m.vertices[:,1])>.001:
  flip=np.einsum('ij,ij->i',m.face_normals,m.triangles_center-m.vertices.mean(axis=0)) < -1e-8
  m.faces[flip]=m.faces[flip][:,::-1]
 parts.append({'mesh':m,'mat':mat,'name':name,'role':role,'solid':solid,'roof':roof,'head':head})
def cube(name,c,s,mat='concrete',role='command',solid=True,roof=False,head=False):
 m=trimesh.creation.box(s);m.apply_translation(c);add(m,mat,name,role,solid,roof,head)
def rod(name,a,b,r=.045,mat='steel',role='rails',solid=False):
 a=np.array(a);b=np.array(b);d=b-a;L=np.linalg.norm(d)
 if L<.012:return
 m=trimesh.creation.cylinder(radius=r,height=L,sections=8);m.apply_transform(trimesh.geometry.align_vectors([0,0,1],d/L));m.apply_translation((a+b)/2);add(m,mat,name,role,solid)
def slab(name,geom,y,depth,mat,role='terrain',ground=False):
 v,f=triangles(geom,y)
 if f:add(trimesh.Trimesh(vertices=v,faces=f,process=False),mat,name,role);parts[-1]['ground']=ground
 if depth:
  for poly in polygons(geom):
   for ring in [poly.exterior,*poly.interiors]:
    cs=list(ring.coords)
    for a,b in zip(cs[:-1],cs[1:]):
     add(trimesh.Trimesh(vertices=[[a[0],y,a[1]],[b[0],y,b[1]],[b[0],y-depth,b[1]],[a[0],y-depth,a[1]]],faces=[[0,1,2],[0,2,3]],process=False),mat,name+' side',role)
pass1='--pass1'in sys.argv
omit=('floating','actual dry','upstream basin water','downstream flood basin','reinforced flood','basin coping','island rim','falling stepped','water turbulence','protected S','S22 ','north water','inspection ','NPC future','guide plaza','raised garden','planted grass','tree trunk','mixed woodland','site light','architectural LED','riverside seating','bench supports')
core_omit={'control centre ground podium','upper command glazed volume','emergency services annex','tower glazing envelope'}
for item in ns['items']:
 n=item['name'];m=item['mesh']
 if n.startswith(('public flood information','info ')):m.apply_translation([-1.795,0,4.829])
 if n.startswith(('flood gauge podium','levee benchmark pole','high water warning head','vertical high water graduation')):m.apply_translation([9.6,0,2.2])
 if n.startswith(omit)or n in core_omit or(not pass1 and (n=='hoist service catwalk'or n in ['control room glass panel','control room front mullion','glass side module','side mullion','rear control glass panel','rear control fin mullion','emergency wing glazing','emergency window dividers','command civic vertical fin'])):continue
 if not pass1 and n=='massive dam bridge crossbeam':m.apply_translation([0,0,-.045])
 role='gate'if any(k in n for k in ['dam','gate','hoist','pier','sluice','gear'])else 'command'if any(k in n for k in ['command','control','facade','glass side','mullion','rear control','civic','observation','observatory','sensor mast','sensor cap','public entrance','entrance soffit','canopy support','closed command','emergency','annex','vent','front facade','sun shade','solar roof','side mullion','info '])else'props'
 is_rail=any(k in n for k in ['guardrail','baluster']);solid=(n in ['dam walkway baluster','dam walkway guardrail'])or (not is_rail and any(k in n for k in ['major dam pier','shear wall','deep steel leaf','front mullion','side mullion','rear control fin','vertical fin','canopy support','closed command lobby','public flood information','flood gauge podium','benchmark pole','sensor podium','sensor pylon','layered flood protection earth berm','levee vegetated crest']))
 roof=any(k in n for k in ['command cantilever roof','emergency centre wing roof','civic observation crown','hoist service catwalk','massive dam bridge crossbeam','public entrance canopy'])
 add(m,item['mat'],n,role,solid,roof,roof)
# Replace all proxy land/floors, and cut real hydraulic throats between the pools.
slab('Dry terrain with continuous hydraulic voids',dry,0,.32,'green','terrain',True)
slab('Paved public floors and S22 full structural bridge deck',paving,P['publicY'],.30,'floor','terrain',True)
# Inspection promenade is already in the paved union; do not stack coplanar slabs.
# A beam-backed slab also under the full wet crossing shoulders, not just the visible core.
slab('S22 load bearing wet crossing underside',roads.intersection(waters),-.275,.12,'concrete2','crossing')
vv,ff=triangles(roads.intersection(waters),-.395);ff=[list(reversed(f))for f in ff];add(trimesh.Trimesh(vertices=vv,faces=ff,process=False),'concrete2','S22 actual continuous soffit','crossing',False,False,True)
for depth,scale,mat in [(-.32,1.0,'rock2'),(-2.3,.87,'rock'),(-4.3,.58,'rock3')]:
 ring=[(x*scale,z*scale)for x,z in P['footprintLocal']]
 slab('Layered floating foundation',Polygon(ring).difference(waters)if scale==1 else Polygon(ring),depth,1.45,mat,'terrain')
slab('Upstream retained water',up,-.66,.025,'water_upper','water');slab('Downstream retention water',low,-1.8,.025,'water_lower','water')
# Real hydraulic surfaces through the three open throats, with anchored pier feet.
for i,x in enumerate([-12.45,-9.35,-6.25]):
 for j in range(8):
  z1=7.25-j*.74;z2=z1-.74
  def level(z):return -.66 if z>=6.8 else max(-1.8,-.66-(6.8-z)*1.14/5.45)
  a=level(z1);b=level(z2);v=[[x-1.02,a,z1],[x+1.02,a,z1],[x+1.02,b,z2],[x-1.02,b,z2]];f=[[0,1,2],[0,2,3]]
  add(trimesh.Trimesh(vertices=v,faces=f,process=False),'water_lower','Continuous gate discharge '+str(i),'water')
  if j%2==0:rod('Surface-following discharge foam',[x-.86,b+.02,z2],[x+.86,b+.02,z2],.014,'foam','water')
for x in [-14,-10.9,-7.8,-4.7]:cube('Anchored submerged pier foundation',(x,-1.5,6.25),(1.8,1.7,4.3),'concrete_shadow','gate',True)
# Unified visible/physical safety follows the dry shared boundary, leaving all mouths open.
rails=[]
def rail(name,a,b,base=0):
 if math.dist(a,b)<.02:return
 L=math.dist(a,b);rod(name+' top',[a[0],base+1.3,a[1]],[b[0],base+1.3,b[1]],.045,'steel','rails');rod(name+' mid',[a[0],base+.63,a[1]],[b[0],base+.63,b[1]],.027,'steel','rails')
 for i in range(max(1,math.ceil(L/1.9))+1):
  t=i/max(1,math.ceil(L/1.9));x=a[0]+(b[0]-a[0])*t;z=a[1]+(b[1]-a[1])*t;rod(name+' post',[x,base,z],[x,base+1.3,z],.037,'steel','rails')
 rails.append({'name':name,'segment':[list(a),list(b)],'base':base,'top':base+1.3,'thickness':.07})
for w in load('src/data/yuan-surface.json')['barriers']:
 if w.get('island')=='crystal':
  a=[w['a']['x']-C[0],w['a']['z']-C[2]];b=[w['b']['x']-C[0],w['b']['z']-C[2]];rail('Exterior safety',a,b);rails.pop() # shared world boundary already owns physical wall
for e in site['waterRails']:
 a=e['a'];b=e['b'];rail('S22 water crossing safety'if e['coveredCrossing']else'Water edge safety',a,b)
 # Stone banks have real thickness rather than a floating line on a color patch.
 edge=LineString([a,b]).buffer(.10,cap_style=2).difference(waters).intersection(shell);slab('Basin stone coping',edge,.045,.25,'concrete2','water')
# Actual closed facades in place of opaque schematic masses. No inaccessible black doorway.
for x,z,w,d,h,label in [(9.315,4.905,10.875,6.264,3.0,'Main'),(10.794,-2.229,6.786,3.567,3.0,'Emergency')]:
 for zz in [z-d/2,z+d/2]:
  cube(label+' masonry base',(x,.18,zz),(w,.36,.22));cube(label+' upper fascia',(x,h-.12,zz),(w,.24,.23))
  count=6 if label=='Main'else 5
  for k in range(count+1):cube(label+' facade pier',(x-w/2+w*k/count,1.55,zz),(.13,2.75,.24),'steel')
  for k in range(count):cube(label+' closed glazing cassette',(x-w/2+w*(k+.5)/count,1.55,zz),(w/count-.13,2.46,.065),'glass2')
 for xx in [x-w/2,x+w/2]:
  cube(label+' side plinth',(xx,.18,z),(.22,.36,d));cube(label+' side fascia',(xx,h-.12,z),(.23,.24,d))
  for k in range(5):
   zz=z-d/2+d*(k+.5)/5;cube(label+' side window',(xx,1.55,zz),(.065,2.46,d/5-.12),'glass');cube(label+' side frame',(xx,1.55,zz+d/10),(.22,2.75,.12),'steel')
 cube(label+' interior slab',(x,.09,z),(w-.3,.15,d-.3),'floor','command',False)
# The upper command band is separately framed glazing, capped by the retained cantilever roof.
for z in [1.75,8.06]:
 for k in range(6):
  x=3.8775+10.875*(k+.5)/6;cube('Upper command clerestory',(x,4.04,z),(10.875/6-.12,1.55,.065),'glass2')
 for k in range(7):
  x=3.8775+10.875*k/6;cube('Upper clerestory mullion',(x,4.04,z),(.10,1.7,.17),'steel')
  if not pass1 and z==1.75:cube('Continuous civic facade fin',(x,2.6,1.49),(.18,4.5,.27),'concrete2')
for x in [3.9,14.85]:
 for k in range(5):cube('Upper return glass',(x,4.04,2.35+k*1.25),(.065,1.55,1.15),'glass');cube('Upper return post',(x,4.04,1.75+k*1.25),(.17,1.7,.1),'steel')
cube('Actual upper command floor',(9.35,3.05,4.9),(10.9,.16,6.3),'floor','command',False)
# Observation lantern has real floor, four glazed sides and corner structure.
x=13.8*.87+1.05;z=7*.87+.12
cube('Observation room floor',(x,5.43,z),(2.65,.16,2.88),'floor','observation',False)
for zz in [z-1.435,z+1.435]:cube('Observation glazed front-back',(x,6.95,zz),(2.60,2.8,.06),'glass2','observation',True)
for xx in [x-1.30,x+1.30]:cube('Observation glazed return',(xx,6.95,z),(.06,2.8,2.8),'glass','observation',True)
# Coherent planted edges on actual dry land; no falling planters or source proxy trees.
for i,(x,z,s)in enumerate(P['treeAnchors']):
 m=trimesh.creation.cylinder(radius=.17*s,height=1.65*s,sections=9);m.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0]));m.apply_translation([x,.82*s,z]);add(m,'wood','Tree trunk '+str(i),'landscape',True)
 for j,(dx,dy,dz)in enumerate([(0,2.15,0),(.4,2.55,0),(-.42,2.6,.16),(.12,2.8,-.2)]):
  m=trimesh.creation.icosphere(subdivisions=1,radius=1);m.apply_scale([.75*s,.62*s,.65*s]);m.apply_translation([x+dx*s,dy*s,z+dz*s]);add(m,['leaf1','leaf2','leaf3','leaf4'][j],'Tree canopy '+str(i),'landscape')
for i,(x,z,rx,rz)in enumerate(P['gardenAnchors']):
 poly=Point(x,z).buffer(1,quad_segs=12);from shapely.affinity import scale
 poly=scale(poly,rx,rz);slab('Curated riparian raised bed',poly,.24,.24,'concrete2','landscape');parts[-1]['solid']=False
 for j in range(7):
  t=j*2.3999;r=.2+.25*(j%3);xx=x+math.cos(t)*r*rx;zz=z+math.sin(t)*r*rz;m=trimesh.creation.icosphere(subdivisions=1,radius=1);m.apply_scale([.32,.27,.34]);m.apply_translation([xx,.48,zz]);add(m,'leaf2'if j%2 else'leaf1','Riparian planting','landscape')
# Intentional benches facing the water/command court, not a random prop grid.
for x,z in P['benchesXZ']:
 cube('Waterfront seat',(x,.48,z),(1.7,.16,.52),'wood','props',True)
 for dx in [-.6,.6]:cube('Seat metal foot',(x+dx,.23,z),(.08,.42,.4),'steel','props',True)
if not pass1:
 catwalk=box(-16.05,4.2,-2.65,8.0);openings=[box(x-.72,5.3,x+.72,6.9)for x in [-12.45,-9.35,-6.25]]
 deck=catwalk.difference(unary_union(openings));slab('Open hoist service deck',deck,7.52,.2,'steel_lite','gate')
 vv,ff=triangles(deck,7.32);ff=[list(reversed(f))for f in ff];add(trimesh.Trimesh(vertices=vv,faces=ff,process=False),'steel_lite','Service deck actual soffit','gate',False,False,True)
 for p in parts:
  if p['name']=='Open hoist service deck':p['roof']=True;p['head']=True
 for opening in openings:
  cs=list(opening.exterior.coords)
  for a,b in zip(cs[:-1],cs[1:]):rail('Maintenance aperture protection',a,b,7.52)
 habitat=LineString([(-14.1,13.2),(-10.5,15.1),(-5.8,14.8),(-2.8,13.7)]).buffer(.48,cap_style=1).intersection(dry.buffer(-.15))
 slab('Continuous riparian habitat bank',habitat,.12,.12,'turf','landscape')
 for poly in polygons(habitat):
  line=poly.exterior
  for k in range(0,int(line.length),2):
   q=line.interpolate(k);x,z=q.x,q.y
   for j in range(3):rod('Bank reed stand',[x+j*.10,.12,z],[x+j*.10+.07,.72+.1*j,z+.06],.018,'leaf2','landscape')
 for k in range(6):
  x=5.0+k*1.48;cube('Glazed command display console',(x,.92,6.0),(1.05,.16,.55),'interior','interior',False);cube('Console screen',(x,1.15,6.12),(.75,.4,.055),'steel','interior',False)
  cube('Control room chair',(x,.52,5.25),(.47,.12,.46),'chair','interior',False);cube('Chair back',(x,.82,5.05),(.47,.57,.1),'chair','interior',False)
 for x,z,y in [(9.1,-2.2,.84),(12.3,-2.2,.84),(6.3,4.4,3.82),(11.8,6.3,3.82)]:
  cube('Operations work surface',(x,y,z),(1.65,.13,.75),'interior','interior',False)
  cube('Operations display',(x,y+.35,z+.18),(1.0,.55,.05),'steel','interior',False)
 cube('Observation instrument table',(13.056,6.15,6.2),(1.4,.12,.7),'interior','interior',False)
 rod('Closed visitor entry handle',[7.9,.85,1.42],[7.9,1.55,1.42],.035,'bronze','props')
 for x in [-12.45,-9.35,-6.25]:
  for a in range(12):
   angle=a*math.pi/6;cube('Hoist wheel gear tooth',(x+math.cos(angle)*.46,6.67,6.1+math.sin(angle)*.46),(.10,.12,.10),'gold','gate',False)
  for y in np.arange(4.3,6.6,.22):rod('Threaded hoist screw detail',[x-.12,y,6.15],[x+.12,y+.12,6.15],.028,'gold','gate')
  for dx in [-.72,.72]:cube('Gate leaf bolted flange',(x+dx,1.7,5.66),(.12,3.8,.1),'bronze','gate',False)
 for z in [2.4,3.7,5.0,6.3,7.6]:cube('Rear warm screening fin',(15.85*.87+1.05,1.55,z),(.12,2.7,.075),'wood','command')
 for x in [5.6,9.6]:cube('Entrance wall mounted warm luminaire',(x,2.7,1.32),(.26,.12,.14),'foam','command',False)
# Geometry/proxy proof and bounded build input. No mesh binary is printed.
solids=list(rails);ground=[];support=[];roof=[];ceiling=[];camera=[];issues=[]
publicBody=LineString(P['publicCircuit']).buffer(.365,cap_style=1,join_style=1)
core=unary_union([lines[s].buffer(2.4,cap_style=1,join_style=2)for s in ['S21','S22']]);reserve=box(nx-1.5,nz-1.5,nx+1.5,nz+1.5)
for p in parts:
 m=p['mesh'];v=np.asarray(m.vertices);faces=np.asarray(m.faces);norm=np.asarray(m.face_normals)
 # Explicit floor only. Water and rocks are never in floor raycasts.
 if p.get('ground'):ground.extend(v[faces[norm[:,1]>.85]].reshape(-1).round(5).tolist())
 if p['solid']:
  hull=MultiPoint(np.round(v[:,[0,2]],5)).convex_hull.simplify(.00001,preserve_topology=True)
  if hull.geom_type=='Polygon'and hull.area>.00001:
   lo=float(v[:,1].min());hi=float(v[:,1].max());solids.append({'name':p['name'],'polygon':list(map(list,hull.exterior.coords))[:-1],'base':lo,'top':hi})
   if hi>.05 and lo<1.6:
    if hull.intersection(core).area>.02:issues.append({'name':p['name'],'kind':'road core solid','area':hull.intersection(core).area})
    if hull.intersection(reserve).area>.02:issues.append({'name':p['name'],'kind':'NPC solid'})
    if hull.intersection(publicBody).area>.0001:issues.append({'name':p['name'],'kind':'authored public walking path blocked','area':hull.intersection(publicBody).area})
    if hull.difference(shell).area>.03:issues.append({'name':p['name'],'kind':'solid outside island','area':hull.difference(shell).area})
  support.extend(v[faces[norm[:,1]>.85]].reshape(-1).round(5).tolist())
 if p['roof']:
  roof.extend(v[faces[norm[:,1]>.2]].reshape(-1).round(5).tolist())
 if p['head']:ceiling.extend(v[faces[norm[:,1]<-.2]].reshape(-1).round(5).tolist())
 if p['role']in ['command','gate','observation']and p['mat']not in ['water_upper','water_lower','foam']:
  camera.extend(v[faces].reshape(-1).round(5).tolist())
# Raised beds are physical banks corresponding to their visible footprint.
for x,z,rx,rz in P['gardenAnchors']:
 poly=scale(Point(x,z).buffer(1,quad_segs=12),rx,rz)
 if poly.difference(dry).area>.01:issues.append({'kind':'garden outside dry land','x':x,'z':z,'area':poly.difference(dry).area})
 if poly.intersection(core).area>.02:issues.append({'kind':'raised bed blocks protected road core','x':x,'z':z})
 if poly.intersection(publicBody).area>.0001:issues.append({'kind':'raised bed blocks public path','x':x,'z':z})
 if poly.intersection(reserve).area>.001:issues.append({'kind':'raised bed blocks NPC','x':x,'z':z})
 solids.append({'name':'Curated raised garden bank','polygon':list(map(list,poly.exterior.coords))[:-1],'base':0,'top':.24})
save(R/'src/data/flood-control-collision.json',{'revision':'G-V5','groundPositions':ground+support,'dryGroundFloats':len(ground),'roofSupportPositions':roof,'ceilingPositions':ceiling,'cameraPositions':camera,'solids':solids,'waterIsCollider':False})
save(W/'parts.json',{'pass':1 if pass1 else 2,'materials':mats,'parts':[{k:v for k,v in p.items()if k!='mesh'}|{'vertices':p['mesh'].vertices.round(7).tolist(),'faces':p['mesh'].faces.tolist()}for p in parts]})
save(D/'placement-audit.json',{'pass':1 if pass1 else 2,'issues':issues,'parts':len(parts),'trianglesBeforeBevel':sum(len(p['mesh'].faces)for p in parts),'floorArea':accessible.area,'waterArea':waters.area,'waterHolesArea':holes.area,'crossingArea':roads.intersection(waters).area,'npcCount':1,'scale':1,'newRoadLamps':0,'centre':C,'sourceDesignUsedAs':'architecture only; all hydraulic voids, crossing, boundaries and collision regenerated'})
print('G V5 parts/proxies generated:',len(parts),'parts;',len(issues),'placement issues (details saved)')

if issues:raise SystemExit(2)
