"""Verify saved moss material parameters and unchanged source pixels after map reload."""
import unreal,json,hashlib
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert '/Blender/Maps/HomesteadBlender.' in world.get_path_name()
dest='/Game/Terrarium/Blender/MossFringe';mat=unreal.load_asset(dest+'/M_MossFringe');mesh=unreal.load_asset(dest+'/SM_Blender_MossFringe')
assert mesh.get_material(0)==mat
names=[str(n) for n in unreal.MaterialEditingLibrary.get_scalar_parameter_names(mat)]
assert 'MossTileSizeCm' in names
period=unreal.MaterialEditingLibrary.get_material_default_scalar_parameter_value(mat,'MossTileSizeCm');assert abs(period-64)<.0001
source=root/'SourceAssets/Voxel/terrain_moss_cap_v1.png';copied=root/'SourceAssets/Blender/MossFringe/MossFringe_BaseColor.png';assert source.read_bytes()==copied.read_bytes()
folder=root/'Docs/BlenderRebuild/MossFringe'
placement=json.loads((folder/'saved-world-verification.json').read_text());assert placement['instances']==209 and placement['all_transforms_verified']
report={'world':world.get_path_name(),'material':mat.get_path_name(),'scalar_parameters':names,'tile_size_cm':period,'source_byte_identical':True,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'instances_verified':209,'fidelity_accepted':False}
(folder/'saved-material-verification.json').write_text(json.dumps(report,indent=2));unreal.log('BLENDER_MOSS_MATERIAL_VERIFIED')
