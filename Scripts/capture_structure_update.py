"""Native 3D render at exactly three times the reference image dimensions."""
import unreal
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/HomesteadFidelity.' in str(levels.get_current_level())
camera=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(world,'r.HighResScreenshotDelay 64')
p=Path(unreal.Paths.project_dir(),'Docs/Fidelity');p.mkdir(parents=True,exist_ok=True)
task=unreal.AutomationLibrary.take_high_res_screenshot(1443,2427,str(p/'Structures/structure-update.png'),camera=camera,delay=2.0)
assert task
