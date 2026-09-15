"""Opt-in bronze patina on the crest's authored vertex-alpha regions only."""
import unreal

def apply(mesh):
    lib=unreal.MaterialEditingLibrary
    name='M_EmberCrest_Patina_R6';folder='/Game/Terrarium/Reconstruction/Materials'
    path=folder+'/'+name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        mat=unreal.load_asset(path)
    else:
        mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,folder,unreal.Material,unreal.MaterialFactoryNew())
        def node(cls,x=0,y=0):return lib.create_material_expression(mat,cls,x,y)
        def link(a,out,b,pin):assert lib.connect_material_expressions(a,out,b,pin),pin
        def scalar(value):
            n=node(unreal.MaterialExpressionConstant);n.set_editor_property('r',value);return n
        vc=node(unreal.MaterialExpressionVertexColor,-800,0)
        noise=node(unreal.MaterialExpressionNoise,-800,200)
        noise.set_editor_property('scale',8.0)
        noise.set_editor_property('levels',2)
        noise.set_editor_property('output_min',.67)
        noise.set_editor_property('output_max',1.12)
        mix=node(unreal.MaterialExpressionLinearInterpolate,-500,180)
        link(scalar(1),'',mix,'A');link(noise,'',mix,'B');link(vc,'A',mix,'Alpha')
        color=node(unreal.MaterialExpressionMultiply,-250,0)
        link(vc,'',color,'A');link(mix,'',color,'B')
        assert lib.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
        metallic=node(unreal.MaterialExpressionMultiply,-250,300)
        link(vc,'A',metallic,'A');link(scalar(.42),'',metallic,'B')
        assert lib.connect_material_property(metallic,'',unreal.MaterialProperty.MP_METALLIC)
        rough=node(unreal.MaterialExpressionLinearInterpolate,-250,450)
        link(scalar(.76),'',rough,'A');link(scalar(.58),'',rough,'B');link(vc,'A',rough,'Alpha')
        assert lib.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
        assert lib.connect_material_property(scalar(.25),'',unreal.MaterialProperty.MP_SPECULAR)
        lib.recompile_material(mat)
        assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
    mesh.set_material(0,mat)
    assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    return path
