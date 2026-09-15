import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
path='/Game/Terrarium/Blender/Maps/HomesteadBlender'
levels.eject_pilot_level_actor()
assert levels.load_level(path)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
house=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Reference_Cottage')
mesh=house.static_mesh_component.static_mesh
assert mesh.get_path_name()=='/Game/Terrarium/Blender/Cottage/SM_Blender_Cottage.SM_Blender_Cottage'
assert house.get_actor_location().z==560 and abs(house.get_actor_rotation().yaw+90)<.001
assert len(mesh.static_materials)==1
assert mesh.get_material(0).get_path_name()=='/Game/Terrarium/Blender/Cottage/M_Cottage.M_Cottage'
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Blender_Cottage_Review')
cc=camera.get_component_by_class(unreal.CameraComponent)
cc.set_editor_property('ortho_width',1450)
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
assert levels.save_current_level()
(root/'Docs/BlenderRebuild/Cottage/saved-world-verification.json').write_text(json.dumps({'map':path,'reopened':True,'mesh_binding':mesh.get_path_name(),'material_binding':mesh.get_material(0).get_path_name(),'location_z_cm':560,'facing_yaw_degrees':-90,'source_editable_blender':True,'visual_status':'in_progress_not_exact_concept_parity'},indent=2))
