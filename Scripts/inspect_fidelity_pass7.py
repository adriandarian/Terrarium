"""Inspect the connected native editor before pass 7 edits."""
import unreal, json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
report = {'project': unreal.Paths.get_project_file_path(),
          'engine': unreal.SystemLibrary.get_engine_version(),
          'level': str(levels.get_current_level()),
          'actors': len(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())}
Path(unreal.Paths.project_dir(), 'Docs/Fidelity/Pass7/editor-before.json').write_text(json.dumps(report, indent=2))
unreal.log('PASS7_EDITOR_VERIFIED ' + str(report))
