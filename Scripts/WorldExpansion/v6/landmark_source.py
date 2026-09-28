import sys,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(Path(__file__).parent))
import plan
from plan import Geo
start=len(plan.geometries)
g=Geo('RiverMillFoundation','stone');g.box(65,-280,-1.5,12,11,8.6)
for z in [1,3,5,7]:g.box(65,-280,z,12.3,11.3,.18)
g.save()
g=Geo('RiverMillWheel','wood');cx,cy,cz=57.3,-280,2.25
def point(x,r,a):return [cx+x,cy+r*math.cos(a),cz+r*math.sin(a)]
for i in range(32):
 a=i*math.tau/32;b=(i+1)*math.tau/32
 for x in [-.5,.5]:g.face([point(x,2.5,a),point(x,2.5,b),point(x,2.16,b),point(x,2.16,a)])
 for rad in [2.16,2.5]:g.face([point(-.5,rad,a),point(.5,rad,a),point(.5,rad,b),point(-.5,rad,b)])
 g.face([point(-.7,2.48,a),point(.7,2.48,a),point(.7,2.72,a),point(-.7,2.72,a)])
 if i%4==0:
  for x in [-.38,.38]:g.face([point(x,.25,a-.15),point(x,2.16,a-.04),point(x,2.16,a+.04),point(x,.25,a+.15)])
g.box(59,-280,2.08,5,.34,.34);g.save()
g=Geo('MillLanding','wood');g.box(57.8,-292,1.2,4.4,7,.25)
for x in [55.8,59.8]:
 for y in [-295,-292,-289]:g.box(x,y,-2,.25,.25,3.8)
for y in range(-295,-288):g.box(57.8,y,1.47,4.4,.075,.055)
g.save()
# Remains of a four-span aqueduct, with genuine open arches and broken top courses.
g=Geo('OldAqueduct','stone');base=8.8;yy=490
for x in [-213,-204,-195,-186,-177]:g.box(x,yy,base,1.6,2.1,5.8)
for x in [-208.5,-199.5,-190.5,-181.5]:
 for i in range(16):
  a=i*math.pi/16;b=(i+1)*math.pi/16
  def p(rad,t,y):return [x+rad*math.cos(t),y,base+5.8+rad*math.sin(t)]
  for y in [yy-1.05,yy+1.05]:g.face([p(3.7,a,y),p(4.8,a,y),p(4.8,b,y),p(3.7,b,y)])
  for rad in [3.7,4.8]:g.face([p(rad,a,yy-1.05),p(rad,b,yy-1.05),p(rad,b,yy+1.05),p(rad,a,yy+1.05)])
 for j in range(7):g.box(x-3+j,yy,base+10.4,1,2.15,.5+(.4 if j%3 else 0))
g.save()
(R/'Docs/WorldExpansion/V6/landmarks.json').write_text(json.dumps({'geometry':plan.geometries[start:],'placements':[{'name':'RiverMill','asset':'Lodge','location':[65,-280,7.1],'yaw':90,'scale':[1.28,1.28,1.1]},{'name':'MillStore','asset':'BlueShed','location':[68,-284,7.1],'yaw':0,'scale':[1,1,1]},{'name':'MillSign','asset':'Sign','location':[70,-272,6.8],'yaw':90,'scale':[.85,.85,.85]}],'paths':[{'name':'MillTrack','mesh_name':'MillTrackR2','points':[[69,-272],[105,-266],[155,-273],[195,-272],[218,-263],[236,-260],[246,-261]],'width':2.7},{'name':'AqueductTrail','points':[[-225,390],[-211,412],[-214,443],[-195,469],[-195,490]],'width':2.4}]},indent=2))
print('Landmark geometry',len(plan.geometries)-start)

