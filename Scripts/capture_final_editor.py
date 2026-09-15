"""A native Unreal high-resolution render, with no external image synthesis."""
import unreal
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/Homestead.' in str(levels.get_current_level())
camera=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(world,'r.HighResScreenshotDelay 64')
folder=Path(unreal.Paths.project_dir(),'Docs/Final');folder.mkdir(parents=True,exist_ok=True)
task=unreal.AutomationLibrary.take_high_res_screenshot(1584,2400,str(folder/'homestead.png'),camera=camera,delay=2.0)
assert task
