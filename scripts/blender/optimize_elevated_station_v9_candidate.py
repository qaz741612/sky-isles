"""Candidate-only thin-glass pass reduction; never modifies the art BLEND/showcase. MIT."""
import bpy,sys,os,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from elevated_station_v9.exporter import export
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/design/transport-elevated-station-v9-prototype';source=OUT/'transport-station-v9.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(source);show=sha(OUT/'transport-station-v9-showcase.glb');bpy.ops.wm.open_mainfile(filepath=str(source));root=bpy.data.objects['YuanliElevatedStationV9'];changes=[]
for name,alpha in [('glass',.25),('trainGlass',.54)]:
 m=bpy.data.materials[name];p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=0;p.inputs['Alpha'].default_value=alpha;m.surface_render_method='BLENDED';m.diffuse_color=(*m.diffuse_color[:3],alpha);changes.append({'material':name,'alpha':alpha,'transmission':0,'appearanceDifference':'Thin transparent approximation retains views through panes but removes refraction; inspect candidate browser views against showcase.'})
for o in root.children_recursive:
 for m in o.modifiers:
  if m.type=='BEVEL':m.segments=1
bpy.context.view_layer.update();r=export(root,OUT/'transport-station-v9-game-candidate.glb',True);assert sha(source)==before and sha(OUT/'transport-station-v9-showcase.glb')==show;r['sha256']=sha(OUT/'transport-station-v9-game-candidate.glb');r['thinGlassOptimization']=changes;r['mode']+='; candidate-only alpha thin glass, no refraction pass';m=json.loads((OUT/'model-report.json').read_text());m['candidate']=r;m['candidateOptimizationScriptSHA256']=sha(Path(__file__));(OUT/'model-report.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print('CANDIDATE_ONLY_OPTIMIZED',json.dumps(r),flush=True);sys.stdout.flush();os._exit(0)
