"""Bind separate glass, liquid and opaque trim to the verified FBX slots."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
base='/Game/Terrarium/Blender/MossTonic';out=root/'Docs/BlenderRebuild/MossTonic'
mesh=unreal.load_asset(base+'/SM_Blender_MossTonic');assert len(mesh.static_materials)==3
mel=unreal.MaterialEditingLibrary;at=unreal.AssetToolsHelpers.get_asset_tools()
albedo=unreal.load_asset(base+'/T_MossTonic_BaseColor');roughness=unreal.load_asset(base+'/T_MossTonic_Roughness')
report=[]
for i,slot in enumerate(mesh.static_materials):
    name=str(slot.get_editor_property('imported_material_slot_name'))
    role=next(r for r in ['Glass','Liquid','Trim'] if name.startswith('M_MossTonic_'+r))
    mat=unreal.load_asset(base+'/M_MossTonic_'+role) or at.create_asset('M_MossTonic_'+role,base,unreal.Material,unreal.MaterialFactoryNew())
    mel.delete_all_material_expressions(mat)
    mat.set_editor_property('two_sided',False)
    mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT if role!='Trim' else unreal.BlendMode.BLEND_OPAQUE)
    if role!='Trim':
        mat.set_editor_property('translucency_lighting_mode',unreal.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
        mat.set_editor_property('refraction_method',unreal.RefractionMode.RM_INDEX_OF_REFRACTION)
    for tex,prop in [(albedo,unreal.MaterialProperty.MP_BASE_COLOR),(roughness,unreal.MaterialProperty.MP_ROUGHNESS)]:
        node=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-400,0);node.texture=tex
        if tex==roughness:node.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR
        assert mel.connect_material_property(node,'R' if tex==roughness else 'RGB',prop)
    params={'Specular':(.5,unreal.MaterialProperty.MP_SPECULAR)}
    if role!='Trim':params.update({'Opacity':(.30 if role=='Glass' else .90,unreal.MaterialProperty.MP_OPACITY),'IOR':(1.46 if role=='Glass' else 1.33,unreal.MaterialProperty.MP_REFRACTION)})
    for key,(value,prop) in params.items():
        node=mel.create_material_expression(mat,unreal.MaterialExpressionScalarParameter,-150,200);node.set_editor_property('parameter_name',key);node.set_editor_property('default_value',value)
        if key=='IOR':
            # UE screen-space distortion assumes an unbounded medium. Limit that
            # displacement for this small thick-walled bottle; Blender retains IOR.
            subtract=mel.create_material_expression(mat,unreal.MaterialExpressionAdd,-50,220);subtract.set_editor_property('const_b',-1)
            assert mel.connect_material_expressions(node,'',subtract,'A')
            mult=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,100,220)
            scale=mel.create_material_expression(mat,unreal.MaterialExpressionScalarParameter,-50,360);scale.set_editor_property('parameter_name','RefractionScale');scale.set_editor_property('default_value',.045)
            assert mel.connect_material_expressions(subtract,'',mult,'A') and mel.connect_material_expressions(scale,'',mult,'B')
            add=mel.create_material_expression(mat,unreal.MaterialExpressionAdd,250,220);add.set_editor_property('const_b',1)
            assert mel.connect_material_expressions(mult,'',add,'A') and mel.connect_material_property(add,'',prop)
        else:assert mel.connect_material_property(node,'',prop)
    mel.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
    mesh.set_material(i,mat)
    values={k:v[0] for k,v in params.items()}
    if role!='Trim':values['RefractionScale']=.045
    report.append({'index':i,'imported_name':name,'role':role,'material':mat.get_path_name(),'blend_mode':str(mat.get_editor_property('blend_mode')),'parameters':values})
assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
(out/'material-bindings.json').write_text(json.dumps({'slots':report,'limits':'Engine raster translucency approximates Blender transmission; native world review required.'},indent=2))
