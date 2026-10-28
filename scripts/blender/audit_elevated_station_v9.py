"""Independent offline polygon/route/footprint validation from saved prototype data. MIT."""
from pathlib import Path
from collections import deque
import json,hashlib,math,subprocess
import numpy as np
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import unary_union
from shapely.prepared import prep
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/design/transport-elevated-station-v9-prototype';m=json.loads((OUT/'model-report.json').read_text());shells=json.loads((OUT/'collision-shells.json').read_text())['shells'];plan=json.loads((ROOT/'src/data/yuan-plan.json').read_text());site=Polygon(m['sitePolygonXZ']);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(OUT/'transport-station-v9.blend')==m['blendSHA256'];assert not m['geometryAuditIssues']
# Recognize either the approved model base or current PR14; road/centre geometry is identical.
baseApproved='ac433fd5d23f00d3aab9470d96349114e1a37b24';basePR14='81f7408468bcce2f7452b13e0a9d7ea1d4be62a1';planSHA=sha(ROOT/'src/data/yuan-plan.json');base=next((ref for ref in [basePR14,baseApproved]if hashlib.sha256(subprocess.check_output(['git','show',ref+':src/data/yuan-plan.json'],cwd=ROOT)).hexdigest()==planSHA),None);assert base,'Unrecognized world plan; re-audit before continuing';buildPlan=json.loads(subprocess.check_output(['git','show',baseApproved+':src/data/yuan-plan.json'],cwd=ROOT));assert plan['edges']==buildPlan['edges'];assert [(n['id'],n['x'],n['y'],n['z'])for n in plan['nodes']]==[(n['id'],n['x'],n['y'],n['z'])for n in buildPlan['nodes']];assert m['worldPlanSHA256']==hashlib.sha256(subprocess.check_output(['git','show',baseApproved+':src/data/yuan-plan.json'],cwd=ROOT)).hexdigest()
def line(e):
 c=e['controlPointsXZ']
 if len(c)==2:return LineString(c)
 return LineString([tuple((1-t)**3*c[0][a]+3*(1-t)**2*t*c[1][a]+3*(1-t)*t*t*c[2][a]+t**3*c[3][a]for a in [0,1])for t in np.linspace(0,1,801)])
lines={e['id']:line(e)for e in plan['edges']};ground=[r for r in shells if r['bottom']<1.5 and r['top']>.22 and r['role']not in ['walkable']];obstacle=unary_union([Polygon(r['polygonXZ'])for r in ground]);npc=[]
for bounds in m['NPCReservedSquaresXZ']:
 p=box(*bounds);hits=[r['id']for r in ground if Polygon(r['polygonXZ']).intersection(p).area>1e-6];npc.append({'squareXZ':bounds,'intersectingGroundShells':hits,'passed':not hits});assert not hits,hits
spine=unary_union([lines[k].buffer(2.4,cap_style=2)for k in ['S09','S10']]).intersection(site);spineHits=[{'id':r['id'],'area':Polygon(r['polygonXZ']).intersection(spine).area}for r in ground if Polygon(r['polygonXZ']).intersection(spine).area>1e-5];assert not spineHits,spineHits
# Conservative player-radius erosion and full-width real centreline openings; four-neighbour grid avoids corner cutting.
safe=site.buffer(-.33).difference(obstacle.buffer(.33));pr=prep(safe);res=.12;xs=np.arange(site.bounds[0],site.bounds[2]+res,res);zs=np.arange(site.bounds[1],site.bounds[3]+res,res);mask=np.array([[pr.contains(Point(float(x),float(z)))for x in xs]for z in zs],dtype=bool)
nav={'mobile_observation_walkway':(0,7.5),'spawn':(0,3.5),'lobby':(0,-2.45),'west_stair_public_approach_before_step':(-7.8,-2.4),'east_lift_approach':(7.7,-2.8),'NPC_west':(-3.7,3.93),'NPC_east':(3.65,3.93),'NPC_west_stop':(-3.7,2.75),'NPC_east_stop':(3.65,2.75),'west_rest':(-4.7,4.10),'east_rest':(4.7,4.10)};ports=[]
for key in ['S09','S10','S15','S18']:
 points=lines[key].intersection(site.boundary);pts=[points]if points.geom_type=='Point'else list(points.geoms);assert pts,key;p=min(pts,key=lambda p:p.distance(Point(0,0)));nav[key]=(p.x*.88,p.y*.88);ports.append({'id':key,'centrelineWorldXZ':[p.x,p.y],'width':4.8,'fenceInMouthArea':unary_union([Polygon(r['polygonXZ'])for r in ground if r['kind']=='guard']).intersection(lines[key].buffer(2.4).intersection(site)).area})
def ix(p):return(int(np.argmin(abs(zs-p[1]))),int(np.argmin(abs(xs-p[0]))))
start=ix(nav['spawn']);seen={start};q=deque([start]);assert mask[start]
while q:
 y,x=q.popleft()
 for yy,xx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
  if 0<=yy<len(zs)and 0<=xx<len(xs)and mask[yy,xx]and(yy,xx)not in seen:seen.add((yy,xx));q.append((yy,xx))
checks=[{'target':k,'pointXZ':list(v),'reachable':ix(v)in seen}for k,v in nav.items()];failed=[r for r in checks if not r['reachable']];assert not failed,failed
foreign={k:site.intersection(v.buffer(2.4,cap_style=2)).area for k,v in lines.items()if k not in ['S09','S10','S15','S18']};overlaps={k:v for k,v in foreign.items()if v>1e-4};assert not overlaps,overlaps
family=next(n for n in plan['nodes']if n['id']=='A');familyOverlap=site.intersection(Point(family['x'],family['z']).buffer(max(10.2,family['r']))).area;assert familyOverlap<1e-4
protected=[]
for file in ['src/data/yuan-plan.json','docs/design/parent-child-blender-refinement-v2/parent-child-centre.blend','docs/design/parent-child-blender-refinement-v2/parent-child-centre.glb']:
 old=subprocess.check_output(['git','show',base+':'+file]);assert hashlib.sha256(old).hexdigest()==sha(ROOT/file);protected.append({'path':file,'sha256':sha(ROOT/file),'unchanged':True})
changed=subprocess.check_output(['git','diff',base,'--name-only','--','src','public','package.json','package-lock.json'],cwd=ROOT,text=True).strip();assert not changed
r={'allOfflineChecksPassed':True,'protectedBaselineCommit':base,'currentWorldPlanSHA256':planSHA,'geometryBuildWorldPlanSHA256':m['worldPlanSHA256'],'allRoadControlsAndIslandCentersMatch':True,'sourceBlendSHA256':m['blendSHA256'],'siteArea':site.area,'referenceSiteArea':m['referenceSiteArea'],'gardenTerraceProposalAddedArea':m['localGardenTerraceProposalAddedArea'],'siteBoundsXZ':list(site.bounds),'NPCSquares':npc,'fullWidthEastWestSpineIntersections':spineHits,'groundNavigation':{'method':'0.12 four-neighbour grid on actual proposed site minus shell polygons expanded by 0.33 player radius. Offline 2D feasibility, not runtime physics.','targets':checks,'connectedCells':len(seen)},'fourUnchangedBridgePorts':ports,'foreignRoadOverlapAreas':foreign,'familyOverlapArea':familyOverlap,'sourcePreservation':protected,'gameSourceChanged':False,'knownLimits':['Two-dimensional navigation does not certify actual capsule collision, jumping, head clearance, stair stepping, elevator operation or game camera occlusion.','Upper stair flight/landing/bridge geometry exists; vertical traversal needs game integration.','Static train not boardable; no NPC model or dialogue system.','Terrace proposal is in standalone model only, never written into the approved world layout.']};(OUT/'geometry-space-audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'groundTargets':len(checks),'allReachable':True,'NPCSquaresClear':2,'foreignRoadOverlaps':overlaps,'familyOverlap':familyOverlap,'proposedAreaAdded':r['gardenTerraceProposalAddedArea']},ensure_ascii=False))
