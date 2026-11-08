import json,numpy as np, matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
from shapely.affinity import scale
from shapely.ops import unary_union
j=json.load(open('/mnt/data/sky_isles_R21/base/BDEH_R18/data/road-candidate-r2.json'))
size={'B':(30,28),'D':(32,29),'E':(34,31),'H':(33,30)}
fig,axs=plt.subplots(2,2,figsize=(13,12));
for ax,(c,(w,d)) in zip(axs.ravel(),size.items()):
 site=scale(Point(0,0).buffer(1,resolution=90),w/2*.95,d/2*.95)
 a=np.array(j['nodes'][c]);lines=[]
 for e in j['allRoutesProposed']:
  if c not in (e['from'],e['to']):continue
  p=np.array(e['proposedControlPointsXZ']); t=np.linspace(0,1,200)[:,None]
  if len(p)==4: Q=(1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t**2*p[2]+t**3*p[3]
  else: Q=(1-t)*p[0]+t*p[-1]
  Q=Q-a;l=LineString(Q);cut=l.intersection(site)
  if cut.is_empty:continue
  if cut.geom_type=='LineString': parts=[cut]
  else:parts=[g for g in cut.geoms if g.geom_type=='LineString']
  for part in parts:
   P=np.array(part.coords);ax.plot(P[:,0],P[:,1],color='red',lw=2);lines.append(part)
   q=P[0] if np.linalg.norm(P[0])>np.linalg.norm(P[-1]) else P[-1]
   ax.text(q[0],q[1],e['id'],fontsize=9)
 road=unary_union([l.buffer(2.4) for l in lines]);sx,sy=site.exterior.xy;ax.plot(sx,sy,color='black',lw=2)
 if road.geom_type=='Polygon':ax.fill(*road.exterior.xy,color='lightcoral',alpha=.25)
 else:
  for p in road.geoms:
   if p.geom_type=='Polygon':ax.fill(*p.exterior.xy,color='lightcoral',alpha=.25)
 ax.set_title(c+f'  {w}x{d}');ax.set_aspect('equal');ax.grid(True,alpha=.15);ax.set_xlim(-19,19);ax.set_ylim(-19,19)
plt.tight_layout();plt.savefig('/mnt/data/sky_isles_R21/base/gate-intrusion.png',dpi=160)
