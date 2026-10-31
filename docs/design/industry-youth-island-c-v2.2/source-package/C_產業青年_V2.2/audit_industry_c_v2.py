"""Static C island site check. NOT an in-game collision test."""
import os,json,hashlib
import numpy as np
import trimesh
from shapely.geometry import Polygon,Point
from build_industry_c_v2 import scene,core,foot,ports,road_centerlines
OUT=os.path.dirname(os.path.abspath(__file__))
# fixed site structures by actual Blender-style mesh bounding polygons
features={
 'workshop_podium':['factory-limestone-podium'],
 'workshop_envelope':['factory-masonry-shell','sawtooth-zinc-roof-0','sawtooth-zinc-roof-1','sawtooth-zinc-roof-2'],
 'greenhouse':['greenhouse-foundation'],
 'exhibition_pavilion':['exhibit-stage'],
}
records={};fatal=[]
for tag,names in features.items():
 meshes=[m for m,_,n in scene.parts if n in names]
 assert meshes,(tag,names)
 bbox=np.array([m.bounds for m in meshes]);low=bbox[:,0,:].min(axis=0);high=bbox[:,1,:].max(axis=0)
 rect=Polygon([(low[0],low[2]),(high[0],low[2]),(high[0],high[2]),(low[0],high[2])])
 road_area=rect.intersection(core).area;land_area=rect.difference(foot).area
 records[tag]={'bboxXYZ':[[round(float(x),3) for x in low],[round(float(x),3) for x in high]],'roadCoreOverlapArea':round(road_area,5),'outsideIslandArea':round(land_area,5)}
 if tag in ['workshop_podium','workshop_envelope','greenhouse','exhibition_pavilion']:
  if road_area>.01 or land_area>.01:fatal.append(tag)
npc=Polygon([(-1,6.85),(2,6.85),(2,9.85),(-1,9.85)])
npc_issue=[];road_block=[]
block_names={'tree-trunk','factory-post-west','greenhouse-corner-frame','exhibit-wood-columns','courtyard-low-bollard','maker-portal-frame','bench-leg','outdoor-makers-table'}
for m,_,n in scene.parts:
 if n not in block_names and not n.startswith('canopy-leaf'):continue
 lo,hi=m.bounds;box=Polygon([(lo[0],lo[2]),(hi[0],lo[2]),(hi[0],hi[2]),(lo[0],hi[2])])
 if box.intersects(npc):npc_issue.append(n)
 if n in block_names and box.intersection(core).area>.001:road_block.append(n)
if npc_issue:fatal.append('NPC')
if road_block:fatal.append('blocking_props')
# Existing jump pad remains the only playable object, not cloned into the delivered model
mushroom=Point(3.0560736586,3.4380828659).buffer(.95)
if mushroom.intersection(core).area>.001:fatal.append('mushroom_vs_route')
# old bridge lamp positions (from PR#15) near C; optional scenic relocation after runtime audit
lampWorld={'S14-L2':(-28.9762325682,25.5702987697),'S15-L2':(-8.3850345106,28.0633628244),'S16-L1':(-31.3493630045,49.9246219844)}
lamps={k:{'localXZ':[round(x+20.358,3),round(z-38.61,3)],'insideNewIsland':foot.covers(Point(x+20.358,z-38.61))} for k,(x,z) in lampWorld.items()}
tri_counts={}
for f in ['C_IndustryYouth_V2_DesignReference.glb','C_IndustryYouth_V2_RuntimeAssetCandidate.glb']:
 p=os.path.join(OUT,f);glb=trimesh.load(p,force='scene',process=False)
 tri_counts[f]={'geometryBatches':len(glb.geometry),'triangles':int(sum(len(m.faces) for m in glb.geometry.values())),'bytes':os.path.getsize(p),'sha256':hashlib.sha256(open(p,'rb').read()).hexdigest()}
report={
 'status':'STATIC_LAYOUT_CHECK_PASSED' if not fatal else 'STATIC_LAYOUT_CHECK_FAILED',
 'notRuntimeVerification':True,
 'worldCentreXYZ':[-20.358,0,38.61],
 'siteBoundsLocalXZ':[round(float(foot.bounds[0]),3),round(float(foot.bounds[1]),3),round(float(foot.bounds[2]),3),round(float(foot.bounds[3]),3)],
 'siteArea':round(float(foot.area),3),
 'approvedRouteIds':list(road_centerlines),
 'roadsSource':'PR#15 cubic Bezier controls, sampled 641 steps on each, buffered 4.8 units',
 'NPCReservationLocalXZ':{'center':[0.5,8.35],'rect':[-1,6.85,2,9.85],'existingNPCOriginal':[1,4.8]},
 'npcSolidIntersections':npc_issue,
 'blockingSolidIntersections':road_block,
 'mushroomRetained':{'localXZ':[3.0560736586,3.4380828659],'duplicateMeshIncluded':False},
 'buildingFootprints':records,
 'nearbyExistingLamps':lamps,
 'assets':tri_counts,
 'failures':fatal,
 'limitations':['No Blender .blend generated in this environment; GLB import and editable Python source provided.', 'No Sky Isles game runtime or Playwright test was run.', 'Runtime candidate excludes visual bridge stubs and perimeter rail for correct collision regeneration.', 'Static XY tests are not game collision tests.'],
}
with open(os.path.join(OUT,'C_IndustryYouth_V2_StaticAudit.json'),'w',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print('STATUS',report['status'],'FATAL',fatal)
print('asset counts',[(a,x['triangles']) for a,x in tri_counts.items()]);print('footprints',records)
assert not fatal,'fix geometry before delivery'
