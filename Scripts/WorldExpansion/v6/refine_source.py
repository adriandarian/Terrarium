import sys,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(Path(__file__).parent));import plan
Geo=plan.Geo;start=len(plan.geometries)
g=Geo('MillStairs','wood');ax,ay,bx,by=59,-275,55.8,-289;dx=bx-ax;dy=by-ay;ln=math.hypot(dx,dy);nx=-dy/ln;ny=dx/ln
def stepface(points):g.face([[ax+dx*t+nx*s,ay+dy*t+ny*s,z] for t,s,z in points])
for i in range(32):
 a=i/32;b=(i+1)/32;z=7.1-(i+1)*5.6/32
 stepface([(a,-.85,z),(b,-.85,z),(b,.85,z),(a,.85,z)])
 stepface([(a,-.85,z),(a,.85,z),(a,.85,z+.175),(a,-.85,z+.175)])
 if i%4==0:
  t=(a+b)/2
  for side in [-1,1]:g.box(ax+dx*t+nx*.87*side,ay+dy*t+ny*.87*side,z,.13,.13,1.0)
for side in [-1,1]:
 for off in [-.055,.055]:stepface([(0,side*.87+off,8.1),(1,side*.87+off,2.5),(1,side*.87+off,2.62),(0,side*.87+off,8.22)])
g.save()
g=Geo('CivicPlanterStone','stone')
for x,y in [(279.5,295),(279.5,311),(319.5,295),(319.5,311)]:
 for yy in [y-2,y+2]:g.box(x,yy,25.5,4,.35,.55)
 for xx in [x-2,x+2]:g.box(xx,y,25.5,.35,4,.55)
g.save()
g=Geo('Bell','brass');x,y,z=284,307,38.5
levels=[(0,.72),(.14,.66),(.5,.46),(.85,.36),(1,.18)]
for (h,r),(hh,rr) in zip(levels,levels[1:]):
 for i in range(20):
  a=i*math.tau/20;b=(i+1)*math.tau/20;g.face([[x+r*math.cos(a),y+r*math.sin(a),z+h],[x+r*math.cos(b),y+r*math.sin(b),z+h],[x+rr*math.cos(b),y+rr*math.sin(b),z+hh],[x+rr*math.cos(a),y+rr*math.sin(a),z+hh]])
g.box(x,y,z-.15,.16,.16,.7);g.save()
(R/'Docs/WorldExpansion/V6/refinements.json').write_text(json.dumps({'geometry':plan.geometries[start:]},indent=2))
