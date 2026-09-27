import unreal
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
l=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
l.eject_pilot_level_actor();assert l.load_level('/Game/Terrarium/Blender/Maps/HomesteadBlender')
exec((root/'Scripts/inspect_scene_assembly.py').read_text())

