"""Additive urban infill and courtyard dressing. Run --plan outside the editor.

Default execution integrates only this file's WX_Dressing_ labels/private types;
all previously integrated actors and tested street centre lines remain unchanged.
"""
import json, math, sys
from pathlib import Path
from collections import Counter, defaultdict
ROOT=Path('C:/Users/hello/Projects/Terrarium')
DOC=ROOT/'Docs/WorldExpansion'
data=json.loads((DOC/'settlement-layout.json').read_text())
sources=dict(data['assets'])
sources.update(json.loads((DOC/'settlement-collision-assets.json').read_text())['assets'])
sources['GardenWell']='/Game/Terrarium/Meshes/SM_GardenWell_v2_Detail'
placements=[];instances=[]

def add(asset,x,y,yaw=0,scale=1,kind='detail',instanced=True):
    s=[scale]*3 if isinstance(scale,(int,float)) else list(scale)
    row={'label':f'WX_Dressing_{asset}_{len(placements)+len(instances):05d}',
         'asset':asset,'location_m':[300+x,260+y,24],'yaw_deg':yaw,'scale':s,'kind':kind}
    (instances if instanced else placements).append(row)

# Narrow new frontages occupy unused avenue medians, preserving a 7m carriageway.
new=[]
for x in [-78,-68,-54,-40,-26,26,40,54,68,78]:new.append((x,-10,0))
for x in [-98,-78,78,98]:new.append((x,10,180))
for x in [-10,10]:
    for y in [-30,-58]:new.append((x,y,-90 if x<0 else 90))
for x in [-15,15]:
    new.append((x,56,90 if x<0 else -90))
    new.append((x,100,180))
for x in [-101,101]:
    new.append((x,-14,0))
for i,(x,y,yaw) in enumerate(new):
    add('Cottage' if i%4 else 'Lodge',x,y,yaw,.96,'infill_building',False)
    # Small crafted landing reinforces frontage without stretching the detail mesh.
    a=math.radians(yaw);fx=-math.sin(a);fy=math.cos(a)
    add('WornPath2m',x+fx*3.8,y+fy*3.8,yaw,(1,1,.4),'landing')

# Rear and side courtyard fences give houses individual lots; fronts stay open.
for row in data['placements']:
    if row['settlement']!='Alderhaven' or row['district'] not in ['OldTown','MerchantWard','ArtisanWard','GardenWard']:continue
    if row['asset'] not in ['Cottage','Lodge']:continue
    x=row['location_m'][0]-300;y=row['location_m'][1]-260
    back=1 if row['yaw_deg']==180 else -1
    for dx in [-3,0,3]:add('Fence',x+dx,y+back*4.5,0,(1,1,.74),'courtyard_boundary')
    for side in [-1,1]:add('Fence',x+side*4.5,y+back*2.1,90,(1.4,1,.74),'courtyard_boundary')
    for dx in [-2.7,0,2.7]:add('ShrubGroundcover',x+dx,y+back*3.7,0,(1,.7,.75),'courtyard_hedge')
    add('GardenPatch2m',x-2.6,y+back*3.5,0,.65,'courtyard_garden')

# Low moss stone and planted fronts give the avenue continuous urban edges.
for sign in [-1,1]:
    for x in [-76,-60,-46,-32,32,46,60,76]:
        # Keep narrow breaks between modules; no stone crosses a street centreline.
        add('MossCliff4m',x,sign*16,0,(.78,.18,.30),'avenue_wall')
        add('ShrubGroundcover',x,sign*15.1,0,(1.25,.65,.70),'avenue_hedge')
for x in [-90,90]:
    for y in [-67,-38,38,67]:add('BroadTree5m',x,y,0,.98,'avenue_tree')
for x in [-6.3,6.3]:
    for y in [-88,-80,-51,-23]:add('BroadTree5m',x,y,0,.95,'avenue_tree')
for x in [-75,-57,-43,43,57,75]:add('BroadTree5m',x,-6.5,0,.9,'avenue_tree')

# The existing authored well has a real masonry ring and open lifting frame.
# Its old source receipt marked visual review pending; coordinator inspects new use.
add('GardenWell',0,11,0,1.18,'market_focal',False)
for x in [-5,5]:
    add('MarketStall',x,13,180,.92,'market_stall',False)
    add('Lantern',x,6.5,0,.85,'market_lantern')
for x in [-13,13]:
    for y in [-13,13]:add('GardenPatch2m',x,y,0,1.3,'square_planter')
add('Sign',-4,8,0,.8,'market_wayfinding')

# Reject overlapping infill using minimum centre spacing and preserve world extent.
buildings=[r for r in data['placements'] if r['kind']=='building']
for i,row in enumerate([r for r in placements if r['kind']=='infill_building']):
    assert math.dist(row['location_m'][:2],[300,260])<120
    for old in buildings:
        assert math.dist(row['location_m'][:2],old['location_m'][:2])>=6.5,(row['label'],old['label'])
    buildings.append(row)
    # Conservative square envelope contains each near-unit Lodge/Cottage footprint.
    # Reject intersection with every preexisting authored urban street rectangle.
    rx,ry=row['location_m'][:2]
    for road in data['roads']:
        if road['settlement']!='Alderhaven':continue
        p,q=road['points_m'];w=road['width_m']/2
        x0,x1=min(p[0],q[0])-w,max(p[0],q[0])+w
        y0,y1=min(p[1],q[1])-w,max(p[1],q[1])+w
        assert not (rx+3>x0 and rx-3<x1 and ry+3>y0 and ry-3<y1),(row['label'],'road footprint',road)
plan={'map':data['map'],'assets':sources,'placements':placements,'instances':instances,
      'summary':{'infill_buildings':len(new),'actors':len(placements),'instances':len(instances),
                 'instances_by_asset':dict(Counter(r['asset'] for r in instances))},
      'preservation':'Additive WX_Dressing actors and private foliage only; original settlement and home actors are untouched'}
(DOC/'settlement-dressing-layout.json').write_text(json.dumps(plan,indent=2))
if '--plan' in sys.argv:
    print(json.dumps(plan['summary'],indent=2));raise SystemExit(0)

import unreal
assert Path(unreal.Paths.project_dir()).resolve()==ROOT
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not E.get_game_world() and E.get_editor_world().get_path_name().split('.')[0]==data['map']
world=E.get_editor_world();AT=unreal.AssetToolsHelpers.get_asset_tools()
meshes={k:unreal.load_asset(sources[k]) for k in {r['asset'] for r in placements+instances}}
assert all(meshes.values())
old_labels={a.get_actor_label() for a in A.get_all_level_actors() if not a.get_actor_label().startswith('WX_Dressing_')}
for actor in list(A.get_all_level_actors()):
    if actor.get_actor_label().startswith('WX_Dressing_'):A.destroy_actor(actor)

def transform(row):
    x,y,z=[v*100 for v in row['location_m']];z-=meshes[row['asset']].get_bounding_box().min.z*row['scale'][2]
    if row['asset']=='WornPath2m':z+=2
    return unreal.Transform(location=unreal.Vector(x,y,z),rotation=unreal.Rotator(pitch=0,yaw=row['yaw_deg'],roll=0),scale=unreal.Vector(*row['scale']))

placed=[]
for row in placements:
    t=transform(row);a=A.spawn_actor_from_class(unreal.StaticMeshActor,t.translation);a.set_actor_label(row['label'])
    a.set_folder_path('WorldExpansion/UrbanDressing');a.static_mesh_component.set_static_mesh(meshes[row['asset']]);a.set_actor_transform(t,False,False)
    a.static_mesh_component.set_collision_profile_name('BlockAll');a.static_mesh_component.set_editor_property('forced_lod_model',0)
    placed.append({'label':row['label'],'mesh':meshes[row['asset']].get_path_name(),'location_m':row['location_m']})
groups=defaultdict(list)
for row in instances:groups[row['asset']].append(row)
receipts=[]
for key,rows in groups.items():
    name='FT_WX_Dressing_'+key;folder='/Game/Terrarium/WorldExpansion/DressingFoliage'
    ft=unreal.load_asset(folder+'/'+name) or AT.create_asset(name,folder,unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory())
    ft.set_editor_property('mesh',meshes[key]);body=ft.get_editor_property('body_instance')
    # Decorative courtyard limits do not alter any validated walking corridor.
    body.set_editor_property('collision_profile_name','NoCollision');body.set_editor_property('collision_enabled',unreal.CollisionEnabled.NO_COLLISION)
    ft.set_editor_property('body_instance',body);assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
    unreal.InstancedFoliageActor.remove_all_instances(world,ft)
    before={c.get_path_name():c.get_instance_count() for a in A.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==meshes[key]}
    unreal.InstancedFoliageActor.add_instances(world,ft,[transform(row) for row in rows])
    cs=[c for a in A.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==meshes[key]]
    delta=sum(c.get_instance_count()-before.get(c.get_path_name(),0) for c in cs)
    assert delta==len(rows),(key,delta,len(rows))
    receipts.append({'asset':key,'count':delta,'foliage_type':ft.get_path_name()})
assert old_labels<={a.get_actor_label() for a in A.get_all_level_actors()}
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(DOC/'settlement-dressing-integration.json').write_text(json.dumps({'actors':placed,'instances':receipts,'summary':plan['summary'],
    'original_actor_labels_preserved':True,'validation':'Native count verification and save; visual and traversal confirmation follow.'},indent=2))
print(json.dumps(plan['summary']))
