"""MIT. Incremental edits to the approved final R21 .blend, never a rebuild
from R18/R20/research primitives. Architecture, terrain and scale stay locked.
"""
import bpy,bmesh,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent));from flood_export import export_batched
D=R/'docs/design/bdeh-r21';O=R/'docs/previews/bdeh-r21/final-qa';W=R/'work/r21-final-qa';W.mkdir(exist_ok=True)
finalQA=json.loads((R/'src/data/bdeh-final-qa.json').read_text())
codes=[sys.argv[sys.argv.index('--code')+1]]if'--code'in sys.argv else list('BDEH')
for code in codes:
 source=D/f'final-qa-baseline/docs/design/bdeh-r21/{code}/{code}-r21.blend';baseline=json.loads((D/f'final-qa-baseline/docs/design/bdeh-r21/{code}/model-report.json').read_text());assert hashlib.sha256(source.read_bytes()).hexdigest()==baseline['sourceBlendSHA256']
 bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;root=bpy.data.objects[f'R21_{code}_MODEL'];bpy.context.preferences.filepaths.save_version=0
 original=[o for o in root.children_recursive if o.type=='MESH'];groups={o.name.removeprefix('ROLE_'):o for o in root.children};added=[];edited=[];removed=[];counter=0
 def material(name,hexcolor):
  col=[int(hexcolor[i:i+2],16)/255 for i in[0,2,4]];col=[v/12.92 if v<=.04045 else((v+.055)/1.055)**2.4 for v in col]
  m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.78;return m
 if code=='E':material('FinalNativeSage','80996B');material('FinalNativeFlower','D6AF98');material('FinalWaterRipple','91BCB5')
 def mesh(name,vertices,faces,mat,role='landscape',physical=False):
  global counter
  counter+=1;me=bpy.data.meshes.new('FinalQA_'+name);me.from_pydata([(x,-z,y)for x,y,z in vertices],[],faces);me.materials.append(bpy.data.materials[mat]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();o=bpy.data.objects.new(f'FinalQA_{counter:03d}_{name}',me);scene.collection.objects.link(o);o.parent=groups[role];o['sourceComponent']='FinalQA_'+name;o['semanticRole']=role;o['physical']=physical;o['refinementBase']='39f41940fd3af0f432b477ebd36ad5b677a71db1';added.append(o);return o
 def box(name,x,y,z,w,h,d,mat,physical=True):
  v=[(x+dx*w/2,y+dy*h/2,z+dz*d/2)for dx,dy,dz in[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
  return mesh(name,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5)],mat,physical=physical)
 def stem(name,a,b,radius,mat,sides=5,physical=False):
  a,b=Vector(a),Vector(b);axis=(b-a).normalized();v=axis.cross(Vector((0,1,0)))
  if v.length<.01:v=axis.cross(Vector((1,0,0)))
  v.normalize();u=axis.cross(v);verts=[]
  for p in[a,b]:verts +=[tuple(p+radius*(math.cos(t*math.tau/sides)*u+math.sin(t*math.tau/sides)*v))for t in range(sides)]
  faces=[tuple(range(sides-1,-1,-1)),tuple(range(sides,sides*2))]+[(i,(i+1)%sides,(i+1)%sides+sides,i+sides)for i in range(sides)]
  return mesh(name,verts,faces,mat,physical=physical)
 def band(name,cx,cz,rx,rz,width,bottom,top,start,end,mat,physical=False,segments=24):
  verts=[]
  for i in range(segments+1):
   t=math.radians(start+(end-start)*i/segments)
   for inner,y in[(0,bottom),(1,bottom),(1,top),(0,top)]:verts.append((cx+(rx-inner*width)*math.cos(t),y,cz+(rz-inner*width)*math.sin(t)))
  faces=[]
  for i in range(segments):
   for j in range(4):faces.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
  faces +=[(0,1,2,3),(4*segments+3,4*segments+2,4*segments+1,4*segments)]
  return mesh(name,verts,faces,mat,physical=physical)
 def leaf(name,x,y,z,height,width,theta,mat):
  # E uses closed biconvex, blunt-ended broad leaves. Low, overlapping
  # perennial cover replaces the previous pointed lanceolate sprays; no balls,
  # billboard cards, transparency or added tree canopies.
  if code=='E':
   dx,dz=math.cos(theta),math.sin(theta);v=[]
   for along,side in[(0,.38),(.5,1),(1,.38),(1,-.38),(.5,-1),(0,-.38)]:
    lift=height*(.04+.25*along+.05*math.sin(along*math.pi));v.append((x+dx*height*.82*along-dz*width*side,y+lift,z+dz*height*.82*along+dx*width*side))
   v +=[(x+dx*height*.41,y+height*.35,z+dz*height*.41),(x+dx*height*.41,y+height*.16,z+dz*height*.41)]
   return mesh(name,v,[(i,(i+1)%6,6)for i in range(6)]+[((i+1)%6,i,7)for i in range(6)],mat)
  dx,dz=math.cos(theta),math.sin(theta);lx,lz=-dz*width,dx*width
  v=[(x,y,z),(x+dx*height*.44+lx,y+height*.35,z+dz*height*.44+lz),(x+dx*height*.86,y+height*.78,z+dz*height*.86),(x+dx*height*.44-lx,y+height*.35,z+dz*height*.44-lz),(x+dx*height*.4,y+height*.22-.018,z+dz*height*.4)]
  return mesh(name,v,[(0,1,2),(0,2,3),(0,4,1),(1,4,2),(2,4,3),(3,4,0)],mat)
 def clump(name,x,y,z,size,kind,phase=0):
  if kind=='low':
   for i in range(7):leaf(name,x,y,z,size,.30*size,phase+i*math.tau/7,'FinalNativeSage'if code=='E'else'careGarden')
  elif kind=='fern':
   for i in range(5):
    angle=phase+i*2.4;stem(name+'Petiole',(x,y,z),(x+.10*math.cos(angle),y+size*.65,z+.10*math.sin(angle)),.012,'ecoDeep')
    for side in[-1,1]:leaf(name+'Pinna',x,y+size*.28,z,size*.65,.25*size,angle+side*.6,'ecoLeaf')
  else:
   for i in range(3):
    angle=phase+i*2.1;xx=x+.20*math.cos(angle);zz=z+.20*math.sin(angle);flowerHeight=size*(.65 if code=='E'else 1);stem(name+'Stem',(xx,y,zz),(xx,y+flowerHeight,zz),.012,'ecoDeep'if code=='E'else'careGarden')
    leaf(name+'Basal',xx,y+.06,zz,size*.55,.10*size,angle,'FinalNativeSage'if code=='E'else'careGarden')
    for j in range(4):leaf(name+'Blossom',xx,y+flowerHeight-.03,zz,.10,.045 if code=='E'else .025,angle+j*math.pi/2,'FinalNativeFlower'if code=='E'else'flower')
 def local_top(objects,x,z):
  best=None
  for ob in objects:
   inv=ob.matrix_world.inverted();start=inv@Vector((x,-z,20));direction=inv.to_3x3()@Vector((0,0,-1));hit,p,normal,face=ob.ray_cast(start,direction)
   if hit:
    y=(ob.matrix_world@p).z
    if best is None or y>best:best=y
  assert best is not None,('No real source roof at planted point',x,z)
  return best
 if code=='B':
  for o in original:
   if o.get('sourceComponent')=='SensoryHerbRing':
    for v in o.data.vertices:v.co.x=-4.5+(v.co.x+3.95)*(4.2/5.3)
    o['finalQAEdited']=True;edited.append(o)
  # Two short companion seats outside the existing sensory herb bed. Preserve
  # all three old benches and the central tree; no added trees or spare pots.
  for start,end in[(-30,-5),(10,35)]:
   band('CompanionCourtSeat',-3.95,-3.9,3.13,3.13,.43,.62,.74,start,end,'warmwood',True,10)
   band('CompanionCourtBack',-3.95,-3.9,3.15,3.15,.09,.74,1.14,start,end,'copperdark',True,10)
   for t in[start+4,end-4]:
    a=math.radians(t);x=-3.95+2.92*math.cos(a);z=-3.9+2.92*math.sin(a);stem('CompanionCourtFoot',(x,.28,z),(x,.65,z),.055,'copperdark',physical=True)
  for i,t in enumerate([110,130,150,170,190,212,320,338]):
   a=math.radians(t);x=-4.5+1.65*math.cos(a);z=-3.9+1.92*math.sin(a);clump('SensoryHerbCommunity',x,.41,z,.31 if i%2 else .40,'flower'if i in[0,3,6]else'low',a)
 elif code=='D':
  # Mounted service icon, not an extra exhibition building or an invented policy.
  box('ServiceInformationBacking',4.45,2.55,1.86,.38,.52,.055,'civicSteel',False)
  box('ServiceInformationStem',4.45,2.52,1.821,.055,.20,.025,'civicLight',False)
  box('ServiceInformationDot',4.45,2.70,1.821,.065,.065,.025,'civicLight',False)
 elif code=='E':
  rg=finalQA['E']['rainGarden'];wx,wz=rg['centre'];sx=rg['dimensions'][0]/4.7;sz=rg['dimensions'][1]/2.0
  ribbon=[o for o in original if o.get('sourceComponent')=='BiophilicContinuousGreenRibbon'];assert len(ribbon)==1
  for o in original:
   name=o.get('sourceComponent','')
   if o.name in finalQA['E']['shadeTree']['parts']:
    tree=finalQA['E']['shadeTree'];o.location.x+=tree['to'][0]-tree['from'][0];o.location.y-=tree['to'][1]-tree['from'][1];o['physical']=name=='trees';edited.append(o)
   if name=='GreenSpineNativeLeafSpray':removed.append(name);bpy.data.objects.remove(o,do_unlink=True)
   if name in['RainGardenLivingWetlandBase','RainGardenLivingWetlandWater']:
    for v in o.data.vertices:
     x,z=v.co.x,-v.co.y;v.co.x=wx+(x+7.1)*sx;v.co.y=-(wz+(z+10.35)*sz)
    o['finalQAEdited']=True;edited.append(o)
   elif name in['RainGardenNativeReedStem','RainGardenNativeLeaf']:
    for v in o.data.vertices:v.co.x=wx+(v.co.x+7.1)*sx;v.co.y=-(wz+(-v.co.y+10.35)*sz)
    edited.append(o)
   elif name.startswith('PolicyCommonsAccessibleSeat')and sum(v.co.x for v in o.data.vertices)/len(o.data.vertices)>0:
    seat=finalQA['E']['watersideSeat']['centre'];o.location.x+=seat[0]-1.7;o.location.y-=seat[1]+8.7;o['physical']=True;edited.append(o)
  # Plant communities follow the actual continuous structural ribbon, whose
  # geometry stays intact. Height changes and open gaps reveal timber edges.
  anchors=finalQA['E']['roofCommunities']
  # A shallow, continuous timber-edged planting trough follows the real roof.
  # The approved structural ribbon is untouched; broad leaf communities replace
  # sparse narrow stars. Soil and plant heights provide three distinct layers.
  for edge in[-1,0,1]:
   vertices=[]
   for j in range(57):
    f=j/56*(len(anchors)-1);k=min(int(f),len(anchors)-2);t=f-k;a=Vector(anchors[k]);b=Vector(anchors[k+1]);v=a.lerp(b,t);tangent=(b-a).normalized();normal=Vector((-tangent.y,tangent.x));offset=.48+edge*.43
    width=.045 if edge else .82
    for side in[-1,1]:
     q=v+normal*(offset+side*width/2);y=local_top(ribbon,q.x,q.y)+(.15 if edge else .065);vertices.append((q.x,y,q.y))
   faces=[(2*k,2*k+1,2*k+3,2*k+2)for k in range(56)]
   # Thin, closed fabricated edging/soil shell, not a new green platform.
   n=len(vertices);vertices +=[(x,y-(.15 if edge else .065),z)for x,y,z in vertices];faces +=[tuple(i+n for i in reversed(f))for f in faces[:]]
   for k in range(56):
    for side in[0,1]:faces.append((2*k+side,2*(k+1)+side,2*(k+1)+side+n,2*k+side+n))
   faces +=[(0,1,n+1,n),(n-2,n-1,2*n-1,2*n-2)]
   mesh('ContinuousRoofTimberPlanter'if edge else'RoofPlantingSoil',vertices,faces,'ecoWood'if edge else'earthbrown')
  for i,(x,z)in enumerate(anchors):
   tangent=(Vector(anchors[min(i+1,len(anchors)-1)])-Vector(anchors[max(0,i-1)])).normalized();normal=Vector((-tangent.y,tangent.x));centre=Vector((x,z))+normal*.48
   for k,(along,across,scale)in enumerate([(-.20,.08,.62),(.22,-.10,.46),(0,.18,.74)]):
    q=centre+tangent*along+normal*across;y=local_top(ribbon,q.x,q.y)+.07
    clump('RoofNativeCommunity',q.x,y,q.y,scale,['low','fern','flower'][(i+k)%3],i*.8+k)
   if i<len(anchors)-1:
    for t in[.33,.67]:
     q=Vector((x,z)).lerp(Vector(anchors[i+1]),t)+normal*.48;y=local_top(ribbon,q.x,q.y)+.07
     clump('RoofPerennialUnderstorey',q.x,y,q.y,.44 if i%2 else .51,'low',i*.9+t)
  rx,rz=rg['dimensions'][0]/2,rg['dimensions'][1]/2
  band('RainGardenStoneBank',wx,wz,rx+.05,rz+.05,.17,.15,.49,0,360,'stone2',True,40)
  for i,t in enumerate([30,70,110,150,190,235,280,320]):
   a=math.radians(t);x=wx+(rx+.13)*math.cos(a);z=wz+(rz+.13)*math.sin(a);clump('RainGardenBankCommunity',x,.15,z,.38 if i%2 else .60,'flower'if i%3==0 else'low',a)
  for i,t in enumerate([25,145,245]):band('ShallowWaterReadableRipple',wx,wz,.44+i*.22,.43+i*.2,.026,.371,.377,t,t+70,'FinalWaterRipple',False,16)
  box('RainGardenInterpretationPost',-3.45,.54,-10.12,.09,.91,.09,'ecoWood')
  box('RainGardenInterpretationDesk',-3.45,1.0,-10.12,.85,.07,.45,'ecoWood')
  box('RainGardenWaterSymbol',-3.45,1.042,-10.12,.30,.014,.25,'ecoWater',False)
 elif code=='H':
  # A small open-book wayfinding landmark at the forum edge; no new classroom.
  box('LearningForumBookStand',-10.6,.48,-5.4,.20,.80,.20,'eduAmber')
  top=[(x,1.03+(z+5.65)*.28-.035,z)for x,z in[(-10.72,-5.63),(-10.48,-5.63),(-10.48,-5.18),(-10.72,-5.18)]]
  verts=top+[(x,.86,z)for x,y,z in top]
  mesh('LearningForumSlopedLecternSupport',verts,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'eduAmber',physical=True)
  for side in[-1,1]:
   top=[(-10.6,1.03,-5.65),(-10.6+side*.36,1.12,-5.65),(-10.6+side*.36,1.26,-5.15),(-10.6,1.17,-5.15)]
   verts=top+[(x,y-.035,z)for x,y,z in top]
   mesh('LearningForumOpenBook',verts,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'eduCream')
   for z in[-5.52,-5.40,-5.28]:
    y=1.03+(z+5.65)*.28+.045
    box('LearningForumPageLine',-10.6+side*.19,y+.008,z,.22,.012,.018,'eduBlue',False)
  box('LearningForumBookBase',-10.6,.18,-5.4,.57,.19,.57,'stone2')
 # Export only semantic changed/new geometry for incremental collision updates.
 bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();parts=[]
 for o in added+edited:
  ev=o.evaluated_get(deps);m=ev.to_mesh();m.calc_loop_triangles();vertices=[]
  for v in m.vertices:
   p=o.matrix_world@v.co;vertices.append([round(p.x,7),round(p.z,7),round(-p.y,7)])
  parts.append({'name':o.get('sourceComponent',o.name),'vertices':vertices,'faces':[list(t.vertices)for t in m.loop_triangles],'physical':bool(o.get('physical')),'editedExisting':o in edited,'material':o.data.materials[0].name});ev.to_mesh_clear()
 (W/f'{code}-polish-parts.json').write_text(json.dumps(parts,separators=(',',':'))+'\n')
 dest=D/code/f'{code}-r21.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
 runtime=R/f'public/models/bdeh-r21/{code}.glb';report=export_batched(root,runtime,f'R21_{code}_PolicyPlace',f'{code} final R21 incremental polish from approved39f4194')
 report.update({'code':code,'stage':2,'rebuildOrigin':'Approved final39f4194 Blender source, incremental edits only','sourceObjectsRetained':len(original)-len(removed),'newOrChangedObjects':len(added)+len(edited),'sourceBlend':str(dest.relative_to(R)),'sourceBlendSHA256':hashlib.sha256(dest.read_bytes()).hexdigest(),'GLBSHA256':hashlib.sha256(runtime.read_bytes()).hexdigest(),'glbBytes':runtime.stat().st_size,'blendBytes':dest.stat().st_size,'partsSHA256':hashlib.sha256((W/f'{code}-polish-parts.json').read_bytes()).hexdigest(),'basePartsSHA256':baseline['partsSHA256'],'baseBlendSHA256':baseline['sourceBlendSHA256'],'scale':1,'newLights':0,'materials':len({m.name for o in root.children_recursive if o.type=='MESH'for m in o.data.materials})})
 (D/code/'model-report.json').write_text(json.dumps(report,indent=2)+'\n');(O/code).mkdir(parents=True,exist_ok=True)
 (O/code/'model-changes.json').write_text(json.dumps({'baseCommit':'39f41940fd3af0f432b477ebd36ad5b677a71db1','newComponents':len(added),'editedComponents':[o.get('sourceComponent')for o in edited],'removedOnlySparseRoofMarkers':len(removed),'before':baseline,'after':report},indent=2)+'\n')
 print('Final R21 incremental',code,report['triangles'],'triangles;',len(added),'new components;',len(edited),'edited;',len(removed),'old sparse markers removed',flush=True)
