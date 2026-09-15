"""Native viewport render from the reference camera, retaining actual exposure."""
import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/Environment';out.mkdir(exist_ok=True)
r=json.loads((root/'Saved/environment-capture.json').read_text())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True);actors.set_selected_level_actors([])
levels.editor_invalidate_viewports()
task=unreal.AutomationLibrary.take_high_res_screenshot(962,1618,str(out/(r['name']+'.png')),camera=camera,delay=1.0)
assert task
(out/(r['name']+'-camera.json')).write_text(json.dumps({'position':str(camera.get_actor_location()),'rotation':str(camera.get_actor_rotation()),'width':camera.camera_component.ortho_width,'world':str(levels.get_current_level()),'native_viewport':True},indent=2))
