"""MIT. Editable water infrastructure park; game X/Z, Y up -> Blender X/-Y/Z.
No approved asset imported. All architectural geometry authored here.
Run blender -b -t 4 --python scripts/blender/build_flood_g.py [-- --draft].
"""
import bpy,math,sys,json,random
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from flood_export import export_batched
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/design/flood-control-island-g-v1';OUT.mkdir(parents=True,exist_ok=True)
P=json.loads((ROOT/'src/data/flood-control-plan.json').read_text());SITE=json.loads((ROOT/'src/data/flood-control-site.json').read_text());draft='--draft' in sys.argv
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';random.seed(173)
root=bpy.data.objects.new('FloodControlPark_MODEL',None);scene.collection.objects.link(root)
def group(n):
 o=bpy.data.objects.new(n,None);scene.collection.objects.link(o);o.parent=root;return o
G={n:group(n) for n in ['Terrain_Foundation','SluiceGate','WaterChannels','RetentionPond','CommandCenter','ObservationDeck','Walkways_Railings','Vegetation_Props']}
def mat(n,c,metal=0,rough=.6,alpha=1):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,alpha);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*c,alpha);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m
M={'stone':mat('Warm pale precast concrete',(.68,.68,.60)), 'edge':mat('Chalk coping',(.85,.83,.72)), 'metal':mat('Deep teal coated steel',(.055,.19,.21),.55,.34),'water':mat('Clear jade water low-cost opaque',(.12,.46,.48),.18,.22),'lower':mat('Deep water blue',(.075,.30,.36),.12,.26),'foam':mat('Pale moving-water lines',(.65,.87,.82),.1,.32),'glass':mat('Blue green glass',(.20,.43,.45),.18,.18),'wood':mat('Warm oak louvres',(.57,.34,.15),0,.6),'paver':mat('Warm limestone paving',(.74,.72,.63)), 'soil':mat('Earth bank',(.29,.37,.22)),'green':mat('Meadow bank',(.37,.48,.22)), 'leaf':mat('Canopy light',(.42,.59,.20)), 'darkleaf':mat('Canopy shade',(.22,.40,.18)), 'rock':mat('Weathered rock',(.39,.43,.38)), 'gold':mat('Satin brass details',(.64,.48,.22),.65,.3),'warm':mat('Warm interior',(.83,.66,.35)), 'bloom':mat('Warm meadow flower',(.88,.70,.46)), 'white':mat('Wayfinding cream',(.93,.90,.76))}
# Thin glazing uses alpha-blend rather than costly physical transmission.
b=M['glass'].node_tree.nodes.get('Principled BSDF');b.inputs['Alpha'].default_value=.43;M['glass'].surface_render_method='DITHERED'
solids=[];floors=[];ceilings=[];cameras=[]
def V(p):x,y,z=p;return (x,-z,y)
def finish(o,n,m,g):
 o.name=n;o.parent=G[g];o.data.materials.append(M[m]);return o
def box(n,c,s,m='stone',g='CommandCenter',bevel=.025,solid=False,camera=False,head=False):
 bpy.ops.mesh.primitive_cube_add(size=1,location=V(c));o=bpy.context.object;o.scale=(s[0],s[2],s[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,n,m,g)
 if bevel:
  mod=o.modifiers.new('Soft fabricated edges','BEVEL');mod.width=bevel;mod.segments=2
  o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 if solid:
  x,y,z=c;w,h,d=s;solids.append({'name':n,'polygon':[[x-w/2,z-d/2],[x+w/2,z-d/2],[x+w/2,z+d/2],[x-w/2,z+d/2]],'base':y-h/2,'top':y+h/2})
 if camera:cameras.append(o)
 if head:ceilings.append(o)
 return o

def mesh(n,verts,faces,m,g):
 data=bpy.data.meshes.new(n);data.from_pydata([V(v) for v in verts],[],faces);data.update();o=bpy.data.objects.new(n,data);scene.collection.objects.link(o);finish(o,n,m,g);return o

def curve(n,pts,r,m,g='Walkways_Railings'):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=1;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for dst,p in zip(sp.points,pts):dst.co=(*V(p),1)
 o=bpy.data.objects.new(n,cu);scene.collection.objects.link(o);o.parent=G[g];cu.materials.append(M[m]);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);return o

def post(n,x,z,h=.99,base=0):return box(n,(x,base+h/2,z),(.06,h,.06),'metal','Walkways_Railings',.015)
def rail(n,a,b,base=0,h=1.13,physics=True):
 for y,r in [(base+h,.035),(base+.50,.022)]:curve(n+' handrail',[(a[0],y,a[1]),(b[0],y,b[1])],r,'metal')
 d=math.dist(a,b)
 for i in range(max(1,math.ceil(d/1.6))+1):
  t=i/max(1,math.ceil(d/1.6));post(n+' stanchion',a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t,h,base)
 if physics:solids.append({'name':n,'segment':[a,b],'base':base,'top':base+h,'thickness':.07})
def poly_slab(n,rings,top,bottom,m,g):
 from mathutils.geometry import tessellate_polygon
 # Blender tessellation does not subtract holes: use pretriangulated site floor instead below.
 rr=rings[0][:-1];nvert=len(rr);verts=[(x,top,z)for x,z in rr]+[(x,bottom,z)for x,z in rr]
 faces=[]
 for tri in tessellate_polygon([[Vector((x,-z,top))for x,z in rr]]):faces.append(tuple(tri))
 faces.extend([(i,(i+1)%nvert,(i+1)%nvert+nvert,i+nvert)for i in range(nvert)])
 return mesh(n,verts,faces,m,g)
# Actual floor triangulated by Three's earcut, matches water holes exactly.
tri=json.loads((ROOT/'src/data/flood-control-floor.json').read_text());verts=[tuple(v)for v in tri['vertices']];floor=mesh('Public dry ground with true water voids',verts,tri['triangles'],'paver','Terrain_Foundation');floors.append(floor)
# Foundation skirts and bevelled coping run around irregular authored outline.
ring=P['footprintLocal'];outer=[]
for a,b in zip(ring,ring[1:]):
 mesh('Island layered retaining wall',[(a[0],-.04,a[1]),(b[0],-.04,b[1]),(b[0],-1.8,b[1]),(a[0],-1.8,a[1])],[(0,1,2,3)],'stone','Terrain_Foundation')
 curve('Limestone perimeter coping',[(a[0],-.06,a[1]),(b[0],-.06,b[1])],.10,'edge','Terrain_Foundation')
# Actual exposed boundary only: generated union leaves both mouths open.
surface=json.loads((ROOT/'src/data/yuan-surface.json').read_text())
for w in surface['barriers']:
 if w.get('island')=='crystal':
  a=[w['a']['x']-P['centre'][0],w['a']['z']-P['centre'][2]];b=[w['b']['x']-P['centre'][0],w['b']['z']-P['centre'][2]];rail('Exterior safety',a,b,h=1.3,physics=False)
# Continuous visible water beneath actual bridge crossing; water never a collider.
for n,r,y,m in [('Upstream retention and canal',P['water']['upstream'],-.55,'water'),('Downstream demonstration basin',P['water']['downstream'],-1.35,'lower')]:poly_slab(n,[r],y,y-.07,m,'WaterChannels')
for e in SITE['waterRails']:
 a,b=e['a'],e['b'];rail('Water edge safety',a,b)
 mesh('Channel coping and retaining wall',[(a[0],-.04,a[1]),(b[0],-.04,b[1]),(b[0],-1.65,b[1]),(a[0],-1.65,a[1])],[(0,1,2,3)],'edge','WaterChannels')
# Water-control structure: two tall sculpted concrete portal frames, deep gate leaves,
# operable-looking guide tracks, screw hoists, access catwalk and parapet caps.
for x in [-7.5,-5.3,-3.1]:
 box('Tapered gate pier footing',(x,-.15,4.6),(.72,2.4,2.15),'stone','SluiceGate',.08,True,True)
 box('Gate pier',(x,1.45,4.6),(.52,3.2,1.42),'stone','SluiceGate',.05,True,True)
 box('Pier crown',(x,3.12,4.6),(.86,.22,1.76),'edge','SluiceGate',.04,False,False,True)
 for z in [3.91,5.29]:box('Gate metal guide track',(x,1.0,z),(.12,3.15,.12),'metal','SluiceGate',.015)
for x in [-6.4,-4.2]:
 box('Deep gate leaf',(x,.65,4.9),(1.62,2.65,.18),'metal','SluiceGate',.04,True)
 for y in [-.35,.25,.85,1.45,2.05]:box('Gate stiffening rib',(x,y,5.035),(1.72,.075,.10),'metal','SluiceGate',.02)
 box('Hoist spindle',(x,2.6,4.9),(.065,2.5,.065),'gold','SluiceGate',.01)
 box('Hoist gearbox',(x,3.35,4.8),(.48,.30,.42),'metal','SluiceGate',.04)
 # Sculpted solid waterfall surface and foam lines (opaque, no particle simulation).
 pts=[(x-.74,-.53,4.45),(x+.74,-.53,4.45),(x+.74,-1.30,6.4),(x-.74,-1.30,6.4)]
 mesh('Gate discharge sheet',pts,[(0,1,2,3)],'water','WaterChannels')
 for j in range(4):curve('Discharge streak',[(x-.6+j*.4,-.52,4.55),(x-.6+j*.4,-.84,5.5),(x-.6+j*.4,-1.28,6.35)],.018,'foam','WaterChannels')
box('Gate maintenance lintel',(-5.3,2.94,4.6),(5.45,.30,1.62),'stone','SluiceGate',.06,False,True,True)
# Public facing viewing deck beside lower pool, no elevated stair requirement.
box('Oak viewing apron',(-.6,-.055,8.6),(2.3,.11,3.2),'wood','ObservationDeck',.04)
rail('Viewing deck lower-water edge',[-1.72,7.05],[-1.72,10.2]);box('Interpretation desk',(-.6,.70,9.55),(1.15,.16,.48),'metal','ObservationDeck',.04,True)
for x in [-1.0,-.2]:box('Interpretation desk foot',(x,.34,9.55),(.07,.68,.07),'metal','ObservationDeck',.01)
# Command centre: terraced volumes and connected projecting flat roofs, usable porch.
b=P['building'];
for x,z,w,d,h in [(5.1,5.6,2.6,5.6,2.9),(8,5.6,3.2,5.6,2.65)]:
 box('Stone back wall',(x,h/2,8.2),(w,h,.22),'stone',solid=True,camera=True)
 box('Deep projecting roof',(x,h+.15,z),(w+.6,.25,d+.6),'metal',bevel=.07,head=True)
 box('Roof stone fascia',(x,h-.03,z),(w+.65,.12,d+.65),'edge',bevel=.025)
# Side walls and full-height glazed front with genuine framing, roof soffit and piers.
for x in [3.8,10]:box('Side masonry return',(x,1.35,6.65),(.22,2.7,3.1),'stone',solid=True,camera=True)
for x in [4.0,5.45,6.9,8.35,9.8]:
 box('Facade timber mullion',(x,1.3,2.85),(.10,2.6,.18),'wood',solid=True)
 if x<9.7:box('Recessed glass panel',(x+.67,1.32,2.9),(1.22,2.4,.035),'glass',bevel=0)
# Closed glazed line gets exact physical low sill/door surface; porch remains open.
box('Glazed facade physical line',(6.9,1.3,2.93),(6.1,2.6,.045),'glass',bevel=0,solid=True,camera=True)
box('Open entrance canopy',(6.9,2.72,1.85),(4.1,.20,2.35),'edge',head=True)
for x in [4.95,8.85]:box('Porch timber column',(x,1.3,.85),(.14,2.6,.14),'wood',solid=True,camera=True)
for x in [4.1+i*.22 for i in range(10)]:box('Southwest oak screening',(x,1.3,7.7),(.085,2.4,.22),'wood')
for z in [3.5,4.35,5.2,6.05,6.9]:
 box('East glazed light',(10.025,1.4,z),(.035,1.85,.65),'glass',bevel=0)
 box('East stone rib',(10.04,1.4,z+.38),(.13,2.3,.085),'stone')
# Upper clerestory / observation lantern sits on opaque rear structural tower.
box('Observation tower stone shaft',(9,2.4,6.6),(1.15,4.8,1.25),'stone',bevel=.08,solid=True,camera=True)
box('Observation lantern glass',(9,5.13,6.6),(1.55,.65,1.65),'glass',bevel=.02)
for x in [8.25,9.75]:
 for z in [5.83,7.37]:box('Lantern mullion',(x,5.13,z),(.07,.75,.07),'metal')
box('Observation cap',(9,5.57,6.6),(1.95,.18,2.05),'metal',bevel=.06)
curve('Antenna mast',[(9,5.65,6.6),(9,6.2,6.6)],.045,'metal','CommandCenter')
box('Clerestory lantern',(5.45,3.5,5.55),(2.1,.72,2.8),'glass',bevel=.035)
box('Clerestory canopy',(5.45,3.96,5.55),(2.7,.18,3.3),'metal',bevel=.07,head=True)
for x in [4.45,6.45]:
 for z in [4.2,6.9]:box('Clerestory frame',(x,3.5,z),(.1,.8,.1),'wood')
# Interior control desk/screens visible through front glazing, no claim of playable interior.
for x in [4.5,6.25,8.1]:
 box('Interior worktable',(x,.78,4.5),(1.25,.12,.65),'wood')
 box('Worktable frame',(x,.38,4.5),(.1,.76,.1),'metal')
 box('Control display',(x,1.15,4.65),(.65,.38,.07),'metal')
 box('Display inset',(x,1.15,4.60),(.53,.25,.015),'water',bevel=0)
box('Entrance identification band',(6.9,2.27,2.73),(1.85,.34,.09),'metal')
# Water-drop civic emblem authored as a silhouette, not a policy-text panel.
curve('Water identity',[(6.7,2.28,2.64),(6.9,2.42,2.64),(7.1,2.28,2.64),(7.03,2.17,2.64),(6.77,2.17,2.64),(6.7,2.28,2.64)],.025,'white','CommandCenter')
# Ecological bank composition. Deliberately placed canopy groups and sinuous earth beds.
def tree(x,z,scale=1):
 box('Tree trunk',(x,1.1*scale,z),(.20*scale,2.2*scale,.20*scale),'wood','Vegetation_Props',.06,True)
 for dx,dy,dz,s in [(-.55,2.35,.0,.95),(.55,2.5,.15,1.05),(0,3.05,-.08,1.05)]:
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=s*scale,location=V((x+dx*scale,dy*scale,z+dz*scale)));o=bpy.context.object;o.scale=(1,.85,.8);finish(o,'Layered tree canopy','leaf'if dy>2.5 else'darkleaf','Vegetation_Props')
if not draft:
 for x,z,s in [(-11,4.2,.85),(-10,6.6,.7),(-9.8,-7.5,.72),(-6.5,-10.4,.75),(10.5,-5.7,.9),(11,1.5,.8),(8.3,9.6,.72),(-.2,11.2,.6)]:tree(x,z,s)
 for a,b in [((-11,-2),(-11,2.9)),((10.8,3),(10.8,7)),((-8.7,9),(-4,11.3)),((-10,-10),(-5.6,-11.2))]:
  pts=[(a[0]*(1-t)+b[0]*t,.13,a[1]*(1-t)+b[1]*t+.24*math.sin(t*math.pi))for t in [i/12 for i in range(13)]]
  curve('Continuous planted grass berm',pts,.32,'green','Vegetation_Props')
  for i in range(9):
   t=i/8;x=a[0]*(1-t)+b[0]*t;z=a[1]*(1-t)+b[1]*t
   bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.40,location=V((x,.36,z)));o=bpy.context.object;o.scale=(1.4,.8,.7);finish(o,'Layered ecological shrub','darkleaf','Vegetation_Props')
   if i%2==0:
    for j in range(3):
     bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.08,location=V((x+.13*j-.13,.66,z)));finish(bpy.context.object,'Meadow blossom','bloom','Vegetation_Props')
 # Natural bank rocks share coarse geometry, not a repeated block border.
 for i in range(16):
  a=i/15*math.pi;x=-6.5+3.4*math.cos(a);z=-6.9+2.9*math.sin(a)
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.4+random.random()*.25,location=V((x,-.28,z)));o=bpy.context.object;o.scale=(1.3,.85,.7);o.rotation_euler.z=a;finish(o,'Water-worn bank stone','rock','Vegetation_Props')
 for x,z in [(-8.8,-6.6),(-8,-7.5),(-5,-8.6),(-6,9.5)]:
  for j in range(7):
   a=j*2.4;curve('Emergent reed',[(x+.15*math.cos(a),-.5,z+.15*math.sin(a)),(x+.3*math.cos(a),.3+j%3*.12,z+.3*math.sin(a))],.025,'green','Vegetation_Props')
 # Waterfront seating kept out of bridge cores and NPC clear squares.
 for x,z in [(10.7,-1),(-10.5,2.3),(1.2,10.3)]:
  box('Oak seat',(x,.48,z),(1.5,.13,.5),'wood','Vegetation_Props',.04,True)
  box('Oak seat back',(x,.8,z+.23),(1.5,.5,.08),'wood','Vegetation_Props',.03,True)
  for dx in [-.55,.55]:box('Seat steel leg',(x+dx,.21,z),(.06,.42,.4),'metal','Vegetation_Props')
 # Restrained paving joints on dry surface only, none across water.
 for x in range(-12,14,2):
  # Not scatter: fine joints in the deliberate eastern civic court.
  if 0<=x<=12:curve('Civic court paving joint',[(x,.003,-.0),(x,.003,10)],.007,'stone','Terrain_Foundation')
 # Small water-level gauge on a real pier, with three markings.
 for i in range(5):box('Water-level graduation',(-2.79,.2+i*.34,5.32),(.18,.035,.012),'white','SluiceGate',0)
 for z in [7.0,8.2,9.4]:curve('Downstream ripples',[(-7.2+i*.4,-1.335,z+.06*math.sin(i*1.4))for i in range(12)],.014,'foam','WaterChannels')
# Collision geometry exported from exact source floor + roofs and structural shells.
bpy.context.view_layer.update()
def tris(objects):
 out=[];deps=bpy.context.evaluated_depsgraph_get()
 for o in objects:
  e=o.evaluated_get(deps);me=e.to_mesh();me.calc_loop_triangles()
  for tri in me.loop_triangles:
   for idx in tri.vertices:
    v=o.matrix_world@me.vertices[idx].co;out.extend([round(v.x,6),round(v.z,6),round(-v.y,6)])
  e.to_mesh_clear()
 return out
collision={'solids':solids,'groundPositions':tris(floors),'ceilingPositions':tris(ceilings),'cameraPositions':tris(cameras+ceilings),'waterIsCollider':False}
(ROOT/'src/data/flood-control-collision.json').write_text(json.dumps(collision,separators=(',',':')))
# Render stage is outside the model and is never exported to game.
world=bpy.data.worlds.new('Neutral soft daylight');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.52,.62,.65,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6
bpy.ops.object.light_add(type='AREA',location=(-9,-13,25));bpy.context.object.data.energy=2400;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=16
bpy.ops.object.light_add(type='SUN',location=(4,-8,16));bpy.context.object.rotation_euler=(.45,-.4,-.6);bpy.context.object.data.energy=2.0;bpy.context.object.data.angle=.3
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.image_settings.file_format='PNG';scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
for name,pos in [('hero',(25,24,31)),('front',(0,12,38)),('back',(0,12,-38)),('left',(-38,12,0)),('right',(38,12,0)),('top',(0,42,0))]:
 bpy.ops.object.camera_add(location=V(pos));cam=bpy.context.object;cam.name='VIEW_'+name;target=Vector(V((0,0,0)));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=34
scene.camera=bpy.data.objects['VIEW_hero'];scene.render.resolution_x=1200;scene.render.resolution_y=1000
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'flood-control-g.blend'))
report=export_batched(root,ROOT/'public/models/flood-control-g/flood-control-g.glb')
report.update({'draft':draft,'waterIsCollider':False,'centre':P['centre'],'scale':1,'boundsNominal':[28,8,26],'upperWaterY':-.55,'lowerWaterY':-1.35,'maximumTowerY':6.245,'floorTriangles':len(tri['triangles']) if isinstance(tri,dict) else len(collision['groundPositions'])//9})
(OUT/'model-report.json').write_text(json.dumps(report,indent=2));print('FLOOD_G_SAVED',json.dumps(report),flush=True)
