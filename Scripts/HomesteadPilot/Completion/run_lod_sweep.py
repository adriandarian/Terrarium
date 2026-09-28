"""Coordinator staging of automatic LOD review; preserve every scene actor."""
from pathlib import Path
import unreal
root = Path(unreal.Paths.project_dir()).resolve()
assert root == Path('C:/Users/hello/Projects/Terrarium')
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
levels.eject_pilot_level_actor()
levels.editor_set_game_view(True)
unreal.get_editor_subsystem(unreal.EditorActorSubsystem).set_selected_level_actors([])
path = root/'Scripts/HomesteadPilot/RuntimeCompletion/sweep_automatic_lod.py'
exec(compile(path.read_text(),str(path),'exec'), {})
