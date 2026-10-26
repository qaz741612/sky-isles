"""Stage two: open and refine the actual PR11 Blender source. Never rebuild its project.
MIT. Source, camera lineage and exact changes are recorded alongside the new artifact.
"""
import bpy,sys,math,json,hashlib,random
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import parent_child_geometry as G
import parent_child_export
ROOT=Path(__file__).resolve().parents[2];OLD=ROOT/'docs/design/parent-child-blender-model-v1';OUT=ROOT/'docs/design/parent-child-blender-refinement-v2'
CFG=json.loads((OUT/'layout.json').read_text());SOURCE=OLD/'parent-child-centre.blend'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==CFG['sourceBlendSHA256'],'PR11 source changed; inspect before refining'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));model=bpy.data.objects['ParentChildCentre_MODEL'];arch=bpy.data.objects['Architecture'];interior=bpy.data.objects['InteriorFurniture'];land=bpy.data.objects['Landscape'];play=bpy.data.objects['Playground'];street=bpy.data.objects['StreetFurniture'];scene=bpy.context.scene
model['refinement']='Second-stage refinement of PR11; standalone art, not integrated';model['source_blend_sha256']=CFG['sourceBlendSHA256']
M={key:bpy.data.materials[key]for key in ['cream','stone','trim','roof','seam','wood','woodLight','woodDark','rail','leaf','leafLight','leafDark','soil','sand','rubber','rubberBlue','rubberOchre','coral','slide','petal','petalPink','greenCloth','tealCloth','floor','gray']};M['glass']=bpy.data.materials['Clear warm architectural glazing']
def remove(objects):
 for o in list(objects):
  if o.name in bpy.data.objects:bpy.data.objects.remove(o,do_unlink=True)
def tree(name):return [bpy.data.objects[name],*bpy.data.objects[name].children_recursive]
def warp(objects,fn):
 for o in objects:
  if o.type!='MESH':continue
  o.data=o.data.copy();mat=o.matrix_world.copy();inv=mat.inverted()
  for v in o.data.vertices:v.co=inv@Vector(fn(mat@v.co))
  o.data.update()
def col(name):G.COL=bpy.data.collections[name]
def bx(name,p,d,mat='cream',parent=arch,r=.025):return G.box(name,p,d,M[mat],parent,r)
def bm(name,a,b,w=.07,mat='wood',parent=arch):return G.beam(name,a,b,w,M[mat],parent)
# Improve actual physically transmitted glazing; no planar picture or fake transparency.
for key,h,rough,metal in [('roof','729FA1',.50,.035),('seam','709B9E',.52,.04),('wood','BF9866',.48,0),('woodLight','D8B984',.5,0),('woodDark','96734C',.62,0)]:
 m=M[key];p=m.node_tree.nodes.get('Principled BSDF');c=G.linear(h);m.diffuse_color=(*c,1);p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
p=M['glass'].node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*G.linear('F9FCF9'),1)
for key,value in [('Roughness',CFG['glass']['roughness']),('Transmission Weight',CFG['glass']['transmission']),('IOR',CFG['glass']['ior']),('Specular IOR Level',CFG['glass']['specularIORLevel'])]:p.inputs[key].default_value=value
M['glass'].diffuse_color=(*G.linear('F9FCF9'),1)
# Keep entry canopy and arch completely unchanged. Reshape only existing curved shells and fitted clerestories.
oldcfg=json.loads((OLD/'layout.json').read_text())
def soft(x,p,rise):
 u=max(0,min(1,(x-p['x0'])/(p['x1']-p['x0'])));return p['left']+(p['right']-p['left'])*(u*u*(3-2*u))+rise*math.sin(math.pi*u)**CFG['roof']['profileExponent']
for group,key,rise,base in [('MainCurvedHall','mainRoof',CFG['roof']['mainRise'],2.74),('UpperLeftDaylightLevel','upperLeftRoof',CFG['roof']['loftRise'],3.38)]:
 root=bpy.data.objects[group];params=oldcfg[key]
 remove([o for o in root.children_recursive if 'StandingSeam' in o.name or 'PanelJoint' in o.name])
 def curve(v):
  x,y,z=v;old=G.profile(x,params['x0'],params['x1'],params['left'],params['right'],params['rise']);delta=soft(x,params,rise)-old;weight=max(0,min(1,(z-base)/max(.1,old-base)))
  return x,y,z+delta*weight
 warp(root.children_recursive,curve)
 col('10_ARCHITECTURE');n=max(2,round((params['x1']-params['x0'])/CFG['roof']['seamSpacing']))
 for i in range(1,n):
  x=params['x0']+(params['x1']-params['x0'])*i/n;z=soft(x,params,rise)+.007
  bm(group+'_QuietRoofSeam',(x,params['y0']+.035,z),(x,params['y1']-.035,z),CFG['roof']['seamWidth'],'seam',root)
# Deeper true enclosed wings, preserving their front facades and the successful entrance.
for name,key in [('LeftFamilyReadingWing','leftWingDepth'),('RightCareWing','rightWingDepth')]:
 d=CFG[key];front=d['front'];ratio=(d['newRear']-front)/(d['oldRear']-front)
 warp(bpy.data.objects[name].children_recursive,lambda v:(v.x,front+(v.y-front)*ratio,v.z))
# Low-wing roof seams reduced just like the primary roofs; fascia lines stay structural.
for name in ['LeftFamilyReadingWing','RightCareWing']:
 root=bpy.data.objects[name];seams=[o for o in root.children_recursive if 'StandingSeam'in o.name]
 for i,o in enumerate(seams):
  if i%3:remove([o])
  else:o.data=o.data.copy();o.scale.x*=.65;o.scale.y*=.65
 remove([o for o in root.children_recursive if 'PanelJoint'in o.name])
# Extend the high daylight loft to give its side return actual depth.
warp(bpy.data.objects['UpperLeftDaylightLevel'].children_recursive,lambda v:(v.x,2.42+(v.y-2.42)*1.18,v.z))
# Match low-wing fascia returns / roof bearings that belonged to the shared architecture root.
for prefix,front,ratio in [('LeftWing_ClosedFasciaInfill',1.3,4.45/3.15),('WestWingRoofBearing',1.3,4.45/3.15),('CareWing_ClosedFasciaInfill',1.55,4.3/3.1),('CareEastRoofBearing',1.55,4.3/3.1)]:
 warp([o for o in arch.children_recursive if o.name.startswith(prefix)],lambda v:(v.x,front+(v.y-front)*ratio,v.z))
# Rear furniture is moved into the deeper rooms; front table positions remain usable.
for o in interior.children_recursive:
 if 'ReadingLibrary' in o.name or 'CareWingStorage' in o.name:o.location.y+=1.05
# Open-backed library shelves avoid opaque rear-facade blocks while retaining solid shelves/books.
remove([o for o in interior.children_recursive if any(o.name.startswith(prefix)for prefix in ['ReadingLibrary_Back','MainHallLibrary_Back','CareWingStorage_Back','LoftReadingShelf_Back'])])
# Add real semi-outdoor side verandas: floor, thin solid roof, separated posts and open bays.
col('10_ARCHITECTURE');verandas=G.empty('SideVerandas',arch)
for label,x0,x1,y0,y1,z in [('West',-8.22,-7.10,.45,4.9,2.72),('East',7.0,8.05,.60,5.05,2.62)]:
 root=G.empty(label+'OpenVeranda',verandas);bx(label+'VerandaPaving',((x0+x1)/2,(y0+y1)/2,.055),(x1-x0,y1-y0,.11),'stone',root,.03)
 bx(label+'VerandaSolidCanopy',((x0+x1)/2,(y0+y1)/2,z+.09),(x1-x0+.12,y1-y0+.18,.14),'roof',root,.035)
 x=x0+.08 if label=='West'else x1-.08
 for y in [y0+.12,(y0+y1)/2,y1-.12]:bx(label+'VerandaTimberColumn',(x,y,z/2),(.085,.085,z),'wood',root,.015)
 for y in [y0+.25+i*.47 for i in range(9)]:bm(label+'VerandaSoffit',(x0+.04,y,z-.015),(x1-.04,y,z-.015),.055,'woodLight',root)
# New soft play composition built around existing actual playhouse/slide geometry.
shift=CFG['playShiftXY']
for rootname in ['PlayhouseAndPlatform','LowPlayBridge','CurvedSlide']:
 root=bpy.data.objects[rootname];root.location.x+=shift[0];root.location.y+=shift[1]
sand=bpy.data.objects['SandPlayAndToys'];sand.location.x+=CFG['sandbox'][0]-oldcfg['sandbox'][0];sand.location.y+=CFG['sandbox'][1]-oldcfg['sandbox'][1]
remove(tree('SoftPlaySurface'));col('40_PLAYGROUND');matroot=G.empty('SoftPlaySurface',play)
def blob(name,x,y,rx,ry,z,mat,phase=0):
 pts=[]
 for i in range(96):
  a=i*math.tau/96;r=1+.026*math.sin(3*a+phase)+.018*math.cos(5*a+phase);pts.append((x+rx*r*math.cos(a),y+ry*r*math.sin(a)))
 return G.prism_xy(name,pts,z,.035,M[mat],matroot)
blob('SoftPlaySage',*CFG['softPlay']['centre'],*CFG['softPlay']['radii'],.038,'rubber');blob('SoftSlideLanding',-5.0,-4.3,1.35,1.05,.077,'rubberBlue');blob('SoftClimbingMeadow',-4.8,-5.25,1.45,.85,.079,'rubberOchre',.8)
climb=G.empty('LowTimberClimbingNest',play);cx,cy=CFG['climber']
# Low arched climbing ladder and knotted cross-rope web; muted timber/rope colours.
for side in [-1,1]:
 pts=[(cx-1.0+2*i/32,cy+side*.42,.13+.68*math.sin(math.pi*i/32))for i in range(33)]
 G.tube('ClimberCurvedTimberRail',pts,.048,M['wood'],climb,10)
for i in range(9):
 t=(i+.4)/9;x=cx-1+2*t;z=.13+.68*math.sin(math.pi*t);bm('ClimberLowRung',(x,cy-.42,z),(x,cy+.42,z),.06,'woodLight',climb)
for y in [cy-.20,cy+.20]:G.tube('ClimberRope',[(cx-1+2*i/32,y,.11+.68*math.sin(math.pi*i/32))for i in range(33)],.014,M['woodDark'],climb,6)
# Parent bench faces the play zone, at normal adult seating scale.
col('60_SITE_FURNITURE');bench=G.empty('CaregiverRestBench',street);x,y=CFG['parentBench']
for j in range(4):bx('ParentBenchSeatSlat',(x,y-.19+j*.125,.48),(2.35,.105,.07),'woodLight',bench,.015)
for x1 in [x-.90,x+.90]:
 for dy in [-.15,.15]:bx('ParentBenchLeg',(x1,y+dy,.24),(.07,.07,.43),'rail',bench,.012)
for z in [.73,.93]:bx('ParentBenchBackSlat',(x,y-.28,z),(2.35,.07,.13),'wood',bench,.02)
# Move only planting that would otherwise conflict with deeper rooms/play access.
for name,dx,dy in [('RearGardenA',0,.9),('RearGardenB',0,.5),('SouthwestCornerFlowers',.15,11.58),('PlaygroundFlowerBorder',-.3,-2.35),('ForecourtRimFlowers',2.2,-.75),('EntryFlowerBed',0,.18),('SoutheastTreeFlowers',1.05,.05)]:
 o=bpy.data.objects[name];o.location.x+=dx;o.location.y+=dy
# Refine canopy silhouettes: asymmetry + a single light subdivision of existing leaf masses.
for idx in range(4):
 root=bpy.data.objects['Tree_'+str(idx)]
 for j,o in enumerate([v for v in root.children_recursive if v.name.startswith('FacetedCrown')]):
  o.data=o.data.copy()
  for v in o.data.vertices:
   q=v.co.copy();v.co*=1+.035*math.sin(q.x*5.2+q.y*3.1+idx+j)
  for p in o.data.polygons:p.use_smooth=True
  sub=o.modifiers.new('GentleRoundedCrown','SUBSURF');sub.levels=1;sub.render_levels=1
  o.scale.x*=1.03 if j%2 else .97;o.scale.z*=.94 if j%3 else 1.05
# Keep the deeper verandas and west approach clear of the existing trees.
for index,d in CFG['treeRefinements'].items():
 root=bpy.data.objects['Tree_'+index];base=oldcfg['trees'][int(index)][:2];factor=d.get('scaleXYAroundOriginalTrunk',1);dx,dy=d['offsetXY']
 warp(root.children_recursive,lambda v:(base[0]+(v.x-base[0])*factor+dx,base[1]+(v.y-base[1])*factor+dy,v.z))
# Move the western lantern away from the measured arrival corridor.
lamp=bpy.data.objects['CourtyardLantern'];lamp.location.x-=1.0;lamp.location.y+=.95
# Rebuild ONLY the standalone site from the original PR11 site generator, new radius.
remove(tree('SiteAndBridgeStubs'));G.COL=bpy.data.collections['30_SITE_AND_PAVING'];site=G.empty('SiteAndBridgeStubs',model);site['role']='Standalone expanded review plinth; exclude from game integration'
R=CFG['siteRadius'];CFG_SITE=oldcfg.copy();CFG_SITE['siteRadius']=R
code=(Path(__file__).parent/'build_parent_child.py').read_text();site_code=code[code.index("R=CFG['siteRadius'];"):code.index('# Components for the second pass:')]
site_code=site_code.replace('range(-13,14)','range(-16,17)').replace('range(-11,12)','range(-13,14)')
saved_cfg=CFG;CFG=CFG_SITE;exec(compile(site_code,'PR11_site_generator','exec'));CFG=saved_cfg
# Lighten the stone variation and soften joints without removing editable paving geometry.
for m in bpy.data.materials:
 if m.name.startswith('LimestonePaver_'):
  p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.74
# Narrow roof reflections and make actual interior furniture legible through the glass.
scene.cycles.max_bounces=12;scene.cycles.transmission_bounces=10;scene.cycles.glossy_bounces=4
for o in bpy.data.objects:
 if o.type=='LIGHT' and o.name.startswith('WarmInterior'):
  o.data.energy=130;o.data.color=(1,.86,.65)
  if o.location.z>4.2:o.location.z=4.12
# Preserve exact previous camera position/rotation and lens. Only shared framing is widened.
views=json.loads((OLD/'render-record.json').read_text())['views']
framing=CFG['renderFraming']
for rec in views:
 name=Path(rec['file']).stem;o=bpy.data.objects[rec['camera']];o.location=rec['cameraPositionXYZ'];o.rotation_euler=rec['cameraRotationRadians'];o.data.lens=rec['lensMM']
 if o.data.type=='ORTHO':o.data.ortho_scale=framing[name]
scene.camera=bpy.data.objects['01_ReferenceHero'];scene.render.resolution_x=1600;scene.render.resolution_y=1096;scene.cycles.samples=96
OUT.mkdir(exist_ok=True,parents=True);(OUT/'renders').mkdir(exist_ok=True);bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'parent-child-centre.blend'),compress=True)
web=parent_child_export.export_batched(model,OUT/'parent-child-centre.glb')
deps=bpy.context.evaluated_depsgraph_get();points=[];tris=0;count=0;roles={}
for o in model.children_recursive:
 if o.type!='MESH':continue
 e=o.evaluated_get(deps);mesh=e.to_mesh();mesh.calc_loop_triangles();tris+=len(mesh.loop_triangles);count+=1;points.extend(tuple(o.matrix_world@v.co)for v in mesh.vertices);e.to_mesh_clear()
report={'sourcePR':11,'sourceBlendSHA256':CFG['sourceBlendSHA256'],'role':'Standalone model refinement only; not a live-game island radius change','blenderVersion':bpy.app.version_string,'triangles':tris,'meshObjects':count,'bounds':{'min':[min(p[i]for p in points)for i in range(3)],'max':[max(p[i]for p in points)for i in range(3)]},'webExport':web,'siteRadius':R,'materials':[{'name':m.name,'baseColorLinear':list(m.diffuse_color)}for m in M.values()]};report['sizeXYZ']=[report['bounds']['max'][i]-report['bounds']['min'][i]for i in range(3)]
(OUT/'model-report.json').write_text(json.dumps(report,indent=2));print('REFINEMENT_SAVED',json.dumps({'triangles':tris,'meshObjects':count,'size':report['sizeXYZ']}),flush=True)
