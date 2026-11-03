from pathlib import Path
import json
from shapely.geometry import Polygon,LineString,box,Point
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[2];D=R/'docs/design/flood-control-island-g-v5';P=json.loads((R/'src/data/flood-control-plan.json').read_text());base=Polygon(P['footprintLocal']);C=P['centre'];L=json.loads((R/'src/data/yuan-layout.json').read_text());route=next(p for p in L['paths']if p['id']=='S22');line=LineString([(v['x']-C[0],v['z']-C[2])for v in route['points']]);bay=Polygon([(-30,-12),(-16,-9.7),(-13.2,-8.9),(-11.7,-7.6),(-11,-6.3),(-12.1,-4.8),(-16,-3.9),(-30,-3.9)]);new=base.difference(bay)
variants=[]
for name,land in [('full-reference',base),('western-entry-notch',new)]:
 water=unary_union([Polygon(p).intersection(land.buffer(-.9))for p in P['water'].values()]);intersection=line.intersection(land.boundary)
 variants.append({'name':name,'area':land.area,'bounds':land.bounds,'S22InsideLength':line.intersection(land).length,'S22OutsideLength':line.difference(land).length,'S22CentrelineBoundaryCrossings':intersection.wkt,'S22EndOutsideIsland':not land.covers(Point(line.coords[-1])),'waterArea':water.area,'S22WetCoreArea':line.buffer(2.4).intersection(water).area})
(D/'footprint-comparison.json').write_text(json.dumps({'bayCut':list(map(list,bay.exterior.coords)),'variants':variants,'decision':'Use the western-entry notch: preserve exact S22 centreline/end and real west bridge interface. Clip only southwest pool bank and relocate affected decor, do not shrink buildings.','centreUnchanged':C},indent=2)+'\n')
print('Notch comparison saved:',[(v['name'],round(v['S22OutsideLength'],2),round(v['waterArea'],2))for v in variants])
