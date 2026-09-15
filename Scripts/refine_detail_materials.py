"""Soft close-range material detail: wood fibers, worn clay and mineral pigment."""
import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/DetailPass'
lib=unreal.MaterialEditingLibrary
path='/Game/Terrarium/Materials/M_DetailCrafted'
mat=unreal.load_asset(path)
if not mat:
    mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_DetailCrafted','/Game/Terrarium/Materials',unreal.Material,unreal.MaterialFactoryNew())
    mat.set_editor_property('used_with_instanced_static_meshes',True)
    v=lib.create_material_expression(mat,unreal.MaterialExpressionVertexColor,-700,0)
    p=lib.create_material_expression(mat,unreal.MaterialExpressionWorldPosition,-700,180)
    n=lib.create_material_expression(mat,unreal.MaterialExpressionVertexNormalWS,-700,350)
    c=lib.create_material_expression(mat,unreal.MaterialExpressionCustom,-200,0)
    c.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    inputs=[]
    for name in ('Pigment','World','Normal'):
        pin=unreal.CustomInput();pin.set_editor_property('input_name',name);inputs.append(pin)
    c.set_editor_property('inputs',inputs)
    c.set_editor_property('code','''
float3 p=World;
float grainAxis=abs(Normal.z)>.7 ? p.x*.73+p.y*.68 : p.z;
float across=abs(Normal.x)>.7 ? p.y : p.x;
if(abs(Normal.z)>.7) across=p.x*.68-p.y*.73;
float wave=sin(across*1.65+sin(grainAxis*.09)*1.1+sin(grainAxis*.023)*2.0);
float fine=sin(across*4.6+sin(grainAxis*.06));
float fibers=smoothstep(.50,.95,wave)*.13+smoothstep(.78,.99,fine)*.045;
float wood=step(Pigment.b*1.75,Pigment.r)*step(Pigment.g*1.12,Pigment.r)*(1-step(.43,Pigment.r));
float clay=step(Pigment.g*1.65,Pigment.r)*step(.20,Pigment.r);
float cloud=sin(p.x*.07+sin(p.z*.047))*sin(p.y*.065-p.z*.093);
float grit=frac(sin(dot(floor(p*.62),float3(127.1,311.7,74.7)))*43758.5453);
float wear=lerp(.92,1.065,grit)*(.98+.065*cloud);
float shade=lerp(wear,(1.025-fibers)*(.98+.04*cloud),wood*(1-clay));
shade=lerp(shade,.96+.10*cloud+.075*grit,clay);
return Pigment*shade;
''')
    for node,name in ((v,'Pigment'),(p,'World'),(n,'Normal')):assert lib.connect_material_expressions(node,'',c,name)
    assert lib.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
    for prop,value in ((unreal.MaterialProperty.MP_ROUGHNESS,.96),(unreal.MaterialProperty.MP_SPECULAR,.06)):
        q=lib.create_material_expression(mat,unreal.MaterialExpressionConstant,-150,350)
        q.set_editor_property('r',value);lib.connect_material_property(q,'',prop)
    lib.recompile_material(mat)
    assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
families=('Cottage','Shed','PlankBridge','Fence','GardenWell','Lantern','GardenBed','Traveler')
updated=[]
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if not c.static_mesh:continue
        name=c.static_mesh.get_name()
        if '_Detail' not in name or not any(s in name for s in families):continue
        c.set_material(0,mat);updated.append(name)
        if isinstance(c,unreal.FoliageInstancedStaticMeshComponent):
            ft=unreal.load_asset('/Game/Terrarium/Foliage/FT_'+name[3:])
            ft.set_editor_property('override_materials',[mat]);unreal.EditorAssetLibrary.save_loaded_asset(ft)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(out/'crafted-material.json').write_text(json.dumps({'material':path,'assets':sorted(set(updated))},indent=2))
unreal.log('CRAFTED_SURFACES_SAVED')
