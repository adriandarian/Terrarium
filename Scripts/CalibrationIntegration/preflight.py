import unreal,json,hashlib
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
report={'project':str(root),'engine':unreal.SystemLibrary.get_engine_version(),'current_level':str(levels.get_current_level()),'dirty_map_packages':[p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()],'baseline_map_sha256':hashlib.sha256((root/'Content/Terrarium/Blender/Maps/HomesteadBlender.umap').read_bytes()).hexdigest()}
(root/'Docs/CalibrationIntegration/preflight.json').write_text(json.dumps(report,indent=2))
