"""Offline measured siting options only. Never writes game plans or generated surfaces. MIT."""
from pathlib import Path
import json,math,hashlib
from shapely.geometry import Point,Polygon,LineString
from shapely import affinity
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/design/seven-policy-islands-blender-v1';plan=json.loads((ROOT/'src/data/yuan-plan.json').read_text());layout=json.loads((ROOT/'src/data/yuan-layout.json').read_text());foot=json.loads((OUT/'content-footprints.json').read_text());keys={'transport':'home','senior':'temple','industry':'koi','environment':'meadow','digital':'windmill','water':'crystal','education':'lookout'};nodes={n['island']:n for n in plan['nodes']if n.get('island')};newr={n:nodes[n]['r']for n in nodes};reports={k:json.loads((OUT/k/'model-report.json').read_text())for k in keys}
for k,island in keys.items():newr[island]=reports[k]['recommendedPlatform']['radius']
def world(poly,node):return affinity.translate(affinity.scale(poly,xfact=1,yfact=-1,origin=(0,0)),node['x'],node['z'])
def coord(poly):return {'exterior':[[round(x,5),round(y,5)]for x,y in poly.exterior.coords],'holes':[[[round(x,5),round(y,5)]for x,y in ring.coords]for ring in poly.interiors]}
roads={p['id']:LineString([(v['x'],v['z'])for v in p['points']])for p in layout['paths']};results=[]
for asset in foot['assets']:
 key=asset['id'];node=nodes[keys[key]];r=newr[keys[key]];report=reports[key];body=Polygon(asset['contentHullXY']);buffer=body.buffer(1.0,resolution=24);circle=Point(0,0).buffer(r,resolution=64);local=buffer.union(Point(0,0).buffer(node['r'],resolution=64));sample=list(buffer.exterior.coords)
 options=[]
 for ix in range(math.ceil(max(9,max(abs(p[0])for p in sample))*5),math.ceil(r*1.5*5)+1):
  rx=ix/5;ry=max(abs(y)/math.sqrt(max(1e-10,1-(x/rx)**2))for x,y in sample if abs(x)<rx)
  if any(abs(x)>=rx for x,y in sample):continue
  ry=math.ceil(max(9,ry)*5)/5
  if ry<=r*1.6:options.append((rx*ry,rx,ry))
 _,rx,ry=min(options);ellipse=affinity.scale(Point(0,0).buffer(1,resolution=96),rx,ry,origin=(0,0))
 peers=[]
 for name,other in nodes.items():
  if name==keys[key]:continue
  dist=math.hypot(node['x']-other['x'],node['z']-other['z']);peers.append({'island':name,'policyName':other['name'],'centreDistance':dist,'oldEdgeGap':dist-node['r']-other['r'],'suggestedCircleEdgeGap':dist-r-newr[name]})
 incident=[p for p in layout['paths']if node['id']in[p['from'],p['to']]];entries=[];wcircle=world(circle,node);wlocal=world(local,node);wellipse=world(ellipse,node)
 for path in incident:
  hit=roads[path['id']].intersection(wcircle.boundary);pts=[hit]if hit.geom_type=='Point'else list(hit.geoms)if hit.geom_type=='MultiPoint'else[]
  for pt in pts:
   x,y=pt.x-node['x'],-(pt.y-node['z']);angle=math.degrees(math.atan2(y,x))%360;entries.append({'path':path['id'],'worldXZ':[pt.x,pt.y],'localBlenderXY':[x,y],'angleBlenderDegrees':angle,'actualWidth':4.8,'nearestReviewStubAngleDifference':min(abs((angle-p['angleDegrees']+180)%360-180)for p in report['reviewConnections'])})
 road_relations=[]
 for path in layout['paths']:
  if node['id']in[path['from'],path['to']]:continue
  road=roads[path['id']].buffer(2.4,cap_style=2,join_style=1);a=wcircle.intersection(road).area;b=wlocal.intersection(road).area
  if a>.01 or b>.01:road_relations.append({'path':path['id'],'circleOverlapSquareUnits':a,'localExtensionOverlapSquareUnits':b,'meaning':'A non-incident fixed stroke enters proposed land; future union/entrance audit is required, not an added connection.'})
 junctions=[]
 for n in plan['nodes']:
  if n.get('island'):continue
  d=math.hypot(n['x']-node['x'],n['z']-node['z']);a=wcircle.intersection(Point(n['x'],n['z']).buffer(n['r'],resolution=32)).area;b=wlocal.intersection(Point(n['x'],n['z']).buffer(n['r'],resolution=32)).area
  if a>.01 or b>.01:junctions.append({'node':n['id'],'centreDistance':d,'circleOverlapArea':a,'localExtensionOverlapArea':b})
 closed=[]
 for room in report['rooms']:
  if room.get('base',0)>1.6 or room['name']=='OpenGardenPavilion':continue
  a,b,c,d=room['footprint'];rect=world(Polygon([(a,b),(c,b),(c,d),(a,d)]),node)
  for path in incident:
   area=rect.intersection(roads[path['id']].buffer(2.4,cap_style=2)).area
   if area>.01:closed.append({'room':room['name'],'path':path['id'],'overlapArea':area,'meaning':'Legacy straight in-island approach conflicts with closed building; author new in-island paths at integration, preserve external centreline.'})
 record={'id':key,'policyName':report['policyName'],'worldIsland':keys[key],'fixedWorldCentreXYZ':[node['x'],node['y'],node['z']],'oldGameRadius':node['r'],'assetReviewPlatformRadius':r,'circleRadiusOver12':r>12,'over12Reason':{'transport':'Full-size station and rear train/canopy sweep require 11.56 radial units before a 1m edge margin.','industry':'Greenhouse plus working/display shelter have measured corner extent beyond 11m; keep their original proportions and a rear service margin.','water':'Upper channel, control structures, basin and management hall need separate banks and observation clearance.'}.get(key),'nearestNeighbours':sorted(peers,key=lambda p:p['centreDistance'])[:3],'actualFixedBridgeEntrancesAtSuggestedCircle':entries,'reviewArmsMatchActualEntrances':False,'reviewArmsNote':'Four 4.8-wide diorama review arms follow the reference presentation; do not directly substitute them for actual B-network ports. Remove/adapt review arms only during a separately authorised integration.','proposals':{'circle':{'radius':r,'area':circle.area,'containedContentEnvelope':circle.covers(body),'usage':'Saved modelling review platform; not an approved live radius change.'},'ellipse':{'radiusX':rx,'radiusY':ry,'area':ellipse.area,'containsBufferedContent':ellipse.buffer(.002).covers(buffer),'outlineLocalBlenderXY':coord(ellipse)},'localExtension':{'method':'Existing live circle UNION actual content convex envelope buffered by 1m, excluding review bridge arms and high tree crowns.','area':local.area,'boundsLocalBlenderXY':list(local.bounds),'outlineLocalBlenderXY':coord(local),'usage':'Prefer for integration review where a full circle would absorb nearby Yuan-stroke junctions; no live geometry changed.'}},'nearbyJunctionOverlaps':junctions,'nonIncidentFixedStrokes':road_relations,'inIslandApproachConflicts':closed,'runtimeStatus':'Standalone models only; no gate alignment, runtime collision, world union or map edits performed.'}
 results.append(record);(OUT/key/'site-planning.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
pairs=[]
for i,(name,a)in enumerate(nodes.items()):
 for other,b in list(nodes.items())[i+1:]:
  d=math.hypot(a['x']-b['x'],a['z']-b['z']);pairs.append({'a':a['name'],'b':b['name'],'centreDistance':d,'edgeGapWithAllSuggestedCircles':d-newr[name]-newr[other]})
summary={'method':'Offline geometric options from actual exported vertices and unchanged B-plan coordinates. No model or game file is changed.','worldPlanSHA256':hashlib.sha256((ROOT/'src/data/yuan-plan.json').read_bytes()).hexdigest(),'allEightCirclePairs':pairs,'minimumCircleEdgeGap':min(p['edgeGapWithAllSuggestedCircles']for p in pairs),'circleIslandOverlapPairs':[p for p in pairs if p['edgeGapWithAllSuggestedCircles']<0],'warning':'Island-to-island clearance alone does not prove bridge/junction compatibility; explicit intersections and closed-building approach conflicts below remain integration work.','results':results};(OUT/'site-planning-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'minimumCircleEdgeGap':summary['minimumCircleEdgeGap'],'islandOverlapPairs':summary['circleIslandOverlapPairs'],'assets':[{'id':r['id'],'radius':r['assetReviewPlatformRadius'],'ellipse':[r['proposals']['ellipse']['radiusX'],r['proposals']['ellipse']['radiusY']],'junctionOverlaps':[v['node']for v in r['nearbyJunctionOverlaps']],'nonIncidentStrokes':[v['path']for v in r['nonIncidentFixedStrokes']]}for r in results]},ensure_ascii=False,indent=2))
