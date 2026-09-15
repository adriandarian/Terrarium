"""Keep the supplied moss pattern at a fixed physical scale despite foliage scaling."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
dest='/Game/Terrarium/Blender/MossFringe';mat=unreal.load_asset(dest+'/M_MossFringe');assert mat
backup=dest+'/M_MossFringe_BeforeWorldMapping'
if not unreal.EditorAssetLibrary.does_asset_exist(backup):
    assert unreal.EditorAssetLibrary.duplicate_asset(mat.get_path_name(),backup)
mel=unreal.MaterialEditingLibrary;mel.delete_all_material_expressions(mat)
mat.set_editor_property('used_with_instanced_static_meshes',True)
world=mel.create_material_expression(mat,unreal.MaterialExpressionWorldPosition,-1000,0)
normal=mel.create_material_expression(mat,unreal.MaterialExpressionVertexNormalWS,-1000,180)
period=mel.create_material_expression(mat,unreal.MaterialExpressionScalarParameter,-1000,360)
period.set_editor_property('parameter_name','MossTileSizeCm');period.set_editor_property('default_value',64.)
uv=mel.create_material_expression(mat,unreal.MaterialExpressionCustom,-650,0);uv.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT2)
pins=[]
for name in ['World','Normal','Period']:
    p=unreal.CustomInput();p.set_editor_property('input_name',name);pins.append(p)
uv.set_editor_property('inputs',pins)
code='float3 N = abs(Normal); if (N.z >= max(N.x, N.y)) return float2(World.x, -World.y) / Period + 0.5; if (N.x >= N.y) return float2(World.y, -World.z) / Period + 0.5; return float2(World.x, -World.z) / Period + 0.5;'
uv.set_editor_property('code',code)
for node,name in [(world,'World'),(normal,'Normal'),(period,'Period')]:assert mel.connect_material_expressions(node,'',uv,name)
for j,kind in enumerate(['BaseColor','Emission','Roughness']):
    sample=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-250,j*220)
    sample.texture=unreal.load_asset(dest+'/T_MossFringe_'+kind);assert sample.texture
    if kind=='BaseColor':assert mel.connect_material_expressions(uv,'',sample,'UVs')
    if kind=='Roughness':sample.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR
    prop={'BaseColor':unreal.MaterialProperty.MP_BASE_COLOR,'Emission':unreal.MaterialProperty.MP_EMISSIVE_COLOR,'Roughness':unreal.MaterialProperty.MP_ROUGHNESS}[kind]
    assert mel.connect_material_property(sample,'R' if kind=='Roughness' else 'RGB',prop)
spec=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-100,660);spec.r=.15
assert mel.connect_material_property(spec,'',unreal.MaterialProperty.MP_SPECULAR)
mel.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
(root/'Docs/BlenderRebuild/MossFringe/world-material.json').write_text(json.dumps({'material':mat.get_path_name(),'previous_material_copy':backup,'projection':'Dominant face axis in world space','tile_size_cm':64,'uv_code':code,'source_image_unchanged':True,'geometry_and_transforms_unchanged':True,'visual_review':'pending','tradeoff':'Pattern size is independent of instance scaling; world-projected color no longer follows the source-luminance relief one-to-one.'},indent=2))
unreal.log('BLENDER_MOSS_WORLD_MAPPING_READY')
