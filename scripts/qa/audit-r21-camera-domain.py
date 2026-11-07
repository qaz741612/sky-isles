"""Verify four local camera domains do not extend onto protected island land."""
from pathlib import Path
import json
from shapely.geometry import Point,Polygon
R=Path(__file__).resolve().parents[2];world=json.loads((R/'src/data/yuan-plan.json').read_text());plan=json.loads((R/'src/data/bdeh-plan.json').read_text());sites={}
for code in['A','C','F','G']:
 node=next(n for n in world['nodes']if n['id']==code)
 sites[code]=Polygon(world['islandFootprintsXZ'][code])if code in world['islandFootprintsXZ']else Point(node['x'],node['z']).buffer(node['r'],quad_segs=128)
rows=[]
for code,v in plan['islands'].items():
 area=Point(v['centre'][0],v['centre'][2]).buffer(max(v['maxDimensions'])/2+2,quad_segs=128)
 overlap={c:area.intersection(site).area for c,site in sites.items()};assert all(v<1e-7 for v in overlap.values()),(code,overlap)
 rows.append({'code':code,'protectedSiteOverlap':overlap})
(R/'docs/previews/bdeh-r21/final-qa/camera-domain-audit.json').write_text(json.dumps({'method':'Full local camera domain disks vs actual F/C/G footprint polygons and actual A configured radius circle; all16 intersections zero','rows':rows},indent=2)+'\n')
print('Four local camera domains: zero overlap with all four protected island lands')
