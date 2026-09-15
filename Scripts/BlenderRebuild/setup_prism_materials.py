"""Keep crystal transmission, luminous inclusion and metal as distinct UE shaders."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
base='/Game/Terrarium/Blender/TrailPrism';out=root/'Docs/BlenderRebuild/TrailPrism'
mesh=unreal.load_asset(base+'/SM_Blender_TrailPrism');assert len(mesh.static_materials)==3
mel=unreal.MaterialEditingLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();report=[]
for i,slot in enumerate(mesh.static_materials):
    imported=str(slot.get_editor_property('imported_material_slot_name'))
    role=next(r for r in ['Crystal','Core','Frame'] if imported.startswith('M_TrailPrism_'+r))
    name='M_TrailPrism_'+role;mat=unreal.load_asset(base+'/'+name) or at.create_asset(name,base,unreal.Material,unreal.MaterialFactoryNew())
    mel.delete_all_material_expressions(mat)
    mat.set_editor_property('two_sided',False)
    mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT if role=='Crystal' else unreal.BlendMode.BLEND_OPAQUE)
    if role=='Crystal':
        mat.set_editor_property('translucency_lighting_mode',unreal.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
        mat.set_editor_property('refraction_method',unreal.RefractionMode.RM_INDEX_OF_REFRACTION)
    for kind,prop in [('BaseColor',unreal.MaterialProperty.MP_BASE_COLOR),('Roughness',unreal.MaterialProperty.MP_ROUGHNESS)]:
        node=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-500,0)
        node.texture=unreal.load_asset(base+'/T_TrailPrism_'+kind)
        if kind=='Roughness':node.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR
        assert mel.connect_material_property(node,'R' if kind=='Roughness' else 'RGB',prop)
    params={'Metallic':(.82 if role=='Frame' else 0,unreal.MaterialProperty.MP_METALLIC),'Specular':(.2 if role=='Crystal' else .5,unreal.MaterialProperty.MP_SPECULAR)}
    if role=='Crystal':params.update({'Opacity':(.36,unreal.MaterialProperty.MP_OPACITY),'Refraction':(1.0054,unreal.MaterialProperty.MP_REFRACTION)})
    for key,(value,prop) in params.items():
        node=mel.create_material_expression(mat,unreal.MaterialExpressionScalarParameter,-100,200)
        node.set_editor_property('parameter_name',key);node.set_editor_property('default_value',value)
        assert mel.connect_material_property(node,'',prop)
    values={k:v[0] for k,v in params.items()}
    if role=='Crystal':
        # Approximate the core's internal scattering through amber. Surface
        # translucency alone does not illuminate outward faces from an inner light.
        tex=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-500,400);tex.texture=unreal.load_asset(base+'/T_TrailPrism_BaseColor')
        strength=mel.create_material_expression(mat,unreal.MaterialExpressionScalarParameter,-400,600)
        strength.set_editor_property('parameter_name','CoreScatter');strength.set_editor_property('default_value',1800)
        mult=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,-150,400)
        assert mel.connect_material_expressions(tex,'RGB',mult,'A') and mel.connect_material_expressions(strength,'',mult,'B')
        assert mel.connect_material_property(mult,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        values['CoreScatter']=1800
    if role=='Core':
        tex=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-500,400);tex.texture=unreal.load_asset(base+'/T_TrailPrism_Emission')
        strength=mel.create_material_expression(mat,unreal.MaterialExpressionScalarParameter,-400,600)
        strength.set_editor_property('parameter_name','EmissionStrength');strength.set_editor_property('default_value',2000)
        mult=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,-150,400)
        assert mel.connect_material_expressions(tex,'RGB',mult,'A') and mel.connect_material_expressions(strength,'',mult,'B')
        assert mel.connect_material_property(mult,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        values['EmissionStrength']=2000
    mel.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
    mesh.set_material(i,mat)
    report.append({'index':i,'role':role,'imported_name':imported,'material':mat.get_path_name(),'blend_mode':str(mat.get_editor_property('blend_mode')),'parameters':values})
assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
(out/'material-bindings.json').write_text(json.dumps({'slots':report,'limits':'Blender crystal uses stylized IOR 1.12 and transmission 0.82. UE uses opacity and reduced screen-space refraction; optical equivalence is not claimed.'},indent=2))
