"""Apply only R21's candidate coordinates and four bounded footprints.
Keep F/A/C/G assets and centres byte-protected. No compression is multiplied.
"""
from pathlib import Path
import json,hashlib,subprocess,sys
import numpy as np
from shapely.geometry import Polygon,LineString
from reference import R,D,W,load_reference
O=R/'docs/previews/bdeh-r21';O.mkdir(parents=True,exist_ok=True)
original=D/'baseline';original.mkdir(exist_ok=True)
source='2b4404927f33096ab28539a01f5e6236d670c038'
paths=['src/data/yuan-plan.json','src/data/yuan-layout.json','src/data/yuan-surface.json','src/data/bridge-landscape.json']
for name in paths:
 p=original/Path(name).name
 if not p.exists():p.write_bytes(subprocess.check_output(['git','show',source+':'+name],cwd=R))
baseline=json.loads((original/'yuan-plan.json').read_text());plan=json.loads(json.dumps(baseline));ref=load_reference();candidate=ref.road
for node in plan['nodes']:
 if node['id']in ['B','E','T4','T6','T7']:
  node['x'],node['z']=candidate['nodes'][node['id']]
for edge in plan['edges']:
 row=next(r for r in candidate['allRoutesProposed']if r['id']==edge['id']);
 if row['changed']:edge['controlPointsXZ']=row['proposedControlPointsXZ']
# The B courtyard is not a through road. One shared grounded hub joins its four
# existing bridge mouths along R21's north/east circulation, not through wings.
plan['islandApproaches']={'B':{'hubLocal':[4.7,7.0],'source':'R21 bridge_approach; explicit local north/east connectors, rounded within the candidate corridor','waypointsLocal':{'S13':[[-8.9,7.1],[-3,7.6],[4.7,7]],'S14':[[4.7,7]],'S08':[[10,-.4],[9,4.2],[4.7,7]],'S12':[[10.5,-4],[10,-.4],[9,4.2],[4.7,7]]}}}
isles={n['id']:n for n in plan['nodes']if n.get('island')};sizes={'B':[30,28],'D':[32,29],'E':[34,31],'H':[33,30]};footprints=plan.setdefault('islandFootprintsXZ',{})
for code,(width,depth)in sizes.items():
 angle=np.linspace(0,np.pi*2,144,endpoint=False);r=np.minimum(.999,.989+.0045*np.sin(3*angle+.6)+.004*np.sin(7*angle-.2));n=isles[code]
 footprints[code]=[[round(float(n['x']+width/2*k*np.cos(t)),5),round(float(n['z']+depth/2*k*np.sin(t)),5)]for t,k in zip(angle,r)]
plan['preservedApproaches']={'S14':{'end':'to','fraction':.60,'reason':'Keep approved C exact mouth and clear original plaza bench'},'S02':{'end':'from','fraction':.28,'reason':'Keep approved A exact bridge interface'}}
plan['referenceBaselineEdges']={e['id']:e['controlPointsXZ']for e in baseline['edges']}
# Preview and audit exact site/route proposals before generation.
polys={c:Polygon(footprints[c])for c in sizes};conflicts=[]
for a,p in polys.items():
 for b in sizes:
  if a<b and p.intersection(polys[b]).area>1e-5:conflicts.append({'a':a,'b':b,'overlap':p.intersection(polys[b]).area})
 for n in baseline['nodes']:
  if n['id']not in ['F','A','C','G']:continue
  ring=baseline.get('islandFootprintsXZ',{}).get(n['id']);q=Polygon(ring)if ring else __import__('shapely').geometry.Point(n['x'],n['z']).buffer(n['r'],resolution=80)
  if p.intersection(q).area>1e-5:conflicts.append({'a':a,'protected':n['id'],'overlap':p.intersection(q).area})
report={'baseCommit':source,'scope':'Source package candidate, not game acceptance','sizes':sizes,'T4':[51,-47],'protectedCentresUnchanged':all(next(x for x in plan['nodes']if x['id']==c)==next(x for x in baseline['nodes']if x['id']==c)for c in ['F','A','C','G']),'changedEdges':[e['id']for e in plan['edges']if e['controlPointsXZ']!=next(x for x in baseline['edges']if x['id']==e['id'])['controlPointsXZ']],'planarIslandConflicts':conflicts,'BInternalConflict':'Radial B road centre traces cut the R21 occupied wings. Keep four mouth intersections and use the supplied north/east connectors to a shared local hub(4.7,7); generator and real Player must use this same geometry.','dependencies':['R21 build_r21.py','R20/R18 primitive engine only','PR18 G V5.1 actual game base'],'notAcceptedYet':['Bridge/landscape/lamp clearance','Actual building hulls','Player/camera/mobile','Human art and true device performance']}
assert report['protectedCentresUnchanged']and not conflicts,report
(O/'SITE-PREFLIGHT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(R/'src/data/yuan-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
print('R21 source site configured once; four bounded footprints, protected F/A/C/G centres, nine candidate edges, B shared interior hub')
