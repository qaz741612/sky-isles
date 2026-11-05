"""R21 named source geometry -> editable Blender inputs and semantic collision.
No research GLB is dropped wholesale into the game. Source primitives are retained;
stage2 completes actual facades, roof bearings, landscape and public thresholds.
"""
from pathlib import Path
import json,math,sys,hashlib,subprocess
import numpy as np
import trimesh
from shapely.geometry import Polygon,Point,LineString,MultiPoint
from shapely.ops import unary_union,triangulate
from reference import R,D,W,load_reference
stage=1 if '--stage1'in sys.argv else 2;ref=load_reference();OUT=R/'docs/previews/bdeh-r21';OUT.mkdir(exist_ok=True)
layout=json.loads((R/'src/data/yuan-layout.json').read_text());surface=json.loads((R/'src/data/yuan-surface.json').read_text());worldPlan=json.loads((R/'src/data/yuan-plan.json').read_text())
theme={'B':'temple','D':'windmill','E':'meadow','H':'lookout'}
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
def polygon_parts(p):return [p]if p.geom_type=='Polygon'else[g for g in getattr(p,'geoms',[])if g.geom_type=='Polygon']
def triangles(p,y):
 result=[]
 for poly in polygon_parts(p):
  for t in triangulate(poly):
   if abs(t.area-t.intersection(poly).area)>1e-6:continue
   a=np.array([[x,y,z]for x,z in list(t.exterior.coords)[:3]])
   if np.cross(a[1]-a[0],a[2]-a[0])[1]<0:a=a[[0,2,1]]
   result.extend(a.ravel().tolist())
 return result
def footprint(mesh):
 if len(mesh.vertices)<50:return MultiPoint(mesh.vertices[:,[0,2]]).convex_hull
 faces=mesh.vertices[mesh.faces][:,:,[0,2]];polys=[]
 for t in faces:
  p=Polygon(t)
  if p.area>1e-8:polys.append(p)
 return unary_union(polys).buffer(0)if polys else MultiPoint(mesh.vertices[:,[0,2]]).convex_hull
def public_paths(code):
 if code=='B':return [[4.7,7],[7.2,-6.6],[7.2,-8.6],[7.2,-6.6],[7.2,-1.1],[4.4,-1.3],[.5,.2],[-1.9,-.7],[-3,-.55],[-1.9,-.7],[.5,.2],[4.7,7]]
 if code=='D':return [[0,0],[6.2,1.6],[6.1,2.72],[6.2,1.6],[8.8,1.0],[9.1,-3.55],[11.3,-3.55],[11.9,-4.9],[11.9,-6.35],[7,-7],[0,0],[-1.2,-5.5],[-1.2,-10.8],[-1.2,-5.5],[0,0]]
 if code=='E':return [[0,0],[4.7,2.8],[-1,2.4],[-6,4],[-10.55,6.5],[-6,4],[-1,2.4],[-2.4,-4.7],[-2.4,-7.9],[-7.2,-8.2],[-2.4,-7.9],[0,0]]
 return [[0,0],[0,2.5],[-5.5,2.8],[6,2.8],[6,-1.5],[0,-8.1],[-2,-4.4],[-6.3,-4.3],[-6.3,-6.36],[-6.3,-4.3],[-2,-4.4],[0,0]]
npcs={'B':{'position':[7.2,.15,-8.6],'playerStop':[7.2,.15,-7.15],'facing':0},'D':{'position':[11.9,.15,-4.9],'playerStop':[11.9,.15,-6.35],'facing':math.pi},'E':{'position':[-12.0,.15,6.5],'playerStop':[-10.55,.15,6.5],'facing':math.pi/2},'H':{'position':[0,.15,-10],'playerStop':[0,.15,-8.55],'facing':0}}
allAudit={};config={'revision':'BDEH-R21-game-v1','sourceBase':'2b4404927f33096ab28539a01f5e6236d670c038','stage':stage,'islands':{}}
for code in 'BDEH':
 s=ref.Design(code);ref.bounded_floating_island(s);ref.bridge_approach(s)
 node=next(n for n in layout['nodes']if n['id']==code);centre=np.array([node['x'],node['z']]);site=Polygon(np.asarray(worldPlan['islandFootprintsXZ'][code])-centre)
 patch=next(v for v in surface['islandPaving']if v['island']==theme[code]);pave=unary_union([Polygon(np.asarray(r[0])-centre,[np.asarray(h)-centre for h in r[1:]])for r in patch['domain']]);s._publicCorridor=pave
 ref.STRUCT[code](s);ref.theme_finish(s);ref.complete_public_realm(s)
 active={id(m)for meshes in s.meshes.values()for m in meshes};s.named=[p for p in s.named if id(p['mesh'])in active and p['name']!='Protected42_4p8CorridorGround']
 # NPC research points were only checked against roads in the package. Resolve
 # two actual tree conflicts once, deliberately, and retain each tree as a group.
 relocations={'B':[((5.6,-8.7),(4.4,-11.0)),((-10.3,5.7),(-10.3,3.7)),((-8.4,5.7),(-8.4,3.7))],'D':[((10.9,-4.4),(12.5,-1.0))],'E':[((-11.3,5.2),(-13.5,4.1))]}
 for a,b in relocations.get(code,[]):
  for part in s.named:
   t=part['tree']
   if t and np.linalg.norm(np.array(t[:2])-a)<.01:part['mesh']=part['mesh'].copy();part['mesh'].apply_translation([b[0]-a[0],0,b[1]-a[1]]);part['tree']=[*b,*t[2:]]
 if code=='H':
  for part in s.named:
   g=part.get('garden')
   if g and np.linalg.norm(np.array(g[:2])-[2,-10.6])<.01:part['mesh']=part['mesh'].copy();part['mesh'].apply_translation([1.8,0,-.5]);part['garden']=[3.8,-11.1,g[2]]
 # Restore human-scale shade at R21's authored tree groups. Main courtyard
 # specimens keep their approved larger sizes; no extra scattered trees.
 if stage==2:
  for part in s.named:
   tree=part['tree']
   if tree and tree[2]<.8:
    ratio=max(tree[2],.94 if code in 'DEH'else .86)/tree[2];m=part['mesh'].copy();origin=[tree[0],.1,tree[1]];m.apply_translation(-np.array(origin));m.apply_scale(ratio);m.apply_translation(origin);part['mesh']=m;part['tree']=[tree[0],tree[1],tree[2]*ratio,tree[3]]
 # All public paving comes from the same regenerated 22-path domain.
 for poly in polygon_parts(pave):s.hardprism('RegeneratedSharedPublicPaving',list(poly.exterior.coords)[:-1],.075,.145,'paveLight')
 # Exact union exterior: open actual mouths, never duplicate interior rails.
 for wall in surface['barriers']:
  if wall.get('island')!=theme[code]:continue
  a=[wall['a']['x']-centre[0],wall['a']['z']-centre[1]];b=[wall['b']['x']-centre[0],wall['b']['z']-centre[1]]
  if math.dist(a,b)<1e-5:continue
  s.panel('ActualUnionStoneSafetyCurb',a,b,.075,.46,'stone2',.15)
  s.girder('ActualUnionContinuousSafetyTop',(a[0],1.22,a[1]),(b[0],1.22,b[1]),.034,'civicSteel'if code=='D'else'metal',role=None)
  if int(abs(a[0]*17+a[1]*11))%4==0:s.post('ActualUnionSafetyPost',a[0],a[1],.10,1.25,.038,'metal',role=None)
 # Enclosed interiors remain closed; ground-level thresholds and open verandas
 # are real public spaces. Low forum tiers need solid infill, not floating treads.
 if code=='E'and stage==2:s.hardbox('OpenForumAccessibleLandingStep',-3.6,-8.1,.65,2.3,.075,.24,'stone2')
 if code=='H':
  for k in range(5):s.hardbox('SupportedLearningForumRiser',-6.3,-5.2-k*.58,6.7-k*.4,.62,.075,.35+k*.16,'paveLight')
 if stage==2:
  if code=='B':
   cx,cz=-3.95,-3.90
   for angle,height in [(83,5.95),(222,5.95),(227,4.65),(310,4.65)]:
    t=math.radians(angle);a=(cx+4.18*math.cos(t),cz+4.18*math.sin(t));b=(cx+7.65*math.cos(t),cz+7.65*math.sin(t))
    ref.glasswall(s,'CompletedCareWingEndFacade',a,b,.81,height-.22,5,'careGlass','careRoof','careLinen')
   for a0,a1,h in [(83,222,5.95),(227,310,4.65)]:
    angles=np.linspace(math.radians(a0),math.radians(a1),24)
    for aa,bb in zip(angles[:-1],angles[1:]):
     for rad,level in [(4.02,3.31),(7.78,3.30)]:
      p=(cx+rad*math.cos(aa),cz+rad*math.sin(aa));q=(cx+rad*math.cos(bb),cz+rad*math.sin(bb));s.panel('ContinuousCareFloorFascia',p,q,level-.14,level+.04,'careLinen',.11)
     p=(cx+7.91*math.cos(aa),cz+7.91*math.sin(aa));q=(cx+7.91*math.cos(bb),cz+7.91*math.sin(bb));s.panel('TimberCareRoofDripEdge',p,q,h+.08,h+.29,'copperdark',.09)
   # Forum is a genuine entry volume; second-floor bands connect the two wings.
   for x in [.25,1.2,2.2,3.25]:s.hardbox('FamilyForumTimberBearingSeat',x,-4.5,.18,.32,3.05,3.42,'careRoof')
  elif code=='D':
   for x,z,y in [(-6.5,-6.5,5.25),(5.9,5.9,6.55)]:s.hardbox('CivicPortalActualRoofBearing',x,z,1.15,.92,y-.25,y+.22,'civicStone')
   for x,z in [(2.75,3.15),(11.6,3.15),(11.75,9),(7.5,11),(-10.8,-9.9),(-2.75,-9.95),(-2.75,-4.85)]:
    s.post('CivicFacadeStoneCornerPier',x,z,.19,6.25 if x>0 else 5.12,.13,'civicStone')
   s.hardbox('CivicServiceEntryCanopy',6.1,2.65,3.6,1.7,3.28,3.52,'civicSteel')
   for x in [4.45,7.75]:s.post('CivicCanopyTimberColumn',x,2.0,.15,3.30,.105,'civicGold')
   for k in range(3):s.hardbox('CivicEntryRealThresholdStep',6.1,2.35+k*.32,2.25,.36,.075,.22+k*.20,'paveLight')
   for x in np.linspace(4.5,7.7,9):s.girder('CivicEntryCanopySoffit',(x,3.22,1.95),(x,3.22,3.3),.038,'civicGold')
  elif code=='E':
   from scipy.interpolate import CubicSpline
   path=np.array([[-7.9,-7.85],[-5.8,-3.2],[-2.2,.85],[2.6,3.8],[6.2,7.4]])
   spx=CubicSpline(np.arange(5),path[:,0],bc_type='natural');spz=CubicSpline(np.arange(5),path[:,1],bc_type='natural')
   last=None
   for t in np.linspace(0,4,25):
    x,z=float(spx(t)),float(spz(t));dx,dz=float(spx(t,1)),float(spz(t,1));l=math.hypot(dx,dz);nx,nz=-dz/l,dx/l;y=4.23+1.47*t/4+2.55*math.sin(t/4*math.pi)
    current=[(x+side*nx*1.28,y-.29,z+side*nz*1.28)for side in [-1,1]]
    if last:
     for a,b in zip(last,current):s.girder('GreenSpineContinuousStructuralEdge',a,b,.075,'ecoWood')
    if int(t*6)%3==0:s.girder('GreenSpineCrossLaminatedSoffit',current[0],current[1],.072,'ecoWood')
    last=current
   for x,z,y in [(-7.9,-7.85,4.12),(6.2,7.4,5.72)]:s.hardbox('GreenSpineBearingConnection',x,z,1.25,.9,y-.22,y+.15,'ecoWood')
   for x,z in [(-9.1,-9.15),(-5.8,-9.15)]:ref.bench(s,'BioswaleForumCommunityBench',x,z,1.55,'ecoWood')
   for t in np.linspace(math.pi,math.tau,13):
    x,z=-7.1+2.22*math.cos(t),-10.35+.88*math.sin(t)
    s.post('RainGardenNativeReedStem',x,z,.38,.85,.025,'ecoDeep',sides=5)
    for side in [-1,1]:s.girder('RainGardenNativeLeaf',(x,.55,z),(x+side*.12,.9,z+.08),.035,'ecoLeaf')
  else:
   # Actual clerestory wedges join occupied facade and page shell; the roof is
   # not a floating icon above a separate generic flat box.
   for lo,hi in [(-10.45,-1.95),(1.65,10.35)]:
    for z in [4.19,10.32]:
     for x0,x1 in zip(np.linspace(lo,hi,13)[:-1],np.linspace(lo,hi,13)[1:]):
      y=lambda x:7.16+2.45*(abs(x+.25)/11.4)**1.55+.34*math.sin((z-4.3)/6.5*math.pi)-.37
      v=np.array([[x0,6.62,z],[x1,6.62,z],[x1,y(x1),z],[x0,y(x0),z]])
      m=trimesh.Trimesh(vertices=v,faces=[[0,1,2],[0,2,3]],process=False);s.mesh('OccupiedBookPageClerestory',m,'eduGlass','building')
      s.girder('BookPageClerestoryHeadFrame',(x0,y(x0),z),(x1,y(x1),z),.052,'eduAmber')
      s.post('BookPageClerestoryMullion',x0,z,6.6,y(x0),.043,'eduCream')
   for x in [-9.7,-6.0,5.8,9.6]:
    y=7.16+2.45*(abs(x+.25)/11.4)**1.55-.34
    for z in [4.23,10.2]:s.girder('BookPageTriangularRoofBearing',(x,6.55,z),(x+.5,y,z),.095,'eduAmber')
 # Purposeful planting follows the original beds/roof, not new scattered props.
 if stage==2:
  finished=[]
  for part in s.named:
   if part['name']=='E_NativeGreenRoofBioStrip':continue
   if '_groupedPlants'in part['name']:
    x,y,z=part['mesh'].bounds.mean(axis=0)
    for dx,dz,scale in [(-.055,0,.13),(.07,.015,.115),(0,-.065,.105)]:
     leaf=trimesh.creation.icosphere(subdivisions=1,radius=scale);leaf.apply_scale([1,.6,1]);leaf.apply_translation([x+dx,y+.025,z+dz]);finished.append({'name':'AuthoredBedNativeLeafCluster','mesh':leaf,'material':part['material'],'tree':None})
   elif part['name']=='BiophilicRidgeLowNativePlant':
    x,z=part['mesh'].bounds.mean(axis=0)[[0,2]];y=part['mesh'].bounds[0,1];verts=[];faces=[]
    for theta in [0,2.1,4.2]:
     q=len(verts);dx,dz=.13*math.cos(theta),.13*math.sin(theta);verts.extend([[x,y,z],[x+dx*.5-dz*.35,y+.16,z+dz*.5+dx*.35],[x+dx,y+.35,z+dz],[x+dx*.5+dz*.35,y+.16,z+dz*.5-dx*.35]]);faces.extend([[q,q+1,q+2],[q,q+2,q+3]])
    finished.append({'name':'GreenSpineNativeLeafSpray','mesh':trimesh.Trimesh(vertices=verts,faces=faces,process=False),'material':'ecoDeep','tree':None})
   else:finished.append(part)
  s.named=finished
  if code=='E':
   for material,extra in [('ecoWood',.05),('ecoLeaf',.13)]:
    grid=[[[float(x),5.6+.5*(z-4.4)/5.7+.42*math.sin((x-2.4)/9.2*math.pi)+extra,float(z)]for x in np.linspace(3,10.9,25)]for z in [9.0,9.4]]
    s.patch('ConnectedRoofRainGardenPlanter'if material=='ecoWood'else'ContinuousNativeRoofPlanting',np.array(grid),material,.08)
 # Keep only current named meshes (source pruning must not resurrect R20 parts).
 parts=[p for p in s.named if p['name']!='Protected42_4p8CorridorGround']
 # Global boundary collision is owned by the generated shared union, while its
 # visible island section is in this model; these rails are not duplicated.
 ground=triangles(site,.075);dryCount=len(ground);support=[];roofFaces=[];ceilings=[];camera=[];solids=[];serialized=[];intrusions=[]
 for idx,p in enumerate(parts):
  
  if p['name']=='TieredLearningAmphitheatre':continue # replaced by complete, gap-free supported risers
  mesh=p['mesh'].copy();mesh.merge_vertices();mesh.update_faces(mesh.nondegenerate_faces());mesh.remove_unreferenced_vertices()
  if not len(mesh.faces):continue
  try:trimesh.repair.fix_normals(mesh,multibody=True)
  except ValueError:pass
  n=p['name'];low,high=float(mesh.bounds[0,1]),float(mesh.bounds[1,1]);mat=p['material'];tree=p['tree']
  terrain=n in ['FloatingRockFace','PlayableIslandTop'];rail=n.startswith('ActualUnion');paving=any(t in n for t in ['Paving','paving','PathPaver','PathInlay','PavingInlay','ColoredInlay']);land=bool(tree)or any(t in n for t in ['Garden','Flower','Plant','foliage','Reed','Leaf','Seat','Bench','CareChatPlace','RootZone']);roof=any(t in n for t in ['Roof','roof','Page','Spine','Rafter','Rib','Soffit','Canopy','PublicPortal','ElevatedWalkover'])
  role='terrain'if terrain else'rails'if rail else'paving'if paving else'landscape'if land else'roof'if roof else'building'
  glass=mat in ['careGlass','civicGlass','mistglass','eduGlass','blueglass','glass2','darkglass','deepglass']
  serialized.append({'name':f'{idx:04d}_{n}','sourceName':n,'role':role,'material':mat,'vertices':np.round(mesh.vertices,6).tolist(),'faces':mesh.faces.tolist(),'tree':tree})
  if terrain or rail:continue
  facePoints=mesh.vertices[mesh.faces];normals=mesh.face_normals
  water_surface=n=='RainGardenLivingWetlandWater'
  basin_base=n=='RainGardenLivingWetlandBase'
  walkable=paving or any(t in n for t in ['Walkable','AccessibleFloor','ForumFoundation','AccessibleLandingStep','ThresholdStep','ForumRiser','TieredLearning','AmphitheatreWood'])
  if walkable:
   ground.extend(facePoints[(normals[:,1]>.35)&(facePoints[:,:,1].min(axis=1)>-.01)].ravel().tolist())
  elif basin_base or (not land and not glass and not water_surface):
   (roofFaces if role=='roof'else support).extend(facePoints[normals[:,1]>.35].ravel().tolist())
  if role in ['building','roof']:
   camera.extend(facePoints.ravel().tolist())
   ceilings.extend(facePoints[(normals[:,1]<-.35)&(facePoints[:,:,1].min(axis=1)>1.7)].ravel().tolist())
  # Terrain-height paint, planted leaves and walkable terraces do not turn into
  # barriers. Tree trunks are real cylinders, not their whole crown envelopes.
  blocking=not walkable and not terrain and not rail and not water_surface and high>.32 and not any(t in n for t in ['foliage','flowering_tree','Plants','Leaf','Reed','BioStrip','Planting'])
  if tree and n!='trees':blocking=False
  if blocking:
   poly=footprint(mesh)
   # Thin visible clerestory glazing has a line footprint; give that actual
   # pane a 5cm physical shell, rather than omitting its collision entirely.
   if n=='OccupiedBookPageClerestory'and poly.geom_type=='LineString':poly=poly.buffer(.025,cap_style=2)
   for component in polygon_parts(poly):
    if component.area<1e-7:continue
    solids.append({'name':n,'polygon':np.round(np.asarray(component.exterior.coords)[:-1],6).tolist(),'holes':[np.round(np.asarray(h.coords)[:-1],6).tolist()for h in component.interiors],'base':low,'top':high,'role':role})
    if low<1.8 and high>.35 and component.intersection(pave).area>.015:intrusions.append({'name':n,'overlap':component.intersection(pave).area,'height':[low,high]})
 npc={**npcs[code],'id':f'{code.lower()}-policy-guide-reservation','reservation':[3,3],'interactionRadius':1.65,'implemented':False}
 region=Polygon([(npc['position'][0]+x,npc['position'][2]+z)for x,z in [(-1.5,-1.5),(1.5,-1.5),(1.5,1.5),(-1.5,1.5)]])
 npcConflicts=[x['name']for x in solids if x['base']<2 and x['top']>.32 and Polygon(x['polygon'],x['holes']).intersection(region).area>1e-5]
 colours={k:[v/255 for v in ref.r.base.rgb(ref.C[k])]for k in sorted(set(p['material']for p in serialized))}
 out={'code':code,'stage':stage,'materials':colours,'parts':serialized,'source':'User R21 named Python geometry, never R18/R20 buildings','centre':[node['x'],0,node['z']]};save(W/f'{code}-parts.json',out)
 collision={'version':'BDEH-R21','groundPositions':ground,'dryGroundFloats':dryCount,'supportPositions':support,'roofPositions':roofFaces,'ceilingPositions':ceilings,'cameraPositions':camera,'solids':solids};save(R/f'src/data/bdeh-{code.lower()}-collision.json',collision)
 config['islands'][code]={'name':theme[code],'centre':[node['x'],0,node['z']],'maxDimensions':ref.SIZES[code],'npc':[npc],'publicCircuit':public_paths(code),'kind':{'B':'r21-care-courtyard','D':'r21-civic-service-portal','E':'r21-living-green-spine','H':'r21-open-book-learning'}[code],'sizePolicy':'No world/model rescale; R21 footprint maximum retained','upperStructuresPublic':False}
 allAudit[code]={'stage':stage,'sourceTriangles':json.loads((D/'source-package/qa/geometry_audit.json').read_text())[code]['triangles'],'preparedTriangles':sum(len(p['faces'])for p in serialized),'objects':len(serialized),'lowSolidCoreIntrusions':intrusions,'NPC3x3SolidIntrusions':npcConflicts,'NPCOutsideLandArea':region.difference(site).area,'NPC4p8CoreOverlapArea':region.intersection(pave).area,'NPCRoadEdgeClearance':region.distance(pave),'publicCorridorComponents':len(polygon_parts(pave)),'sceneBounds':np.array([np.min([np.min(p['vertices'],axis=0)for p in serialized],axis=0),np.max([np.max(p['vertices'],axis=0)for p in serialized],axis=0)]).tolist()}
 print(code,'named objects',len(serialized),'low core conflicts',len(intrusions),'NPC conflicts',len(npcConflicts),flush=True)
save(R/'src/data/bdeh-plan.json',config);save(OUT/f'geometry-stage-{stage}.json',allAudit)
