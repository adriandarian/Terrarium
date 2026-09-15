"""Capture the actual saved 3D composition through its review camera."""
import unreal
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/HomesteadFidelity.' in str(levels.get_current_level())
camera=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(world,'r.HighResScreenshotDelay 64')
task=unreal.AutomationLibrary.take_high_res_screenshot(1443,2427,str(Path(unreal.Paths.project_dir(),'Docs/Fidelity/Pass7/pass-7.png')),camera=camera,delay=1.0)
assert task
