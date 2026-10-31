"""Refine V3 architecture into existing PR17 land; no proxy terrain import.
Source geometry stays traceable; local adjustments are central JSON parameters.
"""
from pathlib import Path
import runpy,json,math,sys,hashlib
import numpy as np
import trimesh
from shapely.geometry import Polygon,MultiPoint,Point,LineString,box
from shapely.ops import unary_union
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_c

ROOT=Path(__file__).resolve().parents[2]
CONFIG=ROOT/'src/data/industry-youth-v3-buildings.json'
SOURCE=ROOT/'docs/design/industry-youth-island-c-v3/source-package/C_island_v3_geometry.py'

def author():
    base,old=prepare_c.source(True);a=base['scene'];cfg=json.loads(CONFIG.read_text());roles={};detail=1 if '--pass1'in sys.argv else 2
    # Original authored land/plaza retained verbatim. Replace only architecture
    # and the now-obstructive small props; do not adopt proxy land/roads.
    keep_prefix=('landscape-turf','floating-rock','cliff-scree','NW-grass','SW-garden','NE-landscape',
      'three-road-structural-core','public-path','main-plaza','plaza-','mushroom-visual')
    a.parts=[(m,mat,n)for m,mat,n in old if n.startswith(keep_prefix)]
    base['COL'].update({'v3_copper':(216,148,94),'v3_brick':(181,139,103),'v3_metal':(54,75,87)})
    src=runpy.run_path(str(SOURCE));src['M'].clear()
    for name in ['workshop','youth','greenhouse']:src[name]()
    palette={'cliff_top':'stone_cream','woodlight':'woodlight','wood':'wood','steel':'steel','steel2':'steel_light','metal':'v3_metal','glass':'glass','glass2':'glass_light','roof':'roof','solar':'solar','copper':'v3_copper','gold':'woodlight','white':'stone_bright','accent':'solar_hi','soil':'soil','plant':'plant_leaf','leaf3':'plant_yellow'}
    # Discard only the solid schematic masses behind glass. Real facade wall
    # bands/piers, beams, soffits and closed glass doors are built below.
    omit={'w wall shell','y south wing shell','y front ground shell'}
    if detail==2:omit.update(['y long roof plate','y raised north roof parapet','y upper clerestory glazing'])
    def add(mesh,mat,name,role=None):
        a.parts.append((mesh,mat,name))
        if role:roles[name]=role
    def placed(mesh,group):
        mesh=trimesh.Trimesh(vertices=mesh.vertices.copy(),faces=mesh.faces.copy(),process=False)
        c=cfg[group];px,pz=c['sourcePivotXY'];s=c['uniformBuildingScale'];dx,dz=c['translationXZ'];v=mesh.vertices.copy()
        mesh.vertices=np.column_stack((px+(v[:,0]-px)*s+dx,v[:,2]*s,pz+(v[:,1]-pz)*s+dz))
        mesh.faces=mesh.faces[:,[0,2,1]] # axis swap reflection
        return mesh
    for name,m,col in src['M']:
        if name in omit or(detail==2 and name.startswith('g seedlings')):continue
        group={'w':'workshop','y':'youth','g':'greenhouse'}[name[0]]
        prefix={'w':'factory','y':'exhibition','g':'greenhouse'}[name[0]]
        n=prefix+'-v3-'+name[2:].replace(' ','-')
        mesh=placed(m,group)
        if name.startswith('w sawtooth roof panel'):
            v=mesh.vertices.copy();verts=np.concatenate((v,v-[0,.075,0]));mesh=trimesh.Trimesh(vertices=verts,faces=[[0,1,2],[0,2,3],[4,6,5],[4,7,6],[0,4,5],[0,5,1],[1,5,6],[1,6,2],[2,6,7],[2,7,3],[3,7,4],[3,4,0]],process=False)
        role='roof'if any(k in name for k in ['roof','canopy','lintel','arch rib','arch rail','blueglass'])else'floor'if name in ['w base slab','y plinth','g low plinth']else'solid'
        if 'seedlings'in name:role=None
        # Faceted glazed roof panels are real thin surfaces, not massive boxes.
        add(mesh,palette[col],n,role)

    # Helpers use original V3 coordinates and the same placement transform.
    def block(group,name,ctr,size,mat,role='solid'):
        m=trimesh.creation.box(extents=size);m.apply_translation(ctr);add(placed(m,group),mat,name,role)
    def rod(group,name,A,B,r,mat,role='solid'):
        A=np.array(A);B=np.array(B);d=B-A;m=trimesh.creation.cylinder(radius=r,height=np.linalg.norm(d),sections=8);m.apply_transform(trimesh.geometry.align_vectors([0,0,1],d/np.linalg.norm(d)));m.apply_translation((A+B)/2);add(placed(m,group),mat,name,role)
    # Workshop full front/side/rear thickness, glazing bands and exposed joints.
    for yy in [-3.89,2.59]:
        block('workshop','factory-v3-wall-sill',[9.95,yy,.55],[7.3,.15,.70],'v3_brick')
        block('workshop','factory-v3-wall-head',[9.95,yy,4.72],[7.3,.16,.32],'wood')
        for xx in [6.38,8.1,9.95,11.8,13.52]:block('workshop','factory-v3-wall-pier',[xx,yy,2.6],[.14,.18,4.0],'woodlight')
    for xx in [6.34,13.55]:
        block('workshop','factory-v3-facade-sill',[xx,-.65,.55],[.16,6.5,.7],'v3_brick')
        for yy in [-2.65,-.65,1.35]:
            block('workshop','factory-v3-rear-glazing',[13.60,yy,2.7],[.045,1.6,3.5],'glass')
        for yy in [-3.8,-1.7,.4,2.5]:block('workshop','factory-v3-rear-column',[13.52,yy,2.6],[.18,.15,4.9],'steel')
    block('workshop','factory-v3-closed-entry-glass',[6.265,-2.5,1.63],[.055,1.45,2.75],'glass_light')
    for yy in [-3.25,-2.5,-1.75]:block('workshop','factory-v3-entry-frame',[6.22,yy,1.62],[.10,.06,2.78],'steel')
    for yy in [-2.85,-2.15]:rod('workshop','factory-v3-entry-pull',[6.16,yy,1.2],[6.16,yy,1.85],.026,'woodlight')
    for yy in [-2.8,-.3,2.2]:
        block('workshop','factory-v3-interior-worktable',[9.5,yy,1.02],[2.6,1,.15],'woodlight')
        for xx in [8.4,10.6]:block('workshop','factory-v3-interior-table-leg',[xx,yy,.57],[.12,.75,.84],'steel')
    if detail==2:
        # First side/back renders exposed an unfinished band beneath the teeth.
        # Close each gable with genuinely framed clerestory glass, preserving
        # the three-sawtooth silhouette and all solar geometry.
        for i in range(3):
            xa=6.30+i*7.3/3;xb=6.30+(i+1)*7.3/3
            for yy in [-3.96,2.66]:
                v=np.array([[xa,yy-.024,4.90],[xb,yy-.024,4.90],[xb,yy-.024,5.35],[xa,yy-.024,7.05]])
                vv=np.concatenate((v,v+[0,.048,0]));faces=[[0,1,2],[0,2,3],[4,6,5],[4,7,6],[0,4,5],[0,5,1],[1,5,6],[1,6,2],[2,6,7],[2,7,3],[3,7,4],[3,4,0]]
                add(placed(trimesh.Trimesh(vertices=vv,faces=faces,process=False),'workshop'),'glass_light','factory-v3-framed-gable-glass','solid')
                rod('workshop','factory-v3-gable-sloping-frame',[xa,yy,7.05],[xb,yy,5.35],.045,'steel','roof')
                rod('workshop','factory-v3-gable-horizontal-frame',[xa,yy,4.94],[xb,yy,4.94],.045,'steel')
                for xx,h in [(xa,7.02),(xb,5.32)]:rod('workshop','factory-v3-gable-post',[xx,yy,4.94],[xx,yy,h],.044,'steel')
    # Youth centre is a complete closed two-height building, not a larger shed.
    for xx in [-12.55,-5.94]:
        block('youth','exhibition-v3-closed-wall-base',[xx,1.0,.48],[.18,5.7,.55],'v3_brick')
        block('youth','exhibition-v3-rear-band',[xx,1.0,4.25],[.18,5.7,.36],'wood')
        for yy in [-1.65,.2,2.0,3.8]:block('youth','exhibition-v3-timber-pier',[xx,yy,2.32],[.18,.18,4.15],'woodlight')
    for yy in [-1.75,3.82]:
        block('youth','exhibition-v3-side-sill',[-9.25,yy,.5],[6.65,.17,.60],'v3_brick')
        block('youth','exhibition-v3-side-head',[-9.25,yy,4.26],[6.65,.17,.32],'wood')
        for xx in [-12.5,-10.85,-9.2,-7.55,-5.95]:block('youth','exhibition-v3-side-pier',[xx,yy,2.3],[.17,.18,4.0],'woodlight')
        for xx in [-11.65,-10,-8.35,-6.7]:block('youth','exhibition-v3-rear-window',[xx,yy,2.5],[1.35,.045,2.9],'glass')
    for yy in [-.9,.9,2.7]:block('youth','exhibition-v3-west-window',[-12.62,yy,2.5],[.045,1.4,2.9],'glass')
    block('youth','exhibition-v3-interior-floor',[-9.25,1,.27],[6.5,5.5,.13],'stone_cream','floor')
    for yy in [.7,2.8]:
        block('youth','exhibition-v3-interior-display',[-10,yy,1.0],[1.6,.8,.7],'woodlight')
    if detail==2:
        # The reference's raised slab was hidden below its full roof plate.
        # A real 0.7-height step makes the intended second volume readable.
        block('youth','exhibition-v3-lower-roof',[-9.2,-.40,4.95],[7.3,3.20,.24],'roof','roof')
        block('youth','exhibition-v3-raised-roof',[-9.38,2.64,5.68],[5.5,2.90,.24],'roof','roof')
        for yy in [1.21,4.02]:
            block('youth','exhibition-v3-raised-clerestory',[-9.38,yy,5.26],[5.28,.055,.65],'glass')
            block('youth','exhibition-v3-raised-header',[-9.38,yy,5.59],[5.5,.10,.09],'woodlight')
            for xx in [-11.95,-10.2,-8.5,-6.8]:block('youth','exhibition-v3-clerestory-post',[xx,yy,5.27],[.08,.10,.65],'steel')
        for xx in[-12.08,-6.68]:block('youth','exhibition-v3-raised-side-wall',[xx,2.64,5.16],[.13,2.9,.88],'woodlight')
    # Complete arch end walls: closed glazing and a proper south entrance.
    for yy in [2.725,7.275]:
        for k in range(16):
            t0=math.pi*k/16;t1=math.pi*(k+1)/16
            x0=8.4+2.95*math.cos(t0);x1=8.4+2.95*math.cos(t1);h0=.4+3.5*math.sin(t0);h1=.4+3.5*math.sin(t1)
            v=[[x0,yy-.018,.30],[x1,yy-.018,.30],[x1,yy-.018,h1],[x0,yy-.018,h0]]
            # Extruded strip guarantees visible thickness and horizontal collision.
            vv=np.array(v);verts=np.concatenate((vv,vv+[0,.036,0]));faces=[[0,1,2],[0,2,3],[4,6,5],[4,7,6],[0,4,5],[0,5,1],[1,5,6],[1,6,2],[2,6,7],[2,7,3],[3,7,4],[3,4,0]]
            add(placed(trimesh.Trimesh(vertices=verts,faces=faces,process=False),'greenhouse'),'glass_light','greenhouse-v3-end-glass','solid')
    for xx in [7.72,9.08]:rod('greenhouse','greenhouse-v3-entry-post',[xx,7.31,.27],[xx,7.31,2.6],.045,'steel')
    rod('greenhouse','greenhouse-v3-entry-head',[7.72,7.31,2.6],[9.08,7.31,2.6],.045,'steel')
    block('greenhouse','greenhouse-v3-entry-glass',[8.4,7.325,1.43],[1.28,.04,2.24],'glass_light')
    for xx in [5.45,11.35]:block('greenhouse','greenhouse-v3-low-side-glass',[xx,5,.57],[.04,4.55,.66],'glass')
    if detail==2:
        for yy in np.linspace(2.725,7.275,7):
            for xx in[5.45,11.35]:block('greenhouse','greenhouse-v3-arch-foot',[xx,yy,.30],[.18,.19,.13],'steel')
        for xx in[6.98,9.82]:
            for yy in np.linspace(3.15,6.85,5):
                for dx,dz,s in [(-.17,0,.16),(.13,.07,.19),(0,-.1,.14)]:
                    p=cfg['greenhouse'];dxw,dzw=p['translationXZ'];a.sphere([xx+dx+dxw,.91,yy+dz+dzw],s,'plant_leaf'if s>.15 else'plant_yellow','greenhouse-v3-growing-leaf',1,scale=[1,.65,.7])
    # Three deliberate shared-lifecycle landscape areas, with no scattered props.
    for i,(x,z)in enumerate(cfg['treesXZ']):
        a.rod([x,-.1,z],[x,1.4,z],.13,'wood','v3-garden-trunk',8);roles['v3-garden-trunk']='solid'
        for dx,dy,dz,r,mat in [(0,1.9,0,.78,'plant_leaf'),(.38,2.2,.10,.56,'plant_yellow'),(-.3,1.85,.2,.58,'plant_bush')]:a.sphere([x+dx,dy,z+dz],r,mat,'v3-garden-canopy',1,scale=[1,.8,1])
        # Low circular stone edging anchors the tree without blocking route core.
        ring=Point(x,z).buffer(.75,resolution=16).difference(Point(x,z).buffer(.65,resolution=16));a.polygon(ring,-.1,.12,'stone_cream','v3-garden-tree-edge');roles['v3-garden-tree-edge']='floor'
    # One meaningful machinery exhibit and two seating groups outside the core.
    a.cyl([10.6,.12,-5.1],.75,.3,'stone_cream','v3-industry-exhibit-base',20,r0=1);roles['v3-industry-exhibit-base']='floor'
    a.cyl([10.6,.85,-5.1],.43,1.2,'steel','v3-industry-rotor',12,r0=1);roles['v3-industry-rotor']='solid'
    for t in np.linspace(0,2*math.pi,8,endpoint=False):a.rod([10.6,1.1,-5.1],[10.6+.64*math.cos(t),1.1,-5.1+.64*math.sin(t)],.055,'v3_copper','v3-industry-spoke',8)
    for x,z in [(-10.8,-3.0),(-1.9,11)]:
        a.box([x,.38,z],[1.5,.16,.45],'woodlight','v3-garden-bench');roles['v3-garden-bench']='solid'
        for dx in[-.55,.55]:a.box([x+dx,.12,z],[.09,.4,.38],'steel','v3-garden-bench-leg')
    # Ground approach only: no change to original roads or circular plaza.
    for points in [[(3.0,8.4),(3,9.4),(5.4,9.8),(6.0,9.8)],[(-3,0),(-4.6,-.55)],[(3.1,-1),(4.4,-1.2)]]:
        a.polygon(LineString(points).buffer(.65,cap_style=2,join_style=1).intersection(base['foot'].buffer(-.15)),-.1,.025,'path','v3-local-approach');roles['v3-local-approach']='floor'
    base['collisionRoles']=roles;base['description']='C V3 architectural refinement on unchanged PR17 ground; semantic proxies at 1e-5'
    return base,a.parts,cfg

def main():
    g,parts,cfg=author();prepare_c.build((g,parts),preserve_site=True)
    p=ROOT/'docs/design/industry-youth-island-c-v3';p.mkdir(exist_ok=True)
    # Audit actual placed component hulls, with overhead and standing-body bands separate.
    foot=g['foot'];core=g['core'];npc=box(-1,6.85,2,9.85);groups={};issues=[]
    for mesh,mat,name in parts:
        role=g['collisionRoles'].get(name);v=mesh.vertices;h=MultiPoint(v[:,[0,2]]).convex_hull
        if h.geom_type!='Polygon':continue
        group='workshop'if name.startswith('factory-v3')else'youth'if name.startswith('exhibition-v3')else'greenhouse'if name.startswith('greenhouse-v3')else'site'
        if group!='site':groups.setdefault(group,[]).append(v)
        if role in ['solid','floor','roof']:
            outside=h.difference(foot).area;over=h.intersection(core).area if role=='solid'and mesh.bounds[0,1]<1.6 else 0;npcover=h.intersection(npc).area if role=='solid'else 0
            if outside>.0001 or over>.0001 or npcover>.0001:issues.append({'part':name,'outsideArea':outside,'bodyCoreArea':over,'NPCOverlap':npcover})
    report={'baseCommit':'0c7cab7','proxyLandImported':False,'axisNote':cfg['sourceAxisMapping'],'placement':cfg,'bounds':{},'issues':issues,'editableParts':len(parts)}
    for name,vs in groups.items():
        v=np.concatenate(vs);report['bounds'][name]={'min':v.min(axis=0).tolist(),'max':v.max(axis=0).tolist(),'dimensions':np.ptp(v,axis=0).tolist()}
    (p/'placed-geometry-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('V3 placed geometry:',len(parts),'parts;',len(issues),'issues (report file)')
    if issues:raise SystemExit(1)

if __name__=='__main__':main()
