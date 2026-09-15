"""Lit orange creature with an explicit horn-only emissive vertex mask."""
import unreal

def apply(mesh):
    lib=unreal.MaterialEditingLibrary
    folder='/Game/Terrarium/Reconstruction/Materials'
    path=folder+'/M_KindlehornGlow_R4'
    mat=unreal.load_asset(path)
    if not mat:
        mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_KindlehornGlow_R4',folder,unreal.Material,unreal.MaterialFactoryNew())
        def node(cls):return lib.create_material_expression(mat,cls,0,0)
        def link(a,out,b,pin):assert lib.connect_material_expressions(a,out,b,pin)
        def scalar(v):
            n=node(unreal.MaterialExpressionConstant);n.set_editor_property('r',v);return n
        vc=node(unreal.MaterialExpressionVertexColor)
        lib.connect_material_property(vc,'',unreal.MaterialProperty.MP_BASE_COLOR)
        mask=node(unreal.MaterialExpressionMultiply);link(vc,'',mask,'A');link(vc,'A',mask,'B')
        glow=node(unreal.MaterialExpressionMultiply);link(mask,'',glow,'A');link(scalar(5),'',glow,'B')
        lib.connect_material_property(glow,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        lib.connect_material_property(scalar(.8),'',unreal.MaterialProperty.MP_ROUGHNESS)
        lib.connect_material_property(scalar(.15),'',unreal.MaterialProperty.MP_SPECULAR)
        lib.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
    mesh.set_material(0,mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    return path

def spark_material():
    folder='/Game/Terrarium/Reconstruction/Materials';path=folder+'/M_KindlehornSpark_R4'
    mat=unreal.load_asset(path)
    if not mat:
        mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_KindlehornSpark_R4',folder,unreal.Material,unreal.MaterialFactoryNew())
        mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_ADDITIVE)
        mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
        mat.set_editor_property('two_sided',True)
        mat.set_editor_property('used_with_niagara_sprites',True)
        lib=unreal.MaterialEditingLibrary
        pc=lib.create_material_expression(mat,unreal.MaterialExpressionParticleColor,0,0)
        lib.connect_material_property(pc,'RGB',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        lib.connect_material_property(pc,'A',unreal.MaterialProperty.MP_OPACITY)
        lib.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
    return mat
