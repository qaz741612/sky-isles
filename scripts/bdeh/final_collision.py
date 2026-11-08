"""Incremental physical edits from actual evaluated final Blender components.
Keep old public ground, roofs, cameras and all world/bridge data byte-stable.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import trimesh
from shapely.geometry import Polygon,MultiPoint
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[2];D=R/'docs/design/bdeh-r21/final-qa-baseline';O=R/'docs/previews/bdeh-r21/final-qa';W=R/'work/r21-final-qa'
plan=json.loads((R/'src/data/bdeh-plan.json').read_text());surface=json.loads((R/'src/data/yuan-surface.json').read_text());world=json.loads((R/'src/data/yuan-plan.json').read_text())
def polygons(p):return[p]if p.geom_type=='Polygon'else[g for g in getattr(p,'geoms',[])if g.geom_type=='Polygon']
def footprint(mesh):
 pp=[Polygon(t[:,[0,2]])for t in mesh.vertices[mesh.faces]];pp=[p for p in pp if p.area>1e-8]
 return unary_union(pp).buffer(0)if pp else MultiPoint(mesh.vertices[:,[0,2]]).convex_hull
audit={}
for code in'BDEH':
 target=R/f'src/data/bdeh-{code.lower()}-collision.json';data=json.loads((D/f'src/data/bdeh-{code.lower()}-collision.json').read_text());parts=json.loads((W/f'{code}-polish-parts.json').read_text())
 c=plan['islands'][code]['centre'];site=Polygon(np.asarray(world['islandFootprintsXZ'][code])-np.array([c[0],c[2]]));pave=next(p for p in surface['islandPaving']if p['island']==plan['islands'][code]['name']);core=unary_union([Polygon(np.asarray(p[0])-np.array([c[0],c[2]]),[np.asarray(h)-np.array([c[0],c[2]])for h in p[1:]])for p in pave['domain']])
 npc=plan['islands'][code]['npc'][0]['position'];square=Polygon([(npc[0]+dx,npc[2]+dz)for dx,dz in[(-1.5,-1.5),(1.5,-1.5),(1.5,1.5),(-1.5,1.5)]])
 if code=='E':
  # The original tray is the only physical .33-upward surface inside this
  # rectangle. Remove those actual support faces and replace with edited mesh.
  old=np.asarray(data['supportPositions']).reshape(-1,3,3);mask=(np.abs(old[:,:,1]-.33).max(axis=1)<1e-6)&(old[:,:,0].min(axis=1)>=-9.451)&(old[:,:,0].max(axis=1)<=-4.749)&(old[:,:,2].min(axis=1)>=-11.350)&(old[:,:,2].max(axis=1)<=-9.350)
  assert mask.sum()==56,('Original evaluated tray faces not found',mask.sum());data['supportPositions']=old[~mask].ravel().tolist();data['solids']=[s for s in data['solids']if s['name']not in['RainGardenLivingWetlandBase','RainGardenLivingWetlandWater']]
 if code=='B':data['solids']=[s for s in data['solids']if s['name']!='SensoryHerbRing']
 if code=='E':data['solids']=[s for s in data['solids']if not(s['name'].startswith('PolicyCommonsAccessibleSeat')and np.mean(np.array(s['polygon'])[:,0])>0)]
 if code=='E':data['solids']=[s for s in data['solids']if not(s['name']=='trees'and np.linalg.norm(np.mean(np.array(s['polygon']),axis=0)-np.array([1.3,-10.6]))<.5)]
 changes=[];original_solids=list(data['solids'])
 for part in parts:
  if not part['physical']and part['name']not in['RainGardenLivingWetlandBase','SensoryHerbRing']:continue
  mesh=trimesh.Trimesh(vertices=part['vertices'],faces=part['faces'],process=False);mesh.update_faces(mesh.nondegenerate_faces());mesh.remove_unreferenced_vertices();trimesh.repair.fix_normals(mesh,multibody=True)
  low,high=mesh.bounds[:,1];poly=footprint(mesh);above=mesh.vertices[mesh.faces][mesh.face_normals[:,1]>.35];data['supportPositions'].extend(above.ravel().tolist())
  for shape in polygons(poly):
   assert shape.intersection(core).area<1e-5,('New physical piece enters4.8 core',code,part['name']);assert shape.intersection(square).area<1e-5,('NPC3x3 intrusion',code,part['name']);assert shape.difference(site).area<1e-4,('Outside fixed island',code,part['name'])
   data['solids'].append({'name':part['name'],'polygon':list(map(list,list(shape.exterior.coords)[:-1])),'holes':[list(map(list,list(h.coords)[:-1]))for h in shape.interiors],'base':float(low),'top':float(high),'role':'landscape'})
  for old in original_solids:
   if old['base']>=1.8 or old['top']<=low+.01 or old['base']>=high-.01:continue
   if part['name']=='SensoryHerbRing'and old['name']=='trees':continue
   if old['name']in['SensoryHerbRing','RainGardenLivingWetlandBase','RainGardenLivingWetlandWater']:continue
   old_poly=Polygon(old['polygon'],old['holes']);assert poly.intersection(old_poly).area<.004,('New furniture overlaps old hard solid',code,part['name'],old['name'],poly.intersection(old_poly).area)
  changes.append({'name':part['name'],'footprintArea':poly.area,'base':float(low),'top':float(high),'outsideIslandArea':poly.difference(site).area,'roadCoreOverlap':poly.intersection(core).area,'NPCOverlap':poly.intersection(square).area})
 # The original ground, roof support, camera and headroom must not change.
 original=json.loads((D/f'src/data/bdeh-{code.lower()}-collision.json').read_text())
 for key in['groundPositions','roofPositions','ceilingPositions','cameraPositions','dryGroundFloats']:assert data[key]==original[key],(code,key)
 target.write_text(json.dumps(data,separators=(',',':'))+'\n');audit[code]={'realPhysicalChanges':changes,'originalGroundRoofCameraUnchanged':True,'newWaterPlaneIsCollision':False,'NPC3x3Unchanged':True}
for r in json.loads((D/'LOCKS.json').read_text())['files']:assert hashlib.sha256((R/r['path']).read_bytes()).hexdigest()==r['sha256'],r['path']
(O/'physical-edit-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print('Final collision delta validated: original land/roof/camera retained;new pieces clear road/NPC/island;37 locks match')
