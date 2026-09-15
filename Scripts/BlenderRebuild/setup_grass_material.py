"""Use the supplied grass image continuously in world XY across adjoining terrain instances."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
dest='/Game/Terrarium/Blender/GrassTerrain'
mat=unreal.load_asset(dest+'/M_GrassTerrain');mesh=unreal.load_asset(dest+'/SM_Blender_GrassTerrain');assert mat and mesh
mel=unreal.MaterialEditingLibrary;mel.delete_all_material_expressions(mat)
mat.set_editor_property('used_with_instanced_static_meshes',True)
world=mel.create_material_expression(mat,unreal.MaterialExpressionWorldPosition,-700,0)
uv=mel.create_material_expression(mat,unreal.MaterialExpressionCustom,-470,0)
uv.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT2)
pin=unreal.CustomInput();pin.set_editor_property('input_name','World');uv.set_editor_property('inputs',[pin])
uv.set_editor_property('code','return float2(World.x, -World.y) / 200.0 + 0.5;')
assert mel.connect_material_expressions(world,'',uv,'World')
for j,kind in enumerate(['BaseColor','Emission','Roughness']):
    tex=unreal.load_asset(dest+'/T_GrassTerrain_'+kind);assert tex
    sample=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-200,j*200);sample.texture=tex
    if kind=='BaseColor':
        names=mel.get_material_expression_input_names(sample)
        assert 'UVs' in names,names
        assert mel.connect_material_expressions(uv,'',sample,'UVs')
    if kind=='Roughness':sample.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR
    prop={'BaseColor':unreal.MaterialProperty.MP_BASE_COLOR,'Emission':unreal.MaterialProperty.MP_EMISSIVE_COLOR,'Roughness':unreal.MaterialProperty.MP_ROUGHNESS}[kind]
    assert mel.connect_material_property(sample,'R' if kind=='Roughness' else 'RGB',prop)
spec=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-100,600);spec.r=.15
assert mel.connect_material_property(spec,'',unreal.MaterialProperty.MP_SPECULAR)
mel.recompile_material(mat)
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
assert unreal.EditorAssetLibrary.save_loaded_asset(mat) and unreal.EditorAssetLibrary.save_loaded_asset(mesh)
(root/'Docs/BlenderRebuild/GrassTerrain/world-material.json').write_text(json.dumps({'albedo':'T_GrassTerrain_BaseColor','world_tile_size_cm':200,'uv_code':'float2(World.x, -World.y) / 200.0 + 0.5','purpose':'Continuous source texture coordinates across rotated/scaled meadow instances.','mesh_collision':'ComplexAsSimple'},indent=2))
unreal.log('BLENDER_GRASS_MATERIAL_READY')
