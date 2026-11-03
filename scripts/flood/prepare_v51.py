"""V5.1 art refinement, preserving the approved V5 site/roads and part provenance.
Execute V5 through its part stage, refine those real components, then reuse its
semantic collision/audit writer. Never regenerate or rewrite the world site.
"""
from pathlib import Path
import json,math,sys
import numpy as np
import trimesh
from shapely.geometry import Polygon,Point,LineString,box,MultiPoint
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[2];D=R/'docs/design/flood-control-island-g-v5-1';W=R/'work/g-v51';D.mkdir(exist_ok=True);W.mkdir(exist_ok=True)
A=json.loads((R/'src/data/flood-control-art.json').read_text());source=(R/'scripts/flood/prepare_v5.py').read_text();marker='# Geometry/proxy proof and bounded build input.';ns={'__file__':str(R/'scripts/flood/prepare_v5.py')};exec(compile(source.split(marker)[0],str(R/'scripts/flood/prepare_v5.py'),'exec'),ns)
parts=ns['parts'];mats=ns['mats'];mats.update({k:tuple(v)for k,v in A['materials'].items()});add=ns['add'];cube=ns['cube'];rod=ns['rod'];slab=ns['slab'];triangles=ns['triangles'];waters=ns['waters'];dry=ns['dry'];shell=ns['shell'];paving=ns['paving'];P=ns['P'];fromdomain=ns['fromdomain'];site=ns['site']
baseParts=len(parts);removed=[]
# Replace weak full-length slope and thin transverse foam with real crest/fall/runout.
keep=[]
for p in parts:
 n=p['name']
 if n.startswith(('Continuous gate discharge','Surface-following discharge foam')):removed.append(n);continue
 # Lift the already-modelled gate leaves, not the concrete structure/catwalk.
 if n in ['sluice gate deep steel leaf','sluice leaf vertical ribs','vertical sluice steel ribs','upper gate header plate','Gate leaf bolted flange']:p['mesh'].apply_translation([0,A['gateLift'],0])
 if n=='threaded gate screw':
  v=p['mesh'].vertices;lo=v[:,1].min();hi=v[:,1].max();v[:,1]=(v[:,1]-lo)*(hi-lo-A['gateLift'])/(hi-lo)+lo+A['gateLift']
 keep.append(p)
parts[:]=keep
# Thin duplicate visual rail posts at tessellated vertices, retaining continuous bars
# and every physical shared boundary. Corners and isolated aperture guards stay.
kept=[];posts={};removedPosts=0
for p in parts:
 if p['name'].endswith(' post')and p['role']=='rails':
  c=p['mesh'].vertices.mean(axis=0);level=round(float(c[1]),2);seen=posts.setdefault(level,[])
  if any(math.hypot(c[0]-x,c[2]-z)<1.1 for x,z in seen):removedPosts+=1;continue
  seen.append((c[0],c[2]))
 kept.append(p)
parts[:]=kept
# Closed fabricated water-ribbon surfaces, opaque PBR. All levels stay above their
# corresponding basin and never become ground/support collision.
upY=P['waterHeights']['upstream'];lowY=P['waterHeights']['downstream'];lanes=A['water']['laneCentres']
def level(z):
 if z>=6.35:return upY+.014
 if z>=5.35:
  t=(6.35-z);return upY+.014-(upY-lowY-.10)*t*t
 return lowY+.11-(5.35-z)*.12 if z>4.5 else lowY+.014

def ribbon(name,points,width,mat='foam',role='water'):
 verts=[]
 for i,p in enumerate(points):
  a=np.array(points[max(0,i-1)]);b=np.array(points[min(len(points)-1,i+1)]);d=b-a;n=np.array([-d[2],0,d[0]]);L=np.linalg.norm(n)
  if L<1e-8:n=np.array([1.,0,0])
  else:n/=L
  verts.extend([(np.array(p)-n*width/2).tolist(),(np.array(p)+n*width/2).tolist()])
 faces=[]
 for i in range(len(points)-1):faces.extend([[2*i,2*i+1,2*i+3],[2*i,2*i+3,2*i+2]])
 add(trimesh.Trimesh(vertices=verts,faces=faces,process=False),mat,name,role)
for lane,x in enumerate(lanes):
 # Full concrete channel bed, guide flanks and six energy-dissipation blocks.
 cube('V51 sluice apron thick invert',(x,-2.03,3.65),(2.55,.38,6.9),'concrete_shadow','gate',False)
 for sign in [-1,1]:
  cube('V51 channel inner concrete wall',(x+sign*1.14,-1.2,4.5),(.17,1.44,3.25),'concrete2','gate',False)
 cube('V51 steel gate sill',(x,-.79,6.05),(2.28,.16,.23),'steel','gate',False)
 for i in range(3):
  for sign in [-1,1]:cube('V51 energy baffle',(x+sign*.56,-1.58,2.8+i*.68),(.4,.38,.28),'concrete2','gate',False)
 for strip in range(9):
  offset=-.98+strip*.245;pts=[]
  for z in np.linspace(7.1,1.1,33):pts.append([x+offset*(1+.07*math.sin(z*1.5)),level(z),float(z)])
  ribbon('V51 crest falling sheet and runout',pts,.26,'water_lower'if strip%3 else'ripple')
 # Restrained narrow longitudinal highlights show the actual direction/downstep.
 for k in range(5):
  xx=x-.78+k*.39;pts=[[xx+.035*math.sin(z*4+k),level(z)+.015,float(z)]for z in np.linspace(6.55,3.75,23)]
  ribbon('V51 accelerating flow filament',pts,.025 if k%2 else .04,'foam')
 for row in range(6):
  z=5.1-row*.46;fan=.88+.055*row;pts=[]
  for j in range(15):
   t=j/14;zz=z-.15*math.sin(t*math.pi)+.025*math.sin(j*2+lane);pts.append([x+(t-.5)*fan*2,level(zz)+.022,zz])
  ribbon('V51 aerated stilling fan',pts,.035+.004*(row%3),'foam'if row<3 else'ripple')
 # Visible flanges/anchor bolts and travel sensors, no new realtime lights.
 for side in [-1,1]:
  for z in [4.9,7.5]:cube('V51 pier bearing shoe',(x+side*1.54,.22,z),(.45,.22,.42),'concrete_shadow','gate',False)
  for y in [1.0,2.2,3.4,4.6]:cube('V51 gate guide fastening',(x+side*1.37,y,5.61),(.15,.12,.07),'bronze','gate',False)
 cube('V51 hoist position indicator',(x,6.18,4.54),(.56,.29,.08),'steel','gate',False)
 for j in range(3):cube('V51 hoist indicator segments',(x-.17+j*.17,6.18,4.49),(.09,.045,.02),'foam','gate',False)
# Layered bank walls down into each real pool and continuous water-line bands.
for poly,waterY in [(ns['up'],upY),(ns['low'],lowY)]:
 line=poly.exterior
 band=poly.difference(poly.buffer(-.17));slab('V51 submerged waterline stone band',band,waterY+.035,.22,'concrete_shadow','water')
 # Clipped broad current bands, avoiding the three gate throats and every dry deck.
 for i,z in enumerate(np.arange(poly.bounds[1]+1.15,poly.bounds[3]-.7,1.6)):
  shape=box(poly.bounds[0],z-.025,poly.bounds[2],z+.025).intersection(poly.buffer(-.35))
  if not shape.is_empty:slab('V51 basin coherent current band',shape,waterY+.008,0,'ripple','water')
# Real entrance/observation construction, all based on retained V5 dimensions.
for z in [1.40,8.41]:
 cube('V51 command roof standing edge',(8.96,5.26,z),(12.40,.11,.12),'steel','command',False)
 cube('V51 command soffit warm reveal',(8.96,4.91,z+.10 if z<3 else z-.10),(12.2,.07,.16),'wood','command',False)
for x in [2.76,15.18]:cube('V51 command roof return edge',(x,5.26,4.9),(.12,.11,6.9),'steel','command',False)
# Existing entry: a fabricated frame, slatted underside and flush usable threshold.
for x in [5.39,9.93]:cube('V51 entry folded canopy return',(x,3.39,.99),(.11,.31,1.8),'steel','command',False,False,True)
cube('V51 entrance canopy fascia',(7.66,3.39,.10),(4.63,.30,.12),'steel','command',False,False,True)
for x in np.linspace(5.6,9.7,12):cube('V51 entry timber soffit slat',(float(x),3.22,.99),(.10,.065,1.55),'wood','command',False,False,True)
cube('V51 entry stone threshold',(7.66,.04,1.45),(3.9,.03,.54),'concrete2','command',False)
# Unambiguous water/communications identity integrated on the canopy, no long text.
cube('V51 command identity panel',(7.66,3.76,.12),(2.0,.68,.12),'steel','command',False)
for k in range(3):
 verts=[]
 for t in np.linspace(0,1,25):
  x=6.96+t*1.4;y=3.60+k*.13+.035*math.sin(t*math.pi*2)
  verts.extend([[x,y-.022,.052],[x,y+.022,.052]])
 faces=[]
 for j in range(24):faces.extend([[2*j,2*j+1,2*j+3],[2*j,2*j+3,2*j+2]])
 add(trimesh.Trimesh(vertices=verts,faces=faces,process=False),'bronze','V51 water-command entrance emblem','command')
# Tower proportions unchanged; add a thin roof rim, warm soffit, framed lantern.
tx=13.056;tz=6.21
for zz in [4.43,8.0]:
 cube('V51 observation crown thin metal rim',(tx,8.82,zz),(3.57,.10,.09),'steel','observation',False)
 cube('V51 observation crown soffit',(tx,8.39,zz+.15 if zz<6 else zz-.15),(3.2,.06,.17),'wood','observation',False)
for xx in [11.28,14.84]:cube('V51 observation roof return',(xx,8.82,tz),(.09,.10,3.57),'steel','observation',False)
for xx in [11.76,14.35]:
 for zz in [4.80,7.61]:cube('V51 observation corner frame',(xx,6.95,zz),(.12,2.94,.12),'steel','observation',False)
for zz in [4.77,7.65]:
 cube('V51 observation transom',(tx,7.45,zz),(2.7,.06,.08),'wood','observation',False)
 cube('V51 observation lower console band',(tx,5.72,zz),(2.7,.27,.11),'steel_lite','observation',False)
# Small weather/communications instruments, keeping retained maximum height.
rod('V51 weather mast',[12.0,8.85,6.5],[12.0,9.65,6.5],.04,'steel','observation')
rod('V51 anemometer beam',[11.57,9.45,6.5],[12.43,9.45,6.5],.025,'steel','observation')
for x in [11.57,12.43]:
 m=trimesh.creation.icosphere(subdivisions=1,radius=.10);m.apply_scale([1,.45,1]);m.apply_translation([x,9.45,6.5]);add(m,'steel_lite','V51 wind measurement cup','observation')
# Four facades: terracotta/wood spandrels and return fins, not blank office boxes.
for z in [1.61,8.19]:
 for x in [4.35,6.16,7.97,9.78,11.59,13.40]:cube('V51 command facade warm spandrel',(x,.46,z),(1.47,.20,.045),'wood','command',False)
for x in [3.76,14.98]:
 for z in [2.25,3.5,4.75,6.,7.25]:cube('V51 side vertical shading fin',(x,2.0,z),(.23,3.5,.07),'wood','command',False)
for x in [8.4,10.3,12.2]:cube('V51 annex framed service panel',(x,.64,-4.06),(1.45,.46,.07),'steel_lite','command',False)
# Site-scale composition. Flush geometry only in the protected road/plaza core.
# Coarse joint lines connect building plinths and courts, rather than floating colors.
for x in np.arange(-18,20,1.7):
 shape=box(x-.012,-18,x+.012,18).intersection(paving.buffer(-.08))
 if not shape.is_empty:slab('V51 public paving scored joint',shape,P['publicY']+.0015,0,'concrete2','terrain')
for z in np.arange(-17,18,1.7):
 shape=box(-20,z-.012,20,z+.012).intersection(paving.buffer(-.08))
 if not shape.is_empty:slab('V51 public paving scored joint',shape,P['publicY']+.0015,0,'concrete2','terrain')
mx,mz=A['zones']['arrival']['medallion'];rr=A['zones']['arrival']['radius']
for i,r in enumerate([rr,rr*.72,rr*.39]):
 ring=Point(mx,mz).buffer(r,quad_segs=32).difference(Point(mx,mz).buffer(r-(.12 if i<2 else .08),quad_segs=32));shape=ring.intersection(paving)
 slab('V51 arrival water-cycle stone inlay',shape,P['publicY']+.004+i*.0005,0,'steel_lite'if i%2 else'bronze','terrain')
# Curated command court edge: one integrated bed, not arbitrary pot scattering.
bed=Polygon(A['zones']['forecourt']['bed']);slab('V51 command rain-garden wall',bed,.34,.34,'concrete2','landscape');soil=bed.buffer(-.13);slab('V51 command rain-garden soil',soil,.345,.03,'leaf1','landscape')
# Add its real physical bank to the standard collision proof without using a box
# spanning any entrance. The exact polygon is appended after the shared writer.
for i in range(7):
 x=12.6+i*.37;z=-5.98
 for j in range(3):
  m=trimesh.creation.icosphere(subdivisions=1,radius=1);m.apply_scale([.25,.18+.035*(i%2),.23]);m.apply_translation([x,.53,z+(j-1)*.15]);add(m,'leaf2'if j==1 else'leaf1','V51 coherent rain-garden planting','landscape')
# Existing seats gain useful backs and refined timber construction in the same sites.
for x,z in P['benchesXZ']:
 for h in [.70,.83]:cube('V51 retained seat timber back',(x,h,z+.22),(1.7,.09,.075),'wood','props',True)
# Water interpretation mounts to the bank, leaving the full promenade open.
sx,sz=A['zones']['overlook']['sign'];cube('V51 waterside interpretation frame',(sx,.83,sz),(.12,.62,.85),'steel','props',True)
for j in range(5):cube('V51 water level interpretation mark',(sx+.066,.60+j*.10,sz),(.01,.025,.45-.045*j),'foam','props',False)
# S22 concave edge receives a continuous fine coping profile at the existing rail,
# never an inner fence. Floor geometry remains unchanged.
for e in site['waterRails']:
 if e['coveredCrossing']:
  shape=LineString([e['a'],e['b']]).buffer(.07,cap_style=2).intersection(ns['accessible'])
  slab('V51 S22 water-side coping reveal',shape,P['publicY']+.008,.045,'concrete2','crossing')
# Refine the retained trees into broader irregular shade crowns, keeping all trunks.
for p in parts:
 if p['name'].startswith('Tree canopy'):
  v=p['mesh'].vertices;c=v.mean(axis=0);v[:]=c+(v-c)*np.array([1.14,.87,1.09])
for i,(x,z,s)in enumerate(P['treeAnchors']):
 for dx,dz in [(-.34,.12),(.30,-.12)]:rod('V51 retained tree branch',[x,1.1*s,z],[x+dx*s,1.95*s,z+dz*s],.055*s,'wood','landscape')
# One authored bank: certify against the same real core/guide/walking constraints.
reserve=box(ns['nx']-1.5,ns['nz']-1.5,ns['nx']+1.5,ns['nz']+1.5);core=unary_union([ns['lines'][s].buffer(2.4,cap_style=1)for s in ['S21','S22']]);body=LineString(P['publicCircuit']).buffer(.365)
assert bed.intersection(core).area<1e-6 and bed.intersection(reserve).area<1e-6 and bed.intersection(body).area<1e-6 and bed.difference(dry).area<1e-6,'authored forecourt bank placement fails'
# Reuse the V5 explicit semantic collision writer for all existing/new real walls,
# columns, benches, bank-mounted display and roof soffits; water stays non-ground.
ns['D']=D;ns['W']=W;ns['parts']=parts;ns['mats']=mats;exec(compile(marker+source.split(marker)[1],str(R/'scripts/flood/prepare_v5.py'),'exec'),ns)
collision=json.loads((R/'src/data/flood-control-collision.json').read_text());collision['solids'].append({'name':'V51 command rain-garden bank','polygon':list(map(list,bed.exterior.coords))[:-1],'base':0,'top':.34});collision['artRevision']='G-V5.1';(R/'src/data/flood-control-collision.json').write_text(json.dumps(collision,separators=(',',':'))+'\n')
proof={'baseCommit':A['baseCommit'],'baseParts':baseParts,'parts':len(parts),'removedOldFlowParts':len(removed),'redundantVisualPostsRemoved':removedPosts,'gateLeafLift':A['gateLift'],'headerTop':4.23+A['gateLift'],'retainedBeamUnderside':5.06,'headerClearance':5.06-(4.23+A['gateLift']),'waterLevels':P['waterHeights'],'geometryFloorUntouched':True,'newRealtimeLights':0,'newTransparentWater':0,'zones':A['zones']}
(D/'art-change-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');print('V5.1 true-art parts prepared; header clearance %.3f; all site/core/guide domains retained'%proof['headerClearance'])
