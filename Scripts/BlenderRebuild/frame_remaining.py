import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};cam=scene['Review_Camera']
cam.camera_component.set_projection_mode(unreal.CameraProjectionMode.PERSPECTIVE);cam.camera_component.set_editor_property('field_of_view',48.)
cam.set_actor_location(unreal.Vector(800,2000,1200),False,False);cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(cam.get_actor_location(),unreal.Vector(0,-180,110)),False)
levels.pilot_level_actor(cam);levels.set_exact_camera_view(True);levels.editor_set_game_view(True);levels.save_current_level()
p=cam.get_actor_location();r=cam.get_actor_rotation();args=json.loads((root/'Saved/remaining-batch-capture.json').read_text());args['captureTransform']['location']={'x':p.x,'y':p.y,'z':p.z};args['captureTransform']['rotation']={'pitch':r.pitch,'yaw':r.yaw,'roll':r.roll};(root/'Saved/remaining-batch-capture.json').write_text(json.dumps(args))
