"""Finish visible clay chips and block-scale material variation for the set."""
import unreal,sys,importlib
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());sys.path.insert(0,str(root/'Scripts/Assets'))
import homestead_assembly as family;importlib.reload(family)
for name,fn in [('SM_Assembly_Cottage_v2',family.cottage),('SM_Assembly_BlueShed_v2',family.shed)]:
    if not unreal.EditorAssetLibrary.does_asset_exist('/Game/Terrarium/Meshes/'+name):fn()
path='/Game/Terrarium/Materials/M_AssemblyCrafted'
mat=unreal.load_asset(path)
if not mat:
    mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_AssemblyCrafted','/Game/Terrarium/Materials',unreal.Material,unreal.MaterialFactoryNew())
    lib=unreal.MaterialEditingLibrary
    v=lib.create_material_expression(mat,unreal.MaterialExpressionVertexColor,-500,0)
    p=lib.create_material_expression(mat,unreal.MaterialExpressionWorldPosition,-500,200)
    code=lib.create_material_expression(mat,unreal.MaterialExpressionCustom,0,0)
    code.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    inputs=[]
    for name in ('Pigment','World'):
        pin=unreal.CustomInput();pin.set_editor_property('input_name',name);inputs.append(pin)
    code.set_editor_property('inputs',inputs)
    code.set_editor_property('code','''
float3 cell=floor(World/11.0);
float big=frac(sin(dot(cell,float3(127.1,311.7,74.7)))*43758.5453);
float3 chip=floor(World/3.5);
float small=frac(sin(dot(chip,float3(71.7,213.3,119.9)))*21942.174);
float warm=step(Pigment.g*1.3,Pigment.r);
float shade=lerp(.78,1.18,big)*lerp(.96,1.045,small);
float darkChip=step(small,.035)*.12;
return Pigment*(shade-darkChip)*(1.0+warm*.045);
''')
    lib.connect_material_expressions(v,'',code,'Pigment');lib.connect_material_expressions(p,'',code,'World')
    lib.connect_material_property(code,'',unreal.MaterialProperty.MP_BASE_COLOR)
    for prop,value in [(unreal.MaterialProperty.MP_ROUGHNESS,.96),(unreal.MaterialProperty.MP_SPECULAR,.055)]:
        node=lib.create_material_expression(mat,unreal.MaterialExpressionConstant,0,250);node.set_editor_property('r',value)
        lib.connect_material_property(node,'',prop)
    lib.recompile_material(mat);unreal.EditorAssetLibrary.save_loaded_asset(mat)
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if not isinstance(a,unreal.StaticMeshActor) or not a.static_mesh_component.static_mesh:continue
    n=a.static_mesh_component.static_mesh.get_name()
    if n in ('SM_Assembly_Cottage','SM_Assembly_BlueShed'):
        a.static_mesh_component.set_static_mesh(unreal.load_asset('/Game/Terrarium/Meshes/'+n+'_v2'))
    if n.startswith('SM_Assembly_'):a.static_mesh_component.set_material(0,mat)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.log('ASSEMBLY_SURFACES_FINISHED')
