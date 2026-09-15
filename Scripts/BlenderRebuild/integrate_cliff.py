"""Replace the two original cliff meshes, retaining all transforms and original foliage types."""
import unreal,json
from pathlib import Path
from collections import Counter
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
folder=root/'Docs/BlenderRebuild/CliffColumn';receipt=folder/'instance-placement.json';assert not receipt.exists()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/Terrarium/Blender/Maps/HomesteadBlender.')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
mesh=unreal.load_asset('/Game/Terrarium/Blender/CliffColumn/SM_Blender_CliffColumn');assert mesh
assert (folder/'world-material.json').exists()
def vec(v):return [v.x,v.y,v.z]
def serial(t):
    q=t.rotation;return {'translation':vec(t.translation),'scale':vec(t.scale3d),'rotation_xyzw':[q.x,q.y,q.z,q.w]}
def instances(m):return [c.get_instance_transform(i,world_space=True) for a in actors.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==m for i in range(c.get_instance_count())]
def code(t):return json.dumps(serial(t),sort_keys=True)
assert not instances(mesh)
jobs=[];before=[]
for suffix,count in [('A',668),('B',665)]:
    oldmesh=unreal.load_asset('/Game/Terrarium/Environment/Meshes/SM_Env_Cliff_'+suffix+'_R2');assert oldmesh
    transforms=instances(oldmesh);assert len(transforms)==count
    assert not [a for a in actors.get_all_level_actors() if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh==oldmesh]
    fts=[]
    for path in unreal.EditorAssetLibrary.list_assets('/Game/Terrarium/Environment/Foliage',recursive=True):
        ft=unreal.load_asset(path)
        if isinstance(ft,unreal.FoliageType_InstancedStaticMesh) and ft.get_editor_property('mesh')==oldmesh:fts.append(ft)
    assert len(fts)==1,[f.get_path_name() for f in fts]
    dest='/Game/Terrarium/Blender/CliffColumn/FT_Blender_CliffColumn_'+suffix
    assert not unreal.EditorAssetLibrary.does_asset_exist(dest)
    jobs.append((suffix,oldmesh,fts[0],dest,transforms))
    before.append({'suffix':suffix,'old_mesh':oldmesh.get_path_name(),'old_foliage_type':fts[0].get_path_name(),'count':count,'transforms':[serial(t) for t in transforms]})
(folder/'before-placement.json').write_text(json.dumps({'world':world.get_path_name(),'groups':before},indent=2))
groups=[]
for suffix,oldmesh,oldft,dest,transforms in jobs:
    ft=unreal.EditorAssetLibrary.duplicate_asset(oldft.get_path_name(),dest);assert ft
    ft.set_editor_property('mesh',mesh);ft.set_editor_property('override_materials',[])
    body=ft.get_editor_property('body_instance');body.set_editor_property('collision_profile_name','BlockAll');body.set_editor_property('collision_enabled',unreal.CollisionEnabled.QUERY_AND_PHYSICS);ft.set_editor_property('body_instance',body)
    assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
    unreal.InstancedFoliageActor.remove_all_instances(world,oldft);assert not instances(oldmesh)
    unreal.InstancedFoliageActor.add_instances(world,ft,transforms)
    groups.append({'suffix':suffix,'old_mesh':oldmesh.get_path_name(),'old_foliage_type':oldft.get_path_name(),'new_foliage_type':ft.get_path_name(),'count':len(transforms),'transforms':[serial(t) for t in transforms]})
expected=[t for job in jobs for t in job[4]]
assert Counter(code(t) for t in instances(mesh))==Counter(code(t) for t in expected)
assert levels.save_current_level()
receipt.write_text(json.dumps({'world':world.get_path_name().split('.')[0],'mesh':mesh.get_path_name(),'count':len(expected),'groups':groups,'status':'saved_pending_reload_and_visual_review'},indent=2))
unreal.log('BLENDER_CLIFF_MIGRATED')
