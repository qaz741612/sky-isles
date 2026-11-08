"""Compare identical actual-Player H diagnostics, never infer hardware FPS."""
from pathlib import Path
import json,math,hashlib
R=Path(__file__).resolve().parents[2];W=R/'work/r21-final-qa';O=R/'docs/previews/bdeh-r21/final-qa/performance';O.mkdir(exist_ok=True)
a=json.loads((W/'H-native-before.json').read_text());b=json.loads((W/'H-spatial-after.json').read_text())
assert a['codes']==b['codes']=='H'and a['marks'][-1]['ticks']==b['marks'][-1]['ticks']
x,y=a['result']['records'][0],b['result']['records'][0]
for key in ['route','edgeProbes','orbitProbes','availableBoundarySegments','sampledBoundarySegments','excludedEdgeStarts']:assert x[key]==y[key],key
assert math.dist(x['end'],y['end'])<1e-8
models={}
for code in'BDEH':
 paths=[R/f'work/r21-final-candidate26-dist/models/bdeh-r21/{code}.glb',R/f'work/r21-final-spatial-dist/models/bdeh-r21/{code}.glb',R/f'public/models/bdeh-r21/{code}.glb'];values=[hashlib.sha256(p.read_bytes()).hexdigest()for p in paths];assert len(set(values))==1;models[code]=values[0]
for name,r in [('H-native-before.json',a),('H-spatial-after.json',b)]:(O/name).write_text(json.dumps(r,indent=2)+'\n')
(O/'camera-index-comparison.json').write_text(json.dumps({'method':'Same real Player helper, same H public path,8 requested orbit directions,22 valid boundary probes,4,132 fixed60Hz ticks; all8 models loaded. Renderer/native loop disabled in both. Same four GLB bytes in frozen snapshots, same final player position. Different JS backend only. Shared2-core cloud CPU; not phone FPS or human comfort.','modelSHA256':models,'beforeBundleSHA256':a['bundleSHA256'],'afterBundleSHA256':b['bundleSHA256'],'beforeMs':a['elapsedMs'],'afterMs':b['elapsedMs'],'ratio':a['elapsedMs']/b['elapsedMs'],'ticks':b['marks'][-1]['ticks'],'actualEndDistance':math.dist(x['end'],y['end']),'afterTriangleIndex':b['result']['r21CameraIndex']},indent=2)+'\n')
print('Same H audit:',a['elapsedMs'],'→',b['elapsedMs'],'ms; no hardware FPS claim.')
