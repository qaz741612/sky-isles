"""Read-only actual PR17 baseline and V5 package geometry audit."""
from pathlib import Path
import json,hashlib,math
from shapely.geometry import Polygon,LineString,Point
R=Path(__file__).resolve().parents[2];D=R/'docs/design/flood-control-island-g-v5';O=R/'docs/previews/flood-control-island-g-v5';O.mkdir(exist_ok=True)
def load(f):return json.loads((R/f).read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
plan=load('src/data/yuan-plan.json');ref=load('docs/design/flood-control-island-g-v5/source-package/G_V5_design_manifest.json');c=ref['GworldCentre'];land=Polygon(ref['newFootprint']);world=Polygon([(x+c[0],z+c[2])for x,z in ref['newFootprint']])
def curve(e,n=4096):
 cp=e['controlPointsXZ'];pts=[]
 for k in range(n+1):
  t=k/n
  pts.append([sum(q[j]*b for q,b in zip(cp,[(1-t)**3,3*(1-t)**2*t,3*(1-t)*t*t,t**3]))for j in [0,1]]if len(cp)==4 else[cp[0][j]*(1-t)+cp[1][j]*t for j in [0,1]])
 return LineString(pts)
roads={e['id']:curve(e)for e in plan['edges']};gaps=[]
for n in plan['nodes']:
 if not n.get('island')or n['id']=='G':continue
 poly=Polygon(plan['islandFootprintsXZ'][n['id']])if n['id']in plan['islandFootprintsXZ']else Point(n['x'],n['z']).buffer(n['r'],quad_segs=96)
 gaps.append({'id':n['id'],'island':n['island'],'edgeDistance':world.distance(poly),'overlapArea':world.intersection(poly).area})
paths=['public/prototypes/transport-elevated-station-v9/transport-station-v9-game-candidate.glb','public/models/parent-child-centre/parent-child-centre.glb','public/models/industry-youth-c/industry-youth-c.glb','src/data/elevated-station-collision.json','src/data/parent-child-collision.json','src/data/industry-youth-collision.json','src/data/industry-youth-plan.json','src/world/elevated-station.js','src/world/parent-child-model.js','src/world/industry-youth.js','src/data/bridge-landscape.json','src/sim/player.js','src/sim/movement.js','public/data/policies.json']
files=[]
for f in paths:
 p=R/f
 if p.exists():files.append({'path':f,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
# Snapshot all authored road data and non-G footprints for semantic comparison after regeneration.
save(D/'protected-baseline.json',{'baseCommit':'cd4bacba72b6a1f7bf607c687566dc14f12c4896','files':files,'yuanSource':plan,'layout':load('src/data/yuan-layout.json'),'surface':load('src/data/yuan-surface.json')})
water=[Polygon(r)for r in ref['waterBodies']];npc=Polygon([(8.7,-10.6),(11.7,-10.6),(11.7,-7.6),(8.7,-7.6)])
report={'centre':c,'newFootprintBounds':land.bounds,'area':land.area,'islandGaps':gaps,'S20':{'denseBezierSamples':4097,'centrelineGap':world.distance(roads['S20']),'core4_8Gap':world.distance(roads['S20'].buffer(2.4)),'outerRailEnvelope6_2Gap':world.distance(roads['S20'].buffer(3.1))},'waterArea':sum(w.area for w in water),'S22CoreWaterOverlap':sum(roads['S22'].buffer(2.4).intersection(Polygon([(x+c[0],z+c[2])for x,z in list(w.exterior.coords)])).area for w in water),'NPC':{'count':1,'position':[10.2,0,-9.1],'reservationArea':npc.area,'outsideIsland':npc.difference(land).area,'waterOverlap':sum(npc.intersection(w).area for w in water)},'issuesToResolve':['Reference gate piers stop above lower pool: add anchored submerged footings.','Reference dry strip separates upper/lower pools under gates: cut three real sluice throats.','Reference opaque podium blocks glazing: replace with actual walls/frames.','Reference S22 sketch balusters are incomplete and not collision: generate rails from dry shared boundary.','Reference perimeter coping crosses bridge mouths: regenerate exposed boundaries from expanded island union.'],'scope':'Preflight only; not game acceptance'}
save(D/'preflight.json',report);print('G V5 preflight saved: S20 core gap %.3f, outer rail envelope gap %.3f; protected %s assets/source files'%(report['S20']['core4_8Gap'],report['S20']['outerRailEnvelope6_2Gap'],len(files)))
