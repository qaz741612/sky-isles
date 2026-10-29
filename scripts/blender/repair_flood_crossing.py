"""MIT. Repair the saved final source's hydraulic openings without rebuilding artwork.
Public surface, collision, NPC, all architecture/vegetation and camera poses stay exact.
"""
import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'docs/design/flood-control-island-g-v1';bpy.ops.wm.open_mainfile(filepath=str(D/'flood-control-g.blend'));parent=bpy.data.objects['WaterChannels'];material=bpy.data.materials['Chalk coping']
for o in list(parent.children):
 if o.name.startswith('Channel coping and retaining wall')or o.name.startswith('Actual public crossing underside'):bpy.data.objects.remove(o,do_unlink=True)
def mesh(name,v,f):
 m=bpy.data.meshes.new(name);m.from_pydata([(x,-z,y)for x,y,z in v],[],f);m.materials.append(material);m.update();o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);o.parent=parent
site=json.loads((ROOT/'src/data/flood-control-site.json').read_text())
for e in site['waterRails']:
 a,b=e['a'],e['b'];base=-.32 if e['coveredCrossing'] else -1.65;mesh('Channel coping and retaining wall',[(a[0],-.04,a[1]),(b[0],-.04,b[1]),(b[0],base,b[1]),(a[0],base,a[1])],[(0,1,2,3)])
d=json.loads((ROOT/'src/data/flood-control-bridge-soffit.json').read_text());mesh('Actual public crossing underside',d['vertices'],d['triangles']);bpy.ops.wm.save_as_mainfile(filepath=str(D/'flood-control-g.blend'));print('CROSSING_OPENINGS_REPAIRED',sum(e['coveredCrossing']for e in site['waterRails']),flush=True)
