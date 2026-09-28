"""Deterministic, human-scale town planning; pure Python, no editor mutation."""
import json, math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Docs/WorldExpansion/settlement-layout.json'
MAP = '/Game/Terrarium/WorldExpansion/Maps/ValleyRegion'
SETTLEMENTS = {
    'Alderhaven': {'center_m': [300,260,24], 'radius_m':125, 'role':'Regional city: civic square, market, garden ward, artisan ward'},
    'Stonegate': {'center_m':[-320,390,35], 'radius_m':95, 'role':'Fortified upland town and southern gate'},
    'Brookmere': {'center_m':[-220,180,16], 'radius_m':65, 'role':'Orchard village and market green'},
    'Reedbank': {'center_m':[280,-300,12], 'radius_m':65, 'role':'Lowland trading village and kitchen gardens'},
    'Highfield': {'center_m':[-340,-310,22], 'radius_m':65, 'role':'Wheat farming village below the mountain pass'},
}
assets = {}
for source, field in [('Architecture/unreal-import.json','meshes'),('Landscape/unreal-import.json','meshes'),('RemainingArt/unreal-integration.json','assets')]:
    for row in json.loads((ROOT/'Docs/HomesteadPilot'/source).read_text())[field]:
        assets[row['name']] = row['mesh']
placements, instances, roads, viewpoints = [], [], [], []

def add(s, district, asset, x, y, yaw=0, scale=1, kind='building', instance=False, zoffset=0):
    center=SETTLEMENTS[s]['center_m']; scale=[scale]*3 if isinstance(scale,(int,float)) else list(scale)
    row={'label':f'WX_{s}_{asset}_{len(placements)+len(instances):05d}', 'settlement':s,
         'district':district,'asset':asset,'location_m':[center[0]+x,center[1]+y,center[2]+zoffset],
         'yaw_deg':yaw,'scale':scale,'kind':kind}
    (instances if instance else placements).append(row)
    return row

def pave(s,district,x,y,w,h):
    # Actual authored cobble modules. Thickness remains small; terrain carries collision.
    nx=max(1,math.ceil(w/4));ny=max(1,math.ceil(h/4))
    for ix in range(nx):
        for iy in range(ny):
            add(s,district,'WornPath2m',x-w/2+(ix+.5)*w/nx,y-h/2+(iy+.5)*h/ny,
                scale=(w/nx/2,h/ny/2,.45),kind='paving',instance=True,zoffset=.015)

def street(s,district,x1,y1,x2,y2,width):
    assert x1==x2 or y1==y2
    pave(s,district,(x1+x2)/2,(y1+y2)/2,abs(x2-x1) or width,abs(y2-y1) or width)
    c=SETTLEMENTS[s]['center_m']
    roads.append({'settlement':s,'district':district,'width_m':width,
                  'points_m':[[c[0]+x1,c[1]+y1,c[2]],[c[0]+x2,c[1]+y2,c[2]]]})

def frontage(s,district,x,y,asset='Cottage',scale=1):
    # Imported Blender front is local +Y (FBX Y flip confirmed by native bounds).
    # Face nearest horizontal street. Offset entrance path stops at the facade.
    yaw=180 if y>0 else 0
    add(s,district,asset,x,y,yaw,scale)
    sign=-1 if y>0 else 1
    add(s,district,'GardenPatch2m',x+4.5,y,scale=.9,kind='garden',instance=True)
    add(s,district,'ShrubGroundcover',x-3.8,y+sign*2.6,scale=.75,kind='planting',instance=True)

def square(s,size=30):
    pave(s,'MarketSquare',0,0,size,size)
    for x in [-10,10]:
        for y in [-9,9]:
            add(s,'MarketSquare','MarketStall',x,y,90 if x>0 else -90,.9,kind='market')
    for x in [-17,17]:
        for y in [-17,17]:
            add(s,'MarketSquare','BroadTree5m',x,y,scale=1.08,kind='tree',instance=True)
            add(s,'MarketSquare','Lantern',x+(1.8 if x<0 else -1.8),y,scale=.85,kind='street_furniture',instance=True)
    add(s,'MarketSquare','Sign',-6,-18,scale=.8,kind='wayfinding',instance=True)

# Main city: four compact wards are separated by cross streets; square remains open.
s='Alderhaven';square(s,36)
for sx in [-1,1]:
    for sy in [-1,1]:
        district={(-1,1):'ArtisanWard',(1,1):'GardenWard',(-1,-1):'OldTown',(1,-1):'MerchantWard'}[(sx,sy)]
        for ix,x0 in enumerate([30,44,58,72]):
            for iy,y0 in enumerate([30,44,58,72]):
                key='HomesteadCompound' if district=='GardenWard' and (ix+iy)%3==0 else ('Lodge' if (ix+iy)%4==0 else 'Cottage')
                frontage(s,district,sx*x0,sy*y0,key,1 if key!='Lodge' else 1.05)
        for offset in [21,51,81]:
            street(s,district,sx*offset,sy*20,sx*offset,sy*84,4)
            street(s,district,sx*20,sy*offset,sx*84,sy*offset,4)
for side in [-1,1]:
    for q in [-60,-45,-30,30,45,60]:
        frontage(s,'OuterWard',q,side*94,'Cottage')
        add(s,'OuterWard','Lodge' if q in [-30,30] else 'Cottage',side*94,q,90 if side>0 else -90)
    street(s,'OuterWard',-82,side*86,82,side*86,5)
    street(s,'OuterWard',side*86,-82,side*86,82,5)
    for q in [-72,-44,44,72]:
        add(s,'Boulevards','BroadTree5m',side*9,q,kind='tree',instance=True)
        add(s,'Boulevards','Lantern',q,side*5,scale=.85,kind='street_furniture',instance=True)
add(s,'CivicQuarter','CivicHall',0,34,180,1.12)
add(s,'CivicQuarter','Tower',-13,34,scale=1.1)
add(s,'CivicQuarter','Tower',13,34,scale=1.1)
add(s,'CivicQuarter','CivicHall',0,70,180,1)
add(s,'GuildQuarter','Lodge',-34,10,180,1.1)
add(s,'GuildQuarter','Lodge',34,10,180,1.1)
for x in [-62,-48,48,62]:add(s,'GuildQuarter','Cottage',x,10,180)
street(s,'GrandAvenue',-122,0,122,0,7)
street(s,'SouthAvenue',0,-122,0,-19,7)
street(s,'CivicWalk',0,19,0,29,7)
for x in [-9,9]:street(s,'CivicWalk',x,42,x,86,3)

# Stonegate: urban courtyard blocks enclosed by a readable octagonal stone wall.
s='Stonegate';square(s,28)
for sx in [-1,1]:
    for sy in [-1,1]:
        for ix,x in enumerate([26,40,54]):
            for iy,y in enumerate([26,40,54]):
                frontage(s,'InnerTown',sx*x,sy*y,'Lodge' if (ix+iy)%4==0 else 'Cottage')
        for offset in [18,47,70]:
            street(s,'InnerTown',sx*offset,sy*17,sx*offset,sy*60,4)
        for offset in [18,47,62]:street(s,'InnerTown',sx*17,sy*offset,sx*70,sy*offset,4)
add(s,'CivicCourt','CivicHall',0,35,180,1.04)
for side in [-1,1]:
    for x in [-40,-26,26,40]:frontage(s,'OuterTown',x,side*68,'Cottage')
for x in [-32,-18,18,32]:add(s,'SouthGate','Lodge',x,-72,0)
for x in [-8,8]:add(s,'SouthGate','Tower',x,-79,0,1.15)
street(s,'GateStreet',0,-94,0,-15,6)
street(s,'CrossStreet',-90,0,90,0,6)
# Native authored moss modules maintain stone detail, each wall 4m long and 1m thick.
vertices=[(90*math.cos(a*math.pi/4+math.pi/8),90*math.sin(a*math.pi/4+math.pi/8)) for a in range(8)]
for p,q in zip(vertices,vertices[1:]+vertices[:1]):
    length=math.dist(p,q);n=math.ceil(length/4)
    for i in range(n):
        t=(i+.5)/n;x=p[0]+t*(q[0]-p[0]);y=p[1]+t*(q[1]-p[1])
        # Four gates stay clear of roads, including south arrival.
        if abs(x)<5.5 or abs(y)<5.5:continue
        add(s,'CurtainWall','MossCliff4m',x,y,math.degrees(math.atan2(q[1]-p[1],q[0]-p[0])),
            (length/n/4,.26,1.35),kind='wall',instance=True)
for x,y in vertices:add(s,'CurtainWall','Tower',x,y,scale=1.08)

# Villages: green, short lanes, gardens and planted fields have deliberate boundaries.
for s in ['Brookmere','Reedbank','Highfield']:
    pave(s,'VillageGreen',0,0,22,22)
    street(s,'VillageLane',-62,0,62,0,4)
    street(s,'VillageLane',0,-62,0,62,4)
    for sy in [-1,1]:
        for x in [-34,-20,20,34]:
            for y in [19,34]:
                frontage(s,'Homes',x,sy*y,'Cottage' if (x+y)%3 else 'Lodge',.97)
        street(s,'VillageLane',-42,sy*26,42,sy*26,3)
    add(s,'VillageGreen','Lodge',0,20,180)
    add(s,'VillageGreen','MarketStall',-8,5,-90,.85,kind='market')
    add(s,'VillageGreen','MarketStall',8,5,90,.85,kind='market')
    add(s,'VillageGreen','Tower',-8,-8,scale=.82)
    add(s,'VillageGreen','Sign',4,-9,scale=.8,kind='wayfinding',instance=True)
    for x in [-11,11]:add(s,'VillageGreen','Lantern',x,-4,scale=.8,kind='street_furniture',instance=True)
    for x in [-45,45]:
        for y in [-35,-23,23,35]:add(s,'Orchard','BroadTree5m',x,y,scale=1.05,kind='tree',instance=True)
    # Highfield reads as an agricultural settlement; other villages have gardens.
    for ix in range(9):
        for iy in range(4):
            x=-10+ix*2.5;y=-46+iy*2.5
            add(s,'Fields','WheatPatch2m' if s=='Highfield' else 'GardenPatch2m',x,y,kind='field',instance=True)

for s,row in SETTLEMENTS.items():
    x,y,z=row['center_m'];r=row['radius_m']
    viewpoints.append({'name':s+'_Overview','location_m':[x-r*.85,y-r*1.3,z+r*.75], 'target_m':[x,y,z+3]})
    viewpoints.append({'name':s+'_Arrival','location_m':[x+7,y-42,z+2], 'target_m':[x,y+8,z+3]})

# Reject accidental footprint intersections and structures outside flattened pads.
building_rows=[r for r in placements if r['kind']=='building']
for row in placements+instances:
    c=SETTLEMENTS[row['settlement']]['center_m'];r=SETTLEMENTS[row['settlement']]['radius_m']
    assert math.dist(row['location_m'][:2],c[:2])<=r+.1,(row['label'],'outside settlement pad')
for i,a in enumerate(building_rows):
    for b in building_rows[i+1:]:
        if a['settlement']==b['settlement']:
            assert math.dist(a['location_m'][:2],b['location_m'][:2])>=7,(a['label'],b['label'])
data={'map':MAP,'coordinate_system':'Unreal metres, Z-up; mesh front local +Y after FBX Y flip',
      'ground_anchor':'location_m is requested bottom; integrator subtracts native bounds.min.z * scale.z',
      'source_policy':'Reuse admitted HomesteadPilot meshes and shaders; keep original map and meshes unchanged',
      'settlements':SETTLEMENTS,'assets':assets,'placements':placements,'instances':instances,'roads':roads,'viewpoints':viewpoints,
      'summary':{'actors':len(placements),'instances':len(instances),'buildings':len(building_rows),
                 'actors_by_settlement':dict(Counter(r['settlement'] for r in placements)),
                 'instances_by_asset':dict(Counter(r['asset'] for r in instances))}}
OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(data,indent=2))
print(json.dumps(data['summary'],indent=2))
