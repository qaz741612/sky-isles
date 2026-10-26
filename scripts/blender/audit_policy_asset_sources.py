"""Final readonly closed-solid/volume/material audit of all seven saved BLEND files. MIT."""
import bpy,bmesh,json,hashlib,sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/design/seven-policy-islands-blender-v1';ids=['transport','senior','industry','environment','digital','water','education'];summary=[]
for key in ids:
 source=OUT/key/(key+'.blend');sha=hashlib.sha256(source.read_bytes()).hexdigest();report=json.loads((OUT/key/'model-report.json').read_text());assert sha==report['blendSHA256'];bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update();root=bpy.data.objects[key+'_MODEL'];deps=bpy.context.evaluated_depsgraph_get();issues=[];tris=0;objects=0;wheel_bottom=[];rail_top=[]
 for o in root.children_recursive:
  if o.type!='MESH':continue
  objects+=1;e=o.evaluated_get(deps);me=e.to_mesh();me.calc_loop_triangles();tris+=len(me.loop_triangles);bm=bmesh.new();bm.from_mesh(me);opened=sum(not ed.is_manifold for ed in bm.edges);vol=bm.calc_volume(signed=True);bm.free()
  if opened or vol<=0:issues.append({'name':o.name,'nonManifoldEdges':opened,'signedVolume':vol})
  if o.name.startswith('TrainWheel'):wheel_bottom.append(min((o.matrix_world@v.co).z for v in me.vertices))
  if o.name.startswith('SteelDisplayRail'):rail_top.append(max((o.matrix_world@v.co).z for v in me.vertices))
  e.to_mesh_clear()
 assert not issues,(key,issues[:5]);assert tris==report['evaluatedTriangles'];assert tris<=381520
 images=[im.filepath for im in bpy.data.images if im.source=='FILE'and im.filepath];assert not images
 actual={'id':key,'sourceBlendSHA256':sha,'checkedObjects':objects,'evaluatedTriangles':tris,'nonClosedOrNegativeVolumeIssues':issues,'externalImageDependencies':images,'passed':True}
 if key=='transport':
  assert len(wheel_bottom)==8 and len(rail_top)==2
  err=max(abs(z-max(rail_top))for z in wheel_bottom);assert err<.005
  actual['wheelRailContact']={'wheelBottomZ':wheel_bottom,'railTopZ':rail_top,'maximumVerticalMismatch':err,'gauge':1.1,'passed':True}
 assert hashlib.sha256(source.read_bytes()).hexdigest()==sha;(OUT/key/'source-audit.json').write_text(json.dumps(actual,indent=2)+'\n');summary.append(actual);print('SOURCE_AUDIT_PASS',key,tris,flush=True)
(OUT/'source-audit-summary.json').write_text(json.dumps({'allPassed':True,'assets':summary},indent=2)+'\n');sys.stdout.flush();os._exit(0)
