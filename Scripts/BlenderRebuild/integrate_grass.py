"""Migrate both existing meadow foliage types, preserving every instance transform."""
import unreal,json,shutil
from pathlib import Path
from collections import Counter
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
folder=root/'Docs/BlenderRebuild/GrassTerrain';receipt=folder/'instance-placement.json';assert not receipt.exists()
before_path=root/'Saved/blender-foliage-GrassTerrain.json';before=json.loads(before_path.read_text())
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()==before['world'] and '/Blender/Maps/HomesteadBlender.' in world.get_path_name()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
mesh=unreal.load_asset('/Game/Terrarium/Blender/GrassTerrain/SM_Blender_GrassTerrain')
oldmesh=unreal.load_asset(before['components'][0]['mesh']);assert mesh and oldmesh
assert len(before['foliage_types'])==2 and not before['static_actors']
def vec(v):return [v.x,v.y,v.z]
def serial(t):
    q=t.rotation;return {'translation':vec(t.translation),'scale':vec(t.scale3d),'rotation_xyzw':[q.x,q.y,q.z,q.w]}
def code(t):return json.dumps(serial(t),sort_keys=True)
def instances(m):return [c.get_instance_transform(i,world_space=True) for a in actors.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==m for i in range(c.get_instance_count())]
initial=instances(oldmesh)
assert len(initial)==5841 and not instances(mesh)
assert [serial(t) for t in initial]==[t for c in before['components'] for t in c['transforms']]
shutil.copyfile(before_path,folder/'before-placement.json')
groups=[]
for i,row in enumerate(before['foliage_types']):
    oldft=unreal.load_asset(row['path']);assert oldft.get_editor_property('mesh')==oldmesh
    suffix='Edge' if 'Edge' in oldft.get_name() else 'Interior'
    dest='/Game/Terrarium/Blender/GrassTerrain/FT_Blender_GrassTerrain_'+suffix
    assert not unreal.EditorAssetLibrary.does_asset_exist(dest)
    ft=unreal.EditorAssetLibrary.duplicate_asset(oldft.get_path_name(),dest);assert ft
    ft.set_editor_property('mesh',mesh);ft.set_editor_property('override_materials',[])
    body=ft.get_editor_property('body_instance')
    body.set_editor_property('collision_profile_name','BlockAll')
    body.set_editor_property('collision_enabled',unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    ft.set_editor_property('body_instance',body)
    assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
    # Removing the intended source type identifies its exact membership without
    # guessing which component name represents the interior or edge type.
    prior=instances(oldmesh);prior_count=Counter(code(t) for t in prior)
    unreal.InstancedFoliageActor.remove_all_instances(world,oldft)
    remaining=Counter(code(t) for t in instances(oldmesh));removed=prior_count-remaining
    jobs=[]
    for t in prior:
        k=code(t)
        if removed[k]>0:jobs.append(t);removed[k]-=1
    assert jobs and not +removed
    group={'old_foliage_type':oldft.get_path_name(),'new_foliage_type':ft.get_path_name(),'count':len(jobs),'transforms':[serial(t) for t in jobs]}
    (folder/('migration-'+suffix+'.json')).write_text(json.dumps(group,indent=2))
    previous_new=len(instances(mesh));unreal.InstancedFoliageActor.add_instances(world,ft,jobs)
    assert len(instances(mesh))==previous_new+len(jobs)
    groups.append(group)
assert not instances(oldmesh)
assert Counter(code(t) for t in instances(mesh))==Counter(code(t) for t in initial)
assert levels.save_current_level()
receipt.write_text(json.dumps({'asset':'GrassTerrain','world':world.get_path_name().split('.')[0],'mesh':mesh.get_path_name(),'old_mesh':oldmesh.get_path_name(),'count':len(initial),'groups':groups,'status':'saved_pending_reload_visual_and_collision_checks'},indent=2))
unreal.log('BLENDER_GRASS_MIGRATED')
