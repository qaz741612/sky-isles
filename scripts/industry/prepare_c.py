"""User-authored V2.2 geometry -> editable parts, site source and semantic collision.
Run with numpy, trimesh and shapely. Does not rebuild any other policy asset.
"""
from pathlib import Path
import runpy, json, math, hashlib, sys
import numpy as np
from shapely.geometry import MultiPoint, Polygon

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'docs/design/industry-youth-island-c-v2.2/source-package/C_產業青年_V2.2/build_industry_c_v2.py'
EXCLUDE=('bridge-guard','S14-accurate-skywalk','S15-accurate-skywalk','S16-accurate-skywalk','island-boundary-','npc-reservation-reference')

def source(refine=False):
    g=runpy.run_path(str(SOURCE))
    if refine:
        a=g['scene']
        # Two small source planters intruded into the exact 4.8 route core.
        # Move the complete planter+foliage assemblies, not the route/buildings.
        for mesh,mat,name in a.parts:
            x,y,z=mesh.bounds.mean(axis=0)
            if (name=='architectural-raised-planter' or name=='planter-layer') and abs(x-3.6)<.8 and abs(z+2.65)<.4:
                mesh.apply_translation([3.6,0,-.6])
            if name.startswith(('entry-planter','entry-flower','entry-leaf')) and z<0:
                mesh.apply_translation([.4,0,0])
        # Keep the approved envelope. Replace the opaque internal mass behind
        # the glazing with real wall thickness and a readable workshop interior.
        a.parts=[(m,mat,n) for m,mat,n in a.parts if n not in ('factory-masonry-shell','factory-main-glass-doors')]
        a.box([8.95,.25,1],[7.48,.18,6.05],'stone_cream','factory-interior-floor')
        a.box([12.60,1.8,1],[.18,3.45,6.05],'warmbrick','factory-rear-wall')
        for z in [-1.96,3.96]:
            a.box([8.95,.66,z],[7.48,.65,.18],'warmbrick','factory-side-base')
            a.box([8.95,3.25,z],[7.48,.38,.18],'bricklight','factory-side-upper')
            for x in [5.2,6.61,7.96,9.31,10.66,12.6]:
                a.box([x,1.94,z],[.16,2.25,.19],'bricklight','factory-side-pier')
        a.box([5.18,.64,1.0],[.16,.62,6.02],'warmbrick','factory-front-base')
        a.box([5.18,3.28,1.0],[.16,.32,6.02],'bricklight','factory-front-upper')
        a.box([4.97,1.43,.25],[.045,2.2,1.6],'glass_light','factory-main-glass-doors')
        for z in [-.55,.25,1.05]:
            a.box([4.93,1.43,z],[.07,2.22,.045],'steel','factory-entry-door-frame')
        for z in [-.12,.6]:a.rod([4.87,1.18,z],[4.87,1.68,z],.025,'woodlight','factory-door-pull',8)
        for z in [-.7,2.65]:
            a.box([8.2,.95,z],[2.4,.14,.76],'woodlight','factory-workbench')
            for x in [7.2,9.2]:a.box([x,.59,z],[.09,.65,.5],'steel','factory-workbench-leg')
        # Articulate load-bearing beam joints and the original PV panels, rather
        # than changing the approved sawtooth or greenhouse silhouette.
        for z in [-1.95,.07,2.09,4.03]:
            a.box([5.13,3.38,z],[.15,.28,.25],'steel','factory-beam-connection')
        # Glass tint/roughness are refined in Blender; the closed greenhouse is
        # an exhibit, approached at its west door, not an untested new interior.
        g['COL']['glass']=(115,182,184,100)
        g['COL']['glass_light']=(180,222,215,72)
        g['COL']['glass_shadow']=(104,165,172,120)
    return g,[(m,mat,n) for m,mat,n in g['scene'].parts if not n.startswith(EXCLUDE)]

def write(path,value):
    path=ROOT/path;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,separators=(',',':'),ensure_ascii=False)+'\n')

def build():
    g,parts=source('--refine' in sys.argv)
    # Floor is extracted from authored level slabs, not from foliage or all meshes.
    floor_names=('landscape-turf','NW-grass-terrace','SW-garden-terrace','NE-landscape-terrace',
      'three-road-structural-core','public-path','main-plaza','plaza-inlay-ring',
      'factory-limestone-podium','factory-forecourt-step','greenhouse-foundation',
      'greenhouse-floor','greenhouse-entry-path','exhibit-stage','terrace-vegetation-foundation',
      'plaza-inner-limestone-inlay','plaza-centre-copper-medallion','plaza-medallion-rim',
      'plaza-radial-paving-joint','plaza-inner-motif','greenhouse-timber-terrace','factory-interior-floor',
      'architectural-deck-trim','west-observation-platform','public-art-pedestal','maker-monument-plinth')
    solid_names=('factory-masonry-shell','factory-west-glazing','factory-post-west',
      'factory-main-glass-doors','greenhouse-front-glass','greenhouse-side-glass',
      'greenhouse-corner-frame','greenhouse-raised-bed','greenhouse-entrance',
      'exhibit-wood-columns','exhibit-rear-glass','tree-trunk','architectural-raised-planter',
      'entry-planter-plinth','plaza-bench-seat','courtyard-low-bollard','factory-identity-pylon',
      'factory-front-timber-fins','outdoor-makers-table','exhibit-vertical','exhibit-machinery-table',
      'factory-rear-wall','factory-side-base','factory-side-upper','factory-side-pier','factory-front-base',
      'factory-front-upper','factory-entry-door-frame','maker-portal-frame','overlook-support',
      'abstract-art-spine','innovation-sculpture-stem')
    ground=[];roof=[];support=[];camera=[];ceiling=[];solids=[];editable=[]
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
                        support.extend(t.flatten().tolist())
        if any(s in name for s in ['roof','canopy','lintel','greenhouse-arched-truss','curved-glass-panel']):
            camera.extend(v[faces].flatten().tolist());ceiling.extend(v[faces].flatten().tolist())
            # Real top support allows deliberate jumps; roof is never a checkpoint.
            for t in v[faces]:
                n=np.cross(t[1]-t[0],t[2]-t[0])
                if abs(n[1])>max(abs(n[0]),abs(n[2])):
                    if n[1]<0:t=t[[0,2,1]]
                    roof.extend(t.flatten().tolist())
    footprint=list(g['foot'].exterior.coords)[:-1]
    write(Path('src/data/industry-youth-plan.json'),{'centre':[-20.358,0,38.610],'footprintLocal':footprint,'kind':'blender-industry-campus','npc':[{'id':'industry-guide-reserved','position':[.5,0,8.35],'playerStop':[.5,0,6.95],'groundElevation':-.1,'standingSize':[3,3],'facingYaw':math.pi,'interactionRadius':1.6,'implemented':False}],'entrances':['S14','S15','S16'],'mushroomLocal':[3.0560736586,0,3.4380828659],'sourceSHA256':hashlib.sha256(SOURCE.read_bytes()).hexdigest()})
    # Collision is already rendered/queried as Float32. Quantize generated
    # proxies to the generator's 1e-5 grid, without touching visible geometry.
    # This avoids shipping long repeated Float64 decimal strings to phones.
    def quantize(v):
        if isinstance(v,float):return round(v,5)
        if isinstance(v,list):return[quantize(x)for x in v]
        if isinstance(v,tuple):return[quantize(x)for x in v]
        if isinstance(v,dict):return{k:quantize(x)for k,x in v.items()}
        return v
    write(Path('src/data/industry-youth-collision.json'),quantize({'groundPositions':ground,'supportPositions':support,'roofPositions':roof,'ceilingPositions':ceiling,'cameraPositions':camera,'solids':solids,'source':'V2.2 semantic components, not all mesh raycast; 1e-5 proxy precision'}))
    write(Path('work/industry-editable-parts.json'),{'colours':g['COL'],'parts':editable})
    p=ROOT/'src/data/yuan-plan.json';plan=json.loads(p.read_text());plan['landscapeRetainedLampAnchors']=list(dict.fromkeys(plan.get('landscapeRetainedLampAnchors',[])+['S14-L2','S15-L2','S16-L1']));plan.setdefault('islandFootprintsXZ',{})['C']=[[x-20.358,z+38.610]for x,z in footprint];p.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
    print('C site prepared: %s parts, %s solids, %s dry triangles'%(len(parts),len(solids),len(ground)//9))

if __name__=='__main__':build()
