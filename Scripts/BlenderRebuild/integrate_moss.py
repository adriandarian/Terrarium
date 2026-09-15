"""Replace the 209 cliff-fringe instances while preserving their placement records."""
import unreal,json,shutil
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
folder=root/'Docs/BlenderRebuild/MossFringe';receipt=folder/'instance-placement.json';assert not receipt.exists()
before_path=root/'Saved/blender-foliage-MossFringe.json';before=json.loads(before_path.read_text())
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_path_name()==before['world'] and '/Blender/Maps/HomesteadBlender.' in world.get_path_name()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert len(before['foliage_types'])==1 and not before['static_actors']
oldft=unreal.load_asset(before['foliage_types'][0]['path']);oldmesh=oldft.get_editor_property('mesh');mesh=unreal.load_asset('/Game/Terrarium/Blender/MossFringe/SM_Blender_MossFringe');assert mesh
def vec(v):return [v.x,v.y,v.z]
def serial(t):
    q=t.rotation;return {'translation':vec(t.translation),'scale':vec(t.scale3d),'rotation_xyzw':[q.x,q.y,q.z,q.w]}
def instances(m):return [c.get_instance_transform(i,world_space=True) for a in actors.get_all_level_actors() for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent) if c.static_mesh==m for i in range(c.get_instance_count())]
jobs=instances(oldmesh);assert len(jobs)==209 and not instances(mesh)
assert [serial(t) for t in jobs]==[t for c in before['components'] for t in c['transforms']]
dest='/Game/Terrarium/Blender/MossFringe/FT_Blender_MossFringe';assert not unreal.EditorAssetLibrary.does_asset_exist(dest)
ft=unreal.EditorAssetLibrary.duplicate_asset(oldft.get_path_name(),dest);assert ft
ft.set_editor_property('mesh',mesh);ft.set_editor_property('override_materials',[]);assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
shutil.copyfile(before_path,folder/'before-placement.json')
unreal.InstancedFoliageActor.add_instances(world,ft,jobs);assert len(instances(mesh))==209
unreal.InstancedFoliageActor.remove_all_instances(world,oldft);assert not instances(oldmesh)
assert levels.save_current_level()
receipt.write_text(json.dumps({'asset':'MossFringe','world':world.get_path_name().split('.')[0],'mesh':mesh.get_path_name(),'old_mesh':oldmesh.get_path_name(),'old_foliage_type':oldft.get_path_name(),'new_foliage_type':ft.get_path_name(),'count':209,'instances':[{'before':serial(t),'after':serial(t)} for t in jobs],'scale_policy':'Original transforms retained, including placement-specific width and compressed hanging length. Attachment review follows migration.','status':'saved_pending_visual_and_attachment_review'},indent=2))
unreal.log('BLENDER_MOSS_MIGRATED')
