import json,math
import numpy as np
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle, Circle
from shapely.geometry import Polygon,Point,box,LineString
P=Path('/mnt/data/G_V5_work')
x=json.load(open(P/'G_V5_design_manifest.json'))
shell=Polygon(x['newFootprint']);water=[Polygon(a) for a in x['waterBodies']]
centre=np.array([44.928,45.279]);route={
'S21':np.array([[44.226,6.318],[47.736,13.338],[53.001,33.696],[44.928,45.279]])-centre,
'S22':np.array([[44.928,45.279],[37.908,46.683],[36.504,40.716],[31.239,37.557]])-centre,
'S20':np.array([[50.544,88.452],[59.319,88.803],[60.021,83.538],[58.617,65.286]])-centre}
def be(cp,t):return (1-t)**3*cp[0]+3*(1-t)**2*t*cp[1]+3*(1-t)*t*t*cp[2]+t**3*cp[3]
roads={n:LineString([be(c,i/400) for i in range(401)]) for n,c in route.items()}
core={n:r.buffer(2.4,cap_style=2) for n,r in roads.items()}
NPC=box(8.7,-10.6,11.7,-7.6)
architect={ 'Command centre':box(2.75,1.42,15.2,8.45),'Operations wing':box(7.4,-4.5,14.5,-.3),'Dam gate block':box(-15.7,4.08,-2.95,8.7)}
# Geometry hard checks. Dam intentionally intersects upstream/downstream water; bridge intentionally overlaps lower water.
issues=[]
if any(not shell.contains(q) for q in water):issues.append('water basin outside island')
if not shell.contains(NPC):issues.append('NPC square outside island')
if any(NPC.intersects(q) for q in water):issues.append('NPC square intersects water')
for name,q in core.items():
 if name in ['S21','S22'] and q.intersects(NPC):issues.append('NPC intersects protected '+name)
for name,p in architect.items():
 if not shell.covers(p):issues.append('building outside island: '+name)
 if name!='Dam gate block' and any(p.intersects(core[k]) for k in ['S21','S22']):issues.append('building overlaps 4.8 road core '+name)
 if name=='Command centre' and any(p.intersects(q) for q in water):issues.append('centre touches basin')
# Distances without S20 buffered core collision
if shell.intersects(core['S20']):issues.append('S20 hits widened G')
if issues: print('ISSUES',issues)
else:print('NO HARD STATIC ISSUE identified. Still not verified in actual game.')
# Actual clearance with S20
clearance=shell.distance(core['S20'])
# Water crossing requires a structural bridge, not a defect if elevated
crossing=core['S22'].intersection(water[1])
assert crossing.area>1
assert round(crossing.area,2)==x['routeAudit']['S22']['waterOverlapLower']
# site diagram left local + area right overview
plt.rcParams['font.family']='DejaVu Sans'
fig,(ax,ax2)=plt.subplots(1,2,figsize=(15,8),facecolor='#f5f6f4',gridspec_kw={'width_ratios':[1.08,.92]})
for a in [ax,ax2]:a.set_facecolor('#f7f8f5');a.set_aspect('equal');a.grid(color='#d8dedc',lw=.5,alpha=.6)
old=Polygon([(14*math.cos(t),13*math.sin(t)) for t in np.linspace(0,math.tau,65)])
ax.plot(*old.exterior.xy,color='#afafab',lw=1.8,linestyle='--',label='Original G 28x26')
ax.add_patch(MPoly(np.array(shell.exterior.coords),facecolor='#d7e8d0',edgecolor='#385458',linewidth=2,label='Expanded G 38.4x34.4'))
for i,w in enumerate(water):ax.add_patch(MPoly(np.array(w.exterior.coords),facecolor=('#3d9aa7' if i==0 else '#2e7188'),alpha=.88,edgecolor='#21546a',linewidth=1.5))
for k,c in core.items():
 if k!='S20':
  ax.add_patch(MPoly(np.array(c.intersection(shell).exterior.coords),facecolor='#c8bca7',alpha=.86,edgecolor='none'))
for name,p in architect.items():
 color={'Command centre':'#bda579','Operations wing':'#dcc1a0','Dam gate block':'#435c63'}[name]
 ax.add_patch(MPoly(np.array(p.exterior.coords),facecolor=color,edgecolor='#283d47',linewidth=1.4))
ax.add_patch(MPoly(np.array(NPC.exterior.coords),facecolor='#f8d778',edgecolor='#7d6634',linewidth=1.6))
ax.text(10.2,-9.1,'NPC',ha='center',va='center',fontsize=9,fontweight='bold')
ax.text(-10.3,7,'3-bay gate',ha='center',fontsize=10,color='white',fontweight='bold');ax.text(9.3,5.3,'Command',ha='center',fontsize=10,color='#142a33')
ax.text(-10.5,10.6,'Upper',ha='center',color='#f6ffff');ax.text(-9,-1,'Lower',ha='center',color='white')
ax.plot(*roads['S22'].xy,color='#f9f7ea',lw=1.5,alpha=.9);ax.plot(*roads['S21'].xy,color='#f9f7ea',lw=1.5,alpha=.9)
ax.annotate('S22 bridge\nover water',xy=(-10,-3.8),xytext=(-21,-13),arrowprops={'arrowstyle':'->','color':'#b36332'},color='#7c4b30',fontsize=10)
ax.set_xlim(-23,23);ax.set_ylim(-20,21);ax.set_title('G V5 — proposed geometry / protected routes',fontsize=13,color='#23434b')
# overview
ax2.add_patch(MPoly(np.array(shell.exterior.coords),facecolor='#d7e8d0',edgecolor='#466a5f',linewidth=2))
for nm in ['S20','S21','S22']:
 q=core[nm];ax2.add_patch(MPoly(np.array(q.exterior.coords),facecolor=('#dda15e' if nm=='S20' else '#b4bec4'),edgecolor='none',alpha=.6))
 ax2.plot(*roads[nm].xy,lw=1.7,label=nm)
H=Point(50.544,88.452)-Point(44.928,45.279) if False else (50.544-44.928,88.452-45.279)
ax2.add_patch(Circle(H,radius=9,facecolor='#cad2dc',edgecolor='#506c88',alpha=.8))
ax2.text(H[0],H[1],'H island',ha='center',va='center',fontsize=11)
ax2.text(0,0,'G (expanded)',ha='center',fontsize=10,color='#224c45')
ax2.set_xlim(-29,32);ax2.set_ylim(-21,56);ax2.set_title('Regional bridge and neighboring island clearance',fontsize=13,color='#23434b')
fig.suptitle('Sky Isles  /  G Flood Control V5  /  preliminary footprint feasibility',fontsize=18,color='#1f3940',y=.98)
fig.text(.5,.02,'Reference centre (44.928, 45.279). Static geometry check only — game collisions/camera/mobile FPS remain unverified.',ha='center',fontsize=10,color='#687779')
fig.tight_layout(rect=[0,.045,1,.95]);fig.savefig(P/'G_V5_spatial_audit.png',dpi=165,bbox_inches='tight');plt.close(fig)
report={'islandArea':round(shell.area,2),'islandBounds':list(map(list,[shell.bounds[:2],shell.bounds[2:]])), 'waterArea':round(sum(z.area for z in water),2),
 'waterPercent':round(100*sum(z.area for z in water)/shell.area,1),'actualBridgeCoreWidth':4.8,
 'S20WaterGGapAfterCore':round(clearance,2),'S20ConservativeSampleGap':4.08,'S22RoadWaterOverlap':round(crossing.area,2),
 'NPCNew':list(NPC.bounds),'npcBoundaryGap':round(NPC.distance(shell.boundary),2),
 'npcS21CoreGap':round(NPC.distance(core['S21']),2),'issues':issues,
 'qualifiedOnlyFor':'2D static geometry; NO in-engine proof',
 'knownOutstanding':['S22 road over basin requires actual continuous bridge structure and side-rails/collision','new water holes require regenerating dry ground, coping and camera collision','S20 G boundary must retain path buffer and scene clearance','full in-game camera and player walk tests not performed']}
(P/'G_V5_spatial_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,indent=2))
