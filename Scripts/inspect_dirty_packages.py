import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
r={'content':[p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()],'maps':[p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]}
Path(unreal.Paths.project_dir(),'Saved/dirty-packages.json').write_text(json.dumps(r,indent=2))
