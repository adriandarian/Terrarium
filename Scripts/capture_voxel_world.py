"""Retain the native asynchronous screenshot task until capture completes."""
import unreal
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert '/HomesteadFidelity.' in str(levels.get_current_level())
camera=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
levels.pilot_level_actor(camera)
levels.set_exact_camera_view(True)
levels.editor_set_game_view(True)
task=unreal.AutomationLibrary.take_high_res_screenshot(962,1618,str(Path(unreal.Paths.project_dir(),'Docs/VoxelPass/voxel-world.png')),camera=camera,delay=1.0)
assert task
