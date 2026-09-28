"""V6 authored settlement plans. Pure source generation; native admission is separate."""
import json,math,random,hashlib
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parents[3];D=R/'Docs/WorldExpansion/V6';S=R/'SourceAssets/WorldExpansion/V6'
rng=random.Random(629)
old=json.loads((R/'Docs/WorldExpansion/settlement-layout.json').read_text())
assets=old['assets'];assets.update(json.loads((R/'Docs/WorldExpansion/settlement-collision-assets.json').read_text())['assets'])
assets['GardenWell']='/Game/Terrarium/Meshes/SM_GardenWell_v2_Detail'
centers={k:v['center_m'] for k,v in old['settlements'].items()} if 'settlements' in old else {'Alderhaven':[300,260,24],'Stonegate':[-320,390,35],'Brookmere':[-220,180,16],'Reedbank':[280,-300,12],'Highfield':[-340,-310,22]}
placements=[];instances=[];routes=[];geometries=[];occupied=[]
class Geo:
 def __init__(self,name,mat):self.name=name;self.mat=mat;self.v=[];self.t=[];self.uv=[]
 def face(self,p):
  n=len(self.v);self.v+=p
  a,b,c=p[:3];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)];normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  axis=max(range(3),key=lambda k:abs(normal[k]));axes=[k for k in range(3) if k!=axis]
  self.uv += [[q[axes[0]]/2,q[axes[1]]/2] for q in p]
  self.t += [[n,n+i,n+i+1] for i in range(1,len(p)-1)]
 def box(self,x,y,z,w,d,h):
  p=[[x+dx*w/2,y+dy*d/2,z+dz*h] for dz in [0,1] for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
  for f in [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]:self.face([p[i] for i in f])
 def save(self):
  if not self.v:return
  data={'vertices':self.v,'triangles':self.t,'uv0':self.uv};p=S/(self.name+'.json');p.write_text(json.dumps(data,separators=(',',':')))
  geometries.append({'name':self.name,'asset_suffix':'_r2' if self.name in ['CivicRamp','BellTowerStone'] else '', 'material':self.mat,'source':str(p.relative_to(R)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'triangles':len(self.t)})
def add(s,k,x,y,yaw=0,scale=1,z=0,kind='detail',actor=False):
 c=centers[s];scale=[scale]*3 if isinstance(scale,(int,float)) else list(scale)
 row={'label':f'WX6_{s}_{k}_{len(placements)+len(instances):05d}','settlement':s,'asset':k,'location_m':[c[0]+x,c[1]+y,c[2]+z],'yaw_deg':yaw,'scale':scale,'kind':kind}
 (placements if actor else instances).append(row);return row
def distseg(p,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
 return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def road(s,name,points,w=3.5):
 routes.append({'settlement':s,'name':name,'points':points,'width':w})
def nearest(s,x,y):
 return min(distseg((x,y),a,b)-r['width']/2 for r in routes if r['settlement']==s for a,b in zip(r['points'],r['points'][1:]))
def house(s,x,y,yaw=0,k='Cottage',scale=1,z=0,force=False):
 rad=5.7 if k=='HomesteadCompound' else 5.1 if k=='CivicHall' else 3.95
 rad*=scale
 if not force and (nearest(s,x,y)<rad+.65 or any(ss==s and math.hypot(x-xx,y-yy)<rad+rr+.6 for ss,xx,yy,rr in occupied)):return False
 occupied.append((s,x,y,rad));add(s,k,x,y,yaw,scale,z,'building',True)
 # Each lot has a rear garden and a broken boundary. No fence across front doors.
 a=math.radians(yaw);back=(math.sin(a),-math.cos(a));right=(math.cos(a),math.sin(a))
 for t in [-2.8,0,2.8]:
  gx=x+back[0]*5+right[0]*t;gy=y+back[1]*5+right[1]*t
  if nearest(s,gx,gy)>1.4:add(s,'Fence',gx,gy,yaw,(.87,1,.68),z,kind='lot_boundary')
 for t in [-1.6,1.6]:
  gx=x+back[0]*3.9+right[0]*t;gy=y+back[1]*3.9+right[1]*t
  if nearest(s,gx,gy)>1.4:add(s,'GardenPatch2m',gx,gy,yaw,.75,z,kind='kitchen_garden')
 return True
def frontages(s,r,spacing=10):
 for a,b in zip(r['points'],r['points'][1:]):
  dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);nx=-dy/length;ny=dx/length
  for i in range(max(1,int(length/spacing))):
   t=(i+.5)/max(1,int(length/spacing))
   for side in [-1,1]:
    offset=r['width']/2+5.1+rng.uniform(0,1.8);x=a[0]+t*dx+side*nx*offset;y=a[1]+t*dy+side*ny*offset
    if math.hypot(x,y)>({'Alderhaven':113,'Stonegate':78}.get(s,54)):continue
    yaw=math.degrees(math.atan2(side*nx,-side*ny))+rng.uniform(-5,5)
    house(s,x,y,yaw,'Lodge' if rng.random()<.3 else 'Cottage',rng.uniform(.95,1.1))
def wall(s,points,height=.7,gate=False):
 for a,b in zip(points,points[1:]):
  length=math.dist(a,b);n=math.ceil(length/3.8);yaw=math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]))
  for i in range(n):
   t=(i+.5)/n;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t
   if gate and nearest(s,x,y)<3:continue
   add(s,'MossCliff4m',x,y,yaw,(length/n/4,.16,height/2),kind='wall')
def orchard(s,x,y,w,h):
 for ix in range(int(w/6.5)):
  for iy in range(int(h/6.5)):
   xx=x+(ix+.5)*6.5;yy=y+(iy+.5)*6.5
   if nearest(s,xx,yy)>4 and all(ss!=s or math.hypot(xx-a,yy-b)>rr+3 for ss,a,b,rr in occupied):add(s,'BroadTree5m',xx,yy,rng.uniform(0,360),rng.uniform(.9,1.35),kind='orchard')
 wall(s,[(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)],.65,True)
def field(s,x,y,w,h,yaw=0):
 a=math.radians(yaw)
 def pt(dx,dy):return (x+math.cos(a)*dx-math.sin(a)*dy,y+math.sin(a)*dx+math.cos(a)*dy)
 for ix in range(int(w/2.2)):
  for iy in range(int(h/2.4)):
   xx,yy=pt((ix+.5)*2.2,(iy+.5)*2.4)
   if nearest(s,xx,yy)>2 and all(ss!=s or math.hypot(xx-bx,yy-by)>rr+1 for ss,bx,by,rr in occupied):add(s,'WheatPatch2m',xx,yy,yaw,(1,.93,rng.uniform(.75,1)),kind='crop')
 wall(s,[pt(0,0),pt(w,0),pt(w,h),pt(0,h),pt(0,0)],.65,True)

# Irregular market city: a civic terrace, three crooked loops, open orchard ward.
s='Alderhaven'
road(s,'South arrival',[(0,-125),(0,-28),(0,2)],6)
road(s,'Trade street',[(-125,0),(-50,0),(0,0),(65,0),(125,0)],5)
road(s,'West merchants',[(-86,-63),(-99,-23),(-83,24),(-53,62),(-12,78),(30,71),(69,47),(85,14),(74,-39),(38,-69),(-15,-81),(-58,-72),(-86,-63)],3.8)
road(s,'Potters lane',[(-87,-23),(-58,-36),(-28,-23),(0,-28),(26,-34),(51,-27),(74,-39)],3.3)
road(s,'Garden passage',[(-83,24),(-49,28),(-31,16),(0,0),(31,14),(51,32),(69,47)],3.2)
road(s,'North walk',[(-53,62),(-40,47),(-31,16)],3)
road(s,'East court',[(38,-69),(36,-51),(26,-34),(31,14)],3)
road(s,'Civic ascent',[(0,0),(0,15),(0,25),(0,34)],5)
# Civic precinct exclusion is explicit; housing cannot occupy the raised terrace.
occupied += [(s,0,44,27),(s,0,0,14)]
house(s,1,46,180,'CivicHall',1.35,1.5,True)
add(s,'GardenWell',-7,-6,scale=1,kind='market_focus',actor=True)
for x,y,a in [(-15,-11,90),(14,-9,-90),(-18,8,90),(16,8,-90)]:add(s,'MarketStall',x,y,a,.95,kind='market',actor=True)
for r in list(routes):
 if r['settlement']==s and r['name'] not in ['Civic ascent','South arrival']:frontages(s,r)
orchard(s,-110,50,36,36);orchard(s,60,58,37,34)
field(s,-79,-106,40,17,4);field(s,32,-107,35,19,-8)

# Stonegate follows a bent gate street inside an asymmetric enclosure.
s='Stonegate'
road(s,'Gate climb',[(0,-95),(0,-56),(-12,-30),(-6,-4),(8,20),(0,47)],5)
road(s,'Crossing',[(-95,0),(-36,0),(-6,-4),(35,0),(95,0)],4.4)
road(s,'West court',[(-55,-49),(-62,-19),(-51,18),(-25,40),(0,47),(35,38),(53,10),(49,-26),(22,-52),(-16,-63),(-55,-49)],3.4)
occupied += [(s,0,54,13),(s,-6,-4,10)]
house(s,0,57,180,'CivicHall',1.13,0,True)
add(s,'GardenWell',-12,-7,kind='well',actor=True)
for r in list(routes):
 if r['settlement']==s:frontages(s,r,10.5)
wall(s,[(-73,-59),(-84,-14),(-68,45),(-20,76),(38,67),(78,27),(79,-32),(30,-78),(-26,-80),(-73,-59)],2.5,True)
orchard(s,-69,32,28,22)

# Orchard village: horseshoe green, lanes, two substantial bounded orchards.
s='Brookmere'
road(s,'Orchard road',[(-65,0),(-24,0),(0,0),(25,0),(65,0)],3.8)
road(s,'Hill connection',[(0,0),(0,64)],4.4)
road(s,'Green crescent',[(-41,-27),(-21,-39),(7,-36),(29,-20),(33,0)],3)
road(s,'North gardens',[(-39,0),(-33,23),(-15,37),(0,33),(27,29)],2.8)
occupied += [(s,0,4,12)]
house(s,14,14,160,'Lodge',1.1,0,True)
add(s,'GardenWell',-7,-7,kind='well',actor=True)
for r in list(routes):
 if r['settlement']==s:frontages(s,r,13)
orchard(s,-57,24,25,30);orchard(s,23,27,29,25)
field(s,-53,-54,27,16,4)

# Reedbank is a long trading street, a warehouse yard and garden alleys.
s='Reedbank'
road(s,'North road',[(0,65),(0,23),(-8,4),(-6,-22),(12,-45)],4.5)
road(s,'Trade road',[(-8,4),(19,0),(65,0)],5)
road(s,'Waterside lane',[(-34,39),(-43,13),(-38,-17),(-19,-42),(12,-45),(37,-21),(33,2),(36,28),(15,40),(0,23)],3.4)
occupied += [(s,-7,4,11)]
house(s,-18,24,-90,'Lodge',1.18,0,True)
add(s,'MarketStall',-18,4,90,.95,kind='trade_stall',actor=True)
add(s,'MarketStall',-16,-5,90,.95,kind='trade_stall',actor=True)
for r in list(routes):
 if r['settlement']==s:frontages(s,r,12)
orchard(s,20,29,28,24);field(s,15,-56,33,15,-8)

# Highfield: village crescent at the edge of three working fields.
s='Highfield'
road(s,'Farm road',[(65,0),(18,0),(0,0),(-29,-9),(-54,-25)],4)
road(s,'North connection',[(0,0),(0,65)],4)
road(s,'Farm crescent',[(-45,22),(-22,35),(0,33),(29,26),(39,0)],3)
occupied += [(s,0,2,11)]
house(s,-14,10,-80,'Lodge',1.07,0,True)
add(s,'GardenWell',6,8,kind='well',actor=True)
for r in list(routes):
 if r['settlement']==s:frontages(s,r,13.5)
field(s,-51,-52,31,24,-5);field(s,-11,-49,28,27,4);field(s,22,-43,28,29,9)
orchard(s,-58,26,23,24)

# Streets are actual narrow mesh ribbons with the imagegen stone albedo.
for s,c in centers.items():
 g=Geo(s+'_Lanes','paving')
 for r in routes:
  if r['settlement']!=s:continue
  for a,b in zip(r['points'],r['points'][1:]):
   dx=b[0]-a[0];dy=b[1]-a[1];ln=math.hypot(dx,dy);nx=-dy/ln*r['width']/2;ny=dx/ln*r['width']/2
   def z(p):return c[2]+.065+(max(0,min(1,(p[1]-15)/10))*1.5 if s=='Alderhaven' and r['name']=='Civic ascent' else 0)
   g.face([[c[0]+p[0]+sx*nx,c[1]+p[1]+sx*ny,z(p)] for p,sx in [(a,1),(a,-1),(b,-1),(b,1)]])
 # Irregular small market courts, with substantial green retained elsewhere.
 outline=[(-13,-13),(10,-15),(17,-5),(14,11),(0,16),(-16,7)] if s=='Alderhaven' else [(-8,-9),(9,-7),(10,6),(0,10),(-10,5)]
 for a,b in zip(outline,outline[1:]+outline[:1]):g.face([[c[0],c[1],c[2]+.07],[c[0]+a[0],c[1]+a[1],c[2]+.07],[c[0]+b[0],c[1]+b[1],c[2]+.07]])
 g.save()
 # Street trees and lanterns follow actual lanes, with spaces around buildings.
 for r in [q for q in routes if q['settlement']==s]:
  for a,b in zip(r['points'],r['points'][1:]):
   x=(a[0]+b[0])/2;y=(a[1]+b[1])/2;dx=b[0]-a[0];dy=b[1]-a[1];ln=math.hypot(dx,dy)
   xx=x-dy/ln*(r['width']/2+2.2);yy=y+dx/ln*(r['width']/2+2.2)
   if all(ss!=s or math.hypot(xx-bx,yy-by)>rr+2 for ss,bx,by,rr in occupied):add(s,'BroadTree5m',xx,yy,scale=1.35,kind='street_tree')
   add(s,'Lantern',x+dy/ln*(r['width']/2+.65),y-dx/ln*(r['width']/2+.65),scale=.88,kind='street_furniture')

# Varied groves fill unused settlement margins and dissolve the bare pad edges.
for s,c in centers.items():
 radius={'Alderhaven':122,'Stonegate':91}.get(s,62)
 existing=[(r['location_m'][0]-c[0],r['location_m'][1]-c[1],2.6 if r['kind']=='crop' else 4) for r in instances if r['settlement']==s and r['kind'] in ['crop','orchard']]
 for _ in range(1500):
  x=rng.uniform(-radius,radius);y=rng.uniform(-radius,radius);d=math.hypot(x,y)
  if d>radius or d<radius*.52 or nearest(s,x,y)<5:continue
  if s=='Stonegate' and d>77:continue
  if any(ss==s and math.hypot(x-bx,y-by)<rr+4 for ss,bx,by,rr in occupied):continue
  if any(math.hypot(x-bx,y-by)<rr+3 for bx,by,rr in existing):continue
  add(s,'BroadTree5m',x,y,rng.uniform(0,360),rng.uniform(1.25,1.85),kind='grove_edge');existing.append((x,y,4))
  for j in range(3):add(s,'ShrubGroundcover',x+rng.uniform(-3,3),y+rng.uniform(-3,3),rng.uniform(0,360),rng.uniform(.85,1.5),kind='grove_understory')

# Physical civic terrace and a distinct 17m masonry bell tower.
g=Geo('CivicTerrace','stone');g.box(300,304,24,48,37,1.5);g.save()
g=Geo('CivicTerraceSurface','paving');g.face([[276,285.5,25.51],[324,285.5,25.51],[324,322.5,25.51],[276,322.5,25.51]]);g.save()
g=Geo('CivicRamp','stone');g.face([[297.5,275,24],[302.5,275,24],[302.5,285.5,25.5],[297.5,285.5,25.5]])
g.face([[297.5,275,24],[297.5,285.5,25.5],[297.5,285.5,24]])
g.face([[302.5,275,24],[302.5,285.5,24],[302.5,285.5,25.5]])
g.save()
g=Geo('BellTowerStone','stone');tx,ty,tz=284,307,25.5
g.box(tx,ty,tz,5.8,5.8,.7);g.box(tx,ty,tz+.7,4.8,4.8,10.6)
for h in [3.5,7,10.8,14.7]:g.box(tx,ty,tz+h,5.2,5.2,.25)
for dx in [-1.88,1.88]:
 for dy in [-1.88,1.88]:g.box(tx+dx,ty+dy,tz+11,1.04,1.04,3.9)
g.box(tx,ty,tz+14.8,5.3,5.3,.5)
# Buttresses and small individual stone blocks break the large shaft silhouette.
for dx in [-2.48,2.48]:
 for dy in [-1.6,1.6]:g.box(tx+dx,ty+dy,tz+.7,.7,.85,4.2)
for h in range(20):
 for sx in [-1,1]:
  for sy in [-1,1]:g.box(tx+sx*2.1,ty+sy*2.1,tz+1+h*.48,.8,.8,.40)
g.save()
g=Geo('BellTowerRoof','roof');p=[[tx-3,ty-3,tz+15.3],[tx+3,ty-3,tz+15.3],[tx+3,ty+3,tz+15.3],[tx-3,ty+3,tz+15.3]]
for a,b in zip(p,p[1:]+p[:1]):g.face([a,b,[tx,ty,tz+18]])
g.save()
# Stonegate entrance gets real 9m gate bastions, not enlarged miniature props.
g=Geo('StonegateBastions','stone')
for x in [-329,-311]:
 g.box(x,311,35,5,6,8)
 for dx in [-2,0,2]:
  for dy in [-2.5,2.5]:g.box(x+dx,311+dy,43,1,1,1)
g.save()

data={'revision':6,'map':'/Game/Terrarium/WorldExpansion/Maps/ValleyRegion','assets':assets,'centers':centers,'placements':placements,'instances':instances,'routes':routes,'geometry':geometries,'summary':{'buildings':sum(p['kind']=='building' for p in placements),'actors':len(placements),'detail_instances':len(instances),'by_settlement':dict(Counter(p['settlement'] for p in placements)),'detail_kinds':dict(Counter(p['kind'] for p in instances))}}
(D/'layout.json').write_text(json.dumps(data,indent=2));print(json.dumps(data['summary']))
