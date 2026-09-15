"""Preserve traced stone UVs and match cliff-cap grass to the continuous meadow mapping."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
dest='/Game/Terrarium/Blender/CliffColumn';mat=unreal.load_asset(dest+'/M_CliffColumn');mesh=unreal.load_asset(dest+'/SM_Blender_CliffColumn');assert mat and mesh
mel=unreal.MaterialEditingLibrary;mel.delete_all_material_expressions(mat)
mat.set_editor_property('used_with_instanced_static_meshes',True)
world=mel.create_material_expression(mat,unreal.MaterialExpressionWorldPosition,-900,0)
coords=mel.create_material_expression(mat,unreal.MaterialExpressionTextureCoordinate,-900,180)
uv=mel.create_material_expression(mat,unreal.MaterialExpressionCustom,-650,0)
uv.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT2)
inputs=[]
for name in ['World','MeshUV']:
    pin=unreal.CustomInput();pin.set_editor_property('input_name',name);inputs.append(pin)
uv.set_editor_property('inputs',inputs)
code='if (MeshUV.x > 0.5) return float2(0.5 + 0.5 * frac(World.x / 200.0 + 0.5), frac(-World.y / 200.0 + 0.5)); return MeshUV;'
uv.set_editor_property('code',code)
assert mel.connect_material_expressions(world,'',uv,'World') and mel.connect_material_expressions(coords,'',uv,'MeshUV')
for j,kind in enumerate(['BaseColor','Emission','Roughness']):
    sample=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-250,j*220)
    sample.texture=unreal.load_asset(dest+'/T_CliffColumn_'+kind);assert sample.texture
    if kind=='BaseColor':assert mel.connect_material_expressions(uv,'',sample,'UVs')
    if kind=='Roughness':sample.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR
    prop={'BaseColor':unreal.MaterialProperty.MP_BASE_COLOR,'Emission':unreal.MaterialProperty.MP_EMISSIVE_COLOR,'Roughness':unreal.MaterialProperty.MP_ROUGHNESS}[kind]
    assert mel.connect_material_property(sample,'R' if kind=='Roughness' else 'RGB',prop)
spec=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-100,660);spec.r=.15
assert mel.connect_material_property(spec,'',unreal.MaterialProperty.MP_SPECULAR)
mel.recompile_material(mat)
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
assert unreal.EditorAssetLibrary.save_loaded_asset(mat) and unreal.EditorAssetLibrary.save_loaded_asset(mesh)
(root/'Docs/BlenderRebuild/CliffColumn/world-material.json').write_text(json.dumps({'uv_code':code,'grass_repeat_cm':200,'mesh_collision':'ComplexAsSimple','stone_uvs_preserved':True},indent=2))
unreal.log('BLENDER_CLIFF_MATERIAL_READY')
