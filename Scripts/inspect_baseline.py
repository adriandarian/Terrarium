import unreal
import json
from pathlib import Path

info = {'project': unreal.Paths.get_project_file_path(), 'engine': unreal.SystemLibrary.get_engine_version()}
assert 'Terrarium.uproject' in info['project']
for name in ['EditorLevelLibrary', 'LevelEditorSubsystem', 'EditorLoadingAndSavingUtils', 'CameraComponent', 'PostProcessSettings', 'RendererSettings']:
    cls = getattr(unreal, name, None)
    info[name] = [x for x in dir(cls) if any(k in x for k in ['level','camera','pilot','exposure','lumen','reflection','illumination','ortho','save','view'])]
Path(unreal.Paths.project_saved_dir(), 'baseline-api.json').write_text(json.dumps(info, indent=2))
