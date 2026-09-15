"""Bind Storm's opaque lightning and cloud texture material."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
base='/Game/Terrarium/Blender/Storm';out=root/'Docs/BlenderRebuild/Storm'
mesh=unreal.load_asset(base+'/SM_Blender_Storm');assert len(mesh.static_materials)==2
mel=unreal.MaterialEditingLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();report=[]
for i,slot in enumerate(mesh.static_materials):
    imported=str(slot.get_editor_property('imported_material_slot_name'))
    role=next(r for r in ['Lightning','Cloud'] if imported.startswith('M_Storm_'+r))
    name='M_Storm_'+role;mat=unreal.load_asset(base+'/'+name) or at.create_asset(name,base,unreal.Material,unreal.MaterialFactoryNew())
    mel.delete_all_material_expressions(mat);mat.set_editor_property('two_sided',False);mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_OPAQUE)
    for kind,prop in [('BaseColor',unreal.MaterialProperty.MP_BASE_COLOR),('Roughness',unreal.MaterialProperty.MP_ROUGHNESS)]:
        tx=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-400,0);tx.texture=unreal.load_asset(base+'/T_Storm_'+kind)
        if kind=='Roughness':tx.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR
        assert mel.connect_material_property(tx,'R' if kind=='Roughness' else 'RGB',prop)
    values={'Metallic':0,'Specular':.5}
    for key,value in values.items():
        node=mel.create_material_expression(mat,unreal.MaterialExpressionScalarParameter,-100,200);node.set_editor_property('parameter_name',key);node.set_editor_property('default_value',value)
        assert mel.connect_material_property(node,'',unreal.MaterialProperty.MP_METALLIC if key=='Metallic' else unreal.MaterialProperty.MP_SPECULAR)
    # Explicitly clear the emission input after temporary color probes.
    black=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-100,350);black.r=0
    assert mel.connect_material_property(black,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat);mesh.set_material(i,mat)
    report.append({'index':i,'imported_name':imported,'role':role,'material':mat.get_path_name(),'parameters':values,'blend_mode':str(mat.get_editor_property('blend_mode'))})
assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
(out/'material-bindings.json').write_text(json.dumps({'slots':report,'emission':'None. Opaque stylized lightning and cloud parts; no emitted light.'},indent=2))

