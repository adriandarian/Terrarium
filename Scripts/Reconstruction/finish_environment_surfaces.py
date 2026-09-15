"""Restore irregular trail silhouettes, weather props, and orient the authored tree crowns."""
import unreal,json,math
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/Environment'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/HomesteadReference.' in str(levels.get_current_level())
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();lib=unreal.MaterialEditingLibrary;at=unreal.AssetToolsHelpers.get_asset_tools()
def pigment(name,code):
    mat=unreal.load_asset('/Game/Terrarium/Environment/Materials/'+name) or at.create_asset(name,'/Game/Terrarium/Environment/Materials',unreal.Material,unreal.MaterialFactoryNew())
    lib.delete_all_material_expressions(mat);mat.set_editor_property('used_with_instanced_static_meshes',True)
    v=lib.create_material_expression(mat,unreal.MaterialExpressionVertexColor,-500,-100);p=lib.create_material_expression(mat,unreal.MaterialExpressionWorldPosition,-500,80)
    c=lib.create_material_expression(mat,unreal.MaterialExpressionCustom,-180,0);c.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    pins=[]
    for key in ['Pigment','World']:
        pin=unreal.CustomInput();pin.set_editor_property('input_name',key);pins.append(pin)
    c.set_editor_property('inputs',pins);c.set_editor_property('code',code)
    assert lib.connect_material_expressions(v,'',c,'Pigment');assert lib.connect_material_expressions(p,'',c,'World');assert lib.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
    for prop,value,y in [(unreal.MaterialProperty.MP_ROUGHNESS,.98,170),(unreal.MaterialProperty.MP_SPECULAR,.05,280)]:
        n=lib.create_material_expression(mat,unreal.MaterialExpressionConstant,-180,y);n.set_editor_property('r',value);lib.connect_material_property(n,'',prop)
    lib.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat);return mat
pathmat=pigment('M_ReferenceTrail','''
float2 row=floor(World.xy/float2(27,21));
float h=frac(sin(dot(row,float2(127.1,311.7)))*43758.5453);
float broad=sin(World.x*.012+sin(World.y*.008))*sin(World.y*.009)*.5+.5;
float3 tan=lerp(float3(.31,.233,.112),float3(.385,.306,.172),broad);
float worn=frac(sin(dot(floor(World.xy/7.0),float2(41.3,27.9)))*13453.);
return tan*lerp(.86,1.13,h)*lerp(.97,1.02,worn);
''')
prop=pigment('M_ReferenceWeatheredProps','''
float h=frac(sin(dot(floor(World/12),float3(127.1,311.7,74.7)))*43758.5453);
float broad=sin(World.x*.04+sin(World.z*.03))*sin(World.y*.045-World.z*.023);
float lum=dot(Pigment,float3(.21,.72,.07));
return lerp(lum.xxx,Pigment,.88)*(0.90+.14*h+.045*broad);
''')
oldpath=unreal.load_asset('/Game/Terrarium/Meshes/SM_PathTile_v4_Detail');assert oldpath
ft=unreal.load_asset('/Game/Terrarium/Environment/Foliage/FT_Env_PathTile_v4_Detail');assert ft
ts=[]
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if c.static_mesh and c.static_mesh.get_name()=='SM_Env_PathTile':
            if isinstance(c,unreal.FoliageInstancedStaticMeshComponent):ts.extend(c.get_instance_transform(i,world_space=True) for i in range(c.get_instance_count()))
            else:c.set_static_mesh(oldpath);c.set_material(0,pathmat)
unreal.InstancedFoliageActor.remove_all_instances(world,ft)
ft.set_editor_property('mesh',oldpath);ft.set_editor_property('override_materials',[pathmat]);assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
unreal.InstancedFoliageActor.add_instances(world,ft,ts)
for a in actors.get_all_level_actors():
    if a.get_actor_label().startswith('Reference_') and isinstance(a,unreal.StaticMeshActor) and a.get_actor_label()!='Reference_Player':a.static_mesh_component.set_material(0,prop)
ft=unreal.load_asset('/Game/Terrarium/Environment/Foliage/FT_Env_Tree_v3_Detail');ts=[]
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
        if c.static_mesh and c.static_mesh.get_name()=='SM_Recon_HomesteadTree_R3':
            for i in range(c.get_instance_count()):
                t=c.get_instance_transform(i,world_space=True);p=t.translation
                ts.append(unreal.Transform(location=p,rotation=unreal.Rotator(pitch=0,yaw=70+12*math.sin(p.x*.015),roll=0),scale=t.scale3d))
unreal.InstancedFoliageActor.remove_all_instances(world,ft);unreal.InstancedFoliageActor.add_instances(world,ft,ts)
assert levels.save_current_level()
(out/'integration-stage4.json').write_text(json.dumps({'irregular_path_mesh':oldpath.get_path_name(),'path_material':pathmat.get_path_name(),'prop_material':prop.get_path_name(),'trees_oriented_to_reference':len(ts),'reason':'Reject hard rectangular ribbon from stage2; restore continuous irregular edge geometry.'},indent=2))
