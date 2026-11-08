"""Compose evidence only; original rendered pixels and provenance stay separate."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, math, heapq

R=Path(__file__).resolve().parents[2]
O=R/'docs/previews/bdeh-r21'
D=R/'docs/design/bdeh-r21'
def board(files, labels, target, columns=2, tile=(800,600)):
    width,height=tile; rows=math.ceil(len(files)/columns)
    canvas=Image.new('RGB',(width*columns,(height+32)*rows),'#f5f5f2')
    draw=ImageDraw.Draw(canvas)
    for i,(file,label) in enumerate(zip(files,labels)):
        x,y=(i%columns)*width,(i//columns)*(height+32)
        image=Image.open(file).convert('RGB'); image.thumbnail(tile)
        canvas.paste(image,(x+(width-image.width)//2,y+32))
        draw.text((x+12,y+10),label,fill='#18373d')
    target.parent.mkdir(parents=True,exist_ok=True);canvas.save(target)

records=[]
for code in 'BDEH':
    folder=O/code/'blender'; record=json.loads((folder/'render-record.json').read_text())
    report=json.loads((D/code/'model-report.json').read_text())
    sha=hashlib.sha256((D/code/f'{code}-r21.blend').read_bytes()).hexdigest()
    assert sha==record['sourceBlendSHA256']==report['sourceBlendSHA256']
    views=['hero','front','back','left','right','top']
    board([folder/f'{v}.png' for v in views],[f'{code} / actual Blender / {v}' for v in views],O/code/'six-views.png',3)
    before=O/code/'iteration-1/blender/hero.png'
    if before.exists():
        board([before,folder/'hero.png'],[f'{code} / saved iteration 1 / same camera / 16 samples',f'{code} / refined R21 / same camera / 64 samples'],O/code/'before-after-blender.png')
    records.append({'code':code,'sourceBlendSHA256':sha,'renderViews':len(record['records']),'blenderEngine':record['engine']})
board([O/c/'blender/hero.png' for c in 'BDEH'],[f'{c} / same camera and 45-unit orthographic scale' for c in 'BDEH'],O/'four-island-blender-overview.png')

game=O/'game'
if (game/'capture-record.json').exists():
    final=json.loads((game/'capture-record.json').read_text())
    early=json.loads((O/'iteration-1/game/capture-record.json').read_text())
    for c in 'BDEH':
        for suffix in ['hero','top','mobile-native','mobile-facing']:
            name=f'{c}-{suffix}'; a=next(r for r in early['records']if r['name']==name);b=next(r for r in final['records']if r['name']==name)
            # Native obstruction avoidance can move the camera; QA comparison
            # requires exact camera equality. Native images retain pose records.
            if suffix in ['hero','top']:assert a['camera']==b['camera']
            board([O/'iteration-1/game'/f'{name}.png',game/f'{name}.png'],['Actual game / saved first integration','Actual game / final R21 / same player orbit and viewport'],O/c/f'before-after-game-{suffix}.png',tile=(600,800)if'mobile'in suffix else(800,600))
    board([game/f'{c}-hero.png'for c in 'BDEH'],[f'{c} / actual eight-island game / QA overview'for c in 'BDEH'],O/'four-island-game-overview.png')
    board([game/f'{c}-mobile-facing.png'for c in 'BDEH'],[f'{c} / native portrait profile / normal orbit rotation'for c in 'BDEH'],O/'four-island-mobile-overview.png',4,(430,932))

# Compare the actual accepted PR18 network, not the generator's historical A
# reference. Distances use actual regenerated centreline samples and edge graph.
def summarize(file):
    layout=json.loads(file.read_text());graph={n['id']:[]for n in layout['nodes']}
    for p in layout['paths']:
        graph[p['from']].append((p['to'],p['length']));graph[p['to']].append((p['from'],p['length']))
    pairs={}
    for start in 'ABCDEFGH':
        dist={start:0};queue=[(0,start)]
        while queue:
            cost,node=heapq.heappop(queue)
            if cost!=dist[node]:continue
            for end,length in graph[node]:
                new=cost+length
                if new<dist.get(end,1e20):dist[end]=new;heapq.heappush(queue,(new,end))
        pairs[start]={end:round(dist[end],3)for end in 'ABCDEFGH'}
    coords=[point for p in layout['paths']for point in p['points']]
    xs=[p[0]if isinstance(p,list)else p['x'] for p in coords];zs=[p[2]if isinstance(p,list)else p['z']for p in coords]
    return {'totalCentrelineLength':sum(p['length']for p in layout['paths']),'pathCount':len(layout['paths']),'width':layout['width'],'nodeCount':len(layout['nodes']),'shortestIslandGraphDistances':pairs,'centrelineBounds':[min(xs),min(zs),max(xs),max(zs)],'note':'Graph endpoint lengths, not exact door-to-door distance across each public courtyard.'}
comparison={'baseCommit':'2b4404927f33096ab28539a01f5e6236d670c038','before':summarize(D/'baseline/yuan-layout.json'),'after':summarize(R/'src/data/yuan-layout.json')}
(O/'network-comparison-r21.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2)+'\n')
(O/'render-provenance.json').write_text(json.dumps({'finalBlender':records,'pixelCompositionOnly':True,'noAIImages':True,'historicalImagesAreNotFinal':True},indent=2)+'\n')
print('R21 evidence boards and same-source render hashes verified')
