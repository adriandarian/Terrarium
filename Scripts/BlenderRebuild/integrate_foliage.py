"""Migrate inspected foliage into a separate Blender foliage type in the working map."""
import unreal,json,shutil
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
key=(root/'Saved/blender-import-asset.txt').read_text().strip();assert key=='HomesteadTree'
before_path=root/'Saved'/('blender-foliage-'+key+'.json');before=json.loads(before_path.read_text())
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()==before['world'] and '/Blender/Maps/HomesteadBlender.' in world.get_path_name()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
folder=root/'Docs/BlenderRebuild'/key;receipt=folder/'instance-placement.json';assert not receipt.exists()
assert len(before['foliage_types'])==1 and not before['static_actors']
oldft=unreal.load_asset(before['foliage_types'][0]['path']);oldmesh=oldft.get_editor_property('mesh')
mesh=unreal.load_asset('/Game/Terrarium/Blender/'+key+'/SM_Blender_'+key);assert mesh
def vec(v):return [v.x,v.y,v.z]
def serial(t):
    q=t.rotation;return {'translation':vec(t.translation),'scale':vec(t.scale3d),'rotation_xyzw':[q.x,q.y,q.z,q.w]}
def instances(m):return [c.get_instance_transform(i,world_space=True) for a in actors.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==m for i in range(c.get_instance_count())]
jobs=instances(oldmesh);assert jobs and not instances(mesh)
assert [serial(t) for t in jobs]==[t for c in before['components'] for t in c['transforms']]
ob=oldmesh.get_bounding_box();nb=mesh.get_bounding_box();factor=(ob.max.z-ob.min.z)/(nb.max.z-nb.min.z)
changes=[]
for t in jobs:
    initial=serial(t);s=t.scale3d;t.scale3d=s*factor;p=t.translation;p.z+=ob.min.z*s.z-nb.min.z*t.scale3d.z;t.translation=p
    changes.append({'before':initial,'after':serial(t)})
dest='/Game/Terrarium/Blender/'+key+'/FT_Blender_'+key;assert not unreal.EditorAssetLibrary.does_asset_exist(dest)
ft=unreal.EditorAssetLibrary.duplicate_asset(oldft.get_path_name(),dest);assert ft
ft.set_editor_property('mesh',mesh);ft.set_editor_property('override_materials',[]);assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
shutil.copyfile(before_path,folder/'before-placement.json')
unreal.InstancedFoliageActor.add_instances(world,ft,jobs);assert len(instances(mesh))==len(jobs)
unreal.InstancedFoliageActor.remove_all_instances(world,oldft);assert not instances(oldmesh)
assert levels.save_current_level()
receipt.write_text(json.dumps({'asset':key,'world':world.get_path_name().split('.')[0],'old_foliage_type':oldft.get_path_name(),'new_foliage_type':ft.get_path_name(),'mesh':mesh.get_path_name(),'old_mesh':oldmesh.get_path_name(),'count':len(jobs),'height_fit_factor':factor,'instances':changes,'status':'saved_pending_visual_review'},indent=2))
unreal.log('BLENDER_FOLIAGE_MIGRATED_'+key)
