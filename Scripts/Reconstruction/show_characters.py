"""Open the completed character gallery in the verified Terrarium editor."""
import json
from pathlib import Path
import unreal

assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.load_level('/Game/Terrarium/Reconstruction/Maps/Characters')
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
camera = next(a for a in actors if a.get_actor_label() == 'GalleryOverviewCamera')
unreal.EditorLevelLibrary.set_level_viewport_camera_info(camera.get_actor_location(), camera.get_actor_rotation())
Path(unreal.Paths.project_dir(), 'Saved/reconstruction-presentation.json').write_text(json.dumps({
    'project': unreal.Paths.get_project_file_path(),
    'level': str(levels.get_current_level()),
    'camera': camera.get_actor_label()
}, indent=2))
