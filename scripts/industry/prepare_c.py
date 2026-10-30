"""User-authored V2.2 geometry -> editable parts, site source and semantic collision.
Run with numpy, trimesh and shapely. Does not rebuild any other policy asset.
"""
from pathlib import Path
import runpy, json, math, hashlib
import numpy as np
from shapely.geometry import MultiPoint, Polygon

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'docs/design/industry-youth-island-c-v2.2/source-package/C_產業青年_V2.2/build_industry_c_v2.py'
EXCLUDE=('bridge-guard','S14-accurate-skywalk','S15-accurate-skywalk','S16-accurate-skywalk','island-boundary-','npc-reservation-reference')

def source():
    g=runpy.run_path(str(SOURCE))
    return g,[(m,mat,n) for m,mat,n in g['scene'].parts if not n.startswith(EXCLUDE)]

def write(path,value):
    path=ROOT/path;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,separators=(',',':'),ensure_ascii=False)+'\n')

def build():
    g,parts=source()
    # Floor is extracted from authored level slabs, not from foliage or all meshes.
    floor_names=('landscape-turf','NW-grass-terrace','SW-garden-terrace','NE-landscape-terrace',
      'three-road-structural-core','public-path','main-plaza','plaza-inlay-ring',
      'factory-limestone-podium','factory-forecourt-step','greenhouse-foundation',
      'greenhouse-floor','greenhouse-entry-path','exhibit-stage','terrace-vegetation-foundation',
      'plaza-inner-limestone-inlay','plaza-centre-copper-medallion','plaza-medallion-rim',
      'plaza-radial-paving-joint','plaza-inner-motif','greenhouse-timber-terrace')
    solid_names=('factory-masonry-shell','factory-west-glazing','factory-post-west',
      'factory-main-glass-doors','greenhouse-front-glass','greenhouse-side-glass',
      'greenhouse-corner-frame','greenhouse-raised-bed','greenhouse-entrance',
      'exhibit-wood-columns','exhibit-rear-glass','tree-trunk','architectural-raised-planter',
      'entry-planter-plinth','plaza-bench-seat','courtyard-low-bollard','factory-identity-pylon',
      'factory-front-timber-fins','outdoor-makers-table','exhibit-vertical', 'maker-portal-frame')
    ground=[];roof=[];camera=[];ceiling=[];solids=[];editable=[]
    for mesh,mat,name in parts:
        v=np.asarray(mesh.vertices);faces=np.asarray(mesh.faces);lo,hi=mesh.bounds
        editable.append({'name':name,'material':mat,'vertices':v.tolist(),'faces':faces.tolist()})
        if name.startswith(floor_names):
            for t in v[faces]:
                if np.ptp(t[:,1])<1e-5 and abs(t[0,1]-hi[1])<1e-4:
                    if np.cross(t[1]-t[0],t[2]-t[0])[1]<0:t=t[[0,2,1]]
                    ground.extend(t.flatten().tolist())
        if name.startswith(solid_names) and hi[1]>.25 and hi[1]-lo[1]>.02:
            hull=MultiPoint(v[:,[0,2]]).convex_hull
            if isinstance(hull,Polygon) and hull.area>.0001:
                solids.append({'name':name,'base':round(float(lo[1]),5),'top':round(float(hi[1]),5),'polygon':list(hull.exterior.coords)[:-1]})
                camera.extend(v[faces].flatten().tolist())
                for t in v[faces]:
                    if np.ptp(t[:,1])<1e-5 and abs(t[0,1]-hi[1])<1e-4:
                        if np.cross(t[1]-t[0],t[2]-t[0])[1]<0:t=t[[0,2,1]]
                        roof.extend(t.flatten().tolist())
        if any(s in name for s in ['roof','canopy','lintel','greenhouse-arched-truss','curved-glass-panel']):
            camera.extend(v[faces].flatten().tolist());ceiling.extend(v[faces].flatten().tolist())
            # Real top support allows deliberate jumps; roof is never a checkpoint.
            for t in v[faces]:
                n=np.cross(t[1]-t[0],t[2]-t[0])
                if abs(n[1])>max(abs(n[0]),abs(n[2])):
                    if n[1]<0:t=t[[0,2,1]]
                    roof.extend(t.flatten().tolist())
    footprint=list(g['foot'].exterior.coords)[:-1]
    write(Path('src/data/industry-youth-plan.json'),{'centre':[-20.358,0,38.610],'footprintLocal':footprint,'kind':'blender-industry-campus','npc':[{'id':'industry-guide-reserved','position':[.5,0,8.35],'playerStop':[.5,0,6.45],'standingSize':[3,3],'facingYaw':math.pi,'interactionRadius':1.6,'implemented':False}],'entrances':['S14','S15','S16'],'mushroomLocal':[3.0560736586,0,3.4380828659],'sourceSHA256':hashlib.sha256(SOURCE.read_bytes()).hexdigest()})
    write(Path('src/data/industry-youth-collision.json'),{'groundPositions':ground,'roofPositions':roof,'ceilingPositions':ceiling,'cameraPositions':camera,'solids':solids,'source':'V2.2 semantic components, not all mesh raycast'})
    write(Path('work/industry-editable-parts.json'),{'colours':g['COL'],'parts':editable})
    p=ROOT/'src/data/yuan-plan.json';plan=json.loads(p.read_text());plan['landscapeRetainedLampAnchors']=list(dict.fromkeys(plan.get('landscapeRetainedLampAnchors',[])+['S14-L2','S15-L2','S16-L1']));plan.setdefault('islandFootprintsXZ',{})['C']=[[x-20.358,z+38.610]for x,z in footprint];p.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
    print('C site prepared: %s parts, %s solids, %s dry triangles'%(len(parts),len(solids),len(ground)//9))

if __name__=='__main__':build()
