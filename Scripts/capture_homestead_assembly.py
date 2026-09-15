"""Native reference-scale framing for the house and both fence runs."""
import unreal,sys
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());sys.path.insert(0,str(root/'Scripts/Fidelity'))
import reference as ref
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
baseline=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
review=next((a for a in actors.get_all_level_actors() if a.get_actor_label()=='HouseFence_Review_Transient'),None)
if review is None:review=actors.spawn_actor_from_class(unreal.CameraActor,unreal.Vector())
review.set_actor_label('HouseFence_Review_Transient')
review.set_actor_location(baseline.get_actor_location()+unreal.Vector(*ref.world(260,316,0)),False,False)
review.set_actor_rotation(baseline.get_actor_rotation(),False)
cc=review.camera_component;cc.set_projection_mode(unreal.CameraProjectionMode.ORTHOGRAPHIC)
cc.set_ortho_width(2200);cc.set_editor_property('aspect_ratio',1.5)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
levels.pilot_level_actor(review);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
task=unreal.AutomationLibrary.take_high_res_screenshot(1500,1000,str(root/'Docs/HomesteadAssembly/in-world.png'),camera=review,delay=1)
assert task

