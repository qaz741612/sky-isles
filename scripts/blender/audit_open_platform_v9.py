"""Additional open-platform collision candidate/visibility audit, never game QA. MIT."""
import bpy,sys,os,json,hashlib,math
from pathlib import Path
import numpy as np
from mathutils import Vector
from shapely.geometry import Polygon,LineString,box
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/design/transport-elevated-station-v9-prototype';file=OUT/'transport-station-v9.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();h=sha(file);bpy.ops.wm.open_mainfile(filepath=str(file));bpy.context.view_layer.update();root=bpy.data.objects['YuanliElevatedStationV9'];deps=bpy.context.evaluated_depsgraph_get();rows=json.loads((OUT/'collision-shells.json').read_text())['shells'];site=Polygon(json.loads((OUT/'model-report.json').read_text())['sitePolygonXZ'])
assert not bpy.data.objects.get('Canopy')
for n in ['StandingSeamRoofWing','HallSkylight','TimberFacadeFin','OriginalStationName','LoadBearingArchFascia','PhysicalStairTread','LiftTowerPost']:assert any(o.name.startswith(n)for o in root.children_recursive),n
# All upper route samples use real geometry-supported catalogue floor. No steps certified.
upper=[p for p in rows if p['bottom']<5.25 and p['top']>3.75 and p['role']not in ['walkable','stepped_walkable']and p['kind']!='train'and p['id']not in ['LiftShaft']and not p['id'].startswith(('Hall','StandingSeamRoof','RoofSky','HallSkylight'))]
checks=[]
for name,route in [('platform-clear-lane',LineString([(-8.90,-6.64),(8.90,-6.64)])),('stair-upper-connector',LineString([(-6.52,-3.14),(-6.52,-6.64)])),('lift-upper-connector',LineString([(7.70,-5.80),(7.70,-6.64)]))]:
 body=route.buffer(.33,cap_style=2);hits=[p['id']for p in upper if Polygon(p['polygonXZ']).intersection(body).area>1e-5];checks.append({'route':name,'radius':.33,'intersectingShells':hits});assert not hits,(name,hits)
# One true shelter; its footprint must stay completely away from the train swept plan.
shelter=box(-7.41,-4.59,-5.63,-2.81);train=next(p for p in rows if p['kind']=='train');sweep=Polygon(train['polygonXZ']);assert sweep.intersection(shelter).area==0
# Actual ground bench low geometry, not just a renamed old proxy, within terrace and outside NPC squares.
furniture=[]
for o in root.children_recursive:
 if o.type!='MESH' or not o.name.startswith('GardenWaitingBench'):continue
 points=[o.matrix_world@Vector(v)for v in o.bound_box];from shapely.geometry import MultiPoint
 p=MultiPoint([(v.x,-v.y)for v in points]).convex_hull
 if p.geom_type=='Polygon':furniture.append(p)
from shapely.ops import unary_union
benches=unary_union(furniture);benchOutside=benches.difference(site).area
assert benchOutside<1e-5,benchOutside
# Projections of actual evaluated vertices; head bounding box stays entirely within strict portrait.
parts={name:[]for name in ['cab','train','entrance','structure']}
for o in root.children_recursive:
 if o.type!='MESH':continue
 role=o
 while role.parent and role.parent!=root:role=role.parent
 keys=[]
 if role.name=='TrainRollingStock':keys.append('train')
 if o.name.startswith(('OriginalRoundedCabNose','CabNoseFrameWithRealOpening','CabWindowGasket','CabActualWindscreen','CabHeadlight')):keys.append('cab')
 if o.name.startswith(('DeepEntryHeader','EntryPortalPost','LevelEntryThreshold','StationIdentityPlaque','OriginalStationName')):keys.append('entrance')
 if role.name=='Viaduct':keys.append('structure')
 if not keys:continue
 e=o.evaluated_get(deps);me=e.to_mesh();points=[tuple(o.matrix_world@v.co)+(1,)for v in me.vertices]
 for k in keys:parts[k]+=points
 e.to_mesh_clear()
framing=[]
for camera,w,hgt in [('hero',1440,1080),('player-desktop',1440,900),('player-mobile',720,1280)]:
 cam=bpy.data.objects[camera];pr=np.array(cam.calc_matrix_camera(deps,x=w,y=hgt))@np.array(cam.matrix_world.inverted());p={}
 for k,pts in parts.items():
  q=pr@np.array(pts).T;ndc=q[:2]/q[3];inside=(np.max(abs(ndc),axis=0)<=1);p[k]={'allVerticesInFrame':bool(inside.all()),'vertexFractionInFrame':float(inside.mean()),'minNDC':ndc.min(axis=1).tolist(),'maxNDC':ndc.max(axis=1).tolist()}
 framing.append({'camera':camera,'viewport':[w,hgt],'parts':p,'scope':'Framing of real evaluated geometry, not a pixel visibility or gameplay proof.'})
assert all(v['parts']['cab']['allVerticesInFrame']and v['parts']['entrance']['allVerticesInFrame']for v in framing)
# A ray to the front windscreen cannot be obstructed by new shelter/platform objects.
rayChecks=[];cab=bpy.data.objects['CabActualWindscreen']
# Source cab has world geometry as local coordinates, train parent supplies rigid rotation.
for n in ['hero','player-mobile']:
 cam=bpy.data.objects[n];target=cab.matrix_world@(sum((v.co for v in cab.data.vertices),Vector())/len(cab.data.vertices));d=target-cam.location;hit,loc,norm,face,obj,matrix=bpy.context.scene.ray_cast(deps,cam.location,d.normalized(),distance=d.length+.1);allowed=bool(hit and (obj.name.startswith(('Cab','OriginalRoundedCabNose'))));rayChecks.append({'camera':n,'firstHit':obj.name if hit else None,'cabFirstHit':allowed});assert allowed,rayChecks[-1]
assert sha(file)==h
r={'sourceBlendSHA256':h,'upperRouteChecks':checks,'shelterTrainOverlapArea':sweep.intersection(shelter).area,'shelterClearanceAboveUpperWalk':5.69-3.75,'groundBenchesOutsideSiteArea':benchOutside,'retainedGroundRoofAndIdentity':True,'canopyRemaining':False,'framing':framing,'cabRayChecks':rayChecks,'knownLimits':['Offline geometry/proxy checks only, no runtime capsule or mobile-device proof.','Strict portrait retains west cab and entrance but crops east trailing end/outer supports.','Static train, lift nonfunctional, stair step controller absent; not gameplay integration.']};(OUT/'open-platform-audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False),flush=True);sys.stdout.flush();os._exit(0)
