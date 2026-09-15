"""Build the explicitly requested versioned assets, sequentially in Unreal."""
import unreal, sys, importlib, json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root = Path(unreal.Paths.project_dir())
sys.path.insert(0, str(root/'Scripts/Assets'))
request = json.loads((root/'Saved/pass7-build.json').read_text())
for recipe, asset in request:
    recipe, _, method = recipe.partition(':')
    assert recipe.replace('_', '').isalnum()
    path = '/Game/Terrarium/Meshes/' + asset
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.log('PASS7_EXISTING ' + asset)
        continue
    module = importlib.import_module(recipe)
    importlib.reload(module)
    getattr(module, method or 'build')()
    assert unreal.EditorAssetLibrary.does_asset_exist(path), path
    unreal.log('PASS7_BUILT ' + asset)
unreal.log('PASS7_BUILD_BATCH_COMPLETE')
