"""Finish the third original cliff group using the existing Blender placement module."""
import unreal,json
from pathlib import Path
from collections import Counter
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
folder=root/'Docs/BlenderRebuild/CliffColumn';path=folder/'instance-placement.json';r=json.loads(path.read_text())
assert r['count']==1333 and {g['suffix'] for g in r['groups']}=={'A','B'}
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_path_name()==r['world']+'.HomesteadBlender'
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
mesh=unreal.load_asset(r['mesh']);oldmesh=unreal.load_asset('/Game/Terrarium/Environment/Meshes/SM_Env_Cliff_C_R2')
def vec(v):return [v.x,v.y,v.z]
def serial(t):
    q=t.rotation;return {'translation':vec(t.translation),'scale':vec(t.scale3d),'rotation_xyzw':[q.x,q.y,q.z,q.w]}
def instances(m):return [c.get_instance_transform(i,world_space=True) for a in actors.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==m for i in range(c.get_instance_count())]
def code(t):return json.dumps(serial(t),sort_keys=True)
transforms=instances(oldmesh);assert len(transforms)==743 and len(instances(mesh))==1333
assert not [a for a in actors.get_all_level_actors() if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh==oldmesh]
fts=[]
for p in unreal.EditorAssetLibrary.list_assets('/Game/Terrarium/Environment/Foliage',recursive=True):
    ft=unreal.load_asset(p)
    if isinstance(ft,unreal.FoliageType_InstancedStaticMesh) and ft.get_editor_property('mesh')==oldmesh:fts.append(ft)
assert len(fts)==1;oldft=fts[0]
dest='/Game/Terrarium/Blender/CliffColumn/FT_Blender_CliffColumn_C';assert not unreal.EditorAssetLibrary.does_asset_exist(dest)
g={'suffix':'C','old_mesh':oldmesh.get_path_name(),'old_foliage_type':oldft.get_path_name(),'new_foliage_type':dest+'.FT_Blender_CliffColumn_C','count':743,'transforms':[serial(t) for t in transforms]}
(folder/'before-placement-C.json').write_text(json.dumps(g,indent=2))
prior=instances(mesh)
ft=unreal.EditorAssetLibrary.duplicate_asset(oldft.get_path_name(),dest);assert ft
ft.set_editor_property('mesh',mesh);ft.set_editor_property('override_materials',[])
body=ft.get_editor_property('body_instance');body.set_editor_property('collision_profile_name','BlockAll');body.set_editor_property('collision_enabled',unreal.CollisionEnabled.QUERY_AND_PHYSICS);ft.set_editor_property('body_instance',body)
assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
unreal.InstancedFoliageActor.remove_all_instances(world,oldft);assert not instances(oldmesh)
unreal.InstancedFoliageActor.add_instances(world,ft,transforms)
assert Counter(code(t) for t in instances(mesh))==Counter(code(t) for t in prior+transforms)
assert levels.save_current_level()
r['groups'].append(g);r['count']=2076;r['status']='saved_pending_all_three_groups_reload'
path.write_text(json.dumps(r,indent=2));unreal.log('BLENDER_CLIFF_C_MIGRATED')
