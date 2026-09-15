"""Replace matching environment assets in HomesteadBlender with authored models."""
import unreal,json,shutil
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
world_path='/Game/Terrarium/Blender/Maps/HomesteadBlender'
assert world.get_path_name().startswith(world_path+'.')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
folder=root/'Docs/BlenderRebuild/Environment';folder.mkdir(exist_ok=True)
receipt=folder/'instance-placement.json';assert not receipt.exists(),'Already migrated; use a refinement script'
before=json.loads((root/'Saved/blender-environment-before.json').read_text())
assert len(before['foliage_types'])==1
oldft=unreal.load_asset(before['foliage_types'][0]['path']);assert oldft
oldmesh=oldft.get_editor_property('mesh')
shrub=unreal.load_asset('/Game/Terrarium/Blender/MeadowShrub/SM_Blender_MeadowShrub')
rock=unreal.load_asset('/Game/Terrarium/Blender/MossRock/SM_Blender_MossRock');assert shrub and rock
def vec(v):return [v.x,v.y,v.z]
def serial(t):
    q=t.rotation
    return {'translation':vec(t.translation),'scale':vec(t.scale3d),'rotation_xyzw':[q.x,q.y,q.z,q.w]}
def instances(mesh):
    return [c.get_instance_transform(i,world_space=True) for a in actors.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==mesh for i in range(c.get_instance_count())]
jobs=instances(oldmesh);expected=[t for row in before['foliage'] for t in row['transforms']]
assert [serial(t) for t in jobs]==expected,'World changed since inspection'
oldbounds=oldmesh.get_bounding_box();newbounds=shrub.get_bounding_box()
factor=(oldbounds.max.z-oldbounds.min.z)/(newbounds.max.z-newbounds.min.z)
shrub_records=[]
for t in jobs:
    initial=serial(t);oldscale=t.scale3d;t.scale3d=oldscale*factor
    # Preserve each original root elevation; terrain offsets remain explicitly unchanged.
    p=t.translation;p.z+=oldbounds.min.z*oldscale.z-newbounds.min.z*t.scale3d.z;t.translation=p
    shrub_records.append({'before':initial,'after':serial(t)})
dest='/Game/Terrarium/Blender/MeadowShrub/FT_Blender_MeadowShrub'
assert not unreal.EditorAssetLibrary.does_asset_exist(dest)
ft=unreal.EditorAssetLibrary.duplicate_asset(oldft.get_path_name(),dest);assert ft
ft.set_editor_property('mesh',shrub);ft.set_editor_property('override_materials',[])
assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
assert not instances(shrub),'Unexpected preexisting instances'
shutil.copyfile(root/'Saved/blender-environment-before.json',folder/'before-placement.json')
unreal.InstancedFoliageActor.add_instances(world,ft,jobs)
assert len(instances(shrub))==len(jobs)
unreal.InstancedFoliageActor.remove_all_instances(world,oldft)
assert not instances(oldmesh)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};rock_records=[]
for record in before['rocks']:
    a=scene[record['actor']];c=a.static_mesh_component;old=c.static_mesh
    assert old.get_path_name()==record['mesh'] and serial(a.get_actor_transform())==record['transform']
    ob=old.get_bounding_box();nb=rock.get_bounding_box();ratio=(ob.max.z-ob.min.z)/(nb.max.z-nb.min.z)
    oldscale=a.get_actor_scale3d();uniform=oldscale.z*ratio;newscale=unreal.Vector(uniform,uniform,uniform);p=a.get_actor_location();p.z+=ob.min.z*oldscale.z-nb.min.z*newscale.z
    c.set_static_mesh(rock);c.set_editor_property('override_materials',[])
    a.set_actor_scale3d(newscale);a.set_actor_location(p,False,False)
    rock_records.append({'actor':a.get_actor_label(),'before':record['transform'],'after':serial(a.get_actor_transform()),'height_fit_factor':ratio})
assert levels.save_current_level()
receipt.write_text(json.dumps({'world':world_path,'old_foliage_type':oldft.get_path_name(),'new_foliage_type':ft.get_path_name(),'shrub_mesh':shrub.get_path_name(),'rock_mesh':rock.get_path_name(),'shrub_count':len(jobs),'rock_count':len(rock_records),'shrub_height_fit_factor':factor,'shrubs':shrub_records,'rocks':rock_records,'status':'saved_pending_reload_and_visual_check'},indent=2))
unreal.log('BLENDER_ENVIRONMENT_MIGRATED')
