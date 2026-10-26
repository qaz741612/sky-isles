"""Size, SHA256 and actual media dimensions. No image editing/generation."""
import json,hashlib,subprocess
from pathlib import Path
from PIL import Image
root=Path('docs/previews/parent-child-glb-integration-v1');files=[]
for p in sorted([*root.glob('*.png'),*root.glob('*.mp4')]):
 data={'path':p.name,'repoPath':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 if p.suffix=='.png':
  with Image.open(p)as im:data.update(width=im.width,height=im.height)
 else:
  video=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));stream=next(s for s in video['streams']if s['codec_type']=='video');data.update(width=stream['width'],height=stream['height'],duration=float(video['format']['duration']),codec=stream['codec_name'],containerFrameRate=stream.get('avg_frame_rate'),audioTracks=sum(s['codec_type']=='audio'for s in video['streams']))
 files.append(data)
p=Path('public/models/parent-child-centre/parent-child-centre.glb');files.append({'path':str(p),'repoPath':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'kind':'Approved PR11 GLB, unchanged copy'})
(root/'media-manifest.json').write_text(json.dumps({'source':'Final running Three.js production build. QA screenshots labelled separately from player-follow cameras. Video from actual native keyboard input and CDP frames with original timestamps; no AI concept images.','files':files},ensure_ascii=False,indent=2)+'\n');(root/'SHA256SUMS').write_text(''.join(f['sha256']+'  '+f['repoPath']+'\n'for f in files));print(json.dumps({'files':len(files),'media':len(files)-1}))
