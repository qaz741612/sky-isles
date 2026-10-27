"""Read-only independent saved-BLEND geometry, contacts and camera projections. MIT."""
import bpy,bmesh,sys,os,json,hashlib,math
import numpy as np
from pathlib import Path
from shapely.geometry import MultiPoint,box
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/design/transport-elevated-station-v9-prototype';source=OUT/'transport-station-v9.blend';sha=lambda:hashlib.sha256(source.read_bytes()).hexdigest();before=sha();bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update();root=bpy.data.objects['YuanliElevatedStationV9'];deps=bpy.context.evaluated_depsgraph_get();pts=[];issues=[];tris=0;objects=0;parts={};npc=[box(x-1.5,2.43,x+1.5,5.43)for x in [-3.7,3.65]];hits=[[],[]];wheel=[];rail=[]
for o in root.children_recursive:
 if o.type!='MESH':continue
 objects+=1;e=o.evaluated_get(deps);me=e.to_mesh();me.calc_loop_triangles();tris+=len(me.loop_triangles);bm=bmesh.new();bm.from_mesh(me);bad=sum(not ed.is_manifold for ed in bm.edges);vol=bm.calc_volume(signed=True);bm.free()
 if bad or vol<=0:issues.append({'name':o.name,'nonManifoldEdges':bad,'signedVolume':vol})
 world=[o.matrix_world@v.co for v in me.vertices];ys=[v.z for v in world];low=min(ys);high=max(ys)
 if low<1.5 and high>.22:
  lowPoints=[(v.x,-v.y)for v in world if v.z<=1.5]
  p=MultiPoint(lowPoints).convex_hull
  if p.geom_type=='Polygon':
   for i,n in enumerate(npc):
    if n.intersection(p).area>1e-5:hits[i].append(o.name)
 if o.name.startswith('RailContactWheel'):wheel.append(low)
 if o.name.startswith('RailPolishedHead'):rail.append(high)
 for name in ['Hall','TrainRollingStock','Canopy','VerticalCirculation','Viaduct']:
  p=o
  while p.parent and p.parent!=root:p=p.parent
  if p.name==name:parts.setdefault(name,[]).extend((v.x,v.z,-v.y)for v in world)
 pts.extend((v.x,v.y,v.z,1)for v in world);e.to_mesh_clear()
assert not issues,issues;assert not any(hits),hits;assert len(wheel)==8 and len(rail)==2;contact=max(abs(v-max(rail))for v in wheel);assert contact<.003,contact
positions=np.array(pts,dtype=float).T;cameraResults=[]
for name,w,h in [('hero',1440,1080),('front',1200,900),('back',1200,900),('left',1200,900),('right',1200,900),('top',1440,1080),('train-side',1440,1080),('player-desktop',1440,900),('player-mobile',720,1280)]:
 cam=bpy.data.objects[name];bpy.context.scene.render.resolution_x=w;bpy.context.scene.render.resolution_y=h;proj=np.array(cam.calc_matrix_camera(deps,x=w,y=h,scale_x=1,scale_y=1))@np.array(cam.matrix_world.inverted());p=proj@positions;xy=p[:2]/p[3];ndcMin=xy.min(axis=1).tolist();ndcMax=xy.max(axis=1).tolist();fits=max(abs(n)for n in [*ndcMin,*ndcMax])<=1;partFits={}
 for role,pp in parts.items():
  aa=np.array([(v[0],-v[2],v[1],1)for v in pp]).T;cc=proj@aa;xyPart=cc[:2]/cc[3];partFits[role]=bool(np.max(np.abs(xyPart))<=1)
 cameraResults.append({'name':name,'viewport':[w,h],'projection':cam.data.type,'wholeAssetInFrame':bool(fits),'actualPartsWithinFrame':partFits,'minNDC':ndcMin,'maxNDC':ndcMax,'simulationOnly':bool(cam.get('simulationOnly',False))})
 if name in ['hero','front','back','left','right','top']:assert fits,(name,ndcMin,ndcMax)
# Packed original wood image is self-contained. Nothing depends on the user reference PNG as a texture.
images=[{'name':im.name,'packed':bool(im.packed_file),'size':list(im.size)}for im in bpy.data.images if im.type=='IMAGE'and im.name!='Render Result'];assert all(i['packed']for i in images)
bounds={}
for name,points in parts.items():a=np.array(points);bounds[name]={'minWorldXYZ':a.min(axis=0).tolist(),'maxWorldXYZ':a.max(axis=0).tolist(),'sizeWorldXYZ':(a.max(axis=0)-a.min(axis=0)).tolist()}
r={'sourceBlendSHA256':before,'sourceUnchangedAfterInspection':sha()==before,'allClosedPositiveVolume':True,'meshObjectsChecked':objects,'evaluatedTriangles':tris,'issues':issues,'actualLowGeometryNPCIntrusions':hits,'wheelRail':{'wheelBottomWorldY':wheel,'railHeadWorldY':rail,'maximumMismatch':contact},'componentBounds':bounds,'packedImages':images,'cameras':cameraResults,'scope':'Offline geometry/contact/framing only. Strict player cameras are simulations of original spawn plus target offset 1.5; not actual gameplay. A crop in strict player view is reported, never hidden by changing required parameters.'};(OUT/'source-audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'sourceSHA256':before,'objects':objects,'triangles':tris,'closed':True,'NPCclear':True,'wheelRailMismatch':contact,'cameraFits':{r['name']:r['wholeAssetInFrame']for r in cameraResults}},ensure_ascii=False),flush=True);sys.stdout.flush();os._exit(0)
