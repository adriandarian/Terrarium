"""Coordinator-only: place authored town plan in verified ValleyRegion editor.

No source mesh/material changes. Private FoliageTypes persist repeated details;
architecture remains individually selectable. Safe rerun replaces only this plan.
"""
import json
from collections import defaultdict
from pathlib import Path
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
assert ROOT==Path('C:/Users/hello/Projects/Terrarium')
DATA=json.loads((ROOT/'Docs/WorldExpansion/settlement-layout.json').read_text())
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not E.get_game_world(), 'Stop PIE before integration'
world=E.get_editor_world()
assert world.get_path_name().split('.')[0]==DATA['map'],world.get_path_name()
DEST='/Game/Terrarium/WorldExpansion/SettlementFoliage'
AT=unreal.AssetToolsHelpers.get_asset_tools()
used={r['asset'] for r in DATA['placements']+DATA['instances']}
meshes={key:unreal.load_asset(DATA['assets'][key]) for key in used}
collision_manifest=ROOT/'Docs/WorldExpansion/settlement-collision-assets.json'
if collision_manifest.exists():
    collision_data=json.loads(collision_manifest.read_text())
    assert collision_data['map']==DATA['map']
    for key,path in collision_data['assets'].items():
        assert path.startswith('/Game/Terrarium/WorldExpansion/Architecture/Meshes/')
        mesh=unreal.load_asset(path)
        assert mesh and mesh.get_editor_property('lod_for_collision')==2
        assert unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).get_lod_count(mesh)==3
        meshes[key]=mesh
assert all(isinstance(m,unreal.StaticMesh) for m in meshes.values()), 'All admitted source meshes must exist'
labels={r['label'] for r in DATA['placements']}
for actor in list(A.get_all_level_actors()):
    if actor.get_actor_label() in labels:A.destroy_actor(actor)

def transform(row):
    mesh=meshes[row['asset']];x,y,z=[v*100 for v in row['location_m']]
    # Actual imported bounds are authoritative, including native props with nonzero pivots.
    z-=mesh.get_bounding_box().min.z*row['scale'][2]
    return unreal.Transform(location=unreal.Vector(x,y,z),
        rotation=unreal.Rotator(pitch=0,yaw=row['yaw_deg'],roll=0),scale=unreal.Vector(*row['scale']))

def serial(t):
    return {'location_cm':[t.translation.x,t.translation.y,t.translation.z],
            'scale':[t.scale3d.x,t.scale3d.y,t.scale3d.z],
            'quaternion_xyzw':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w]}

actual=[]
for row in DATA['placements']:
    t=transform(row);actor=A.spawn_actor_from_class(unreal.StaticMeshActor,t.translation)
    assert actor,row['label']
    actor.set_actor_label(row['label']);actor.set_folder_path('WorldExpansion/Settlements/'+row['settlement']+'/'+row['district'])
    actor.static_mesh_component.set_static_mesh(meshes[row['asset']])
    actor.set_actor_transform(t,False,False)
    actor.static_mesh_component.set_collision_profile_name('BlockAll')
    actor.static_mesh_component.set_editor_property('forced_lod_model',0)
    actor.static_mesh_component.set_editor_property('generate_overlap_events',False)
    actual.append({'label':row['label'],'asset':row['asset'],'kind':row['kind'],
                   'settlement':row['settlement'],'mesh':meshes[row['asset']].get_path_name(),**serial(t)})

groups=defaultdict(list)
for row in DATA['instances']:groups[row['asset']].append(row)
instance_receipts=[]
for key,rows in groups.items():
    name='FT_WX_Settlement_'+key;path=DEST+'/'+name
    ft=unreal.load_asset(path) or AT.create_asset(name,DEST,unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory())
    assert ft
    ft.set_editor_property('mesh',meshes[key])
    # Paving lies on the collidable terrain, planting/furniture does not obstruct streets.
    # Curtain walls use authored moss mesh collision via a private body setup profile.
    body=ft.get_editor_property('body_instance')
    body.set_editor_property('collision_profile_name','BlockAll' if key=='MossCliff4m' else 'NoCollision')
    body.set_editor_property('collision_enabled',unreal.CollisionEnabled.QUERY_AND_PHYSICS if key=='MossCliff4m' else unreal.CollisionEnabled.NO_COLLISION)
    ft.set_editor_property('body_instance',body)
    assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
    unreal.InstancedFoliageActor.remove_all_instances(world,ft)
    before={c.get_path_name():c.get_instance_count() for a in A.get_all_level_actors()
            for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==meshes[key]}
    transforms=[transform(row) for row in rows]
    unreal.InstancedFoliageActor.add_instances(world,ft,transforms)
    components=[];count=0
    for actor in A.get_all_level_actors():
        for component in actor.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
            if component.static_mesh==meshes[key]:
                delta=component.get_instance_count()-before.get(component.get_path_name(),0)
                if delta:
                    assert delta>0
                    count+=delta;components.append(component.get_path_name())
    assert count==len(rows),(key,count,len(rows))
    instance_receipts.append({'asset':key,'foliage_type':ft.get_path_name(),'mesh':meshes[key].get_path_name(),
                              'count':count,'components':components,'transforms':[serial(t) for t in transforms]})
    unreal.log('WorldExpansion settlement instances %s: %s'%(key,count))
assert L.save_current_level()
receipt={'map':DATA['map'],'actors':actual,'instances':instance_receipts,'summary':DATA['summary'],
         'source_meshes_and_materials_modified':False,'automatic_lods':True,
         'validation':'Saved after native instance-count readback. Reopen, visual and traversal validation remain coordinator work.'}
(ROOT/'Docs/WorldExpansion/settlement-integration.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(DATA['summary']))
