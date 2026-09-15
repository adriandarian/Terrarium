"""Native closer views of the assembled environment, preserving the hero camera."""
import unreal,json,sys
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/Environment';sys.path.insert(0,str(root/'Scripts/Fidelity'));import reference as ref
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/HomesteadReference.' in str(levels.get_current_level())
r=json.loads((root/'Saved/environment-detail.json').read_text())
levels.eject_pilot_level_actor()
for a in list(actors.get_all_level_actors()):
    if a.get_actor_label()=='Reference_TransientDetailCamera':actors.destroy_actor(a)
baseline=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
camera=actors.spawn_actor_from_class(unreal.CameraActor,baseline.get_actor_location()+unreal.Vector(*ref.world(*r['center'],0)),baseline.get_actor_rotation())
camera.set_actor_label('Reference_TransientDetailCamera');cc=camera.camera_component
cc.set_projection_mode(unreal.CameraProjectionMode.ORTHOGRAPHIC);cc.set_ortho_width(r['width']);cc.set_editor_property('aspect_ratio',1.5)
cc.set_editor_property('post_process_settings',baseline.camera_component.post_process_settings);cc.set_editor_property('post_process_blend_weight',1.0)
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
task=unreal.AutomationLibrary.take_high_res_screenshot(1500,1000,str(out/(r['name']+'.png')),camera=camera,delay=1.0);assert task
