"""Run a single explicitly selected asset recipe inside the editor."""
import unreal,sys,importlib
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir())
sys.path.insert(0,str(root/'Scripts/Assets'))
name=(root/'Saved/asset-request.txt').read_text().strip()
assert name.replace('_','').isalnum()
import meshkit
importlib.reload(meshkit)
module=importlib.import_module(name)
importlib.reload(module)
module.build()
