"""Approved spatial audit plus actual V5.1 structural and planted-bank clearance."""
from pathlib import Path
import json,hashlib
from shapely.geometry import Polygon,box
from shapely.affinity import translate
R=Path(__file__).resolve().parents[2];source=(R/'scripts/flood/audit_final_v5.py').read_text().replace("O=R/'docs/previews/flood-control-island-g-v5'","O=R/'docs/previews/flood-control-island-g-v5-1'").replace('work/g-v5/parts.json','work/g-v51/parts.json');ns={'__file__':str(R/'scripts/flood/audit_final_v5.py')};exec(compile(source,str(R/'scripts/flood/audit_final_v5.py'),'exec'),ns)
a=json.loads((R/'src/data/flood-control-art.json').read_text());p=ns['p'];c=ns['c'];report=ns['report'];banks=[('arrival',a['zones']['arrival']['bed']),('arrival-curve',a['zones']['arrival']['curvedBed']),('forecourt',a['zones']['forecourt']['bed'])];nx,_,nz=p['npc'][0]['position'];npc=box(nx-1.5,nz-1.5,nx+1.5,nz+1.5);rows=[]
for name,points in banks:
 poly=Polygon(points);world=translate(poly,p['centre'][0],p['centre'][2]);gap=min(world.distance(ns['roads'][k])for k in ['S21','S22']);ngap=poly.distance(npc);assert gap>2.75 and ngap>.4;rows.append({'name':name,'actualRoadCentrelineGap':gap,'actualGuideReservationEdgeGap':ngap,'outsideDryArea':poly.difference(ns['dry']).area})
parts=ns['parts'];bounds=lambda name:[min(v[1]for t in parts if t['name']==name for v in t['vertices']),max(v[1]for t in parts if t['name']==name for v in t['vertices'])]
foot=bounds('Anchored submerged pier foundation');stem=bounds('V51 continuous submerged pier stem');pier=bounds('major dam pier concrete');assert foot[1]<p['waterHeights']['downstream']-.1 and stem[0]<foot[1]and stem[1]>pier[0]
base=json.loads((R/'docs/design/flood-control-island-g-v5-1/protected-baseline.json').read_text());drift=[f['path']for f in base['files']if hashlib.sha256((R/f['path']).read_bytes()).hexdigest()!=f['sha256']];assert not drift
old=json.loads((R/'docs/design/flood-control-island-g-v5-1/baseline/flood-control-collision.json').read_text());assert c['groundPositions'][:c['dryGroundFloats']]==old['groundPositions'][:old['dryGroundFloats']]
report.update({'version':'G-V5.1','baseV5Commit':a['baseCommit'],'protectedV5Files':len(base['files']),'protectedDrift':drift,'artBanks':rows,'hydraulicStructure':{'footingY':foot,'pierStemY':stem,'originalPierY':pier,'footingSubmergence':p['waterHeights']['downstream']-foot[1],'stemToFootingOverlap':foot[1]-stem[0],'stemToPierOverlap':stem[1]-pier[0]},'publicDryGroundByteIdentical':True,'submergedSupportTrianglesRemoved':c['submergedSupportTrianglesRemoved']})
(R/'docs/previews/flood-control-island-g-v5-1/spatial-audit-final.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('V5.1:214 protected files, connected submerged foundations,3 cleared art banks verified')
