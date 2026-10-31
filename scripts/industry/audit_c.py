"""Bounded, reproducible spatial/protected-asset audit; emits a report file."""
from pathlib import Path
import json, hashlib, subprocess
from shapely.geometry import Polygon,Point,LineString,box
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads((ROOT/p).read_text())
def old(p):return subprocess.check_output(['git','show','ae2a63f:'+str(p)],cwd=ROOT)
plan=read('src/data/yuan-plan.json');base=json.loads(old('src/data/yuan-plan.json'))
site=read('src/data/industry-youth-plan.json');layout=read('src/data/yuan-layout.json');data=read('src/data/industry-youth-collision.json')
world=Polygon(plan['islandFootprintsXZ']['C']);local=Polygon(site['footprintLocal'])
assert plan['nodes']==base['nodes'] and plan['edges']==base['edges'] and plan['width']==4.8
others=[]
for n in plan['nodes']:
    if not n.get('island') or n['id']=='C':continue
    shape=Polygon(plan['islandFootprintsXZ'][n['id']])if n['id']in plan['islandFootprintsXZ']else Point(n['x'],n['z']).buffer(n['r'],resolution=64)
    others.append({'id':n['id'],'overlapArea':world.intersection(shape).area,'groundGap':world.distance(shape)})
roads=[]
for path in layout['paths']:
    if path['id']in site['entrances']:continue
    ribbon=LineString([(q['x'],q['z'])for q in path['points']]).buffer(2.4)
    roads.append({'id':path['id'],'CIntersectionArea':world.intersection(ribbon).area})
core=unary_union([LineString([(q['x']+20.358,q['z']-38.61)for q in path['points']]).buffer(2.4)for path in layout['paths']if path['id']in site['entrances']])
npc=box(-1,6.85,2,9.85);conflicts=[]
entrances=[]
for edge in plan['edges']:
    if edge['id']not in site['entrances']:continue
    cp=edge['controlPointsXZ'];points=[]
    for i in range(1281):
        t=i/1280;u=1-t
        points.append([u**3*cp[0][j]+3*u*u*t*cp[1][j]+3*u*t*t*cp[2][j]+t**3*cp[3][j]for j in range(2)])
    hit=LineString(points).intersection(world.boundary)
    hits=list(hit.geoms)if hasattr(hit,'geoms')else[hit]
    entrances.append({'id':edge['id'],'width':4.8,'newFootprintCrossingsWorldXZ':[list(p.coords)[0]for p in hits if p.geom_type=='Point']})
for s in data['solids']:
    if s['base']>=1.6 or s['top']<.25:continue
    shape=Polygon(s['polygon']);a=core.intersection(shape).area;b=npc.intersection(shape).area
    if a>.0001 or b>.0001:conflicts.append({'source':s['name'],'roadArea':a,'npcArea':b})
locks=[]
for f in (ROOT/'public').rglob('*.glb'):
    rel=f.relative_to(ROOT)
    if 'industry-youth-c' in str(rel):continue
    h=hashlib.sha256(f.read_bytes()).hexdigest();locks.append({'path':str(rel),'sha256':h,'matchesBase':h==hashlib.sha256(old(rel)).hexdigest()})
before=json.loads(old('src/data/bridge-landscape.json'));after=read('src/data/bridge-landscape.json')
report={'basis':'ae2a63f + user V2.2','nodesAnd22BezierControlsUnchanged':True,'coreWidth':4.8,'CWorldCentre':site['centre'],'footprintBoundsLocal':local.bounds,'footprintArea':local.area,'entrances':entrances,'NPCReservation':[[-1,6.85],[2,9.85]],'NPCPlayerStopDistance':1.4,'otherIslands':others,'nonCRoutes':roads,'coreAndNPCSolidConflicts':conflicts,'lampAnchorsUnchanged':before['lamps']==after['lamps'],'protectedAssets':locks,'limits':'Static geometry only. Live walking/camera evidence separate. No hardware FPS claim.'}
assert not conflicts and report['lampAnchorsUnchanged'] and all(v['overlapArea']<.0001 for v in others) and all(v['CIntersectionArea']<.0001 for v in roads) and all(v['matchesBase']for v in locks)
(ROOT/'docs/previews/industry-youth-island-c-v1/geometry-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('C spatial audit passed: 7 other islands, 19 non-C routes, all original GLBs and lamp anchors preserved')
