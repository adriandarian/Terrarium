"""Deterministic 1.6 km Terrarium valley source; metres, Z-up, no editor dependency."""
import math
import json
import random
import hashlib
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'SourceAssets/WorldExpansion/Terrain'
PADS = [
    {'name':'StartingHome','center':[0,0,5.6],'radius':42},
    {'name':'Alderhaven','center':[300,260,24],'radius':125},
    {'name':'Brookmere','center':[-220,180,16],'radius':65},
    {'name':'Reedbank','center':[280,-300,12],'radius':65},
    {'name':'Highfield','center':[-340,-310,22],'radius':65},
    {'name':'Stonegate','center':[-320,390,35],'radius':95},
]
ROADS = [
    {'name':'HomeApproach','width':4,'points':[[-12.9179,26.9575,5.6],[-25,55,5.6]]},
    {'name':'CityRoad','width':6,'points':[[-25,55,5.6],[35,65,6],[75,65,7.6],[155,95,11],[220,100,17],[300,138,24],[300,260,24]]},
    {'name':'BrookmereRoad','width':4.5,'points':[[-25,55,5.6],[-85,50,8],[-150,110,12],[-158,180,16],[-220,180,16]]},
    {'name':'ReedbankRoad','width':5,'points':[[155,95,11],[175,-50,9],[160,-170,8],[200,-220,9],[280,-238,12],[280,-300,12]]},
    {'name':'HighfieldRoad','width':4.5,'points':[[-85,50,8],[-85,-95,8],[-180,-160,13],[-260,-240,18],[-278,-310,22],[-340,-310,22]]},
    {'name':'StonegateRoad','width':5,'points':[[-220,180,16],[-220,242,16],[-245,265,25],[-275,280,30],[-320,296,35],[-320,390,35]]},
    {'name':'WesternTradeRoad','width':4.5,'points':[[-220,180,16],[-282,180,16],[-330,80,19],[-360,-60,24],[-385,-180,25],[-340,-248,22],[-340,-310,22]]},
    {'name':'EasternTradeRoad','width':6,'points':[[300,260,24],[422,260,24],[460,140,19],[430,-10,16],[385,-160,15],[342,-300,12],[280,-300,12]]},
]

def smooth(a,b,v):
    t=max(0,min(1,(v-a)/(b-a)))
    return t*t*(3-2*t)

def river_center_x(y):
    return 91+49*math.sin(y/190)+18*math.sin(y/83)

def river_halfwidth(y):
    return 10+2.0*math.sin(y/105)+1.2*math.cos(y/49)

def segment_info(x,y,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)))
    return math.hypot(x-a[0]-dx*t,y-a[1]-dy*t),a[2]+(b[2]-a[2])*t,t

def road_info(x,y):
    best=(1e9,0,0,'')
    for r in ROADS:
        for a,b in zip(r['points'],r['points'][1:]):
            d,z,t=segment_info(x,y,a,b)
            if d<best[0]:best=(d,z,r['width'],r['name'])
    return best

def height_m(x,y):
    # Broad connected basin, interrupted ridges and varied angular summits.
    z=8+3.2*math.sin(x/135)*math.cos(y/167)+2.1*math.sin((x+y)/83)
    peaks=[(-665,560,208,175,220),(-440,705,260,180,145),(5,735,180,180,140),
           (485,650,225,190,155),(740,245,205,125,225),(670,-540,190,180,210),
           (-720,-380,190,140,230),(-440,-720,160,190,135)]
    for px,py,h,sx,sy in peaks:
        q=math.sqrt(((x-px)/sx)**2+((y-py)/sy)**2)
        z+=h*max(0,1-q/1.85)**2
    relief=smooth(24,70,z)
    z+=relief*(9*math.sin(x/28)*math.cos(y/36)+5*math.sin((x-y)/17))
    z+=.7*math.sin(x/23)*math.sin(y/19)+.25*math.sin((x+y)/7)
    for p in PADS:
        px,py,pz=p['center'];d=math.hypot(x-px,y-py)
        blend=1-smooth(p['radius'],p['radius']+32,d)
        z=z*(1-blend)+pz*blend
    d,rz,w,_=road_info(x,y)
    blend=1-smooth(w/2+5,w/2+19,d)
    z=z*(1-blend)+rz*blend
    # River remains unbroken beneath explicit road bridges.
    channel=abs(x-river_center_x(y));half=river_halfwidth(y)
    # At high mountain elevations, a fixed 17 m bank produced an artificial
    # vertical slot. Widen only distant mountain reaches; inhabited valley,
    # validated routes, and the home tributary retain their original heights.
    distant=smooth(420,560,abs(y))
    expansion=max(0,z-18)*1.8*distant
    bank_width=17+expansion
    if channel<half+bank_width:
        mix=1-smooth(half-2,half+bank_width,channel)
        original_bed=-1.7+.22*math.sin(y/35)+1.5*(channel/max(half,1))**2
        broad_bed=-1.7+.22*math.sin(y/35)+1.5*min(1,channel/max(half,1))**2
        blend=smooth(0,12,expansion)
        bed=original_bed*(1-blend)+broad_bed*blend
        z=z*(1-mix)+bed*mix
    # The inherited homestead sits above this underlay, preserving its terraces.
    core=max(abs(x)/40,abs(y)/45)
    if core<1.5:
        blend=1-smooth(1,1.5,core)
        z=z*(1-blend)+(-2)*blend
    # Outside the measured original home bounds, roads must take precedence
    # over the protective underlay. Otherwise its feathering cuts a hollow
    # beneath CityRoad along the north edge of the inherited home.
    if core<1.5 and (abs(x)>43 or abs(y)>44):
        d,rz,w,_=road_info(x,y)
        blend=1-smooth(w/2+5,w/2+19,d)
        # Retain the deliberately excavated river underneath the stone bridge.
        if channel>half+12:
            z=z*(1-blend)+rz*blend
    # Support the existing path exit continuously across the inherited boundary.
    if -34<x<-6 and 24<y<65:
        d,rz,_=segment_info(x,y,ROADS[0]['points'][0],ROADS[0]['points'][1])
        blend=1-smooth(4,9,d)
        z=z*(1-blend)+rz*blend
    # East-flowing home stream joins the new main river at the same elevation.
    if 37<x<92 and -27<y<5:
        d,_,_=segment_info(x,y,[37,-9,0],[river_center_x(-12),-12,0])
        blend=1-smooth(4.5,11,d)
        z=z*(1-blend)-1.45*blend
    return z

def srgb(h):
    return [((int(h[i:i+2],16)/255+.055)/1.055)**2.4 for i in (0,2,4)]

PALETTE={k:srgb(v) for k,v in {'grass':'788349','meadow':'899456','moss':'667147','stone':'929181','darkstone':'666e67','scree':'b3b1a0','bank':'a99775','snow':'d4d9cb','road':'bbaa81','water':'3c8884'}.items()}

def tint(x,y,z):
    slope=math.hypot(height_m(x+1,y)-height_m(x-1,y),height_m(x,y+1)-height_m(x,y-1))/2
    channel=abs(x-river_center_x(y))
    key='grass'
    if math.sin(x/31)+math.sin(y/45)>0.5:key='meadow'
    if slope>.5:key='stone'
    if slope>.95:key='darkstone'
    if z>125 and slope<.6:key='scree'
    if z>192 and slope<1.2:key='snow'
    if channel<river_halfwidth(y)+9:key='bank'
    factor=1+.035*math.sin(x*1.8+y*2.3)+.065*math.sin(x/12)*math.cos(y/15)
    return [round(c*factor,5) for c in PALETTE[key]]

def save_geometry(name,vertices,triangles,colors,kind,collision=True):
    row={'name':name,'kind':kind,'units':'meters','vertices':vertices,'triangles':triangles,'colors':colors,'collision':collision}
    path=OUT/(name+'.json');path.write_text(json.dumps(row,separators=(',',':')))
    return {'name':name,'kind':kind,'source':path.relative_to(ROOT).as_posix(),'vertices':len(vertices),'triangles':len(triangles),'collision':collision,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def terrain_tiles():
    rows=[]
    for tx in range(8):
        for ty in range(8):
            x0=-800+tx*200;y0=-800+ty*200;n=41;vs=[];cs=[];ts=[]
            for j in range(n):
                for i in range(n):
                    x=x0+i*5;y=y0+j*5;z=height_m(x,y)
                    vs.append([x,y,round(z,4)]);cs.append(tint(x,y,z))
            for j in range(n-1):
                for i in range(n-1):
                    if -65<x0+i*5+2.5<65 and -65<y0+j*5+2.5<65:continue
                    a=j*n+i;b=a+1;c=a+n;d=c+1
                    ts.extend([[a,b,d],[a,d,c]] if (i+j)%2 else [[a,b,c],[b,d,c]])
            rows.append(save_geometry(f'Terrain_{tx}_{ty}',vs,ts,cs,'terrain'))
    return rows

def home_apron():
    """Fine ground transition matched to the measured pilot perimeter."""
    site=json.loads((ROOT/'Docs/HomesteadPilot/site-details.json').read_text())
    grass=[(t['location'][0]/100,t['location'][1]/100,t['location'][2]/100)
           for c in site['components'] if 'GrassTerrain' in c['mesh'] for t in c['instances']]
    waterdata=json.loads((ROOT/'Docs/HomesteadPilot/RemainingEnvironment/unreal-validation.json').read_text())
    wet=[(t['translation'][0]/100,t['translation'][1]/100) for g in waterdata['groups'] for t in g['before']]
    cells={(round(x/.72),round(y/.72)):(x,y,z) for x,y,z in grass}
    edge=[p for (i,j),p in cells.items() if any((i+di,j+dj) not in cells for di,dj in [(1,0),(-1,0),(0,1),(0,-1)])]
    points=sorted(set((round(x+dx,3),round(y+dy,3)) for x,y,z in grass for dx,dy in [(-.369,-.369),(-.369,.369),(.369,-.369),(.369,.369)]))
    def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lower=[];upper=[]
    for p in points:
        while len(lower)>=2 and cross(lower[-2],lower[-1],p)<=0:lower.pop()
        lower.append(p)
    for p in reversed(points):
        while len(upper)>=2 and cross(upper[-2],upper[-1],p)<=0:upper.pop()
        upper.append(p)
    hull=lower[:-1]+upper[:-1]
    def profile(x,y):
        baseline=rendered_height_m(x,y)
        if abs(x)==65 or abs(y)==65:return baseline
        inside=all(cross(a,b,(x,y))>=0 for a,b in zip(hull,hull[1:]+hull[:1]))
        boundary=min(segment_info(x,y,[*a,0],[*b,0])[0] for a,b in zip(hull,hull[1:]+hull[:1]))
        if inside and boundary>=2:return -2
        nearest=sorted(edge,key=lambda p:(p[0]-x)**2+(p[1]-y)**2)[:5]
        distance=math.hypot(nearest[0][0]-x,nearest[0][1]-y)
        weights=[1/(.3+(p[0]-x)**2+(p[1]-y)**2)**2 for p in nearest]
        target=sum(w*p[2] for w,p in zip(weights,nearest))/sum(weights)-.24
        # Wet edge samples keep both ends of the inherited stream exposed.
        wetdistance=min(math.hypot(x-px,y-py) for px,py in wet)
        if wetdistance<2.1:target=-1.3
        blend=1-smooth(2,22,distance)
        z=baseline*(1-blend)+target*blend
        if inside:z=target*(1-smooth(0,2,boundary))-2*smooth(0,2,boundary)
        # Preserve all verified paths exactly, outside the original interior.
        rd,rz,rw,_=road_info(x,y)
        if not inside or (x<-6 and y>24):
            rb=1-smooth(rw/2+3,rw/2+10,rd);z=z*(1-rb)+rz*rb
        if 37<x<92 and -27<y<5:
            d,_,_=segment_info(x,y,[37,-9,0],[river_center_x(-12),-12,0])
            blend=1-smooth(4.8,9,d);z=z*(1-blend)-1.45*blend
        # One perimeter interval transitions to the exact coarse-mesh edge.
        feather=smooth(60,65,max(abs(x),abs(y)))
        return z*(1-feather)+baseline*feather
    vs=[];cs=[];ts=[];n=131
    for j in range(n):
        for i in range(n):
            x=-65+i;y=-65+j;z=profile(x,y)
            vs.append([x,y,round(z,4)]);cs.append(tint(x,y,z))
    for j in range(n-1):
        for i in range(n-1):
            a=j*n+i;b=a+1;c=a+n;d=c+1;ts.extend([[a,b,d],[a,d,c]])
    row=save_geometry('HomeApron',vs,ts,cs,'terrain')
    (OUT/'apron-profile.json').write_text(json.dumps({'source_grass_tiles':len(grass),'boundary_samples':len(edge),'hull_m':hull,'grid_m':1,'bounds_m':[-65,-65,65,65],'inherited_terrain_untouched':True,'coarse_mesh_cutout':True},indent=2))
    return row

def ribbon(name,points,width,kind):
    vs=[];cs=[];ts=[];samples=[]
    for segment,(a,b) in enumerate(zip(points,points[1:])):
        length=math.hypot(b[0]-a[0],b[1]-a[1]);steps=max(1,math.ceil(length/2.5))
        dx=-(b[1]-a[1])/length*width/2;dy=(b[0]-a[0])/length*width/2
        for i in range(steps+1):
            t=i/steps;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t
            z=a[2]+(b[2]-a[2])*t+.08
            idx=len(vs);vs.extend([[x-dx,y-dy,z],[x+dx,y+dy,z]])
            cs.extend([PALETTE['road'],PALETTE['road']])
            if i:ts.extend([[idx-2,idx,idx-1],[idx-1,idx,idx+1]])
            if i%max(1,steps//4)==0:samples.append({'location_m':[x,y,z],'kind':'route','route':name})
    return save_geometry(name,vs,ts,cs,kind),samples

def water():
    vs=[];ts=[];cs=[]
    for i in range(641):
        y=-800+i*2.5;x=river_center_x(y);w=river_halfwidth(y)+1.0
        vs.extend([[x-w,y,.05],[x+w,y,.05]])
        cs.extend([PALETTE['water'],PALETTE['water']])
        if i: a=i*2;ts.extend([[a-2,a-1,a],[a-1,a+1,a]])
    return save_geometry('AlderRiver',vs,ts,cs,'water',False)

def tributary():
    vs=[];ts=[];cs=[]
    for i in range(25):
        t=i/24;x=35.5+(river_center_x(-12)-35.5)*t;y=-9-3*t
        vs.extend([[x,y-7.5,.05],[x,y+7.5,.05]]);cs.extend([PALETTE['water']]*2)
        if i:a=i*2;ts.extend([[a-2,a,a-1],[a-1,a,a+1]])
    return save_geometry('HomeTributary',vs,ts,cs,'water',False)

def forests():
    rng=random.Random(7433);points=[];tries=0
    while len(points)<2200 and tries<50000:
        tries+=1;x=rng.uniform(-690,690);y=rng.uniform(-690,690);z=height_m(x,y)
        if z<3 or z>133 or max(abs(x),abs(y))<76:continue
        if any(math.hypot(x-p['center'][0],y-p['center'][1])<p['radius']+18 for p in PADS):continue
        if road_info(x,y)[0]<13 or abs(x-river_center_x(y))<river_halfwidth(y)+10:continue
        if math.hypot(height_m(x+2,y)-height_m(x-2,y),height_m(x,y+2)-height_m(x,y-2))/4>.6:continue
        if math.sin(x/57)*math.cos(y/73)+.5*math.sin((x+y)/43)<-.1:continue
        points.append({'location_m':[round(x,3),round(y,3),round(rendered_height_m(x,y)-.08,3)],'scale':round(rng.uniform(.85,1.7),3),'yaw':rng.uniform(0,360)})
    return points

def rendered_height_m(x,y):
    """Barycentric height on the exact 5 m alternating terrain triangulation."""
    i=math.floor((x+800)/5);j=math.floor((y+800)/5)
    x0=-800+i*5;y0=-800+j*5;fx=(x-x0)/5;fy=(y-y0)/5
    a,b,c,d=[round(height_m(xx,yy),4) for xx,yy in [(x0,y0),(x0+5,y0),(x0,y0+5),(x0+5,y0+5)]]
    if (i+j)%2:
        return a+(b-a)*(fx-fy)+(d-a)*fy if fy<=fx else a+(d-a)*fx+(c-a)*(fy-fx)
    return a+(b-a)*fx+(c-a)*fy if fx+fy<=1 else d+(c-d)*(1-fx)+(b-d)*(1-fy)

def bridges():
    vs=[];ts=[];cs=[];sites=[]
    def box(cx,cy,z0,z1,length,width,yaw):
        base=len(vs);c=math.cos(yaw);s=math.sin(yaw)
        for z in [z0,z1]:
            for x,y in [(-length/2,-width/2),(length/2,-width/2),(length/2,width/2),(-length/2,width/2)]:
                vs.append([cx+x*c-y*s,cy+x*s+y*c,z]);cs.append(PALETTE['stone'])
        faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
        for f in faces:ts.extend([[base+f[0],base+f[1],base+f[2]],[base+f[0],base+f[2],base+f[3]]])
    for r in ROADS:
        for a,b in zip(r['points'],r['points'][1:]):
            length=math.hypot(b[0]-a[0],b[1]-a[1]);n=math.ceil(length)
            active=[]
            for i in range(n+1):
                t=i/n;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t
                if abs(x-river_center_x(y))<river_halfwidth(y)+12:active.append(t)
            if not active:continue
            lo,hi=min(active),max(active);yaw=math.atan2(b[1]-a[1],b[0]-a[0]);nx=-math.sin(yaw);ny=math.cos(yaw)
            sites.append({'road':r['name'],'from_m':[a[k]+(b[k]-a[k])*lo for k in range(3)],'to_m':[a[k]+(b[k]-a[k])*hi for k in range(3)]})
            segments=max(1,math.ceil((hi-lo)*length/2))
            for j in range(segments):
                t=lo+(hi-lo)*(j+.5)/segments;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t;z=a[2]+(b[2]-a[2])*t
                box(x,y,z-.8,z+.02,(hi-lo)*length/segments+.08,r['width']+.65,yaw)
                for side in [-1,1]:box(x+nx*(r['width']/2+.25)*side,y+ny*(r['width']/2+.25)*side,z,z+.8,(hi-lo)*length/segments+.02,.4,yaw)
                if j%5==0:box(x,y,-1.6,z-.65,1.4,r['width']+.5,yaw)
    return save_geometry('RiverStoneBridges',vs,ts,cs,'bridge'),sites

def texture():
    rng=random.Random(60117);size=256;data=bytearray()
    for y in range(size):
        for x in range(size):
            grain=rng.uniform(-.13,.13)
            veins=.07*math.sin(x*.3+math.sin(y*.12)*4)+.035*math.sin((x+y)*.73)
            v=int(255*max(.4,min(.97,.82+grain+veins)))
            data.extend((int(v*.95),v,min(255,int(v*1.025))))
    (OUT/'T_ValleyMineral.tga').write_bytes(struct.pack('<BBBHHBHHHHBB',0,0,2,0,0,0,0,0,size,size,24,32)+data)

def generate():
    OUT.mkdir(parents=True,exist_ok=True);rows=terrain_tiles();samples=[]
    for road in ROADS:
        row,ss=ribbon(road['name'],road['points'],road['width'],'road');rows.append(row);samples+=ss
    rows.append(water());rows.append(tributary());bridge,sites=bridges();rows.append(bridge);rows.append(home_apron());texture()
    manifest={'version':1,'seed':60117,'coordinate_system':'meters Z-up; Unreal cm = value*100; winding source CCW, Unreal reversed',
              'bounds_m':[-800,-800,800,800],'terrain_grid_m':5,'home_apron_grid_m':1,'tile_size_m':200,'pads':PADS,'roads':ROADS,
              'assets':rows,'route_samples':samples,'bridges':sites,'forest_instances':forests(),'texture':'SourceAssets/WorldExpansion/Terrain/T_ValleyMineral.tga',
              'notes':['Original homestead actors remain untouched; measured perimeter apron replaces central 130m coarse surface and keeps the interior below original terraces.',
                       'Road ribbons are collidable and span river as bridges; settlement integration supplies bridge structures.',
                       'All terrain has real triangles and complex collision; runtime optimization and streaming remain future work.']}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps({'assets':len(rows),'triangles':sum(r['triangles'] for r in rows),'manifest':str(OUT/'manifest.json')}))

if __name__=='__main__':generate()
