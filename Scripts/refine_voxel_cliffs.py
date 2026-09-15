"""Make square stone courses legible with shallow stepped face offsets."""
import unreal,sys,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir())
# Reuse the exact mesh recipe without executing its scene integration.
source=(root/'Scripts/voxel_world_pass.py').read_text()
recipe=source[source.index('class VoxelMesh'):source.index('for tree in (True, False):')]
recipe=recipe.replace("'SM_VoxelCliff_' + variant", "'SM_VoxelCliffStepped_' + variant")
sys.path.insert(0,str(root/'Scripts/Assets'))
from meshkit import Mesh
exec(compile(recipe,'voxel_cliff_recipe','exec'))
for variant in 'ABC':
    ft=unreal.load_asset('/Game/Terrarium/Foliage/FT_VoxelCliff_'+variant)
    ft.set_editor_property('mesh',replacements['SM_CliffColumn_v6'+variant])
    unreal.EditorAssetLibrary.save_loaded_asset(ft)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.save_current_level()
unreal.log('VOXEL_STEPPED_CLIFFS_SAVED')
