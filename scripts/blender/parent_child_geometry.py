"""Editable, original geometry for the supplied parent/child centre reference. MIT."""
import bpy, bmesh, math, random
from mathutils import Vector

COL=None

def collection(name):
    global COL
    COL=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(COL)
    return COL

def move(obj,parent=None):
    for c in list(obj.users_collection):c.objects.unlink(obj)
    COL.objects.link(obj)
    if parent:obj.parent=parent
    return obj

def empty(name,parent=None):
    o=bpy.data.objects.new(name,None);COL.objects.link(o)
    if parent:o.parent=parent
    return o

def linear(h):
    h=h.lstrip('#');v=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v)

def material(name,hexcolor,rough=.55,metal=0,transmission=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;c=linear(hexcolor);m.diffuse_color=(*c,1)
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    p.inputs['Transmission Weight'].default_value=transmission;p.inputs['IOR'].default_value=1.45
    return m

def mesh(name,verts,faces,mat,parent=None,smooth=False):
    g=bpy.data.meshes.new(name);g.from_pydata(verts,[],faces);g.update();o=bpy.data.objects.new(name,g);COL.objects.link(o)
    if mat:g.materials.append(mat)
    if parent:o.parent=parent
    if smooth:
        for p in g.polygons:p.use_smooth=True
    return o

def bevel(o,width=.03,segments=3):
    if width:
        b=o.modifiers.new('Physical edge radii','BEVEL');b.width=width;b.segments=segments
        b.limit_method='ANGLE'
        n=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL');n.keep_sharp=True
    return o

def box(name,loc,dims,mat,parent=None,r=.025):
    x,y,z=[v/2 for v in dims]
    v=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    o=mesh(name,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,parent);o.location=loc
    return bevel(o,min(r,min(dims)*.35),3)

def cylinder(name,loc,radius,depth,mat,parent=None,vertices=32,r2=None):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=radius,radius2=radius if r2 is None else r2,depth=depth,location=loc)
    o=move(bpy.context.object,parent);o.name=name;o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
    return bevel(o,min(.012,radius*.08,depth*.12),2)

_ico_cache={}
def sphere(name,loc,scale,mat,parent=None,subdiv=2):
    key=(subdiv,mat.name)
    if key not in _ico_cache:
        g=bpy.data.meshes.new('SharedIcosphere_'+mat.name+'_'+str(subdiv));bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=subdiv,radius=1);bm.to_mesh(g);bm.free();g.materials.append(mat);_ico_cache[key]=g
    o=bpy.data.objects.new(name,_ico_cache[key]);COL.objects.link(o);o.location=loc;o.scale=scale
    if parent:o.parent=parent
    return o

def beam(name,a,b,width,mat,parent=None,depth=None):
    a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(width,width if depth is None else depth,(b-a).length),mat,parent,r=width*.2)
    o.rotation_mode='QUATERNION';o.rotation_quaternion=(b-a).to_track_quat('Z','Y');return o

def tube(name,points,radius,mat,parent=None,sides=8,caps=True):
    pts=[Vector(p) for p in points];verts=[]
    for i,p in enumerate(pts):
        tangent=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized()
        ref=Vector((0,0,1)) if abs(tangent.z)<.95 else Vector((1,0,0));u=tangent.cross(ref).normalized();v=tangent.cross(u).normalized()
        for j in range(sides):verts.append(tuple(p+radius*(u*math.cos(j*math.tau/sides)+v*math.sin(j*math.tau/sides))))
    faces=[]
    for i in range(len(pts)-1):
        for j in range(sides):a=i*sides+j;b=i*sides+(j+1)%sides;faces.append((a,b,b+sides,a+sides))
    if caps:faces.extend([tuple(reversed(range(sides))),tuple((len(pts)-1)*sides+j for j in range(sides))])
    return mesh(name,verts,faces,mat,parent,True)

def prism_xz(name,outline,y,thickness,mat,parent=None):
    # CCW in X/Z when viewed from the south; front/back faces closed.
    if sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(outline,outline[1:]+outline[:1]))<0:outline=list(reversed(outline))
    n=len(outline);verts=[(x,y-thickness/2,z)for x,z in outline]+[(x,y+thickness/2,z)for x,z in outline]
    faces=[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[(i,i+n,(i+1)%n+n,(i+1)%n)for i in range(n)]
    return mesh(name,verts,faces,mat,parent)

def prism_xy(name,outline,z,thickness,mat,parent=None):
    n=len(outline);verts=[(x,y,z)for x,y in outline]+[(x,y,z+thickness)for x,y in outline]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
    return mesh(name,verts,faces,mat,parent)

def profile(x,x0,x1,left,right,rise):
    u=max(0,min(1,(x-x0)/(x1-x0)));return left+(right-left)*u+rise*math.sin(math.pi*u)

def roof(name,x0,x1,y0,y1,left,right,rise,thickness,mats,parent):
    n=128;xs=[x0+(x1-x0)*i/n for i in range(n+1)];zs=[profile(x,x0,x1,left,right,rise)for x in xs]
    verts=[]
    for y,dz in [(y0,0),(y1,0),(y0,-thickness),(y1,-thickness)]:verts.extend((x,y,z+dz)for x,z in zip(xs,zs))
    k=n+1;faces=[];indices=[]
    for i in range(n):
        faces.extend([(i,i+1,k+i+1,k+i),(2*k+i,3*k+i,3*k+i+1,2*k+i+1),(i,2*k+i,2*k+i+1,i+1),(k+i,k+i+1,3*k+i+1,3*k+i)])
        indices.extend([0,1,2,2])
    faces.extend([(0,k,3*k,2*k),(n,2*k+n,3*k+n,k+n)]);indices.extend([2,2])
    o=mesh(name,verts,faces,mats[0],parent)
    for m in mats[1:]:o.data.materials.append(m)
    for p,index in zip(o.data.polygons,indices):p.material_index=index;p.use_smooth=index<2
    return o

def arch_pane(name,x0,x1,y,bottom,top_func,glass,parent):
    n=12;outline=[(x0,bottom),(x1,bottom)]+[(x1+(x0-x1)*i/n,top_func(x1+(x0-x1)*i/n))for i in range(n+1)]
    return prism_xz(name,outline,y,.038,glass,parent)

def ring(name,centre,r0,r1,z,height,mat,parent,n=96,start=0,end=math.tau):
    full=abs(end-start-math.tau)<1e-6;k=n if full else n+1
    verts=[]
    for radius,zz in [(r0,z),(r1,z),(r0,z+height),(r1,z+height)]:
        verts.extend((centre[0]+radius*math.cos(start+(end-start)*i/n),centre[1]+radius*math.sin(start+(end-start)*i/n),zz)for i in range(k))
    faces=[]
    for i in range(n):
        j=(i+1)%k
        faces.extend([(i,j,k+j,k+i),(2*k+i,3*k+i,3*k+j,2*k+j),(k+i,k+j,3*k+j,3*k+i),(i,2*k+i,2*k+j,j)])
    if not full:faces.extend([(0,k,3*k,2*k),(n,2*k+n,3*k+n,k+n)])
    return mesh(name,verts,faces,mat,parent)

def camera(name,position,target,ortho=None,lens=48):
    c=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,c);bpy.context.scene.collection.objects.link(o);o.location=position;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();c.lens=lens
    if ortho:c.type='ORTHO';c.ortho_scale=ortho
    c.clip_start=.05;c.clip_end=200;return o
