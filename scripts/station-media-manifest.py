"""Read metadata only; all media comes from the actual final Three.js build."""
import json,hashlib,subprocess
from pathlib import Path
from PIL import Image
root=Path('docs/previews/transport-station-glb-integration-v1');files=[]
for p in sorted(list(root.glob('*.png'))+list(root.glob('*.mp4'))):
 d={'path':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 if p.suffix=='.png':
  with Image.open(p) as image:d.update(width=image.width,height=image.height)
 else:
  v=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_streams','-show_format','-of','json',str(p)]));s=next(s for s in v['streams'] if s['codec_type']=='video');d.update(width=s['width'],height=s['height'],durationSeconds=float(v['format']['duration']),codec=s['codec_name'],audioStreams=sum(s['codec_type']=='audio' for s in v['streams']))
 files.append(d)
assert len([d for d in files if d['path'].endswith('.png')])==8
assert len([d for d in files if d['path'].endswith('.mp4')])==1
(root/'media-manifest.json').write_text(json.dumps({'source':'Final built Three.js game; native keyboard/mouse video without teleports or time scaling. QA photo cameras explicitly labelled.','files':files},ensure_ascii=False,indent=2)+'\n')
(root/'SHA256SUMS').write_text(''.join(d['sha256']+'  '+d['path']+'\n' for d in files))
print(json.dumps({'files':len(files),'bytes':sum(d['bytes'] for d in files),'video':files[-1] if files[-1]['path'].endswith('.mp4') else next(d for d in files if d['path'].endswith('.mp4'))}))
