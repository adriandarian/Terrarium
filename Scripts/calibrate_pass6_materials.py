"""Original lit palette calibration from measured reference-region color differences."""
import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
lib=unreal.MaterialEditingLibrary
def material(name):
    path='/Game/Terrarium/Materials/'+name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        mat=unreal.load_asset(path);lib.delete_all_material_expressions(mat);return mat,True
    return unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,'/Game/Terrarium/Materials',unreal.Material,unreal.MaterialFactoryNew()),True
def node(mat,typ,x,y):return lib.create_material_expression(mat,typ,x,y)
def connect(a,b,pin):
    inputs=lib.get_material_expression_input_names(b)
    outputs=lib.get_material_expression_output_names(a)
    if pin=='Input':pin=inputs[0]
    assert lib.connect_material_expressions(a,outputs[0],b,pin),(inputs,outputs,pin)
def color_node(mat,value,x,y):
    n=node(mat,unreal.MaterialExpressionConstant3Vector,x,y)
    n.set_editor_property('constant',unreal.LinearColor(*value,1));return n
def finish(mat,result):
    assert lib.connect_material_property(result,'',unreal.MaterialProperty.MP_BASE_COLOR)
    for prop,v,y in [(unreal.MaterialProperty.MP_ROUGHNESS,.96,420),(unreal.MaterialProperty.MP_SPECULAR,.06,500)]:
        n=node(mat,unreal.MaterialExpressionConstant,250,y);n.set_editor_property('r',v)
        assert lib.connect_material_property(n,'',prop)
    lib.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat)

ground,new=material('M_MeadowAltitudePalette')
if new:
    vc=node(ground,unreal.MaterialExpressionVertexColor,-800,-200)
    noise=node(ground,unreal.MaterialExpressionNoise,-800,0)
    for k,v in [('scale',.06),('levels',2),('quality',1),('output_min',.86),('output_max',1.12)]:noise.set_editor_property(k,v)
    paint=node(ground,unreal.MaterialExpressionMultiply,-550,-100);connect(vc,paint,'A');connect(noise,paint,'B')
    pos=node(ground,unreal.MaterialExpressionWorldPosition,-1100,230)
    mask=node(ground,unreal.MaterialExpressionComponentMask,-920,230)
    for k,v in [('r',False),('g',False),('b',True),('a',False)]:mask.set_editor_property(k,v)
    connect(pos,mask,'Input')
    subtract=node(ground,unreal.MaterialExpressionSubtract,-760,230);subtract.set_editor_property('const_b',280);connect(mask,subtract,'A')
    divide=node(ground,unreal.MaterialExpressionDivide,-600,230);divide.set_editor_property('const_b',600);connect(subtract,divide,'A')
    clamp=node(ground,unreal.MaterialExpressionClamp,-430,230);connect(divide,clamp,'Input')
    low=color_node(ground,(.80,.70,.80),-430,360);high=color_node(ground,(1.25,1.0,1.2),-430,450)
    gradient=node(ground,unreal.MaterialExpressionLinearInterpolate,-220,220)
    connect(low,gradient,'A');connect(high,gradient,'B');connect(clamp,gradient,'Alpha')
    result=node(ground,unreal.MaterialExpressionMultiply,80,0);connect(paint,result,'A');connect(gradient,result,'B')
    finish(ground,result)
sm=unreal.load_asset('/Game/Terrarium/Meshes/SM_MeadowTile_v4')
sm.set_material(0,ground);assert unreal.EditorAssetLibrary.save_loaded_asset(sm)
p=Path(unreal.Paths.project_dir(),'Docs/Phase1/Validation/SM_MeadowTile_v4.json')
report=json.loads(p.read_text());report['surface_material']=ground.get_path_name();report['visual_review']='pending: final altitude palette review'
p.write_text(json.dumps(report,indent=2))

water,new=material('M_QuietRiverPalette')
if new:
    vc=node(water,unreal.MaterialExpressionVertexColor,-400,0)
    tint=color_node(water,(.93,.72,.68),-400,130)
    result=node(water,unreal.MaterialExpressionMultiply,-100,0);connect(vc,result,'A');connect(tint,result,'B')
    finish(water,result)
Path(unreal.Paths.project_dir(),'Docs/Fidelity/Pass6/material-calibration.json').write_text(json.dumps({'ground_low_linear_multiplier':[.8,.7,.8],'ground_upper_linear_multiplier':[1.25,1,1.2],'ground_elevation_range_cm':[280,880],'water_linear_multiplier':[.93,.72,.68],'normal_mapping':False,'shading':'lit, single-sided, matte'},indent=2))
