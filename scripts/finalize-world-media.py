"""Index final native screenshots/video. Contact sheet only arranges real frames."""
from pathlib import Path
import hashlib, json, subprocess, struct
from PIL import Image, ImageDraw, ImageFont
root=Path('docs/previews/eight-islands-world-redesign-v1')
record=json.loads((root/'build-record.json').read_text())
for p,expected in record['sources'].items():
    assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==expected, f'Final runtime source changed: {p}'
stats=json.loads((root/'after/render-stats.json').read_text())
asset='/assets/'+Path(record['runtimeAsset']['path']).name
assert all(v['sourceAsset']==asset for v in stats['views'].values()), 'Screenshot source mismatch'
assert not stats['errors']
ops=json.loads((root/'operation-log.json').read_text())
assert not any(o['type']=='failure' for o in ops), 'Recording failed'
assert ops[-1]['type']=='final' and ops[-1]['state']['respawnCount']==0
assert len({o['name'] for o in ops if o['type']=='island'})==7, 'Recording did not visit eight islands including home'
assert next(o['source'] for o in ops if o['type']=='asset')==asset
names=['home','tree','temple','koi','meadow','windmill','crystal','lookout']
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
sheet=Image.new('RGB',(1200,8*310),(245,243,235));draw=ImageDraw.Draw(sheet)
for row,name in enumerate(names):
    for col,side in enumerate(['front','side','back']):
        im=Image.open(root/f'after/qa-{name}-{side}.png').convert('RGB');im.thumbnail((400,278))
        sheet.paste(im,(col*400,row*310+28));draw.text((col*400+8,row*310+4),f'{name} / QA {side}',font=font,fill=(47,66,65))
sheet.save(root/'architecture-contact-sheet.png')
video=root/'normal-operation.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-print_format','json','-show_format','-show_streams',str(video)]))
raw=Path('work/world-recording/normal-operation.webm')
if raw.exists():
    raw_probe=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-print_format','json','-show_format','-show_streams',str(raw)]))
    assert abs(float(raw_probe['format']['duration'])-float(probe['format']['duration']))<.1, 'Video time base changed'
    probe['sourceWebm']={'retainedInWork':True,'bytes':raw.stat().st_size,'sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'durationSeconds':float(raw_probe['format']['duration'])}
(root/'video-metadata.json').write_text(json.dumps(probe,indent=2))
stream=next(s for s in probe['streams'] if s['codec_type']=='video')
files=[]
for p in sorted(root.rglob('*')):
    if p.suffix.lower() not in ['.png','.mp4']:continue
    item={'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    if p.suffix.lower()=='.png':
        with Image.open(p) as im:
            item.update(width=im.width,height=im.height);im.verify()
        if p.name=='architecture-contact-sheet.png':item.update(role='QA collage of final native frames',sourceAsset=asset)
        elif p.parent.name=='before':item.update(role='V4 normal exploration frame; physical collision may adjust observer position',sourceCommit=record['base'])
        elif p.parent.name=='comparison':item.update(role='Same-optics QA comparison, avatar/UI hidden',sourceCommit=record['base'] if p.name.startswith('before-') else record.get('sourceCommit'),sourceAsset='/assets/index-2zaL7Num.js' if p.name.startswith('before-') else asset)
        else:item.update(role='Final QA camera' if p.name.startswith('qa-') else 'Final normal exploration/panorama camera',sourceAsset=asset)
    else:item.update(width=stream['width'],height=stream['height'],durationSeconds=float(probe['format']['duration']),role='Normal-speed native automated keyboard/mouse game operation; no teleport or sim stepping; silent',sourceAsset=asset)
    files.append(item)
manifest={'runtimeSourceCommit':record.get('sourceCommit'),'runtimeAsset':record['runtimeAsset'],'sourceCommitForBefore':record['base'],'files':files,'count':len(files),'totalBytes':sum(f['bytes'] for f in files)}
(root/'media-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(root/'SHA256SUMS').write_text(''.join(f"{f['sha256']}  {f['path']}\n" for f in files))
print(json.dumps({'mediaCount':len(files),'totalBytes':manifest['totalBytes'],'videoSeconds':float(probe['format']['duration'])}))
