"""Source-only clustered woodland plan; preserves all existing forest instances."""
import json,math,random,sys
from collections import defaultdict
from pathlib import Path
ROOT=Path('C:/Users/hello/Projects/Terrarium');DOC=ROOT/'Docs/WorldExpansion'
sys.path.insert(0,str(ROOT/'Scripts/WorldExpansion'))
from terrain_source import height_m,river_center_x,river_halfwidth,road_info
rng=random.Random(927505)
old=json.loads((ROOT/'SourceAssets/WorldExpansion/Terrain/manifest.json').read_text())
settlements=json.loads((DOC/'settlement-layout.json').read_text())['settlements']
centers=[(-520,210,64),(-470,55,62),(-500,-140,67),(-245,-70,58),(-205,-425,64),(-80,-315,63),
         (5,305,64),(15,460,60),(205,465,65),(490,350,66),(525,70,64),(465,-285,62),
         (190,-470,62),(465,-435,64),(-475,455,60),(-130,500,66),(-120,70,48),(260,-80,58)]
cells=defaultdict(list)
def cell(x,y):return (math.floor(x/5),math.floor(y/5))
for row in old['forest_instances']:
    x,y,_=row['location_m'];cells[cell(x,y)].append((x,y,3.2))
instances=[];groves=[]
for gi,(cx,cy,radius) in enumerate(centers):
    count=0;phase=rng.uniform(0,math.tau);holes=[(rng.uniform(-radius*.5,radius*.5),rng.uniform(-radius*.5,radius*.5),rng.uniform(4,9)) for _ in range(3)]
    for attempt in range(12000):
        if count>=215:break
        a=rng.uniform(0,math.tau);r=math.sqrt(rng.random())*radius
        edge=.82+.14*math.sin(a*3+phase)+.06*math.sin(a*7)
        x=cx+math.cos(a)*r*edge;y=cy+math.sin(a)*r*edge*.83
        if any(math.hypot(x-cx-hx,y-cy-hy)<hr for hx,hy,hr in holes):continue
        if abs(x)<70 and abs(y)<75:continue
        if any(math.hypot(x-s['center_m'][0],y-s['center_m'][1])<s['radius_m']+14 for s in settlements.values()):continue
        d,_,w,_=road_info(x,y)
        if d<w/2+7:continue
        if abs(x-river_center_x(y))<river_halfwidth(y)+17:continue
        z=height_m(x,y)
        if z<3 or z>88:continue
        slope=math.hypot(height_m(x+1,y)-height_m(x-1,y),height_m(x,y+1)-height_m(x,y-1))/2
        if slope>.48:continue
        s=rng.uniform(.9,1.3);spacing=3.0+s*.5
        ix,iy=cell(x,y)
        if any(math.hypot(x-ox,y-oy)<max(spacing,os) for dx in [-1,0,1] for dy in [-1,0,1] for ox,oy,os in cells.get((ix+dx,iy+dy),[])):continue
        cells[(ix,iy)].append((x,y,spacing));count+=1
        instances.append({'xy_m':[round(x,3),round(y,3)],'scale':round(s,4),'yaw_deg':round(rng.uniform(0,360),3),'grove':gi,'source_ground_hint_m':round(z,3)})
    groves.append({'id':gi,'center_m':[cx,cy],'radius_m':radius,'trees':count,'gaps':[list(h) for h in holes]})
assert 2500<=len(instances)<=4000,len(instances)
result={'map':'/Game/Terrarium/WorldExpansion/Maps/ValleyRegion','seed':927505,
        'mesh':'/Game/Terrarium/WorldExpansion/Forest/SM_WX_BroadTree5m.SM_WX_BroadTree5m',
        'native_canopy_m':[3.68,3.91],'native_height_m':4.992,
        'collision_contract':{'simple_capsules':1,'radius_cm':30,'center_cm':[0,0,130],'cylinder_length_cm':200},
        'instances':instances,'groves':groves,'summary':{'planned_trees':len(instances),'groves':len(groves),'grove_counts':[g['trees'] for g in groves]},
        'preservation':'Existing forest transforms and foliage type untouched; adds one private V5Forest type; roads/pads/home/rivers protected'}
(DOC/'forest-groves-v5-layout.json').write_text(json.dumps(result,indent=2));print(json.dumps(result['summary']))
