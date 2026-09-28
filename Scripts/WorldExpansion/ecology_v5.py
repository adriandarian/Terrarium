"""Deterministic ground-layer ecology, source-only; no Unreal/Blender access.

Writes a new additive layout. It does not alter terrain, prior placements or art.
"""
import json, math, random
from pathlib import Path
from collections import Counter
ROOT=Path('C:/Users/hello/Projects/Terrarium')
DOC=ROOT/'Docs/WorldExpansion'
rng=random.Random(927051)
settlement=json.loads((DOC/'settlement-layout.json').read_text())
terrain=json.loads((ROOT/'SourceAssets/WorldExpansion/Terrain/manifest.json').read_text())
retained=json.loads((ROOT/'Docs/HomesteadPilot/RemainingEnvironment/inherited-lod-validation.json').read_text())
names={'Grass':'SM_MeadowGrass_v2_Detail','GroundPlants':'SM_GroundPlants_v2_Detail',
       'Flowers':'SM_MeadowFlowers_v2_Detail','RockCluster':'SM_RockCluster_Detail',
       'ShoreOutcrop':'SM_ShoreOutcrop_Detail','Bush':'SM_Bush_v2_Detail','MossRock':'SM_Blender_MossRock'}
assets={}
for key,name in names.items():
    row=next(r for r in retained['meshes'] if r['mesh'].split('/')[-1].split('.')[0]==name)
    b=row['source_contract']['bounds']
    assets[key]={'mesh':row['mesh'],'native_bounds_cm':b,'native_dimensions_m':[(b[1][i]-b[0][i])/100 for i in range(3)],
                 'source_triangles':row['triangles']}
for key in ['ShrubGroundcover','GardenPatch2m','WheatPatch2m','MossCliff4m']:
    row=next(r for r in json.loads((ROOT/'Docs/HomesteadPilot/Landscape/unreal-import.json').read_text())['meshes'] if r['name']==key)
    b=row['bounds_cm'];assets[key]={'mesh':row['mesh'],'native_bounds_cm':[b['min'],b['max']],
                                'native_dimensions_m':[v/100 for v in row['dimensions_cm']]}

roads=[]
for r in terrain['roads']:
    for p,q in zip(r['points'],r['points'][1:]):roads.append((p,q,r['width']))
for r in settlement['roads']:
    for p,q in zip(r['points_m'],r['points_m'][1:]):roads.append((p,q,r['width_m']))
buildings=list(settlement['placements'])
dress=DOC/'settlement-dressing-layout.json'
if dress.exists():buildings+=json.loads(dress.read_text())['placements']
exclusions=[(r['location_m'][0],r['location_m'][1],7.2 if r['asset']=='HomesteadCompound' else 5.1 if r['asset'] in ['CivicHall','Cottage','Lodge'] else 2.7) for r in buildings]

def distance_segment(x,y,p,q):
    dx=q[0]-p[0];dy=q[1]-p[1]
    t=max(0,min(1,((x-p[0])*dx+(y-p[1])*dy)/(dx*dx+dy*dy)))
    return math.hypot(x-p[0]-t*dx,y-p[1]-t*dy)

def allowed(x,y,footprint=.3):
    # Keep the complete pilot, apron seam and its front door approaches untouched.
    if abs(x)<53 and abs(y)<53:return False
    for p,q,w in roads:
        if distance_segment(x,y,p,q)<w/2+1.15+footprint:return False
    for bx,by,r in exclusions:
        if math.hypot(x-bx,y-by)<r+footprint:return False
    # Civic/market squares remain deliberately open and readable.
    for s in settlement['settlements'].values():
        cx,cy,_=s['center_m']
        if abs(x-cx)<18+footprint and abs(y-cy)<18+footprint:return False
    if abs(x)>770 or abs(y)>770:return False
    return True

instances=[];occupied={};cluster_receipts=[]
def add(key,x,y,scale=1,yaw=None,zone='',purpose='',embed=None):
    s=[scale]*3 if isinstance(scale,(float,int)) else list(scale)
    dims=assets[key]['native_dimensions_m'];rad=max(dims[0]*s[0],dims[1]*s[1])/2
    if not allowed(x,y,rad):return False
    # Separate tiny ground elements enough to read as distinct, irregular tufts.
    cell=(math.floor(x/.35),math.floor(y/.35),key)
    if cell in occupied:return False
    occupied[cell]=True
    if embed is None:embed=.025 if key in ['Grass','GroundPlants','Flowers'] else .05 if key in ['Bush','ShrubGroundcover'] else .10
    instances.append({'asset':key,'xy_m':[round(x,3),round(y,3)],'scale':[round(v,4) for v in s],
                      'yaw_deg':round(rng.uniform(0,360) if yaw is None else yaw,3),
                      'embed_m':embed,'zone':zone,'purpose':purpose})
    return True

def patch(cx,cy,size,zone,kind):
    start=len(instances);phase=rng.uniform(0,math.tau)
    # Elliptical clusters have lobed margins and mixed low/middle-height layers.
    for i in range(65 if kind=='roadside' else 105):
        a=rng.uniform(0,math.tau);rr=math.sqrt(rng.random())*size
        lobes=.78+.20*math.sin(a*3+phase)
        x=cx+math.cos(a)*rr*lobes;y=cy+math.sin(a)*rr*.62*lobes
        u=rng.random()
        key='Grass' if u<.64 else 'GroundPlants' if u<.81 else 'Flowers' if u<.90 else 'ShrubGroundcover' if u<.97 else 'RockCluster'
        scale=rng.uniform(.72,1.12) if key not in ['ShrubGroundcover','RockCluster'] else rng.uniform(.6,.94)
        add(key,x,y,scale,zone=zone,purpose='irregular_meadow_ground_layer')
    # Offset bush clumps provide visible masses at regional-view scale.
    if kind!='court':
        for i in range(rng.randint(5,10)):
            a=rng.uniform(0,math.tau);rr=rng.uniform(0,size*.42)
            add('Bush',cx+math.cos(a)*rr,cy+math.sin(a)*rr*.7,rng.uniform(.65,1.05),zone=zone,purpose='thicket')
        if rng.random()<.45:
            add('ShoreOutcrop' if rng.random()<.7 else 'MossRock',cx+size*.35,cy-size*.2,rng.uniform(.75,1.1),zone=zone,purpose='moss_stone_cluster')
    if len(instances)>start:cluster_receipts.append({'center_m':[round(cx,3),round(cy,3)],'radius_m':size,'zone':zone,'kind':kind,'accepted_instances':len(instances)-start})

# Ground masses within and around each settlement, with clear cultivated inner lots.
for name,s in settlement['settlements'].items():
    cx,cy,z=s['center_m'];r=s['radius_m']
    clusters=60 if name=='Alderhaven' else 42 if name=='Stonegate' else 30
    for i in range(clusters):
        a=rng.uniform(0,math.tau);radius=rng.uniform(.28,.98)*r
        patch(cx+math.cos(a)*radius,cy+math.sin(a)*radius,rng.uniform(3.8,7.8),name,'court' if radius<r*.65 else 'edge')
    # Broken masonry follows portions of the outer pad, rather than enclosing it
    # in a perfect circle. Stone is only half a metre high at native human scale.
    for run in range(7):
        phase=run*math.tau/7+rng.uniform(-.14,.14)
        for j in range(rng.randint(6,11)):
            a=phase+j*2.65/(r-3);radius=r-3+rng.uniform(-.6,.6)
            x=cx+math.cos(a)*radius;y=cy+math.sin(a)*radius
            add('MossCliff4m',x,y,(.65,.16,.25),math.degrees(a)+90,name,'broken_low_retaining_edge',.10)
            for k in range(4):
                add('Grass',x+rng.uniform(-1.5,1.5),y+rng.uniform(-1.5,1.5),rng.uniform(.8,1.05),zone=name,purpose='stone_edge_tufts')
    # Small planted beds at sheltered side edges, bounded by flowers and tufts.
    if name in ['Brookmere','Reedbank','Highfield']:
        for side in [-1,1]:
            bx=cx+side*44;by=cy+8
            for ix in range(4):
                for iy in range(4):
                    add('WheatPatch2m' if name=='Highfield' else 'GardenPatch2m',bx+ix*2.15,by+iy*2.15,.96,zone=name,purpose='cultivated_field_edge',embed=.01)
            for j in range(24):
                a=j*math.tau/24
                add('Flowers',bx+3+math.cos(a)*6,by+3+math.sin(a)*6,.95,zone=name,purpose='field_border')

# Alternating, irregular thickets and ground tufts along walking connections.
# Keep side offsets varied; the result is habitat patches, never a line of trees.
for road in terrain['roads']:
    for p,q in zip(road['points'],road['points'][1:]):
        dx=q[0]-p[0];dy=q[1]-p[1];length=math.hypot(dx,dy)
        for j in range(max(1,int(length/20))):
            t=(j+.5)/max(1,int(length/20));side=-1 if rng.random()<.5 else 1
            offset=road['width']/2+rng.uniform(6,17)
            x=p[0]+dx*t-dy/length*offset*side;y=p[1]+dy*t+dx/length*offset*side
            patch(x,y,rng.uniform(4.5,8.5),road['name'],'roadside')

manifest={'version':5,'seed':927051,'map':settlement['map'],'assets':assets,'instances':instances,'clusters':cluster_receipts,
          'grounding':'Integrator traces actual collidable current terrain and embeds tiny amounts; no stale analytical heights are used',
          'protection':{'home_exclusion_box_m':[-53,-53,53,53],'street_extra_clearance_m':1.15,'building_clearance_includes_front_door':True,
                        'all_instances_no_collision':True,'original_meshes_materials_and_placements_unchanged':True},
          'summary':{'planned_instances':len(instances),'clusters':len(cluster_receipts),'by_asset':dict(Counter(r['asset'] for r in instances)),
                     'by_zone':dict(Counter(r['zone'] for r in instances))}}
(DOC/'ecology-v5-layout.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest['summary'],indent=2))
