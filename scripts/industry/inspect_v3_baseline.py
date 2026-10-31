"""Read-only PR17 .blend measurement before V3; no geometry/render/save calls."""
from pathlib import Path
import bpy,json,hashlib

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/design/industry-youth-island-c-v3/preflight'
OUT.mkdir(parents=True,exist_ok=True)
collection=bpy.data.collections.get('EXPORT_AND_RENDER')
if not collection:raise RuntimeError('Expected PR17 editable Blender display collection missing')

def box(objects):
    vertices=[o.matrix_world@v.co for o in objects if o.type=='MESH'for v in o.data.vertices]
    if not vertices:return None
    lo=[min(v[i]for v in vertices)for i in range(3)];hi=[max(v[i]for v in vertices)for i in range(3)]
    # Blender (x,-z,y) -> Three.js (x,y,z)
    a=[lo[0],lo[2],-hi[1]];b=[hi[0],hi[2],-lo[1]]
    return {'minLocalXYZ':a,'maxLocalXYZ':b,'dimensionsXYZ':[b[i]-a[i]for i in range(3)]}

objects=list(collection.objects);groups={}
for area in ['00_TerrainAndPlaza','01_Workshop','02_Greenhouse','03_Exhibition','04_GardensAndFurniture']:
    group=[o for o in objects if o.get('sourceArea')==area]
    groups[area]={'objectCount':len(group),'bounds':box(group)}
editable=bpy.data.collections.get('EDITABLE_COMPONENTS')
building_sets={
 'workshop_with_eaves':[o for o in editable.objects if o.get('semanticArea')=='01_Workshop' and o.get('sourceComponent')not in ['entry-planter-plinth']],
 'greenhouse_without_approach_paving':[o for o in editable.objects if o.get('semanticArea')=='02_Greenhouse' and 'path'not in o.get('sourceComponent','')],
 'old_exhibition_pavilion':[o for o in editable.objects if o.get('sourceComponent','').startswith(('exhibit-','exhibition-','pavilion-'))],
}
source=Path(bpy.data.filepath)
report={'sourceCommit':'0c7cab7e7e2a75537363a7736206aaa8134787f6','sourceBlend':str(source.relative_to(ROOT)),'sourceBlendSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'readOnly':True,'worldCentre':[-20.358,0,38.610],'displayObjects':len(objects),'editableObjects':len(editable.objects),'wholeAssetBounds':box(objects),'renderAreaBounds':groups,'architecturalBounds':{name:box(obs)for name,obs in building_sets.items()},'limits':['Existing PR17 measured, not V3 measurements.','Merged area bounds may include podium, canopy, plants, signs; use component/collision geometry for detailed clearance.','No Blender geometry saved, exported or rebuilt by this inspection.']}
(OUT/'baseline-blender-bounds.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Read-only baseline Blender inspection saved; %s visible batches'%len(objects))
