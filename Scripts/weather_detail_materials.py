"""Original fine-scale mottling on the revised shed and bridge only.

Noise affects base color, never normals or silhouette. Both assets retain their
matte, single-sided surface and their previously validated mesh topology.
"""
import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
path='/Game/Terrarium/Materials/M_WeatheredDetails'
lib=unreal.MaterialEditingLibrary
if unreal.EditorAssetLibrary.does_asset_exist(path):
    mat=unreal.load_asset(path)
else:
    mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_WeatheredDetails','/Game/Terrarium/Materials',unreal.Material,unreal.MaterialFactoryNew())
    vc=lib.create_material_expression(mat,unreal.MaterialExpressionVertexColor,-600,-200)
    noise=[]
    for scale,levels,low,high,y in [(.15,2,.82,1.12,0),(.022,1,.86,1.08,180)]:
        n=lib.create_material_expression(mat,unreal.MaterialExpressionNoise,-600,y)
        for key,value in [('scale',scale),('quality',1),('levels',levels),('output_min',low),('output_max',high)]:n.set_editor_property(key,value)
        noise.append(n)
    grain=lib.create_material_expression(mat,unreal.MaterialExpressionMultiply,-330,30)
    assert lib.connect_material_expressions(noise[0],'',grain,'A')
    assert lib.connect_material_expressions(noise[1],'',grain,'B')
    base=lib.create_material_expression(mat,unreal.MaterialExpressionMultiply,-120,-80)
    assert lib.connect_material_expressions(vc,'',base,'A')
    assert lib.connect_material_expressions(grain,'',base,'B')
    assert lib.connect_material_property(base,'',unreal.MaterialProperty.MP_BASE_COLOR)
    for prop,value,y in [(unreal.MaterialProperty.MP_ROUGHNESS,.96,200),(unreal.MaterialProperty.MP_SPECULAR,.07,280)]:
        n=lib.create_material_expression(mat,unreal.MaterialExpressionConstant,-120,y)
        n.set_editor_property('r',value);assert lib.connect_material_property(n,'',prop)
    lib.recompile_material(mat)
assert not mat.get_editor_property('two_sided')
assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
for name in ['SM_Shed_v2','SM_PlankBridge_v2']:
    sm=unreal.load_asset('/Game/Terrarium/Meshes/'+name);assert sm
    sm.set_material(0,mat);assert unreal.EditorAssetLibrary.save_loaded_asset(sm)
    p=Path(unreal.Paths.project_dir(),'Docs/Phase1/Validation',name+'.json')
    r=json.loads(p.read_text());r['surface_material']=path
    r['surface_detail']='Original two-frequency base-color noise; no normal or displacement changes.'
    r['visual_review']='pending: recapture final weathered material'
    p.write_text(json.dumps(r,indent=2))
