"""Refresh native surface graphs in the existing composed world."""
import importlib
import json
import sys
from pathlib import Path
import unreal

assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root = Path(unreal.Paths.project_dir())
sys.path.insert(0, str(root / 'Scripts/Fidelity'))
import materials_v7
importlib.reload(materials_v7)
report = materials_v7.apply()
(root / 'Docs/Fidelity/Pass7/materials.json').write_text(json.dumps(report, indent=2))
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.log('PASS7_SURFACES_REFRESHED')
